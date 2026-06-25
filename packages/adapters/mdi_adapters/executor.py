from __future__ import annotations

from dataclasses import dataclass
from typing import Any, MutableMapping

from jsonschema import Draft202012Validator

from mdi_artifact_core import content_hash, stable_json_dumps
from mdi_schemas import Artifact, ArtifactType, RegisteredTool, ToolExecutionRequest
from mdi_tool_registry import ToolRegistry, load_manifests

from .context import ToolExecutionContext
from .errors import ToolExecutionError, normalize_exception
from .registry import create_adapter


ArtifactCache = MutableMapping[str, list[Artifact]]


@dataclass(frozen=True)
class ToolExecutionResult:
    tool: RegisteredTool
    artifacts: list[Artifact]
    cache_key: str
    cache_hit: bool


def execute_tool_request(
    context: ToolExecutionContext,
    request: ToolExecutionRequest | dict[str, Any],
    *,
    registry: ToolRegistry | None = None,
    cache: ArtifactCache | None = None,
) -> ToolExecutionResult:
    """Execute a ToolExecutionRequest through the registry-approved adapter path."""

    parsed_request = request if isinstance(request, ToolExecutionRequest) else ToolExecutionRequest.model_validate(request)
    active_registry = registry or load_manifests()
    tool = _lookup_tool(active_registry, parsed_request.toolId)

    _validate_artifact_types(tool, parsed_request.artifactTypes)
    _validate_params(tool, parsed_request.params)
    cache_key = _cache_key(context, parsed_request, tool)

    context.tool_id = tool.toolId
    context.tool_version = tool.version
    context.registry_version = active_registry.version
    context.resource_limits = {**tool.resourceLimits, **context.resource_limits}

    if cache is not None and tool.cachePolicy == "reuse" and cache_key in cache:
        return ToolExecutionResult(tool=tool, artifacts=cache[cache_key], cache_key=cache_key, cache_hit=True)

    try:
        adapter = create_adapter(tool.adapter)
    except KeyError as exc:
        raise ToolExecutionError(
            code="TOOL_ADAPTER_UNAVAILABLE",
            message=f"Adapter `{tool.adapter}` is not registered.",
            tool_id=tool.toolId,
            details={"adapter": tool.adapter},
        ) from exc

    try:
        artifacts = adapter.execute(context, parsed_request)
    except ToolExecutionError:
        raise
    except Exception as exc:
        raise normalize_exception(exc, tool_id=tool.toolId) from exc

    if cache is not None and tool.cachePolicy == "reuse":
        cache[cache_key] = artifacts

    return ToolExecutionResult(tool=tool, artifacts=artifacts, cache_key=cache_key, cache_hit=False)


def _lookup_tool(registry: ToolRegistry, tool_id: str) -> RegisteredTool:
    try:
        return registry.get_tool_by_id(tool_id)
    except KeyError as exc:
        raise ToolExecutionError(
            code="TOOL_NOT_REGISTERED",
            message=f"Tool `{tool_id}` is not registered in Tool Registry.",
            tool_id=tool_id,
        ) from exc


def _validate_artifact_types(tool: RegisteredTool, artifact_types: list[ArtifactType]) -> None:
    allowed = set(tool.artifactTypes)
    requested = set(artifact_types)
    invalid = sorted(artifact_type.value for artifact_type in requested - allowed)
    if invalid:
        raise ToolExecutionError(
            code="TOOL_ARTIFACT_INVALID",
            message="Requested artifact types are not declared by the registered tool.",
            tool_id=tool.toolId,
            details={"invalidArtifactTypes": invalid},
        )


def _validate_params(tool: RegisteredTool, params: dict[str, Any]) -> None:
    schema = tool.paramsSchema or {"type": "object", "additionalProperties": True}
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(params), key=lambda error: list(error.path))
    if errors:
        raise ToolExecutionError(
            code="TOOL_PARAM_INVALID",
            message="Tool params do not match the registered paramsSchema.",
            tool_id=tool.toolId,
            details={"errors": [error.message for error in errors]},
        )


def _cache_key(context: ToolExecutionContext, request: ToolExecutionRequest, tool: RegisteredTool) -> str:
    try:
        resolved_inputs = context.resolve_input_refs(request.inputRefs)
        input_hashes = context.input_hashes(resolved_inputs)
    except Exception as exc:
        raise ToolExecutionError(
            code="TOOL_INPUT_INVALID",
            message=str(exc),
            tool_id=tool.toolId,
        ) from exc

    payload = {
        "kind": "tool_result",
        "toolId": tool.toolId,
        "toolVersion": tool.version,
        "adapter": tool.adapter,
        "inputHashes": input_hashes,
        "params": request.params,
        "artifactTypes": [artifact_type.value for artifact_type in request.artifactTypes],
    }
    return f"cache:tool_result:{content_hash(stable_json_dumps(payload))}"

