from __future__ import annotations

from collections import Counter
from typing import Any, Mapping


PROJECT_HISTORY_SCHEMA_VERSION = "ProjectHistoryView/1.0"


class ProjectHistoryService:
    """Build a bounded user-facing audit view from persisted product records."""

    def __init__(self, repositories: Any, *, archived_run_ids: set[str] | None = None) -> None:
        self.repositories = repositories
        self.archived_run_ids = set(archived_run_ids or ())

    def build(self, project_id: str) -> dict[str, Any]:
        project = _record(self.repositories.projects.get(project_id))
        datasets = _records(self.repositories.datasets.list_for_project(project_id))
        profiles = _records(self.repositories.data_profiles.list_by_project(project_id))
        jobs = _records(self.repositories.jobs.list_by_project(project_id))
        workspaces = _project_records(self.repositories.workspaces, project_id)
        artifacts = _project_records(self.repositories.artifacts, project_id, jobs)
        reports = _project_records(self.repositories.reports, project_id, jobs)
        recipes = _project_records(self.repositories.recipes, project_id, jobs)
        interpretations = _project_records(self.repositories.interpretations, project_id, jobs)

        profile_by_dataset = _latest_by(profiles, "datasetId")
        workspace_by_job = {
            str(item.get("sourceJobId")): item
            for item in workspaces
            if item.get("sourceJobId")
        }
        artifacts_by_job = _group_by(artifacts, "jobId")
        reports_by_job = _group_by(reports, "jobId", "sourceJobId")
        recipes_by_job = _group_by(recipes, "sourceJobId", "jobId")
        interpretations_by_job = _group_by(interpretations, "jobId")

        dataset_views = [
            self._dataset_view(
                dataset,
                profile_by_dataset.get(str(dataset.get("datasetId") or dataset.get("id"))),
                jobs,
                artifacts,
                workspaces,
                interpretations,
                reports,
                recipes,
            )
            for dataset in datasets
        ]
        analysis_views = [
            self._analysis_view(
                job,
                workspace_by_job.get(str(job.get("jobId") or job.get("id"))),
                artifacts_by_job,
                interpretations_by_job,
                reports_by_job,
                recipes_by_job,
            )
            for job in jobs
        ]
        dataset_views.sort(key=_updated_at, reverse=True)
        analysis_views.sort(key=_updated_at, reverse=True)
        activity = self._activity(project_id, dataset_views, analysis_views)
        activity_times = [str(item["occurredAt"]) for item in activity if item.get("occurredAt")]

        return {
            "schemaVersion": PROJECT_HISTORY_SCHEMA_VERSION,
            "project": {
                "projectId": str(project.get("projectId") or project.get("id") or project_id),
                "name": str(project.get("name") or project_id),
                "description": project.get("description"),
                "role": "owner",
                "status": str(project.get("status") or "active"),
                "createdAt": project.get("createdAt"),
                "updatedAt": project.get("updatedAt") or project.get("createdAt"),
            },
            "summary": {
                "datasetCount": len(datasets),
                "analysisCount": len(jobs),
                "completedAnalysisCount": sum(
                    1 for item in jobs if str(item.get("status", "")).lower() == "succeeded"
                ),
                "artifactCount": len(artifacts),
                "workspaceCount": len(workspaces),
                "reportCount": len(reports),
                "lastActivityAt": max(activity_times) if activity_times else project.get("updatedAt") or project.get("createdAt"),
            },
            "datasets": dataset_views,
            "analyses": analysis_views,
            "activity": activity[:100],
        }

    def _dataset_view(
        self,
        dataset: Mapping[str, Any],
        profile: Mapping[str, Any] | None,
        jobs: list[dict[str, Any]],
        artifacts: list[dict[str, Any]],
        workspaces: list[dict[str, Any]],
        interpretations: list[dict[str, Any]],
        reports: list[dict[str, Any]],
        recipes: list[dict[str, Any]],
    ) -> dict[str, Any]:
        dataset_id = str(dataset.get("datasetId") or dataset.get("id") or "")
        metadata = _record(dataset.get("metadata") or {})
        files = metadata.get("files") or []
        exports = metadata.get("normalizedExports") or []
        dataset_jobs = [item for item in jobs if str(item.get("datasetId") or "") == dataset_id]
        latest_job = max(dataset_jobs, key=_updated_at, default=None)
        job_ids = {str(item.get("jobId") or item.get("id") or "") for item in dataset_jobs}
        dataset_artifacts = _related_records(artifacts, dataset_id, job_ids)
        dataset_workspaces = _related_records(workspaces, dataset_id, job_ids)
        dataset_interpretations = _related_records(interpretations, dataset_id, job_ids)
        dataset_reports = _related_records(reports, dataset_id, job_ids)
        dataset_recipes = _related_records(recipes, dataset_id, job_ids)
        parse_outcome = _parse_outcome(files)
        analysis_status = _aggregate_status(dataset_jobs)
        result_status = "ready" if dataset_artifacts or dataset_workspaces or dataset_reports else ("pending" if dataset_jobs else "not_started")
        return {
            "datasetId": dataset_id,
            "name": str(dataset.get("name") or dataset_id),
            "status": str(dataset.get("status") or "created"),
            "createdAt": dataset.get("createdAt") or metadata.get("createdAt"),
            "updatedAt": dataset.get("updatedAt") or dataset.get("createdAt") or metadata.get("createdAt"),
            "import": {
                "fileCount": len(files),
                "files": [_file_view(item) for item in files if isinstance(item, Mapping)],
                "resources": [_resource_view(item) for item in exports if isinstance(item, Mapping)],
                "parseOutcome": parse_outcome,
            },
            "profile": _profile_view(profile),
            "analysisCount": len(dataset_jobs),
            "lastAnalysisStatus": latest_job.get("status") if latest_job else None,
            "process": [
                {"key": "import", "label": "导入", "status": parse_outcome, "detail": f"{len(files)} 个源文件"},
                {"key": "profile", "label": "Profile", "status": "ready" if profile else "pending", "detail": _profile_detail(profile)},
                {"key": "analysis", "label": "分析", "status": analysis_status, "detail": f"{len(dataset_jobs)} 次分析"},
                {"key": "results", "label": "结果", "status": result_status, "detail": f"{len(dataset_artifacts)} 个结果，{len(dataset_reports)} 份报告"},
            ],
            "resultSummary": {
                "artifactCount": len(dataset_artifacts),
                "workspaceCount": len(dataset_workspaces),
                "interpretationCount": len(dataset_interpretations),
                "reportCount": len(dataset_reports),
                "recipeCount": len(dataset_recipes),
                "artifactTypes": sorted({str(item.get("type")) for item in dataset_artifacts if item.get("type")}),
                "latestReportStatus": _latest_status(dataset_reports),
            },
        }

    def _analysis_view(
        self,
        job: Mapping[str, Any],
        workspace: Mapping[str, Any] | None,
        artifacts_by_job: Mapping[str, list[dict[str, Any]]],
        interpretations_by_job: Mapping[str, list[dict[str, Any]]],
        reports_by_job: Mapping[str, list[dict[str, Any]]],
        recipes_by_job: Mapping[str, list[dict[str, Any]]],
    ) -> dict[str, Any]:
        job_id = str(job.get("jobId") or job.get("id") or "")
        calls = _records(self.repositories.tool_calls.list_for_job(job_id))
        question = job.get("userPrompt") or job.get("prompt")
        execution = self.repositories.analysis_intents.get_execution_for_job(job_id)
        if isinstance(execution, Mapping):
            intent_id = execution.get("intentId") or execution.get("intent_id")
            if intent_id:
                try:
                    intent_record = _record(self.repositories.analysis_intents.get_intent(str(intent_id)))
                    intent = _record(intent_record.get("analysisIntent") or intent_record)
                    question = intent.get("rawUserRequest") or intent.get("userRequest") or question
                except LookupError:
                    pass
        plan: dict[str, Any] | None = None
        try:
            plan = _record(self.repositories.analysis_plans.get_plan_for_job(job_id))
        except LookupError:
            pass
        artifacts = artifacts_by_job.get(job_id, [])
        return {
            "jobId": job_id,
            "datasetId": job.get("datasetId"),
            "status": str(job.get("status") or "created"),
            "createdAt": job.get("createdAt"),
            "updatedAt": job.get("updatedAt") or job.get("createdAt"),
            "userQuestion": question,
            "toolIds": [str(item.get("toolId")) for item in calls if item.get("toolId")],
            "stepCount": len((plan or {}).get("steps") or calls),
            "artifactCount": len(artifacts),
            "artifactTypes": sorted({str(item.get("type")) for item in artifacts if item.get("type")}),
            "interpretationCount": len(interpretations_by_job.get(job_id, [])),
            "reportCount": len(reports_by_job.get(job_id, [])),
            "recipeCount": len(recipes_by_job.get(job_id, [])),
            "workspaceId": workspace.get("workspaceId") if workspace else None,
            "workspaceTitle": workspace.get("title") if workspace else None,
            # Archival is a reversible product-visibility projection. The Job
            # terminal status and every scientific child record remain intact.
            "archived": job_id in self.archived_run_ids,
            "visibleInReports": job_id not in self.archived_run_ids,
        }

    @staticmethod
    def _activity(
        project_id: str,
        datasets: list[dict[str, Any]],
        analyses: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for dataset in datasets:
            dataset_id = str(dataset["datasetId"])
            file_count = int((dataset.get("import") or {}).get("fileCount") or 0)
            items.append({
                "activityId": f"dataset:{dataset_id}",
                "kind": "dataset_import",
                "title": f"导入 {dataset.get('name')}",
                "detail": f"{file_count} 个源文件 · DataProfile {'已就绪' if dataset.get('profile') else '待生成'}",
                "status": dataset.get("status"),
                "occurredAt": dataset.get("createdAt"),
                "datasetId": dataset_id,
                "href": f"/projects/{project_id}/datasets/{dataset_id}",
            })
        for analysis in analyses:
            workspace_id = analysis.get("workspaceId")
            job_id = str(analysis["jobId"])
            items.append({
                "activityId": f"analysis:{job_id}",
                "kind": "analysis",
                "title": str(analysis.get("userQuestion") or "分析运行"),
                "detail": f"{analysis.get('artifactCount', 0)} 个结果 · {analysis.get('reportCount', 0)} 份报告",
                "status": analysis.get("status"),
                "archived": bool(analysis.get("archived")),
                "occurredAt": analysis.get("updatedAt") or analysis.get("createdAt"),
                "datasetId": analysis.get("datasetId"),
                "jobId": job_id,
                "workspaceId": workspace_id,
                "href": f"/workspaces/{workspace_id}" if workspace_id else f"/analysis?jobId={job_id}",
            })
        items.sort(key=lambda item: str(item.get("occurredAt") or ""), reverse=True)
        return items


def _file_view(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "fileId": item.get("fileId"),
        "name": item.get("name") or item.get("fileName"),
        "format": item.get("detectedFormat"),
        "status": item.get("status"),
        "byteSize": item.get("byteSize"),
        "objectCount": item.get("objectCount"),
        "errorCode": item.get("errorCode"),
        "importKind": item.get("importKind"),
        "companionGroupId": item.get("companionGroupId"),
    }


def _resource_view(item: Mapping[str, Any]) -> dict[str, Any]:
    metadata = item.get("metadata") if isinstance(item.get("metadata"), Mapping) else {}
    return {"objectId": item.get("objectId"), "objectType": metadata.get("objectType")}


def _profile_view(profile: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if profile is None:
        return None
    value = _record(profile)
    table = _record(value.get("tableSummary") or {})
    ready: list[str] = []
    blocked: list[str] = []
    for item in value.get("readiness") or []:
        if not isinstance(item, Mapping):
            continue
        capability = item.get("capability") or item.get("capabilityId")
        if not capability:
            continue
        (ready if str(item.get("status") or "").upper() == "READY" else blocked).append(str(capability))
    roles = Counter(
        str(item.get("semanticRole") or item.get("semanticType"))
        for item in table.get("columns") or []
        if isinstance(item, Mapping) and (item.get("semanticRole") or item.get("semanticType"))
    )
    return {
        "profileId": value.get("profileId") or value.get("id"),
        "version": value.get("version") or value.get("profileVersion"),
        "profileContractVersion": value.get("schemaVersion") or value.get("profileContractVersion"),
        "datasetType": value.get("datasetType"),
        "createdAt": value.get("createdAt"),
        "rowCount": table.get("rowCount") or table.get("nRows"),
        "columnCount": len(table.get("columns") or []),
        "objectCount": value.get("objectCount") or len(value.get("objects") or []),
        "semanticRoles": dict(roles),
        "readyCapabilities": ready,
        "blockedCapabilities": blocked,
        "warnings": value.get("warnings") or [],
    }


def _parse_outcome(files: Any) -> str:
    statuses = [str(item.get("status") or "").lower() for item in files if isinstance(item, Mapping)]
    if not statuses:
        return "unknown"
    successful = {"success", "succeeded", "parsed"}
    failed = {"failed", "error"}
    if all(item in successful for item in statuses):
        return "succeeded"
    if any(item in failed for item in statuses):
        return "partial" if any(item in successful for item in statuses) else "failed"
    return "processing"


def _profile_detail(profile: Mapping[str, Any] | None) -> str:
    if not profile:
        return "等待生成"
    view = _profile_view(profile) or {}
    rows = view.get("rowCount")
    columns = view.get("columnCount")
    if rows is not None and columns is not None:
        return f"{rows} 行 · {columns} 列"
    return "已生成"


def _aggregate_status(records: list[dict[str, Any]]) -> str:
    if not records:
        return "not_started"
    statuses = {str(item.get("status") or "").lower() for item in records}
    if statuses and statuses.issubset({"succeeded", "completed", "success"}):
        return "succeeded"
    if "failed" in statuses or "error" in statuses:
        return "partial" if statuses - {"failed", "error"} else "failed"
    return "processing"


def _latest_status(records: list[dict[str, Any]]) -> str | None:
    latest = max(records, key=_updated_at, default=None)
    return str(latest.get("status")) if latest and latest.get("status") else None


def _related_records(
    records: list[dict[str, Any]],
    dataset_id: str,
    job_ids: set[str],
) -> list[dict[str, Any]]:
    return [
        item for item in records
        if str(item.get("datasetId") or "") == dataset_id
        or str(item.get("jobId") or item.get("sourceJobId") or "") in job_ids
    ]


def _project_records(repo: Any, project_id: str, jobs: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    method = getattr(repo, "list_by_project", None)
    if callable(method):
        return _records(method(project_id))
    if jobs is None:
        return []
    records: list[dict[str, Any]] = []
    for job in jobs:
        job_id = str(job.get("jobId") or job.get("id") or "")
        if job_id:
            records.extend(_records(repo.list_for_job(job_id)))
    return records


def _latest_by(records: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for item in records:
        key = str(item.get(field) or "")
        if key and (key not in grouped or _updated_at(item) >= _updated_at(grouped[key])):
            grouped[key] = item
    return grouped


def _group_by(records: list[dict[str, Any]], *fields: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in records:
        key = next((str(item.get(field)) for field in fields if item.get(field)), "")
        if key:
            grouped.setdefault(key, []).append(item)
    return grouped


def _updated_at(item: Mapping[str, Any]) -> str:
    return str(item.get("updatedAt") or item.get("createdAt") or "")


def _record(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "model_dump"):
        return dict(value.model_dump(mode="json"))
    return dict(value)


def _records(values: Any) -> list[dict[str, Any]]:
    return [_record(item) for item in (values or [])]
