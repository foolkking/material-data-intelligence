from __future__ import annotations

import html
import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
from pydantic import BaseModel, Field, model_validator

from mdi_api.artifact_storage import LocalFileArtifactStorage
from mdi_adapters import ToolExecutionContext
from mdi_artifact_core import ArtifactPayload, LocalArtifactExporter, content_hash, stable_json_dumps
from mdi_material_parsers import NormalizedObjectDraft, ParseResult, build_data_profile, parse_file
from mdi_schemas import (
    AnalysisPlan,
    AnalysisStep,
    Artifact,
    ArtifactType,
    DataProfile,
    InputRef,
    JobEventStatus,
    JobStatus,
    MaterialObjectType,
    ToolExecutionRequest,
    VisualizationRecipe,
)
from mdi_tool_registry import ToolRegistry, load_manifests
from mdi_workers import InMemoryJobStore, WorkerToolExecutionError, run_tool_call_job


PHASE2_TOOL_ORDER = (
    "composition.ptable_heatmap",
    "composition.chem_sys_treemap",
    "structure.viewer_3d",
    "ml.basic_metrics",
    "ml.outlier_table",
)

DEFAULT_ARTIFACT_ROOT = Path("artifacts") / "phase2_runtime"


class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    projectType: str = "mixed_material_dataset"
    defaultUnits: dict[str, str] = Field(default_factory=dict)
    defaultDownloadFormats: list[str] = Field(default_factory=lambda: ["html", "json", "png", "markdown"])
    llmConfigRef: str | None = None


class InlineUploadFile(BaseModel):
    fileName: str = Field(min_length=1, max_length=240)
    content: str


class DatasetUploadRequest(BaseModel):
    projectId: str
    datasetName: str = Field(default="Uploaded materials dataset", min_length=1, max_length=160)
    filePaths: list[str] = Field(default_factory=list)
    files: list[InlineUploadFile] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_files(self) -> "DatasetUploadRequest":
        if not self.filePaths and not self.files:
            raise ValueError("filePaths or files must contain at least one file.")
        return self


class CreateJobRequest(BaseModel):
    projectId: str
    datasetId: str
    userPrompt: str = "Analyze this materials dataset."
    mode: str = "auto"


@dataclass
class ProjectRecord:
    id: str
    name: str
    project_type: str
    default_units: dict[str, str]
    default_download_formats: list[str]
    llm_config_ref: str | None
    created_at: str = field(default_factory=lambda: _utc_now())

    def summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "projectId": self.id,
            "name": self.name,
            "role": "owner",
            "projectType": self.project_type,
            "defaultUnits": self.default_units,
            "defaultDownloadFormats": self.default_download_formats,
            "llmConfigRef": self.llm_config_ref,
            "status": "created",
            "createdAt": self.created_at,
        }


@dataclass
class DatasetRecord:
    id: str
    project_id: str
    name: str
    files: list[dict[str, Any]]
    parse_results: list[ParseResult]
    objects: list[NormalizedObjectDraft]
    profile: DataProfile
    object_store: dict[str, Any]
    object_refs: dict[str, str]
    normalized_exports: list[dict[str, str]]
    created_at: str = field(default_factory=lambda: _utc_now())
    status: str = "profile_ready"

    def summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "datasetId": self.id,
            "projectId": self.project_id,
            "name": self.name,
            "status": self.status,
            "fileCount": len(self.files),
            "objectCount": len(self.objects),
            "profileId": self.profile.profileId,
            "normalizedExports": self.normalized_exports,
            "createdAt": self.created_at,
        }


@dataclass
class JobRunRecord:
    id: str
    project_id: str
    dataset_id: str
    prompt: str
    plan: AnalysisPlan
    plan_summary: dict[str, Any]
    artifact_ids: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: _utc_now())
    updated_at: str = field(default_factory=lambda: _utc_now())


class LocalFileArtifactStore:
    """Small local artifact index over LocalArtifactExporter output."""

    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir)
        self.artifacts: dict[str, Artifact] = {}

    def register(self, artifacts: Iterable[Artifact]) -> None:
        for artifact in artifacts:
            self.artifacts[artifact.id] = artifact

    def list_for_job(self, job_id: str) -> list[Artifact]:
        return [artifact for artifact in self.artifacts.values() if artifact.jobId == job_id]

    def get(self, artifact_id: str) -> Artifact:
        try:
            return self.artifacts[artifact_id]
        except KeyError as exc:
            raise LookupError(f"Unknown artifact_id: {artifact_id}") from exc

    def detail(self, artifact_id: str) -> dict[str, Any]:
        artifact = self.get(artifact_id)
        path = self.root_dir / artifact.storageKey
        payload = artifact.model_dump(mode="json")
        payload["artifactId"] = artifact.id
        payload["downloadUrl"] = f"/artifacts/{artifact.id}/download"
        payload["storageProvider"] = payload.get("storageProvider") or "local"
        payload["contentType"] = payload.get("contentType") or artifact.metadata.provenance.get("mediaType") or _content_type_for_name(artifact.name)
        payload["sha256"] = payload.get("sha256") or artifact.contentHash
        payload["createdAt"] = payload.get("createdAt") or artifact.metadata.createdAt
        payload["exists"] = path.exists()
        payload["contentEncoding"] = "missing"
        if path.exists():
            content = path.read_bytes()
            if artifact.type == ArtifactType.preview_png:
                payload["contentEncoding"] = "binary"
            else:
                text = content.decode("utf-8")
                if artifact.name.endswith(".json"):
                    payload["content"] = json.loads(text)
                    payload["contentEncoding"] = "json"
                else:
                    payload["content"] = text
                    payload["contentEncoding"] = "text"
        return payload


class Phase2ProductRuntime:
    """Deterministic in-memory product loop for Phase 2 acceptance.

    This runtime is intentionally local and replaceable. It proves the product
    state transitions and query API without introducing PostgreSQL, Redis,
    Celery, MinIO, or a real LLM provider.
    """

    def __init__(self, artifact_root: str | Path = DEFAULT_ARTIFACT_ROOT, registry: ToolRegistry | None = None) -> None:
        self.artifact_root = Path(artifact_root)
        self.registry = registry or load_manifests()
        self.projects: dict[str, ProjectRecord] = {}
        self.datasets: dict[str, DatasetRecord] = {}
        self.jobs: dict[str, JobRunRecord] = {}
        self.job_store = InMemoryJobStore()
        self.artifact_store = LocalFileArtifactStore(self.artifact_root)
        self.artifact_storage = LocalFileArtifactStorage(self.artifact_root)
        self._project_seq = 0
        self._dataset_seq = 0
        self._job_seq = 0

    def create_project(self, request: CreateProjectRequest | dict[str, Any]) -> dict[str, Any]:
        request = request if isinstance(request, CreateProjectRequest) else CreateProjectRequest.model_validate(request)
        self._project_seq += 1
        project = ProjectRecord(
            id=f"project_{self._project_seq:04d}",
            name=request.name,
            project_type=request.projectType,
            default_units=request.defaultUnits,
            default_download_formats=request.defaultDownloadFormats,
            llm_config_ref=request.llmConfigRef,
        )
        self.projects[project.id] = project
        return project.summary()

    def list_projects(self) -> list[dict[str, Any]]:
        return [project.summary() for project in self.projects.values()]

    def list_datasets(self) -> list[dict[str, Any]]:
        return [dataset.summary() for dataset in self.datasets.values()]

    def ensure_project(self, project_id: str, *, name: str = "Local Demo Project") -> dict[str, Any]:
        if project_id not in self.projects:
            self.projects[project_id] = ProjectRecord(
                id=project_id,
                name=name,
                project_type="mixed_material_dataset",
                default_units={},
                default_download_formats=["html", "json", "png", "markdown"],
                llm_config_ref=None,
            )
        return self.projects[project_id].summary()

    def upload_dataset(self, request: DatasetUploadRequest | dict[str, Any]) -> dict[str, Any]:
        request = request if isinstance(request, DatasetUploadRequest) else DatasetUploadRequest.model_validate(request)
        self._require_project(request.projectId)
        self._dataset_seq += 1
        dataset_id = f"dataset_{self._dataset_seq:04d}"
        paths = self._materialize_uploads(request, dataset_id)
        parse_results: list[ParseResult] = []
        for index, path in enumerate(paths, start=1):
            parse_results.append(parse_file(path, dataset_id=dataset_id, file_id=f"file_{index:03d}"))

        objects = [obj for result in parse_results for obj in result.objects]
        profile = build_data_profile(
            dataset_id=dataset_id,
            parse_results=parse_results,
            platform_tool_ids={tool.toolId for tool in self.registry.tools},
        )
        object_store, object_refs = build_object_store(objects)
        normalized_exports = self._export_normalized_objects(request.projectId, dataset_id, objects)
        record = DatasetRecord(
            id=dataset_id,
            project_id=request.projectId,
            name=request.datasetName,
            files=[_uploaded_file_summary(result) for result in parse_results],
            parse_results=parse_results,
            objects=objects,
            profile=profile,
            object_store=object_store,
            object_refs=object_refs,
            normalized_exports=normalized_exports,
        )
        self.datasets[dataset_id] = record
        return {**record.summary(), "files": record.files, "profile": profile.model_dump(mode="json")}

    def get_dataset(self, dataset_id: str) -> dict[str, Any]:
        dataset = self._require_dataset(dataset_id)
        return {**dataset.summary(), "files": dataset.files, "demo": dataset.id == "dataset_demo"}

    def get_dataset_profile(self, dataset_id: str) -> dict[str, Any]:
        return self._require_dataset(dataset_id).profile.model_dump(mode="json")

    def get_dataset_profile_model(self, dataset_id: str) -> DataProfile:
        return self._require_dataset(dataset_id).profile

    def get_dataset_object_store(self, dataset_id: str) -> dict[str, Any]:
        return dict(self._require_dataset(dataset_id).object_store)

    def create_dataset_profile(self, dataset_id: str) -> dict[str, Any]:
        dataset = self._require_dataset(dataset_id)
        return {
            **dataset.profile.model_dump(mode="json"),
            "status": dataset.status,
            "profileGenerated": True,
        }

    def ensure_demo_dataset(self, project_id: str = "project_local") -> dict[str, Any]:
        self.ensure_project(project_id, name="Demo Materials Analysis Project")
        dataset_id = "dataset_demo"
        if dataset_id in self.datasets:
            dataset = self.datasets[dataset_id]
            return {
                **dataset.summary(),
                "demo": True,
                "files": dataset.files,
                "profile": dataset.profile.model_dump(mode="json"),
            }

        request = DatasetUploadRequest(
            projectId=project_id,
            datasetName="Demo metrics dataset",
            files=[
                InlineUploadFile(
                    fileName="demo_metrics.csv",
                    content=(
                        "formula,y_true,y_pred\n"
                        "LiFePO4,3.45,3.40\n"
                        "NaCl,1.20,1.25\n"
                        "SiO2,2.10,2.00\n"
                        "Al2O3,2.80,2.95\n"
                        "MgO,1.85,1.78\n"
                    ),
                )
            ],
        )
        paths = self._materialize_uploads(request, dataset_id)
        parse_results: list[ParseResult] = []
        for index, path in enumerate(paths, start=1):
            parse_results.append(parse_file(path, dataset_id=dataset_id, file_id=f"file_{index:03d}"))

        objects = [obj for result in parse_results for obj in result.objects]
        profile = build_data_profile(
            dataset_id=dataset_id,
            parse_results=parse_results,
            platform_tool_ids={tool.toolId for tool in self.registry.tools},
        )
        object_store, object_refs = build_object_store(objects)
        normalized_exports = self._export_normalized_objects(project_id, dataset_id, objects)
        record = DatasetRecord(
            id=dataset_id,
            project_id=project_id,
            name=request.datasetName,
            files=[_uploaded_file_summary(result) for result in parse_results],
            parse_results=parse_results,
            objects=objects,
            profile=profile,
            object_store=object_store,
            object_refs=object_refs,
            normalized_exports=normalized_exports,
        )
        self.datasets[dataset_id] = record
        return {**record.summary(), "demo": True, "files": record.files, "profile": profile.model_dump(mode="json")}

    def create_job(
        self,
        request: CreateJobRequest | dict[str, Any],
        *,
        analysis_plan: AnalysisPlan | None = None,
        execute: bool = True,
    ) -> dict[str, Any]:
        request = request if isinstance(request, CreateJobRequest) else CreateJobRequest.model_validate(request)
        self._require_project(request.projectId)
        dataset = self._require_dataset(request.datasetId)
        if dataset.project_id != request.projectId:
            raise LookupError("Dataset does not belong to the requested project.")

        self._job_seq += 1
        job_id = f"job_{self._job_seq:04d}"
        base_context = ToolExecutionContext(
            job_id=job_id,
            project_id=request.projectId,
            dataset_id=request.datasetId,
            tool_id="platform.phase2_runtime",
            tool_version="0.1.0",
            adapter_version="0.1.0",
            registry_version=self.registry.version,
            artifact_root=self.artifact_root,
            tool_call_id="system",
            object_store=dataset.object_store,
        )
        job = self.job_store.ensure_job(base_context)
        self.job_store.append_event(
            job_id,
            event_type="job.created",
            status=JobEventStatus.info,
            message="Created local Phase 2 job.",
            payload={"projectId": request.projectId, "datasetId": request.datasetId, "mode": request.mode},
            progress=0.0,
        )
        self.job_store.set_job_status(job_id, JobStatus.queued)
        self.job_store.append_event(
            job_id,
            event_type="job.queued",
            status=JobEventStatus.info,
            message="Queued job for LocalWorkerRuntime.",
            progress=0.05,
        )
        self.job_store.set_job_status(job_id, JobStatus.running)
        self.job_store.append_event(
            job_id,
            event_type="job.running",
            status=JobEventStatus.running,
            message="LocalWorkerRuntime started deterministic execution.",
            progress=0.1,
        )
        self.job_store.append_event(
            job_id,
            event_type="profile.ready",
            status=JobEventStatus.success,
            message="Data Profile is available for deterministic planning.",
            payload={"profileId": dataset.profile.profileId, "datasetType": dataset.profile.datasetType},
            progress=0.2,
        )

        if analysis_plan is not None:
            # Phase 8A: execute the EXACT validated plan (e.g. from the LLM
            # planner). Never overwrite it with the deterministic planner.
            plan = analysis_plan
            plan_source = "provided"
        else:
            plan = build_phase2_plan(
                user_prompt=request.userPrompt,
                data_profile=dataset.profile,
                registry=self.registry,
                object_refs=dataset.object_refs,
            )
            plan_source = "deterministic"
        plan_summary = summarize_plan(plan, self.registry)
        record = JobRunRecord(
            id=job_id,
            project_id=request.projectId,
            dataset_id=request.datasetId,
            prompt=request.userPrompt,
            plan=plan,
            plan_summary=plan_summary,
        )
        self.jobs[job_id] = record
        self.job_store.append_event(
            job_id,
            event_type="plan.generated",
            status=JobEventStatus.success,
            message=f"Loaded {plan_source} plan with {len(plan.steps)} MVP tool call(s).",
            payload={"planSummary": plan_summary, "planSource": plan_source},
            progress=0.3,
        )

        system_artifacts = []
        system_artifacts.extend(self._export_plan_artifact(plan=plan, project_id=request.projectId, dataset_id=request.datasetId, job_id=job_id))
        system_artifacts.extend(self._export_recipe_artifact(plan=plan, project_id=request.projectId, dataset_id=request.datasetId, job_id=job_id))
        self._register_artifacts(job_id, system_artifacts, event_progress=0.35)

        if not execute:
            # Phase 8A: planned-only mode. The validated plan is persisted and
            # the plan artifact is exported, but no ToolCalls run. The job
            # stays in a queued/planned state for later execution.
            self.job_store.append_event(
                job_id,
                event_type="job.planned",
                status=JobEventStatus.info,
                message="Planned job created; execution deferred (execute=False).",
                payload={"planSource": plan_source, "toolCount": len(plan.steps)},
                progress=0.4,
            )
            self.job_store.set_job_status(job_id, JobStatus.queued)
            record.artifact_ids = [artifact.id for artifact in self.artifact_store.list_for_job(job_id)]
            record.updated_at = _utc_now()
            return self.get_job(job_id)

        cache: dict[str, list[Artifact]] = {}
        tool_artifacts: list[Artifact] = []
        try:
            for index, step in enumerate(plan.steps, start=1):
                tool = self.registry.get_tool_by_id(step.toolId)
                context = ToolExecutionContext(
                    job_id=job_id,
                    project_id=request.projectId,
                    dataset_id=request.datasetId,
                    tool_id=tool.toolId,
                    tool_version=tool.version,
                    adapter_version="0.1.0",
                    registry_version=self.registry.version,
                    artifact_root=self.artifact_root,
                    tool_call_id=f"tool_call_{index:02d}_{_safe_id(tool.toolId)}",
                    object_store=dataset.object_store,
                    resource_limits=tool.resourceLimits,
                )
                tool_request = ToolExecutionRequest(
                    jobId=job_id,
                    stepId=step.stepId,
                    toolId=step.toolId,
                    inputRefs=step.inputRefs,
                    params=step.params,
                    artifactTypes=[ArtifactType(item) for item in step.output["artifactTypes"]],
                )
                result = run_tool_call_job(context, tool_request, store=self.job_store, registry=self.registry, cache=cache)
                tool_artifacts.extend(result.execution.artifacts)
                self.artifact_store.register(result.execution.artifacts)
        except WorkerToolExecutionError:
            self.job_store.append_event(
                job_id,
                event_type="job.failed",
                status=JobEventStatus.error,
                message="LocalWorkerRuntime failed while executing a ToolCall.",
                progress=1.0,
            )
            self.job_store.set_job_status(job_id, JobStatus.failed)
            record.updated_at = _utc_now()
            return self.get_job(job_id)

        report_artifacts = self._export_report_artifacts(
            project=self.projects[request.projectId],
            dataset=dataset,
            plan_summary=plan_summary,
            artifacts=[*system_artifacts, *tool_artifacts],
            job_id=job_id,
        )
        self._register_artifacts(job_id, report_artifacts, event_progress=0.95)
        self.job_store.append_event(
            job_id,
            event_type="report.ready",
            status=JobEventStatus.success,
            message="Markdown and HTML reports are ready.",
            payload={"artifactIds": [artifact.id for artifact in report_artifacts]},
            progress=0.97,
        )
        self.job_store.append_event(
            job_id,
            event_type="job.completed",
            status=JobEventStatus.success,
            message="Phase 2 local product loop completed.",
            payload={"toolCount": len(plan.steps), "artifactCount": len(self.artifact_store.list_for_job(job_id))},
            progress=1.0,
        )
        self.job_store.set_job_status(job_id, JobStatus.completed)
        record.artifact_ids = [artifact.id for artifact in self.artifact_store.list_for_job(job_id)]
        record.updated_at = _utc_now()
        return self.get_job(job_id)

    def get_job(self, job_id: str) -> dict[str, Any]:
        record = self._require_job(job_id)
        worker_job = self.job_store.jobs[job_id]
        artifacts = self.artifact_store.list_for_job(job_id)
        return {
            "id": record.id,
            "jobId": record.id,
            "projectId": record.project_id,
            "datasetId": record.dataset_id,
            "status": worker_job.status.value,
            "createdAt": worker_job.created_at,
            "updatedAt": worker_job.updated_at,
            "prompt": record.prompt,
            "plan": record.plan.model_dump(mode="json"),
            "planSummary": record.plan_summary,
            "toolCallCount": len(worker_job.tool_calls),
            "artifactCount": len(artifacts),
            "reportArtifactIds": [artifact.id for artifact in artifacts if artifact.type in {ArtifactType.report_md, ArtifactType.report_html}],
        }

    def get_job_events(self, job_id: str, after_seq: int = 0) -> list[dict[str, Any]]:
        self._require_job(job_id)
        return [event.model_dump(mode="json") for event in self.job_store.list_events_after_seq(job_id, after_seq)]

    async def iter_job_sse_events(self, job_id: str, after_seq: int = 0) -> Any:
        self._require_job(job_id)
        for event in self.job_store.list_events_after_seq(job_id, after_seq):
            yield _sse_event(event.model_dump(mode="json"))

    def get_job_tool_calls(self, job_id: str) -> list[dict[str, Any]]:
        self._require_job(job_id)
        return [tool_call.model_dump(mode="json") for tool_call in self.job_store.jobs[job_id].tool_calls.values()]

    def get_job_artifacts(self, job_id: str) -> list[dict[str, Any]]:
        self._require_job(job_id)
        return [_artifact_summary(artifact) for artifact in self.artifact_store.list_for_job(job_id)]

    def get_artifact(self, artifact_id: str) -> dict[str, Any]:
        return self.artifact_store.detail(artifact_id)

    def get_artifact_download(self, artifact_id: str) -> dict[str, Any]:
        artifact = self.artifact_store.get(artifact_id)
        content_type = artifact.metadata.provenance.get("mediaType") or _content_type_for_name(artifact.name)
        signed = self.artifact_storage.signed_url(artifact.storageKey, content_type=content_type)
        return {
            "artifactId": artifact.id,
            "storageKey": artifact.storageKey,
            "previewKey": artifact.previewKey,
            "contentType": content_type,
            "sha256": artifact.contentHash,
            "contentHash": artifact.contentHash,
            "sizeBytes": artifact.sizeBytes,
            "signedUrl": signed.url,
            "signedUrlStatus": signed.status,
            "expiresInSec": signed.expires_in_sec,
        }

    def _materialize_uploads(self, request: DatasetUploadRequest, dataset_id: str) -> list[Path]:
        raw_dir = self.artifact_root / "projects" / request.projectId / "datasets" / dataset_id / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        paths: list[Path] = []
        for file_path in request.filePaths:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Upload file does not exist: {file_path}")
            file_id = f"file_{len(paths) + 1:03d}"
            target = raw_dir / file_id / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            paths.append(target)
        for inline_file in request.files:
            file_id = f"file_{len(paths) + 1:03d}"
            target = raw_dir / file_id / Path(inline_file.fileName).name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(inline_file.content, encoding="utf-8")
            paths.append(target)
        return paths

    def _export_normalized_objects(
        self,
        project_id: str,
        dataset_id: str,
        objects: list[NormalizedObjectDraft],
    ) -> list[dict[str, str]]:
        exporter = LocalArtifactExporter(self.artifact_root)
        exports: list[dict[str, str]] = []
        for obj in objects:
            exported = exporter.export_normalized_object(
                object_id=obj.id,
                storage_key=obj.storage_key,
                payload=obj.payload,
                metadata=obj.metadata,
                project_id=project_id,
                dataset_id=dataset_id,
                provenance={"phase": "phase2_local_product_loop", "objectType": obj.object_type.value},
            )
            exports.append(
                {
                    "objectId": exported.object_id,
                    "storageKey": exported.storage_key,
                    "metadataKey": exported.metadata_key,
                    "contentHash": exported.content_hash,
                }
            )
        return exports

    def _export_plan_artifact(self, *, plan: AnalysisPlan, project_id: str, dataset_id: str, job_id: str) -> list[Artifact]:
        exporter = LocalArtifactExporter(self.artifact_root)
        return exporter.export_payloads(
            payloads=[
                ArtifactPayload(
                    artifact_type=ArtifactType.analysis_plan_json,
                    file_name="analysis_plan.json",
                    content=plan.model_dump(mode="json"),
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
            params_hash=content_hash(stable_json_dumps({"planner": "phase2_deterministic"})),
            provenance={"runtime": "phase2_product_runtime", "boundary": "structured_json_plan"},
        )

    def _export_recipe_artifact(self, *, plan: AnalysisPlan, project_id: str, dataset_id: str, job_id: str) -> list[Artifact]:
        exporter = LocalArtifactExporter(self.artifact_root)
        recipe = {
            "schemaVersion": "0.1",
            "recipeId": f"recipe_{job_id}",
            "name": "Phase 2 deterministic material analysis",
            "version": "1",
            "projectId": project_id,
            "sourceJobId": job_id,
            "sourcePlanId": "system_plan-analysis_plan_json",
            "inputRequirements": _recipe_input_requirements(plan),
            "steps": [
                {
                    "stepId": step.stepId,
                    "toolId": step.toolId,
                    "toolVersion": self.registry.get_tool_by_id(step.toolId).version,
                    "inputBindings": {f"input_{index}": ref.ref for index, ref in enumerate(step.inputRefs, start=1)},
                    "params": step.params,
                    "artifactTypes": step.output["artifactTypes"],
                }
                for step in plan.steps
            ],
            "environment": {"toolRegistryVersion": self.registry.version, "planner": "phase2_deterministic"},
        }
        recipe_payload = VisualizationRecipe.model_validate(recipe).model_dump(mode="json")
        return exporter.export_payloads(
            payloads=[ArtifactPayload(ArtifactType.recipe_json, "recipe.json", recipe_payload, "application/json")],
            project_id=project_id,
            dataset_id=dataset_id,
            job_id=job_id,
            tool_call_id="system_recipe",
            tool_id="platform.recipe",
            tool_version="0.1.0",
            adapter_version="0.1.0",
            input_hashes=[content_hash(plan.model_dump_json())],
            params_hash=content_hash(stable_json_dumps({"version": "1"})),
            provenance={"runtime": "phase2_product_runtime", "recipeScope": "job"},
        )

    def _export_report_artifacts(
        self,
        *,
        project: ProjectRecord,
        dataset: DatasetRecord,
        plan_summary: dict[str, Any],
        artifacts: list[Artifact],
        job_id: str,
    ) -> list[Artifact]:
        markdown = _report_markdown(project=project, dataset=dataset, plan_summary=plan_summary, artifacts=artifacts)
        html_report = _report_html(markdown)
        exporter = LocalArtifactExporter(self.artifact_root)
        return exporter.export_payloads(
            payloads=[
                ArtifactPayload(ArtifactType.report_md, "report.md", markdown, "text/markdown"),
                ArtifactPayload(ArtifactType.report_html, "report.html", html_report, "text/html"),
            ],
            project_id=project.id,
            dataset_id=dataset.id,
            job_id=job_id,
            tool_call_id="system_report",
            tool_id="platform.report",
            tool_version="0.1.0",
            adapter_version="0.1.0",
            input_hashes=[content_hash(stable_json_dumps(plan_summary)), content_hash(dataset.profile.model_dump_json())],
            params_hash=content_hash(stable_json_dumps({"formats": ["markdown", "html"]})),
            provenance={"runtime": "phase2_product_runtime", "reportFormats": ["markdown", "html"]},
        )

    def _register_artifacts(self, job_id: str, artifacts: list[Artifact], *, event_progress: float) -> None:
        self.artifact_store.register(artifacts)
        for artifact in artifacts:
            self.job_store.append_event(
                job_id,
                event_type="artifact.ready",
                status=JobEventStatus.success,
                message=f"Artifact ready: {artifact.name}",
                payload={"artifactId": artifact.id, "artifactType": artifact.type.value, "storageKey": artifact.storageKey},
                progress=event_progress,
            )

    def _require_project(self, project_id: str) -> ProjectRecord:
        try:
            return self.projects[project_id]
        except KeyError as exc:
            raise LookupError(f"Unknown project_id: {project_id}") from exc

    def _require_dataset(self, dataset_id: str) -> DatasetRecord:
        try:
            return self.datasets[dataset_id]
        except KeyError as exc:
            raise LookupError(f"Unknown dataset_id: {dataset_id}") from exc

    def _require_job(self, job_id: str) -> JobRunRecord:
        try:
            return self.jobs[job_id]
        except KeyError as exc:
            raise LookupError(f"Unknown job_id: {job_id}") from exc


def build_phase2_plan(
    *,
    user_prompt: str,
    data_profile: DataProfile,
    registry: ToolRegistry,
    object_refs: dict[str, str],
) -> AnalysisPlan:
    steps: list[AnalysisStep] = []
    for tool_id in PHASE2_TOOL_ORDER:
        step = _phase2_step(tool_id, data_profile, registry, object_refs)
        if step is not None:
            steps.append(step)
        if len(steps) == 5:
            break

    warnings = [issue["message"] for issue in data_profile.qualityIssues if issue.get("severity") == "warning"]
    if len(steps) < 3:
        warnings.append("Fewer than three MVP tools are available for this dataset profile.")

    return AnalysisPlan(
        goal=user_prompt,
        datasetId=data_profile.datasetId,
        profileId=data_profile.profileId,
        toolRegistryVersion=registry.version,
        assumptions=[
            "Phase 2 uses a deterministic local planner; no real LLM API is called.",
            "All executable steps must pass Tool Registry and adapter validation.",
        ],
        warnings=warnings,
        steps=steps,
        expectedArtifacts=_expected_artifacts_for_steps(steps),
    )


def summarize_plan(plan: AnalysisPlan, registry: ToolRegistry) -> dict[str, Any]:
    return {
        "goal": plan.goal,
        "toolCount": len(plan.steps),
        "steps": [
            {
                "stepId": step.stepId,
                "toolId": step.toolId,
                "purpose": step.purpose,
                "reason": step.reason,
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


def build_object_store(objects: list[NormalizedObjectDraft]) -> tuple[dict[str, Any], dict[str, str]]:
    structures = [obj.payload for obj in objects if obj.object_type == MaterialObjectType.Structure]
    formulas = [
        obj.metadata["formula"]
        for obj in objects
        if obj.object_type in {MaterialObjectType.Structure, MaterialObjectType.Atoms} and "formula" in obj.metadata
    ]
    dataframes = [pd.DataFrame(obj.payload) for obj in objects if obj.object_type == MaterialObjectType.DataFrame]
    for dataframe in dataframes:
        for formula_column in ("formula", "composition"):
            if formula_column in dataframe.columns:
                formulas.extend(str(value) for value in dataframe[formula_column].dropna().tolist())

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


def list_phase2_projects() -> list[dict[str, Any]]:
    return get_phase2_runtime().list_projects()


def create_phase2_project(request: CreateProjectRequest) -> dict[str, Any]:
    return get_phase2_runtime().create_project(request)


def list_phase2_datasets() -> list[dict[str, Any]]:
    return get_phase2_runtime().list_datasets()


def get_phase2_dataset(dataset_id: str) -> dict[str, Any]:
    return _api_call(lambda: get_phase2_runtime().get_dataset(dataset_id))


def create_phase2_demo_dataset() -> dict[str, Any]:
    return _api_call(lambda: get_phase2_runtime().ensure_demo_dataset())


def upload_phase2_dataset(request: DatasetUploadRequest) -> dict[str, Any]:
    return _api_call(lambda: get_phase2_runtime().upload_dataset(request))


def get_phase2_dataset_profile(dataset_id: str) -> dict[str, Any]:
    return _api_call(lambda: get_phase2_runtime().get_dataset_profile(dataset_id))


def get_phase2_dataset_object_store(dataset_id: str) -> dict[str, Any]:
    return get_phase2_runtime().get_dataset_object_store(dataset_id)


def get_phase2_dataset_profile_model(dataset_id: str) -> DataProfile:
    return get_phase2_runtime().get_dataset_profile_model(dataset_id)


def create_phase2_dataset_profile(dataset_id: str) -> dict[str, Any]:
    return _api_call(lambda: get_phase2_runtime().create_dataset_profile(dataset_id))


def create_phase2_job(request: CreateJobRequest) -> dict[str, Any]:
    return _api_call(lambda: get_phase2_runtime().create_job(request))


def get_phase2_job(job_id: str) -> dict[str, Any]:
    return _api_call(lambda: get_phase2_runtime().get_job(job_id))


def get_phase2_job_events(job_id: str, after_seq: int = 0) -> list[dict[str, Any]]:
    return _api_call(lambda: get_phase2_runtime().get_job_events(job_id, after_seq=after_seq))


def stream_phase2_job_events(job_id: str, after_seq: int = 0) -> Any:
    def make_response() -> Any:
        try:
            from fastapi.responses import StreamingResponse

            return StreamingResponse(
                get_phase2_runtime().iter_job_sse_events(job_id, after_seq=after_seq),
                media_type="text/event-stream",
            )
        except ImportError:
            return get_phase2_runtime().get_job_events(job_id, after_seq=after_seq)

    return _api_call(make_response)


def get_phase2_job_tool_calls(job_id: str) -> list[dict[str, Any]]:
    return _api_call(lambda: get_phase2_runtime().get_job_tool_calls(job_id))


def get_phase2_job_artifacts(job_id: str) -> list[dict[str, Any]]:
    return _api_call(lambda: get_phase2_runtime().get_job_artifacts(job_id))


def get_phase2_artifact(artifact_id: str) -> dict[str, Any]:
    return _api_call(lambda: get_phase2_runtime().get_artifact(artifact_id))


def get_phase2_artifact_download(artifact_id: str) -> dict[str, Any]:
    return _api_call(lambda: get_phase2_runtime().get_artifact_download(artifact_id))


def reset_phase2_runtime(artifact_root: str | Path | None = None, registry: ToolRegistry | None = None) -> Phase2ProductRuntime:
    global _PHASE2_RUNTIME
    _PHASE2_RUNTIME = Phase2ProductRuntime(artifact_root or DEFAULT_ARTIFACT_ROOT, registry=registry)
    return _PHASE2_RUNTIME


def get_phase2_runtime() -> Phase2ProductRuntime:
    return _PHASE2_RUNTIME


def _phase2_step(
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
    if tool_id.startswith("table.") and "ml_table" not in object_refs:
        return None
    if tool_id.startswith("viz.") and "ml_table" not in object_refs:
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


def _recipe_input_requirements(plan: AnalysisPlan) -> list[dict[str, Any]]:
    requirements: dict[str, dict[str, Any]] = {}
    for step in plan.steps:
        if step.toolId.startswith("composition."):
            requirements["formulas"] = {"role": "formulas", "objectType": "Composition", "required": True}
        elif step.toolId.startswith("structure."):
            requirements["structures"] = {"role": "structures", "objectType": "Structure", "required": True}
        elif step.toolId.startswith(("ml.", "table.", "viz.")):
            requirements["dataframe"] = {"role": "dataframe", "objectType": "DataFrame", "required": True}
    return list(requirements.values())


def _report_markdown(
    *,
    project: ProjectRecord,
    dataset: DatasetRecord,
    plan_summary: dict[str, Any],
    artifacts: list[Artifact],
) -> str:
    artifact_types = sorted({artifact.type.value for artifact in artifacts})
    lines = [
        "# Phase 2 Material Analysis Report",
        "",
        f"- Project: `{project.name}`",
        f"- Dataset: `{dataset.name}`",
        f"- Data Profile: `{dataset.profile.profileId}`",
        f"- Dataset type: `{dataset.profile.datasetType}`",
        f"- Structures: {(dataset.profile.structureSummary or {}).get('nStructures', 0)}",
        f"- Table rows: {(dataset.profile.tableSummary or {}).get('nRows', 0)}",
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
            f"- Count before report: {len(artifacts)}",
            f"- Types: {', '.join(artifact_types)}",
            "",
            "## Reproducibility",
            "",
            "This report was generated from the deterministic Phase 2 AnalysisPlan. Tool calls were validated by the Tool Registry and executed by adapters.",
        ]
    )
    return "\n".join(lines) + "\n"


def _report_html(markdown: str) -> str:
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<title>Phase 2 Material Analysis Report</title></head>"
        "<body><pre>"
        f"{html.escape(markdown)}"
        "</pre></body></html>"
    )


def _uploaded_file_summary(result: ParseResult) -> dict[str, Any]:
    return {
        "fileId": result.file_id,
        "name": result.file_path.name,
        "detectedFormat": result.detected_format.value,
        "status": result.parse_status,
        "objectCount": len(result.objects),
        "errorCode": result.error_code,
    }


def _artifact_summary(artifact: Artifact) -> dict[str, Any]:
    content_type = artifact.contentType or artifact.metadata.provenance.get("mediaType") or _content_type_for_name(artifact.name)
    return {
        "id": artifact.id,
        "artifactId": artifact.id,
        "type": artifact.type.value,
        "name": artifact.name,
        "downloadUrl": f"/artifacts/{artifact.id}/download",
        "storageKey": artifact.storageKey,
        "storageProvider": artifact.storageProvider or "local",
        "bucket": artifact.bucket,
        "toolCallId": artifact.toolCallId,
        "sizeBytes": artifact.sizeBytes,
        "contentType": content_type,
        "contentHash": artifact.contentHash,
        "sha256": artifact.sha256 or artifact.contentHash,
        "createdAt": artifact.createdAt or artifact.metadata.createdAt,
    }


def _sse_event(event: dict[str, Any]) -> str:
    event_name = str(event["eventType"])
    event_id = str(event["seq"])
    data_event = {
        **event,
        "job_id": event.get("jobId"),
        "event_type": event.get("eventType"),
        "created_at": event.get("createdAt"),
    }
    data = json.dumps(data_event, separators=(",", ":"), sort_keys=True)
    return f"id: {event_id}\nevent: {event_name}\ndata: {data}\n\n"


def _content_type_for_name(name: str) -> str:
    if name.endswith(".json"):
        return "application/json"
    if name.endswith(".html"):
        return "text/html"
    if name.endswith(".md"):
        return "text/markdown"
    if name.endswith(".png"):
        return "image/png"
    if name.endswith(".csv"):
        return "text/csv"
    if name.endswith(".svg"):
        return "image/svg+xml"
    return "application/octet-stream"


def _default_params_for(tool_id: str) -> dict[str, Any]:
    defaults: dict[str, dict[str, Any]] = {
        "composition.ptable_heatmap": {"countMode": "composition", "colorScale": "viridis", "title": "Element coverage"},
        "composition.chem_sys_treemap": {"showCounts": "value", "maxCells": 20, "title": "Chemical systems"},
        "structure.summary": {"maxStructures": 50, "includeSitesPreview": True, "maxPreviewSites": 20},
        "structure.lattice_summary": {"maxStructures": 100, "detectOutliers": True},
        "structure.spacegroup_summary": {"symprec": 0.01, "angleTolerance": 5, "maxStructures": 50},
        "structure.composition_from_structure": {"maxStructures": 100, "includeRecommendedTools": True},
        "structure.preview_metadata": {"maxPreviewSites": 100, "includeCartesian": True, "includeFractional": True},
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
        "ml.basic_metrics": {"targetColumn": "y_true", "predictionColumn": "y_pred"},
        "ml.outlier_table": {"targetColumn": "y_true", "predictionColumn": "y_pred", "topK": 5},
    }
    return defaults.get(tool_id, {})


def _purpose_for(tool_id: str) -> str:
    purposes = {
        "composition.ptable_heatmap": "Inspect element coverage and frequency.",
        "composition.chem_sys_treemap": "Show chemical-system distribution.",
        "structure.summary": "Summarize structure formula, elements, sites, and lattice.",
        "structure.lattice_summary": "Summarize lattice parameters and volumes.",
        "structure.spacegroup_summary": "Detect space group and crystal system distribution.",
        "structure.composition_from_structure": "Extract composition statistics from structures.",
        "structure.preview_metadata": "Generate lightweight structure preview metadata.",
        "structure.viewer_scene_metadata": "Generate static scene metadata for future structure viewer rendering.",
        "structure.viewer_export_package": "Generate a static structure viewer export package without a renderer.",
        "structure.viewer_3d": "Generate canonical artifacts for the minimal interactive crystal structure viewer.",
        "ml.basic_metrics": "Compute regression quality metrics.",
        "ml.outlier_table": "List highest-error rows for review.",
    }
    return purposes[tool_id]


def _input_reason_for(tool_id: str, profile: DataProfile) -> str:
    if tool_id.startswith("composition."):
        elements = ", ".join((profile.structureSummary or {}).get("elements", []))
        return f"Formulas are available from parsed structures and/or table columns; detected elements: {elements}."
    if tool_id.startswith("structure."):
        count = (profile.structureSummary or {}).get("nStructures", 0)
        return f"{count} periodic structure object(s) are available."
    columns = [column["name"] for column in (profile.tableSummary or {}).get("columns", [])]
    return f"Regression table columns are available: {', '.join(columns)}."


def _api_call(fn: Any) -> Any:
    try:
        return fn()
    except LookupError as exc:
        try:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ImportError:
            raise
    except (FileNotFoundError, ValueError) as exc:
        try:
            from fastapi import HTTPException

            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except ImportError:
            raise


def _safe_id(value: str) -> str:
    return value.replace(".", "_").replace("-", "_")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


_PHASE2_RUNTIME = Phase2ProductRuntime()
