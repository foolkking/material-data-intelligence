from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mdi_artifact_core import (
    ArtifactPayload,
    PHONON_BAND_DOS_COMPATIBILITY_SCHEMA_VERSION,
    PHONON_BAND_DOS_MANIFEST_SCHEMA_VERSION,
    PHONON_BAND_DOS_PLOT_SCHEMA_VERSION,
    PHONON_BAND_DOS_SCHEMA_VERSION,
    PHONON_BAND_DOS_SUMMARY_SCHEMA_VERSION,
    PHONON_BAND_DOS_TABLE_SCHEMA_VERSION,
    PhononBandDosContractError,
    PhononBandDosProducts,
    compose_phonon_band_dos,
    stable_phonon_json,
)
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError


@dataclass(frozen=True)
class PreparedPhononBandDos:
    band: Any
    dos: Any


@dataclass(frozen=True)
class PhononBandDosResult:
    products: PhononBandDosProducts
    recipe: dict[str, Any]


class PhononBandDosAdapter(BaseToolAdapter):
    tool_id = "phonon.band_dos"
    adapter_version = "0.1.0"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedPhononBandDos:
        del context, params
        if len(input_refs) != 2 or len(self._resolved_inputs) != 2:
            raise _error("PHONON_BAND_DOS_INPUT_COUNT_INVALID", "phonon.band_dos requires exactly one band artifact and one DOS artifact.")
        resolved_by_role: dict[str, Any] = {}
        expected_object_type = {"band": "PhononBand", "dos": "PhononDos"}
        for input_ref, value in zip(input_refs, self._resolved_inputs, strict=True):
            role = _ref_value(input_ref, "fieldRole")
            ref_type = _ref_value(input_ref, "refType")
            object_type = _ref_value(input_ref, "objectType")
            object_type_value = getattr(object_type, "value", object_type)
            if role not in expected_object_type or role in resolved_by_role or ref_type != "artifact" or object_type_value != expected_object_type[role]:
                raise _error(
                    "PHONON_BAND_DOS_INPUT_BINDING_INVALID",
                    "Combined inputs must be unique role-bound artifact references for PhononBand and PhononDos.",
                )
            resolved_by_role[role] = value
        if set(resolved_by_role) != {"band", "dos"}:
            raise _error("PHONON_BAND_DOS_INPUT_BINDING_INVALID", "Both band and DOS artifact roles are required.")
        return PreparedPhononBandDos(resolved_by_role["band"], resolved_by_role["dos"])

    def run(self, prepared: PreparedPhononBandDos, params: dict[str, Any]) -> PhononBandDosResult:
        normalized = _normalize_params(params)
        try:
            products = compose_phonon_band_dos(
                prepared.band,
                prepared.dos,
                selected_projection_ids=normalized["selected_projection_ids"],
                domain_policy=normalized["domain_policy"],
                manual_frequency_domain=normalized["manual_frequency_domain"],
                max_table_rows=normalized["max_table_rows"],
            )
        except PhononBandDosContractError as exc:
            raise _error(exc.code, str(exc), exc.details) from exc
        return PhononBandDosResult(products, _recipe_payload(self, normalized, products))

    def export(self, result: PhononBandDosResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        defaults = {
            ArtifactType.phonon_band_dos_json,
            ArtifactType.phonon_summary_json,
            ArtifactType.phonon_compatibility_json,
            ArtifactType.plotly_json,
            ArtifactType.table_json,
            ArtifactType.phonon_manifest_json,
            ArtifactType.recipe_json,
        }
        requested = set(artifact_types) or defaults
        products = result.products
        payload_by_type = {
            ArtifactType.phonon_band_dos_json: ("phonon_band_dos.json", products.combined),
            ArtifactType.phonon_summary_json: ("phonon_band_dos_summary.json", products.summary),
            ArtifactType.phonon_compatibility_json: ("phonon_band_dos_compatibility_report.json", products.compatibility_report),
            ArtifactType.plotly_json: ("phonon_band_dos_plot.json", products.plot),
            ArtifactType.table_json: ("phonon_band_dos_table.json", products.table),
            ArtifactType.phonon_manifest_json: ("phonon_band_dos_manifest.json", products.manifest),
            ArtifactType.recipe_json: ("recipe.json", result.recipe),
        }
        payloads = [
            ArtifactPayload(
                artifact_type=kind,
                file_name=name,
                content=stable_phonon_json(payload),
                media_type="application/json",
            )
            for kind, (name, payload) in payload_by_type.items()
            if kind in requested
        ]
        return self.export_payloads(
            payloads,
            provenance={
                "adapter": self.tool_id,
                "schemaVersion": PHONON_BAND_DOS_SCHEMA_VERSION,
                "compatibilitySchemaVersion": PHONON_BAND_DOS_COMPATIBILITY_SCHEMA_VERSION,
                "plotSchemaVersion": PHONON_BAND_DOS_PLOT_SCHEMA_VERSION,
                "manifestSchemaVersion": PHONON_BAND_DOS_MANIFEST_SCHEMA_VERSION,
                "structureIdentity": products.combined["structure_identity"],
                "sourceArtifactHashes": products.combined["provenance"]["source_hashes"],
                "sharedFrequencyAxis": True,
                "eigenvectorsIncluded": False,
                "animationIncluded": False,
                "externalResources": False,
            },
        )


def _normalize_params(params: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "selected_projection_ids",
        "domain_policy",
        "manual_frequency_min",
        "manual_frequency_max",
        "max_table_rows",
        "layout",
    }
    unknown = sorted(set(params) - allowed)
    if unknown:
        raise _error("PHONON_BAND_DOS_PARAM_INVALID", "Unknown combined band and DOS parameters are not accepted.", {"unknownParams": unknown})
    selected = params.get("selected_projection_ids", [])
    if not isinstance(selected, list) or any(not isinstance(value, str) for value in selected):
        raise _error("PHONON_BAND_DOS_PARAM_INVALID", "selected_projection_ids must be a list of approved projection identities.")
    domain_policy = params.get("domain_policy", "union")
    minimum = params.get("manual_frequency_min")
    maximum = params.get("manual_frequency_max")
    if domain_policy not in {"union", "manual_view"}:
        raise _error("PHONON_BAND_DOS_PARAM_INVALID", "domain_policy must be union or manual_view.")
    if domain_policy == "union":
        if minimum is not None or maximum is not None:
            raise _error("PHONON_BAND_DOS_PARAM_INVALID", "Manual frequency bounds require domain_policy=manual_view.")
        manual = None
    else:
        if not _finite(minimum) or not _finite(maximum) or float(minimum) >= float(maximum):
            raise _error("PHONON_BAND_DOS_PARAM_INVALID", "Manual frequency bounds must be finite and ordered.")
        manual = (float(minimum), float(maximum))
    max_rows = params.get("max_table_rows", 200)
    if not isinstance(max_rows, int) or isinstance(max_rows, bool) or not 1 <= max_rows <= 500:
        raise _error("PHONON_BAND_DOS_PARAM_INVALID", "max_table_rows must be an integer between 1 and 500.")
    if params.get("layout", "band_left_dos_right") != "band_left_dos_right":
        raise _error("PHONON_BAND_DOS_PARAM_INVALID", "Only the shared-frequency band-left/DOS-right layout is approved.")
    return {
        "selected_projection_ids": list(selected),
        "domain_policy": domain_policy,
        "manual_frequency_domain": manual,
        "max_table_rows": max_rows,
        "layout": "band_left_dos_right",
    }


def _recipe_payload(adapter: PhononBandDosAdapter, params: dict[str, Any], products: PhononBandDosProducts) -> dict[str, Any]:
    serializable_params = {**params, "manual_frequency_domain": list(params["manual_frequency_domain"]) if params["manual_frequency_domain"] is not None else None}
    return {
        "schema_version": "phase10h3.phonon_band_dos_recipe.v1",
        "tool_id": adapter.tool_id,
        "adapter_version": adapter.adapter_version,
        "structure_identity": products.combined["structure_identity"],
        "source_artifacts": products.manifest["source_artifacts"],
        "params": serializable_params,
        "compatibility_status": products.compatibility_report["status"],
        "steps": [
            "resolve_role_bound_artifacts",
            "validate_independent_contracts",
            "run_ordered_compatibility_checks",
            "apply_proven_unit_canonicalization",
            "derive_shared_frequency_domain",
            "emit_combined_static_artifacts",
        ],
        "schemas": {
            "combined": PHONON_BAND_DOS_SCHEMA_VERSION,
            "summary": PHONON_BAND_DOS_SUMMARY_SCHEMA_VERSION,
            "compatibility": PHONON_BAND_DOS_COMPATIBILITY_SCHEMA_VERSION,
            "plot": PHONON_BAND_DOS_PLOT_SCHEMA_VERSION,
            "table": PHONON_BAND_DOS_TABLE_SCHEMA_VERSION,
            "manifest": PHONON_BAND_DOS_MANIFEST_SCHEMA_VERSION,
        },
        "deterministic": True,
        "shared_frequency_axis": True,
        "eigenvectors": False,
        "animation": False,
        "thermal_properties": False,
        "phonon_calculation": False,
        "external_resources": False,
        "dependencies": {"new_dependencies_added": False, **adapter.dependency_versions()},
    }


def _ref_value(value: Any, field: str) -> Any:
    if hasattr(value, field):
        return getattr(value, field)
    if isinstance(value, dict):
        return value.get(field)
    return None


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and abs(float(value)) <= 1e12


def _error(error_type: str, message: str, details: dict[str, Any] | None = None) -> ToolExecutionError:
    return ToolExecutionError(
        code="TOOL_INPUT_INVALID",
        message=message,
        tool_id=PhononBandDosAdapter.tool_id,
        details={"errorType": error_type, **(details or {})},
    )
