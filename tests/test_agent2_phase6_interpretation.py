from __future__ import annotations

import os
import importlib.util
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import func, select, update

from mdi_api.db import analysis_plans, artifacts, jobs, scientific_result_snapshots, tool_calls
from mdi_api.interpretation.assembler import InterpreterInputAssembler
from mdi_api.interpretation.client import DeepSeekInterpreterClient, FakeStructuredInterpreterClient
from mdi_api.interpretation.grounding import validate_interpretation
from mdi_api.interpretation.schemas import ScientificInterpretationOutput
from mdi_api.interpretation.service import ScientificInterpretationService
from mdi_api.interpretation.queue import InMemoryInterpretationQueue
from mdi_api.research_agent.orchestration.processor import AgentTurnProcessor
from mdi_api.research_agent.registry_validation import build_default_agent2_registries
from mdi_api.scientific_objects.schemas import ScientificObjectRef
from mdi_api.scientific_results.schemas import ScientificResultBundle


def _bundle(*, execution_status: str = "SUCCESS") -> ScientificResultBundle:
    ref = ScientificObjectRef(object_id=uuid4(), version_id=uuid4(), project_id="project", object_type="structure.crystal")
    return ScientificResultBundle(
        schema_version="1.0", result_id=uuid4(), project_id="project", research_session_id="session", research_turn_id=uuid4(),
        research_question="Explain the RDF", source_object_refs=[ref], execution_status=execution_status, relevance_status="CURRENT",
        result_items=[{"id": "rdf.item", "result_type": "rdf_curve", "role": "PRIMARY", "title": "RDF", "artifact_ids": ["artifact-1"], "scientific_object_refs": [ref], "fact_refs": ["rdf.first_peak"], "evidence_refs": ["evidence.rdf"]}],
        facts=[{"fact_id": "rdf.first_peak", "predicate": "rdf.first_peak_position", "subject_ref": "structure:v1", "value": 2.5, "unit": "angstrom", "source": {"artifact_id": "artifact-1", "artifact_locator": "/summary/firstPeakPosition"}}],
        figures=[], tables=[], output_object_refs=[],
        evidence=[{"evidence_id": "evidence.rdf", "evidence_type": "structured_summary", "artifact_id": "artifact-1", "artifact_locator": "/summary"}],
        methods=[], limitations=[], warnings=[], provenance={"artifact_ids": ["artifact-1"]}, projection_version="agent2.result/1.0",
    )


def _output(statement: str = "第一峰位于 2.5 angstrom。", *, lead: str = "RDF 结果支持一个明确的第一峰。", fact: str = "rdf.first_peak") -> dict:
    return {"contract_version": "1.0", "title": "RDF 解释", "answer_lead": lead,
            "primary_findings": [{"finding_id": "finding-1", "statement": statement, "importance": "HIGH", "confidence": "HIGH", "fact_refs": [fact], "evidence_refs": ["evidence.rdf"], "result_item_refs": ["rdf.item"]}],
            "supporting_findings": [], "limitations": [], "primary_result_refs": ["rdf.item"], "supporting_result_refs": [], "follow_up_suggestions": []}


def test_grounding_rejects_unknown_refs_numeric_hallucination_and_unit_conversion():
    bundle = _bundle()
    unknown = ScientificInterpretationOutput.model_validate(_output(fact="missing.fact"))
    assert not validate_interpretation(unknown, bundle).valid
    hallucinated = ScientificInterpretationOutput.model_validate(_output("第一峰位于 23 angstrom。"))
    assert not validate_interpretation(hallucinated, bundle).valid
    converted = ScientificInterpretationOutput.model_validate(_output("第一峰位于 0.25 nm。"))
    assert not validate_interpretation(converted, bundle).valid
    answer_lead = ScientificInterpretationOutput.model_validate(_output(lead="有 42 个峰。"))
    assert not validate_interpretation(answer_lead, bundle).valid
    angstrom_symbol = ScientificInterpretationOutput.model_validate(_output("A peak is recorded at 2.5 Å."))
    assert validate_interpretation(angstrom_symbol, bundle).valid


def test_grounding_ignores_opaque_provenance_identifiers_in_answer_lead():
    bundle = _bundle()
    lead = (
        "结果 440636e5-d4e6-4410-b2e4-6909399cde82 的第一峰位于 2.5 angstrom，"
        "依据 fact.rdf.first_peak 和 evidence.evidence.rdf。"
    )
    result = ScientificInterpretationOutput.model_validate(_output(lead=lead))
    assert validate_interpretation(result, bundle).valid


def test_grounding_does_not_treat_lowercase_k_labels_as_kelvin_units():
    base = _bundle()
    bundle = base.model_copy(update={"facts": [*base.facts, {"fact_id": "rdf.kpoint_count", "predicate": "electronic.kpoint_count", "subject_ref": "structure:v1", "value": 81, "unit": "count", "source": {"artifact_id": "artifact-1", "artifact_locator": "/summary/kpointCount"}}]})
    result = ScientificInterpretationOutput.model_validate(
        _output(statement="该结果包含 81 k 点。", fact="rdf.kpoint_count")
    )
    # The statement intentionally has no measured unit; ``k`` is a path label.
    assert validate_interpretation(result, bundle).valid


def test_partial_result_cannot_be_presented_as_complete():
    result = ScientificInterpretationOutput.model_validate(_output(statement="完整分析已完成，第一峰位于 2.5 angstrom。"))
    assert not validate_interpretation(result, _bundle(execution_status="PARTIAL")).valid


def test_interpreter_input_is_bounded_and_excludes_raw_artifacts():
    bundle = _bundle()
    envelope, fingerprint = InterpreterInputAssembler().assemble(bundle=bundle, question="Explain the RDF", relevance_status="STALE")
    assert fingerprint
    assert envelope.result["relevance_status"] == "STALE"
    assert "artifact_payloads" not in envelope.result
    assert "evidence" not in envelope.result
    assert envelope.result["facts"][0]["fact_id"] == "rdf.first_peak"


def test_interpreter_input_records_every_truncated_supporting_item():
    bundle = _bundle()
    fact = bundle.facts[0]
    evidence = bundle.evidence[0]
    expanded = bundle.model_copy(update={"facts": [fact] * 66, "evidence": [evidence] * 66})
    envelope, _fingerprint = InterpreterInputAssembler().assemble(bundle=expanded, question="Explain the RDF", relevance_status="CURRENT")
    assert len(envelope.result["facts"]) == 64
    assert len(envelope.evidence) == 64
    assert envelope.omitted_supporting_items == [
        "fact:rdf.first_peak",
        "fact:rdf.first_peak",
        "evidence:evidence.rdf",
        "evidence:evidence.rdf",
    ]


def test_schema_invalid_response_gets_one_bounded_repair():
    client = FakeStructuredInterpreterClient([{"bad": True}, _output()])
    service = ScientificInterpretationService(repository_factory=None, client=client)  # type: ignore[arg-type]
    result, repaired, _meta = service._generate_with_one_repair(InterpreterInputAssembler().assemble(bundle=_bundle(), question="Explain the RDF", relevance_status="CURRENT")[0], _bundle())
    assert result.title == "RDF 解释"
    assert repaired is True
    assert client.calls == 2


def test_schema_invalid_after_repair_is_not_accepted():
    client = FakeStructuredInterpreterClient([{"bad": True}, {"still": "bad"}])
    service = ScientificInterpretationService(repository_factory=None, client=client)  # type: ignore[arg-type]
    with pytest.raises(Exception) as exc:
        service._generate_with_one_repair(InterpreterInputAssembler().assemble(bundle=_bundle(), question="Explain the RDF", relevance_status="CURRENT")[0], _bundle())
    assert getattr(exc.value, "code", "") == "INTERPRETATION_SCHEMA_INVALID"
    assert client.calls == 2


def test_interpretation_queue_is_identity_only_and_idempotent():
    queue = InMemoryInterpretationQueue()
    turn_id = uuid4()
    first = queue.enqueue_turn(turn_id)
    second = queue.enqueue_turn(turn_id)
    assert first.enqueued is True
    assert second.enqueued is False
    assert queue.pop_next() == turn_id


def test_previous_result_interpretation_reuses_one_snapshot_across_new_turns_without_execution():
    phase2_path = Path(__file__).resolve().parent / "test_agent2_phase2_processor.py"
    spec = importlib.util.spec_from_file_location("agent2_phase2_fixture", phase2_path)
    assert spec is not None and spec.loader is not None
    phase2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(phase2)
    engine, owner, factory, _objects, turns = phase2.foundation()
    previous_turn_id, snapshot_id = phase2.add_previous_result(factory)
    payload = _bundle().model_dump(mode="json")
    payload.update({"project_id": "project", "research_session_id": "session", "research_turn_id": str(previous_turn_id), "source_object_refs": []})
    payload["result_items"][0]["scientific_object_refs"] = []
    with engine.begin() as connection:
        connection.execute(update(scientific_result_snapshots).where(scientific_result_snapshots.c.id == snapshot_id).values(bundle_json=payload))

    def counts() -> dict[str, int]:
        with engine.connect() as connection:
            return {
                "plans": connection.execute(select(func.count()).select_from(analysis_plans)).scalar_one(),
                "jobs": connection.execute(select(func.count()).select_from(jobs)).scalar_one(),
                "tools": connection.execute(select(func.count()).select_from(tool_calls)).scalar_one(),
                "artifacts": connection.execute(select(func.count()).select_from(artifacts)).scalar_one(),
                "snapshots": connection.execute(select(func.count()).select_from(scientific_result_snapshots)).scalar_one(),
            }

    before = counts()
    for question in ("解释刚才 RDF 第一峰。", "再说明一下刚才的 RDF 结果。"):
        turn = phase2.receive(turns, owner, question)
        queue = InMemoryInterpretationQueue()
        orchestrator = phase2.FakeStructuredClient([phase2.decision(
            "INTERPRET_RESULT",
            assistant_message="已识别已有 RDF 结果，准备解释。",
            reusable_result_ref_keys=["result_1"],
        )])
        processor = AgentTurnProcessor(
            repository_factory=factory,
            registries=build_default_agent2_registries(),
            llm_client=orchestrator,
            interpretation_queue=queue,
        )
        assert __import__("asyncio").run(processor.process(turn.turn_id)).status == "ORCHESTRATING"
        assert queue.pop_next() == turn.turn_id
        row = ScientificInterpretationService(factory, client=FakeStructuredInterpreterClient(_output())).process_turn(turn.turn_id)
        assert row["result_snapshot_id"] == snapshot_id
        with factory.session() as session:
            stored_turn = session.agent2.research_turns.get(turn.turn_id)
            assert stored_turn["status"] == "COMPLETED"
            assert stored_turn["assistant_final_message_id"]
    assert counts() == before


@pytest.mark.live_llm
@pytest.mark.skipif(os.getenv("MDI_RUN_AGENT2_LIVE") != "1" or not os.getenv("DEEPSEEK_KEY"), reason="live DeepSeek qualification is explicitly gated")
def test_live_deepseek_interpretation_is_grounded():
    bundle = _bundle()
    envelope = InterpreterInputAssembler().assemble(bundle=bundle, question="解释 RDF 第一峰。", relevance_status="CURRENT")[0]
    service = ScientificInterpretationService(repository_factory=None, client=DeepSeekInterpreterClient(), timeout_seconds=120)  # type: ignore[arg-type]
    result, _repaired, _meta = service._generate_with_one_repair(envelope, bundle)
    validation = validate_interpretation(result, bundle)
    assert validation.valid, validation.errors
