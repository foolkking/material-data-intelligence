"""AnalysisPlan strict validator.

LLM output MUST be validated before any job is created or enqueued.

This validator operates in STRICT mode only — invalid plans are rejected
with structured errors.  Automatic repair is deferred to a later phase.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mdi_schemas import AnalysisPlan, ArtifactType
from mdi_tool_registry import ToolRegistry


@dataclass
class PlanValidationError:
    code: str
    message: str
    detail: Any | None = None


def _error(code: str, message: str, detail: Any = None) -> PlanValidationError:
    return PlanValidationError(code=code, message=message, detail=detail)


@dataclass
class PlanValidationResult:
    ok: bool
    errors: list[PlanValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return self.ok


def validate_plan(plan: dict[str, Any] | AnalysisPlan, *, registry: ToolRegistry) -> PlanValidationResult:
    """Validate an LLM-produced AnalysisPlan dict against the registry.

    Returns PlanValidationResult with ok=True only when ALL checks pass.
    """
    errors: list[PlanValidationError] = []

    # 1. Must be a dict
    if not isinstance(plan, dict):
        return PlanValidationResult(ok=False, errors=[_error("PLAN_NOT_DICT", "LLM output is not a JSON object.")])

    # 2. Must parse as AnalysisPlan
    try:
        parsed = AnalysisPlan.model_validate(plan)
    except Exception as exc:
        return PlanValidationResult(ok=False, errors=[_error("PLAN_SCHEMA_INVALID", "Plan does not match AnalysisPlan schema.", detail=str(exc))])

    # 3. steps cannot be empty
    if not parsed.steps:
        errors.append(_error("STEPS_EMPTY", "AnalysisPlan must contain at least one step."))

    # 4. step_id must be unique
    step_ids = [s.stepId for s in parsed.steps]
    duplicate_ids = [sid for sid in step_ids if step_ids.count(sid) > 1]
    if duplicate_ids:
        errors.append(_error("DUPLICATE_STEP_ID", f"Duplicate stepId values: {sorted(set(duplicate_ids))}"))

    # 5. Every tool_id must exist in registry
    registered_tool_ids = {t.toolId for t in registry.tools}
    for step in parsed.steps:
        if step.toolId not in registered_tool_ids:
            errors.append(_error("UNKNOWN_TOOL", f"Tool '{step.toolId}' is not in the Tool Registry.", {"stepId": step.stepId}))

    # 6. Tool must be MVP stage (no V1/V2 tools)
    tool_by_id = {t.toolId: t for t in registry.tools}
    for step in parsed.steps:
        tool = tool_by_id.get(step.toolId)
        if tool is None:
            continue  # already reported as UNKNOWN_TOOL
        if tool.stage != "mvp":
            errors.append(
                _error(
                    "NON_MVP_TOOL",
                    f"Tool '{step.toolId}' has stage '{tool.stage}'. Only MVP tools are allowed.",
                    {"stepId": step.stepId, "stage": tool.stage},
                )
            )

    # 7. expectedArtifacts type must be a known ArtifactType
    valid_artifact_types = {a.value for a in ArtifactType}
    for ea in parsed.expectedArtifacts:
        try:
            at_value = ea.type.value if hasattr(ea.type, "value") else ea.type
        except Exception:
            at_value = str(ea.type)
        if at_value not in valid_artifact_types:
            errors.append(
                _error(
                    "UNKNOWN_ARTIFACT_TYPE",
                    f"ExpectedArtifact type '{at_value}' is not a valid ArtifactType.",
                    {"artifactName": ea.name, "artifactType": at_value},
                )
            )

    # 8. inputRefs must reference known types
    _valid_ref_types = {"dataset", "profile", "normalized_object", "dataframe_column", "artifact"}
    for step in parsed.steps:
        for ref in step.inputRefs:
            try:
                rt = ref.refType.value if hasattr(ref.refType, "value") else str(ref.refType)
            except Exception:
                rt = str(ref.refType) if hasattr(ref, "refType") else "unknown"
            if rt not in _valid_ref_types:
                errors.append(_error("UNKNOWN_REF_TYPE", f"Unknown refType '{rt}' in step '{step.stepId}'.", {"stepId": step.stepId, "refType": rt}))

    # 9. params MUST NOT contain credential keys
    _credential_keys = {"api_key", "apikey", "api-key", "token", "password", "secret", "credential", "authorization"}
    for step in parsed.steps:
        for key in step.params:
            if key.lower().replace("_", "").replace("-", "") in _credential_keys:
                errors.append(_error("CREDENTIAL_IN_PARAMS", f"Param '{key}' looks like a credential in step '{step.stepId}'.", {"stepId": step.stepId, "key": key}))

    return PlanValidationResult(ok=len(errors) == 0, errors=errors)
