"""Read-only, bounded structure display; never a persisted analysis result.

The coordinate payload and its checksum remain unchanged. This projection
uses the same radius-neighbor kernel as the registered structure viewer tool.
Long scientific analyses continue to run through the asynchronous job path.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
import math
from typing import Any

from ase.data import atomic_numbers
from jsonschema import Draft202012Validator
from pymatgen.core import Composition

from mdi_adapters.platform_builtin.structure_neighbors import (
    COVALENT_RADIUS_REFERENCE, COVALENT_RADIUS_SCALE, MAX_PREVIEW_SITES,
    NeighborPreviewLimit, covalent_radius_neighbors, element_covalent_radius,
)
from mdi_artifact_core import DEFAULT_VIEWER_SCENE_CAPS, VIEWER_SCENE_V2_CAPABILITIES, stable_json_dumps, validate_viewer_scene
from mdi_tool_registry import get_tool_by_id


PREVIEW_VERSION = "source_structure_preview/1.0"
_PARAMETERS = {"include_bonds": True, "bond_method": "covalent_radii"}


@dataclass(frozen=True)
class SourceStructurePreview:
    scene: dict[str, Any] | None
    issue: str | None = None


@lru_cache(maxsize=1)
def _validate_preview_parameters() -> None:
    tool = get_tool_by_id("structure.viewer_3d")
    Draft202012Validator(tool.paramsSchema).validate(_PARAMETERS)


def source_structure_preview(
    payload: Any, *, object_type: str, object_id: str, source_hash: str,
    dataset_id: str | None = None, version_id: str | None = None,
) -> SourceStructurePreview:
    if object_type not in {"Structure", "Atoms", "structure.crystal", "structure.atomic"}:
        return SourceStructurePreview(None)
    if not source_hash:
        return SourceStructurePreview(None, "VIEWER_PREVIEW_SOURCE_IDENTITY_MISSING")
    try:
        _validate_preview_parameters()
        sites, lattice, pbc = _source_geometry(payload, object_type)
        elements = [site["element"] for site in sites]
        neighbors = covalent_radius_neighbors(elements, [site["xyz"] for site in sites], lattice, pbc)
        periodic = any(pbc)
        bonds = neighbors.bonds if periodic else [
            {"from": bond["from"]["site_index"], "to": bond["to"]["site_index"],
             "distance": bond["distance_angstrom"], "source": "distance_cutoff", "authoritative": False}
            for bond in neighbors.bonds
        ]
        warnings = []
        if neighbors.missing_elements:
            warnings.append({"code": "VIEWER_SCENE_RADII_UNAVAILABLE", "message": "部分元素缺少参考半径，未生成相应连接：" + ", ".join(neighbors.missing_elements)})
        if neighbors.candidate_count > len(bonds):
            warnings.append({"code": "VIEWER_SCENE_BONDS_TRUNCATED", "message": f"当前显示前 {len(bonds)} / {neighbors.candidate_count} 条近邻连接。"})
        species = sorted(set(elements))
        if len(species) > DEFAULT_VIEWER_SCENE_CAPS["max_species"]:
            raise NeighborPreviewLimit("VIEWER_NEIGHBOR_SPECIES_LIMIT")
        scene = {
            "kind": "viewer_scene",
            "version": "viewer_scene.v2" if periodic else "viewer_scene.v1",
            "schema_version": "phase10f18.viewer_scene.v2" if periodic else "phase10f8.viewer_scene.v1",
            **({"capabilities": dict(VIEWER_SCENE_V2_CAPABILITIES)} if periodic else {}),
            "source": {"resource_id": object_id, "kind": "normalized_source_preview", "hash": source_hash},
            "metadata": {
                "formula": Composition(dict(Counter(elements))).reduced_formula,
                "site_count": len(sites), "species_count": len(species), "species": species,
                "periodic": periodic, "display_only": True,
                "connectivity": {"method": "covalent_radii", "radius_scale": COVALENT_RADIUS_SCALE,
                                 "radius_reference": COVALENT_RADIUS_REFERENCE, "authoritative": False},
            },
            "scene": {
                "coordinate_basis": "cartesian_angstrom", "sites": sites,
                "lattice": {"vectors": lattice, "pbc": pbc, **({"presentation_only": True} if not periodic else {})},
                "bonds": bonds, "cell_expansion": [1, 1, 1],
                "style": {"representation": "ball_and_stick", "background": "transparent"},
            },
            "validation": {"status": "passed_with_warnings" if warnings else "passed", "deterministic": True,
                           "truncated": neighbors.candidate_count > len(bonds), "caps_enforced": True},
            "caps": dict(DEFAULT_VIEWER_SCENE_CAPS), "warnings": warnings,
            "provenance": {"projection": PREVIEW_VERSION, "source_hash": source_hash, "source_object_id": object_id,
                           "source_dataset_id": dataset_id, "source_version_id": version_id,
                           "connection_parameters": dict(_PARAMETERS), "scientific_analysis_result": False},
            "security": {"contains_javascript": False, "external_urls": [], "external_urls_allowed": False,
                         "artifact_supplied_js_allowed": False, "renderer_required": False, "remote_assets_allowed": False, "html_allowed": False},
        }
        validation = validate_viewer_scene(scene, raw_size_bytes=len(stable_json_dumps(scene).encode("utf-8")))
        if not validation.valid:
            return SourceStructurePreview(None, "VIEWER_PREVIEW_VALIDATION_FAILED")
        return SourceStructurePreview(scene)
    except NeighborPreviewLimit as exc:
        return SourceStructurePreview(None, str(exc))
    except (ValueError, TypeError, KeyError, ArithmeticError):
        return SourceStructurePreview(None, "VIEWER_PREVIEW_GEOMETRY_UNSUPPORTED")


def _triplet(value: Any) -> list[float]:
    if not isinstance(value, (list, tuple)) or len(value) != 3 or any(
        isinstance(item, bool) or not isinstance(item, (int, float)) or not math.isfinite(item) for item in value
    ):
        raise ValueError("Invalid coordinate")
    return [float(item) for item in value]


def _periodicity(value: Any) -> list[bool]:
    if not isinstance(value, (list, tuple)) or len(value) != 3 or any(type(item) is not bool for item in value):
        raise ValueError("Invalid periodicity")
    return list(value)


def _source_geometry(payload: Any, object_type: str) -> tuple[list[dict[str, Any]], list[list[float]], list[bool]]:
    if not isinstance(payload, dict):
        raise ValueError("Unsupported source")
    atoms = object_type in {"Atoms", "structure.atomic"}
    raw_sites = payload.get("positions") if atoms else payload.get("sites")
    if not isinstance(raw_sites, list) or not raw_sites:
        raise ValueError("Missing sites")
    if len(raw_sites) > MAX_PREVIEW_SITES:
        raise NeighborPreviewLimit("VIEWER_NEIGHBOR_SITE_LIMIT")
    if atoms:
        symbols = payload.get("symbols")
        if not isinstance(symbols, list) or len(symbols) != len(raw_sites):
            raise ValueError("Invalid atom symbols")
        pbc = _periodicity(payload.get("pbc", [False, False, False]))
        raw_lattice = payload.get("cell")
    else:
        lattice = payload.get("lattice")
        if not isinstance(lattice, dict):
            raise ValueError("Missing lattice")
        raw_lattice = lattice.get("matrix")
        pbc = _periodicity(lattice.get("pbc", [True, True, True]))
    sites = []
    for index, raw in enumerate(raw_sites):
        if atoms:
            element, xyz = symbols[index], _triplet(raw)
            fractional = None
        else:
            if not isinstance(raw, dict):
                raise ValueError("Invalid site")
            species = raw.get("species")
            if not isinstance(species, list) or len(species) != 1 or not isinstance(species[0], dict):
                raise ValueError("Disordered site requires an explicit connection model")
            occupancy = species[0].get("occu", 1)
            if isinstance(occupancy, bool) or not isinstance(occupancy, (int, float)) or occupancy != 1:
                raise ValueError("Partial occupancy requires an explicit connection model")
            element, xyz = species[0].get("element"), _triplet(raw.get("xyz"))
            fractional = _triplet(raw["abc"]) if "abc" in raw else None
        if not isinstance(element, str) or atomic_numbers.get(element, 0) <= 0:
            raise ValueError("Unknown element")
        radius = element_covalent_radius(element)
        sites.append({"index": index, "element": element, "label": f"{element}{index + 1}", "xyz": xyz,
                      **({"frac": fractional} if fractional is not None else {}), "occupancy": 1,
                      # Display radii leave the connections visible; they do not
                      # claim that covalent radii are a sample measurement.
                      "style": {"radius": round(0.45 * radius, 6) if radius else 0.45}})
    if any(pbc):
        if not isinstance(raw_lattice, list) or len(raw_lattice) != 3:
            raise ValueError("Missing periodic lattice")
        matrix = [_triplet(row) for row in raw_lattice]
        for site in sites:
            if "frac" in site:
                reconstructed = [sum(site["frac"][axis] * matrix[axis][component] for axis in range(3)) for component in range(3)]
                if any(abs(left - right) > 1e-5 for left, right in zip(reconstructed, site["xyz"], strict=True)):
                    raise ValueError("Coordinate representations disagree")
    else:
        spans = [max(site["xyz"][axis] for site in sites) - min(site["xyz"][axis] for site in sites) for axis in range(3)]
        matrix = [[max(4.0, spans[row] + 4.0) if row == column else 0.0 for column in range(3)] for row in range(3)]
    return sites, matrix, pbc
