"""Independent numerical, source-integrity and workflow checks for project tools."""
from __future__ import annotations

import asyncio
import hashlib
import math
from collections import Counter
from copy import deepcopy
from dataclasses import replace
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from mdi_adapters.context import ToolExecutionContext
from mdi_adapters.platform_builtin.project_parameters import compute_parameters, parameter_hash, result_scene
from mdi_api.agent2_errors import ScientificResultProjectionFailed
from mdi_api.application.scientific_results.projectors.base import ScientificResultProjectionContext
from mdi_api.application.scientific_results.projectors.parameters import ParameterResultProjector
from mdi_api.db import datasets, data_profiles, jobs
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.infrastructure.scientific_results.service import ScientificResultProjectionService
from mdi_api.research_agent.execution.dispatcher import ResearchExecutionDispatcher
from mdi_api.research_agent.execution.supervisor import ResearchExecutionSupervisor
from mdi_api.research_agent.planning.processor import CapabilityPlanningProcessor
from mdi_api.research_agent.registry_validation import build_default_agent2_registries, validate_agent2_registries
from mdi_schemas import AnalysisPlanV04, compute_dependency_graph_hash
from mdi_tool_registry import load_manifests
from mdi_tool_registry.project_parameters import PARAMETER_TOOLS, SI_REFERENCE_SOURCE
from mdi_workers import QueueWorkerRuntime
from tests.test_agent2_execution import CaptureQueue
from tests.test_agent2_processor import FakeStructuredClient, decision, foundation, processor, receive, structure
from tests.test_project_reference import seed_project


CASES = {
    "reference.convert_units": {"values": [5], "from_unit": "nm", "to_unit": "angstrom"},
    "generation.function_curve": {"x_min": -2, "x_max": 2, "point_count": 5, "functions": [{"kind": "polynomial", "coefficients": [-1, 0, 1]}]},
    "composition.from_formula": {"formula": "Ca3(PO4)2"},
    "viz.inline_xy": {"data_text": "时间(s),位移(nm)\n2,4\n0,0\n1,2"},
    "generation.ideal_crystal": {"prototype": "bcc", "elements": ["Fe"], "lattice_a_angstrom": 3},
}


@pytest.mark.parametrize("tool_id", CASES)
def test_independent_known_parameter_results(tool_id):
    params = deepcopy(CASES[tool_id])
    original = deepcopy(params)
    result = compute_parameters(tool_id, params)
    assert params == original
    if tool_id == "reference.convert_units":
        assert result.rows == [{"原数值": 5, "原单位": "nm", "换算结果": 50, "目标单位": "angstrom"}]
        assert next(fact for fact in result.facts if fact["predicate"] == "calculation.conversion_factor")["value"] == 10
    elif tool_id == "generation.function_curve":
        assert [row["x"] for row in result.rows] == [-2, -1, 0, 1, 2]
        assert [row["曲线 A"] for row in result.rows] == [3, 0, -1, 0, 3]
        assert result.figure["data"][0]["y"] == [3, 0, -1, 0, 3]
    elif tool_id == "composition.from_formula":
        assert [row["元素"] for row in result.rows] == ["Ca", "P", "O"]
        assert [row["化学计量数"] for row in result.rows] == [3, 2, 8]
        assert [row["原子分数"] for row in result.rows] == pytest.approx([3/13, 2/13, 8/13])
        assert sum(row["原子百分比"] for row in result.rows) == pytest.approx(100)
    elif tool_id == "viz.inline_xy":
        assert [list(row.values()) for row in result.rows] == [[2, 4], [0, 0], [1, 2]]
        assert result.figure["data"][0]["x"] == [2, 0, 1]
        assert result.details["textHash"] == hashlib.sha256(params["data_text"].encode()).hexdigest()
    else:
        assert len(result.model) == 2
        assert result.model.volume == pytest.approx(27)
        assert result.details["nearestDistance"] == pytest.approx(3 * math.sqrt(3) / 2)
        assert result.origin == "IDEAL_MODEL"


@pytest.mark.parametrize("params,expected", [
    ({"values": [25, -273.15], "from_unit": "degC", "to_unit": "K"}, [298.15, 0]),
    ({"values": [10, -10], "from_unit": "degC", "to_unit": "K", "quantity": "temperature_difference"}, [10, -10]),
    ({"values": [1], "from_unit": "eV", "to_unit": "J"}, [1.602176634e-19]),
    ({"values": [1e9], "from_unit": "Pa", "to_unit": "GPa"}, [1]),
    ({"values": [1000], "from_unit": "fs", "to_unit": "ps"}, [1]),
])
def test_si_values_temperature_semantics_and_exact_definitions(params, expected):
    result = compute_parameters("reference.convert_units", params)
    assert [row["换算结果"] for row in result.rows] == pytest.approx(expected, rel=1e-14, abs=0)


@pytest.mark.parametrize("kind,params,expected", [
    ("sine", {}, [0, 1, 0]),
    ("cosine", {}, [1, 0, -1]),
    ("gaussian", {"center": math.pi / 2, "sigma": math.pi / 2, "amplitude": 2}, [2 * math.exp(-.5), 2, 2 * math.exp(-.5)]),
])
def test_function_definitions_use_radians_and_record_resolved_defaults(kind, params, expected):
    result = compute_parameters("generation.function_curve", {"x_min": 0, "x_max": math.pi, "point_count": 3, "functions": [{"kind": kind, **params}]})
    assert result.figure["data"][0]["y"] == pytest.approx(expected, abs=1e-14)
    assert result.resolved["functions"][0]["offset"] == 0


@pytest.mark.parametrize("formula,counts", [("Li0.5FePO4", [.5, 1, 1, 4]), ("Ca(OH)2", [1, 2, 2]), ("C", [1])])
def test_formula_parentheses_fractional_stoichiometry_and_single_elements(formula, counts):
    result = compute_parameters("composition.from_formula", {"formula": formula})
    assert [row["化学计量数"] for row in result.rows] == counts


@pytest.mark.parametrize("tool_id,params", [
    ("reference.convert_units", {"values": [1], "from_unit": "nm", "to_unit": "eV"}),
    ("reference.convert_units", {"values": [-274], "from_unit": "degC", "to_unit": "K"}),
    ("reference.convert_units", {"values": [float("nan")], "from_unit": "nm", "to_unit": "nm"}),
    ("reference.convert_units", {"values": [True], "from_unit": "nm", "to_unit": "nm"}),
    ("reference.convert_units", {"values": [1], "from_unit": "nm", "to_unit": "nm", "quantity": "temperature_difference"}),
    ("generation.function_curve", {"x_min": 0, "x_max": 2, "functions": [{"kind": "logarithm"}]}),
    ("generation.function_curve", {"x_min": 300, "x_max": 400, "functions": [{"kind": "exponential"}]}),
    ("generation.function_curve", {"x_min": 0, "x_max": 0, "functions": [{"kind": "sine"}]}),
    ("generation.function_curve", {"x_min": 0, "x_max": 1, "functions": [{"kind": "python", "code": "print(1)"}]}),
    ("generation.function_curve", {"x_min": 0, "x_max": 1, "functions": [{"kind": "gaussian", "sigma": 0}]}),
    ("composition.from_formula", {"formula": "Xx2O3"}), ("composition.from_formula", {"formula": "Fe0O"}),
    ("composition.from_formula", {"formula": "CuSO4·5H2O"}), ("composition.from_formula", {"formula": "Ca(OH"}),
    ("composition.from_formula", {"formula": "(Fe1000000)1000000"}),
    ("viz.inline_xy", {"data_text": "x,y\n0,\n1,2"}),
    ("viz.inline_xy", {"data_text": "x,y\n0,=1+2\n1,2"}),
    ("viz.inline_xy", {"data_text": "x,y\n0,NaN\n1,2"}),
    ("viz.inline_xy", {"data_text": "x,x\n0,1\n1,2"}),
    ("viz.inline_xy", {**CASES["viz.inline_xy"], "x_column": 1, "y_columns": [1]}),
    ("generation.ideal_crystal", {"prototype": "rocksalt", "elements": ["Na"], "lattice_a_angstrom": 4}),
    ("generation.ideal_crystal", {"prototype": "fcc", "elements": ["Cu"], "lattice_a_angstrom": 4, "repetitions": [100, 100, 100]}),
    ("generation.ideal_crystal", {"prototype": "fcc", "elements": ["Cu"], "lattice_a_angstrom": 4, "lattice_c_angstrom": 5}),
])
def test_parameter_domains_reject_invalid_or_executable_inputs(tool_id, params):
    with pytest.raises(ValueError):
        compute_parameters(tool_id, params)


@pytest.mark.parametrize("prototype,elements,sites,neighbors", [
    ("sc", ["Fe"], 1, 6), ("bcc", ["Fe"], 2, 8), ("fcc", ["Cu"], 4, 12),
    ("diamond", ["Si"], 8, 4), ("rocksalt", ["Na", "Cl"], 8, 6),
    ("cscl", ["Cs", "Cl"], 2, 8), ("hcp", ["Mg"], 2, 12),
])
def test_ideal_crystals_keep_analytic_geometry_and_periodic_first_shell(tmp_path, prototype, elements, sites, neighbors):
    params = {"prototype": prototype, "elements": elements, "lattice_a_angstrom": 4}
    result = compute_parameters("generation.ideal_crystal", params)
    context = ToolExecutionContext("job", "project", None, "generation.ideal_crystal", "0.1.0", "1.0.0", "registry", tmp_path)
    payload = result_scene("generation.ideal_crystal", params, result, context)
    assert len(payload["scene"]["sites"]) == sites
    degrees = Counter()
    for bond in payload["scene"]["bonds"]:
        degrees[bond["from"]["site_index"]] += 1
        degrees[bond["to"]["site_index"]] += 1
        assert bond["distance_angstrom"] == pytest.approx(result.details["nearestDistance"], abs=1e-5)
        assert bond["authoritative"] is False
    assert set(degrees.values()) == {neighbors}
    assert len(degrees) == sites
    assert payload["source"]["resource_type"] == "ideal_model"
    assert payload["provenance"]["sample_analysis"] is False
    assert payload["validation"]["truncated"] is False


@pytest.mark.parametrize("text", ["x,y\n0,0\n1,2", "x\ty\n0\t0\n1\t2", "| x | y |\n|---|---|\n|0|0|\n|1|2|"])
def test_csv_tsv_markdown_retain_every_value(text):
    result = compute_parameters("viz.inline_xy", {"data_text": text})
    assert result.rows == [{"x": 0, "y": 0}, {"x": 1, "y": 2}]


def _context(tmp_path, tool_id, monkeypatch):
    monkeypatch.setattr(QueueWorkerRuntime, "_notify_agent2_progress", staticmethod(lambda job_id: None))
    registry = load_manifests()
    tool = registry.get_tool_by_id(tool_id)
    plan = AnalysisPlanV04.model_validate({"schemaVersion": "0.4", "scope": "PROJECT", "projectId": "project", "goal": "Use explicit parameters",
        "toolRegistryVersion": registry.version, "graphHash": compute_dependency_graph_hash([]), "referenceSources": tool.source.get("reference_sources", []),
        "steps": [{"stepId": "parameters", "toolId": tool_id, "purpose": "Calculate", "reason": "Explicit parameters", "inputRefs": [],
                   "params": CASES[tool_id], "output": {"artifactTypes": [kind.value for kind in tool.artifactTypes]}}]})
    repos = InMemoryRepositoryBundle.create()
    seed_project(repos, plan)
    runtime = QueueWorkerRuntime(repositories=repos, registry=registry, artifact_root=tmp_path)
    outcome = runtime.handle_job("job_reference")
    assert outcome.status == "completed", outcome.message
    artifacts = repos.artifacts.list_for_job("job_reference")
    return ScientificResultProjectionContext(project_id="project", research_session_id="parameter_session", research_turn_id=str(uuid4()),
        research_question="请分析本次输入：\n" + CASES[tool_id].get("data_text", str(CASES[tool_id])),
        execution_summary={"job_id": "job_reference", "outcome": "SUCCESS"},
        capability_plan={"steps": [{"step_id": "parameters", "capability_id": tool_id, "capability_version": "1.0"}]},
        analysis_plan=plan.model_dump(mode="json"), tool_calls=tuple(repos.tool_calls.list_for_job("job_reference")),
        artifacts=tuple(artifacts), artifact_payloads={item["id"]: runtime.artifact_storage.get_json(item["storageKey"]) for item in artifacts if item["type"].endswith("_json")})


@pytest.mark.parametrize("tool_id", CASES)
def test_parameter_results_keep_exact_fact_locators_context_and_input_identity(tmp_path, monkeypatch, tool_id):
    from mdi_api.application.scientific_results.projectors.canonical import resolve_json_pointer
    from mdi_api.application.interpretation.assembler import InterpreterInputAssembler
    context = _context(tmp_path, tool_id, monkeypatch)
    bundle = ParameterResultProjector(tool_id).project(context).bundle
    assert not bundle.source_object_refs and not bundle.output_object_refs
    assert len(bundle.tables) == 1
    assert len(bundle.figures) == (0 if tool_id == "reference.convert_units" else 1)
    for fact in bundle.facts:
        assert resolve_json_pointer(context.artifact_payloads[fact.source.artifact_id], fact.source.artifact_locator) == fact.value
    envelope, _ = InterpreterInputAssembler().assemble(bundle=bundle, question=context.research_question, relevance_status="CURRENT")
    assert envelope.result["provenance"]["input_origin"] == bundle.provenance.model_dump()["input_origin"]
    assert bundle.provenance.model_dump()["parameter_inputs"][0]["content_hash"] == parameter_hash(CASES[tool_id])


def test_ideal_repetitions_are_citable_from_saved_inputs_without_changing_artifacts(tmp_path, monkeypatch):
    from mdi_api.application.interpretation.grounding import validate_interpretation
    from mdi_api.domain.interpretation.contracts import ScientificInterpretationOutput
    monkeypatch.setitem(CASES, "generation.ideal_crystal", {
        "prototype": "fcc", "elements": ["Cu"], "lattice_a_angstrom": 3.6, "repetitions": [2, 1, 1],
    })
    context = _context(tmp_path, "generation.ideal_crystal", monkeypatch)
    before = deepcopy(context.artifact_payloads)
    bundle = ParameterResultProjector("generation.ideal_crystal").project(context).bundle
    repeat = [fact for fact in bundle.facts if fact.predicate.startswith("model.repeat_")]
    assert [fact.value for fact in repeat] == [2, 1, 1]
    assert [fact.source.artifact_locator for fact in repeat] == [f"/resolvedParameters/repetitions/{index}" for index in range(3)]
    assert all(fact.fact_id in bundle.figures[0].fact_refs for fact in repeat)
    assert context.artifact_payloads == before
    output = ScientificInterpretationOutput.model_validate({
        "contract_version": "1.0", "title": "理想超晶胞", "answer_lead": "已生成理想超晶胞。",
        "primary_findings": [{"finding_id": "supercell", "statement": "理想超晶胞重复数为 2×1×1。",
            "importance": "HIGH", "confidence": "HIGH",
            "fact_refs": [fact.fact_id for fact in repeat], "evidence_refs": [], "result_item_refs": []}],
        "supporting_findings": [], "limitations": [], "follow_up_suggestions": [],
        "primary_result_refs": [bundle.result_items[0].id], "supporting_result_refs": [],
    })
    assert validate_interpretation(output, bundle).valid
    output.primary_findings[0].statement = "理想超晶胞重复数为 3×1×1。"
    assert not validate_interpretation(output, bundle).valid


@pytest.mark.parametrize("tool_id", CASES)
def test_parameter_report_basis_keeps_bound_inputs_and_metric_names(tmp_path, monkeypatch, tool_id):
    from mdi_api.application.scientific_reports.basis import report_scientific_basis
    context = _context(tmp_path, tool_id, monkeypatch)
    bundle = ParameterResultProjector(tool_id).project(context).bundle
    before = bundle.model_dump(mode="json")
    names = {"composition.element", "calculation.function", "inline.column"}
    cited = [fact.fact_id for fact in bundle.facts if fact.predicate not in names]
    basis = report_scientific_basis(snapshot_id="snapshot", bundle=bundle,
        report={"main_findings": [{"fact_refs": cited}]},
        artifacts=list(context.artifacts), calls=list(context.tool_calls), artifact_versions={})
    assert len(basis["facts"]) == len(bundle.facts)
    assert basis["parameter_inputs"] == before["provenance"]["parameter_inputs"]
    for fact in basis["facts"]:
        assert fact["source_refs"] == []
        assert fact["input_origin"] == before["provenance"]["input_origin"]
        assert fact["input_hash"] == parameter_hash(CASES[tool_id])
        assert fact["tool_id"] == tool_id
    assert bundle.model_dump(mode="json") == before


@pytest.mark.parametrize("fault", ["hash", "origin", "tool", "call", "dataset", "duplicate_artifact", "duplicate_call", "version_binding"])
def test_parameter_report_basis_does_not_borrow_unbound_input_provenance(tmp_path, monkeypatch, fault):
    from mdi_api.application.scientific_reports.basis import report_scientific_basis
    context = _context(tmp_path, "reference.convert_units", monkeypatch)
    bundle = ParameterResultProjector("reference.convert_units").project(context).bundle
    fact = bundle.facts[0]
    artifacts, calls = deepcopy(list(context.artifacts)), deepcopy(list(context.tool_calls))
    artifact = next(item for item in artifacts if item["id"] == fact.source.artifact_id)
    call = next(item for item in calls if item["id"] == artifact["toolCallId"])
    if fault == "hash": artifact["metadata"]["provenance"]["inputHash"] = "f" * 64
    if fault == "origin": artifact["metadata"]["provenance"]["inputOrigin"] = "IDEAL_MODEL"
    if fault == "tool": call["toolId"] = "generation.ideal_crystal"
    if fault == "call": artifact["toolCallId"] = "other-call"
    if fault == "dataset": artifact["datasetId"] = "unrelated-dataset"
    if fault == "duplicate_artifact": artifacts.append(deepcopy(artifact))
    if fault == "duplicate_call": calls.append(deepcopy(call))
    basis = report_scientific_basis(snapshot_id="snapshot", bundle=bundle,
        report={"main_findings": [{"fact_refs": [fact.fact_id]}]}, artifacts=artifacts, calls=calls,
        artifact_versions={artifact["id"]: {str(uuid4())}} if fault == "version_binding" else {})
    assert len(basis["facts"]) == 1
    assert "input_hash" not in basis["facts"][0]
    assert "input_origin" not in basis["facts"][0]
    assert "parameter_inputs" not in basis
    assert basis["facts"][0]["source_refs"] == []


def test_parameter_report_does_not_expose_inputs_without_a_bound_citation(tmp_path, monkeypatch):
    from mdi_api.application.scientific_reports.basis import report_scientific_basis
    context = _context(tmp_path, "viz.inline_xy", monkeypatch)
    bundle = ParameterResultProjector("viz.inline_xy").project(context).bundle
    basis = report_scientific_basis(snapshot_id="snapshot", bundle=bundle, report={},
        artifacts=list(context.artifacts), calls=list(context.tool_calls), artifact_versions={})
    assert "parameter_inputs" not in basis
    assert not basis["facts"] and not basis["evidence"]


def test_parameter_report_does_not_replace_a_conflicting_sample_with_parameters(tmp_path, monkeypatch):
    from mdi_api.application.scientific_reports.basis import report_scientific_basis
    context = _context(tmp_path, "reference.convert_units", monkeypatch)
    bundle = ParameterResultProjector("reference.convert_units").project(context).bundle
    engine, _owner, _factory, objects, _turns = foundation()
    try:
        foreign_source = structure(objects)
        fact = bundle.facts[0]
        bundle.facts[0] = fact.model_copy(update={"source": fact.source.model_copy(update={"scientific_object_ref": foreign_source})})
        basis = report_scientific_basis(snapshot_id="snapshot", bundle=bundle,
            report={"main_findings": [{"fact_refs": [fact.fact_id]}]}, artifacts=list(context.artifacts),
            calls=list(context.tool_calls), artifact_versions={})
        assert basis["facts"][0]["source_refs"] == []
        assert "input_hash" not in basis["facts"][0]
        assert "parameter_inputs" not in basis
    finally:
        engine.dispose()


def test_ideal_model_view_repair_names_material_requirements_and_keeps_parameters(tmp_path):
    engine, owner, factory, objects, turns = foundation(tmp_path)
    try:
        unrelated = structure(objects)
        turn = receive(turns, owner, "生成 Cu 的理想 FCC 晶格，a=3.6 Å，2×1×1 超晶胞和最近邻连接，不使用项目文件。",
                       refs=[unrelated], selected=[unrelated])
        ideal = {"requirement_id": "generation.ideal_crystal", "criticality": "REQUIRED", "subject_ref_keys": [],
                 "constraints": {"prototype": "fcc", "elements": ["Cu"], "lattice_a_angstrom": 3.6, "repetitions": [2, 1, 1]}}
        invalid = decision("ANALYZE", research_objective="生成理想模型并显示近邻。", scientific_requirements=[ideal, *[
            {"requirement_id": name, "criticality": "REQUIRED", "subject_ref_keys": [], "constraints": {}}
            for name in ["structure.inspect_view", "structure.inspect_coordination"]]])
        valid = {**invalid, "scientific_requirements": [ideal]}
        fake = FakeStructuredClient([invalid, valid])
        result = asyncio.run(processor(factory, fake).process(turn.turn_id))
        assert result.status == "READY_TO_PLAN" and result.provider_calls == 2
        feedback = fake.calls[1]["request_context"]["repair"]["validation_error"]
        assert "structure.inspect_view" in feedback and "structure.inspect_coordination" in feedback
        assert "generated model is not an existing source object" in feedback
        with factory.session() as unit:
            saved = unit.agent2.research_turn_decisions.get_for_turn(turn.turn_id)
        assert saved["decision_json"]["scientific_requirements"] == [ideal]
        assert saved["decision_json"]["selected_scope_ref_keys"] == []
        assert saved["repair_attempted"] is True
        with engine.connect() as connection:
            assert connection.execute(select(func.count()).select_from(jobs)).scalar_one() == 0
    finally:
        engine.dispose()


@pytest.mark.parametrize("tool_id", CASES)
@pytest.mark.parametrize("fault", ["value", "input_hash", "sample", "recipe", "parameters"])
def test_parameter_result_rejects_changed_outputs_or_source(tmp_path, monkeypatch, tool_id, fault):
    context = _context(tmp_path, tool_id, monkeypatch)
    table = next(item for item in context.artifacts if item["type"] == "table_json")
    if fault == "value":
        context.artifact_payloads[table["id"]]["facts"][0]["value"] = "invented"
    elif fault == "input_hash":
        context.artifact_payloads[table["id"]]["inputHash"] = "0" * 64
    elif fault == "sample":
        table["datasetId"] = "unrelated"
    elif fault == "recipe":
        context = replace(context, artifacts=tuple(item for item in context.artifacts if item["type"] != "recipe_json"))
    else:
        context.analysis_plan["steps"][0]["params"]["invented"] = 1
    with pytest.raises(ScientificResultProjectionFailed):
        ParameterResultProjector(tool_id).project(context)


def test_inline_result_cannot_relabel_a_different_user_table(tmp_path, monkeypatch):
    context = _context(tmp_path, "viz.inline_xy", monkeypatch)
    with pytest.raises(ScientificResultProjectionFailed):
        ParameterResultProjector("viz.inline_xy").project(replace(context, research_question="x,y\n0,0\n1,999"))


@pytest.mark.parametrize("tool_ids", [[tool_id] for tool_id in CASES] + [
    ["reference.convert_units", "generation.ideal_crystal", "viz.inline_xy"],
])
def test_parameter_research_executes_without_a_dataset(tmp_path, monkeypatch, tool_ids):
    from mdi_api.application.interpretation.grounding import validate_interpretation
    from mdi_api.domain.interpretation.contracts import ScientificInterpretationOutput
    from mdi_api.application.scientific_reports.grounded import DeterministicScientificReportComposer
    from mdi_api.application.scientific_reports.grounding import ReportGroundingValidator
    from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
    engine, owner, factory, objects, turns = foundation(tmp_path)
    monkeypatch.setattr(QueueWorkerRuntime, "_notify_agent2_progress", staticmethod(lambda job_id: None))
    monkeypatch.setattr(ScientificResultProjectionService, "_enqueue_interpretation", staticmethod(lambda turn_id: None))
    try:
        unrelated = structure(objects)
        question = "请计算：\n" + "\n".join(CASES[tool_id].get("data_text", str(CASES[tool_id])) for tool_id in tool_ids)
        turn = receive(turns, owner, question, refs=[unrelated], selected=[unrelated])
        request = decision("ANALYZE", assistant_message="开始计算。", research_objective=question,
            scientific_requirements=[{"requirement_id": tool_id, "criticality": "REQUIRED", "subject_ref_keys": [], "constraints": CASES[tool_id]} for tool_id in tool_ids])
        assert asyncio.run(processor(factory, FakeStructuredClient([request])).process(turn.turn_id)).status == "READY_TO_PLAN"
        planned = CapabilityPlanningProcessor(factory).process(turn.turn_id)
        assert planned["status"] == "PLAN_READY", planned
        dispatcher = ResearchExecutionDispatcher(factory, queue=CaptureQueue())
        dispatched = dispatcher.dispatch_turn(turn.turn_id)
        assert dispatcher.dispatch_turn(turn.turn_id).job_id == dispatched.job_id
        runtime = QueueWorkerRuntime(repository_factory=factory, registry=load_manifests(), artifact_root=tmp_path / "artifacts")
        assert runtime.handle_job(dispatched.job_id).status == "completed"
        ResearchExecutionSupervisor(factory).sync_for_job(dispatched.job_id)
        service = ScientificResultProjectionService(factory, artifact_loader=lambda artifact: runtime.artifact_storage.get_json(artifact["storageKey"]) if artifact["type"].endswith("_json") else None)
        result = service.project_turn(turn.turn_id)
        assert service.project_turn(turn.turn_id)["id"] == result["id"]
        bundle = ScientificResultBundle.model_validate(result["bundle_json"])
        assert not bundle.source_object_refs and not bundle.provenance.source_object_version_ids
        from mdi_api.domain.scientific_results.reference_sources import project_reference_context
        provenance = project_reference_context(bundle)
        assert {item["tool_id"] for item in provenance["parameter_inputs"]} == set(tool_ids)
        assert len(bundle.result_items) == len(tool_ids)
        if len(tool_ids) > 1:
            assert provenance["input_origin"] == "MIXED"
            assert provenance["input_origins"] == ["IDEAL_MODEL", "USER_PARAMETERS", "USER_TEXT_DATA"]
            assert [source["referenceId"] for source in provenance["reference_sources"]] == ["si-conversions"]
        fact = next(fact for fact in bundle.facts if isinstance(fact.value, (int, float)))
        statement = f"保存的数值为 {fact.value} {fact.unit or ''}。"
        output = ScientificInterpretationOutput.model_validate({"contract_version": "1.0", "title": "计算结果", "answer_lead": statement,
            "primary_findings": [{"finding_id": "finding", "statement": statement, "importance": "HIGH", "confidence": "HIGH", "fact_refs": [fact.fact_id], "evidence_refs": [], "result_item_refs": [bundle.result_items[0].id]}],
            "supporting_findings": [], "limitations": [], "primary_result_refs": [bundle.result_items[0].id], "supporting_result_refs": [], "follow_up_suggestions": []})
        assert validate_interpretation(output, bundle).valid
        interpretation = {"interpretation": output.model_dump(mode="json")}
        report = DeterministicScientificReportComposer().compose(bundle=bundle, interpretation=interpretation, relevance_status="CURRENT")
        assert ReportGroundingValidator().validate(report, bundle=bundle, interpretation=interpretation) == []
        with engine.connect() as connection:
            assert connection.scalar(select(func.count()).select_from(datasets)) == 0
            assert connection.scalar(select(func.count()).select_from(data_profiles)) == 0
            assert connection.scalar(select(func.count()).select_from(jobs)) == 1
    finally:
        engine.dispose()


def test_parameter_capabilities_have_current_executable_contracts():
    from mdi_api.research_agent.capabilities.quality_evidence import get_capability_quality_evidence, scientific_contract_fingerprint
    registries = build_default_agent2_registries()
    validate_agent2_registries(registries, load_manifests())
    for key in PARAMETER_TOOLS:
        assert not registries.requirements.require(key).requires_material
        assert get_capability_quality_evidence(key).qualified_contract_fingerprint == scientific_contract_fingerprint(registries.capabilities.require(key))


@pytest.mark.parametrize("tool_id,overrides", [
    ("generation.function_curve", {"point_count": 5.0}),
    ("viz.inline_xy", {"x_column": 0.0, "y_columns": [1.0]}),
    ("generation.ideal_crystal", {"repetitions": [1.0, 1.0, 1.0]}),
])
def test_schema_valid_integral_float_parameters_have_same_science(tool_id, overrides):
    original = compute_parameters(tool_id, CASES[tool_id])
    numeric_json = compute_parameters(tool_id, {**CASES[tool_id], **overrides})
    assert numeric_json.rows == original.rows
    assert numeric_json.facts == original.facts


@pytest.mark.parametrize("tool_id", ["generation.function_curve", "composition.from_formula", "viz.inline_xy", "generation.ideal_crystal"])
def test_parameter_result_rejects_changed_plot_values_and_model_coordinates(tmp_path, monkeypatch, tool_id):
    context = _context(tmp_path, tool_id, monkeypatch)
    artifact = next(item for item in context.artifacts if item["type"] in {"plotly_json", "structure_json"})
    payload = context.artifact_payloads[artifact["id"]]
    if artifact["type"] == "plotly_json":
        payload["plotlyFigure"]["data"][0]["y"][0] += 100
    else:
        site = payload["scene"]["sites"][0]
        site["xyz"][0] += 100
    with pytest.raises(ScientificResultProjectionFailed):
        ParameterResultProjector(tool_id).project(context)


def test_planning_rejects_rewritten_inline_table_before_creating_job(tmp_path):
    engine, owner, factory, _objects, turns = foundation(tmp_path)
    try:
        turn = receive(turns, owner, "画这组数据：\nx,y\n0,1\n1,2")
        request = decision("ANALYZE", assistant_message="开始绘图。", research_objective="绘制输入数据",
            scientific_requirements=[{"requirement_id": "viz.inline_xy", "criticality": "REQUIRED", "subject_ref_keys": [],
                                      "constraints": {"data_text": "x,y\n0,999\n1,2"}}])
        assert asyncio.run(processor(factory, FakeStructuredClient([request])).process(turn.turn_id)).status == "READY_TO_PLAN"
        from mdi_api.agent2_errors import CapabilityBindingFailed
        with pytest.raises(CapabilityBindingFailed) as failure:
            CapabilityPlanningProcessor(factory).process(turn.turn_id)
        assert failure.value.code == "INLINE_DATA_SOURCE_MISMATCH"
        with engine.connect() as connection:
            assert connection.scalar(select(func.count()).select_from(jobs)) == 0
    finally:
        engine.dispose()


@pytest.mark.parametrize("unit,word", [("J", "J"), ("kJ", "kJ"), ("degC", "°C"), ("Pa", "Pa"),
    ("MPa", "MPa"), ("GPa", "GPa"), ("um", "µm"), ("ms", "ms"), ("s", "s"), ("Hz", "Hz"), ("MHz", "MHz")])
def test_parameter_units_require_the_cited_unit_in_reports_and_interpretations(unit, word):
    from mdi_api.application.interpretation.grounding import _claim_units
    from mdi_api.application.scientific_reasoning.units import canonical_unit
    from mdi_api.application.scientific_reports.grounding import ReportGroundingValidator
    facts = {"value": {"predicate": "calculation.output_value", "value": 2.5, "unit": unit}}
    assert canonical_unit(unit) in _claim_units(f"数值 2.5 {word}。", list(facts.values()))
    assert not ReportGroundingValidator._numeric_errors(f"数值 2.5 {word}。", ["value"], facts, "finding")
    assert ReportGroundingValidator._numeric_errors("数值 2.5 nm。" if unit != "nm" else "数值 2.5 J。", ["value"], facts, "finding")


@pytest.mark.parametrize("value,claim,valid", [(1.602176634e-19, "1.602176634e-19", True),
    (1.602176634e-19, "1.602e-19", True), (1.602176634e-19, "0", False),
    (1.602176634e-19, "2e-19", False), (1.602176634e-19, "1.602e-18", False), (0, "1e-20", False)])
def test_tiny_nonzero_values_cannot_be_replaced_by_zero_or_a_wrong_exponent(value, claim, valid):
    from mdi_api.application.interpretation.grounding import _numeric_claim_matches_fact
    from mdi_api.application.scientific_reports.grounding import ReportGroundingValidator
    assert _numeric_claim_matches_fact(claim, value) is valid
    facts = {"value": {"predicate": "calculation.output_value", "value": value, "unit": "J"}}
    assert (not ReportGroundingValidator._numeric_errors(f"数值 {claim} J。", ["value"], facts, "finding")) is valid
