"""Planner prompt template for LLM JSON Planner.

The prompt instructs the LLM to produce ONLY a structured JSON AnalysisPlan
with no markdown, no explanatory text, and no chain-of-thought output.

The prompt alone does NOT guarantee valid output — PlanValidator is the
mandatory second line of defense.
"""

from __future__ import annotations

from mdi_schemas import DataProfile, RegisteredTool


def _tool_summary(tools: list[RegisteredTool]) -> str:
    lines: list[str] = []
    for tool in tools:
        if tool.toolId.startswith("$"):
            continue
        lines.append(f"- {tool.toolId}: {tool.description}")
        if tool.artifactTypes:
            lines.append(f"  artifactTypes: {[a.value for a in tool.artifactTypes]}")
    return "\n".join(lines)


def _profile_summary(profile: DataProfile) -> str:
    parts: list[str] = [f"datasetId: {profile.datasetId}", f"profileId: {profile.profileId}"]
    if profile.structureSummary:
        s = profile.structureSummary
        parts.append(f"nStructures: {s.get('nStructures', '?')}")
        parts.append(f"elements: {s.get('elements', [])[:20]}")
    if profile.tableSummary:
        t = profile.tableSummary
        cols = [c.get("name", "?") for c in t.get("columns", [])]
        parts.append(f"columns: {cols}")
        if cols:
            parts.append('table inputRef: {"refType":"normalized_object","ref":"ml_table","objectType":"DataFrame"}')
    if profile.structureSummary:
        parts.append('structure inputRef: {"refType":"normalized_object","ref":"structures","objectType":"Structure"}')
    if profile.structureSummary or profile.tableSummary:
        parts.append('composition/formula inputRef: {"refType":"normalized_object","ref":"formulas","objectType":"Composition"}')
    if profile.qualityIssues:
        parts.append(f"qualityIssues: {len(profile.qualityIssues)} issue(s)")
    return "\n".join(parts)


_SYSTEM_PROMPT = """You are a material data analysis planner.

Your ONLY task is to produce a JSON object that matches this schema:

{
  "schemaVersion": "0.1",
  "goal": "<string>",
  "datasetId": "<string>",
  "profileId": "<string>",
  "toolRegistryVersion": "<string>",
  "assumptions": ["<string>"],
  "warnings": ["<string>"],
  "steps": [
    {
      "stepId": "<unique string>",
      "toolId": "<one of the available tools below>",
      "purpose": "<string>",
      "reason": "<string>",
      "inputRefs": [],
      "params": { "<param>": "<value>" },
      "output": {
        "artifactTypes": ["<from the tool's artifactTypes>"]
      }
    }
  ],
  "expectedArtifacts": [
    {
      "name": "<string>",
      "type": "<ArtifactType value>",
      "fromStepId": "<stepId>"
    }
  ]
}

RULES:
1. Output ONLY the JSON object. No markdown. No explanation text. No backticks.
2. Every step.toolId MUST be one of the "Available tools" listed below.
3. Every step.stepId MUST be unique within the plan.
4. steps must contain at least one step.
5. Choose tools based on the DataProfile below.
6. params must only contain allowed parameter names from the tool manifest.
7. NEVER include api_key, token, password, or secret in params.
8. NEVER invent tool IDs that are not in the list.
9. NEVER include V1/V2 tool IDs (ends-with-v1, -v2, or stage v1/v2).
10. Every expectedArtifact.type must be one of the tool's artifactTypes.
11. For ml.* tools, include inputRefs with {"refType":"normalized_object","ref":"ml_table","objectType":"DataFrame"} when the DataProfile has table columns.
12. For structure.* tools, include inputRefs with {"refType":"normalized_object","ref":"structures","objectType":"Structure"} when structures are available.
13. For composition.* tools, include inputRefs with {"refType":"normalized_object","ref":"formulas","objectType":"Composition"} when formulas or compositions are available.
"""

_USER_PROMPT_TEMPLATE = """User prompt: {user_prompt}

Dataset: {dataset_id}
Profile: {profile_id}
Tool Registry version: {tool_registry_version}

DataProfile summary:
{profile_summary}

Available tools:
{tool_summary}

Generate the AnalysisPlan JSON now."""


def build_planner_prompt(
    request,  # PlannerRequest
    *,
    tools: list[RegisteredTool],
    data_profile: DataProfile,
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt)."""
    user = _USER_PROMPT_TEMPLATE.format(
        user_prompt=request.user_prompt,
        dataset_id=request.dataset_id,
        profile_id=request.profile_id,
        tool_registry_version=request.tool_registry_version,
        profile_summary=_profile_summary(data_profile),
        tool_summary=_tool_summary(tools),
    )
    return _SYSTEM_PROMPT, user
