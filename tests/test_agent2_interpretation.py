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


def test_historical_scientific_message_uses_grounded_read_projection() -> None:
    bundle = _bundle()
    interpretation_id = uuid4()
    snapshot_id = uuid4()
    message_id = "message-scientific-final"
    interpretation_row = {
        "id": interpretation_id,
        "project_id": "project",
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
            },
        }],
        Connection(),
        project_id="project",
    )

    assert "第一峰位于 2.5 angstrom。" in projected[message_id]
    assert "rdf.first_peak" not in projected[message_id]
    assert "非常准确" not in projected[message_id]
    assert "未来源的方法常识" not in projected[message_id]


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


def test_interpreter_prompt_keeps_factless_results_qualitative() -> None:
    from mdi_api.infrastructure.interpretation.client import (
        PROMPT_VERSION,
        load_interpreter_prompt,
    )

    prompt = load_interpreter_prompt()

    assert PROMPT_VERSION == "scientific-interpreter/1.2"
    assert "When a Result supplies no scientific facts" in prompt
    assert "do not create separate findings" in prompt
    assert "limit findings to qualitative availability/status" in prompt


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
