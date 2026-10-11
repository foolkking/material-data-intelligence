"""Read-only source labels from the exact saved Job/AnalysisPlan identity."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from mdi_schemas import AnalysisPlanV03

from mdi_api.application.research.planning.integrity import compute_plan_hash


def verified_multi_source_job_plan(
    job: Mapping[str, Any], record: Mapping[str, Any], available_datasets: set[str],
) -> AnalysisPlanV03 | None:
    try:
        plan = AnalysisPlanV03.model_validate(record.get("analysisPlan"))
        if (
            record.get("projectId") != job.get("projectId")
            or (record.get("planId") or record.get("id")) != job.get("planId")
            or record.get("datasetId") != plan.datasetId
            or record.get("profileId") != plan.profileId
            or plan.datasetId != job.get("datasetId")
            or record.get("planHash") != compute_plan_hash(plan)
            or not {item.datasetId for item in plan.sourceContexts}.issubset(available_datasets)
        ):
            return None
        return plan
    except (TypeError, ValueError):
        return None


def job_source_dataset_summaries(
    job: Mapping[str, Any],
    plan_record: Mapping[str, Any] | None,
    datasets: Sequence[Mapping[str, Any]],
) -> list[dict[str, str]]:
    project_id = job.get("projectId")
    if not project_id:
        return []
    available = {
        str(item.get("datasetId") or item.get("id")): item
        for item in datasets
        if item.get("projectId") == project_id and (item.get("datasetId") or item.get("id"))
    }
    record = plan_record or {}
    payload = record.get("analysisPlan") or record
    if isinstance(payload, Mapping) and payload.get("schemaVersion") == "0.3":
        plan = verified_multi_source_job_plan(job, record, set(available))
        source_ids = [item.datasetId for item in plan.sourceContexts] if plan else []
    else:
        source_ids = [str(job["datasetId"])] if job.get("datasetId") in available else []
    return [
        {"datasetId": dataset_id, "name": str(available[dataset_id].get("name") or "")}
        for dataset_id in source_ids
    ]
