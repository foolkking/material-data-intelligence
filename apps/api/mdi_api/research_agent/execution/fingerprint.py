from __future__ import annotations

import hashlib
import json
from typing import Any


def execution_source_fingerprint(*, analysis_plan_id: str, job: dict[str, Any], tool_calls: list[dict[str, Any]], artifacts: list[dict[str, Any]], events: list[Any], projector_version: str) -> str:
    def compact(row: Any) -> dict[str, Any]:
        if hasattr(row, "model_dump"):
            row = row.model_dump(mode="json")
        if not isinstance(row, dict):
            row = vars(row)
        return {str(key): row[key] for key in sorted(row) if key in {"id", "seq", "status", "stepId", "step_id", "toolId", "tool_id", "version", "sha256", "contentHash", "content_hash", "toolCallId", "tool_call_id", "type", "eventType", "event_type"}}
    payload = {"analysis_plan_id": analysis_plan_id, "job": compact(job), "tool_calls": sorted((compact(item) for item in tool_calls), key=lambda item: (str(item.get("stepId") or item.get("step_id")), str(item.get("id")))), "artifacts": sorted((compact(item) for item in artifacts), key=lambda item: str(item.get("id"))), "events": sorted((compact(item) for item in events), key=lambda item: int(item.get("seq") or 0)), "projector_version": projector_version}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()
