from __future__ import annotations

import json
import os
import importlib.util
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import func, select, update

from mdi_api.db import analysis_plans, artifacts, jobs, scientific_result_snapshots, tool_calls
from mdi_api.interpretation.assembler import InterpreterInputAssembler
from mdi_api.interpretation.client import DeepSeekInterpreterClient, FakeStructuredInterpreterClient
from mdi_api.interpretation.grounding import (
    build_grounding_repair_context,
    project_grounded_answer_lead,
    project_claim_support_assessments,
    project_grounded_communication,
    validate_interpretation,
)
from mdi_api.interpretation.schemas import ScientificFinding, ScientificInterpretationOutput
from mdi_api.interpretation.service import ScientificInterpretationService
from mdi_api.interpretation.queue import InMemoryInterpretationQueue
from mdi_api.research_agent.orchestration.processor import AgentTurnProcessor
from mdi_api.research_agent.registry_validation import build_default_agent2_registries
from mdi_api.research_agent.context.policy import (
    ContextOperation,
    context_budget_policy,
)
from mdi_api.routers.research import _scientific_message_projections
from mdi_api.scientific_objects.schemas import ScientificObjectRef
from mdi_api.scientific_results.schemas import ScientificFigure, ScientificResultBundle


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


def _multi_source_bundle():
    from copy import deepcopy
    payload = _bundle().model_dump(mode="json")
    source_a = {**payload["source_object_refs"][0], "display_name": "Si.cif"}
    source_b = {**source_a, "object_id": str(uuid4()), "version_id": str(uuid4()), "display_name": "Cu.cif"}
    item_a = {**payload["result_items"][0], "scientific_object_refs": [source_a]}
    item_b = {**deepcopy(item_a), "id": "rdf.b", "scientific_object_refs": [source_b], "artifact_ids": ["artifact-b"], "fact_refs": ["rdf.b.density"], "evidence_refs": []}
    fact_b = {**payload["facts"][0], "fact_id": "rdf.b.density", "subject_ref": "b", "value": 4.5, "source": {"artifact_id": "artifact-b", "artifact_locator": "/value"}}
    payload.update(source_object_refs=[source_a, source_b], result_items=[item_a, item_b], facts=[*payload["facts"], fact_b])
    payload["provenance"]["artifact_ids"].append("artifact-b")
    return ScientificResultBundle.model_validate(payload)


def test_interpreter_preserves_exact_material_labels_after_compaction():
    envelope, _ = InterpreterInputAssembler().assemble(bundle=_multi_source_bundle(), question="Compare", relevance_status="CURRENT")
    assert [item["source_labels"] for item in envelope.result["result_items"]] == [["Si.cif"], ["Cu.cif"]]
    assert envelope.result["result_items"][0]["fact_refs"] == ["rdf.first_peak"]


@pytest.mark.parametrize("statement,all_refs,valid", [
    ("Si.cif 的峰位为 2.5 angstrom。", False, True),
    ("Cu.cif 的峰位为 2.5 angstrom。", False, False),
    ("Unknown.cif 的峰位为 2.5 angstrom。", False, False),
    ("Si.cif 为 2.5 angstrom，Cu.cif 为 4.5 angstrom。", True, True),
    ("Si.cif 为 4.5 angstrom，Cu.cif 为 2.5 angstrom。", True, False),
])
def test_material_name_and_value_cannot_borrow_another_sources_citations(statement, all_refs, valid):
    output = ScientificInterpretationOutput.model_validate(_output(statement))
    if all_refs:
        output.primary_findings[0].fact_refs.append("rdf.b.density")
        output.primary_findings[0].result_item_refs.append("rdf.b")
        output.answer_lead = "Si.cif 为 2.5 angstrom，Cu.cif 为 4.5 angstrom。"
    result = validate_interpretation(output, _multi_source_bundle())
    assert result.valid is valid, result.errors
    if not valid:
        assert any("source" in error for error in result.errors)


def _field_bundle(quantity="electron_localization_function"):
    from mdi_api.application.scientific_results.projectors.volumetric import volumetric_field_limitations

    bundle = _bundle()
    bundle.result_items[0].result_type = "volumetric.field"
    bundle.limitations = volumetric_field_limitations("artifact-1", {"quantity": quantity})
    return bundle


@pytest.mark.parametrize("quantity,incorrect", [
    ("electron_localization_function", "使用 Bader 分析处理该 ELF 场以获得电子计数。"),
    ("electron_localization_function", "Integrate ELF basins to obtain their electron populations."),
    ("electron_localization_function", "Use an unrelated method to prove the bond type."),
    ("orbital_density", "通过等值面的面积分得到内部电子数。"),
    ("orbital_density", "将整胞积分解释为 HOMO 轨道占据数。"),
])
def test_volumetric_follow_up_proposals_cannot_bypass_grounding(quantity, incorrect):
    bundle = _field_bundle(quantity)
    output = ScientificInterpretationOutput.model_validate({**_output(), "follow_up_suggestions": [incorrect]})
    before = output.model_dump(mode="json")
    assert any("follow_up_suggestions" in error for error in validate_interpretation(output, bundle).errors)
    live = project_grounded_communication(output, bundle, project_suggestions=False)
    assert not validate_interpretation(live, bundle).valid
    historical = project_grounded_communication(output, bundle)
    assert historical.follow_up_suggestions == []
    assert historical.primary_findings[0].statement == output.primary_findings[0].statement
    assert output.model_dump(mode="json") == before


def test_volumetric_follow_up_choices_are_scoped_to_exact_saved_limitations():
    from mdi_api.application.scientific_reasoning.follow_ups import follow_up_policy

    elf = _field_bundle()
    partial = _field_bundle("orbital_density")
    policy = follow_up_policy(elf)
    assert policy is not None and len(policy["options"]) == 2
    assert {ref for item in policy["options"] for ref in item["limitation_refs"]} == {
        item.limitation_id for item in elf.limitations
    }
    suggestion = "若需要电子数或盆布居，需补充相应的电子密度数据和布居分析结果；当前 ELF 场及其体积分不能替代这些证据。"
    output = ScientificInterpretationOutput.model_validate({**_output(), "follow_up_suggestions": [suggestion]})
    assert validate_interpretation(output, elf).valid
    assert not validate_interpretation(output, partial).valid
    elf.limitations = []
    assert follow_up_policy(elf)["options"] == []
    assert not validate_interpretation(output, elf).valid
    assert validate_interpretation(ScientificInterpretationOutput.model_validate(_output()), elf).valid
    assert follow_up_policy(_bundle()) is None


@pytest.mark.parametrize("repair_succeeds", [True, False])
def test_unsupported_follow_up_requires_real_provider_repair(repair_succeeds):
    from mdi_api.interpretation.service import InterpretationFailure

    bundle = _field_bundle()
    envelope, _ = InterpreterInputAssembler().assemble(bundle=bundle, question="解释场数据", relevance_status="CURRENT")
    allowed = envelope.result["follow_up_policy"]["options"][0]["text"]
    invalid = {**_output(), "follow_up_suggestions": ["Use Bader on ELF to count electrons."]}
    valid = {**_output(), "follow_up_suggestions": [allowed]}
    contexts = []

    class RecordingClient(FakeStructuredInterpreterClient):
        async def generate_structured(self, **kwargs):
            contexts.append(kwargs["request_context"])
            choices = kwargs["output_schema"]["properties"]["follow_up_suggestions"]["items"]["enum"]
            assert allowed in choices and invalid["follow_up_suggestions"][0] not in choices
            return await super().generate_structured(**kwargs)

    client = RecordingClient([invalid, valid if repair_succeeds else invalid])
    service = ScientificInterpretationService(repository_factory=None, client=client)
    if repair_succeeds:
        output, repaired, _ = service._generate_with_one_repair(envelope, bundle)
        assert repaired and output.follow_up_suggestions == [allowed]
    else:
        with pytest.raises(InterpretationFailure, match="follow_up_suggestions"):
            service._generate_with_one_repair(envelope, bundle)
    assert client.calls == 2
    assert any("follow_up_suggestions" in text for text in contexts[1]["repair"]["validation_errors"])
    assert "Use Bader" not in json.dumps(contexts)


def test_femtosecond_symbol_preserves_grounding_without_accepting_picosecond_conversion():
    bundle = _bundle()
    bundle.facts[0].unit = "femtosecond"
    output = ScientificInterpretationOutput.model_validate(_output("所选帧的时间为 2.5 fs。"))
    assert validate_interpretation(output, bundle).valid
    converted = ScientificInterpretationOutput.model_validate(_output("所选帧的时间为 2.5 ps。"))
    assert not validate_interpretation(converted, bundle).valid


@pytest.mark.parametrize("display_unit", ["electron/angstrom^3", "electron/Å^3", "electrons / Å^{3}", "电子/Å³"])
def test_density_units_are_checked_as_whole_units_without_losing_the_numerator(display_unit):
    bundle = _bundle()
    bundle.facts[0].predicate = "volumetric.minimum"
    bundle.facts[0].unit = "electron/angstrom^3"
    output = ScientificInterpretationOutput.model_validate(_output(f"密度为 2.5 {display_unit}。"))
    assert validate_interpretation(output, bundle).valid
    bundle.facts[0].unit = "angstrom"
    assert not validate_interpretation(output, bundle).valid


@pytest.mark.parametrize("wrong_unit", ["Å³", "Å^-3", "electron/bohr^3", "electron/nm³", "elementary_charge/Å^3", "bohr_magneton/Å³"])
def test_density_grounding_rejects_other_quantities_and_spatial_units(wrong_unit):
    bundle = _bundle()
    bundle.facts[0].predicate = "volumetric.minimum"
    bundle.facts[0].unit = "electron/angstrom^3"
    output = ScientificInterpretationOutput.model_validate(_output(f"数值为 2.5 {wrong_unit}。"))
    assert any("unit is absent" in error for error in validate_interpretation(output, bundle).errors)


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


@pytest.mark.parametrize("statement", [
    "回归评估指标已计算，包括 MAE、RMSE、R²。",
    "已生成真实值与预测值的对比散点图及残差图。",
    "已列出绝对误差最大的样本及其 sample_id 和 formula。",
    "MAE was computed; RMSE was not computed.",
    "未计算 RMSE，但 MAE 已计算。",
    "没有训练模型，MAE 已计算。",
])
def test_derived_completion_requires_scoped_scientific_support(statement):
    bundle = _bundle()
    bundle.facts = []
    bundle.result_items[0].fact_refs = []
    bundle.result_items[0].result_type = "data.table_analysis"
    output = _output(statement, lead=statement)
    output["primary_findings"][0]["fact_refs"] = []
    validation = validate_interpretation(ScientificInterpretationOutput.model_validate(output), bundle)
    assert not validation.valid
    assert any("derived product" in error for error in validation.errors)


@pytest.mark.parametrize("statement", [
    "未计算 MAE、RMSE 和 R²。",
    "MAE、RMSE、R² 未计算。",
    "MAE and RMSE were not computed.",
    "No MAE or RMSE is available.",
    "未生成残差图。",
    "已生成普通表格散点图。",
])
def test_unavailable_derived_products_and_generic_views_are_not_false_completion(statement):
    bundle = _bundle()
    bundle.facts = []
    bundle.result_items[0].fact_refs = []
    output = _output(statement, lead=statement)
    output["primary_findings"][0]["fact_refs"] = []
    assert validate_interpretation(ScientificInterpretationOutput.model_validate(output), bundle).valid


@pytest.mark.parametrize("statement", [
    "R² 未定义（目标值为常量）。", "R² is undefined (constant target).",
    "R²状态为undefined_constant_target，因为目标变量为常数，无法定义R²。",
    "由于目标变量为常数，R²无法定义，因此不适用作为该合成测试集的评估指标。",
    "R²不可定义。", "不可定义 R²。",
])
def test_undefined_r2_requires_its_saved_status(statement):
    bundle = _bundle()
    bundle.facts[0].predicate = "ml.r2_status"
    bundle.facts[0].value = "undefined_constant_target"
    bundle.facts[0].unit = None
    output = ScientificInterpretationOutput.model_validate(_output(statement, lead=statement))
    assert validate_interpretation(output, bundle).valid
    bundle.facts[0].value = "defined"
    assert not validate_interpretation(output, bundle).valid


@pytest.mark.parametrize("statement", [
    "R² = 1。", "R² 未定义（目标值为常量），R² = 1。", "R² 已计算。",
    "R²状态为undefined_constant_target，但R²为1。",
    "R²无法定义，R²为0。", "无法定义R²，R²已计算。",
    "R²状态为undefined_constant_target_other。",
])
def test_undefined_r2_status_does_not_support_numeric_or_completion_claims(statement):
    bundle = _bundle()
    bundle.facts[0].predicate = "ml.r2_status"
    bundle.facts[0].value = "undefined_constant_target"
    bundle.facts[0].unit = None
    output = ScientificInterpretationOutput.model_validate(_output(statement, lead=statement))
    assert not validate_interpretation(output, bundle).valid


def test_named_metric_support_cannot_borrow_an_uncited_result():
    bundle = _bundle()
    bundle.facts[0].predicate = "ml.mae"
    bundle.result_items.append(bundle.result_items[0].model_copy(update={"id": "unrelated", "fact_refs": []}))
    output = _output("MAE 已计算。", lead="MAE 已计算。")
    output["primary_findings"][0].update(fact_refs=[], evidence_refs=[], result_item_refs=["unrelated"])
    assert not validate_interpretation(ScientificInterpretationOutput.model_validate(output), bundle).valid
    output["primary_findings"][0]["result_item_refs"] = ["rdf.item"]
    assert validate_interpretation(ScientificInterpretationOutput.model_validate(output), bundle).valid


@pytest.mark.parametrize("repair_succeeds", [True, False])
def test_false_metric_completion_requires_provider_repair(repair_succeeds):
    from mdi_api.interpretation.service import InterpretationFailure

    bundle = _bundle()
    bundle.facts = []
    bundle.result_items[0].fact_refs = []
    invalid = _output("MAE 已计算。", lead="MAE 已计算。")
    invalid["primary_findings"][0]["fact_refs"] = []
    valid = _output("未计算 MAE。", lead="未计算 MAE。")
    valid["primary_findings"][0]["fact_refs"] = []
    envelope, _ = InterpreterInputAssembler().assemble(bundle=bundle, question="评估预测误差", relevance_status="CURRENT")
    client = FakeStructuredInterpreterClient([invalid, valid if repair_succeeds else invalid])
    service = ScientificInterpretationService(repository_factory=None, client=client)
    if repair_succeeds:
        output, repaired, _ = service._generate_with_one_repair(envelope, bundle)
        assert repaired and output.primary_findings[0].statement == "未计算 MAE。"
    else:
        with pytest.raises(InterpretationFailure, match="derived product"):
            service._generate_with_one_repair(envelope, bundle)
    assert client.calls == 2


def test_historical_invalid_interpretation_is_rejected_by_read_and_report_admission(monkeypatch):
    from contextlib import nullcontext
    from types import SimpleNamespace
    from mdi_api.transport.routers import agent2
    from mdi_api.scientific_reports.requests import ScientificReportRequestService
    from mdi_api.scientific_reports.service import ScientificReportError

    bundle = _bundle()
    output = _output("MAE 已计算。", lead="MAE 已计算。")
    row = {"id": uuid4(), "grounding_status": "VALID", "result_snapshot_id": uuid4(), "output_json": {"interpretation": output, "message": "MAE 已计算。"}}
    snapshot = {"project_id": "project", "bundle_json": bundle.model_dump(mode="json")}
    before = json.dumps([row, snapshot], default=str)
    unit = SimpleNamespace(connection=None, agent2=SimpleNamespace(
        research_turns=SimpleNamespace(get=lambda _id: {"id": bundle.research_turn_id, "project_id": "project"}),
        interpretations=SimpleNamespace(get_for_turn=lambda _id: row),
        scientific_result_snapshots=SimpleNamespace(get=lambda _id: snapshot),
    ))
    factory = SimpleNamespace(session=lambda: nullcontext(unit), unit_of_work=lambda: nullcontext(unit))
    monkeypatch.setattr(agent2, "create_repository_factory", lambda: factory)
    monkeypatch.setattr(agent2, "require_project_access", lambda *args, **kwargs: None)
    view = agent2.get_research_turn_interpretation(bundle.research_turn_id, current_user=None)
    assert view["status"] == "REJECTED" and view["interpretation"] is None
    assert "未通过当前事实校验" in view["message"]
    assert agent2._current_interpretation_warning(unit, {"id": bundle.research_turn_id, "project_id": "project", "status": "COMPLETED"})["code"] == "INTERPRETATION_GROUNDING_REJECTED"
    # No generation repository or queue is supplied: rejection must precede
    # both persistent admission and provider dispatch.
    with pytest.raises(ScientificReportError) as error:
        ScientificReportRequestService(factory).request(bundle.research_turn_id, requested_by="user")
    assert error.value.code == "REPORT_INTERPRETATION_REJECTED"
    assert json.dumps([row, snapshot], default=str) == before


def test_grounding_ignores_list_prefixes_and_viewer_dimension_labels() -> None:
    payload = _output(
        statement="1. 该 3D 结构 viewer 场景已生成。",
        fact="rdf.first_peak",
    )
    payload["primary_findings"][0]["fact_refs"] = []
    payload["primary_findings"][0]["evidence_refs"] = []
    payload["primary_findings"][0]["result_item_refs"] = ["rdf.item"]
    result = ScientificInterpretationOutput.model_validate(payload)

    assert validate_interpretation(result, _bundle()).valid


def test_grounding_normalizes_inverse_cubic_angstrom_notation_without_converting_units() -> None:
    payload = _bundle().model_dump(mode="json")
    payload["facts"][0].update(
        {
            "fact_id": "rdf.number_density",
            "predicate": "rdf.number_density",
            "value": 0.037037,
            "unit": "angstrom^-3",
            "source": {
                "artifact_id": "artifact-1",
                "artifact_locator": "/rdf/normalization/number_density_per_angstrom3",
            },
        }
    )
    payload["result_items"][0]["fact_refs"] = ["rdf.number_density"]
    bundle = ScientificResultBundle.model_validate(payload)

    grounded = ScientificInterpretationOutput.model_validate(
        _output(
            statement="数密度为 0.037037 Å⁻³。",
            fact="rdf.number_density",
        )
    )
    converted = ScientificInterpretationOutput.model_validate(
        _output(
            statement="数密度为 0.037037 nm^-3。",
            fact="rdf.number_density",
        )
    )

    assert validate_interpretation(grounded, bundle).valid
    assert not validate_interpretation(converted, bundle).valid


def test_grounding_normalizes_terahertz_name_and_symbol_without_converting_units() -> None:
    payload = _bundle().model_dump(mode="json")
    payload["facts"][0].update(
        {
            "fact_id": "phonon.frequency_max",
            "predicate": "phonon.frequency_max",
            "value": 2.5,
            "unit": "terahertz",
            "source": {
                "artifact_id": "artifact-1",
                "artifact_locator": "/frequency_max",
            },
        }
    )
    payload["result_items"][0]["fact_refs"] = ["phonon.frequency_max"]
    bundle = ScientificResultBundle.model_validate(payload)

    grounded = ScientificInterpretationOutput.model_validate(
        _output(
            statement="最高频率为 2.5 THz。",
            fact="phonon.frequency_max",
        )
    )
    converted = ScientificInterpretationOutput.model_validate(
        _output(
            statement="最高频率为 2.5 eV。",
            fact="phonon.frequency_max",
        )
    )

    assert validate_interpretation(grounded, bundle).valid
    assert not validate_interpretation(converted, bundle).valid


def test_diffusion_fit_window_and_composite_units_remain_fail_closed() -> None:
    payload = _bundle().model_dump(mode="json")
    payload["facts"] = [
        {
            "fact_id": "trajectory.diffusion_coefficient",
            "predicate": "trajectory.diffusion_coefficient",
            "subject_ref": "artifact-1",
            "value": 0.038618084156,
            "unit": "angstrom^2/picosecond",
            "source": {
                "artifact_id": "artifact-1",
                "artifact_locator": "/diffusionEstimate/value",
            },
        },
        {
            "fact_id": "trajectory.diffusion_fit_start_time",
            "predicate": "trajectory.diffusion_fit_start_time",
            "subject_ref": "artifact-1",
            "value": 1.0,
            "unit": "picosecond",
            "source": {
                "artifact_id": "artifact-1",
                "artifact_locator": "/fitWindow/startPs",
            },
        },
        {
            "fact_id": "trajectory.diffusion_fit_end_time",
            "predicate": "trajectory.diffusion_fit_end_time",
            "subject_ref": "artifact-1",
            "value": 6.0,
            "unit": "picosecond",
            "source": {
                "artifact_id": "artifact-1",
                "artifact_locator": "/fitWindow/endPs",
            },
        },
    ]
    payload["result_items"][0]["fact_refs"] = [
        item["fact_id"] for item in payload["facts"]
    ]
    payload["evidence"][0]["supports_fact_refs"] = [
        item["fact_id"] for item in payload["facts"]
    ]
    bundle = ScientificResultBundle.model_validate(payload)
    output = _output(
        statement=(
            "在 1–6 ps 拟合窗口内，扩散系数为 "
            "0.038618084156 angstrom^2/picosecond。"
        ),
        fact="trajectory.diffusion_coefficient",
    )
    output["primary_findings"][0]["fact_refs"] = [
        "trajectory.diffusion_coefficient",
        "trajectory.diffusion_fit_start_time",
        "trajectory.diffusion_fit_end_time",
    ]
    grounded = ScientificInterpretationOutput.model_validate(output)

    assert validate_interpretation(grounded, bundle).valid

    unsupported_payload = grounded.model_dump(mode="json")
    unsupported_payload["primary_findings"][0]["statement"] = (
        "在 1–8 ps 拟合窗口内，扩散系数为 "
        "0.038618084156 angstrom^2/picosecond。"
    )
    unsupported = ScientificInterpretationOutput.model_validate(
        unsupported_payload
    )
    validation = validate_interpretation(unsupported, bundle)
    assert not validation.valid
    assert any("(8)" in error for error in validation.errors)

    converted_payload = grounded.model_dump(mode="json")
    converted_payload["primary_findings"][0]["statement"] = (
        "在 1–6 ps 拟合窗口内，扩散系数为 "
        "0.038618084156 m^2/s。"
    )
    converted = ScientificInterpretationOutput.model_validate(converted_payload)
    assert not validate_interpretation(converted, bundle).valid


def test_grounding_accepts_bounded_display_rounding_but_rejects_unrelated_values() -> None:
    payload = _bundle().model_dump(mode="json")
    payload["facts"] = [
        {
            "fact_id": "trajectory.diffusion_coefficient",
            "predicate": "trajectory.diffusion_coefficient",
            "subject_ref": "artifact-1",
            "value": 0.038618084156,
            "unit": "angstrom^2/picosecond",
            "source": {
                "artifact_id": "artifact-1",
                "artifact_locator": "/diffusionEstimate/value",
            },
        },
        {
            "fact_id": "trajectory.diffusion_fit_r_squared",
            "predicate": "trajectory.diffusion_fit_r_squared",
            "subject_ref": "artifact-1",
            "value": 0.970301847945,
            "unit": None,
            "source": {
                "artifact_id": "artifact-1",
                "artifact_locator": "/fitQuality/r2",
            },
        },
    ]
    payload["result_items"][0]["fact_refs"] = [
        item["fact_id"] for item in payload["facts"]
    ]
    bundle = ScientificResultBundle.model_validate(payload)
    rounded = ScientificInterpretationOutput.model_validate(
        _output(
            statement=(
                "扩散系数为 0.0386 angstrom^2/picosecond，"
                "拟合 R² 为 0.9703。"
            ),
            fact="trajectory.diffusion_coefficient",
        )
    )
    rounded.primary_findings[0].fact_refs = [
        "trajectory.diffusion_coefficient",
        "trajectory.diffusion_fit_r_squared",
    ]
    assert validate_interpretation(rounded, bundle).valid

    ascii_r_squared_payload = rounded.model_dump(mode="json")
    ascii_r_squared_payload["primary_findings"][0]["statement"] = (
        "扩散系数为 0.0386 angstrom^2/picosecond，"
        "拟合 R^2 为 0.9703。"
    )
    ascii_r_squared = ScientificInterpretationOutput.model_validate(
        ascii_r_squared_payload
    )
    assert validate_interpretation(ascii_r_squared, bundle).valid

    unsupported_payload = rounded.model_dump(mode="json")
    unsupported_payload["primary_findings"][0]["statement"] = (
        "扩散系数为 0.038 angstrom^2/picosecond，拟合 R² 为 0.9703。"
    )
    unsupported = ScientificInterpretationOutput.model_validate(unsupported_payload)
    assert not validate_interpretation(unsupported, bundle).valid

    materially_rounded_payload = rounded.model_dump(mode="json")
    materially_rounded_payload["primary_findings"][0]["statement"] = (
        "扩散系数为 0.04 angstrom^2/picosecond，拟合 R² 为 0.9703。"
    )
    materially_rounded = ScientificInterpretationOutput.model_validate(
        materially_rounded_payload
    )
    assert not validate_interpretation(materially_rounded, bundle).valid


def test_quantitative_grounding_follows_bounded_result_and_evidence_fact_edges() -> None:
    bundle_payload = _bundle().model_dump(mode="json")
    bundle_payload["evidence"][0]["supports_fact_refs"] = ["rdf.first_peak"]
    bundle_payload["evidence"][0]["supports_result_item_refs"] = ["rdf.item"]
    bundle = ScientificResultBundle.model_validate(bundle_payload)

    through_result_item = _output()
    through_result_item["primary_findings"][0]["fact_refs"] = []
    result_item_interpretation = ScientificInterpretationOutput.model_validate(
        through_result_item
    )
    assert validate_interpretation(result_item_interpretation, bundle).valid

    through_evidence = _output()
    through_evidence["primary_findings"][0]["fact_refs"] = []
    through_evidence["primary_findings"][0]["result_item_refs"] = []
    evidence_interpretation = ScientificInterpretationOutput.model_validate(
        through_evidence
    )
    assert validate_interpretation(evidence_interpretation, bundle).valid

    unsupported = _output("第一峰位于 23 angstrom。")
    unsupported["primary_findings"][0]["fact_refs"] = []
    unsupported_interpretation = ScientificInterpretationOutput.model_validate(
        unsupported
    )
    validation = validate_interpretation(unsupported_interpretation, bundle)
    assert not validation.valid
    assert any("(23)" in error for error in validation.errors)


def test_quantitative_grounding_follows_result_item_to_evidence_to_fact_edges() -> None:
    payload = _bundle().model_dump(mode="json")
    payload["result_items"][0]["fact_refs"] = []
    payload["result_items"][0]["evidence_refs"] = ["evidence.rdf"]
    payload["evidence"][0]["supports_fact_refs"] = ["rdf.first_peak"]
    payload["evidence"][0]["supports_result_item_refs"] = ["rdf.item"]
    bundle = ScientificResultBundle.model_validate(payload)

    output = _output()
    output["primary_findings"][0]["fact_refs"] = []
    output["primary_findings"][0]["evidence_refs"] = []
    grounded = ScientificInterpretationOutput.model_validate(output)

    assert validate_interpretation(grounded, bundle).valid


def test_result_item_reference_is_a_valid_grounding_root_for_qualitative_finding() -> None:
    output = _output(statement="The supplied RDF result is available.")
    output["primary_findings"][0]["fact_refs"] = []
    output["primary_findings"][0]["evidence_refs"] = []
    grounded = ScientificInterpretationOutput.model_validate(output)

    assert validate_interpretation(grounded, _bundle()).valid


def test_factless_structure_viewer_allows_only_qualitative_scene_language() -> None:
    payload = _bundle().model_dump(mode="json")
    payload["result_items"][0].update(
        {
            "id": "structure.viewer",
            "result_type": "structure.viewer_scene",
            "title": "Structure viewer scene",
            "fact_refs": [],
            "evidence_refs": [],
        }
    )
    payload["facts"] = []
    payload["evidence"] = []
    bundle = ScientificResultBundle.model_validate(payload)

    qualitative = _output(
        statement="结构查看器场景已生成，可在 viewer 中打开。",
    )
    qualitative["primary_findings"][0].update(
        {
            "fact_refs": [],
            "evidence_refs": [],
            "result_item_refs": ["structure.viewer"],
        }
    )
    qualitative["primary_result_refs"] = ["structure.viewer"]
    assert validate_interpretation(
        ScientificInterpretationOutput.model_validate(qualitative),
        bundle,
    ).valid

    quantitative = dict(qualitative)
    quantitative["primary_findings"] = [
        dict(
            qualitative["primary_findings"][0],
            statement="晶格参数为 5.4 angstrom。",
        )
    ]
    assert not validate_interpretation(
        ScientificInterpretationOutput.model_validate(quantitative),
        bundle,
    ).valid

    unrelated = dict(qualitative)
    unrelated["primary_findings"] = [
        dict(
            qualitative["primary_findings"][0],
            statement="该结构具有高稳定性。",
        )
    ]
    assert not validate_interpretation(
        ScientificInterpretationOutput.model_validate(unrelated),
        bundle,
    ).valid


def test_unknown_result_item_reference_remains_fail_closed() -> None:
    output = _output()
    output["primary_findings"][0]["fact_refs"] = []
    output["primary_findings"][0]["evidence_refs"] = []
    output["primary_findings"][0]["result_item_refs"] = ["result_2"]
    grounded = ScientificInterpretationOutput.model_validate(output)

    validation = validate_interpretation(grounded, _bundle())

    assert not validation.valid
    assert any("unknown result-item reference" in error for error in validation.errors)


def test_unknown_top_level_supporting_result_reference_remains_fail_closed() -> None:
    output = _output()
    output["supporting_result_refs"] = ["result_2"]
    grounded = ScientificInterpretationOutput.model_validate(output)

    validation = validate_interpretation(grounded, _bundle())

    assert not validation.valid
    assert "unknown supporting result reference" in validation.errors


def test_volume_bounds_are_grounded_only_when_the_result_persists_them() -> None:
    payload = _bundle().model_dump(mode="json")
    payload["result_items"][0].update(
        {
            "id": "volume.item",
            "result_type": "volumetric.field",
            "fact_refs": ["volume.minimum", "volume.maximum"],
            "evidence_refs": ["evidence.volume"],
        }
    )
    payload["facts"] = [
        {
            **payload["facts"][0],
            "fact_id": "volume.minimum",
            "predicate": "volumetric.minimum",
            "value": -0.74387,
            "unit": "dimensionless",
        },
        {
            **payload["facts"][0],
            "fact_id": "volume.maximum",
            "predicate": "volumetric.maximum",
            "value": 0.7448,
            "unit": "dimensionless",
        },
    ]
    payload["evidence"][0].update(
        {
            "evidence_id": "evidence.volume",
            "supports_fact_refs": ["volume.minimum", "volume.maximum"],
            "supports_result_item_refs": ["volume.item"],
        }
    )
    bundle = ScientificResultBundle.model_validate(payload)

    grounded_payload = _output(
        statement=(
            "The stored field minimum is -0.74387 dimensionless and "
            "the maximum is 0.7448 dimensionless."
        ),
        fact="volume.minimum",
    )
    grounded_payload["primary_findings"][0].update(
        {
            "fact_refs": ["volume.minimum", "volume.maximum"],
            "evidence_refs": ["evidence.volume"],
            "result_item_refs": ["volume.item"],
        }
    )
    grounded_payload["primary_result_refs"] = ["volume.item"]
    grounded = ScientificInterpretationOutput.model_validate(grounded_payload)

    assert validate_interpretation(grounded, bundle).valid

    unsupported = grounded.model_copy(
        update={
            "answer_lead": "The volumetric field spans a range from 0 to 1.",
            "primary_findings": [
                grounded.primary_findings[0].model_copy(
                    update={
                        "statement": (
                            "The volumetric field spans a range from 0 to 1."
                        )
                    }
                )
            ],
        }
    )
    validation = validate_interpretation(unsupported, bundle)
    assert not validation.valid
    assert any("(0, 1)" in error for error in validation.errors)


def test_grounding_ignores_opaque_provenance_identifiers_in_answer_lead():
    bundle = _bundle()
    lead = (
        "结果 440636e5-d4e6-4410-b2e4-6909399cde82 的第一峰位于 2.5 angstrom，"
        "依据 fact.rdf.first_peak 和 evidence.evidence.rdf。"
    )
    result = ScientificInterpretationOutput.model_validate(_output(lead=lead))
    assert validate_interpretation(result, bundle).valid


def test_grounding_ignores_stable_dataset_sample_identifiers():
    bundle = _bundle()
    result = ScientificInterpretationOutput.model_validate(
        _output(statement="样本 mat-2 的第一峰位于 2.5 angstrom。")
    )
    assert validate_interpretation(result, bundle).valid


def test_grounding_accepts_numerals_inside_exact_cited_categorical_value():
    payload = _bundle().model_dump(mode="json")
    payload["facts"][0].update(
        {
            "fact_id": "structure.spacegroup_symbol",
            "predicate": "structure.spacegroup_symbol",
            "value": "Fd-3m",
            "unit": None,
        }
    )
    payload["result_items"][0]["fact_refs"] = ["structure.spacegroup_symbol"]
    bundle = ScientificResultBundle.model_validate(payload)
    result = ScientificInterpretationOutput.model_validate(
        _output(
            statement="The cited space-group symbol is Fd-3m.",
            fact="structure.spacegroup_symbol",
        )
    )

    assert validate_interpretation(result, bundle).valid


def test_only_unsupported_answer_lead_is_projected_from_grounded_finding():
    bundle = _bundle()
    raw = ScientificInterpretationOutput.model_validate(
        _output(lead="结果还包含 42 个未被权威事实支持的峰。")
    )
    assert not validate_interpretation(raw, bundle).valid

    projected = project_grounded_answer_lead(raw, bundle)

    assert projected.answer_lead == raw.primary_findings[0].statement
    assert validate_interpretation(projected, bundle).valid


def test_answer_lead_projection_defers_contract_11_assessment_errors():
    bundle = _bundle()
    payload = _output(lead="结果还包含 42 个未被权威事实支持的峰。")
    payload["contract_version"] = "1.1"
    raw = ScientificInterpretationOutput.model_validate(payload)

    projected = project_grounded_answer_lead(raw, bundle)

    assert projected.answer_lead == raw.primary_findings[0].statement
    assert "answer_lead introduces an unsupported quantitative claim" not in (
        validate_interpretation(projected, bundle).errors
    )
    assert any(
        error == "finding-1: claim support assessment is required"
        for error in validate_interpretation(projected, bundle).errors
    )


def test_answer_lead_projection_never_repairs_an_unsupported_finding():
    bundle = _bundle()
    raw = ScientificInterpretationOutput.model_validate(
        _output(
            statement="第一峰位于 23 angstrom。",
            lead="结果还包含 42 个未被权威事实支持的峰。",
        )
    )

    projected = project_grounded_answer_lead(raw, bundle)

    assert projected is raw
    assert not validate_interpretation(projected, bundle).valid


def test_grounded_communication_drops_unsourced_provider_method_lore() -> None:
    bundle = _bundle()
    raw = ScientificInterpretationOutput.model_validate({
        **_output(),
        "answer_lead": (
            "RDF 结果支持第一峰。该算法通常受某种未提供的物理机制影响。"
        ),
        "limitations": [
            "该算法可能对未在 Result 中记录的参数敏感。",
        ],
    })

    projected = project_grounded_communication(raw, bundle)

    assert projected.answer_lead == raw.primary_findings[0].statement
    assert projected.limitations == []
    assert validate_interpretation(projected, bundle).valid


def test_grounded_communication_hides_exact_reference_echo_from_visible_prose() -> None:
    bundle = _bundle()
    raw = ScientificInterpretationOutput.model_validate(
        _output(statement="第一峰位于 2.5 angstrom。（事实 ID: rdf.first_peak）")
    )

    projected = project_grounded_communication(raw, bundle)

    assert projected.primary_findings[0].statement == "第一峰位于 2.5 angstrom。"
    assert projected.primary_findings[0].fact_refs == ["rdf.first_peak"]
    assert "rdf.first_peak" not in projected.answer_lead
    assert validate_interpretation(projected, bundle).valid


@pytest.mark.parametrize("suffix,expected", [
    ("（figure_type: reference.compare_elements）", ""),
    ("（figure_type: other.figure）", "（figure_type: other.figure）"),
    ("（figure_type: reference.compare_elements，Og 缺失）", "（figure_type: reference.compare_elements，Og 缺失）"),
])
def test_grounded_communication_omits_only_an_exact_redundant_figure_type(suffix, expected):
    bundle = _bundle()
    bundle.figures = [ScientificFigure(
        figure_id="comparison.figure", figure_type="reference.compare_elements",
        role="PRIMARY", artifact_ids=["artifact-1"],
        fact_refs=["rdf.first_peak"], evidence_refs=["evidence.rdf"],
    )]
    raw = ScientificInterpretationOutput.model_validate(_output(statement=f"已生成比较图{suffix}。"))
    before = raw.model_dump(mode="json")
    projected = project_grounded_communication(raw, bundle)
    assert projected.primary_findings[0].statement == f"已生成比较图{expected}。"
    assert projected.primary_findings[0].fact_refs == raw.primary_findings[0].fact_refs
    assert raw.model_dump(mode="json") == before


def test_grounded_communication_removes_opaque_method_and_version_metadata() -> None:
    bundle = _bundle()
    raw = ScientificInterpretationOutput.model_validate(
            _output(
                statement=(
                    "RDF records 2.5 angstrom; source version "
                    "052a21f6-0e2d-4d43-85c6-6033e17a149d."
                )
            )
    )
    raw = raw.model_copy(
        update={
            "supporting_findings": [
                ScientificFinding.model_validate({
                    "finding_id": "finding.method",
                    "statement": (
                        "The result was produced by capability structure.rdf "
                        "(capability version 1.0, method "
                        "method.20fec3cce73b5336a4d98fad0f504f99)."
                    ),
                    "importance": "MEDIUM",
                    "confidence": "HIGH",
                    "evidence_refs": ["evidence.rdf"],
                    "result_item_refs": ["rdf.item"],
                    "claim_type": "METHOD_INTERPRETATION",
                    "support_status": "DIRECTLY_SUPPORTED",
                })
            ],
        }
    )

    projected = project_grounded_communication(
        project_claim_support_assessments(raw, bundle),
        bundle,
    )

    assert "052a21f6-0e2d-4d43-85c6-6033e17a149d" not in projected.primary_findings[0].statement
    assert "method.20fec3cce73b5336a4d98fad0f504f99" not in projected.supporting_findings[0].statement
    assert "capability version 1.0" not in projected.supporting_findings[0].statement
    assert validate_interpretation(projected, bundle).valid


def test_claim_support_uses_the_finding_referenced_result_item() -> None:
    payload = _bundle().model_dump(mode="json")
    payload["result_items"][0].update(
        {
            "id": "composition.item",
            "result_type": "data.composition_space",
            "title": "Composition space",
            "fact_refs": [],
            "evidence_refs": ["evidence.composition"],
        }
    )
    payload["evidence"][0].update(
        {
            "evidence_id": "evidence.composition",
            "supports_fact_refs": [],
            "supports_result_item_refs": ["composition.item"],
        }
    )
    payload["result_items"].append(
        {
            "id": "materials.item",
            "result_type": "data.materials_explorer",
            "role": "PRIMARY",
            "title": "Materials explorer",
            "artifact_ids": ["artifact-2"],
            "scientific_object_refs": payload["source_object_refs"],
            "fact_refs": ["materials.sample_count"],
            "evidence_refs": ["evidence.materials"],
        }
    )
    payload["facts"].append(
        {
            "fact_id": "materials.sample_count",
            "predicate": "dataset.sample_count",
            "subject_ref": "dataset",
            "value": 42,
            "unit": "count",
            "source": {
                "artifact_id": "artifact-2",
                "artifact_locator": "/overview/sampleCount",
            },
        }
    )
    payload["evidence"].append(
        {
            "evidence_id": "evidence.materials",
            "evidence_type": "structured_summary",
            "artifact_id": "artifact-2",
            "artifact_locator": "/overview",
            "supports_fact_refs": ["materials.sample_count"],
            "supports_result_item_refs": ["materials.item"],
        }
    )
    payload["provenance"]["artifact_ids"].append("artifact-2")
    payload["methods"] = [
        {
            "method_id": "method-composition",
            "capability_id": "data.composition_space",
            "capability_version": "1.0",
            "tool_id": "dataset.composition_space",
            "parameters": {},
            "source_object_refs": payload["source_object_refs"],
        }
    ]
    bundle = ScientificResultBundle.model_validate(payload)
    raw = ScientificInterpretationOutput.model_validate(
        {
            "contract_version": "1.1",
            "title": "Dataset interpretation",
            "answer_lead": "The materials explorer reports 42 samples.",
            "primary_findings": [
                {
                    "finding_id": "finding-materials",
                    "statement": "No invalid samples were reported among the 42 samples.",
                    "importance": "HIGH",
                    "confidence": "HIGH",
                    "fact_refs": ["materials.sample_count"],
                    "evidence_refs": ["evidence.materials"],
                    "result_item_refs": ["materials.item"],
                    "claim_type": "DIRECT_OBSERVATION",
                    "support_status": "DIRECTLY_SUPPORTED",
                }
            ],
            "supporting_findings": [],
            "limitations": [],
            "primary_result_refs": ["materials.item"],
            "supporting_result_refs": [],
            "follow_up_suggestions": [],
        }
    )

    projected = project_claim_support_assessments(raw, bundle)

    assessment = projected.primary_findings[0].reasoning_assessment
    assert assessment is not None
    assert assessment.accepted is True
    assert "EXPLORATORY_OUTLIER_DOES_NOT_ESTABLISH_INVALIDITY" not in assessment.reason_codes
    assert validate_interpretation(projected, bundle).valid


def test_composition_fact_support_does_not_inherit_result_level_exploratory_tag():
    payload = _bundle().model_dump(mode="json")
    composition_fact = {
        **payload["facts"][0],
        "fact_id": "composition.invalid_sample_count",
        "predicate": "composition.invalid_sample_count",
        "value": 0,
        "unit": "count",
    }
    payload["facts"] = [composition_fact]
    payload["result_items"][0].update(
        {
            "id": "composition.item",
            "result_type": "data.composition_space",
            "fact_refs": [composition_fact["fact_id"]],
            "evidence_refs": ["evidence.composition"],
        }
    )
    payload["evidence"][0].update(
        {
            "evidence_id": "evidence.composition",
            "supports_fact_refs": [composition_fact["fact_id"]],
            "supports_result_item_refs": ["composition.item"],
        }
    )
    payload["methods"] = [
        {
            "method_id": "method-composition",
            "capability_id": "data.composition_space",
            "capability_version": "1.0",
            "tool_id": "dataset.composition_space",
            "parameters": {},
            "source_object_refs": payload["source_object_refs"],
        }
    ]
    payload["limitations"] = [
        {
            "limitation_id": "limitation.composition",
            "code": "COMPOSITION_SPACE_DESCRIPTIVE",
            "message": (
                "Composition-space projection is descriptive and does not "
                "establish material identity or causality."
            ),
            "source_ref": "agent2.data.composition_space",
        }
    ]
    bundle = ScientificResultBundle.model_validate(payload)
    raw = ScientificInterpretationOutput.model_validate(
        {
            "contract_version": "1.1",
            "title": "Dataset interpretation",
            "answer_lead": "No invalid composition samples were reported.",
            "primary_findings": [
                {
                    "finding_id": "finding.invalid_composition_samples",
                    "statement": "No invalid composition samples were reported.",
                    "importance": "HIGH",
                    "confidence": "HIGH",
                    "fact_refs": [composition_fact["fact_id"]],
                    "evidence_refs": ["evidence.composition"],
                    "result_item_refs": ["composition.item"],
                    "claim_type": "DIRECT_OBSERVATION",
                    "support_status": "DIRECTLY_SUPPORTED",
                }
            ],
            "supporting_findings": [],
            "limitations": [],
            "primary_result_refs": ["composition.item"],
            "supporting_result_refs": [],
            "follow_up_suggestions": [],
        }
    )

    projected = project_claim_support_assessments(raw, bundle)
    assessment = projected.primary_findings[0].reasoning_assessment

    assert assessment is not None
    assert assessment.accepted is True
    assert "EXPLORATORY_OUTLIER_DOES_NOT_ESTABLISH_INVALIDITY" not in (
        assessment.reason_codes
    )
    assert "MATERIAL_EVIDENCE_LIMITATION_OMITTED" not in assessment.reason_codes
    assert validate_interpretation(projected, bundle).valid


def test_grounded_communication_removes_redundant_success_wording() -> None:
    bundle_payload = _bundle().model_dump(mode="json")
    bundle_payload["facts"][0].update({
        "predicate": "successful_coordination_site_count",
        "value": 1,
        "unit": None,
    })
    bundle = ScientificResultBundle.model_validate(bundle_payload)
    raw = ScientificInterpretationOutput.model_validate(
        _output(statement="CrystalNN 成功识别出 1 个成功配位位点。")
    )

    projected = project_grounded_communication(raw, bundle)

    assert projected.primary_findings[0].statement == (
        "CrystalNN 成功识别出 1 个配位位点。"
    )
    assert projected.answer_lead == "CrystalNN 成功识别出 1 个配位位点。"
    assert validate_interpretation(projected, bundle).valid


def test_reference_echo_cleanup_preserves_parenthetical_scientific_content() -> None:
    bundle = _bundle()
    raw = ScientificInterpretationOutput.model_validate(
        _output(
            statement=(
                "第一峰位于 2.5 angstrom"
                "（截断范围内；事实 ID: rdf.first_peak）。"
            )
        )
    )

    projected = project_grounded_communication(raw, bundle)

    assert "截断范围内" in projected.primary_findings[0].statement
    assert "rdf.first_peak" in projected.primary_findings[0].statement
    assert validate_interpretation(projected, bundle).valid


@pytest.mark.parametrize("unsupported", [False, True])
@pytest.mark.parametrize("markdown", [False, True])
def test_historical_scientific_message_uses_grounded_read_projection(unsupported, markdown) -> None:
    bundle = _bundle()
    turn_id = uuid4()
    interpretation_id = uuid4()
    snapshot_id = uuid4()
    message_id = "message-scientific-final"
    interpretation_row = {
        "id": interpretation_id,
        "project_id": "project",
        "research_turn_id": turn_id,
        "grounding_status": "VALID",
        "result_snapshot_id": snapshot_id,
        "output_json": {
            "interpretation": {
                **_output(
                    statement="第一峰位于 2.5 angstrom。（事实 ID: rdf.first_peak）",
                    lead="该方法非常准确，但 Result 未提供这种结论。",
                ),
                "limitations": ["未来源的方法常识。"],
            }
        },
    }
    snapshot_row = {
        "id": snapshot_id,
        "project_id": "project",
        "bundle_json": bundle.model_dump(mode="json"),
    }
    if unsupported:
        interpretation_row["output_json"]["interpretation"]["primary_findings"][0]["statement"] = "MAE 已计算。"
    before = json.dumps([interpretation_row, snapshot_row], default=str)

    class Rows:
        def __init__(self, values):
            self.values = values

        def mappings(self):
            return self

        def all(self):
            return self.values

    class Connection:
        def __init__(self):
            self.calls = 0

        def execute(self, _statement):
            self.calls += 1
            return Rows([interpretation_row] if self.calls == 1 else [snapshot_row])

    projected = _scientific_message_projections(
        [{
            "id": message_id,
            "role": "agent",
            "payload_json": {
                "source": "agent2_scientific_interpreter",
                "messageKind": "ASSISTANT_FINAL",
                "interpretationId": str(interpretation_id),
                "turnId": str(turn_id),
                "sourceResultSnapshotId": str(snapshot_id),
                **({"responseFormat": "markdown"} if markdown else {}),
            },
        }],
        Connection(),
        project_id="project",
    )

    assert json.dumps([interpretation_row, snapshot_row], default=str) == before
    if unsupported:
        assert "未通过当前事实校验" in projected[message_id]
        assert "MAE 已计算" not in projected[message_id]
        return
    assert "第一峰位于 2.5 angstrom。" in projected[message_id]
    assert "rdf.first_peak" not in projected[message_id]
    assert "非常准确" not in projected[message_id]
    assert "未来源的方法常识" not in projected[message_id]
    assert projected[message_id].startswith("## RDF 解释\n\n")


def test_grounding_does_not_treat_lowercase_k_labels_as_kelvin_units():
    base = _bundle()
    bundle = base.model_copy(update={"facts": [*base.facts, {"fact_id": "rdf.kpoint_count", "predicate": "electronic.kpoint_count", "subject_ref": "structure:v1", "value": 81, "unit": "count", "source": {"artifact_id": "artifact-1", "artifact_locator": "/summary/kpointCount"}}]})
    result = ScientificInterpretationOutput.model_validate(
        _output(statement="该结果包含 81 k 点。", fact="rdf.kpoint_count")
    )
    # The statement intentionally has no measured unit; ``k`` is a path label.
    assert validate_interpretation(result, bundle).valid


@pytest.mark.parametrize("path", ["Γ–M–K–Γ", "Γ-M-K-Γ", "Γ → M → K → Γ"])
def test_reciprocal_path_k_is_not_a_kelvin_claim(path):
    payload = _bundle().model_dump(mode="json")
    payload["facts"][0].update(predicate="phonon.qpoint_count", value=51, unit="count")
    bundle = ScientificResultBundle.model_validate(payload)
    result = ScientificInterpretationOutput.model_validate(_output(f"沿 {path} 路径共包含 51 个 q 点。"))
    assert validate_interpretation(result, bundle).valid

    for statement in [f"沿 {path} 路径共包含 51 个 q 点，温度为 51 K。", "温度范围为 0–51 K。"]:
        unsupported = ScientificInterpretationOutput.model_validate(_output(statement))
        assert any("unit is absent" in error for error in validate_interpretation(unsupported, bundle).errors)


def test_reciprocal_path_exception_does_not_apply_to_unrelated_facts():
    result = ScientificInterpretationOutput.model_validate(_output("在 M–K 范围，第一峰为 2.5 angstrom。"))
    assert any("unit is absent" in error for error in validate_interpretation(result, _bundle()).errors)


@pytest.mark.parametrize("label", ["K点", "K 点", "K-point", "K‑point", "K points"])
def test_partial_density_k_point_limitation_is_not_a_temperature_claim(label):
    bundle = _bundle()
    bundle.facts[0].predicate = "volumetric.field_kind"
    bundle.facts[0].value = "partial_charge_density"
    bundle.facts[0].unit = None
    statement = f"该部分电荷密度不能确定具体能带、{label} 或轨道身份。"
    result = ScientificInterpretationOutput.model_validate(_output(statement))
    assert validate_interpretation(result, bundle).valid

    result.primary_findings[0].statement = statement + "温度单位为 K。"
    assert any("unit is absent" in error for error in validate_interpretation(result, bundle).errors)


@pytest.mark.parametrize("statement", ["K 点的温度为 2.5 K。", "温度范围为 2.5–2.5 K。", "温度在 2.5 K 点附近。", "温度在 2.5\nK 点附近。"])
def test_k_point_disambiguation_retains_numeric_kelvin_claims(statement):
    bundle = _bundle()
    bundle.facts[0].predicate = "volumetric.minimum"
    result = ScientificInterpretationOutput.model_validate(_output(statement))
    assert any("unit is absent" in error for error in validate_interpretation(result, bundle).errors)

    bundle.facts[0].unit = "K"
    assert validate_interpretation(result, bundle).valid


def test_reciprocal_path_disambiguation_cannot_borrow_unreferenced_scientific_context():
    bundle = _bundle()
    other = bundle.facts[0].model_copy(update={"fact_id": "unrelated", "predicate": "electronic.energy"})
    bundle.facts.append(other)
    result = ScientificInterpretationOutput.model_validate(_output("沿 M–K 路径。"))
    assert any("unit is absent" in error for error in validate_interpretation(result, bundle).errors)


@pytest.mark.parametrize("label", ["2θ", "2 θ", "2theta", "2Theta"])
def test_xrd_angle_notation_is_not_a_separate_numeric_claim(label):
    payload = _bundle().model_dump(mode="json")
    payload["facts"][0].update(predicate="xrd.peak.two_theta", value=20.498535, unit="degree")
    bundle = ScientificResultBundle.model_validate(payload)
    output = ScientificInterpretationOutput.model_validate(_output(f"峰位 {label} = 20.498535°。"))
    assert validate_interpretation(output, bundle).valid
    for statement in [f"峰位 {label} = 20.498535°，另有 2 个峰。", f"峰位 {label} = 25°。", "峰位 12θ = 20.498535°。"]:
        output.primary_findings[0].statement = statement
        assert any("quantitative claim" in e for e in validate_interpretation(output, bundle).errors)
    payload["facts"][0]["predicate"] = "other.angle"
    output.primary_findings[0].statement = f"峰位 {label} = 20.498535°。"
    assert any("quantitative claim" in e for e in validate_interpretation(output, ScientificResultBundle.model_validate(payload)).errors)


@pytest.mark.parametrize("predicate,value,statement", [
    ("volumetric.length_unit", "angstrom", "坐标长度单位为 Å。"),
    ("volumetric.selected_canonical_unit", "electronvolt", "所选字段单位为 eV。"),
    ("phonon.frequency_unit", "terahertz", "频率单位为 THz。"),
    ("volumetric.canonical_unit", "electron/angstrom^3", "电子密度单位为 电子/Å³。"),
])
def test_explicit_unit_definition_fact_supports_its_unit_symbol(predicate, value, statement):
    payload = _bundle().model_dump(mode="json")
    payload["facts"][0].update(predicate=predicate, value=value, unit=None)
    bundle = ScientificResultBundle.model_validate(payload)
    output = ScientificInterpretationOutput.model_validate(_output(statement, lead=statement))
    assert validate_interpretation(output, bundle).valid
    output.primary_findings[0].statement = "单位为 nm。"
    assert any("unit is absent" in error for error in validate_interpretation(output, bundle).errors)
    payload["facts"][0]["predicate"] = "volumetric.field_name"
    arbitrary_label = ScientificResultBundle.model_validate(payload)
    output.primary_findings[0].statement = statement
    assert any("unit is absent" in error for error in validate_interpretation(output, arbitrary_label).errors)


def test_partial_result_cannot_be_presented_as_complete():
    result = ScientificInterpretationOutput.model_validate(_output(statement="完整分析已完成，第一峰位于 2.5 angstrom。"))
    assert not validate_interpretation(result, _bundle(execution_status="PARTIAL")).valid


def test_dataset_grounding_remains_fail_closed_for_unsupported_claim() -> None:
    ref = ScientificObjectRef(object_id=uuid4(), version_id=uuid4(), project_id="project", object_type="materials.table")
    bundle = ScientificResultBundle(
        schema_version="1.0",
        result_id=uuid4(),
        project_id="project",
        research_session_id="session",
        research_turn_id=uuid4(),
        research_question="Summarize sample mat-2",
        source_object_refs=[ref],
        execution_status="SUCCESS",
        relevance_status="CURRENT",
        result_items=[{
            "id": "dataset.item",
            "result_type": "data.materials_explorer",
            "role": "PRIMARY",
            "title": "Dataset",
            "artifact_ids": ["artifact-1"],
            "scientific_object_refs": [ref],
            "fact_refs": ["dataset.sample.band_gap"],
            "evidence_refs": ["evidence.dataset"],
        }],
        facts=[{
            "fact_id": "dataset.sample.band_gap",
            "predicate": "dataset.sample.band_gap",
            "subject_ref": "dataset-object:mat-2",
            "value": 5.6,
            "unit": None,
            "source": {"artifact_id": "artifact-1", "artifact_locator": "/sampleIndex/0/properties/band_gap"},
        }],
        figures=[],
        tables=[],
        output_object_refs=[],
        evidence=[{
            "evidence_id": "evidence.dataset",
            "evidence_type": "COMMITTED_MACHINE_READABLE_ARTIFACT",
            "artifact_id": "artifact-1",
            "artifact_locator": "/",
        }],
        methods=[],
        limitations=[],
        warnings=[],
        provenance={"artifact_ids": ["artifact-1"]},
        projection_version="agent2.result/1.0",
    )
    unsupported = ScientificInterpretationOutput.model_validate(
        _output("样本 mat-2 的 band gap 为 7.9。", fact="dataset.sample.band_gap")
    )
    validation = validate_interpretation(unsupported, bundle)
    assert not validation.valid
    assert any("quantitative claim" in error for error in validation.errors)


def test_rdf_parameter_facts_do_not_authorize_an_unprojected_peak_claim() -> None:
    base = _bundle()
    parameter_facts = [
        {
            "fact_id": "rdf.r_max",
            "predicate": "rdf.r_max",
            "subject_ref": "artifact-1",
            "value": 8.0,
            "unit": "angstrom",
            "source": {
                "artifact_id": "artifact-1",
                "artifact_locator": "/parameters/r_max_angstrom",
            },
        },
        {
            "fact_id": "rdf.bin_width",
            "predicate": "rdf.bin_width",
            "subject_ref": "artifact-1",
            "value": 0.1,
            "unit": "angstrom",
            "source": {
                "artifact_id": "artifact-1",
                "artifact_locator": "/parameters/bin_width_angstrom",
            },
        },
    ]
    bundle_payload = base.model_dump(mode="json")
    bundle_payload["facts"] = [*bundle_payload["facts"], *parameter_facts]
    bundle = ScientificResultBundle.model_validate(bundle_payload)
    unsupported = ScientificInterpretationOutput.model_validate(
        _output(
            statement=(
                "RDF 计算范围为 8.0 angstrom、分箱宽度为 0.1 angstrom，"
                "第一峰位于 3.7 angstrom。"
            ),
            fact="rdf.r_max",
        )
    )

    validation = validate_interpretation(unsupported, bundle)

    assert not validation.valid
    assert any("quantitative claim" in error for error in validation.errors)


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
    assert len(envelope.result["facts"]) == 16
    assert len(envelope.evidence) == 64
    assert envelope.omitted_supporting_items == [
        *(["fact:rdf.first_peak"] * 50),
        "evidence:evidence.rdf",
        "evidence:evidence.rdf",
    ]


def test_interpreter_input_compacts_support_edges_to_fit_actual_budget():
    payload = _bundle().model_dump(mode="json")
    template = payload["facts"][0]
    facts = []
    for index in range(220):
        facts.append({
            **template,
            "fact_id": f"fact.{index:032x}",
            "value": f"bounded scientific fact {index:04d} " + ("x" * 96),
        })
    fact_ids = [item["fact_id"] for item in facts]
    payload["facts"] = facts
    payload["result_items"][0]["fact_refs"] = fact_ids
    payload["evidence"][0]["supports_fact_refs"] = fact_ids
    expanded = ScientificResultBundle.model_validate(payload)

    envelope, _fingerprint = InterpreterInputAssembler().assemble(
        bundle=expanded,
        question="Explain the bounded result.",
        relevance_status="CURRENT",
    )

    encoded = json.dumps(
        envelope.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    assert len(encoded) // 4 <= context_budget_policy(
        ContextOperation.INTERPRETER
    ).effective_input_budget
    represented_fact_ids = {
        item["fact_id"] for item in envelope.result["facts"]
    }
    assert set(envelope.result["result_items"][0]["fact_refs"]).issubset(
        represented_fact_ids
    )
    assert len(envelope.result["result_items"][0]["fact_refs"]) <= 32
    assert set(envelope.evidence[0]["supports_fact_refs"]).issubset(
        represented_fact_ids
    )
    assert len(envelope.evidence[0]["supports_fact_refs"]) <= 32
    assert {
        value
        for key, value in envelope.result["reference_aliases"].items()
        if key.startswith("fact_")
    } == represented_fact_ids
    assert len(envelope.omitted_supporting_items) == 220 - len(
        represented_fact_ids
    )


def test_interpreter_input_prefers_summary_predicates_over_repetitive_rows():
    payload = _bundle().model_dump(mode="json")
    template = payload["facts"][0]
    summary = [
        {
            **template,
            "fact_id": f"summary.{index}",
            "predicate": f"dataset.summary_{index}",
            "value": index + 1,
            "unit": "count",
        }
        for index in range(8)
    ]
    details = []
    for index in range(100):
        details.extend(
            [
                {
                    **template,
                    "fact_id": f"sample.{index}",
                    "predicate": "dataset.sample_id",
                    "value": f"sample-{index}",
                    "unit": None,
                },
                {
                    **template,
                    "fact_id": f"formula.{index}",
                    "predicate": "dataset.formula",
                    "value": f"A{index}B",
                    "unit": None,
                },
            ]
        )
    payload["facts"] = [*summary, *details]
    payload["result_items"][0]["fact_refs"] = [
        item["fact_id"] for item in payload["facts"]
    ]
    payload["evidence"][0]["supports_fact_refs"] = [
        item["fact_id"] for item in payload["facts"]
    ]

    envelope, _fingerprint = InterpreterInputAssembler().assemble(
        bundle=ScientificResultBundle.model_validate(payload),
        question="Summarize this dataset.",
        relevance_status="CURRENT",
    )

    represented = envelope.result["facts"]
    assert [item["fact_id"] for item in represented] == [
        item["fact_id"] for item in summary
    ]
    assert len(envelope.omitted_supporting_items) == len(details)
    represented_ids = {item["fact_id"] for item in represented}
    assert set(envelope.result["result_items"][0]["fact_refs"]) == represented_ids
    assert set(envelope.evidence[0]["supports_fact_refs"]) == represented_ids


def test_interpreter_input_omits_identifier_only_subject_groups():
    payload = _bundle().model_dump(mode="json")
    template = payload["facts"][0]
    summary = [
        {
            **template,
            "fact_id": f"summary.{index}",
            "predicate": f"dataset.summary_{index}",
            "value": index + 1,
            "unit": "count",
        }
        for index in range(8)
    ]
    details = []
    for index in range(100):
        details.extend(
            [
                {
                    **template,
                    "fact_id": f"sample.{index}",
                    "predicate": "dataset.sample_id",
                    "subject_ref": f"row:{index}",
                    "value": index,
                    "unit": None,
                },
                {
                    **template,
                    "fact_id": f"formula.{index}",
                    "predicate": "dataset.formula",
                    "subject_ref": f"row:{index}",
                    "value": f"A{index}B",
                    "unit": None,
                },
            ]
        )
    payload["facts"] = [*summary, *details]
    payload["result_items"][0]["fact_refs"] = [
        item["fact_id"] for item in payload["facts"]
    ]
    payload["evidence"][0]["supports_fact_refs"] = [
        item["fact_id"] for item in payload["facts"]
    ]

    envelope, _ = InterpreterInputAssembler().assemble(
        bundle=ScientificResultBundle.model_validate(payload),
        question="Summarize this dataset.",
        relevance_status="CURRENT",
    )

    represented = envelope.result["facts"]
    assert [item["fact_id"] for item in represented] == [
        item["fact_id"] for item in summary
    ]
    assert len(envelope.omitted_supporting_items) == len(details)


def test_interpreter_input_preserves_complete_repetitive_fact_groups() -> None:
    payload = _bundle().model_dump(mode="json")
    template = payload["facts"][0]
    summary = [
        {
            **template,
            "fact_id": f"summary.{index}",
            "predicate": f"ml.summary_{index}",
            "subject_ref": "job:summary",
            "value": index,
        }
        for index in range(6)
    ]
    details = []
    for sample in range(10):
        subject = f"sample:{sample}"
        for field in (
            "sample_id",
            "formula",
            "target",
            "prediction",
            "residual",
            "absolute_error",
        ):
            details.append(
                {
                    **template,
                    "fact_id": f"fact.{sample}.{field}",
                    "predicate": f"ml.high_error_{field}",
                    "subject_ref": subject,
                    "value": sample + 1,
                }
            )
    payload["facts"] = [*summary, *details]
    payload["result_items"][0]["fact_refs"] = [
        item["fact_id"] for item in payload["facts"]
    ]
    payload["evidence"][0]["supports_fact_refs"] = [
        item["fact_id"] for item in payload["facts"]
    ]

    envelope, _ = InterpreterInputAssembler().assemble(
        bundle=ScientificResultBundle.model_validate(payload),
        question="Explain the largest errors.",
        relevance_status="CURRENT",
    )
    result_refs = envelope.result["result_items"][0]["fact_refs"]
    evidence_refs = envelope.evidence[0]["supports_fact_refs"]

    assert result_refs == evidence_refs
    assert len(result_refs) <= 32
    assert result_refs
    for sample in range(10):
        complete_group = {
            f"fact.{sample}.{field}"
            for field in (
                "sample_id",
                "formula",
                "target",
                "prediction",
                "residual",
                "absolute_error",
            )
        }
        selected = complete_group.intersection(result_refs)
        assert selected in (set(), complete_group)


def test_interpreter_input_removes_presentation_ordinals_and_runtime_locators() -> None:
    payload = _bundle().model_dump(mode="json")
    payload["result_items"][0].update(
        {
            "id": "volumetric.result",
            "result_type": "volumetric.field",
            "title": "resource 1 / volumetric_field_01",
            "artifact_ids": ["call_step_1-volumetric_field_json"],
            "viewer_binding": "step_1",
        }
    )
    payload["facts"][0].update(
        {
            "fact_id": "volumetric.field_name",
            "predicate": "volumetric.field_name",
            "subject_ref": "resource 1 / volumetric_field_01",
            "value": "scalar",
            "unit": None,
            "source": {
                "artifact_id": "call_step_1-volumetric_field_json",
                "artifact_locator": "/resources/1/volumetric_field_01",
            },
        }
    )
    payload["result_items"][0]["fact_refs"] = ["volumetric.field_name"]
    payload["evidence"][0].update(
        {
            "evidence_id": "volumetric.evidence",
            "evidence_type": "structured_summary",
            "artifact_id": "call_step_1-volumetric_field_json",
            "tool_call_id": "call_step_1",
            "artifact_locator": "/resources/1/volumetric_field_01",
            "supports_fact_refs": ["volumetric.field_name"],
            "supports_result_item_refs": ["volumetric.result"],
        }
    )
    payload["result_items"][0]["evidence_refs"] = ["volumetric.evidence"]
    payload["methods"] = [
        {
            "method_id": "method_step_1",
            "capability_id": "volumetric.inspect",
            "capability_version": "1.0",
            "tool_id": "structure.volumetric_data",
            "tool_version": "0.1.0",
            "parameters": {"quantity": "generic_scalar"},
            "source_object_refs": payload["source_object_refs"],
        }
    ]
    payload["provenance"].update(
        {
            "job_id": "job_resource_1",
            "tool_call_ids": ["call_step_1"],
            "artifact_ids": ["call_step_1-volumetric_field_json"],
        }
    )
    bundle = ScientificResultBundle.model_validate(payload)

    envelope, _ = InterpreterInputAssembler().assemble(
        bundle=bundle,
        question="Inspect this supplied volumetric grid.",
        relevance_status="CURRENT",
    )

    encoded = json.dumps(envelope.model_dump(mode="json"), ensure_ascii=False)
    assert "resource 1" not in encoded
    assert "step_1" not in encoded
    assert "volumetric_field_01" not in encoded
    assert set(envelope.result) == {
        "schema_version",
        "research_question",
        "execution_status",
        "relevance_status",
        "result_items",
        "facts",
        "figures",
        "tables",
        "methods",
        "limitations",
        "warnings",
        "reference_aliases",
        "follow_up_policy",
    }
    assert set(envelope.result["result_items"][0]) == {
        "id",
        "result_type",
        "role",
        "fact_refs",
        "evidence_refs",
    }
    assert set(envelope.evidence[0]) == {
        "evidence_id",
        "evidence_type",
        "supports_fact_refs",
        "supports_result_item_refs",
    }
    assert "source" not in envelope.result["facts"][0]
    assert envelope.result["facts"][0]["subject_ref"] == "subject_a"
    assert set(envelope.result["methods"][0]) == {
        "capability_id",
        "capability_version",
        "parameters",
    }
    persisted = bundle.model_dump(mode="json")
    assert persisted["result_items"][0]["title"] == (
        "resource 1 / volumetric_field_01"
    )
    assert persisted["evidence"][0]["tool_call_id"] == "call_step_1"


def test_provider_aliases_follow_the_bounded_envelope_after_fact_selection():
    payload = _bundle().model_dump(mode="json")
    template = payload["facts"][0]
    details = [
        {
            **template,
            "fact_id": f"detail.{index}",
            "predicate": "dataset.row_detail",
            "value": index,
        }
        for index in range(69)
    ]
    summary = {
        **template,
        "fact_id": "summary.sample_count",
        "predicate": "dataset.sample_count",
        "value": 42,
        "unit": "count",
    }
    payload["facts"] = [*details, summary]
    payload["result_items"][0]["fact_refs"] = [
        item["fact_id"] for item in payload["facts"]
    ]
    payload["evidence"][0]["supports_fact_refs"] = [
        item["fact_id"] for item in payload["facts"]
    ]
    bundle = ScientificResultBundle.model_validate(payload)
    envelope, _fingerprint = InterpreterInputAssembler().assemble(
        bundle=bundle,
        question="Summarize this dataset.",
        relevance_status="CURRENT",
    )

    assert envelope.result["reference_aliases"]["fact_a"] == "summary.sample_count"
    assert all(
        not any(character.isdigit() for character in alias)
        for alias in envelope.result["reference_aliases"]
    )
    assert set(envelope.result["reference_aliases"].values()).issubset(
        {item["fact_id"] for item in envelope.result["facts"]}
        | {item["id"] for item in envelope.result["result_items"]}
        | {item["evidence_id"] for item in envelope.evidence}
    )
    provider_output = _output(
        statement="The dataset sample count is 42 count.",
        fact="fact_a",
    )
    provider_output["primary_findings"][0]["evidence_refs"] = []
    provider_output["primary_findings"][0]["result_item_refs"] = []
    client = FakeStructuredInterpreterClient([provider_output])
    service = ScientificInterpretationService(
        repository_factory=None,  # type: ignore[arg-type]
        client=client,
    )

    result, repaired, _meta = service._generate_with_one_repair(
        envelope,
        bundle,
    )

    assert result.primary_findings[0].fact_refs == ["summary.sample_count"]
    assert result.primary_result_refs == ["rdf.item"]
    assert repaired is False
    assert client.calls == 1


def test_grounding_repair_context_contains_source_facts_and_viewer_boundary() -> None:
    payload = _bundle().model_dump(mode="json")
    payload["facts"] = []
    payload["result_items"][0].update(
        {
            "id": "structure.viewer",
            "result_type": "structure.viewer_scene",
            "fact_refs": [],
            "evidence_refs": [],
        }
    )
    payload["evidence"] = []
    bundle = ScientificResultBundle.model_validate(payload)
    raw = _output(statement="晶格参数为 5.4 angstrom。")
    raw["primary_findings"][0].update(
        {
            "fact_refs": [],
            "evidence_refs": [],
            "result_item_refs": ["structure.viewer"],
        }
    )
    raw["primary_result_refs"] = ["structure.viewer"]
    interpretation = ScientificInterpretationOutput.model_validate(raw)

    errors = validate_interpretation(interpretation, bundle).errors
    context = build_grounding_repair_context(interpretation, bundle, errors)

    assert any("structure.viewer" in item for item in context)
    assert any("fact-less structure viewer" in item for item in context)
    assert any("5.4" in item for item in context)


def test_grounding_repair_context_preserves_supported_ml_group_values() -> None:
    payload = _bundle().model_dump(mode="json")
    payload["facts"] = [
        {
            **payload["facts"][0],
            "fact_id": "ml.high_error_target",
            "predicate": "ml.high_error_target",
            "subject_ref": "sample:1",
            "value": 6.38,
            "unit": "eV",
        },
        {
            **payload["facts"][0],
            "fact_id": "ml.high_error_prediction",
            "predicate": "ml.high_error_prediction",
            "subject_ref": "sample:1",
            "value": 1.1464,
            "unit": "eV",
        },
    ]
    payload["result_items"][0]["fact_refs"] = [
        "ml.high_error_target",
        "ml.high_error_prediction",
    ]
    bundle = ScientificResultBundle.model_validate(payload)
    raw = _output(
        statement="目标值为 6.38 eV，预测值为 2.0 eV。",
        fact="ml.high_error_target",
    )
    raw["primary_findings"][0]["fact_refs"] = [
        "ml.high_error_target",
        "ml.high_error_prediction",
    ]
    interpretation = ScientificInterpretationOutput.model_validate(raw)

    context = build_grounding_repair_context(
        interpretation,
        bundle,
        validate_interpretation(interpretation, bundle).errors,
    )

    assert any("6.38 eV" in item and "1.1464 eV" in item for item in context)
    assert any("unsupported_numeric_tokens=['2.0']" in item for item in context)


class _RepairContextCapturingClient(FakeStructuredInterpreterClient):
    def __init__(self, responses):
        super().__init__(responses)
        self.request_contexts = []

    async def generate_structured(self, **kwargs):
        self.request_contexts.append(kwargs.get("request_context") or {})
        return await super().generate_structured(**kwargs)


def test_unit_only_repair_identifies_the_unsupported_unit_and_its_exact_source():
    bundle = _bundle()
    result = ScientificInterpretationOutput.model_validate(_output("第一峰位于 2.5 nm。"))
    errors = validate_interpretation(result, bundle).errors
    feedback = build_grounding_repair_context(result, bundle, errors)

    assert any("unit is absent from referenced facts (nm)" in error for error in errors)
    assert any("unsupported_units=['nm']" in item for item in feedback)
    assert any("supported_units=['å']" in item for item in feedback)
    assert any("rdf.first_peak=2.5 angstrom" in item for item in feedback)
    assert any("do not convert units" in item for item in feedback)
    assert not validate_interpretation(result, bundle).valid


@pytest.mark.parametrize("unit, valid", [("Å³", True), ("angstrom^3", True), ("Å", False), ("Å^-3", False), ("eV·Å³", False)])
def test_elf_volume_integral_grounding_preserves_the_volume_dimension(unit, valid):
    payload = _bundle().model_dump(mode="json")
    payload["facts"][0].update(predicate="volumetric.volume_integral", value=3.1, unit="angstrom^3")
    bundle = ScientificResultBundle.model_validate(payload)
    result = ScientificInterpretationOutput.model_validate(_output(f"ELF 数学体积分为 3.1 {unit}。"))
    assert validate_interpretation(result, bundle).valid is valid


@pytest.mark.parametrize("unit", ["eV·Å³", "eV Å^3", "electronvolt*angstrom^3", "eV⋅Å^{3}", "eVÅ³"])
def test_potential_volume_integral_accepts_equivalent_unit_spelling(unit):
    payload = _bundle().model_dump(mode="json")
    payload["facts"][0].update(predicate="volumetric.volume_integral", value=89.24575101589733, unit="electronvolt*angstrom^3")
    bundle = ScientificResultBundle.model_validate(payload)
    result = ScientificInterpretationOutput.model_validate(_output(f"源体积分为 89.24575101589733 {unit}。"))
    validation = validate_interpretation(result, bundle)
    assert validation.valid, validation.errors


@pytest.mark.parametrize("unit", ["eV/Å³", "eV·nm³", "eV·Å²", "Å³", "eV", "Ha·Å³"])
def test_potential_volume_integral_rejects_changed_dimension_or_scale(unit):
    payload = _bundle().model_dump(mode="json")
    payload["facts"][0].update(predicate="volumetric.volume_integral", value=89.24575101589733, unit="electronvolt*angstrom^3")
    bundle = ScientificResultBundle.model_validate(payload)
    result = ScientificInterpretationOutput.model_validate(_output(f"源体积分为 89.24575101589733 {unit}。"))
    validation = validate_interpretation(result, bundle)
    assert not validation.valid
    assert any("unit is absent" in error for error in validation.errors)


@pytest.mark.parametrize("label", ["峰 2：", "峰2：", "Peak 2:"])
def test_xrd_repair_explains_unsupported_display_ordinal_without_accepting_it(label):
    payload = _bundle().model_dump(mode="json")
    payload["facts"][0].update(predicate="xrd.peak.two_theta", value=21.874628, unit="degree")
    bundle = ScientificResultBundle.model_validate(payload)
    result = ScientificInterpretationOutput.model_validate(_output(f"{label}2θ = 21.874628°。"))
    errors = validate_interpretation(result, bundle).errors
    feedback = build_grounding_repair_context(result, bundle, errors)

    assert any("quantitative claim" in error and "(2)" in error for error in errors)
    assert any("added display label" in item and "two-theta angle" in item for item in feedback)
    assert any("Do not rewrite the ordinal" in item and "Preserve the supported" in item for item in feedback)
    assert result.primary_findings[0].statement == f"{label}2θ = 21.874628°。"
    result.primary_findings[0].statement = "2θ = 21.874628°。"
    assert validate_interpretation(result, bundle).valid

    result.primary_findings[0].statement = "该峰位于 2°。"
    feedback = build_grounding_repair_context(result, bundle, validate_interpretation(result, bundle).errors)
    assert not any("added display label" in item for item in feedback)
    assert not validate_interpretation(result, bundle).valid


def test_unit_repair_uses_explicit_unit_definitions_without_inventing_conversions():
    payload = _bundle().model_dump(mode="json")
    payload["facts"][0].update(predicate="volumetric.length_unit", value="angstrom", unit=None)
    bundle = ScientificResultBundle.model_validate(payload)
    result = ScientificInterpretationOutput.model_validate(_output("坐标单位为 nm。"))
    feedback = build_grounding_repair_context(result, bundle, validate_interpretation(result, bundle).errors)
    assert any("supported_units=['å']" in item and "unsupported_units=['nm']" in item for item in feedback)
    result.primary_findings[0].statement = "坐标单位为 Å。"
    assert validate_interpretation(result, bundle).valid
    assert build_grounding_repair_context(result, bundle, []) == []


def test_interpretation_repair_sends_source_derived_grounding_context() -> None:
    first = _output(statement="目标值为 6.38 eV，预测值为 2.0 eV。", fact="rdf.first_peak")
    second = _output(statement="第一峰位于 2.5 angstrom。")
    client = _RepairContextCapturingClient([first, second])
    service = ScientificInterpretationService(
        repository_factory=None,  # type: ignore[arg-type]
        client=client,
    )
    envelope, _ = InterpreterInputAssembler().assemble(
        bundle=_bundle(),
        question="Explain the RDF",
        relevance_status="CURRENT",
    )

    result, repaired, _meta = service._generate_with_one_repair(
        envelope,
        _bundle(),
    )

    assert result.primary_findings[0].statement == "第一峰位于 2.5 angstrom。"
    assert repaired is True
    assert len(client.request_contexts) == 2
    repair = client.request_contexts[1]["repair"]
    assert any("finding-1" in item for item in repair["validation_errors"])
    assert any("supported_facts" in item for item in repair["validation_errors"])


def test_schema_invalid_response_gets_one_bounded_repair():
    client = FakeStructuredInterpreterClient([{"bad": True}, _output()])
    service = ScientificInterpretationService(repository_factory=None, client=client)  # type: ignore[arg-type]
    result, repaired, _meta = service._generate_with_one_repair(InterpreterInputAssembler().assemble(bundle=_bundle(), question="Explain the RDF", relevance_status="CURRENT")[0], _bundle())
    assert result.title == "RDF 解释"
    assert repaired is True
    assert client.calls == 2


@pytest.mark.parametrize("reference_field", ["fact_refs", "evidence_refs", "result_item_refs"])
def test_schema_repair_splits_oversized_citations_without_echoing_input(reference_field):
    first = _output()
    first["primary_findings"][0][reference_field] = [
        f"untrusted-provider-reference-{index}" for index in range(35)
    ]
    client = _RepairContextCapturingClient([first, _output()])
    service = ScientificInterpretationService(repository_factory=None, client=client)  # type: ignore[arg-type]
    bundle = _bundle()

    result, repaired, _meta = service._generate_with_one_repair(
        InterpreterInputAssembler().assemble(
            bundle=bundle, question="Explain the RDF", relevance_status="CURRENT",
        )[0],
        bundle,
    )

    assert repaired is True
    assert result.primary_findings[0].fact_refs == ["rdf.first_peak"]
    assert client.calls == 2
    feedback = client.request_contexts[1]["repair"]["validation_errors"]
    assert len(feedback) == 1
    assert f"primary_findings.0.{reference_field}" in feedback[0]
    assert "Maximum length: 32; actual length: 35" in feedback[0]
    assert "one finding per peak" in feedback[0]
    assert "complete relevant references together" in feedback[0]
    assert "Do not truncate" in feedback[0]
    assert "untrusted-provider-reference" not in feedback[0]
    assert len(feedback[0]) < 1000
    assert len(first["primary_findings"][0][reference_field]) == 35


@pytest.mark.parametrize("collection, count", [("primary_findings", 9), ("supporting_findings", 17)])
def test_schema_repair_guides_finding_grouping_with_both_array_limits(collection, count):
    first = _output()
    first[collection] = [
        {**first["primary_findings"][0], "finding_id": f"oversized-{index}"}
        for index in range(count)
    ]
    client = _RepairContextCapturingClient([first, _output()])
    service = ScientificInterpretationService(repository_factory=None, client=client)  # type: ignore[arg-type]
    bundle = _bundle()

    _result, repaired, _meta = service._generate_with_one_repair(
        InterpreterInputAssembler().assemble(
            bundle=bundle, question="Explain the RDF", relevance_status="CURRENT",
        )[0],
        bundle,
    )

    assert repaired is True
    feedback = client.request_contexts[1]["repair"]["validation_errors"]
    assert len(feedback) == 1
    assert f"{collection}: too_long" in feedback[0]
    assert f"actual length: {count}" in feedback[0]
    assert "citation" in feedback[0]
    assert "requested" in feedback[0]
    assert "oversized-0" not in feedback[0]
    if collection == "primary_findings":
        assert "move complete secondary" in feedback[0]
        assert "supporting_findings" in feedback[0]


def test_schema_repair_feedback_bounds_errors_and_excludes_invalid_payloads():
    first = _output()
    first["title"] = "raw-provider-payload" * 500
    first.update({f"unknown_{index}": "raw-provider-payload" for index in range(40)})
    client = _RepairContextCapturingClient([first, _output()])
    service = ScientificInterpretationService(repository_factory=None, client=client)  # type: ignore[arg-type]
    bundle = _bundle()

    service._generate_with_one_repair(
        InterpreterInputAssembler().assemble(
            bundle=bundle, question="Explain the RDF", relevance_status="CURRENT",
        )[0],
        bundle,
    )

    feedback = client.request_contexts[1]["repair"]["validation_errors"]
    assert len(feedback) == 16
    assert all(len(item) < 1000 for item in feedback)
    assert "raw-provider-payload" not in str(feedback)
    assert "Remove this unsupported field" in feedback[-1]


def test_schema_invalid_after_repair_is_not_accepted():
    client = FakeStructuredInterpreterClient([{"bad": True}, {"still": "bad"}])
    service = ScientificInterpretationService(repository_factory=None, client=client)  # type: ignore[arg-type]
    with pytest.raises(Exception) as exc:
        service._generate_with_one_repair(InterpreterInputAssembler().assemble(bundle=_bundle(), question="Explain the RDF", relevance_status="CURRENT")[0], _bundle())
    assert getattr(exc.value, "code", "") == "INTERPRETATION_SCHEMA_INVALID"
    assert client.calls == 2


def test_retired_provider_finding_fields_are_contract_repaired_without_authority():
    legacy = _output()
    for finding in [*legacy["primary_findings"], *legacy["supporting_findings"]]:
        finding["outcome"] = "SUPPORTED"
        finding["accepted"] = True
        finding["limitations"] = ["provider-authored limitation"]
        finding["reason_codes"] = ["FACT_GROUNDED"]
        finding["supporting_refs"] = ["fact_a"]
        finding["contradicting_refs"] = []
        finding["defects"] = []
        finding["independent_evidence_groups"] = 1
        finding["required_qualifiers"] = [
            "provider-authored assessment qualifier"
        ]
        finding["severity"] = None
        finding["method_context"] = None
    client = FakeStructuredInterpreterClient(legacy)
    service = ScientificInterpretationService(repository_factory=None, client=client)  # type: ignore[arg-type]

    result, repaired, _meta = service._generate_with_one_repair(
        InterpreterInputAssembler().assemble(
            bundle=_bundle(),
            question="Explain the RDF",
            relevance_status="CURRENT",
        )[0],
        _bundle(),
    )

    assert result.primary_findings
    assert all(item.reasoning_assessment is None for item in result.primary_findings)
    assert repaired is False
    assert client.calls == 1


@pytest.mark.parametrize("version", ["1.0", "1.1"])
@pytest.mark.parametrize("assessment_shape", ["malformed", "fabricated"])
def test_provider_does_not_author_or_receive_the_server_assessment_contract(version, assessment_shape):
    from jsonschema import Draft202012Validator

    proposed = _output()
    proposed["contract_version"] = version
    # This is deliberately not a valid assessment: the provider cannot supply
    # a server decision, even when using the older response contract.
    proposed["primary_findings"][0]["reasoning_assessment"] = {
        "accepted": True, "provider_marker": "untrusted assessment",
    }
    if assessment_shape == "fabricated":
        proposed["primary_findings"][0]["reasoning_assessment"] = {
            "claim_id": "provider-owned", "claim_type": "CAUSAL_CLAIM",
            "support_status": "DIRECTLY_SUPPORTED", "outcome": "SUPPORTED",
            "accepted": True, "scope": "untrusted assessment",
            "independent_evidence_groups": 16, "supporting_refs": ["foreign"],
        }

    class RecordingClient(FakeStructuredInterpreterClient):
        async def generate_structured(self, **kwargs):
            self.output_schema = kwargs["output_schema"]
            return await super().generate_structured(**kwargs)

    client = RecordingClient(proposed)
    service = ScientificInterpretationService(repository_factory=None, client=client)
    envelope = InterpreterInputAssembler().assemble(bundle=_bundle(), question="Explain the RDF", relevance_status="CURRENT")[0]
    result, repaired, _ = service._generate_with_one_repair(envelope, _bundle())
    assert client.calls == 1 and not repaired
    assert "reasoning_assessment" not in json.dumps(client.output_schema)
    assert "ClaimSupportAssessment" not in json.dumps(client.output_schema)
    validator = Draft202012Validator(client.output_schema)
    validator.check_schema(client.output_schema)
    valid = _output()
    valid["contract_version"] = version
    validator.validate(valid)
    assert list(validator.iter_errors(proposed))
    for invalid in (
        {**valid, "primary_findings": valid["primary_findings"] * 9},
        {**valid, "primary_findings": [{**valid["primary_findings"][0], "fact_refs": ["f"] * 33}]},
        {**valid, "primary_findings": [{**valid["primary_findings"][0], "unknown": True}]},
    ):
        assert list(validator.iter_errors(invalid))
    assert "untrusted assessment" not in result.model_dump_json()
    assessment = result.primary_findings[0].reasoning_assessment
    assert (assessment is None) == (version == "1.0")
    if assessment:
        assert assessment.claim_id == result.primary_findings[0].finding_id
    # The persisted/read contract still contains the server's assessment.
    assert "reasoning_assessment" in json.dumps(ScientificInterpretationOutput.model_json_schema())


def test_interpreter_prompt_keeps_factless_results_qualitative() -> None:
    from mdi_api.infrastructure.interpretation.client import (
        PROMPT_VERSION,
        load_interpreter_prompt,
    )

    prompt = load_interpreter_prompt()

    assert PROMPT_VERSION == "scientific-interpreter/1.19"
    assert "primary_findings array must contain at most 8 findings" in prompt
    assert "Identify each peak by its supplied angle" in prompt
    assert "language of the current original user question" in prompt
    assert "unless that question explicitly requests another response language" in prompt
    assert "do not translate those contract values" in prompt
    assert "source_native does not establish that numbers were copied unchanged" in prompt
    assert "leave the transformation history unknown" in prompt
    assert "They have different dimensions: do not compare their magnitudes" in prompt
    assert "When a Result supplies no scientific facts" in prompt
    assert "do not create separate findings" in prompt
    assert "limit findings to qualitative availability/status" in prompt
    assert "When a cited ml.r2_status fact is undefined_constant_target" in prompt
    assert "never substitute 0 or 1" in prompt
    assert "Cite the exact status fact" in prompt


def test_unknown_provider_finding_field_still_fails_closed_after_bounded_repair():
    first = _output()
    second = _output()
    first["primary_findings"][0]["unknown_provider_field"] = "not authorized"
    second["primary_findings"][0]["unknown_provider_field"] = "not authorized"
    client = FakeStructuredInterpreterClient([first, second])
    service = ScientificInterpretationService(
        repository_factory=None,  # type: ignore[arg-type]
        client=client,
    )

    with pytest.raises(Exception) as exc:
        service._generate_with_one_repair(
            InterpreterInputAssembler().assemble(
                bundle=_bundle(),
                question="Explain the RDF",
                relevance_status="CURRENT",
            )[0],
            _bundle(),
        )

    assert getattr(exc.value, "code", "") == "INTERPRETATION_SCHEMA_INVALID"
    assert client.calls == 2


def test_provider_invalid_json_gets_one_bounded_structured_output_repair():
    class InvalidProviderOutput(RuntimeError):
        code = "DEEPSEEK_RESPONSE_INVALID"

    class InvalidThenValidClient(FakeStructuredInterpreterClient):
        async def generate_structured(self, **kwargs):
            self.calls += 1
            if self.calls == 1:
                raise InvalidProviderOutput("Provider output was not strict JSON.")
            return await super().generate_structured(**kwargs)

    client = InvalidThenValidClient([_output()])
    service = ScientificInterpretationService(
        repository_factory=None,  # type: ignore[arg-type]
        client=client,
    )

    result, repaired, _meta = service._generate_with_one_repair(
        InterpreterInputAssembler().assemble(
            bundle=_bundle(),
            question="Explain the RDF",
            relevance_status="CURRENT",
        )[0],
        _bundle(),
    )

    assert result.title == "RDF 解释"
    assert repaired is True
    assert client.calls == 3


@pytest.mark.parametrize("code, expected_code, attempts", [
    ("PROVIDER_TIMEOUT", "INTERPRETATION_PROVIDER_TIMEOUT", 1),
    ("DEEPSEEK_TIMEOUT", "INTERPRETATION_PROVIDER_TIMEOUT", 1),
    ("LLM_TIMEOUT", "INTERPRETATION_PROVIDER_TIMEOUT", 1),
    ("OPENAI_TIMEOUT", "INTERPRETATION_PROVIDER_TIMEOUT", 1),
    ("PROVIDER_RATE_LIMITED", "INTERPRETATION_PROVIDER_RATE_LIMITED", 1),
    ("PROVIDER_AUTH_FAILED", "INTERPRETATION_PROVIDER_AUTH_FAILED", 1),
    ("PROVIDER_REQUEST_REJECTED", "INTERPRETATION_PROVIDER_REQUEST_REJECTED", 1),
    ("PROVIDER_OUTPUT_TRUNCATED", "INTERPRETATION_PROVIDER_OUTPUT_TRUNCATED", 1),
    ("PROVIDER_INVALID_RESPONSE", "INTERPRETATION_PROVIDER_INVALID_RESPONSE", 2),
    ("EXTERNAL_UNAVAILABLE", "INTERPRETATION_PROVIDER_UNAVAILABLE", 1),
    ("UNKNOWN_PRIVATE_CODE", "INTERPRETATION_PROVIDER_FAILED", 1),
])
def test_interpretation_failure_preserves_a_safe_reason_and_existing_science(code, expected_code, attempts):
    from mdi_llm.providers import LLMProviderError
    from tests.test_research_result_loss_recovery import _saved_result
    from tests.test_research_worker_loss_recovery import _stalled_turn

    class FailingClient:
        def __init__(self):
            self.contexts = []

        async def generate_structured(self, **kwargs):
            self.contexts.append(kwargs.get("request_context"))
            raise LLMProviderError("private-test-credential and hidden model reasoning", code=code)

    factory, turn_id = _stalled_turn("RESULT_READY", age_minutes=0)
    snapshot = _saved_result(factory, turn_id)
    client = FailingClient()
    try:
        with pytest.raises(Exception) as caught:
            ScientificInterpretationService(factory, client=client).process_turn(turn_id)
        assert caught.value.code == expected_code
        assert caught.value.__suppress_context__
        assert len(client.contexts) == attempts
        assert "private-test-credential" not in str(client.contexts)
        assert "hidden model reasoning" not in str(client.contexts)
        with factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            assert turn["status"] == "FAILED" and turn["completed_at"] is not None
            assert turn["error_code"] == expected_code
            assert "private-test-credential" not in turn["error_summary"]
            assert session.agent2.research_turns.get_message(turn["user_message_id"])["content_summary"] == "保留这条研究问题"
            assert session.agent2.scientific_result_snapshots.get(snapshot["id"])["bundle_json"] == snapshot["bundle_json"]
            assert session.agent2.interpretations.get_for_turn(turn_id) is None
            assert turn["assistant_final_message_id"] is None
            failures = [event for event in session.agent2.research_turn_events.list_for_turn(turn_id) if event["event_type"] == "TURN_FAILED"]
            assert len(failures) == 1 and failures[0]["payload_json"]["error_code"] == expected_code
    finally:
        factory.engine.dispose()


def test_interpretation_service_projects_only_an_unsupported_answer_lead_without_retry():
    client = FakeStructuredInterpreterClient(
        [_output(lead="结果还包含 42 个未被权威事实支持的峰。")]
    )
    service = ScientificInterpretationService(repository_factory=None, client=client)  # type: ignore[arg-type]

    result, repaired, _meta = service._generate_with_one_repair(
        InterpreterInputAssembler().assemble(
            bundle=_bundle(),
            question="Explain the RDF",
            relevance_status="CURRENT",
        )[0],
        _bundle(),
    )

    assert result.answer_lead == result.primary_findings[0].statement
    assert repaired is False
    assert client.calls == 1


def test_interpretation_queue_is_identity_only_and_idempotent():
    queue = InMemoryInterpretationQueue()
    turn_id = uuid4()
    first = queue.enqueue_turn(turn_id)
    second = queue.enqueue_turn(turn_id)
    assert first.enqueued is True
    assert second.enqueued is False
    assert queue.pop_next() == turn_id


def test_previous_result_interpretation_reuses_one_snapshot_across_new_turns_without_execution():
    phase2_path = Path(__file__).resolve().parent / "test_agent2_processor.py"
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
            manifests = [
                event["payload_json"]["context_manifest"]
                for event in session.agent2.research_turn_events.list_for_turn(turn.turn_id)
                if event["event_type"] == "CONTEXT_MANIFEST_RECORDED"
                and (event.get("payload_json") or {}).get("operation") == "INTERPRETER"
            ]
            assert len(manifests) == 1
            assert manifests[0]["operation"] == "INTERPRETER"
            assert manifests[0]["input_state"] == "ACTUAL"
            assert manifests[0]["invocation_role"] == "scientific_interpreter"
            assert manifests[0]["serialized_input"]
            assert manifests[0]["serialized_input_fingerprint"]
            assert manifests[0]["included_items"]
            assert any(
                item["kind"] == "SCIENTIFIC_RESULT"
                and item["result_ref"] == str(snapshot_id)
                for item in manifests[0]["included_items"]
            )
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


@pytest.mark.parametrize("predicate", ["structure.atom_x", "trajectory.selected_atom_source_x", "structure.selected_base_cartesian_x", "structure.selected_base_fractional_x"])
def test_communication_prioritizes_only_authoritative_selected_coordinate_facts(predicate):
    selected = predicate != "structure.atom_x"
    bundle = _bundle()
    bundle.facts.append(bundle.facts[0].model_copy(update={
        "fact_id": "coordinate", "predicate": predicate,
        "value": 9.3,
    }))
    bundle.result_items[0].fact_refs.append("coordinate")
    payload = _output()
    coordinate = {**payload["primary_findings"][0], "finding_id": "selected-coordinate", "statement": "所选原子的 x 坐标为 9.3 angstrom。", "fact_refs": ["coordinate"]}
    payload["primary_findings"].append(coordinate)
    raw = ScientificInterpretationOutput.model_validate(payload)
    projected = project_grounded_communication(raw, bundle)
    assert validate_interpretation(projected, bundle).valid
    assert projected.primary_findings[0].finding_id == ("selected-coordinate" if selected else "finding-1")
    assert projected.answer_lead.startswith(projected.primary_findings[0].statement.rstrip("。."))
    assert {item.statement for item in projected.primary_findings} == {item.statement for item in raw.primary_findings}
    assert raw.primary_findings[0].finding_id == "finding-1"


def test_selection_priority_does_not_repair_unfounded_coordinates():
    bundle = _bundle()
    bundle.facts[0].predicate = "trajectory.selected_atom_source_x"
    raw = ScientificInterpretationOutput.model_validate(_output("所选原子的 x 坐标为 99 angstrom。"))
    assert project_grounded_communication(raw, bundle) is raw
    assert not validate_interpretation(raw, bundle).valid
