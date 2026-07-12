from __future__ import annotations

import html
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from mdi_adapters import ToolExecutionContext
from mdi_artifact_core import ArtifactPayload, LocalArtifactExporter, content_hash, stable_json_dumps
from mdi_material_parsers import NormalizedObjectDraft, build_data_profile, parse_file
from mdi_schemas import (
    AnalysisPlan,
    AnalysisStep,
    Artifact,
    ArtifactType,
    DataProfile,
    InputRef,
    JobEvent,
    JobEventStatus,
    JobStatus,
    MaterialObjectType,
    ToolExecutionRequest,
)
from mdi_tool_registry import ToolRegistry, load_manifests
from mdi_workers import InMemoryJobStore, run_tool_call_job


PHASE1_TOOL_ORDER = (
    "composition.ptable_heatmap",
    "composition.elements_hist",
    "composition.chem_sys_treemap",
    "structure.structure_3d",
    "structure.viewer_3d",
    "structure.coordination_hist",
    "ml.density_scatter",
    "ml.error_distribution",
    "ml.basic_metrics",
    "ml.outlier_table",
)


@dataclass(frozen=True)
class Phase1DemoResult:
    project: dict[str, Any]
    dataset: dict[str, Any]
    uploaded_files: list[dict[str, Any]]
    data_profile: DataProfile
    plan: AnalysisPlan
    plan_summary: dict[str, Any]
    job_id: str
    events: list[JobEvent]
    artifacts: list[Artifact]
    report_artifacts: list[Artifact]
    tool_artifacts: list[Artifact]
    object_refs: dict[str, str]


_PHASE1_RESULTS: dict[str, Phase1DemoResult] = {}


def run_phase1_demo(
    file_paths: Iterable[str | Path],
    *,
    user_prompt: str,
    artifact_root: str | Path,
    project_name: str = "Phase 1 Demo Project",
    project_id: str = "project_phase1_demo",
    dataset_id: str = "dataset_phase1_demo",
    job_id: str = "job_phase1_demo",
    registry: ToolRegistry | None = None,
) -> Phase1DemoResult:
    """Run a deterministic Phase 1 acceptance flow through approved boundaries.

    This is a local product-flow runtime for tests and demos. It deliberately
    does not call an LLM or execute user-provided code: the "planner" below is a
    deterministic AnalysisPlan builder over DataProfile + Tool Registry.
    """

    paths = [Path(path) for path in file_paths]
    active_registry = registry or load_manifests()
    artifact_root_path = Path(artifact_root)
    store = InMemoryJobStore()
    base_context = ToolExecutionContext(
        job_id=job_id,
        project_id=project_id,
        dataset_id=dataset_id,
        tool_id="phase1.runtime",
        tool_version="0.1.0",
        adapter_version="0.1.0",
        registry_version=active_registry.version,
        artifact_root=artifact_root_path,
        tool_call_id="phase1_upload",
        object_store={},
    )
    job = store.ensure_job(base_context)
    store.set_job_status(job.job_id, JobStatus.running)

    project = {
        "id": project_id,
        "name": project_name,
        "projectType": "mixed_material_dataset",
        "defaultUnits": {"energy": "eV", "length": "angstrom"},
        "defaultDownloadFormats": ["html", "json", "png", "markdown"],
        "llmConfigRef": "local_demo_config_ref",
        "status": "created",
    }
    dataset = {"id": dataset_id, "projectId": project_id, "name": "Phase 1 mixed dataset", "status": "parsing"}

    store.append_event(
        job_id,
        event_type="upload.started",
        status=JobEventStatus.running,
        message=f"Started upload and parse for {len(paths)} file(s).",
        payload={"projectId": project_id, "datasetId": dataset_id, "fileCount": len(paths)},
        progress=0.05,
    )

    parse_results = []
    for index, path in enumerate(paths, start=1):
        parse_result = parse_file(path, dataset_id=dataset_id, file_id=f"file_{index:03d}")
        parse_results.append(parse_result)
        store.append_event(
            job_id,
            event_type="file.detected",
            status=JobEventStatus.success,
            message=f"Detected {parse_result.detected_format.value} for {path.name}.",
            payload={
                "fileId": parse_result.file_id,
                "fileName": path.name,
                "detectedFormat": parse_result.detected_format.value,
            },
        )
        parsed_ok = parse_result.parse_status in {"success", "partial"}
        store.append_event(
            job_id,
            event_type="file.parsed" if parsed_ok else "file.failed",
            status=JobEventStatus.success if parsed_ok else JobEventStatus.warning,
            message=f"{path.name}: {parse_result.parse_status}.",
            payload={
                "fileId": parse_result.file_id,
                "fileName": path.name,
                "parseStatus": parse_result.parse_status,
                "objectCount": len(parse_result.objects),
                "errorCode": parse_result.error_code,
            },
        )

    objects = [obj for result in parse_results for obj in result.objects]
    profile = build_data_profile(dataset_id=dataset_id, parse_results=parse_results)
    dataset["status"] = "profile_ready"
    store.append_event(
        job_id,
        event_type="profile.ready",
        status=JobEventStatus.success,
        message="Data Profile is ready for structure and ML planning.",
        payload={
            "profileId": profile.profileId,
            "datasetType": profile.datasetType,
            "objectCount": len(profile.objects),
            "qualityIssueCount": len(profile.qualityIssues),
        },
        progress=0.25,
    )

    object_store, object_refs = _build_object_store(objects)
    store.append_event(
        job_id,
        event_type="analysis.requested",
        status=JobEventStatus.info,
        message="Received natural-language analysis request.",
        payload={"mode": "auto", "promptLength": len(user_prompt)},
        progress=0.3,
    )

    plan = build_phase1_plan(
        user_prompt=user_prompt,
        data_profile=profile,
        registry=active_registry,
        object_refs=object_refs,
    )
    plan_summary = summarize_plan(plan, active_registry)
    store.append_event(
        job_id,
        event_type="plan.generated",
        status=JobEventStatus.success,
        message=f"Generated an Analysis Plan with {len(plan.steps)} registry-approved steps.",
        payload={"planSummary": plan_summary},
        progress=0.35,
    )

    artifacts: list[Artifact] = []
    plan_artifacts = _export_plan_artifact(
        plan=plan,
        project_id=project_id,
        dataset_id=dataset_id,
        job_id=job_id,
        artifact_root=artifact_root_path,
    )
    artifacts.extend(plan_artifacts)
    for artifact in plan_artifacts:
        store.append_event(
            job_id,
            event_type="artifact.ready",
            status=JobEventStatus.success,
            message=f"Artifact ready: {artifact.name}",
            payload={"artifactId": artifact.id, "artifactType": artifact.type.value, "storageKey": artifact.storageKey},
        )

    tool_artifacts: list[Artifact] = []
    cache: dict[str, list[Artifact]] = {}
    for index, step in enumerate(plan.steps, start=1):
        tool = active_registry.get_tool_by_id(step.toolId)
        context = ToolExecutionContext(
            job_id=job_id,
            project_id=project_id,
            dataset_id=dataset_id,
            tool_id=tool.toolId,
            tool_version=tool.version,
            adapter_version="0.1.0",
            registry_version=active_registry.version,
            artifact_root=artifact_root_path,
            tool_call_id=f"tool_call_{index:02d}_{_safe_id(tool.toolId)}",
            object_store=object_store,
            resource_limits=tool.resourceLimits,
        )
        request = ToolExecutionRequest(
            jobId=job_id,
            stepId=step.stepId,
            toolId=step.toolId,
            inputRefs=step.inputRefs,
            params=step.params,
            artifactTypes=[ArtifactType(item) for item in step.output["artifactTypes"]],
        )
        result = run_tool_call_job(context, request, store=store, registry=active_registry, cache=cache)
        tool_artifacts.extend(result.execution.artifacts)

    artifacts.extend(tool_artifacts)
    report_artifacts = _export_report_artifacts(
        project=project,
        dataset=dataset,
        profile=profile,
        plan_summary=plan_summary,
        artifacts=artifacts,
        project_id=project_id,
        dataset_id=dataset_id,
        job_id=job_id,
        artifact_root=artifact_root_path,
    )
    artifacts.extend(report_artifacts)
    for artifact in report_artifacts:
        store.append_event(
            job_id,
            event_type="artifact.ready",
            status=JobEventStatus.success,
            message=f"Artifact ready: {artifact.name}",
            payload={"artifactId": artifact.id, "artifactType": artifact.type.value, "storageKey": artifact.storageKey},
        )

    store.append_event(
        job_id,
        event_type="report.ready",
        status=JobEventStatus.success,
        message="Markdown and HTML reports are ready.",
        payload={"artifactIds": [artifact.id for artifact in report_artifacts]},
        progress=0.95,
    )
    store.append_event(
        job_id,
        event_type="job.completed",
        status=JobEventStatus.success,
        message="Phase 1 analysis flow completed.",
        payload={"toolCount": len(plan.steps), "artifactCount": len(artifacts)},
        progress=1.0,
    )
    store.set_job_status(job_id, JobStatus.completed)

    result = Phase1DemoResult(
        project=project,
        dataset=dataset,
        uploaded_files=[_uploaded_file_summary(result) for result in parse_results],
        data_profile=profile,
        plan=plan,
        plan_summary=plan_summary,
        job_id=job_id,
        events=list(store.jobs[job_id].events),
        artifacts=artifacts,
        report_artifacts=report_artifacts,
        tool_artifacts=tool_artifacts,
        object_refs=object_refs,
    )
    remember_phase1_result(result)
    return result


def build_phase1_plan(
    *,
    user_prompt: str,
    data_profile: DataProfile,
    registry: ToolRegistry,
    object_refs: dict[str, str],
) -> AnalysisPlan:
    steps: list[AnalysisStep] = []
    warnings = [issue["message"] for issue in data_profile.qualityIssues if issue.get("severity") == "warning"]

    for tool_id in PHASE1_TOOL_ORDER:
        step = _phase1_step(tool_id, data_profile, registry, object_refs)
        if step is not None:
            steps.append(step)

    if len(steps) < 6:
        warnings.append("Fewer than six MVP tools are available for this dataset profile.")

    return AnalysisPlan(
        goal=user_prompt,
        datasetId=data_profile.datasetId,
        profileId=data_profile.profileId,
        toolRegistryVersion=registry.version,
        assumptions=[
            "Auto mode uses a deterministic Phase 1 planner for local acceptance.",
            "Tool execution is constrained to Tool Registry entries and adapter validation.",
        ],
        warnings=warnings,
        steps=steps,
        expectedArtifacts=_expected_artifacts_for_steps(steps),
    )


def summarize_plan(plan: AnalysisPlan, registry: ToolRegistry) -> dict[str, Any]:
    return {
        "goal": plan.goal,
        "steps": [
            {
                "toolId": step.toolId,
                "purpose": step.purpose,
                "inputSummary": step.reason,
                "keyParams": step.params,
                "expectedArtifacts": step.output["artifactTypes"],
                "displayTarget": registry.get_tool_by_id(step.toolId).outputSchema.displayTarget.value,
            }
            for step in plan.steps
        ],
        "warnings": plan.warnings,
    }


def _expected_artifacts_for_steps(steps: list[AnalysisStep]) -> list[dict[str, str]]:
    return [
        {"name": f"{step.stepId}:{artifact_type}", "type": artifact_type, "fromStepId": step.stepId}
        for step in steps
        for artifact_type in step.output["artifactTypes"]
    ]


def remember_phase1_result(result: Phase1DemoResult) -> None:
    _PHASE1_RESULTS[result.job_id] = result


def get_phase1_job_events(job_id: str) -> list[dict[str, Any]]:
    result = _PHASE1_RESULTS.get(job_id)
    if result is None:
        return []
    return [event.model_dump(mode="json") for event in result.events]


def get_phase1_job_artifacts(job_id: str) -> list[dict[str, Any]]:
    result = _PHASE1_RESULTS.get(job_id)
    if result is None:
        return []
    return [_artifact_summary(artifact) for artifact in result.artifacts]


def submit_analysis_request_stub(body: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "status": "accepted",
        "mode": (body or {}).get("mode", "auto"),
        "planningBoundary": "Agent output must be structured AnalysisPlan JSON.",
        "executionBoundary": "Tool calls are validated by Tool Registry and adapters.",
    }


def stream_phase1_job_events(job_id: str) -> Any:
    events = get_phase1_job_events(job_id)
    try:
        from fastapi.responses import StreamingResponse

        def body() -> Iterable[str]:
            for event in events:
                yield f"event: {event['eventType']}\n"
                yield f"data: {json.dumps(event, ensure_ascii=False, default=str)}\n\n"

        return StreamingResponse(body(), media_type="text/event-stream")
    except Exception:
        return events


def _phase1_step(
    tool_id: str,
    data_profile: DataProfile,
    registry: ToolRegistry,
    object_refs: dict[str, str],
) -> AnalysisStep | None:
    if tool_id.startswith("composition.") and "formulas" not in object_refs:
        return None
    if tool_id.startswith("structure.") and "structures" not in object_refs:
        return None
    if tool_id.startswith("ml.") and "ml_table" not in object_refs:
        return None

    tool = registry.get_tool_by_id(tool_id)
    artifact_types = [artifact_type.value for artifact_type in tool.artifactTypes]
    if tool_id.startswith("composition."):
        input_ref = InputRef(refType="normalized_object", ref=object_refs["formulas"], objectType=MaterialObjectType.Composition)
    elif tool_id == "structure.viewer_3d":
        input_ref = InputRef(refType="normalized_object", ref=object_refs.get("viewer_structure", object_refs["structures"]), objectType=MaterialObjectType.Structure)
    elif tool_id.startswith("structure."):
        input_ref = InputRef(refType="normalized_object", ref=object_refs["structures"], objectType=MaterialObjectType.Structure)
    else:
        input_ref = InputRef(refType="normalized_object", ref=object_refs["ml_table"], objectType=MaterialObjectType.DataFrame)

    return AnalysisStep(
        stepId=f"step_{len(tool_id)}_{_safe_id(tool_id)}",
        toolId=tool_id,
        purpose=_purpose_for(tool_id),
        reason=_input_reason_for(tool_id, data_profile),
        inputRefs=[input_ref],
        params=_default_params_for(tool_id),
        output={"artifactTypes": artifact_types, "displayTarget": tool.outputSchema.displayTarget.value},
        constraints={"stage": tool.stage, "adapter": tool.adapter},
    )


def _build_object_store(objects: list[NormalizedObjectDraft]) -> tuple[dict[str, Any], dict[str, str]]:
    structures = [obj.payload for obj in objects if obj.object_type == MaterialObjectType.Structure]
    formulas = [obj.metadata["formula"] for obj in objects if obj.object_type == MaterialObjectType.Structure and "formula" in obj.metadata]
    dataframes = [pd.DataFrame(obj.payload) for obj in objects if obj.object_type == MaterialObjectType.DataFrame]
    if dataframes and "formula" in dataframes[0].columns:
        formulas.extend(str(value) for value in dataframes[0]["formula"].dropna().tolist())

    object_store: dict[str, Any] = {}
    object_refs: dict[str, str] = {}
    if formulas:
        object_refs["formulas"] = "formulas"
        object_store["formulas"] = formulas
    if structures:
        object_refs["structures"] = "structures"
        object_store["structures"] = structures
        object_refs["viewer_structure"] = "viewer_structure"
        object_store["viewer_structure"] = structures[0]
    if dataframes:
        object_refs["ml_table"] = "ml_table"
        object_store["ml_table"] = dataframes[0]
    return object_store, object_refs


def _export_plan_artifact(
    *,
    plan: AnalysisPlan,
    project_id: str,
    dataset_id: str,
    job_id: str,
    artifact_root: Path,
) -> list[Artifact]:
    exporter = LocalArtifactExporter(artifact_root)
    plan_json = plan.model_dump(mode="json")
    return exporter.export_payloads(
        payloads=[
            ArtifactPayload(
                artifact_type=ArtifactType.analysis_plan_json,
                file_name="analysis_plan.json",
                content=plan_json,
                media_type="application/json",
            )
        ],
        project_id=project_id,
        dataset_id=dataset_id,
        job_id=job_id,
        tool_call_id="system_plan",
        tool_id="platform.analysis_plan",
        tool_version="0.1.0",
        adapter_version="0.1.0",
        input_hashes=[content_hash(stable_json_dumps({"datasetId": dataset_id, "profileId": plan.profileId}))],
        params_hash=content_hash(stable_json_dumps({"mode": "auto"})),
        provenance={"runtime": "phase1_demo", "boundary": "structured_json_plan"},
    )


def _export_report_artifacts(
    *,
    project: dict[str, Any],
    dataset: dict[str, Any],
    profile: DataProfile,
    plan_summary: dict[str, Any],
    artifacts: list[Artifact],
    project_id: str,
    dataset_id: str,
    job_id: str,
    artifact_root: Path,
) -> list[Artifact]:
    markdown = _report_markdown(project=project, dataset=dataset, profile=profile, plan_summary=plan_summary, artifacts=artifacts)
    html_report = _report_html(markdown)
    exporter = LocalArtifactExporter(artifact_root)
    return exporter.export_payloads(
        payloads=[
            ArtifactPayload(ArtifactType.report_md, "report.md", markdown, "text/markdown"),
            ArtifactPayload(ArtifactType.report_html, "report.html", html_report, "text/html"),
        ],
        project_id=project_id,
        dataset_id=dataset_id,
        job_id=job_id,
        tool_call_id="system_report",
        tool_id="platform.report",
        tool_version="0.1.0",
        adapter_version="0.1.0",
        input_hashes=[content_hash(stable_json_dumps(plan_summary)), content_hash(profile.model_dump_json())],
        params_hash=content_hash(stable_json_dumps({"formats": ["markdown", "html"]})),
        provenance={"runtime": "phase1_demo", "reportFormats": ["markdown", "html"]},
    )


def _report_markdown(
    *,
    project: dict[str, Any],
    dataset: dict[str, Any],
    profile: DataProfile,
    plan_summary: dict[str, Any],
    artifacts: list[Artifact],
) -> str:
    artifact_types = sorted({artifact.type.value for artifact in artifacts})
    lines = [
        "# Phase 1 Material Analysis Report",
        "",
        f"- Project: `{project['name']}`",
        f"- Dataset: `{dataset['name']}`",
        f"- Data Profile: `{profile.profileId}`",
        f"- Dataset type: `{profile.datasetType}`",
        f"- Structures: {profile.structureSummary.get('nStructures') if profile.structureSummary else 0}",
        f"- Table rows: {profile.tableSummary.get('nRows') if profile.tableSummary else 0}",
        "",
        "## Analysis Plan",
        "",
    ]
    for index, step in enumerate(plan_summary["steps"], start=1):
        lines.append(f"{index}. `{step['toolId']}` - {step['purpose']}")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Count: {len(artifacts)}",
            f"- Types: {', '.join(artifact_types)}",
            "",
            "## Reproducibility",
            "",
            "All executable steps were validated by Tool Registry and executed by adapters.",
        ]
    )
    return "\n".join(lines) + "\n"


def _report_html(markdown: str) -> str:
    escaped = html.escape(markdown)
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<title>Phase 1 Material Analysis Report</title></head>"
        "<body><pre>"
        f"{escaped}"
        "</pre></body></html>"
    )


def _uploaded_file_summary(result: Any) -> dict[str, Any]:
    return {
        "fileId": result.file_id,
        "name": result.file_path.name,
        "detectedFormat": result.detected_format.value,
        "status": result.parse_status,
        "objectCount": len(result.objects),
    }


def _artifact_summary(artifact: Artifact) -> dict[str, Any]:
    return {
        "id": artifact.id,
        "type": artifact.type.value,
        "name": artifact.name,
        "downloadUrl": f"/artifacts/{artifact.storageKey}",
        "toolCallId": artifact.toolCallId,
    }


def _default_params_for(tool_id: str) -> dict[str, Any]:
    defaults: dict[str, dict[str, Any]] = {
        "composition.ptable_heatmap": {"countMode": "composition", "colorScale": "viridis", "title": "Element coverage"},
        "composition.elements_hist": {"countMode": "composition", "keepTop": 20, "title": "Element distribution"},
        "composition.chem_sys_treemap": {"showCounts": "value", "maxCells": 20, "title": "Chemical systems"},
        "structure.structure_3d": {"showCell": True, "showBonds": False, "maxStructures": 1},
        "structure.viewer_scene_metadata": {"inferBonds": True, "maxSites": 500, "maxBonds": 2000, "cameraPreset": "auto"},
        "structure.viewer_export_package": {"inferBonds": True, "maxSites": 500, "maxBonds": 2000, "cameraPreset": "auto"},
        "structure.viewer_3d": {
            "include_bonds": True,
            "bond_cutoff_angstrom": 3.0,
            "max_sites": 256,
            "max_bonds": 2048,
            "coordinate_basis": "cartesian_angstrom",
            "include_cartesian_positions": True,
            "include_fractional_positions": True,
            "cell_expansion": [1, 1, 1],
            "style_preset": "default",
            "camera_preset": "auto",
        },
        "structure.coordination_hist": {
            "neighbor_policy": "distance_cutoff",
            "cutoff_angstrom": 3.0,
            "max_sites": 500,
            "max_neighbors_per_site": 128,
            "include_site_details": True,
            "group_by_element": True,
            "include_pair_counts": True,
            "plot_kind": "bar",
        },
        "ml.density_scatter": {
            "targetColumn": "y_true",
            "predictionColumn": "y_pred",
            "nBins": False,
            "identityLine": True,
            "title": "Prediction density scatter",
        },
        "ml.error_distribution": {"targetColumn": "y_true", "predictionColumn": "y_pred", "nBins": 10, "topK": 5},
        "ml.basic_metrics": {"targetColumn": "y_true", "predictionColumn": "y_pred"},
        "ml.outlier_table": {"targetColumn": "y_true", "predictionColumn": "y_pred", "topK": 5},
    }
    return defaults.get(tool_id, {})


def _purpose_for(tool_id: str) -> str:
    purposes = {
        "composition.ptable_heatmap": "Inspect element coverage and frequency.",
        "composition.elements_hist": "Summarize element counts across formulas.",
        "composition.chem_sys_treemap": "Show chemical-system distribution.",
        "structure.structure_3d": "Render a representative periodic structure.",
        "structure.viewer_scene_metadata": "Generate static scene metadata for future structure viewer rendering.",
        "structure.viewer_export_package": "Generate a static structure viewer export package without a renderer.",
        "structure.viewer_3d": "Generate canonical artifacts for the minimal interactive crystal structure viewer.",
        "structure.coordination_hist": "Check local coordination environments.",
        "ml.density_scatter": "Compare predicted and target values.",
        "ml.error_distribution": "Inspect residual distribution and top errors.",
        "ml.basic_metrics": "Compute regression quality metrics.",
        "ml.outlier_table": "List highest-error rows for review.",
    }
    return purposes[tool_id]


def _input_reason_for(tool_id: str, profile: DataProfile) -> str:
    if tool_id.startswith("composition."):
        elements = ", ".join((profile.structureSummary or {}).get("elements", []))
        return f"Formulas are available from structure/table objects; detected elements: {elements}."
    if tool_id.startswith("structure."):
        count = (profile.structureSummary or {}).get("nStructures", 0)
        return f"{count} periodic structure object(s) are available."
    columns = [column["name"] for column in (profile.tableSummary or {}).get("columns", [])]
    return f"ML table columns are available: {', '.join(columns)}."


def _safe_id(value: str) -> str:
    return value.replace(".", "_").replace("-", "_")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
