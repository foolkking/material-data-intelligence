from __future__ import annotations

from dataclasses import dataclass
import importlib.metadata as metadata
from itertools import product
import math
import re
import unicodedata
import warnings
from typing import Any, Sequence

import numpy as np
from pymatgen.core import Lattice, Structure

from mdi_artifact_core import (
    ArtifactPayload,
    BRILLOUIN_CAPS,
    BRILLOUIN_TOLERANCES,
    BrillouinContractError,
    brillouin_content_hash,
    build_basis_transformation,
    build_brillouin_zone_manifest,
    build_kpath_contract,
    build_reciprocal_lattice_contract,
    bz_reciprocal_fractional_to_cartesian,
    canonicalize_brillouin_zone,
    stable_brillouin_json,
    stable_json_dumps,
    validate_brillouin_zone,
    validate_brillouin_zone_manifest,
    validate_kpath,
    validate_reciprocal_lattice,
)
from mdi_schemas import Artifact, ArtifactType

from ..context import ToolExecutionContext
from ..errors import ToolExecutionError
from .structure import _BaseStructureAdapter

try:  # pragma: no cover - dependency-present path is exercised in CI.
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
    from pymatgen.symmetry.bandstructure import HighSymmKpath
except Exception:  # pragma: no cover
    SpacegroupAnalyzer = None  # type: ignore[assignment]
    HighSymmKpath = None  # type: ignore[assignment]


BRILLOUIN_ZONE_TOOL_ID = "structure.brillouin_zone"
BRILLOUIN_ZONE_ADAPTER_VERSION = "1.0.0"
_GENERATOR_BINDING_TOLERANCE = 1e-7
_LABEL_TOKEN = re.compile(r"[^A-Z0-9]+")
_GREEK_LABELS = {
    "GAMMA": ("GAMMA", "Γ"),
    "DELTA": ("DELTA", "Δ"),
    "SIGMA": ("SIGMA", "Σ"),
    "LAMBDA": ("LAMBDA", "Λ"),
    "OMEGA": ("OMEGA", "Ω"),
}


@dataclass(frozen=True)
class PreparedBrillouinZone:
    label: str
    structure: Structure


@dataclass(frozen=True)
class BrillouinZoneResult:
    reciprocal_lattice: dict[str, Any]
    brillouin_zone: dict[str, Any]
    kpath: dict[str, Any]
    manifest: dict[str, Any]
    params: dict[str, Any]


class BrillouinZoneAdapter(_BaseStructureAdapter):
    """Generate validated inert reciprocal-lattice, BZ, and k-path artifacts."""

    tool_id = BRILLOUIN_ZONE_TOOL_ID
    adapter_version = BRILLOUIN_ZONE_ADAPTER_VERSION

    def prepare(
        self,
        context: ToolExecutionContext,
        input_refs: list[Any],
        params: dict[str, Any],
    ) -> PreparedBrillouinZone:
        if not self._resolved_inputs:
            raise self._input_error("No structure input was provided.", "resource_missing")
        raw = self._resolved_inputs[0] if len(self._resolved_inputs) == 1 else self._resolved_inputs
        structures = self._coerce_structures(raw)
        if len(structures) != 1:
            raise self._input_error(
                "Brillouin-zone generation accepts exactly one periodic structure.",
                "multiple_structures_unsupported",
                structureCount=len(structures),
            )
        label, structure = next(iter(sorted(structures.items())))
        max_atoms = int(context.resource_limits.get("maxAtomsPerStructure", 512))
        _validate_source_lattice(self, structure)
        self._validate_structure(label, structure, max_atoms=max_atoms)
        _validate_structure_scope(self, structure)
        return PreparedBrillouinZone(label=label, structure=structure.copy())

    def run(self, prepared: PreparedBrillouinZone, params: dict[str, Any]) -> BrillouinZoneResult:
        normalized = _normalize_params(params)
        if SpacegroupAnalyzer is None or HighSymmKpath is None:
            raise _error(
                "TOOL_DEPENDENCY_MISSING",
                "Brillouin-zone generation requires local pymatgen symmetry support.",
                "provider_unavailable",
            )
        structure = prepared.structure
        source_payload = structure.as_dict()
        source_hash = brillouin_content_hash(source_payload)
        source_lattice = _matrix(structure.lattice.matrix)
        provider = _provider_metadata(source_hash, normalized)
        try:
            analyzer = SpacegroupAnalyzer(
                structure,
                symprec=normalized["symmetry_tolerance_angstrom"],
                angle_tolerance=normalized["angle_tolerance_degrees"],
            )
            primitive = analyzer.get_primitive_standard_structure(
                international_monoclinic=False,
                keep_site_properties=False,
            )
            conventional = analyzer.get_conventional_standard_structure(
                international_monoclinic=False,
                keep_site_properties=False,
            )
        except Exception as exc:
            raise _error(
                "TOOL_RUNTIME_ERROR",
                "Primitive-cell standardization failed for the supplied structure.",
                "primitive_standardization_failed",
            ) from exc
        if primitive is None or len(primitive) == 0:
            raise _error(
                "TOOL_RUNTIME_ERROR",
                "Primitive-cell standardization returned no structure.",
                "primitive_standardization_failed",
            )
        primitive_lattice = _matrix(primitive.lattice.matrix)
        conventional_lattice = _matrix(conventional.lattice.matrix)
        transformations = _source_to_primitive_transform(source_lattice, primitive_lattice)
        try:
            point_specs, branches, provider_warnings = _high_symmetry_path(primitive, normalized)
            provider["warnings"] = provider_warnings
            reciprocal = build_reciprocal_lattice_contract(
                source_structure_id=f"structure:{source_hash[:24]}",
                source_structure_sha256=source_hash,
                source_real_lattice=source_lattice,
                primitive_real_lattice=primitive_lattice,
                conventional_real_lattice=conventional_lattice,
                transformations=transformations,
                provider=provider,
                ordered=True,
                partial_occupancy=False,
                magnetic=False,
            )
            zone = canonicalize_brillouin_zone(
                reciprocal,
                _wigner_seitz_faces(primitive_lattice, reciprocal["matrix"]),
                provider_method="pymatgen reciprocal Wigner Seitz",
            )
            kpath = build_kpath_contract(
                reciprocal,
                point_specs=point_specs,
                variant_specs=[
                    {
                        "variant_key": "primary",
                        "description": "Canonical Setyawan Curtarolo path",
                        "branches": branches,
                    }
                ],
                selected_variant_key="primary",
                provider=provider,
                path_convention="setyawan_curtarolo",
                time_reversal_used=True,
            )
            manifest = build_brillouin_zone_manifest(reciprocal, zone, kpath)
            reciprocal = _mark_adapter_provenance(reciprocal, geometry_generated=False)
            zone = _rebind_zone(zone, reciprocal)
            kpath = _rebind_kpath(kpath, reciprocal)
            manifest = build_brillouin_zone_manifest(reciprocal, zone, kpath)
            manifest = _mark_adapter_provenance(manifest, production_adapter_registered=True)
            _validate_package(reciprocal, zone, kpath, manifest)
        except BrillouinContractError as exc:
            raise _error(
                "TOOL_CONTRACT_INVALID",
                "Generated Brillouin-zone data failed canonical validation.",
                exc.code,
            ) from exc
        return BrillouinZoneResult(reciprocal, zone, kpath, manifest, normalized)

    def export(self, result: BrillouinZoneResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        payload_by_type = {
            ArtifactType.reciprocal_lattice_json: ("reciprocal_lattice.json", result.reciprocal_lattice),
            ArtifactType.brillouin_zone_json: ("brillouin_zone.json", result.brillouin_zone),
            ArtifactType.kpath_json: ("kpath.json", result.kpath),
            ArtifactType.brillouin_zone_manifest_json: ("brillouin_zone_manifest.json", result.manifest),
        }
        default_types = [
            *payload_by_type,
            ArtifactType.summary_md,
            ArtifactType.recipe_json,
        ]
        if artifact_types and (
            len(artifact_types) != len(default_types)
            or set(artifact_types) != set(default_types)
        ):
            raise _error(
                "TOOL_INPUT_INVALID",
                "Brillouin-zone execution requires the complete six-artifact package.",
                "artifact_request_mismatch",
            )
        requested = default_types
        payloads: list[ArtifactPayload] = []
        for artifact_type in requested:
            if artifact_type in payload_by_type:
                file_name, payload = payload_by_type[artifact_type]
                payloads.append(
                    ArtifactPayload(artifact_type, file_name, stable_brillouin_json(payload), "application/json")
                )
            elif artifact_type is ArtifactType.summary_md:
                payloads.append(
                    ArtifactPayload(artifact_type, "summary.md", _summary_markdown(result), "text/markdown")
                )
            elif artifact_type is ArtifactType.recipe_json:
                recipe = self.recipe_payload(
                    name="Brillouin Zone Data",
                    params=result.params,
                    artifact_types=requested,
                )
                recipe["scientificContract"] = {
                    "reciprocalConvention": result.reciprocal_lattice["convention"],
                    "standardization": "pymatgen SpacegroupAnalyzer primitive standard structure",
                    "geometry": "pymatgen reciprocal Wigner Seitz",
                    "kpath": "pymatgen HighSymmKpath setyawan curtarolo",
                    "deterministic": True,
                    "rendererIncluded": False,
                    "externalNetwork": False,
                }
                recipe["artifactHashes"] = {
                    "reciprocal_lattice": result.reciprocal_lattice["content_hash"],
                    "brillouin_zone": result.brillouin_zone["content_hash"],
                    "kpath": result.kpath["content_hash"],
                    "manifest": result.manifest["content_hash"],
                }
                payloads.append(
                    ArtifactPayload(artifact_type, "recipe.json", stable_json_dumps(recipe), "application/json")
                )
        return self.export_payloads(
            payloads,
            provenance={
                "contractFamily": "phase10i.brillouin_zone",
                "sourceStructureSha256": result.reciprocal_lattice["real_lattice_binding"]["source_structure_sha256"],
                "deterministic": True,
                "rendererIncluded": False,
                "externalNetwork": False,
            },
        )


def _normalize_params(params: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "include_reciprocal_lattice",
        "include_brillouin_zone",
        "include_kpath",
        "standardization",
        "kpath_provider",
        "time_reversal",
        "symmetry_tolerance_angstrom",
        "angle_tolerance_degrees",
        "include_alternative_path_variants",
    }
    unknown = sorted(set(params) - allowed)
    if unknown:
        raise _error("TOOL_PARAM_INVALID", "Unknown Brillouin-zone parameters are not accepted.", "unknown_params", unknownParams=unknown)
    normalized = {
        "include_reciprocal_lattice": params.get("include_reciprocal_lattice", True),
        "include_brillouin_zone": params.get("include_brillouin_zone", True),
        "include_kpath": params.get("include_kpath", True),
        "standardization": params.get("standardization", "contract_default"),
        "kpath_provider": params.get("kpath_provider", "contract_default"),
        "time_reversal": params.get("time_reversal", True),
        "symmetry_tolerance_angstrom": params.get(
            "symmetry_tolerance_angstrom",
            BRILLOUIN_TOLERANCES["symmetry_symprec_angstrom"],
        ),
        "angle_tolerance_degrees": params.get(
            "angle_tolerance_degrees",
            BRILLOUIN_TOLERANCES["symmetry_angle_tolerance_degrees"],
        ),
        "include_alternative_path_variants": params.get("include_alternative_path_variants", False),
    }
    if normalized["include_reciprocal_lattice"] is not True or normalized["include_brillouin_zone"] is not True or normalized["include_kpath"] is not True:
        raise _error("TOOL_PARAM_INVALID", "All canonical Brillouin-zone artifacts are required.", "required_artifact_disabled")
    if normalized["standardization"] != "contract_default" or normalized["kpath_provider"] != "contract_default":
        raise _error("TOOL_PARAM_INVALID", "Only contract-default providers are approved.", "provider_convention_mismatch")
    if normalized["time_reversal"] is not True or normalized["include_alternative_path_variants"] is not False:
        raise _error("TOOL_PARAM_INVALID", "Only the non-magnetic canonical time-reversal path is supported.", "unsupported_time_reversal_policy")
    symprec = normalized["symmetry_tolerance_angstrom"]
    angle = normalized["angle_tolerance_degrees"]
    if isinstance(symprec, bool) or not isinstance(symprec, (int, float)) or not math.isfinite(float(symprec)) or not 1e-7 <= float(symprec) <= 1.0:
        raise _error("TOOL_PARAM_INVALID", "Symmetry tolerance is outside the approved range.", "invalid_symmetry_tolerance")
    if isinstance(angle, bool) or not isinstance(angle, (int, float)) or not math.isfinite(float(angle)) or not 0.1 <= float(angle) <= 30.0:
        raise _error("TOOL_PARAM_INVALID", "Angle tolerance is outside the approved range.", "invalid_angle_tolerance")
    normalized["symmetry_tolerance_angstrom"] = float(symprec)
    normalized["angle_tolerance_degrees"] = float(angle)
    return normalized


def _validate_structure_scope(adapter: BrillouinZoneAdapter, structure: Structure) -> None:
    if not structure.is_ordered:
        raise adapter._input_error("Disordered or partially occupied structures are unsupported.", "partial_occupancy_unsupported")
    properties = getattr(structure, "properties", {}) or {}
    dimension = properties.get("periodic_dimension")
    if dimension is not None and dimension != 3:
        raise adapter._input_error("Only three-dimensional periodic structures are supported.", "unsupported_dimensionality", periodicDimension=dimension)
    if any(not math.isfinite(float(value)) for row in structure.lattice.matrix for value in row):
        raise adapter._input_error("The real-space lattice contains non-finite values.", "invalid_lattice")
    magnetic_values = structure.site_properties.get("magmom", [])
    for value in magnetic_values:
        try:
            magnitude = float(np.linalg.norm(value)) if isinstance(value, (list, tuple, np.ndarray)) else abs(float(value))
        except (TypeError, ValueError):
            raise adapter._input_error("Magnetic metadata is invalid.", "magnetic_structure_unsupported")
        if magnitude > 1e-12:
            raise adapter._input_error("Magnetic structures are outside the current k-path policy.", "magnetic_structure_unsupported")


def _validate_source_lattice(adapter: BrillouinZoneAdapter, structure: Structure) -> None:
    matrix = np.asarray(structure.lattice.matrix, dtype=float)
    if matrix.shape != (3, 3) or not np.all(np.isfinite(matrix)):
        raise adapter._input_error("The real-space lattice is invalid.", "invalid_lattice")
    scale = float(np.max(np.linalg.norm(matrix, axis=1)))
    determinant = abs(float(np.linalg.det(matrix)))
    if scale == 0 or determinant <= float(BRILLOUIN_TOLERANCES["real_lattice_determinant_relative"]) * scale**3:
        raise adapter._input_error("The real-space lattice is singular.", "singular_lattice")
    condition = float(np.linalg.cond(matrix))
    if not math.isfinite(condition) or condition > float(BRILLOUIN_TOLERANCES["real_lattice_condition_max"]):
        raise adapter._input_error("The real-space lattice is ill-conditioned.", "ill_conditioned_lattice")


def _provider_metadata(source_hash: str, params: dict[str, Any]) -> dict[str, Any]:
    try:
        version = metadata.version("pymatgen")
    except metadata.PackageNotFoundError:  # pragma: no cover
        version = "unavailable"
    return {
        "name": "pymatgen_highsymmkpath",
        "version": version,
        "convention": "setyawan_curtarolo",
        "input_structure_sha256": source_hash,
        "symprec_angstrom": params["symmetry_tolerance_angstrom"],
        "angle_tolerance_degrees": params["angle_tolerance_degrees"],
        "time_reversal_used": True,
        "standardization_status": "standardized",
        "warnings": [],
    }


def _source_to_primitive_transform(source: list[list[float]], primitive: list[list[float]]) -> list[dict[str, Any]]:
    if np.allclose(source, primitive, rtol=0.0, atol=float(BRILLOUIN_TOLERANCES["transformation_roundtrip_absolute"])):
        return []
    try:
        transform = np.asarray(primitive, dtype=float) @ np.linalg.inv(np.asarray(source, dtype=float))
    except np.linalg.LinAlgError as exc:
        raise BrillouinContractError("BZ_TRANSFORMATION_INVALID", "The source lattice transformation is singular.") from exc
    return [
        build_basis_transformation(
            transform.tolist(),
            old_basis="source_cell",
            new_basis="standardized_primitive_cell",
        )
    ]


def _wigner_seitz_faces(
    real_lattice: list[list[float]], reciprocal_matrix: Sequence[Sequence[float]]
) -> list[dict[str, Any]]:
    faces = Lattice(real_lattice).reciprocal_lattice.get_wigner_seitz_cell()
    output: list[dict[str, Any]] = []
    radius = BRILLOUIN_CAPS["max_generator_search_radius"]
    for face in faces:
        vertices = [[float(component) for component in point] for point in face]
        candidates: list[tuple[float, int, tuple[int, int, int]]] = []
        for hkl in product(range(-radius, radius + 1), repeat=3):
            if hkl == (0, 0, 0):
                continue
            generator = bz_reciprocal_fractional_to_cartesian(hkl, reciprocal_matrix)
            offset = sum(component * component for component in generator) / 2.0
            residual = max(
                abs(sum(point[index] * generator[index] for index in range(3)) - offset)
                for point in vertices
            )
            candidates.append((residual, sum(component * component for component in hkl), hkl))
        residual, _, generator_hkl = min(candidates)
        if residual > _GENERATOR_BINDING_TOLERANCE:
            raise BrillouinContractError("BZ_GENERATOR_PLANE_BINDING_FAILED", "A BZ face could not be bound to a bounded reciprocal generator.")
        output.append({"generator_hkl": list(generator_hkl), "vertices": vertices})
    return output


def _high_symmetry_path(
    primitive: Structure,
    params: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[list[str]], list[str]]:
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            provider = HighSymmKpath(
                primitive,
                path_type="setyawan_curtarolo",
                symprec=params["symmetry_tolerance_angstrom"],
                angle_tolerance=params["angle_tolerance_degrees"],
                atol=float(BRILLOUIN_TOLERANCES["label_coordinate_absolute"]),
            )
        raw = provider.kpath
        raw_points = raw["kpoints"]
        raw_branches = raw["path"]
    except Exception as exc:
        raise BrillouinContractError("BZ_KPATH_GENERATION_FAILED", "The approved k-path provider failed.") from exc
    if not isinstance(raw_points, dict) or not raw_points or not isinstance(raw_branches, list) or not raw_branches:
        raise BrillouinContractError("BZ_KPATH_GENERATION_FAILED", "The approved k-path provider returned no path.")
    label_map = {label: _normalize_label(label) for label in raw_points}
    point_specs = [
        {
            "label_key": label_map[label][0],
            "display_label": label_map[label][1],
            "aliases": [],
            "fractional_coordinates": [float(value) for value in coordinates],
        }
        for label, coordinates in sorted(raw_points.items(), key=lambda item: label_map[item[0]][0])
    ]
    branches = [[label_map[label][0] for label in branch] for branch in raw_branches]
    provider_warnings = sorted(
        {
            code
            for warning in caught
            if not issubclass(warning.category, DeprecationWarning)
            for code in [_provider_warning_code(str(warning.message))]
        }
    )
    return point_specs, branches, provider_warnings


def _provider_warning_code(message: str) -> str:
    lowered = message.lower()
    if "expected standard primitive" in lowered:
        return "BZ_PROVIDER_STANDARD_PRIMITIVE_WARNING"
    if "unexpected value" in lowered:
        return "BZ_PROVIDER_UNEXPECTED_SYMMETRY_WARNING"
    if "unknown lattice type" in lowered:
        return "BZ_PROVIDER_UNKNOWN_LATTICE_WARNING"
    if "magmom" in lowered:
        return "BZ_PROVIDER_MAGNETIC_METADATA_WARNING"
    return "BZ_PROVIDER_UNCLASSIFIED_WARNING"


def _normalize_label(value: str) -> tuple[str, str]:
    normalized = unicodedata.normalize("NFKC", str(value)).strip().strip("$")
    token = normalized.replace("\\", "").replace("{", "").replace("}", "")
    upper = token.upper()
    for greek_name, result in _GREEK_LABELS.items():
        if upper == greek_name or normalized == result[1]:
            return result
    key = _LABEL_TOKEN.sub("_", upper).strip("_")
    if not key:
        raise BrillouinContractError("BZ_LABEL_INVALID", "The provider label is empty.")
    if key[0].isdigit():
        key = f"K_{key}"
    if len(key) > 32:
        raise BrillouinContractError("BZ_LABEL_INVALID", "The provider label exceeds the canonical limit.")
    display = token if token else key
    return key, display


def _mark_adapter_provenance(payload: dict[str, Any], **extra: Any) -> dict[str, Any]:
    result = {**payload, "provenance": {**payload["provenance"]}}
    result["provenance"].update(
        {
            "producer": BRILLOUIN_ZONE_TOOL_ID,
            "producer_version": BRILLOUIN_ZONE_ADAPTER_VERSION,
            **extra,
        }
    )
    result["content_hash"] = brillouin_content_hash(result)
    return result


def _rebind_zone(zone: dict[str, Any], reciprocal: dict[str, Any]) -> dict[str, Any]:
    result = {**zone, "reciprocal_lattice_binding": {**zone["reciprocal_lattice_binding"]}}
    result["reciprocal_lattice_binding"]["reciprocal_lattice_sha256"] = reciprocal["content_hash"]
    return _mark_adapter_provenance(result)


def _rebind_kpath(kpath: dict[str, Any], reciprocal: dict[str, Any]) -> dict[str, Any]:
    result = {**kpath, "reciprocal_lattice_binding": {**kpath["reciprocal_lattice_binding"]}}
    result["reciprocal_lattice_binding"]["reciprocal_lattice_sha256"] = reciprocal["content_hash"]
    return _mark_adapter_provenance(result)


def _validate_package(
    reciprocal: dict[str, Any],
    zone: dict[str, Any],
    kpath: dict[str, Any],
    manifest: dict[str, Any],
) -> None:
    validations = (
        validate_reciprocal_lattice(reciprocal),
        validate_brillouin_zone(zone, reciprocal),
        validate_kpath(kpath, reciprocal),
        validate_brillouin_zone_manifest(manifest, reciprocal, zone, kpath),
    )
    for validation in validations:
        if not validation.valid:
            raise BrillouinContractError(validation.errors[0], "The generated artifact package is invalid.")


def _summary_markdown(result: BrillouinZoneResult) -> str:
    topology = result.brillouin_zone["topology"]
    selected = next(item for item in result.kpath["path_variants"] if item["selected"])
    binding = result.reciprocal_lattice["real_lattice_binding"]
    return (
        "# Brillouin Zone Data\n\n"
        f"- source structure: `{binding['source_structure_id']}`\n"
        f"- reciprocal convention: `{result.reciprocal_lattice['convention']}`\n"
        f"- reciprocal units: `{result.reciprocal_lattice['units']}`\n"
        f"- primitive cell volume: `{result.reciprocal_lattice['real_cell_volume']}` angstrom^3\n"
        f"- reciprocal cell volume: `{result.reciprocal_lattice['cell_volume']}` angstrom^-3\n"
        f"- BZ topology: {topology['vertex_count']} vertices, {topology['edge_count']} edges, {topology['face_count']} faces\n"
        f"- BZ volume: `{result.brillouin_zone['volume']}` angstrom^-3\n"
        f"- high-symmetry points: {len(result.kpath['points'])}\n"
        f"- selected path segments: {len(selected['segment_ids'])}\n"
        f"- provider: `{result.kpath['provider']['name']} {result.kpath['provider']['version']}`\n"
        "- preview: JSON only; renderer not included\n"
        "- external network: none\n"
        "- executable artifact content: none\n"
    )


def _matrix(value: Any) -> list[list[float]]:
    return [[float(component) for component in row] for row in value]


def _error(code: str, message: str, error_type: str, **details: Any) -> ToolExecutionError:
    return ToolExecutionError(
        code=code,
        message=message,
        tool_id=BRILLOUIN_ZONE_TOOL_ID,
        details={"errorType": error_type, **details},
    )
