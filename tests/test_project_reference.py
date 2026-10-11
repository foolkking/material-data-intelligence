from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from mdi_adapters.context import ToolExecutionContext
from mdi_adapters.errors import ToolExecutionError
from mdi_adapters.platform_builtin.element_reference import ReferenceElementComparisonAdapter, ReferencePeriodicTableAdapter
from mdi_api.repositories import InMemoryRepositoryBundle, SqlAlchemyRepositoryBundle, compute_plan_hash
from mdi_schemas import AnalysisPlanV04, compute_dependency_graph_hash, parse_analysis_plan
from mdi_schemas.multi_source_planning import parse_artifact_lineage
from mdi_tool_registry import load_manifests, validate_dependency_plan
from mdi_tool_registry.element_reference import ELEMENT_REFERENCE_SOURCE, element_reference
from mdi_tool_registry.loader import ManifestValidationError, validate_manifest
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]


def project_plan(*, comparison=False, params=None):
    return AnalysisPlanV04.model_validate({
        "schemaVersion": "0.4", "scope": "PROJECT", "projectId": "project_reference",
        "goal": "Inspect versioned element references without a sample",
        "datasetId": None, "profileId": None, "toolRegistryVersion": load_manifests().version,
        "graphHash": compute_dependency_graph_hash([]), "dependencyBindings": [],
        "referenceSources": [ELEMENT_REFERENCE_SOURCE.model_dump(mode="json")],
        "steps": [{"stepId": "reference", "toolId": "reference.compare_elements" if comparison else "reference.periodic_table",
                   "purpose": "Show element references", "reason": "Explicit reference request", "inputRefs": [],
                   "params": params or {}, "output": {"artifactTypes": ["plotly_json", "table_json", "summary_md", "recipe_json"]}}],
    })


def run_reference(tmp_path, params=None, *, comparison=False):
    adapter = ReferenceElementComparisonAdapter() if comparison else ReferencePeriodicTableAdapter()
    registry = load_manifests()
    tool = registry.get_tool_by_id(adapter.tool_id)
    context = ToolExecutionContext("reference_job", "project_reference", None, tool.toolId, tool.version,
                                   adapter.adapter_version, registry.version, tmp_path)
    artifacts = adapter.execute(context, {"toolId": tool.toolId, "inputRefs": [], "params": params or {},
                                          "artifactTypes": [item.value for item in tool.artifactTypes]})
    payloads = {item.type.value: json.loads((tmp_path / item.storageKey).read_text(encoding="utf-8"))
                for item in artifacts if item.type.value.endswith("_json")}
    return artifacts, payloads


def test_complete_reference_preserves_all_118_identities_and_exact_reference_bytes(tmp_path):
    artifacts, outputs = run_reference(tmp_path)
    plot = outputs["plotly_json"]
    assert plot["elementCount"] == plot["valueCount"] == 118
    assert len(set(plot["selectedElements"])) == 118
    assert list(plot["elementValues"].values()) != []
    assert {item["atomicNumber"] for item in plot["elementIdentities"]} == set(range(1, 119))
    assert plot["elementValues"]["H"] == 1 and plot["elementValues"]["Og"] == 118
    assert plot["elementIdentities"][109] == {"symbol": "Ds", "atomicNumber": 110, "name": "Darmstadtium"}
    reference = ROOT / "tool_registry/reference_data/elements.v1.json"
    assert hashlib.sha256(reference.read_bytes()).hexdigest() == ELEMENT_REFERENCE_SOURCE.contentHash
    assert outputs["table_json"]["columns"] == ["symbol", "name", "atomic_number"]
    assert outputs["recipe_json"]["inputRequirements"][0]["contentHash"] == ELEMENT_REFERENCE_SOURCE.contentHash
    for artifact in artifacts:
        assert artifact.datasetId is None
        assert artifact.metadata.inputHashes == [ELEMENT_REFERENCE_SOURCE.contentHash]
        assert artifact.metadata.provenance["sampleAnalysis"] is False
        assert artifact.contentHash == hashlib.sha256((tmp_path / artifact.storageKey).read_bytes()).hexdigest()


def test_cordero_reference_values_units_missing_and_pa_are_not_placeholder_data(tmp_path):
    _, outputs = run_reference(tmp_path, {"property": "covalent_radius", "elements": ["H", "C", "Si", "Cu", "Pa", "Bk", "Og"]}, comparison=True)
    plot = outputs["plotly_json"]
    assert plot["elementValues"] == {"H": 0.31, "C": 0.76, "Si": 1.11, "Cu": 1.32, "Pa": 2.0}
    assert plot["missingElements"] == ["Bk", "Og"]
    assert plot["unit"] == "angstrom"
    assert plot["inputOrigin"] == "PLATFORM_REFERENCE" and plot["sampleAnalysis"] is False
    assert outputs["table_json"]["rows"][-1]["covalent_radius_angstrom"] is None
    trace = plot["plotlyFigure"]["data"][0]
    assert trace["x"] == ["H", "C", "Si", "Cu", "Pa"]
    assert trace["y"] == [0.31, 0.76, 1.11, 1.32, 2.0]
    with pytest.raises(ToolExecutionError, match="参考资料未覆盖"):
        run_reference(tmp_path, {"property": "covalent_radius", "elements": ["Bk", "Og"]}, comparison=True)


def test_element_filter_and_highlight_preserve_explicit_user_scope(tmp_path):
    _, outputs = run_reference(tmp_path, {"elements": ["C", "Si", "Ge"], "highlight_elements": ["Si"]})
    assert outputs["plotly_json"]["selectedElements"] == ["C", "Si", "Ge"]
    assert outputs["plotly_json"]["highlightElements"] == ["Si"]
    shapes = outputs["plotly_json"]["plotlyFigure"]["layout"]["shapes"]
    assert {shape["name"] for shape in shapes} == {"highlight-outer:Si", "highlight-inner:Si"}
    assert outputs["plotly_json"]["elementValues"] == {"C": 6, "Si": 14, "Ge": 32}
    with pytest.raises(ToolExecutionError, match="高亮元素"):
        run_reference(tmp_path, {"elements": ["Si"], "highlight_elements": ["C"]})


@pytest.mark.parametrize("params", [{"elements": ["Xx"]}, {"property": "melting_point"}, {"elements": ["Si", "Si"]},
                                     {"elements": []}, {"url": "https://example.invalid"}, {"python": "print(1)"}])
def test_reference_parameters_reject_unknown_properties_elements_and_executable_inputs(tmp_path, params):
    assert not validate_plan(project_plan(params=params).model_dump(mode="json"), registry=load_manifests()).ok
    with pytest.raises(ToolExecutionError):
        run_reference(tmp_path, params)


def test_reference_cache_is_not_mutated_by_callers():
    original = element_reference()
    original["records"][0]["symbol"] = "invented"
    assert element_reference()["records"][0]["symbol"] == "H"


def test_project_plan_schema_hash_and_registry_authority():
    plan = project_plan()
    assert isinstance(parse_analysis_plan(plan), AnalysisPlanV04)
    assert validate_plan(plan.model_dump(mode="json"), registry=load_manifests()).ok
    assert validate_dependency_plan(plan, registry=load_manifests()).ok
    schema = json.loads((ROOT / "packages/schemas/json/analysis-plan-v0.4.schema.json").read_text(encoding="utf-8"))
    assert schema == AnalysisPlanV04.model_json_schema()
    Draft202012Validator(schema).validate(plan.model_dump(mode="json"))
    changed = plan.model_dump(mode="json")
    changed["referenceSources"][0]["contentHash"] = "0" * 64
    assert compute_plan_hash(changed) != compute_plan_hash(plan)
    assert not validate_plan(changed, registry=load_manifests()).ok
    for tool_id in ["structure.rdf", "composition.ptable_heatmap"]:
        changed = plan.model_dump(mode="json")
        changed["steps"][0]["toolId"] = tool_id
        assert not validate_plan(changed, registry=load_manifests()).ok


@pytest.mark.parametrize("mutate", [
    lambda p: p.update(datasetId="hidden_dataset"),
    lambda p: p.update(profileId="hidden_profile"),
    lambda p: p.update(projectId="../outside"),
    lambda p: p.update(sourceVersions=[]),
    lambda p: p["steps"][0].update(inputRefs=[{"refType": "normalized_object", "ref": "sample", "objectType": "Structure"}]),
    lambda p: p["steps"][0]["output"].update(sourceObjectVersionIds=["invented"]),
    lambda p: p["referenceSources"].append(p["referenceSources"][0]),
    lambda p: p.update(schemaVersion="0.2"),
])
def test_project_plan_never_accepts_sample_authority_or_silent_downgrade(mutate):
    draft = project_plan().model_dump(mode="json")
    mutate(draft)
    with pytest.raises(ValueError):
        parse_analysis_plan(draft)


def test_manifest_reference_scope_and_identity_are_strict():
    import yaml
    manifest = yaml.safe_load((ROOT / "tool_registry/platform_builtin_manifest.yaml").read_text(encoding="utf-8"))
    entry = manifest["tools"][0]
    for change in ({"execution_scope": "invented"}, {"execution_scope": "material"},
                   {"reference_sources": {"elements": "1.0"}}, {"reference_sources": [{"referenceId": "elements", "url": "https://example.invalid"}]},
                   {"reference_sources": entry["reference_sources"] * 2}):
        with pytest.raises(ManifestValidationError):
            validate_manifest({"tools": [{**entry, **change}]})


def seed_project(repos, plan=None):
    plan = plan or project_plan()
    repos.projects.save({"id": plan.projectId, "name": "Reference without materials", "createdBy": "owner"})
    repos.analysis_plans.save_plan({"id": "plan_reference", "projectId": plan.projectId, "analysisPlan": plan.model_dump(mode="json"), "planHash": compute_plan_hash(plan)})
    repos.jobs.save({"id": "job_reference", "projectId": plan.projectId, "datasetId": None, "planId": "plan_reference", "status": "created", "kind": "analysis", "createdBy": "owner"})
    repos.analysis_plans.attach_plan_to_job("plan_reference", "job_reference")
    return plan


@pytest.mark.parametrize("backend", ["memory", "sqlite"])
def test_empty_project_executes_durably_without_loading_dataset_and_replays_once(tmp_path, backend):
    from sqlalchemy import create_engine
    from mdi_api.db import metadata

    engine = create_engine(f"sqlite:///{(tmp_path / 'project.sqlite').as_posix()}") if backend == "sqlite" else None
    if engine is not None:
        metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine) if engine is not None else InMemoryRepositoryBundle.create()
    try:
        plan = seed_project(repos)
        class NoMaterialResolver:
            def __call__(self, *args, **kwargs):
                pytest.fail("Project work must not load a dataset")
            def hydrate_agent2_sources(self, *args, **kwargs):
                pytest.fail("Project work must not hydrate sample versions")
        runtime = QueueWorkerRuntime(repositories=repos, registry=load_manifests(), artifact_root=tmp_path / "artifacts", object_store_resolver=NoMaterialResolver())
        first = runtime.handle_job("job_reference")
        assert first.status == "completed", repos.job_events.list_for_job("job_reference")
        assert first.plan_hash == compute_plan_hash(plan)
        calls = repos.tool_calls.list_for_job("job_reference")
        assert len(calls) == 1 and calls[0]["toolId"] == "reference.periodic_table"
        artifacts = repos.artifacts.list_for_job("job_reference")
        assert len(artifacts) == 4 and all(item["datasetId"] is None for item in artifacts)
        for artifact in artifacts:
            lineage = parse_artifact_lineage(repos.dependency_execution.get_lineage_for_artifact(artifact["id"])["artifactLineageRecord"])
            assert lineage.schemaVersion == "1.2" and lineage.planSchemaVersion == "0.4"
            assert lineage.projectId == plan.projectId and lineage.datasetId is None
            assert lineage.referenceSources == plan.referenceSources
        assert runtime.handle_job("job_reference").status == "completed"
        assert repos.tool_calls.list_for_job("job_reference") == calls
        assert repos.artifacts.list_for_job("job_reference") == artifacts
    finally:
        if engine is not None:
            engine.dispose()


@pytest.mark.parametrize("fault", ["project", "dataset", "reference", "object_store"])
def test_worker_rejects_project_reference_or_sample_scope_mismatch_before_call(tmp_path, fault):
    repos = InMemoryRepositoryBundle.create()
    plan = project_plan()
    if fault == "reference":
        draft = plan.model_dump(mode="json")
        draft["referenceSources"][0]["contentHash"] = "0" * 64
        plan = AnalysisPlanV04.model_validate(draft)
    seed_project(repos, plan)
    if fault in ("project", "dataset"):
        repos.jobs.records["job_reference"]["projectId" if fault == "project" else "datasetId"] = "foreign"
    runtime = QueueWorkerRuntime(repositories=repos, registry=load_manifests(), artifact_root=tmp_path)
    result = runtime.handle_job("job_reference", object_store={"unrelated": "sample"} if fault == "object_store" else None)
    assert result.status == "failed"
    assert repos.tool_calls.list_for_job("job_reference") == []
    assert repos.artifacts.list_for_job("job_reference") == []


def test_project_record_hash_and_ownership_are_immutable():
    repos = InMemoryRepositoryBundle.create()
    seed_project(repos)
    saved = repos.analysis_plans.get_plan("plan_reference")
    for field, value in [("projectId", "foreign"), ("datasetId", "unrelated"), ("profileId", "profile")]:
        draft = deepcopy(saved)
        draft[field] = value
        with pytest.raises(ValueError):
            repos.analysis_plans.save_plan(draft)
    draft = deepcopy(saved)
    draft["analysisPlan"]["steps"][0]["params"] = {"elements": ["Si"]}
    draft["planHash"] = compute_plan_hash(draft["analysisPlan"])
    with pytest.raises(ValueError, match="immutable"):
        repos.analysis_plans.save_plan(draft)


@pytest.fixture(scope="module")
def reference_projection_context(tmp_path_factory):
    from uuid import uuid4
    from mdi_api.application.scientific_results.projectors.base import ScientificResultProjectionContext
    repos = InMemoryRepositoryBundle.create()
    plan = seed_project(repos, project_plan(comparison=True, params={"property": "covalent_radius", "elements": ["C", "Si", "Cu", "Og"]}))
    runtime = QueueWorkerRuntime(repositories=repos, registry=load_manifests(), artifact_root=tmp_path_factory.mktemp("reference-projection"))
    assert runtime.handle_job("job_reference").status == "completed"
    artifacts = repos.artifacts.list_for_job("job_reference")
    payloads = {item["id"]: runtime.artifact_storage.get_json(item["storageKey"]) for item in artifacts if item["type"].endswith("_json")}
    return ScientificResultProjectionContext(project_id=plan.projectId, research_session_id="reference_session",
        research_turn_id=str(uuid4()), research_question="Compare C, Si, Cu and Og covalent radii",
        execution_summary={"job_id": "job_reference", "outcome": "SUCCESS"},
        capability_plan={"steps": [{"step_id": "reference", "capability_id": "reference.compare_elements", "capability_version": "1.0"}]},
        analysis_plan=plan.model_dump(mode="json"), tool_calls=tuple(repos.tool_calls.list_for_job("job_reference")),
        artifacts=tuple(artifacts), artifact_payloads=payloads)


def test_reference_projection_keeps_exact_facts_reference_identity_and_missing_values(reference_projection_context):
    from mdi_api.application.scientific_results.projectors.reference import ElementReferenceResultProjector
    from mdi_api.application.scientific_results.projectors.canonical import resolve_json_pointer
    from mdi_api.application.interpretation.assembler import InterpreterInputAssembler
    context = deepcopy(reference_projection_context)
    bundle = ElementReferenceResultProjector("reference.compare_elements").project(context).bundle
    assert bundle.source_object_refs == [] and bundle.output_object_refs == []
    assert len(bundle.figures) == 1 and len(bundle.tables) == 1
    assert bundle.provenance.model_dump()["reference_sources"][0]["contentHash"] == ELEMENT_REFERENCE_SOURCE.contentHash
    assert bundle.limitations[0].code == "PLATFORM_REFERENCE_NOT_SAMPLE"
    assert bundle.warnings[0].code == "REFERENCE_VALUES_MISSING" and "Og" in bundle.warnings[0].message
    radius_facts = [fact for fact in bundle.facts if fact.predicate == "reference.element.covalent_radius"]
    assert [fact.value for fact in radius_facts] == [0.76, 1.11, 1.32]
    assert all(fact.unit == "angstrom" for fact in radius_facts)
    for fact in bundle.facts:
        assert resolve_json_pointer(context.artifact_payloads[fact.source.artifact_id], fact.source.artifact_locator) == fact.value
    assert all(item.scientific_object_refs == [] for item in bundle.evidence)
    envelope, _ = InterpreterInputAssembler().assemble(bundle=bundle, question=context.research_question, relevance_status="CURRENT")
    encoded = envelope.model_dump(mode="json")
    assert "PLATFORM_REFERENCE_NOT_SAMPLE" in json.dumps(encoded)
    assert "covalent_radius" in json.dumps(encoded)
    reference = encoded["result"]["provenance"]["reference_sources"][0]
    assert reference["contentHash"] == ELEMENT_REFERENCE_SOURCE.contentHash
    assert reference["properties"]["covalent_radius"]["unit"] == "angstrom"
    assert reference["sources"][0]["license"] == "LGPL-2.1-or-later"
    assert bundle.provenance.artifact_ids == sorted(item["id"] for item in context.artifacts if item["type"].endswith("_json"))


@pytest.mark.parametrize("fault", ["radius", "reference", "unit", "plan", "dataset", "missing_figure", "parameters", "failed_call", "figure_values"])
def test_reference_projection_rejects_unverified_or_mixed_scientific_authority(reference_projection_context, fault):
    from dataclasses import replace
    from mdi_api.application.scientific_results.projectors.reference import ElementReferenceResultProjector
    from mdi_api.agent2_errors import ScientificResultProjectionFailed
    context = deepcopy(reference_projection_context)
    table = next(item for item in context.artifacts if item["type"] == "table_json")
    payload = context.artifact_payloads[table["id"]]
    if fault == "radius":
        payload["rows"][0]["covalent_radius_angstrom"] = 999
    elif fault == "reference":
        payload["referenceSource"]["contentHash"] = "0" * 64
    elif fault == "unit":
        payload["unit"] = "nanometer"
    elif fault == "plan":
        context.analysis_plan["projectId"] = "other"
    elif fault == "dataset":
        table["datasetId"] = "unrelated"
    elif fault == "missing_figure":
        context = replace(context, artifacts=tuple(item for item in context.artifacts if item["type"] != "plotly_json"))
    elif fault == "parameters":
        context.analysis_plan["steps"][0]["params"]["elements"] = ["C", "Si"]
    elif fault == "failed_call":
        context.tool_calls[0]["status"] = "failed"
    elif fault == "figure_values":
        figure = next(item for item in context.artifacts if item["type"] == "plotly_json")
        context.artifact_payloads[figure["id"]]["plotlyFigure"]["data"][0]["y"][0] = 999
    with pytest.raises(ScientificResultProjectionFailed):
        ElementReferenceResultProjector("reference.compare_elements").project(context)


def test_reference_report_input_and_basis_use_saved_public_sources(reference_projection_context):
    from mdi_api.application.scientific_results.projectors.reference import ElementReferenceResultProjector
    from mdi_api.application.scientific_reports.assembler import ReportComposerInputAssembler
    from mdi_api.application.scientific_reports.basis import report_scientific_basis
    context = deepcopy(reference_projection_context)
    bundle = ElementReferenceResultProjector("reference.compare_elements").project(context).bundle
    before = bundle.model_dump(mode="json")
    payload, fingerprint = ReportComposerInputAssembler().assemble(bundle=bundle, interpretation={}, relevance_status="CURRENT")
    provenance = payload["result"]["provenance"]
    assert provenance["source_object_version_ids"] == []
    assert provenance["input_origin"] == "PLATFORM_REFERENCE"
    assert provenance["reference_sources"] == before["provenance"]["reference_sources"]
    assert len(fingerprint) == 64
    basis = report_scientific_basis(snapshot_id="snapshot", bundle=bundle,
        report={"main_findings": [{"fact_refs": [fact.fact_id for fact in bundle.facts]}]},
        artifacts=list(context.artifacts), calls=list(context.tool_calls), artifact_versions={})
    assert basis["reference_sources"] == provenance["reference_sources"]
    assert all(fact["source_refs"] == [] and fact["reference_source_ids"] == ["elements"] for fact in basis["facts"])
    assert bundle.model_dump(mode="json") == before


@pytest.mark.parametrize("fault", ["extra", "scope", "duplicate"])
def test_reference_context_rejects_unbounded_or_mixed_provenance(reference_projection_context, fault):
    from mdi_api.application.scientific_results.projectors.reference import ElementReferenceResultProjector
    from mdi_api.domain.scientific_results.reference_sources import project_reference_context
    bundle = ElementReferenceResultProjector("reference.compare_elements").project(deepcopy(reference_projection_context)).bundle
    provenance = bundle.provenance
    if fault == "extra":
        provenance.reference_sources[0]["private_key"] = "must-not-cross-boundary"
    elif fault == "scope":
        provenance.execution_scope = "MATERIAL"
    else:
        provenance.reference_sources.append(deepcopy(provenance.reference_sources[0]))
    with pytest.raises(ValueError):
        project_reference_context(bundle)
