from __future__ import annotations

import importlib.metadata as metadata
from abc import ABC, abstractmethod
from typing import Any

from mdi_artifact_core import ArtifactPayload, LocalArtifactExporter, content_hash, stable_json_dumps
from mdi_schemas import Artifact, ArtifactType, ToolExecutionRequest

from .context import ToolExecutionContext
from .errors import ToolExecutionError, normalize_exception


SECRET_PARAM_MARKERS = ("secret", "api_key", "apikey", "token", "password", "byok")


class BaseToolAdapter(ABC):
    tool_id: str
    adapter_version = "0.1.0"

    def __init__(self) -> None:
        self._context: ToolExecutionContext | None = None
        self._resolved_inputs: list[Any] = []
        self._input_hashes: list[str] = []
        self._params_hash = ""

    @property
    def context(self) -> ToolExecutionContext:
        if self._context is None:
            raise RuntimeError("Adapter context is only available during execute/export")
        return self._context

    def execute(self, context: ToolExecutionContext, request: ToolExecutionRequest | Any) -> list[Artifact]:
        requested_tool_id = self._request_value(request, "toolId")
        if requested_tool_id != self.tool_id:
            raise ToolExecutionError(
                code="TOOL_INPUT_INVALID",
                message=f"Request toolId does not match adapter {self.tool_id}",
                tool_id=self.tool_id,
            )

        params = self._request_value(request, "params", {})
        artifact_types = [ArtifactType(item) for item in self._request_value(request, "artifactTypes", [])]
        self._reject_secret_params(params)
        self._context = context
        context.tool_id = self.tool_id
        context.adapter_version = self.adapter_version

        try:
            input_refs = self._request_value(request, "inputRefs", [])
            self._resolved_inputs = context.resolve_input_refs(input_refs)
            self._input_hashes = context.input_hashes(self._resolved_inputs)
            self._params_hash = content_hash(stable_json_dumps(params))
            prepared = self.prepare(context, input_refs, params)
            result = self.run(prepared, params)
            return self.export(result, artifact_types)
        except ToolExecutionError:
            raise
        except Exception as exc:
            raise normalize_exception(exc, tool_id=self.tool_id) from exc
        finally:
            self._context = None

    @abstractmethod
    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> Any:
        """Resolve dataset references and validate input objects."""

    @abstractmethod
    def run(self, prepared: Any, params: dict[str, Any]) -> Any:
        """Call pymatviz / MatterViz / Plotly / platform builtin logic."""

    @abstractmethod
    def export(self, result: Any, artifact_types: list[ArtifactType]) -> list[Artifact]:
        """Export standardized artifacts and metadata."""

    def export_payloads(self, payloads: list[ArtifactPayload], provenance: dict[str, Any]) -> list[Artifact]:
        context = self.context
        exporter = LocalArtifactExporter(context.artifact_root)
        return exporter.export_payloads(
            payloads=payloads,
            project_id=context.project_id,
            dataset_id=context.dataset_id,
            job_id=context.job_id,
            tool_call_id=context.tool_call_id,
            tool_id=self.tool_id,
            tool_version=context.tool_version,
            adapter_version=self.adapter_version,
            input_hashes=self._input_hashes,
            params_hash=self._params_hash,
            provenance={**self.dependency_versions(), **provenance},
        )

    def recipe_payload(self, *, name: str, params: dict[str, Any], artifact_types: list[ArtifactType]) -> dict[str, Any]:
        context = self.context
        return {
            "schemaVersion": "0.1",
            "recipeId": f"recipe_{context.tool_call_id}",
            "name": name,
            "version": "1",
            "projectId": context.project_id,
            "sourceJobId": context.job_id,
            "inputRequirements": [],
            "steps": [
                {
                    "stepId": "step_from_adapter",
                    "toolId": self.tool_id,
                    "toolVersion": context.tool_version,
                    "inputBindings": {"inputRefs": "resolved_by_tool_call"},
                    "params": params,
                    "artifactTypes": [artifact_type.value for artifact_type in artifact_types],
                }
            ],
            "environment": self.dependency_versions(),
        }

    @staticmethod
    def dependency_versions() -> dict[str, str]:
        versions: dict[str, str] = {}
        for package in ("python", "pymatviz", "pymatgen", "ase", "plotly"):
            if package == "python":
                continue
            try:
                versions[f"{package}Version"] = metadata.version(package)
            except metadata.PackageNotFoundError:
                versions[f"{package}Version"] = "not-installed"
        return versions

    def _reject_secret_params(self, params: dict[str, Any]) -> None:
        for key, value in params.items():
            lowered = str(key).lower()
            if any(marker in lowered for marker in SECRET_PARAM_MARKERS):
                raise ToolExecutionError(
                    code="TOOL_PARAM_INVALID",
                    message="Tool params must not contain Secret/BYOK values or references.",
                    tool_id=self.tool_id,
                    details={"param": key},
                )
            if isinstance(value, dict):
                self._reject_secret_params(value)

    @staticmethod
    def _request_value(request: ToolExecutionRequest | Any, key: str, default: Any | None = None) -> Any:
        if hasattr(request, key):
            return getattr(request, key)
        if isinstance(request, dict):
            return request.get(key, default)
        return default

