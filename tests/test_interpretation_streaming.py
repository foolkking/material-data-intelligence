from __future__ import annotations

import asyncio
import json
from copy import deepcopy
from itertools import count
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import update

from mdi_api.db import research_turns
from mdi_api.infrastructure.interpretation.client import DeepSeekInterpreterClient, FakeStructuredInterpreterClient
from mdi_api.infrastructure.interpretation.service import InterpretationFailure, ScientificInterpretationService
from mdi_api.infrastructure.interpretation.streaming import InterpretationStreamPublisher, completed_interpretation_parts
from mdi_api.application.interpretation.assembler import InterpreterInputAssembler
from mdi_api.application.interpretation.grounding import project_grounded_communication
from mdi_api.application.interpretation.projector import AssistantResponseProjector
from mdi_api.domain.interpretation.contracts import ScientificInterpretationOutput
from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
from mdi_llm.http_transport import ProviderStreamCancelled
from mdi_llm.providers import PlannerRawResponse, PlannerUserConfig
from tests.test_agent2_interpretation import _bundle, _output, _multi_source_bundle
from tests.test_research_result_loss_recovery import _saved_result
from tests.test_research_worker_loss_recovery import _stalled_turn


def _events(factory, turn_id):
    with factory.session() as session:
        return session.agent2.research_turn_events.list_for_turn(turn_id)


def _deltas(factory, turn_id):
    return [event["payload_json"] for event in _events(factory, turn_id) if event["event_type"] == "ASSISTANT_RESPONSE_DELTA"]


def _publisher(factory, turn_id, bundle=None):
    bundle = bundle or _bundle()
    envelope, _ = InterpreterInputAssembler().assemble(bundle=bundle, question="解释保存的结果", relevance_status="CURRENT")
    with factory.session() as session:
        version = int(session.agent2.research_turns.get(turn_id)["row_version"])
    return InterpretationStreamPublisher(
        factory, turn_id=turn_id, claim_version=version, bundle=bundle, relevance="CURRENT",
        normalize=lambda value: ScientificInterpretationService._resolve_provider_reference_aliases(
            ScientificInterpretationService._strip_legacy_finding_fields(value), envelope,
        ),
    )


def _finding_prefix(finding, version="1.0"):
    return json.dumps({"contract_version": version}, ensure_ascii=False)[:-1] + ',"primary_findings":[' + json.dumps(finding, ensure_ascii=False)


@pytest.fixture
def interpreting():
    factory, turn_id = _stalled_turn("INTERPRETING", age_minutes=0)
    try:
        yield factory, turn_id
    finally:
        factory.engine.dispose()


def test_parser_waits_for_the_whole_finding_including_late_qualifiers():
    finding = _output()["primary_findings"][0]
    finding["qualifiers"] = ['原字符串包含 }、]、\\ 和 "，不能提前闭合。']
    raw = _finding_prefix(finding)
    for end in range(1, len(raw)):
        assert completed_interpretation_parts(raw[:end]).get("primary_findings", []) == []
    assert completed_interpretation_parts(raw)["primary_findings"] == [finding]
    assert completed_interpretation_parts("```json\n" + raw)["primary_findings"] == [finding]
    with pytest.raises(ValueError):
        completed_interpretation_parts('{"contract_version":"1.0","contract_version":"1.1"}')


def test_publishes_a_closed_grounded_finding_before_the_response_finishes(interpreting):
    factory, turn_id = interpreting
    publisher = _publisher(factory, turn_id)
    finding = _output()["primary_findings"][0]
    raw = _finding_prefix(finding)
    publisher.feed(raw[:-1])
    assert _deltas(factory, turn_id) == []
    publisher.feed("}")
    public = _deltas(factory, turn_id)
    assert len(public) == 1 and public[0]["text"] == "## 分析结果\n\n第一峰位于 2.5 angstrom。"
    with factory.session() as session:
        turn = session.agent2.research_turns.get(turn_id)
        assert turn["status"] == "INTERPRETING" and turn["assistant_final_message_id"] is None
        assert session.agent2.interpretations.get_for_turn(turn_id) is None
    publisher.feed('],"answer_lead":"未校验的摘要与内部内容","title":"不可公开的标题"}')
    assert _deltas(factory, turn_id) == public


@pytest.mark.parametrize("mutation", ["quantity", "unit", "fact", "source", "unknown-field", "causal"])
def test_unverified_claims_never_reach_a_public_delta(interpreting, mutation):
    factory, turn_id = interpreting
    finding = deepcopy(_output()["primary_findings"][0])
    bundle = _bundle()
    version = "1.0"
    if mutation == "quantity":
        finding["statement"] = "第一峰位于 999 angstrom。"
    elif mutation == "unit":
        finding["statement"] = "第一峰位于 2.5 nm。"
    elif mutation == "fact":
        finding["fact_refs"] = ["foreign.fact"]
    elif mutation == "source":
        bundle = _multi_source_bundle()
        finding["statement"] = "Cu.cif 的峰位为 2.5 angstrom。"
    elif mutation == "unknown-field":
        finding["private_reasoning"] = "must not be published"
    else:
        version = "1.1"
        finding.update(statement="该峰证明材料结构导致了高导电性。", claim_type="CAUSAL_CLAIM")
        finding["reasoning_assessment"] = {"accepted": True}
    _publisher(factory, turn_id, bundle).feed(_finding_prefix(finding, version))
    assert _deltas(factory, turn_id) == []


def test_preview_retains_partial_result_qualifications_and_exact_aliases(interpreting):
    factory, turn_id = interpreting
    payload = _bundle(execution_status="PARTIAL").model_dump(mode="json")
    payload["limitations"] = [{"limitation_id": "scope", "code": "PARTIAL_SCOPE", "message": "仅覆盖已保存的结果。", "source_ref": "artifact-1"}]
    payload["limitations"].append({**payload["limitations"][0], "limitation_id": "same-scope", "message": " 仅覆盖已保存的结果。 "})
    payload["warnings"] = [
        {"warning_id": "same-scope", "code": "PARTIAL_SCOPE", "message": "仅覆盖已保存的结果。"},
        {"warning_id": "measurement", "code": "REFERENCE_ONLY", "message": "不代表实验测量。"},
    ]
    bundle = ScientificResultBundle.model_validate(payload)
    finding = deepcopy(_output()["primary_findings"][0])
    finding.update(fact_refs=["fact_a"], evidence_refs=["evidence_a"], result_item_refs=["result_a"])
    _publisher(factory, turn_id, bundle).feed(_finding_prefix(finding))
    text = _deltas(factory, turn_id)[0]["text"]
    assert "部分完成" in text and text.index("仅覆盖已保存的结果") < text.index("第一峰")
    assert "2.5 angstrom" in text and "fact_1" not in text
    assert text.count("仅覆盖已保存的结果。") == 1
    assert text.count("不代表实验测量。") == 1
    assert text.index("仅覆盖已保存的结果。") < text.index("不代表实验测量。") < text.index("第一峰")


@pytest.mark.parametrize("markdown", [False, True])
def test_final_answer_deduplicates_identical_qualifications_without_changing_saved_inputs(markdown):
    payload = _bundle().model_dump(mode="json")
    payload["warnings"] = [
        {"warning_id": "scope", "code": "REFERENCE_ONLY", "message": "仅覆盖已保存的结果。"},
        {"warning_id": "measurement", "code": "REFERENCE_ONLY", "message": "不代表实验测量。"},
        {"warning_id": "duplicate", "code": "REFERENCE_ONLY", "message": " 不代表实验测量。 "},
    ]
    bundle = ScientificResultBundle.model_validate(payload)
    output = ScientificInterpretationOutput.model_validate({
        **_output(), "limitations": ["仅覆盖已保存的结果。", " 仅覆盖已保存的结果。 ", "未验证样品性质。"],
    })
    before = (bundle.model_dump(), output.model_dump())
    text = AssistantResponseProjector().project(output, bundle, effective_relevance="CURRENT", markdown=markdown)
    assert text.count("仅覆盖已保存的结果。") == 1
    assert text.count("未验证样品性质。") == 1
    assert text.count("不代表实验测量。") == 1
    assert text.index("仅覆盖已保存的结果。") < text.index("未验证样品性质。") < text.index("不代表实验测量。")
    assert (bundle.model_dump(), output.model_dump()) == before


@pytest.mark.parametrize("markdown", [False, True])
def test_qualification_repeated_as_finding_is_shown_once_in_its_section(markdown):
    limitation = "这是理想模型，不代表实测或弛豫结构。"
    warning = "未验证样品性质。"
    payload = _bundle().model_dump(mode="json")
    payload["warnings"] = [{"warning_id": "sample", "code": "REFERENCE_ONLY", "message": warning}]
    bundle = ScientificResultBundle.model_validate(payload)
    proposal = _output()
    proposal["answer_lead"] = limitation
    proposal["supporting_findings"] = [
        {**proposal["primary_findings"][0], "finding_id": "scope", "statement": limitation},
        {**proposal["primary_findings"][0], "finding_id": "sample", "statement": warning},
    ]
    proposal["limitations"] = [limitation, "未验证稳定相。"]
    output = ScientificInterpretationOutput.model_validate(proposal)
    before = (bundle.model_dump(), output.model_dump())
    text = AssistantResponseProjector().project(output, bundle, effective_relevance="CURRENT", markdown=markdown)
    assert text.count(limitation) == text.count(warning) == 1
    assert "2.5 angstrom" in text and "未验证稳定相。" in text
    assert text.index("限制") < text.index(limitation) < text.index("警告") < text.index(warning)
    assert (bundle.model_dump(), output.model_dump()) == before


def test_duplicate_or_oversized_response_withdraws_its_preview(interpreting):
    factory, turn_id = interpreting
    publisher = _publisher(factory, turn_id)
    finding = _output()["primary_findings"][0]
    publisher.feed(_finding_prefix(finding))
    publisher.feed("," + json.dumps(finding))
    assert _events(factory, turn_id)[-1]["event_type"] == "ASSISTANT_RESPONSE_RESET"
    assert publisher.enabled is False
    another = _publisher(factory, turn_id)
    another.feed(_finding_prefix(finding))
    another.feed(" " * 200_001)
    assert _events(factory, turn_id)[-1]["event_type"] == "ASSISTANT_RESPONSE_RESET"
    assert another.raw == "" and another.enabled is False


@pytest.mark.parametrize("status", ["CANCELED", "INTERPRETING"])
def test_canceled_or_reclaimed_claim_cannot_publish_more(interpreting, monkeypatch, status):
    factory, turn_id = interpreting
    clock = count(1)
    monkeypatch.setattr("mdi_api.infrastructure.interpretation.streaming.monotonic", lambda: next(clock))
    publisher = _publisher(factory, turn_id)
    publisher.feed(_finding_prefix(_output()["primary_findings"][0]))
    before = _events(factory, turn_id)
    with factory.engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status=status, row_version=5))
    with pytest.raises(ProviderStreamCancelled):
        publisher.feed(" ")
    assert _events(factory, turn_id) == before
    if status == "INTERPRETING":
        _publisher(factory, turn_id)
        assert _events(factory, turn_id)[-1]["event_type"] == "ASSISTANT_RESPONSE_RESET"


@pytest.mark.parametrize("repair", [False, True])
def test_service_reconciles_live_findings_to_one_valid_markdown_message(repair):
    factory, turn_id = _stalled_turn("RESULT_READY", age_minutes=0)
    snapshot = _saved_result(factory, turn_id)
    good = _output()
    bad = deepcopy(good)
    bad["supporting_findings"] = [{**deepcopy(good["primary_findings"][0]), "finding_id": "unsupported", "statement": "第一峰位于 999 angstrom。"}]

    class StreamingClient(FakeStructuredInterpreterClient):
        async def generate_structured(self, **kwargs):
            proposal = self.responses[min(self.calls, len(self.responses) - 1)]
            raw = json.dumps(proposal, ensure_ascii=False)
            callback = kwargs["request_context"]["on_interpretation_delta"]
            for index in range(0, len(raw), 17):
                callback(raw[index:index + 17])
            assert _deltas(factory, turn_id), "preview must arrive before provider completion"
            with factory.session() as session:
                assert session.agent2.research_turns.get(turn_id)["assistant_final_message_id"] is None
            return await super().generate_structured(**kwargs)

    client = StreamingClient([bad, good] if repair else good)
    try:
        row = ScientificInterpretationService(factory, client=client).process_turn(turn_id)
        assert row["grounding_status"] == "VALID" and row["repair_attempted"] is repair
        with factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            message = session.agent2.research_turns.get_message(turn["assistant_final_message_id"])
            assert turn["status"] == "COMPLETED"
            assert message["payload_json"]["responseFormat"] == "markdown"
            assert message["content_summary"].startswith("## RDF 解释\n\n")
            assert message["content_summary"].count("第一峰位于 2.5 angstrom。") == 1
            assert session.agent2.scientific_result_snapshots.get(snapshot["id"])["bundle_json"] == snapshot["bundle_json"]
        events = _events(factory, turn_id)
        resets = [event for event in events if event["event_type"] == "ASSISTANT_RESPONSE_RESET"]
        assert len(resets) == int(repair)
        assert len({item["response_id"] for item in _deltas(factory, turn_id)}) == 1 + int(repair)
        assert "999" not in json.dumps([item["text"] for item in _deltas(factory, turn_id)], ensure_ascii=False)
        assert sum(event["event_type"] == "INTERPRETATION_READY" for event in events) == 1
    finally:
        factory.engine.dispose()


def test_client_streams_and_redacts_before_final_structured_persistence(monkeypatch):
    secret = "local-fixture-credential"
    proposed = _output(f"第一峰位于 2.5 angstrom。 {secret}")
    proposed["title"] = f"RDF {secret}"
    observed = []

    class Provider:
        meta = SimpleNamespace(model="fixture")

        def complete_json(self, **kwargs):
            assert "on_content" in kwargs and kwargs["purpose"] == "GROUNDED_INTERPRETATION"
            assert secret not in str(kwargs["messages"])
            raw = json.dumps(proposed, ensure_ascii=False)
            for index in range(0, len(raw), 11):
                kwargs["on_content"](raw[index:index + 11])
            return PlannerRawResponse(raw_json=proposed, raw_text=raw, model="fixture", finish_reason="stop")

    provider = Provider()
    monkeypatch.setattr("mdi_api.user_models.selection_for_turn", lambda _turn: {"provider": "personal"})
    monkeypatch.setattr("mdi_api.user_models.resolve_user_selection", lambda *_args: (provider, PlannerUserConfig(provider="deepseek", model="fixture", api_key=secret)))
    result = asyncio.run(DeepSeekInterpreterClient(provider).generate_structured(
        input_payload={}, output_schema={}, timeout_seconds=10,
        request_context={"turn_id": str(uuid4()), "on_interpretation_delta": lambda delta, **kwargs: observed.append((delta, kwargs))},
    ))
    assert observed and all(item[1]["secret_values"] == (secret,) for item in observed)
    assert secret not in json.dumps(result.parsed) and "REDACTED" in json.dumps(result.parsed)


def test_secret_split_across_chunks_is_never_part_of_a_public_finding(interpreting):
    factory, turn_id = interpreting
    publisher = _publisher(factory, turn_id)
    secret = "local-fixture-credential"
    raw = _finding_prefix(_output(f"第一峰位于 2.5 angstrom。 {secret}")["primary_findings"][0])
    for index in range(0, len(raw), 9):
        publisher.feed(raw[index:index + 9], secret_values=(secret,))
    public = "".join(item["text"] for item in _deltas(factory, turn_id))
    assert "2.5 angstrom" in public and "REDACTED" in public and secret not in public


@pytest.mark.parametrize("status", ["CANCELED", "INTERPRETING"])
def test_service_stops_a_revoked_stream_without_repair_or_final(status, monkeypatch):
    factory, turn_id = _stalled_turn("RESULT_READY", age_minutes=0)
    snapshot = _saved_result(factory, turn_id)
    clock = count(1)
    monkeypatch.setattr("mdi_api.infrastructure.interpretation.streaming.monotonic", lambda: next(clock))

    class RevokedClient:
        calls = 0

        async def generate_structured(self, **kwargs):
            self.calls += 1
            feed = kwargs["request_context"]["on_interpretation_delta"]
            feed(_finding_prefix(_output()["primary_findings"][0]))
            assert _deltas(factory, turn_id)
            with factory.engine.begin() as connection:
                connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status=status, row_version=50))
            feed(" ")
            pytest.fail("revoked provider stream must stop")

    client = RevokedClient()
    try:
        with pytest.raises(InterpretationFailure) as failure:
            ScientificInterpretationService(factory, client=client).process_turn(turn_id)
        assert failure.value.code == "INTERPRETATION_CLAIM_LOST" and client.calls == 1
        with factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            assert turn["status"] == status and turn["row_version"] == 50
            assert turn["assistant_final_message_id"] is None
            assert session.agent2.interpretations.get_for_turn(turn_id) is None
            assert session.agent2.scientific_result_snapshots.get(snapshot["id"])["bundle_json"] == snapshot["bundle_json"]
        assert not any(event["event_type"] in {"TURN_FAILED", "INTERPRETATION_READY"} for event in _events(factory, turn_id))
    finally:
        factory.engine.dispose()


def test_repeated_invalid_whole_response_withdraws_preview_and_keeps_science():
    factory, turn_id = _stalled_turn("RESULT_READY", age_minutes=0)
    snapshot = _saved_result(factory, turn_id)

    class InvalidClient(FakeStructuredInterpreterClient):
        async def generate_structured(self, **kwargs):
            kwargs["request_context"]["on_interpretation_delta"](_finding_prefix(_output()["primary_findings"][0]))
            return await super().generate_structured(**kwargs)

    client = InvalidClient({**_output(), "unknown_output_field": "rejected"})
    try:
        with pytest.raises(InterpretationFailure) as failure:
            ScientificInterpretationService(factory, client=client).process_turn(turn_id)
        assert failure.value.code == "INTERPRETATION_SCHEMA_INVALID" and client.calls == 2
        public = [event for event in _events(factory, turn_id) if event["event_type"].startswith("ASSISTANT_RESPONSE_")]
        assert [event["event_type"] for event in public] == ["ASSISTANT_RESPONSE_DELTA", "ASSISTANT_RESPONSE_RESET"] * 2
        with factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            assert turn["status"] == "FAILED" and turn["assistant_final_message_id"] is None
            assert session.agent2.scientific_result_snapshots.get(snapshot["id"])["bundle_json"] == snapshot["bundle_json"]
    finally:
        factory.engine.dispose()


def test_non_streaming_provider_saves_its_answer_without_simulated_deltas():
    factory, turn_id = _stalled_turn("RESULT_READY", age_minutes=0)
    _saved_result(factory, turn_id)
    try:
        result = ScientificInterpretationService(factory, client=FakeStructuredInterpreterClient(_output())).process_turn(turn_id)
        assert result["grounding_status"] == "VALID"
        assert _deltas(factory, turn_id) == []
    finally:
        factory.engine.dispose()


def test_final_markdown_does_not_repeat_findings_joined_by_different_punctuation():
    proposal = _output()
    proposal["primary_findings"].append({**proposal["primary_findings"][0], "finding_id": "second", "statement": "保存的峰位是 2.5 angstrom。"})
    output = project_grounded_communication(ScientificInterpretationOutput.model_validate(proposal), _bundle())
    assert "；" in output.answer_lead
    content = AssistantResponseProjector().project(output, _bundle(), effective_relevance="CURRENT", markdown=True)
    assert all(content.count(item.statement) == 1 for item in output.primary_findings)
    assert content.count("2.5 angstrom") == 2
