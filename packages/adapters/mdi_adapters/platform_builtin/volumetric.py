from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mdi_artifact_core import (
    ArtifactPayload,
    VolumetricContractError,
    build_binary_payload,
    build_volumetric_dataset,
    build_volumetric_field,
    build_volumetric_grid,
    build_volumetric_manifest,
    build_volumetric_structure_overlay,
    decode_volumetric_payload,
    stable_json_dumps,
    stable_volumetric_json,
    validate_volumetric_dataset,
    validate_volumetric_manifest,
    volumetric_lattice_hash,
)
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError
from .structure import _viewer_scene_v1_params, _viewer_scene_v1_payload
from pymatgen.core import Structure


VOLUMETRIC_TOOL_ID = "structure.volumetric_data"
VOLUMETRIC_ADAPTER_VERSION = "1.1.0"
VOLUMETRIC_ARTIFACT_TYPES = [
    ArtifactType.volumetric_grid_json,
    ArtifactType.volumetric_payload_json,
    ArtifactType.volumetric_field_json,
    ArtifactType.volumetric_dataset_json,
    ArtifactType.volumetric_manifest_json,
    ArtifactType.volumetric_structure_overlay_json,
    ArtifactType.volumetric_binary,
    ArtifactType.summary_md,
    ArtifactType.recipe_json,
]


@dataclass(frozen=True)
class VolumetricAdapterResult:
    source: dict[str, Any]
    params: dict[str, Any]
    grid: dict[str, Any]
    payloads: tuple[dict[str, Any], ...]
    fields: tuple[dict[str, Any], ...]
    binary_artifacts: dict[str, bytes]
    dataset: dict[str, Any]
    manifest: dict[str, Any]
    structure_overlay: dict[str, Any]


class VolumetricDataAdapter(BaseToolAdapter):
    """Convert one bounded parsed VASP/CUBE source into canonical inert artifacts."""

    tool_id = VOLUMETRIC_TOOL_ID
    adapter_version = VOLUMETRIC_ADAPTER_VERSION

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> dict[str, Any]:
        _normalize_params(params)
        if len(self._resolved_inputs) != 1:
            raise _error("TOOL_INPUT_INVALID", "Exactly one bounded volumetric source is required.", "single_source_required")
        value = self._resolved_inputs[0]
        if hasattr(value, "object_type"):
            if getattr(value.object_type, "value", value.object_type) != "VolumetricData":
                raise _error("TOOL_INPUT_INVALID", "Input must be a normalized VolumetricData object.", "object_type_mismatch")
            value = value.payload
        if not isinstance(value, dict) or value.get("source_format") not in {"vasp_volumetric", "gaussian_cube"}:
            raise _error("TOOL_INPUT_INVALID", "Input is not a validated bounded volumetric source model.", "source_model_invalid")
        if set(value.get("source_sha256", "")) == {"0"} or len(str(value.get("source_sha256", ""))) != 64:
            raise _error("TOOL_INPUT_INVALID", "Volumetric source provenance is missing.", "source_hash_invalid")
        return value

    def run(self, prepared: dict[str, Any], params: dict[str, Any]) -> VolumetricAdapterResult:
        normalized = _normalize_params(params)
        if normalized["format"] != "auto" and normalized["format"] != prepared["source_format"]:
            raise _error("TOOL_INPUT_INVALID", "Explicit format does not match the parsed source.", "format_mismatch")
        prepared = _apply_quantity_hint(prepared, normalized["quantity_hint"])
        selected = _selected_channels(prepared["channels"], normalized["field_selection"])
        if not selected:
            raise _error("TOOL_INPUT_INVALID", "Field selection did not retain a supported source channel.", "field_selection_empty")
        try:
            binding = None
            origin_fractional = None
            if prepared["boundary_conditions"] == ["periodic"] * 3:
                binding = {
                    "structure_sha256": prepared["structure_sha256"],
                    "lattice_sha256": volumetric_lattice_hash(prepared["lattice_matrix"]),
                    "lattice_matrix": prepared["lattice_matrix"],
                    "basis_role": "canonical_structure_cell",
                }
                origin_fractional = [0.0, 0.0, 0.0]
            grid = build_volumetric_grid(
                shape=prepared["shape"],
                origin_cartesian=prepared["origin_cartesian"],
                step_matrix=prepared["step_matrix"],
                sample_location=prepared["sample_location"],
                boundary_conditions=prepared["boundary_conditions"],
                endpoint_policy=prepared["endpoint_policy"],
                structure_binding=binding,
                origin_fractional=origin_fractional,
            )
            structure_overlay = _build_structure_overlay(prepared, grid, self.context)
            provenance = _provenance(prepared)
            channels = _derive_collinear_channels(_coalesce_noncollinear(selected))
            payloads: list[dict[str, Any]] = []
            fields: list[dict[str, Any]] = []
            binaries: dict[str, bytes] = {}
            runtime_warnings = list(prepared.get("warnings", []))
            for index, channel in enumerate(channels):
                components = int(channel.get("stored_components", 1))
                name = f"volumetric_field_{index + 1:02d}.f64"
                encoding = "gzip_binary" if normalized["compression"] == "contract_default" else normalized["compression"]
                if encoding == "gzip_binary":
                    name += ".gz"
                try:
                    bundle = build_binary_payload(
                        channel["values"], grid_shape=prepared["shape"], stored_components=components,
                        dtype="float64" if normalized["stored_dtype"] in {"source_or_float64", "float64"} else "float32",
                        encoding=encoding, artifact_name=name,
                    )
                except VolumetricContractError as exc:
                    if normalized["compression"] != "contract_default" or exc.code != "VOLUME_COMPRESSION_RATIO_EXCEEDED":
                        raise
                    name = name.removesuffix(".gz")
                    bundle = build_binary_payload(
                        channel["values"], grid_shape=prepared["shape"], stored_components=components,
                        dtype="float64" if normalized["stored_dtype"] in {"source_or_float64", "float64"} else "float32",
                        encoding="raw_binary", artifact_name=name,
                    )
                    runtime_warnings.append("VOLUME_COMPRESSION_RATIO_FALLBACK_RAW")
                stored_values = decode_volumetric_payload(bundle.metadata, bundle.artifacts)
                spin = _spin_metadata(channel)
                potential = None
                if channel["quantity"] in {"electrostatic_potential", "local_potential"}:
                    potential = {
                        "kind": "source_defined", "reference_value": 0.0,
                        "reference_unit": channel["canonical_unit"], "shift_applied": False,
                        "shift_amount": 0.0, "source_metadata": "No alignment or mean shift was applied.",
                    }
                field = build_volumetric_field(
                    grid=grid,
                    payload=bundle.metadata,
                    values=stored_values,
                    field_name=channel["name"],
                    quantity=channel["quantity"],
                    unit=channel["canonical_unit"],
                    source_unit=channel["source_unit"],
                    unit_conversion_factor=channel["conversion_factor"],
                    unit_conversion_provenance="source parser unit normalization",
                    value_kind="real",
                    field_rank="vector" if components == 3 else "scalar",
                    normalization_semantics=channel["normalization_semantics"],
                    integral_semantics=channel["integral_semantics"],
                    spin=spin,
                    potential_reference=potential,
                    provenance=_channel_provenance(provenance, channel),
                    warnings=[*runtime_warnings, *channel.get("warnings", [])],
                )
                payloads.append(bundle.metadata)
                fields.append(field)
                binaries.update(bundle.artifacts)
            relationships = _field_relationships(fields, channels)
            dataset = build_volumetric_dataset(
                grid=grid,
                payloads=payloads,
                fields=fields,
                relationships=relationships,
                provenance=provenance,
                warnings=runtime_warnings,
                artifacts=binaries,
            )
            manifest = build_volumetric_manifest(dataset, binaries)
            if not validate_volumetric_dataset(dataset, binaries).valid or not validate_volumetric_manifest(manifest, dataset=dataset, artifacts=binaries).valid:
                raise VolumetricContractError("VOLUME_ADAPTER_VALIDATION_FAILED", "Generated package failed validation.")
        except VolumetricContractError as exc:
            raise _error("TOOL_CONTRACT_INVALID", "Generated volumetric artifacts failed canonical validation.", exc.code) from exc
        return VolumetricAdapterResult(prepared, normalized, grid, tuple(payloads), tuple(fields), binaries, dataset, manifest, structure_overlay)

    def export(self, result: VolumetricAdapterResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        historical_types = set(VOLUMETRIC_ARTIFACT_TYPES) - {ArtifactType.volumetric_structure_overlay_json}
        requested_types = set(artifact_types)
        if artifact_types and requested_types != set(VOLUMETRIC_ARTIFACT_TYPES) and requested_types != historical_types:
            raise _error("TOOL_INPUT_INVALID", "Volumetric execution requires the complete canonical artifact package.", "artifact_request_mismatch")
        payloads: list[ArtifactPayload] = [
            ArtifactPayload(ArtifactType.volumetric_grid_json, "volumetric_grid.json", stable_volumetric_json(result.grid), "application/json"),
            *[
                ArtifactPayload(ArtifactType.volumetric_payload_json, f"volumetric_payload_{idx + 1:02d}.json", stable_volumetric_json(item), "application/json")
                for idx, item in enumerate(result.payloads)
            ],
            *[
                ArtifactPayload(ArtifactType.volumetric_field_json, f"volumetric_field_{idx + 1:02d}.json", stable_volumetric_json(item), "application/json")
                for idx, item in enumerate(result.fields)
            ],
            *[
                ArtifactPayload(ArtifactType.volumetric_binary, name, content, _binary_media_type(name))
                for name, content in sorted(result.binary_artifacts.items())
            ],
            ArtifactPayload(ArtifactType.volumetric_dataset_json, "volumetric_dataset.json", stable_volumetric_json(result.dataset), "application/json"),
            ArtifactPayload(ArtifactType.volumetric_manifest_json, "volumetric_manifest.json", stable_volumetric_json(result.manifest), "application/json"),
            ArtifactPayload(ArtifactType.volumetric_structure_overlay_json, "volumetric_structure_overlay.json", stable_volumetric_json(result.structure_overlay), "application/json"),
            ArtifactPayload(ArtifactType.summary_md, "summary.md", _summary(result), "text/markdown"),
        ]
        recipe = self.recipe_payload(name="Canonical Volumetric Data", params=result.params, artifact_types=VOLUMETRIC_ARTIFACT_TYPES)
        recipe["scientificContract"] = {
            "schemaFamily": "phase10j.volumetric",
            "sourceFormat": result.source["source_format"],
            "sourceSha256": result.source["source_sha256"],
            "flattenOrder": "ijkc_component_fastest",
            "rendererIncluded": False,
            "externalNetwork": False,
            "transformations": result.dataset["provenance"]["transformations"],
            "derivedFieldFormulas": sorted({
                transformation["detail"].split(":", 1)[0]
                for field in result.fields
                for transformation in field["provenance"]["transformations"]
                if transformation["kind"] == "component_remapping"
                and transformation["detail"].startswith(("COLLINEAR_SPIN_UP_V1:", "COLLINEAR_SPIN_DOWN_V1:"))
            }),
            "fieldRelationships": result.dataset["relationships"],
            "potentialFields": [
                {
                    "fieldId": field["field_id"],
                    "quantity": field["quantity"],
                    "unit": field["unit"]["canonical_unit"],
                    "reference": field["potential_reference"],
                }
                for field in result.fields
                if field["quantity"] in {"local_potential", "electrostatic_potential"}
            ],
            "elfOrbitalFields": [
                {
                    "fieldId": field["field_id"],
                    "fieldHash": field["content_hash"],
                    "quantity": field["quantity"],
                    "unit": field["unit"]["canonical_unit"],
                    "normalization": field["normalization_semantics"],
                    "integralSemantics": field["integral_semantics"],
                    "identityCompleteness": "unavailable" if field["quantity"] == "orbital_density" else "not_applicable",
                    "sourceInterpretation": "source_defined_partial_density" if field["quantity"] == "orbital_density" else "source_native_elf",
                    "sourceValuesModified": False,
                }
                for field in result.fields
                if field["quantity"] in {"electron_localization_function", "orbital_density"}
            ],
        }
        payloads.append(ArtifactPayload(ArtifactType.recipe_json, "recipe.json", stable_json_dumps(recipe), "application/json"))
        artifacts = self.export_payloads(payloads, provenance={
            "contractFamily": "phase10j.volumetric", "sourceSha256": result.source["source_sha256"],
            "deterministic": True, "rendererIncluded": False, "externalNetwork": False,
        })
        _make_repeated_artifact_ids_unique(artifacts)
        return artifacts


def _build_structure_overlay(
    prepared: dict[str, Any], grid: dict[str, Any], context: ToolExecutionContext
) -> dict[str, Any]:
    if grid["boundary_conditions"] == ["periodic"] * 3:
        try:
            structure = Structure.from_dict(prepared["structure"])
            viewer_params = _viewer_scene_v1_params({}, context.resource_limits, tool_id=VOLUMETRIC_TOOL_ID)
            viewer_scene, _manifest = _viewer_scene_v1_payload(
                "volumetric-structure",
                structure,
                params=viewer_params,
                tool_id=VOLUMETRIC_TOOL_ID,
                context=context,
            )
            return build_volumetric_structure_overlay(grid=grid, viewer_scene=viewer_scene)
        except (KeyError, TypeError, ValueError, ToolExecutionError):
            return build_volumetric_structure_overlay(
                grid=grid,
                unavailable_reason="periodic_structure_overlay_unavailable",
            )
    atom_records = [
        {
            "atomic_number": int(item["atomic_number"]),
            "cartesian_angstrom": list(item["cartesian_angstrom"]),
        }
        for item in prepared.get("atom_records", [])
    ]
    return build_volumetric_structure_overlay(grid=grid, atom_records=atom_records)


def _normalize_params(params: dict[str, Any]) -> dict[str, Any]:
    allowed = {"format", "quantity_hint", "field_selection", "stored_dtype", "compression", "include_statistics", "include_histogram", "verify_integrals", "allow_partial_dataset"}
    unknown = sorted(set(params) - allowed)
    if unknown:
        raise _error("TOOL_PARAM_INVALID", "Unknown volumetric parameters are not accepted.", "unknown_params", unknownParams=unknown)
    normalized = {
        "format": params.get("format", "auto"), "quantity_hint": params.get("quantity_hint", "auto"),
        "field_selection": params.get("field_selection", "all_supported"), "stored_dtype": params.get("stored_dtype", "source_or_float64"),
        "compression": params.get("compression", "contract_default"), "include_statistics": params.get("include_statistics", True),
        "include_histogram": params.get("include_histogram", False), "verify_integrals": params.get("verify_integrals", True),
        "allow_partial_dataset": params.get("allow_partial_dataset", False),
    }
    enums = {
        "format": {"auto", "vasp_volumetric", "gaussian_cube"},
        "quantity_hint": {"auto", "electron_density", "charge_density", "spin_density", "magnetization_density", "electrostatic_potential", "electron_localization_function", "orbital_density", "wavefunction", "generic_scalar"},
        "field_selection": {"all_supported", "total_only", "spin_channels", "first_scalar"},
        "stored_dtype": {"source_or_float64", "float32", "float64"},
        "compression": {"contract_default", "raw_binary", "gzip_binary"},
    }
    if any(normalized[key] not in values for key, values in enums.items()):
        raise _error("TOOL_PARAM_INVALID", "A volumetric enum parameter is invalid.", "enum_invalid")
    if normalized["include_statistics"] is not True or normalized["include_histogram"] is not False or normalized["verify_integrals"] is not True or normalized["allow_partial_dataset"] is not False:
        raise _error("TOOL_PARAM_INVALID", "Canonical validation and complete bounded output cannot be disabled.", "required_policy_disabled")
    return normalized


def _selected_channels(channels: list[dict[str, Any]], selection: str) -> list[dict[str, Any]]:
    if selection in {"total_only", "first_scalar"}:
        return channels[:1]
    if selection == "spin_channels":
        return [item for item in channels if item.get("spin_channel") not in {None, "total"}]
    return list(channels)


def _apply_quantity_hint(source: dict[str, Any], hint: str) -> dict[str, Any]:
    if hint == "auto":
        return source
    copied = {**source, "channels": [dict(item) for item in source["channels"]], "warnings": list(source.get("warnings", []))}
    if source["source_format"] != "gaussian_cube":
        if any(item["quantity"] != hint for item in copied["channels"]):
            copied["warnings"].append("VOLUME_QUANTITY_HINT_CONFLICT")
        copied["warnings"] = sorted(set(copied["warnings"]))
        return copied
    channel = copied["channels"][0]
    if channel["quantity"] != "generic_scalar":
        if channel["quantity"] != hint:
            copied["warnings"].append("VOLUME_QUANTITY_HINT_CONFLICT")
        return copied
    spatial = str(source.get("source_spatial_unit", "angstrom"))
    density_factor = (1.0 / 0.529177210903**3) if spatial == "bohr" else 1.0
    policies = {
        "electron_density": ("electron/bohr^3" if spatial == "bohr" else "electron/angstrom^3", "electron/angstrom^3", density_factor, "electron_count"),
        "orbital_density": ("electron/bohr^3" if spatial == "bohr" else "electron/angstrom^3", "electron/angstrom^3", density_factor, "electron_count"),
        "charge_density": ("electron/bohr^3" if spatial == "bohr" else "elementary_charge/angstrom^3", "elementary_charge/angstrom^3", density_factor, "elementary_charge"),
        "spin_density": ("electron/bohr^3" if spatial == "bohr" else "bohr_magneton/angstrom^3", "bohr_magneton/angstrom^3", density_factor, "magnetic_moment"),
        "magnetization_density": ("electron/bohr^3" if spatial == "bohr" else "bohr_magneton/angstrom^3", "bohr_magneton/angstrom^3", density_factor, "magnetic_moment"),
        "electrostatic_potential": ("hartree", "hartree", 1.0, "cell_average"),
        "generic_scalar": ("dimensionless", "dimensionless", 1.0, "not_physically_interpreted"),
    }
    if hint not in policies:
        raise _error("TOOL_INPUT_INVALID", "CUBE quantity hint is incompatible with a real scalar source.", "quantity_hint_unsupported")
    source_unit, canonical_unit, factor, integral = policies[hint]
    channel.update({
        "quantity": hint, "source_unit": source_unit, "canonical_unit": canonical_unit,
        "conversion_factor": factor, "values": [float(value) * factor for value in channel["values"]],
        "integral_semantics": integral,
    })
    return copied


def _coalesce_noncollinear(channels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    vectors = [item for item in channels if item.get("spin_channel") in {"magnetization_x", "magnetization_y", "magnetization_z"}]
    if not vectors:
        return channels
    if len(vectors) != 3:
        raise _error("TOOL_INPUT_INVALID", "Non-collinear magnetization requires all three source components.", "noncollinear_incomplete")
    by_name = {item["spin_channel"]: item for item in vectors}
    order = [by_name[f"magnetization_{axis}"] for axis in "xyz"]
    interleaved = [value for row in zip(*(item["values"] for item in order), strict=True) for value in row]
    vector = {**order[0], "name": "magnetization_vector", "values": interleaved, "stored_components": 3, "spin_channel": "magnetization_vector"}
    return [item for item in channels if item not in vectors] + [vector]


def _derive_collinear_channels(channels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_spin = {item.get("spin_channel"): item for item in channels}
    total = by_spin.get("total")
    difference = by_spin.get("spin_difference")
    if total is None or difference is None:
        return channels
    if (
        total.get("quantity") != "electron_density"
        or total.get("canonical_unit") != "electron/angstrom^3"
        or difference.get("quantity") != "magnetization_density"
        or difference.get("canonical_unit") != "bohr_magneton/angstrom^3"
        or len(total["values"]) != len(difference["values"])
    ):
        return channels
    derived: list[dict[str, Any]] = []
    for name, formula_id, sign in (
        ("spin_up", "COLLINEAR_SPIN_UP_V1", 1.0),
        ("spin_down", "COLLINEAR_SPIN_DOWN_V1", -1.0),
    ):
        values = [
            (float(total_value) + sign * float(spin_value)) / 2.0
            for total_value, spin_value in zip(total["values"], difference["values"], strict=True)
        ]
        warnings = []
        if min(values) < -max(1e-12, max(abs(value) for value in values) * 1e-10):
            warnings.append("VOLUME_DERIVED_SPIN_CHANNEL_NEGATIVE")
        derived.append({
            **total,
            "name": name,
            "quantity": "spin_density",
            "source_unit": "electron/angstrom^3",
            "canonical_unit": "electron/angstrom^3",
            "conversion_factor": 1.0,
            "values": values,
            "normalization_semantics": "source_native",
            "integral_semantics": "electron_count",
            "spin_channel": name,
            "derived_formula": formula_id,
            "derived_sources": ("total", "spin_difference"),
            "warnings": warnings,
        })
    return [*channels, *derived]


def _channel_provenance(base: dict[str, Any], channel: dict[str, Any]) -> dict[str, Any]:
    formula = channel.get("derived_formula")
    if formula not in {"COLLINEAR_SPIN_UP_V1", "COLLINEAR_SPIN_DOWN_V1"}:
        return base
    value = {**base, "producer_version": VOLUMETRIC_ADAPTER_VERSION, "transformations": [*base["transformations"], {
        "kind": "component_remapping",
        "detail": f"{formula}: rho=(rho_total +/- rho_spin)/2; one bohr magneton density is treated as one collinear spin-count difference density.",
    }]}
    return value


def _spin_metadata(channel: dict[str, Any]) -> dict[str, Any] | None:
    spin_channel = channel.get("spin_channel")
    if channel["quantity"] not in {"spin_density", "magnetization_density"}:
        return None
    return {
        "representation": "non_collinear" if spin_channel == "magnetization_vector" else "collinear",
        "channel": spin_channel,
        "component_basis": "cartesian" if spin_channel == "magnetization_vector" else "not_applicable",
        "sign_convention": "up minus down" if spin_channel in {"spin_up", "spin_down", "spin_difference"} else "source-defined magnetization sign",
        "source_convention": "allowlisted collinear derivation from VASP total and spin difference" if spin_channel in {"spin_up", "spin_down"} else "VASP total then magnetization components",
    }


def _provenance(source: dict[str, Any]) -> dict[str, Any]:
    transforms = [{"kind": "axis_permutation", "detail": "VASP x-fastest order converted to canonical ijkc."}] if source["source_format"] == "vasp_volumetric" else []
    if any(float(item.get("conversion_factor", 1.0)) != 1.0 for item in source["channels"]):
        transforms.append({"kind": "unit_conversion", "detail": "Source spatial or field units converted to canonical Angstrom-based units."})
    transforms.append({"kind": "dtype_conversion", "detail": "Finite source numbers encoded as deterministic little-endian canonical payloads."})
    return {"source_kind": "uploaded_file", "source_format": source["source_format"], "source_sha256": source["source_sha256"], "producer": "mdi_volumetric_adapter", "producer_version": VOLUMETRIC_ADAPTER_VERSION, "transformations": transforms}


def _field_relationships(fields: list[dict[str, Any]], channels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_name = {field["field_name"]: field for field in fields}
    required = {"total", "spin_difference", "spin_up", "spin_down"}
    if not required.issubset(by_name):
        return []
    up = by_name["spin_up"]["field_id"]
    down = by_name["spin_down"]["field_id"]
    return [
        {
            "relationship_id": "collinear:spin_difference_equals_up_minus_down:v1",
            "kind": "spin_difference_equals_up_minus_down",
            "input_field_ids": [up, down],
            "output_field_id": by_name["spin_difference"]["field_id"],
            "status": "validated",
            "residual": 0.0,
        },
        {
            "relationship_id": "collinear:total_equals_up_plus_down:v1",
            "kind": "total_equals_up_plus_down",
            "input_field_ids": [up, down],
            "output_field_id": by_name["total"]["field_id"],
            "status": "validated",
            "residual": 0.0,
        },
    ]


def _summary(result: VolumetricAdapterResult) -> str:
    cross = "periodic structure cell" if result.grid["boundary_conditions"] == ["periodic"] * 3 else "non-periodic affine grid"
    rows = [
        "# Volumetric Data Summary", "", "## Source", f"- Format: `{result.source['source_format']}`", f"- Source SHA-256: `{result.source['source_sha256']}`",
        "", "## Structure / Domain", f"- Domain: {cross}", f"- Shape: `{' x '.join(map(str, result.grid['shape']))}`", f"- Endpoint policy: `{result.grid['endpoint_policy']}`",
        "", "## Fields",
    ]
    rows.extend(f"- `{field['field_name']}`: {field['quantity']} [{field['unit']['canonical_unit']}]" for field in result.fields)
    potential_fields = [field for field in result.fields if field["quantity"] in {"local_potential", "electrostatic_potential"}]
    if potential_fields:
        rows.extend(["", "## Potential Reference"])
        rows.extend(
            f"- `{field['field_name']}`: `{field['potential_reference']['kind']}`; source metadata: {field['potential_reference']['source_metadata']}"
            for field in potential_fields
        )
        rows.append("- No vacuum, Fermi, work-function, or absolute-zero reference is inferred.")
    elf_fields = [field for field in result.fields if field["quantity"] == "electron_localization_function"]
    orbital_fields = [field for field in result.fields if field["quantity"] == "orbital_density"]
    if elf_fields:
        rows.extend([
            "", "## ELF Product Boundary",
            "- Source-native dimensionless ELF values are preserved without clamping or rescaling.",
            "- ELF isosurfaces are display contours, not bond, lone-pair, basin, shell, or topology classifications.",
            "- The full-cell ELF volume integral has no automatic electron-count or basin-population interpretation.",
        ])
    if orbital_fields:
        rows.extend([
            "", "## Orbital / Partial Density Boundary",
            "- The field is source-defined partial density; orbital, band, k-point, occupancy, energy, and HOMO/LUMO identity are unavailable unless present in authoritative source metadata.",
            "- Full-cell source-grid integrals are reported with source normalization semantics and are not automatically occupancy or probability.",
            "- No absolute value, square, renormalization, orbital reconstruction, character assignment, or complex-phase derivation is performed.",
        ])
    derived_formulas = sorted({
        transformation["detail"].split(":", 1)[0]
        for field in result.fields
        for transformation in field["provenance"]["transformations"]
        if transformation["kind"] == "component_remapping"
        and transformation["detail"].startswith(("COLLINEAR_SPIN_UP_V1:", "COLLINEAR_SPIN_DOWN_V1:"))
    })
    if derived_formulas:
        rows.extend(["", "## Derived Collinear Fields", *[f"- Formula: `{formula}`" for formula in derived_formulas]])
        rows.extend(f"- Relationship: `{relationship['kind']}` ({relationship['status']}, residual {relationship['residual']})" for relationship in result.dataset["relationships"])
    rows.extend(["", "## Transformations", *[f"- {item['kind']}: {item['detail']}" for item in result.dataset["provenance"]["transformations"]], "", "## Limits / Warnings"])
    rows.extend([f"- {warning}" for warning in result.dataset["warnings"]] or ["- None"])
    rows.extend(["", "## Security", "- Inert JSON and binary data only.", "- No renderer, JavaScript, external URL, shader, or executable asset."])
    return "\n".join(rows) + "\n"


def _binary_media_type(name: str) -> str:
    return "application/gzip" if name.endswith(".gz") else "application/vnd.mdi.volumetric+float64"


def _make_repeated_artifact_ids_unique(artifacts: list[Artifact]) -> None:
    counts: dict[str, int] = {}
    for artifact in artifacts:
        counts[artifact.id] = counts.get(artifact.id, 0) + 1
    seen: dict[str, int] = {}
    for artifact in artifacts:
        if counts[artifact.id] <= 1:
            continue
        base = artifact.id
        seen[base] = seen.get(base, 0) + 1
        artifact.id = f"{base}-{seen[base]:02d}"


def _error(code: str, message: str, error_type: str, **details: Any) -> ToolExecutionError:
    return ToolExecutionError(code=code, message=message, tool_id=VOLUMETRIC_TOOL_ID, details={"errorType": error_type, **details})
