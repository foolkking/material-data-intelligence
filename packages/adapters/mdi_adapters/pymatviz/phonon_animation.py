from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mdi_artifact_core import (
    ArtifactPayload,
    PHONON_ANIMATION_MANIFEST_SCHEMA_VERSION,
    PHONON_ANIMATION_RECIPE_SCHEMA_VERSION,
    PHONON_ANIMATION_SCHEMA_VERSION,
    PHONON_ANIMATION_SUMMARY_SCHEMA_VERSION,
    PhononAnimationContractError,
    build_phonon_animation,
    normalize_animation_params,
    phonon_animation_manifest,
    phonon_animation_summary,
    stable_phonon_json,
)
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError


@dataclass(frozen=True)
class PreparedPhononAnimation:
    structure: dict[str, Any]
    band: dict[str, Any]
    eigenvectors: dict[str, Any]


@dataclass(frozen=True)
class PhononAnimationResult:
    package: dict[str, Any]
    summary: dict[str, Any]
    manifest: dict[str, Any]
    recipe: dict[str, Any]


class PhononAnimationAdapter(BaseToolAdapter):
    tool_id = "phonon.animation"
    adapter_version = "0.1.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedPhononAnimation:
        del context, params
        expected = {"structure": "Structure", "band": "PhononBand", "eigenvectors": "PhononEigenvector"}
        if len(input_refs) != 3 or len(self._resolved_inputs) != 3:
            raise _error("PHONON_ANIMATION_INPUT_COUNT_INVALID", "phonon.animation requires structure, band, and eigenvector-set inputs.")
        resolved: dict[str, Any] = {}
        for ref, value in zip(input_refs, self._resolved_inputs, strict=True):
            role = _ref_value(ref, "fieldRole")
            object_type = getattr(_ref_value(ref, "objectType"), "value", _ref_value(ref, "objectType"))
            if role not in expected or role in resolved or object_type != expected[role] or _ref_value(ref, "refType") not in {"artifact", "normalized_object"}:
                raise _error("PHONON_ANIMATION_INPUT_BINDING_INVALID", "Animation inputs must use unique approved roles and object types.")
            if not isinstance(value, dict):
                raise _error("PHONON_ANIMATION_INPUT_INVALID", "Resolved animation inputs must be inert JSON objects.")
            resolved[role] = value
        if set(resolved) != set(expected):
            raise _error("PHONON_ANIMATION_INPUT_BINDING_INVALID", "All animation input roles are required.")
        return PreparedPhononAnimation(resolved["structure"], resolved["band"], resolved["eigenvectors"])

    def run(self, prepared: PreparedPhononAnimation, params: dict[str, Any]) -> PhononAnimationResult:
        try:
            normalized = normalize_animation_params(params)
            package = build_phonon_animation(prepared.structure, prepared.band, prepared.eigenvectors, normalized)
        except PhononAnimationContractError as exc:
            raise _error(exc.code, str(exc)) from exc
        summary = phonon_animation_summary(package)
        manifest = phonon_animation_manifest(package, summary)
        recipe = {
            "schema_version": PHONON_ANIMATION_RECIPE_SCHEMA_VERSION,
            "tool_id": self.tool_id,
            "adapter_version": self.adapter_version,
            "mode_id": package["mode"]["mode"]["mode_id"],
            "params": normalized,
            "steps": ["resolve_role_bound_inputs", "validate_contracts_and_compatibility", "select_canonical_mode", "derive_bounded_commensurate_supercell", "emit_declarative_animation_package"],
            "frames_persisted": False,
            "display_only": True,
            "phonon_calculation_performed": False,
            "external_resources": False,
            "deterministic": True,
        }
        return PhononAnimationResult(package, summary, manifest, recipe)

    def export(self, result: PhononAnimationResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        defaults = {ArtifactType.phonon_animation_json, ArtifactType.phonon_animation_summary_json, ArtifactType.phonon_animation_manifest_json, ArtifactType.recipe_json}
        requested = set(artifact_types) or defaults
        payloads = {
            ArtifactType.phonon_animation_json: ("phonon_animation.json", result.package),
            ArtifactType.phonon_animation_summary_json: ("phonon_animation_summary.json", result.summary),
            ArtifactType.phonon_animation_manifest_json: ("phonon_animation_manifest.json", result.manifest),
            ArtifactType.recipe_json: ("recipe.json", result.recipe),
        }
        return self.export_payloads(
            [ArtifactPayload(artifact_type=kind, file_name=name, content=stable_phonon_json(payload), media_type="application/json") for kind, (name, payload) in payloads.items() if kind in requested],
            provenance={
                "adapter": self.tool_id,
                "schemaVersion": PHONON_ANIMATION_SCHEMA_VERSION,
                "summarySchemaVersion": PHONON_ANIMATION_SUMMARY_SCHEMA_VERSION,
                "manifestSchemaVersion": PHONON_ANIMATION_MANIFEST_SCHEMA_VERSION,
                "modeId": result.package["mode"]["mode"]["mode_id"],
                "structureIdentity": result.package["structure"]["structure_identity"],
                "rendererIncluded": False,
                "externalResources": False,
            },
        )


def _ref_value(value: Any, field: str) -> Any:
    if hasattr(value, field):
        return getattr(value, field)
    return value.get(field) if isinstance(value, dict) else None


def _error(error_type: str, message: str) -> ToolExecutionError:
    return ToolExecutionError(code="TOOL_INPUT_INVALID", message=message, tool_id=PhononAnimationAdapter.tool_id, details={"errorType": error_type})
