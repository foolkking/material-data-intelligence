from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

from mdi_adapters import ToolExecutionContext, execute_tool_request
from mdi_api.artifact_storage import ArtifactStorage, ArtifactStorageMetadata, LocalFileArtifactStorage, create_artifact_storage_from_settings
from mdi_api.config import load_settings
from mdi_api.database import create_repository_factory
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.unit_of_work import RepositoryFactory
from mdi_schemas import (
    AnalysisPlan,
    AnalysisPlanV02,
    ArtifactLineageRecord,
    BindingExecutionState,
    DependencyBindingExecution,
    DependencyExecutionOutcome,
    DependencyExecutionRecord,
    DependencyStepExecution,
    JobStatus,
    ResolvedArtifactInputRef,
    StepExecutionState,
    ToolExecutionRequest,
    dependency_semantic_hash,
    deterministic_dependency_id,
)
from mdi_tool_registry import (
    ToolRegistry,
    build_artifact_port_inventory,
    load_manifests,
    validate_dependency_plan,
)
from mdi_tool_registry.plan_validator import validate_plan

from .object_store import DurableObjectStoreResolver


ToolExecutor = Callable[[ToolExecutionRequest, "QueueWorkerContext"], Any]
ObjectStoreResolver = Callable[[str], Mapping[str, Any] | None]


class DependencyBindingError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


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
    plan_id: str | None = None
    plan_version: str | None = None


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
        if status in {JobStatus.completed.value, JobStatus.partial_success.value}:
            return self._result(repos, job_id, message="job already completed")
        if status == JobStatus.failed.value:
            dependency_execution = repos.dependency_execution.get_execution_for_job(job_id)
            if dependency_execution is not None and dependency_execution.get("outcome") in {
                "ALL_FAILED", "VALIDATION_ABORTED"
            }:
                return self._result(
                    repos,
                    job_id,
                    message="dependency execution already finalized",
                    plan_record=repos.analysis_plans.get_plan_for_job(job_id),
                )

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
            if (plan_payload or {}).get("schemaVersion") == "0.2":
                return self._handle_dependency_plan(
                    repos,
                    job,
                    plan_payload=plan_payload or {},
                    plan_record=plan_record,
                    object_store=effective_object_store,
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

    def _handle_dependency_plan(
        self,
        repos: Any,
        job: Mapping[str, Any],
        *,
        plan_payload: Mapping[str, Any],
        plan_record: Mapping[str, Any] | None,
        object_store: dict[str, Any],
    ) -> QueueWorkerResult:
        job_id = str(job.get("jobId") or job["id"])
        if plan_record is None:
            raise ValueError("AnalysisPlan 0.2 must be loaded from exact persisted plan state.")
        plan = AnalysisPlanV02.model_validate(plan_payload)
        plan_id = str(plan_record.get("planId") or plan_record.get("id"))
        plan_hash = str(plan_record.get("planHash") or plan_record.get("plan_hash"))
        if _runtime_plan_hash(plan) != plan_hash:
            raise ValueError("Persisted AnalysisPlan 0.2 hash verification failed.")
        dependency_validation = validate_dependency_plan(plan, registry=self.registry)
        if not dependency_validation.ok:
            return self._abort_dependency_validation(
                repos, job, plan, plan_record,
                code=dependency_validation.errors[0].code.value,
                message=dependency_validation.errors[0].message,
            )
        ordinary_validation = validate_plan(plan.model_dump(mode="json"), registry=self.registry)
        if not ordinary_validation.ok:
            return self._abort_dependency_validation(
                repos, job, plan, plan_record,
                code=ordinary_validation.errors[0].code,
                message=ordinary_validation.errors[0].message,
            )
        existing_execution = repos.dependency_execution.get_execution_for_job(job_id)
        if existing_execution is not None and existing_execution.get("outcome") in {
            "ALL_SUCCEEDED", "PARTIAL_RESULTS", "ALL_FAILED", "VALIDATION_ABORTED"
        }:
            return self._result(repos, job_id, message="dependency execution already finalized", plan_record=plan_record)

        step_by_id = {item.stepId: item for item in plan.steps}
        bindings_by_consumer: dict[str, list[Any]] = {}
        parents: dict[str, set[str]] = {item.stepId: set() for item in plan.steps}
        for binding in plan.dependencyBindings:
            bindings_by_consumer.setdefault(binding.consumerStepId, []).append(binding)
            parents[binding.consumerStepId].add(binding.producerStepId)
        states: dict[str, DependencyStepExecution] = {
            item.stepId: DependencyStepExecution(stepId=item.stepId, toolId=item.toolId, state=StepExecutionState.pending)
            for item in plan.steps
        }
        binding_states: dict[str, DependencyBindingExecution] = {
            item.bindingId: DependencyBindingExecution(bindingId=item.bindingId, state=BindingExecutionState.pending)
            for item in plan.dependencyBindings
        }
        artifacts_by_step: dict[str, list[dict[str, Any]]] = {}
        resolved_by_consumer: dict[str, list[ResolvedArtifactInputRef]] = {}
        ports = build_artifact_port_inventory(self.registry)

        for index, step_id in enumerate(dependency_validation.topological_order, start=1):
            step = step_by_id[step_id]
            blocked_by = sorted(
                parent for parent in parents[step_id]
                if states[parent].state is not StepExecutionState.succeeded
            )
            if blocked_by:
                states[step_id] = DependencyStepExecution(
                    stepId=step_id,
                    toolId=step.toolId,
                    state=StepExecutionState.blocked_dependency,
                    blockedByStepIds=blocked_by,
                    errorCode="UPSTREAM_STEP_NOT_SUCCEEDED",
                    errorMessage="A required producer did not succeed; the Adapter was not invoked.",
                )
                for binding in bindings_by_consumer.get(step_id, []):
                    producer_state = states[binding.producerStepId].state
                    binding_states[binding.bindingId] = DependencyBindingExecution(
                        bindingId=binding.bindingId,
                        state=(BindingExecutionState.failed_producer if producer_state is StepExecutionState.failed else BindingExecutionState.consumer_not_run),
                        errorCode="UPSTREAM_STEP_NOT_SUCCEEDED",
                    )
                continue

            step_store = dict(object_store)
            step_store["__mdi_artifact_bindings__"] = {}
            step_payload = step.model_dump(mode="json")
            incoming_refs: list[ResolvedArtifactInputRef] = []
            binding_failure: tuple[str, str] | None = None
            for binding in sorted(bindings_by_consumer.get(step_id, []), key=lambda item: item.bindingId):
                try:
                    resolved, materialized = self._resolve_artifact_binding(
                        repos,
                        job=job,
                        plan=plan,
                        plan_id=plan_id,
                        plan_hash=plan_hash,
                        binding=binding,
                        producer_artifacts=artifacts_by_step.get(binding.producerStepId, []),
                        output_port=next(
                            item
                            for item in ports[step_by_id[binding.producerStepId].toolId].outputPorts
                            if item.portId == binding.producerOutputPort
                        ),
                        input_port=next(
                            item for item in ports[step.toolId].inputPorts if item.portId == binding.consumerInputPort
                        ),
                    )
                    step_store[resolved.materializedObjectRef] = materialized
                    step_store["__mdi_artifact_bindings__"][resolved.materializedObjectRef] = resolved.model_dump(mode="json")
                    step_payload["inputRefs"].append(
                        {
                            "refType": "artifact",
                            "ref": resolved.materializedObjectRef,
                            "fieldRole": next(item.inputFieldRole for item in ports[step.toolId].inputPorts if item.portId == binding.consumerInputPort),
                            "objectType": next(item.inputObjectType for item in ports[step.toolId].inputPorts if item.portId == binding.consumerInputPort),
                        }
                    )
                    incoming_refs.append(resolved)
                    binding_states[binding.bindingId] = DependencyBindingExecution(
                        bindingId=binding.bindingId,
                        state=BindingExecutionState.resolved,
                        producerToolCallId=resolved.producerToolCallId,
                        artifactId=resolved.artifactId,
                        artifactChecksum=resolved.checksum,
                    )
                    repos.dependency_execution.save_binding_resolution(
                        {
                            "resolvedArtifactInputRef": resolved.model_dump(mode="json"),
                            "validationOutcome": "RESOLVED",
                        }
                    )
                except Exception as exc:
                    code, state = _binding_error(exc)
                    binding_states[binding.bindingId] = DependencyBindingExecution(
                        bindingId=binding.bindingId,
                        state=state,
                        errorCode=code,
                    )
                    repos.dependency_execution.save_binding_resolution(
                        {
                            "planId": plan_id,
                            "planHash": plan_hash,
                            "jobId": job_id,
                            "bindingId": binding.bindingId,
                            "producerStepId": binding.producerStepId,
                            "consumerStepId": binding.consumerStepId,
                            "consumerInputPort": binding.consumerInputPort,
                            "validationOutcome": state.value,
                            "errorCode": code,
                            "resolvedArtifactInputRef": None,
                        }
                    )
                    binding_failure = (code, str(exc))
                    break
            if binding_failure is not None:
                states[step_id] = DependencyStepExecution(
                    stepId=step_id,
                    toolId=step.toolId,
                    state=StepExecutionState.failed,
                    errorCode=binding_failure[0],
                    errorMessage=binding_failure[1][:1024],
                )
                repos.job_events.append_event(
                    job_id,
                    event_type="dependency.binding_failed",
                    status="error",
                    message=binding_failure[1],
                    payload={"stepId": step_id, "errorCode": binding_failure[0]},
                    progress=1.0,
                )
                continue

            states[step_id] = DependencyStepExecution(stepId=step_id, toolId=step.toolId, state=StepExecutionState.ready)
            try:
                states[step_id] = DependencyStepExecution(stepId=step_id, toolId=step.toolId, state=StepExecutionState.running)
                produced = self._run_step(
                    repos, job, step_payload, index=index, object_store=step_store, plan_record=plan_record
                )
                artifacts_by_step[step_id] = produced
                resolved_by_consumer[step_id] = incoming_refs
                call = _find_tool_call(repos, job_id=job_id, step_id=step_id)
                tool_call_id = str((call or {}).get("id") or "")
                artifact_ids = [str(item["id"]) for item in produced]
                states[step_id] = DependencyStepExecution(
                    stepId=step_id,
                    toolId=step.toolId,
                    state=StepExecutionState.succeeded,
                    toolCallId=tool_call_id,
                    artifactIds=artifact_ids,
                )
                for binding in bindings_by_consumer.get(step_id, []):
                    current = binding_states[binding.bindingId]
                    binding_states[binding.bindingId] = current.model_copy(update={"consumerToolCallId": tool_call_id})
                for artifact in produced:
                    lineage = self._artifact_lineage(
                        repos,
                        job=job,
                        plan=plan,
                        plan_record=plan_record,
                        step=step,
                        artifact=artifact,
                        upstream=incoming_refs,
                        ports=ports,
                    )
                    repos.dependency_execution.save_lineage(lineage.model_dump(mode="json"))
            except Exception as exc:
                states[step_id] = DependencyStepExecution(
                    stepId=step_id,
                    toolId=step.toolId,
                    state=StepExecutionState.failed,
                    toolCallId=str((_find_tool_call(repos, job_id=job_id, step_id=step_id) or {}).get("id") or "") or None,
                    errorCode="ADAPTER_EXECUTION_FAILED",
                    errorMessage=str(exc)[:1024],
                )

        ordered_states = [states[item] for item in dependency_validation.topological_order]
        succeeded = sum(item.state is StepExecutionState.succeeded for item in ordered_states)
        failed = sum(item.state is StepExecutionState.failed for item in ordered_states)
        blocked = sum(item.state is StepExecutionState.blocked_dependency for item in ordered_states)
        not_started = sum(item.state in {StepExecutionState.pending, StepExecutionState.ready, StepExecutionState.running, StepExecutionState.not_started} for item in ordered_states)
        if succeeded == len(ordered_states):
            outcome = DependencyExecutionOutcome.all_succeeded
            job_status = JobStatus.completed
        elif succeeded > 0:
            outcome = DependencyExecutionOutcome.partial_results
            job_status = JobStatus.partial_success
        else:
            outcome = DependencyExecutionOutcome.all_failed
            job_status = JobStatus.failed
        all_artifacts = [artifact_id for item in ordered_states for artifact_id in item.artifactIds]
        record = _dependency_execution_record(
            plan=plan,
            plan_id=plan_id,
            plan_hash=plan_hash,
            job_id=job_id,
            topological_order=dependency_validation.topological_order,
            steps=ordered_states,
            bindings=[binding_states[item.bindingId] for item in plan.dependencyBindings],
            succeeded=succeeded,
            failed=failed,
            blocked=blocked,
            not_started=not_started,
            artifacts=all_artifacts,
            outcome=outcome,
        )
        repos.dependency_execution.save_execution(record.model_dump(mode="json"))
        repos.jobs.set_status(job_id, job_status)
        repos.job_events.append_event(
            job_id,
            event_type="dependency.execution_completed",
            status="success" if outcome is DependencyExecutionOutcome.all_succeeded else "warning",
            message=f"Dependency execution finished with {outcome.value}.",
            payload={"executionId": record.executionId, "outcome": outcome.value, "graphHash": plan.graphHash},
            progress=1.0,
        )
        return self._result(repos, job_id, message=f"dependency execution {outcome.value.lower()}", plan_record=plan_record)

    def _abort_dependency_validation(
        self,
        repos: Any,
        job: Mapping[str, Any],
        plan: AnalysisPlanV02,
        plan_record: Mapping[str, Any],
        *,
        code: str,
        message: str,
    ) -> QueueWorkerResult:
        job_id = str(job.get("jobId") or job["id"])
        plan_id = str(plan_record.get("planId") or plan_record.get("id"))
        plan_hash = str(plan_record.get("planHash") or plan_record.get("plan_hash"))
        steps = [
            DependencyStepExecution(
                stepId=item.stepId,
                toolId=item.toolId,
                state=StepExecutionState.not_started,
                errorCode=code,
                errorMessage=message[:1024],
            )
            for item in plan.steps
        ]
        record = _dependency_execution_record(
            plan=plan, plan_id=plan_id, plan_hash=plan_hash, job_id=job_id,
            topological_order=[item.stepId for item in plan.steps], steps=steps,
            bindings=[DependencyBindingExecution(bindingId=item.bindingId, state=BindingExecutionState.consumer_not_run, errorCode=code) for item in plan.dependencyBindings],
            succeeded=0, failed=0, blocked=0, not_started=len(steps), artifacts=[],
            outcome=DependencyExecutionOutcome.validation_aborted,
        )
        repos.dependency_execution.save_execution(record.model_dump(mode="json"))
        repos.jobs.set_status(job_id, JobStatus.failed)
        repos.job_events.append_event(
            job_id, event_type="dependency.validation_aborted", status="error", message=message,
            payload={"errorCode": code, "executionId": record.executionId}, progress=1.0,
        )
        return self._result(repos, job_id, message=f"dependency validation aborted: {message}", plan_record=plan_record)

    def _resolve_artifact_binding(
        self,
        repos: Any,
        *,
        job: Mapping[str, Any],
        plan: AnalysisPlanV02,
        plan_id: str,
        plan_hash: str,
        binding: Any,
        producer_artifacts: list[dict[str, Any]],
        output_port: Any,
        input_port: Any,
    ) -> tuple[ResolvedArtifactInputRef, Any]:
        job_id = str(job.get("jobId") or job["id"])
        project_id = str(job.get("projectId") or job.get("project_id") or "")
        dataset_id = str(job.get("datasetId") or job.get("dataset_id") or "")
        expected = [item for item in producer_artifacts if str(item.get("type")) == binding.artifactKind.value]
        if len(expected) != 1:
            raise DependencyBindingError("MISSING_ARTIFACT", "Producer did not emit exactly one declared artifact kind.")
        artifact = expected[0]
        if (
            str(artifact.get("jobId")) != job_id
            or str(artifact.get("projectId")) != project_id
            or str(artifact.get("datasetId") or "") != dataset_id
        ):
            raise DependencyBindingError("SCOPE_MISMATCH", "Artifact project/job/dataset scope does not match the current execution.")
        metadata = artifact.get("metadata") or {}
        provenance = metadata.get("provenance") or {}
        if str(provenance.get("planId") or "") != plan_id or str(provenance.get("planHash") or "") != plan_hash:
            raise DependencyBindingError("SCOPE_MISMATCH", "Artifact plan identity does not match the current persisted plan.")
        if (
            str(provenance.get("schemaVersion") or "") != binding.artifactContractVersion
            or binding.artifactContractVersion not in output_port.contractVersions
            or binding.artifactKind != output_port.artifactKind
            or binding.artifactKind not in input_port.acceptedArtifactKinds
        ):
            raise DependencyBindingError("CONTRACT_MISMATCH", "Artifact contract version does not match the declared binding.")
        missing_provenance = [field for field in output_port.requiredProvenanceFields if not provenance.get(field)]
        if missing_provenance:
            raise DependencyBindingError(
                "CONTRACT_MISMATCH",
                f"Artifact provenance is missing required fields: {', '.join(missing_provenance)}.",
            )
        content_type = str(artifact.get("contentType") or "application/octet-stream")
        if content_type != binding.mediaType or content_type not in input_port.mediaTypes:
            raise DependencyBindingError("CONTRACT_MISMATCH", "Artifact media type does not match the consumer port.")
        size = int(artifact.get("sizeBytes") or 0)
        if size <= 0 or size > min(output_port.maxBytes, input_port.maxBytes, 268_435_456):
            raise DependencyBindingError("SIZE_REJECTED", "Artifact size violates the declared consumer cap.")
        storage_key = str(artifact.get("storageKey") or "")
        content = self.artifact_storage.get_bytes(storage_key)
        checksum = hashlib.sha256(content).hexdigest()
        if len(content) != size or checksum != str(artifact.get("sha256") or artifact.get("contentHash") or ""):
            raise DependencyBindingError("CHECKSUM_MISMATCH", "Artifact bytes failed exact size/checksum verification.")
        try:
            materialized = json.loads(content.decode("utf-8"))
        except Exception as exc:
            raise DependencyBindingError("CONTRACT_MISMATCH", "Artifact is not strict inert JSON.") from exc
        internal_ref = f"resolved:{binding.bindingId}"
        resolved = ResolvedArtifactInputRef(
            bindingId=binding.bindingId,
            planId=plan_id,
            planHash=plan_hash,
            jobId=job_id,
            producerStepId=binding.producerStepId,
            producerToolCallId=str(artifact.get("toolCallId") or ""),
            artifactId=str(artifact["id"]),
            artifactKind=binding.artifactKind,
            artifactContractVersion=binding.artifactContractVersion,
            mediaType=binding.mediaType,
            sizeBytes=size,
            checksum=checksum,
            consumerStepId=binding.consumerStepId,
            consumerInputPort=binding.consumerInputPort,
            materializedObjectRef=internal_ref,
        )
        return resolved, materialized

    def _artifact_lineage(
        self,
        repos: Any,
        *,
        job: Mapping[str, Any],
        plan: AnalysisPlanV02,
        plan_record: Mapping[str, Any],
        step: Any,
        artifact: Mapping[str, Any],
        upstream: list[ResolvedArtifactInputRef],
        ports: Mapping[str, Any],
    ) -> ArtifactLineageRecord:
        job_id = str(job.get("jobId") or job["id"])
        plan_id = str(plan_record.get("planId") or plan_record.get("id"))
        plan_hash = str(plan_record.get("planHash") or plan_record.get("plan_hash"))
        capability = repos.capability_planning.get_execution_for_job(job_id)
        decision = repos.capability_planning.get_decision(capability["decisionId"])["capabilityDecision"] if capability else {}
        intent_binding = repos.analysis_intents.get_execution_for_job(job_id)
        intent = repos.analysis_intents.get_intent(intent_binding["intentId"])["analysisIntent"] if intent_binding else {}
        output_port = next(
            (item for item in ports[step.toolId].outputPorts if item.artifactKind.value == str(artifact.get("type"))),
            None,
        )
        metadata = artifact.get("metadata") or {}
        provenance = metadata.get("provenance") or {}
        contract_version = str(provenance.get("schemaVersion") or artifact.get("version") or "1")
        port_id = output_port.portId if output_port is not None else f"result-{artifact.get('type')}"
        draft = {
            "schemaVersion": "1.0",
            "projectId": str(job.get("projectId") or job.get("project_id") or ""),
            "datasetId": job.get("datasetId") or job.get("dataset_id"),
            "datasetVersion": (intent.get("dataScope") or {}).get("datasetVersion"),
            "profileId": plan.profileId,
            "profileSemanticHash": decision.get("profileSemanticHash"),
            "intentId": decision.get("intentId"),
            "intentHash": decision.get("intentHash"),
            "resolutionId": decision.get("resolutionId"),
            "resolutionHash": decision.get("resolutionHash"),
            "decisionId": decision.get("decisionId"),
            "decisionHash": decision.get("decisionHash"),
            "planId": plan_id,
            "planHash": plan_hash,
            "planSchemaVersion": "0.2",
            "graphHash": plan.graphHash,
            "jobId": job_id,
            "producerStepId": step.stepId,
            "producerToolCallId": str(artifact.get("toolCallId") or ""),
            "producerToolId": step.toolId,
            "producerToolVersion": self.registry.get_tool_by_id(step.toolId).version,
            "outputPort": port_id,
            "artifactId": str(artifact["id"]),
            "artifactKind": str(artifact.get("type")),
            "artifactContractVersion": contract_version,
            "mediaType": str(artifact.get("contentType") or "application/octet-stream"),
            "contentHash": str(artifact.get("sha256") or artifact.get("contentHash")),
            "upstreamArtifactIds": sorted(item.artifactId for item in upstream),
            "upstreamArtifactHashes": sorted(item.checksum for item in upstream),
            "bindingIds": sorted(item.bindingId for item in upstream),
            "adapterVersion": (metadata.get("adapterVersion") or provenance.get("adapterVersion")),
            "runtimeVersion": "queue_worker_dependency_1.0",
            "warnings": [],
            "caps": {"steps": 4, "bindings": 6, "depth": 4},
            "createdAt": str(artifact.get("createdAt") or metadata.get("createdAt") or _utc_now()),
        }
        lineage_hash = dependency_semantic_hash(draft, identity_fields=("createdAt",))
        return ArtifactLineageRecord(
            lineageId=deterministic_dependency_id("lineage", lineage_hash),
            lineageHash=lineage_hash,
            **draft,
        )

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
            plan_payload = _parse_plan_payload(plan_record["analysisPlan"])
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
                plan_payload = _parse_plan_payload(explicit_plan)
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
        plan_payload = _parse_plan_payload(plan_record["analysisPlan"])
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
    ) -> list[dict[str, Any]]:
        job_id = str(job.get("jobId") or job["id"])
        project_id = str(job.get("projectId") or job["project_id"])
        dataset_id = job.get("datasetId")
        step_id = str(step.get("stepId") or f"step_{index:02d}")
        tool_id = str(step["toolId"])
        tool_call_id = _safe_id(f"call_{job_id}_{step_id}")
        existing = _find_tool_call(repos, job_id=job_id, step_id=step_id)
        if existing and existing.get("status") == "completed":
            return [
                item for item in repos.artifacts.list_for_job(job_id)
                if str(item.get("toolCallId") or item.get("tool_call_id") or "") == str(existing.get("id"))
            ]

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
                    plan_id=str((plan_record or {}).get("id") or (plan_record or {}).get("planId") or "") or None,
                    plan_version=str(((plan_record or {}).get("analysisPlan") or {}).get("schemaVersion") or "") or None,
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
        persisted_artifacts: list[dict[str, Any]] = []
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
            persisted_artifacts.append(record)
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
        return persisted_artifacts

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
            plan_id=context.plan_id,
            plan_version=context.plan_version,
            artifact_root=self.artifact_root,
            object_store=object_store or {},
            artifact_bindings=(object_store or {}).get("__mdi_artifact_bindings__", {}),
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


def _parse_plan_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    version = str(value.get("schemaVersion") or "0.1")
    parsed = AnalysisPlanV02.model_validate(value) if version == "0.2" else AnalysisPlan.model_validate(value)
    return parsed.model_dump(mode="json")


def _runtime_plan_hash(plan: AnalysisPlan | AnalysisPlanV02 | Mapping[str, Any]) -> str:
    payload = _parse_plan_payload(plan.model_dump(mode="json") if hasattr(plan, "model_dump") else plan)
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _binding_error(exc: Exception) -> tuple[str, BindingExecutionState]:
    code = exc.code if isinstance(exc, DependencyBindingError) else "CONTRACT_MISMATCH"
    state = {
        "MISSING_ARTIFACT": BindingExecutionState.missing_artifact,
        "CONTRACT_MISMATCH": BindingExecutionState.contract_mismatch,
        "SCOPE_MISMATCH": BindingExecutionState.scope_mismatch,
        "CHECKSUM_MISMATCH": BindingExecutionState.checksum_mismatch,
        "SIZE_REJECTED": BindingExecutionState.size_rejected,
    }.get(code, BindingExecutionState.contract_mismatch)
    return code, state


def _dependency_execution_record(
    *,
    plan: AnalysisPlanV02,
    plan_id: str,
    plan_hash: str,
    job_id: str,
    topological_order: list[str],
    steps: list[DependencyStepExecution],
    bindings: list[DependencyBindingExecution],
    succeeded: int,
    failed: int,
    blocked: int,
    not_started: int,
    artifacts: list[str],
    outcome: DependencyExecutionOutcome,
) -> DependencyExecutionRecord:
    now = _utc_now()
    draft = {
        "schemaVersion": "1.0",
        "planId": plan_id,
        "planHash": plan_hash,
        "jobId": job_id,
        "graphHash": plan.graphHash,
        "topologicalOrder": topological_order,
        "steps": [item.model_dump(mode="json") for item in steps],
        "bindings": [item.model_dump(mode="json") for item in bindings],
        "succeededCount": succeeded,
        "failedCount": failed,
        "blockedCount": blocked,
        "notStartedCount": not_started,
        "partialArtifactIds": sorted(set(artifacts)),
        "outcome": outcome.value,
        "runtimeVersion": "queue_worker_dependency_1.0",
        "createdAt": now,
        "updatedAt": now,
    }
    semantic_hash = dependency_semantic_hash(draft, identity_fields=("createdAt", "updatedAt"))
    return DependencyExecutionRecord(
        executionId=deterministic_dependency_id("execution", semantic_hash),
        executionHash=semantic_hash,
        **draft,
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
