from __future__ import annotations

import hashlib
import json
from typing import Any


def capability_registry_fingerprint(registry: Any, tool_registry: Any) -> str:
    rows = []
    for manifest in registry.list_all():
        rows.append({
            "id": manifest.capability_id,
            "version": manifest.version,
            "requirements": sorted(manifest.satisfies_requirements),
            "inputs": [slot.model_dump(mode="json") for slot in manifest.input_slots],
            "outputs": [slot.model_dump(mode="json") for slot in manifest.output_slots],
            "preconditions": [item.model_dump(mode="json") for item in manifest.preconditions],
            "bindings": [item.model_dump(mode="json") for item in manifest.tool_bindings],
        })
    tools = sorted((tool.toolId, tool.version) for tool in tool_registry.tools if any(item[0] == tool.toolId for row in rows for item in [(b["tool_id"], b["version_constraint"]) for b in row["bindings"]]))
    payload = {"capabilities": rows, "tools": tools, "version": "agent2.capability-registry/1.0"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def capability_plan_fingerprint(plan: Any, *, registry_fingerprint: str) -> str:
    payload = {"registry_fingerprint": registry_fingerprint, "plan": plan.model_dump(mode="json")}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
