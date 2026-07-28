from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

from mdi_adapters import ToolExecutionContext, execute_tool_request
from mdi_api.artifact_storage import ArtifactStorage, ArtifactStorageMetadata, LocalFileArtifactStorage, create_artifact_storage_from_settings
from mdi_api.config import load_settings
from mdi_api.database import create_repository_factory
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.unit_of_work import RepositoryFactory
from mdi_schemas import AnalysisPlan, JobStatus, ToolExecutionRequest
from mdi_tool_registry import ToolRegistry, load_manifests

from .object_store import DurableObjectStoreResolver


ToolExecutor = Callable[[ToolExecutionRequest, "QueueWorkerContext"], Any]
ObjectStoreResolver = Callable[[str], Mapping[str, Any] | None]


class QueueBackend(Protocol):
    def enqueue_job(self, job_id: str) -> "QueueSubmitResult":
        ...


@dataclass(frozen=True)
class QueueSubmitResult:
    job_id: str
    enqueued: bool
    backend: str
    message: str


@dataclass(frozen=True)
class QueueWorkerContext:
    job_id: str
    project_id: str
    dataset_id: str | None
    tool_call_id: str
    artifact_storage: ArtifactStorage


@dataclass(frozen=True)
class QueueToolExecution:
    artifacts: list[Any]
    cache_hit: bool = False
    cache_key: str | None = None


@dataclass(frozen=True)
class QueueWorkerResult:
    job_id: str
    status: str
    tool_call_count: int
    artifact_count: int
    event_count: int
    message: str
    plan_id: str | None = None
    plan_hash: str | None = None


class InMemoryQueueBackend:
    """Deterministic queue adapter for unit tests and local no-Redis runs."""

    def __init__(self) -> None:
        self._queued: list[str] = []
        self._known: set[str] = set()

    def enqueue_job(self, job_id: str) -> QueueSubmitResult:
        if job_id in self._known:
            return QueueSubmitResult(job_id=job_id, enqueued=False, backend="memory", message="job already queued")
        self._known.add(job_id)
        self._queued.append(job_id)
        return QueueSubmitResult(job_id=job_id, enqueued=True, backend="memory", message="job queued")

    def pop_next(self) -> str | None:
        if not self._queued:
            return None
        return self._queued.pop(0)


class RedisRQQueueBackend:
    """Redis/RQ-backed enqueue adapter.

    The import is lazy so regular unit tests do not require a running Redis
    service or the optional RQ runtime to be imported at module load time.
    """

    def __init__(self, *, redis_url: str, queue_name: str = "mdi-jobs") -> None:
        self.redis_url = redis_url
        self.queue_name = queue_name

    def enqueue_job(self, job_id: str) -> QueueSubmitResult:
        try:
            from redis import Redis
            from rq import Queue
        except ImportError as exc:
            raise RuntimeError("RedisRQQueueBackend requires redis and rq dependencies.") from exc

        connection = Redis.from_url(self.redis_url)
        queue = Queue(self.queue_name, connection=connection)
        if queue.fetch_job(job_id) is not None:
            return QueueSubmitResult(job_id=job_id, enqueued=False, backend="rq", message=f"job already queued on {self.queue_name}")
        queue.enqueue("mdi_workers.queue_runtime.run_queued_job", job_id, job_id=job_id)
        return QueueSubmitResult(job_id=job_id, enqueued=True, backend="rq", message=f"job queued on {self.queue_name}")


class QueueWorkerRuntime:
    """Queue-oriented worker that persists status, events, tool calls, and artifacts."""

    def __init__(
        self,
        *,
        repositories: InMemoryRepositoryBundle | None = None,
        repository_factory: RepositoryFactory | None = None,
        artifact_storage: ArtifactStorage | None = None,
        queue_backend: QueueBackend | None = None,
        tool_executor: ToolExecutor | None = None,
        object_store_resolver: ObjectStoreResolver | None = None,
        registry: ToolRegistry | None = None,
        artifact_root: str | Path = ".artifacts/phase5",
    ) -> None:
        if repositories is None and repository_factory is None:
            repositories = InMemoryRepositoryBundle.create()
        self.repositories = repositories
        self.repository_factory = repository_factory
        self.artifact_storage = artifact_storage or LocalFileArtifactStorage(artifact_root)
        self.artifact_root = Path(artifact_root)
        self.queue_backend = queue_backend or InMemoryQueueBackend()
        self.tool_executor = tool_executor
        self.object_store_resolver = object_store_resolver
        self.registry = registry or load_manifests()

    def submit_job(self, job_id: str) -> QueueSubmitResult:
        repos = self._repositories()
        job = repos.jobs.get(job_id)
        if job.get("status") == JobStatus.created.value:
            repos.jobs.set_status(job_id, JobStatus.queued)
        return self.queue_backend.enqueue_job(job_id)

    def handle_job(self, job_id: str, *, plan: Mapping[str, Any] | None = None, object_store: Mapping[str, Any] | None = None) -> QueueWorkerResult:
        repos = self._repositories()
        job = repos.jobs.get(job_id)
        status = str(job.get("status") or JobStatus.created.value)
        if status == JobStatus.completed.value:
            return self._result(repos, job_id, message="job already completed")

        job = self._start_job(repos, job)
        plan_payload, plan_record = self._load_execution_plan(repos, job, explicit_plan=plan)
        steps = list((plan_payload or {}).get("steps") or [])
        if not steps:
            repos.job_events.append_event(job_id, event_type="job.completed", status="success", message="Job completed with no tool steps.", progress=1.0)
            repos.jobs.set_status(job_id, JobStatus.completed)
            return self._result(repos, job_id, message="job completed", plan_record=plan_record)

        try:
            expected_profile_id = str((plan_payload or {}).get("profileId") or "") or None
            effective_object_store = dict(
                object_store or self._resolve_object_store(repos, job, profile_id=expected_profile_id)
            )
            _validate_profile_binding(
                effective_object_store,
                dataset_id=str(job.get("datasetId") or job.get("dataset_id") or ""),
                profile_id=expected_profile_id,
            )
            for index, step in enumerate(steps, start=1):
                self._run_step(repos, job, step, index=index, object_store=effective_object_store, plan_record=plan_record)
        except Exception as exc:
            repos.job_events.append_event(
                job_id,
                event_type="job.failed",
                status="error",
                message=str(exc),
                payload={"errorType": type(exc).__name__},
                progress=1.0,
            )
            repos.jobs.set_status(job_id, JobStatus.failed)
            return self._result(repos, job_id, message=f"job failed: {exc}", plan_record=plan_record)

        repos.job_events.append_event(
            job_id,
            event_type="job.completed",
            status="success",
            message="Job completed.",
            payload=_plan_provenance(plan_record),
            progress=1.0,
        )
        repos.jobs.set_status(job_id, JobStatus.completed)
        return self._result(repos, job_id, message="job completed", plan_record=plan_record)

    def _repositories(self) -> Any:
        if self.repository_factory is not None:
            return self.repository_factory.create_repositories()
        if self.repositories is None:
            raise RuntimeError("QueueWorkerRuntime is missing repositories.")
        return self.repositories

    def _start_job(self, repos: Any, job: Mapping[str, Any]) -> dict[str, Any]:
        job_id = str(job.get("jobId") or job["id"])
        status = str(job.get("status") or JobStatus.created.value)
        if status == JobStatus.created.value:
            repos.jobs.set_status(job_id, JobStatus.queued)
            status = JobStatus.queued.value
        if status == JobStatus.failed.value:
            repos.jobs.set_status(job_id, JobStatus.queued)
            status = JobStatus.queued.value
        if status == JobStatus.queued.value:
            repos.jobs.set_status(job_id, JobStatus.running)
        repos.job_events.append_event(job_id, event_type="job.running", status="running", message="Queue worker started job.", progress=0.0)
        return repos.jobs.get(job_id)

    def _resolve_object_store(
        self,
        repos: Any,
        job: Mapping[str, Any],
        *,
        profile_id: str | None,
    ) -> Mapping[str, Any]:
        dataset_id = job.get("datasetId") or job.get("dataset_id")
        if not dataset_id or self.object_store_resolver is None:
            return {}
        job_id = str(job.get("jobId") or job["id"])
        exact_resolver = getattr(self.object_store_resolver, "resolve", None)
        resolved = (
            exact_resolver(str(dataset_id), profile_id=profile_id)
            if callable(exact_resolver)
            else self.object_store_resolver(str(dataset_id))
        ) or {}
        if resolved:
            repos.job_events.append_event(
                job_id,
                event_type="data.loaded",
                status="success",
                message="Loaded dataset objects for queued tool execution.",
                payload={"datasetId": str(dataset_id), "objectRefs": sorted(str(key) for key in resolved.keys())},
                progress=0.08,
            )
        return resolved

    def _load_execution_plan(
        self,
        repos: Any,
        job: Mapping[str, Any],
        *,
        explicit_plan: Mapping[str, Any] | None,
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        job_id = str(job.get("jobId") or job["id"])
        plan_id = job.get("planId") or job.get("plan_id")
        if plan_id:
            plan_record = repos.analysis_plans.get_plan(str(plan_id))
            plan_payload = AnalysisPlan.model_validate(plan_record["analysisPlan"]).model_dump(mode="json")
            repos.job_events.append_event(
                job_id,
                event_type="plan.loaded",
                status="success",
                message=f"Loaded persisted AnalysisPlan with {len(plan_payload['steps'])} step(s).",
                payload=_plan_provenance(plan_record),
                progress=0.05,
            )
            return plan_payload, plan_record

        if explicit_plan is not None:
            try:
                plan_payload = AnalysisPlan.model_validate(explicit_plan).model_dump(mode="json")
            except Exception:
                plan_payload = dict(explicit_plan)
            repos.job_events.append_event(
                job_id,
                event_type="plan.loaded",
                status="info",
                message=f"Loaded explicit fallback AnalysisPlan with {len(plan_payload['steps'])} step(s).",
                payload={"planSource": "explicit_fallback", "toolCount": len(plan_payload["steps"])},
                progress=0.05,
            )
            return plan_payload, None

        try:
            plan_record = repos.analysis_plans.get_plan_for_job(job_id)
        except (AttributeError, LookupError):
            return None, None
        plan_payload = AnalysisPlan.model_validate(plan_record["analysisPlan"]).model_dump(mode="json")
        repos.job_events.append_event(
            job_id,
            event_type="plan.loaded",
            status="success",
            message=f"Loaded persisted AnalysisPlan with {len(plan_payload['steps'])} step(s).",
            payload=_plan_provenance(plan_record),
            progress=0.05,
        )
        return plan_payload, plan_record

    def _run_step(
        self,
        repos: Any,
        job: Mapping[str, Any],
        step: Mapping[str, Any],
        *,
        index: int,
        object_store: Mapping[str, Any] | None,
        plan_record: Mapping[str, Any] | None,
    ) -> None:
        job_id = str(job.get("jobId") or job["id"])
        project_id = str(job.get("projectId") or job["project_id"])
        dataset_id = job.get("datasetId")
        step_id = str(step.get("stepId") or f"step_{index:02d}")
        tool_id = str(step["toolId"])
        tool_call_id = _safe_id(f"call_{job_id}_{step_id}")
        existing = _find_tool_call(repos, job_id=job_id, step_id=step_id)
        if existing and existing.get("status") == "completed":
            return

        request = ToolExecutionRequest(
            jobId=job_id,
            stepId=step_id,
            toolId=tool_id,
            inputRefs=list(step.get("inputRefs") or []),
            params=dict(step.get("params") or {}),
            artifactTypes=list((step.get("output") or {}).get("artifactTypes") or step.get("artifactTypes") or []),
        )
        if existing is None:
            repos.tool_calls.save(
                {
                    "id": tool_call_id,
                    "jobId": job_id,
                    "stepId": step_id,
                    "toolId": tool_id,
                    "status": "planned",
                    "idempotencyKey": f"{job_id}:{step_id}",
                    "params": request.params,
                }
            )
        repos.tool_calls.save(
            {
                "id": tool_call_id,
                "jobId": job_id,
                "stepId": step_id,
                "toolId": tool_id,
                "status": "running",
                "idempotencyKey": f"{job_id}:{step_id}",
                "params": request.params,
            }
        )
        repos.job_events.append_event(
            job_id,
            event_type="tool.started",
            status="running",
            message=f"Started tool {tool_id}.",
            payload={"toolCallId": tool_call_id, "toolId": tool_id, "stepId": step_id, **_plan_provenance(plan_record)},
            progress=0.0,
        )

        try:
            execution = self._execute_tool(
                request,
                QueueWorkerContext(
                    job_id=job_id,
                    project_id=project_id,
                    dataset_id=str(dataset_id) if dataset_id else None,
                    tool_call_id=tool_call_id,
                    artifact_storage=self.artifact_storage,
                ),
                object_store=object_store,
            )
        except Exception as exc:
            repos.tool_calls.save(
                {
                    "id": tool_call_id,
                    "jobId": job_id,
                    "stepId": step_id,
                    "toolId": tool_id,
                    "status": "failed",
                    "idempotencyKey": f"{job_id}:{step_id}",
                    "params": request.params,
                    "error": {"message": str(exc), "type": type(exc).__name__},
                }
            )
            repos.job_events.append_event(
                job_id,
                event_type="tool.failed",
                status="error",
                message=str(exc),
                payload={"toolCallId": tool_call_id, "toolId": tool_id, "stepId": step_id},
                progress=1.0,
            )
            raise

        artifact_ids: list[str] = []
        for artifact in _execution_artifacts(execution):
            record = self._persist_artifact_metadata(
                artifact,
                project_id=project_id,
                dataset_id=str(dataset_id) if dataset_id else None,
                job_id=job_id,
                tool_call_id=tool_call_id,
                tool_id=tool_id,
                plan_record=plan_record,
            )
            repos.artifacts.save(record)
            artifact_ids.append(str(record["id"]))
            repos.job_events.append_event(
                job_id,
                event_type="artifact.ready",
                status="success",
                message=f"Artifact ready: {record['name']}",
                payload={"toolCallId": tool_call_id, "artifactId": record["id"], "storageKey": record["storageKey"], **_plan_provenance(plan_record)},
            )

        repos.tool_calls.save(
            {
                "id": tool_call_id,
                "jobId": job_id,
                "stepId": step_id,
                "toolId": tool_id,
                "status": "completed",
                "idempotencyKey": f"{job_id}:{step_id}",
                "params": request.params,
                "artifactIds": artifact_ids,
            }
        )
        repos.job_events.append_event(
            job_id,
            event_type="tool.completed",
            status="success",
            message=f"Completed tool {tool_id}.",
            payload={"toolCallId": tool_call_id, "artifactIds": artifact_ids, **_plan_provenance(plan_record)},
            progress=1.0,
        )

    def _execute_tool(self, request: ToolExecutionRequest, context: QueueWorkerContext, *, object_store: Mapping[str, Any] | None) -> Any:
        if self.tool_executor is not None:
            return self.tool_executor(request, context)
        tool = self.registry.get_tool_by_id(request.toolId)
        adapter_context = ToolExecutionContext(
            job_id=context.job_id,
            project_id=context.project_id,
            dataset_id=context.dataset_id or "",
            tool_id=tool.toolId,
            tool_version=tool.version,
            adapter_version="0.1.0",
            registry_version=self.registry.version,
            tool_call_id=context.tool_call_id,
            artifact_root=self.artifact_root,
            object_store=object_store or {},
            resource_limits=tool.resourceLimits,
        )
        return execute_tool_request(adapter_context, request, registry=self.registry)

    def _persist_artifact_metadata(
        self,
        artifact: Any,
        *,
        project_id: str,
        dataset_id: str | None,
        job_id: str,
        tool_call_id: str,
        tool_id: str,
        plan_record: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        record = _artifact_record(artifact)
        artifact_id = str(record.get("id") or record.get("artifactId") or _safe_id(f"artifact_{tool_call_id}_{record.get('name') or 'output'}"))
        content = record.get("content")
        content_type = str(record.get("contentType") or record.get("content_type") or "application/json")
        storage_key = str(record.get("storageKey") or f"projects/{project_id}/jobs/{job_id}/tool_calls/{tool_call_id}/{artifact_id}.json")
        if content is not None:
            encoded = _encode_content(content)
            metadata = self.artifact_storage.put_bytes(storage_key, encoded, content_type=content_type, preview_key=record.get("previewKey"))
        elif (self.artifact_root / storage_key).exists():
            metadata = self.artifact_storage.put_bytes(
                storage_key,
                (self.artifact_root / storage_key).read_bytes(),
                content_type=content_type,
                preview_key=record.get("previewKey"),
            )
        else:
            metadata = _metadata_from_record(record, storage_key=storage_key, content_type=content_type)
        artifact_metadata = dict(record.get("metadata") or {})
        adapter_provenance = artifact_metadata.get("provenance")
        if not isinstance(adapter_provenance, Mapping):
            adapter_provenance = {}
        return {
            "id": artifact_id,
            "projectId": project_id,
            "datasetId": dataset_id,
            "jobId": job_id,
            "toolCallId": tool_call_id,
            "type": str(record.get("type") or "metrics_json"),
            "name": str(record.get("name") or f"{artifact_id}.json"),
            "version": str(record.get("version") or "1"),
            "storageKey": metadata.storage_key,
            "storageProvider": metadata.storage_provider,
            "bucket": metadata.bucket,
            "previewKey": metadata.preview_key,
            "sizeBytes": metadata.size_bytes,
            "contentType": metadata.content_type,
            "contentHash": str(record.get("contentHash") or metadata.sha256),
            "sha256": metadata.sha256,
            "metadata": {
                **artifact_metadata,
                "storageProvider": metadata.storage_provider,
                "bucket": metadata.bucket,
                "createdAt": metadata.created_at,
                "provenance": {
                    **dict(adapter_provenance),
                    "toolId": tool_id,
                    "toolCallId": tool_call_id,
                    **_plan_provenance(plan_record),
                },
            },
        }

    def _result(self, repos: Any, job_id: str, *, message: str, plan_record: Mapping[str, Any] | None = None) -> QueueWorkerResult:
        job = repos.jobs.get(job_id)
        return QueueWorkerResult(
            job_id=job_id,
            status=str(job.get("status")),
            tool_call_count=len(repos.tool_calls.list_for_job(job_id)),
            artifact_count=len(repos.artifacts.list_for_job(job_id)),
            event_count=len(repos.job_events.list_for_job(job_id)),
            message=message,
            plan_id=str(plan_record.get("id") or plan_record.get("planId")) if plan_record else None,
            plan_hash=str(plan_record.get("planHash") or plan_record.get("plan_hash")) if plan_record else None,
        )


def _validate_profile_binding(
    object_store: Mapping[str, Any],
    *,
    dataset_id: str,
    profile_id: str | None,
) -> None:
    profile = object_store.get("profile")
    if profile is None:
        return
    actual_dataset_id = (
        profile.get("datasetId") if isinstance(profile, Mapping) else getattr(profile, "datasetId", None)
    )
    actual_profile_id = (
        profile.get("profileId") if isinstance(profile, Mapping) else getattr(profile, "profileId", None)
    )
    if str(actual_dataset_id or "") != dataset_id or (
        profile_id is not None and str(actual_profile_id or "") != profile_id
    ):
        raise ValueError("Resolved DataProfile does not match the persisted AnalysisPlan binding.")


def create_queue_worker_runtime_from_settings() -> QueueWorkerRuntime:
    settings = load_settings()
    repository_factory = create_repository_factory(settings)
    artifact_storage = create_artifact_storage_from_settings(settings)
    resolver = DurableObjectStoreResolver(
        repository_factory=repository_factory,
        artifact_storage=artifact_storage,
    )
    return QueueWorkerRuntime(
        repository_factory=repository_factory,
        artifact_storage=artifact_storage,
        object_store_resolver=resolver,
        artifact_root=getattr(settings, "artifact_root", ".artifacts/phase2"),
    )


def run_queued_job(job_id: str) -> QueueWorkerResult:
    return create_queue_worker_runtime_from_settings().handle_job(job_id)


def _find_tool_call(repos: Any, *, job_id: str, step_id: str) -> dict[str, Any] | None:
    for tool_call in repos.tool_calls.list_for_job(job_id):
        if tool_call.get("stepId") == step_id:
            return tool_call
    return None


def _execution_artifacts(execution: Any) -> list[Any]:
    if isinstance(execution, QueueToolExecution):
        return execution.artifacts
    if isinstance(execution, Mapping):
        return list(execution.get("artifacts") or [])
    return list(getattr(execution, "artifacts", []) or [])


def _artifact_record(artifact: Any) -> dict[str, Any]:
    if hasattr(artifact, "model_dump"):
        return artifact.model_dump(mode="json")
    return dict(artifact)


def _plan_provenance(plan_record: Mapping[str, Any] | None) -> dict[str, Any]:
    if not plan_record:
        return {}
    return {
        "planId": plan_record.get("id") or plan_record.get("planId"),
        "planHash": plan_record.get("planHash") or plan_record.get("plan_hash"),
        "planSource": plan_record.get("planSource") or plan_record.get("plan_source"),
    }


def _metadata_from_record(record: Mapping[str, Any], *, storage_key: str, content_type: str) -> ArtifactStorageMetadata:
    content_hash = str(record.get("sha256") or record.get("contentHash") or _sha256(_encode_content(record)))
    return ArtifactStorageMetadata(
        storage_key=storage_key,
        content_type=content_type,
        sha256=content_hash,
        size_bytes=int(record.get("sizeBytes") or 0),
        preview_key=record.get("previewKey"),
        storage_provider=str(record.get("storageProvider") or "local"),
        bucket=record.get("bucket"),
    )


def _encode_content(content: Any) -> bytes:
    if isinstance(content, bytes):
        return content
    if isinstance(content, str):
        return content.encode("utf-8")
    return json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _safe_id(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in value)
