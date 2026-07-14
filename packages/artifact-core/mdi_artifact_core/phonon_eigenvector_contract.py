from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

from .phonon_contract import (
    FREQUENCY_UNIT,
    IMAGINARY_FREQUENCY_ENCODING,
    PHONON_BAND_SCHEMA_VERSION,
    PHONON_MODE_REF_SCHEMA_VERSION,
    stable_phonon_json,
    validate_phonon_band,
)


PHONON_EIGENVECTOR_SCHEMA_VERSION = "phase10h.phonon_eigenvector.v1"
PHONON_EIGENVECTOR_SET_SCHEMA_VERSION = "phase10h.phonon_eigenvector_set.v1"
PHONON_EIGENVECTOR_SUMMARY_SCHEMA_VERSION = "phase10h.phonon_eigenvector_summary.v1"
PHONON_EIGENVECTOR_MANIFEST_SCHEMA_VERSION = "phase10h.phonon_eigenvector_manifest.v1"
COMPLEX_SCALAR_SCHEMA_VERSION = "phase10h.complex_scalar.v1"
COMPLEX_VECTOR3_SCHEMA_VERSION = "phase10h.complex_vector3.v1"

MODE_FREQUENCY_TOLERANCE = 1e-8
PHASE_TOLERANCE = 1e-12
NORMALIZATION_TOLERANCE = 1e-9
MAX_IMAGE_OFFSET = 16

EIGENVECTOR_CAPS = {
    "max_atoms": 512,
    "max_modes": 4096,
    "max_complex_components": 512 * 4096 * 3,
    "max_metadata_bytes": 1_000_000,
    "max_artifact_bytes": 64_000_000,
    "max_warnings": 32,
    "max_image_offset": MAX_IMAGE_OFFSET,
}

_HASH = re.compile(r"[0-9a-f]{64}")
_SAFE_ID = re.compile(r"[A-Za-z0-9_.:-]{1,128}")
_ELEMENT = re.compile(r"[A-Z][a-z]?")
_SECURITY = {
    "contains_javascript": False,
    "contains_html": False,
    "external_urls_allowed": False,
    "executable_content_allowed": False,
    "external_assets": [],
}
_FORBIDDEN_KEYS = {
    "callback", "callbacks", "code", "eval", "function", "html", "iframe",
    "module", "script", "shader", "src", "texture", "url", "urls",
    "__proto__", "constructor", "prototype",
}
_FORBIDDEN_MARKERS = (
    "http://", "https://", "javascript:", "<script", "<iframe", "eval(",
    "new function", "file://", "data:text/html",
)

_MODE_FIELDS = {
    "schema_version", "mode_id", "band_artifact", "structure_identity",
    "phonon_calculation_identity", "qpoint_index", "qpoint_coordinates",
    "qpoint_coordinate_system", "reciprocal_convention", "segment_index",
    "branch_index", "source_branch_identity", "frequency", "frequency_unit",
    "frequency_tolerance", "nac_direction", "degeneracy",
}
_EIGENVECTOR_FIELDS = {
    "schema_version", "mode", "structure_identity", "atom_count", "species",
    "atom_ordering", "coordinate_basis", "vector_unit", "atomic_masses",
    "stored_vector_representation", "normalization", "eigenvectors",
    "phase_convention", "provenance", "warnings", "security",
}


@dataclass(frozen=True)
class EigenvectorValidationResult:
    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...] = ()
    atom_count: int = 0
    mode_count: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "atom_count": self.atom_count,
            "mode_count": self.mode_count,
        }


class PhononEigenvectorContractError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def eigenvector_content_hash(value: Any) -> str:
    return hashlib.sha256(stable_phonon_json(value).encode("utf-8")).hexdigest()


def phonon_calculation_identity(band: dict[str, Any]) -> str:
    source = band.get("source") if isinstance(band.get("source"), dict) else {}
    payload = {
        "structure_identity": band.get("structure_identity"),
        "input_sha256": source.get("input_sha256"),
        "calculation_method": source.get("calculation_method"),
        "force_constants_source": source.get("force_constants_source"),
        "primitive_matrix": source.get("primitive_matrix"),
        "supercell_matrix": source.get("supercell_matrix"),
        "nac": source.get("nac"),
    }
    return eigenvector_content_hash(payload)


def build_phonon_mode_ref(
    band: dict[str, Any],
    *,
    artifact_id: str,
    artifact_sha256: str | None = None,
    qpoint_index: int,
    branch_index: int,
) -> dict[str, Any]:
    result = validate_phonon_band(band)
    if not result.valid:
        raise PhononEigenvectorContractError("PHONON_MODE_BAND_INVALID", "The source band artifact is invalid.")
    if _SAFE_ID.fullmatch(artifact_id) is None:
        raise PhononEigenvectorContractError("PHONON_MODE_ARTIFACT_INVALID", "The band artifact id is invalid.")
    digest = eigenvector_content_hash(band)
    if artifact_sha256 is not None and artifact_sha256 != digest:
        raise PhononEigenvectorContractError("PHONON_MODE_REFERENCE_STALE", "The band artifact hash is stale.")
    if not _index(qpoint_index, len(band["qpoints"])) or not _index(branch_index, len(band["branches"])):
        raise PhononEigenvectorContractError("PHONON_MODE_REFERENCE_INVALID", "The q-point or branch index is invalid.")
    qpoint = band["qpoints"][qpoint_index]
    branch = band["branches"][branch_index]
    frequency = float(branch["frequencies"][qpoint_index])
    source = band["source"]
    nac = source["nac"]
    direction = nac["gamma_direction"] if nac["enabled"] and _near_zero_triplet(qpoint["coordinates"]) else None
    group = next(
        (
            item for item in band.get("degeneracy_groups", [])
            if item.get("qpoint_index") == qpoint_index and branch_index in item.get("branch_indices", [])
        ),
        None,
    )
    degeneracy = None if group is None else {
        "group_id": f"q{qpoint_index}-branches-{'-'.join(str(value) for value in group['branch_indices'])}",
        "branch_indices": list(group["branch_indices"]),
        "source_declared": True,
        "basis_arbitrary_within_subspace": True,
    }
    identity = {
        "band_artifact_sha256": digest,
        "qpoint_index": qpoint_index,
        "branch_index": branch_index,
        "nac_direction": direction,
    }
    return {
        "schema_version": PHONON_MODE_REF_SCHEMA_VERSION,
        "mode_id": eigenvector_content_hash(identity),
        "band_artifact": {
            "artifact_id": artifact_id,
            "schema_version": PHONON_BAND_SCHEMA_VERSION,
            "sha256": digest,
        },
        "structure_identity": band["structure_identity"],
        "phonon_calculation_identity": phonon_calculation_identity(band),
        "qpoint_index": qpoint_index,
        "qpoint_coordinates": list(qpoint["coordinates"]),
        "qpoint_coordinate_system": band["qpoint_coordinate_system"],
        "reciprocal_convention": band["reciprocal_convention"],
        "segment_index": qpoint["segment_index"],
        "branch_index": branch_index,
        "source_branch_identity": f"source-branch-{branch_index}",
        "frequency": frequency,
        "frequency_unit": band["frequency_unit"],
        "frequency_tolerance": MODE_FREQUENCY_TOLERANCE,
        "nac_direction": None if direction is None else list(direction),
        "degeneracy": degeneracy,
    }


def validate_phonon_mode_ref(value: Any, band: dict[str, Any] | None = None) -> EigenvectorValidationResult:
    errors: set[str] = set()
    if not isinstance(value, dict) or set(value) != _MODE_FIELDS or value.get("schema_version") != PHONON_MODE_REF_SCHEMA_VERSION:
        return _result({"PHONON_EIGENVECTOR_SCHEMA_UNSUPPORTED"})
    artifact = value.get("band_artifact")
    if (
        not isinstance(artifact, dict)
        or set(artifact) != {"artifact_id", "schema_version", "sha256"}
        or _SAFE_ID.fullmatch(str(artifact.get("artifact_id", ""))) is None
        or artifact.get("schema_version") != PHONON_BAND_SCHEMA_VERSION
        or not _sha(artifact.get("sha256"))
    ):
        errors.add("PHONON_MODE_ARTIFACT_INVALID")
    if not _sha(value.get("mode_id")) or not _sha(value.get("structure_identity")) or not _sha(value.get("phonon_calculation_identity")):
        errors.add("PHONON_MODE_REFERENCE_INVALID")
    if not _nonnegative_int(value.get("qpoint_index")) or not _nonnegative_int(value.get("branch_index")):
        errors.add("PHONON_MODE_REFERENCE_INVALID")
    if not _triplet(value.get("qpoint_coordinates")) or value.get("qpoint_coordinate_system") != "reciprocal_fractional" or value.get("reciprocal_convention") != "physics_2pi":
        errors.add("PHONON_MODE_QPOINT_MISMATCH")
    if not _nonnegative_int(value.get("segment_index")) or not isinstance(value.get("source_branch_identity"), str):
        errors.add("PHONON_MODE_REFERENCE_INVALID")
    if not _finite(value.get("frequency")) or value.get("frequency_unit") != FREQUENCY_UNIT or value.get("frequency_tolerance") != MODE_FREQUENCY_TOLERANCE:
        errors.add("PHONON_MODE_FREQUENCY_MISMATCH")
    if value.get("nac_direction") is not None and not _triplet(value.get("nac_direction")):
        errors.add("PHONON_EIGENVECTOR_NAC_DIRECTION_MISMATCH")
    _validate_degeneracy(value.get("degeneracy"), int(value.get("branch_index", -1)), errors)
    _scan_inert(value, errors)
    if band is not None and not errors:
        try:
            expected = build_phonon_mode_ref(
                band,
                artifact_id=artifact["artifact_id"],
                artifact_sha256=artifact["sha256"],
                qpoint_index=value["qpoint_index"],
                branch_index=value["branch_index"],
            )
            if value != expected:
                if value.get("frequency") != expected.get("frequency"):
                    errors.add("PHONON_MODE_FREQUENCY_MISMATCH")
                elif value.get("qpoint_coordinates") != expected.get("qpoint_coordinates"):
                    errors.add("PHONON_MODE_QPOINT_MISMATCH")
                elif value.get("nac_direction") != expected.get("nac_direction"):
                    errors.add("PHONON_EIGENVECTOR_NAC_DIRECTION_MISMATCH")
                else:
                    errors.add("PHONON_MODE_REFERENCE_STALE")
        except PhononEigenvectorContractError as exc:
            errors.add(exc.code)
    return _result(errors)


def canonicalize_global_phase(vectors: Sequence[Sequence[complex]], tolerance: float = PHASE_TOLERANCE) -> list[list[complex]]:
    normalized = _complex_vectors(vectors)
    pivot = next((value for vector in normalized for value in vector if abs(value) > tolerance), None)
    if pivot is None:
        raise PhononEigenvectorContractError("PHONON_EIGENVECTOR_ZERO_NORM", "The eigenvector has zero norm.")
    rotation = complex(math.cos(-math.atan2(pivot.imag, pivot.real)), math.sin(-math.atan2(pivot.imag, pivot.real)))
    result = [[_snap(value * rotation, tolerance) for value in vector] for vector in normalized]
    first = next(value for vector in result for value in vector if abs(value) > tolerance)
    if first.real < 0:
        result = [[-value for value in vector] for vector in result]
    return result


def normalize_mass_weighted_eigenvector(vectors: Sequence[Sequence[complex]]) -> list[list[complex]]:
    values = _complex_vectors(vectors)
    norm = math.sqrt(sum(abs(value) ** 2 for vector in values for value in vector))
    if not math.isfinite(norm) or norm <= PHASE_TOLERANCE:
        raise PhononEigenvectorContractError("PHONON_EIGENVECTOR_ZERO_NORM", "The eigenvector has zero norm.")
    return canonicalize_global_phase([[value / norm for value in vector] for vector in values])


def build_phonon_eigenvector(
    band: dict[str, Any],
    mode: dict[str, Any],
    vectors: Sequence[Sequence[complex]],
    atomic_masses: Sequence[float],
    *,
    mass_source: str = "source_provided",
    mass_reference: str = "source-artifact",
) -> dict[str, Any]:
    mode_result = validate_phonon_mode_ref(mode, band)
    if not mode_result.valid:
        raise PhononEigenvectorContractError(mode_result.errors[0], "The mode reference is invalid.")
    atom_count = int(band["atom_count"])
    if len(vectors) != atom_count or len(atomic_masses) != atom_count:
        raise PhononEigenvectorContractError("PHONON_EIGENVECTOR_SHAPE_INVALID", "The eigenvector atom shape is invalid.")
    masses = [float(value) for value in atomic_masses]
    if any(not math.isfinite(value) or value <= 0 for value in masses):
        raise PhononEigenvectorContractError("PHONON_EIGENVECTOR_MASS_INVALID", "Atomic masses must be positive and finite.")
    if mass_source not in {"source_provided", "canonical_structure_mass", "standard_atomic_weight", "isotope_specific"}:
        raise PhononEigenvectorContractError("PHONON_EIGENVECTOR_MASS_INVALID", "Atomic mass source is unsupported.")
    canonical = normalize_mass_weighted_eigenvector(vectors)
    records = [
        {
            "atom_index": index,
            "real": [_number(component.real) for component in vector],
            "imag": [_number(component.imag) for component in vector],
        }
        for index, vector in enumerate(canonical)
    ]
    imaginary = float(mode["frequency"]) < -float(band["frequency_zero_tolerance"])
    return {
        "schema_version": PHONON_EIGENVECTOR_SCHEMA_VERSION,
        "mode": mode,
        "structure_identity": band["structure_identity"],
        "atom_count": atom_count,
        "species": list(band["species"]),
        "atom_ordering": "canonical_structure_order",
        "coordinate_basis": "cartesian",
        "vector_unit": "dimensionless",
        "atomic_masses": {
            "values": masses,
            "unit": "unified_atomic_mass_unit",
            "source": mass_source,
            "reference": mass_reference,
        },
        "stored_vector_representation": "mass_weighted_eigenvector",
        "normalization": {
            "type": "euclidean_unit_norm",
            "tolerance": NORMALIZATION_TOLERANCE,
            "unweighting_formula": "u_i=e_i/sqrt(m_i)",
        },
        "eigenvectors": records,
        "phase_convention": {
            "global_phase_policy": "first_nonzero_component_real_positive",
            "component_order": "atom_major_xyz",
            "tolerance": PHASE_TOLERANCE,
            "canonicalized": True,
        },
        "provenance": {
            "source_phase_preserved": False,
            "canonical_global_phase": True,
            "partial_occupancy": False,
            "imaginary_mode": imaginary,
            "imaginary_mode_behavior": "static_unstable_direction" if imaginary else "harmonic_mode",
            "display_amplitude_policy": "max_atom_displacement",
            "display_only": True,
            "deterministic": True,
        },
        "warnings": ["PHONON_EIGENVECTOR_IMAGINARY_MODE_STATIC_ONLY"] if imaginary else [],
        "security": dict(_SECURITY),
    }


def validate_phonon_eigenvector(value: Any, band: dict[str, Any] | None = None) -> EigenvectorValidationResult:
    errors: set[str] = set()
    if not isinstance(value, dict) or set(value) != _EIGENVECTOR_FIELDS or value.get("schema_version") != PHONON_EIGENVECTOR_SCHEMA_VERSION:
        return _result({"PHONON_EIGENVECTOR_SCHEMA_UNSUPPORTED"})
    mode = value.get("mode")
    mode_result = validate_phonon_mode_ref(mode, band)
    errors.update(mode_result.errors)
    atom_count = value.get("atom_count") if _positive_int(value.get("atom_count")) else 0
    if atom_count < 1 or atom_count > EIGENVECTOR_CAPS["max_atoms"]:
        errors.add("PHONON_EIGENVECTOR_CAP_EXCEEDED")
    species = value.get("species") if isinstance(value.get("species"), list) else []
    if len(species) != atom_count or any(not isinstance(item, str) or _ELEMENT.fullmatch(item) is None for item in species):
        errors.add("PHONON_EIGENVECTOR_ATOM_ORDER_MISMATCH")
    if value.get("structure_identity") != (mode.get("structure_identity") if isinstance(mode, dict) else None) or value.get("atom_ordering") != "canonical_structure_order":
        errors.add("PHONON_EIGENVECTOR_STRUCTURE_MISMATCH")
    if value.get("coordinate_basis") != "cartesian" or value.get("vector_unit") != "dimensionless" or value.get("stored_vector_representation") != "mass_weighted_eigenvector":
        errors.add("PHONON_EIGENVECTOR_COORDINATE_BASIS_UNSUPPORTED")
    masses = value.get("atomic_masses")
    if not _valid_masses(masses, atom_count):
        errors.add("PHONON_EIGENVECTOR_MASS_INVALID")
    normalization = value.get("normalization")
    if normalization != {"type": "euclidean_unit_norm", "tolerance": NORMALIZATION_TOLERANCE, "unweighting_formula": "u_i=e_i/sqrt(m_i)"}:
        errors.add("PHONON_EIGENVECTOR_NORMALIZATION_INVALID")
    phase = value.get("phase_convention")
    if phase != {"global_phase_policy": "first_nonzero_component_real_positive", "component_order": "atom_major_xyz", "tolerance": PHASE_TOLERANCE, "canonicalized": True}:
        errors.add("PHONON_EIGENVECTOR_PHASE_INVALID")
    vectors = value.get("eigenvectors") if isinstance(value.get("eigenvectors"), list) else []
    parsed: list[list[complex]] = []
    if len(vectors) != atom_count:
        errors.add("PHONON_EIGENVECTOR_SHAPE_INVALID")
    else:
        for index, record in enumerate(vectors):
            if not isinstance(record, dict) or set(record) != {"atom_index", "real", "imag"} or record.get("atom_index") != index or not _triplet(record.get("real")) or not _triplet(record.get("imag")):
                errors.add("PHONON_EIGENVECTOR_SHAPE_INVALID")
                continue
            parsed.append([complex(float(real), float(imag)) for real, imag in zip(record["real"], record["imag"], strict=True)])
    if parsed:
        norm = sum(abs(component) ** 2 for vector in parsed for component in vector)
        if abs(norm - 1.0) > NORMALIZATION_TOLERANCE:
            errors.add("PHONON_EIGENVECTOR_NORMALIZATION_INVALID")
        pivot = next((component for vector in parsed for component in vector if abs(component) > PHASE_TOLERANCE), None)
        if pivot is None:
            errors.add("PHONON_EIGENVECTOR_ZERO_NORM")
        elif abs(pivot.imag) > PHASE_TOLERANCE or pivot.real < 0:
            errors.add("PHONON_EIGENVECTOR_PHASE_INVALID")
    provenance = value.get("provenance")
    if (
        not isinstance(provenance, dict)
        or set(provenance) != {"source_phase_preserved", "canonical_global_phase", "partial_occupancy", "imaginary_mode", "imaginary_mode_behavior", "display_amplitude_policy", "display_only", "deterministic"}
        or provenance.get("source_phase_preserved") is not False
        or provenance.get("canonical_global_phase") is not True
        or provenance.get("partial_occupancy") is not False
        or provenance.get("display_amplitude_policy") != "max_atom_displacement"
        or provenance.get("display_only") is not True
        or provenance.get("deterministic") is not True
    ):
        errors.add("PHONON_EIGENVECTOR_PROVENANCE_INVALID")
    warnings = value.get("warnings") if isinstance(value.get("warnings"), list) else []
    allowed_warnings = {"PHONON_EIGENVECTOR_IMAGINARY_MODE_STATIC_ONLY"}
    if len(warnings) > EIGENVECTOR_CAPS["max_warnings"] or any(item not in allowed_warnings for item in warnings) or warnings != sorted(set(warnings)):
        errors.add("PHONON_EIGENVECTOR_METADATA_INVALID")
    if value.get("security") != _SECURITY:
        errors.add("PHONON_EIGENVECTOR_EXTERNAL_REFERENCE_FORBIDDEN")
    if band is not None and isinstance(mode, dict):
        if value.get("structure_identity") != band.get("structure_identity") or atom_count != band.get("atom_count") or species != band.get("species"):
            errors.add("PHONON_EIGENVECTOR_ATOM_ORDER_MISMATCH")
    _scan_inert(value, errors)
    if len(stable_phonon_json(value).encode("utf-8")) > EIGENVECTOR_CAPS["max_artifact_bytes"]:
        errors.add("PHONON_EIGENVECTOR_CAP_EXCEEDED")
    return _result(errors, atom_count=atom_count, mode_count=1)


def scientific_phase_equivalent(left: dict[str, Any], right: dict[str, Any], tolerance: float = 1e-9) -> bool:
    left_vectors = _records_to_complex(left.get("eigenvectors"))
    right_vectors = _records_to_complex(right.get("eigenvectors"))
    if not left_vectors or len(left_vectors) != len(right_vectors):
        return False
    a = [value for vector in left_vectors for value in vector]
    b = [value for vector in right_vectors for value in vector]
    overlap = sum(x.conjugate() * y for x, y in zip(a, b, strict=True))
    if abs(overlap) <= tolerance:
        return False
    phase = overlap.conjugate() / abs(overlap)
    return max(abs(x - y * phase) for x, y in zip(a, b, strict=True)) <= tolerance


def mass_unweighted_vectors(value: dict[str, Any]) -> list[list[complex]]:
    vectors = _records_to_complex(value.get("eigenvectors"))
    masses = value.get("atomic_masses", {}).get("values", [])
    if len(vectors) != len(masses) or any(not _finite(mass) or mass <= 0 for mass in masses):
        raise PhononEigenvectorContractError("PHONON_EIGENVECTOR_MASS_INVALID", "Mass unweighting requires positive masses.")
    return [[component / math.sqrt(float(mass)) for component in vector] for vector, mass in zip(vectors, masses, strict=True)]


def reconstruct_display_displacements(
    value: dict[str, Any],
    *,
    cell_image: Sequence[int] = (0, 0, 0),
    phase_radians: float = 0.0,
    amplitude_angstrom: float = 0.1,
) -> list[list[float]]:
    if not _image_offset(cell_image) or not _finite(phase_radians) or not _finite(amplitude_angstrom) or amplitude_angstrom < 0 or amplitude_angstrom > 10:
        raise PhononEigenvectorContractError("PHONON_DISPLACEMENT_REQUEST_INVALID", "Display reconstruction inputs are invalid.")
    mode = value.get("mode") if isinstance(value.get("mode"), dict) else {}
    qpoint = mode.get("qpoint_coordinates")
    if not _triplet(qpoint):
        raise PhononEigenvectorContractError("PHONON_MODE_QPOINT_MISMATCH", "The q-point is invalid.")
    spatial_phase = 2.0 * math.pi * sum(float(qpoint[index]) * int(cell_image[index]) for index in range(3))
    rotation = complex(math.cos(spatial_phase + phase_radians), math.sin(spatial_phase + phase_radians))
    raw = [[(component * rotation).real for component in vector] for vector in mass_unweighted_vectors(value)]
    maximum = max((math.sqrt(sum(component * component for component in vector)) for vector in raw), default=0.0)
    if maximum <= PHASE_TOLERANCE:
        raise PhononEigenvectorContractError("PHONON_DISPLACEMENT_DEGENERATE", "The selected phase has zero display displacement.")
    return [[_number(amplitude_angstrom * component / maximum) for component in vector] for vector in raw]


def build_phonon_eigenvector_set(modes: Sequence[dict[str, Any]], *, scope: str = "subset") -> dict[str, Any]:
    if not modes or len(modes) > EIGENVECTOR_CAPS["max_modes"] or scope not in {"subset", "full"}:
        raise PhononEigenvectorContractError("PHONON_EIGENVECTOR_CAP_EXCEEDED", "The eigenvector set is invalid or over cap.")
    ordered = sorted(modes, key=lambda item: (item["mode"]["qpoint_index"], item["mode"]["branch_index"]))
    if len({item["mode"]["mode_id"] for item in ordered}) != len(ordered):
        raise PhononEigenvectorContractError("PHONON_EIGENVECTOR_DUPLICATE_MODE", "Duplicate modes are not allowed.")
    return {
        "schema_version": PHONON_EIGENVECTOR_SET_SCHEMA_VERSION,
        "structure_identity": ordered[0]["structure_identity"],
        "band_artifact": ordered[0]["mode"]["band_artifact"],
        "set_scope": scope,
        "mode_count": len(ordered),
        "ordering": "qpoint_then_branch",
        "modes": ordered,
        "security": dict(_SECURITY),
    }


def validate_phonon_eigenvector_set(value: Any, band: dict[str, Any] | None = None) -> EigenvectorValidationResult:
    errors: set[str] = set()
    fields = {"schema_version", "structure_identity", "band_artifact", "set_scope", "mode_count", "ordering", "modes", "security"}
    if not isinstance(value, dict) or set(value) != fields or value.get("schema_version") != PHONON_EIGENVECTOR_SET_SCHEMA_VERSION:
        return _result({"PHONON_EIGENVECTOR_SCHEMA_UNSUPPORTED"})
    modes = value.get("modes") if isinstance(value.get("modes"), list) else []
    if not modes or len(modes) > EIGENVECTOR_CAPS["max_modes"] or value.get("mode_count") != len(modes):
        errors.add("PHONON_EIGENVECTOR_CAP_EXCEEDED")
    if value.get("set_scope") not in {"subset", "full"} or value.get("ordering") != "qpoint_then_branch" or value.get("security") != _SECURITY:
        errors.add("PHONON_EIGENVECTOR_SCHEMA_UNSUPPORTED")
    identities: list[tuple[int, int]] = []
    for mode in modes:
        result = validate_phonon_eigenvector(mode, band)
        errors.update(result.errors)
        if isinstance(mode, dict) and isinstance(mode.get("mode"), dict):
            identities.append((mode["mode"]["qpoint_index"], mode["mode"]["branch_index"]))
            if mode.get("structure_identity") != value.get("structure_identity") or mode["mode"].get("band_artifact") != value.get("band_artifact"):
                errors.add("PHONON_EIGENVECTOR_STRUCTURE_MISMATCH")
    if identities != sorted(identities) or len(set(identities)) != len(identities):
        errors.add("PHONON_EIGENVECTOR_ORDER_INVALID")
    _scan_inert(value, errors)
    return _result(errors, atom_count=int(modes[0].get("atom_count", 0)) if modes and isinstance(modes[0], dict) else 0, mode_count=len(modes))


def phonon_eigenvector_summary(value: dict[str, Any]) -> dict[str, Any]:
    result = validate_phonon_eigenvector_set(value)
    if not result.valid:
        raise PhononEigenvectorContractError(result.errors[0], "The eigenvector set is invalid.")
    modes = value["modes"]
    return {
        "schema_version": PHONON_EIGENVECTOR_SUMMARY_SCHEMA_VERSION,
        "structure_identity": value["structure_identity"],
        "mode_count": len(modes),
        "atom_count": modes[0]["atom_count"],
        "qpoint_count": len({item["mode"]["qpoint_index"] for item in modes}),
        "imaginary_mode_count": sum(bool(item["provenance"]["imaginary_mode"]) for item in modes),
        "normalization": "mass_weighted_eigenvector/euclidean_unit_norm",
        "phase_policy": "first_nonzero_component_real_positive",
        "set_scope": value["set_scope"],
        "warnings": sorted({warning for item in modes for warning in item["warnings"]}),
    }


def validate_phonon_eigenvector_summary(value: Any) -> EigenvectorValidationResult:
    fields = {"schema_version", "structure_identity", "mode_count", "atom_count", "qpoint_count", "imaginary_mode_count", "normalization", "phase_policy", "set_scope", "warnings"}
    errors: set[str] = set()
    if not isinstance(value, dict) or set(value) != fields or value.get("schema_version") != PHONON_EIGENVECTOR_SUMMARY_SCHEMA_VERSION:
        return _result({"PHONON_EIGENVECTOR_SCHEMA_UNSUPPORTED"})
    if not _sha(value.get("structure_identity")) or not _positive_int(value.get("mode_count")) or not _positive_int(value.get("atom_count")) or not _positive_int(value.get("qpoint_count")):
        errors.add("PHONON_EIGENVECTOR_SUMMARY_INVALID")
    if not _nonnegative_int(value.get("imaginary_mode_count")) or value["imaginary_mode_count"] > value.get("mode_count", 0):
        errors.add("PHONON_EIGENVECTOR_SUMMARY_INVALID")
    if value.get("normalization") != "mass_weighted_eigenvector/euclidean_unit_norm" or value.get("phase_policy") != "first_nonzero_component_real_positive" or value.get("set_scope") not in {"subset", "full"}:
        errors.add("PHONON_EIGENVECTOR_SUMMARY_INVALID")
    _scan_inert(value, errors)
    return _result(errors, atom_count=int(value.get("atom_count", 0) or 0), mode_count=int(value.get("mode_count", 0) or 0))


def phonon_eigenvector_manifest(eigenvector_set: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": PHONON_EIGENVECTOR_MANIFEST_SCHEMA_VERSION,
        "structure_identity": eigenvector_set["structure_identity"],
        "band_artifact": eigenvector_set["band_artifact"],
        "artifacts": [
            {"name": "phonon_eigenvectors.json", "schema_version": PHONON_EIGENVECTOR_SET_SCHEMA_VERSION, "sha256": eigenvector_content_hash(eigenvector_set)},
            {"name": "phonon_eigenvector_summary.json", "schema_version": PHONON_EIGENVECTOR_SUMMARY_SCHEMA_VERSION, "sha256": eigenvector_content_hash(summary)},
        ],
        "security": dict(_SECURITY),
    }


def validate_phonon_eigenvector_manifest(value: Any) -> EigenvectorValidationResult:
    fields = {"schema_version", "structure_identity", "band_artifact", "artifacts", "security"}
    errors: set[str] = set()
    if not isinstance(value, dict) or set(value) != fields or value.get("schema_version") != PHONON_EIGENVECTOR_MANIFEST_SCHEMA_VERSION:
        return _result({"PHONON_EIGENVECTOR_SCHEMA_UNSUPPORTED"})
    artifacts = value.get("artifacts") if isinstance(value.get("artifacts"), list) else []
    expected = [("phonon_eigenvectors.json", PHONON_EIGENVECTOR_SET_SCHEMA_VERSION), ("phonon_eigenvector_summary.json", PHONON_EIGENVECTOR_SUMMARY_SCHEMA_VERSION)]
    if len(artifacts) != 2:
        errors.add("PHONON_EIGENVECTOR_MANIFEST_INVALID")
    else:
        for artifact, (name, schema) in zip(artifacts, expected, strict=True):
            if not isinstance(artifact, dict) or set(artifact) != {"name", "schema_version", "sha256"} or artifact.get("name") != name or artifact.get("schema_version") != schema or not _sha(artifact.get("sha256")):
                errors.add("PHONON_EIGENVECTOR_MANIFEST_INVALID")
    if value.get("security") != _SECURITY or not _sha(value.get("structure_identity")):
        errors.add("PHONON_EIGENVECTOR_MANIFEST_INVALID")
    _scan_inert(value, errors)
    return _result(errors)


def phonon_eigenvector_schema_snapshots() -> dict[str, Any]:
    return {
        "complex_scalar": {"schema_version": COMPLEX_SCALAR_SCHEMA_VERSION, "fields": ["real", "imag"]},
        "complex_vector3": {"schema_version": COMPLEX_VECTOR3_SCHEMA_VERSION, "fields": ["real[3]", "imag[3]"]},
        "mode_ref": {"schema_version": PHONON_MODE_REF_SCHEMA_VERSION, "fields": sorted(_MODE_FIELDS)},
        "eigenvector": {"schema_version": PHONON_EIGENVECTOR_SCHEMA_VERSION, "fields": sorted(_EIGENVECTOR_FIELDS)},
        "eigenvector_set": {"schema_version": PHONON_EIGENVECTOR_SET_SCHEMA_VERSION, "ordering": "qpoint_then_branch"},
        "summary": {"schema_version": PHONON_EIGENVECTOR_SUMMARY_SCHEMA_VERSION},
        "manifest": {"schema_version": PHONON_EIGENVECTOR_MANIFEST_SCHEMA_VERSION},
    }


def _validate_degeneracy(value: Any, branch_index: int, errors: set[str]) -> None:
    if value is None:
        return
    if not isinstance(value, dict) or set(value) != {"group_id", "branch_indices", "source_declared", "basis_arbitrary_within_subspace"}:
        errors.add("PHONON_EIGENVECTOR_DEGENERACY_INVALID")
        return
    indices = value.get("branch_indices")
    if _SAFE_ID.fullmatch(str(value.get("group_id", ""))) is None or not isinstance(indices, list) or len(indices) < 2 or indices != sorted(set(indices)) or branch_index not in indices or any(not _nonnegative_int(item) for item in indices) or value.get("source_declared") is not True or value.get("basis_arbitrary_within_subspace") is not True:
        errors.add("PHONON_EIGENVECTOR_DEGENERACY_INVALID")


def _valid_masses(value: Any, atom_count: int) -> bool:
    if not isinstance(value, dict) or set(value) != {"values", "unit", "source", "reference"}:
        return False
    masses = value.get("values")
    return (
        isinstance(masses, list)
        and len(masses) == atom_count
        and all(_finite(item) and item > 0 for item in masses)
        and value.get("unit") == "unified_atomic_mass_unit"
        and value.get("source") in {"source_provided", "canonical_structure_mass", "standard_atomic_weight", "isotope_specific"}
        and isinstance(value.get("reference"), str)
        and 0 < len(value["reference"]) <= 128
    )


def _records_to_complex(records: Any) -> list[list[complex]]:
    if not isinstance(records, list):
        return []
    result: list[list[complex]] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict) or record.get("atom_index") != index or not _triplet(record.get("real")) or not _triplet(record.get("imag")):
            return []
        result.append([complex(float(real), float(imag)) for real, imag in zip(record["real"], record["imag"], strict=True)])
    return result


def _complex_vectors(vectors: Sequence[Sequence[complex]]) -> list[list[complex]]:
    result: list[list[complex]] = []
    for vector in vectors:
        if len(vector) != 3:
            raise PhononEigenvectorContractError("PHONON_EIGENVECTOR_SHAPE_INVALID", "Each atom vector must have three components.")
        converted = [complex(value) for value in vector]
        if any(not math.isfinite(value.real) or not math.isfinite(value.imag) for value in converted):
            raise PhononEigenvectorContractError("PHONON_EIGENVECTOR_NONFINITE", "Complex components must be finite.")
        result.append(converted)
    return result


def _scan_inert(root: Any, errors: set[str]) -> None:
    queue: list[tuple[str, Any, int]] = [("", root, 0)]
    visited = 0
    while queue:
        key, value, depth = queue.pop()
        visited += 1
        if visited > 5_000_000 or depth > 14:
            errors.add("PHONON_EIGENVECTOR_CAP_EXCEEDED")
            return
        if key.lower() in _FORBIDDEN_KEYS:
            errors.add("PHONON_EIGENVECTOR_EXTERNAL_REFERENCE_FORBIDDEN")
        if isinstance(value, str):
            lowered = value.lower()
            if any(marker in lowered for marker in _FORBIDDEN_MARKERS) or re.match(r"^[A-Za-z]:[\\/]", value) or re.match(r"^/(home|users|root|etc)/", value, re.I):
                errors.add("PHONON_EIGENVECTOR_EXTERNAL_REFERENCE_FORBIDDEN")
        elif isinstance(value, list):
            queue.extend((key, item, depth + 1) for item in value)
        elif isinstance(value, dict):
            queue.extend((str(child_key), item, depth + 1) for child_key, item in value.items())


def _result(errors: Iterable[str], *, atom_count: int = 0, mode_count: int = 0, warnings: Iterable[str] = ()) -> EigenvectorValidationResult:
    error_set = set(errors)
    warning_set = set(warnings)
    return EigenvectorValidationResult(not error_set, tuple(sorted(error_set)), tuple(sorted(warning_set)), atom_count, mode_count)


def _snap(value: complex, tolerance: float) -> complex:
    real = 0.0 if abs(value.real) <= tolerance else value.real
    imag = 0.0 if abs(value.imag) <= tolerance else value.imag
    return complex(real, imag)


def _number(value: float) -> float:
    return 0.0 if abs(value) <= 1e-15 else float(value)


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) and abs(float(value)) <= 1e12


def _triplet(value: Any) -> bool:
    return isinstance(value, list) and len(value) == 3 and all(_finite(item) for item in value)


def _sha(value: Any) -> bool:
    return isinstance(value, str) and _HASH.fullmatch(value) is not None


def _nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _positive_int(value: Any) -> bool:
    return _nonnegative_int(value) and value > 0


def _index(value: Any, length: int) -> bool:
    return _nonnegative_int(value) and value < length


def _near_zero_triplet(value: Any) -> bool:
    return _triplet(value) and all(abs(float(item)) <= 1e-12 for item in value)


def _image_offset(value: Sequence[int]) -> bool:
    return len(value) == 3 and all(isinstance(item, int) and not isinstance(item, bool) and abs(item) <= MAX_IMAGE_OFFSET for item in value)
