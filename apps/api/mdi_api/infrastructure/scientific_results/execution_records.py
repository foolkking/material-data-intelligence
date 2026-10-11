"""Bound execution descriptors to the immutable result, not the Job's latest attempt."""

from __future__ import annotations

from typing import Any, Mapping
from uuid import UUID

from sqlalchemy import case, select

from mdi_api.db import artifacts, research_execution_summaries, tool_calls


def _ids(values: Any) -> set[str]:
    return {value for value in values if isinstance(value, str) and value} if isinstance(values, list) else set()


def read_snapshot_execution_records(
    connection: Any, snapshot: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Keep recorded calls and exact outputs, including saved companion files.

    Older snapshots without call inventories can identify their producer calls
    through exact saved artifact references. Missing identity never broadens
    the read to all executions of a Job. Limits apply after source filtering.
    """
    bundle = snapshot.get("bundle_json") or {}
    provenance = bundle.get("provenance") or {}
    job_id, project_id = snapshot.get("job_id"), snapshot.get("project_id")
    if not job_id or not project_id:
        return [], []
    if (provenance.get("job_id") and provenance["job_id"] != job_id) or (
        bundle.get("project_id") and bundle["project_id"] != project_id
    ):
        raise ValueError("result execution scope is inconsistent")

    call_ids = _ids(provenance.get("tool_call_ids"))
    artifact_ids = _ids(provenance.get("artifact_ids"))
    for key in ("result_items", "figures", "tables"):
        for item in bundle.get(key) or []:
            artifact_ids.update(_ids(item.get("artifact_ids")))
    for item in bundle.get("evidence") or []:
        artifact_ids.update(_ids([item.get("artifact_id")]))
    for item in bundle.get("facts") or []:
        artifact_ids.update(_ids([(item.get("source") or {}).get("artifact_id")]))
    primary_ids = set(artifact_ids)
    summary_id = provenance.get("execution_summary_id")
    if summary_id:
        summary = connection.execute(select(research_execution_summaries).where(
            research_execution_summaries.c.id == UUID(str(summary_id)),
        )).mappings().first()
        if summary is not None:
            payload = summary["summary_json"]
            owner_turn = str(snapshot["research_turn_id"])
            if (summary["job_id"] != job_id or str(summary["research_turn_id"]) != owner_turn
                    or payload.get("job_id") != job_id or str(payload.get("research_turn_id")) != owner_turn):
                raise ValueError("result execution summary scope is inconsistent")
            artifact_ids.update(_ids([item.get("artifact_id") for item in payload.get("artifact_refs") or []]))
            for step in payload.get("steps") or []:
                call_ids.update(_ids(step.get("tool_call_ids")))
    if not call_ids and not artifact_ids:
        return [], []

    raw_artifacts = connection.execute(select(artifacts).where(
        artifacts.c.project_id == project_id, artifacts.c.job_id == job_id,
        artifacts.c.id.in_(artifact_ids),
    ).order_by(
        case((artifacts.c.id.in_(primary_ids), 0), else_=1),
        artifacts.c.created_at, artifacts.c.id,
    ).limit(64)).mappings().all()
    # Old snapshots can identify a producer through their exact saved artifact.
    call_ids.update(str(row["tool_call_id"]) for row in raw_artifacts if row.get("tool_call_id"))
    raw_tools = connection.execute(select(tool_calls).where(
        tool_calls.c.job_id == job_id, tool_calls.c.id.in_(call_ids),
    ).order_by(tool_calls.c.created_at, tool_calls.c.id).limit(64)).mappings().all() if call_ids else []
    return [dict(row) for row in raw_artifacts], [dict(row) for row in raw_tools]
