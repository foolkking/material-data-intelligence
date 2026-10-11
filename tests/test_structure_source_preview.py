from __future__ import annotations

from collections import Counter
from copy import deepcopy
import math

from jsonschema import Draft202012Validator, ValidationError
from pymatgen.core import Lattice, Structure
import pytest

from mdi_adapters.platform_builtin.structure_neighbors import covalent_radius_neighbors, element_covalent_radius, NeighborPreviewLimit
from mdi_api.scientific_viewers.structure_preview import source_structure_preview
from mdi_artifact_core import validate_viewer_scene
from mdi_tool_registry import get_tool_by_id


def _preview(payload, object_type="Structure"):
    return source_structure_preview(payload, object_type=object_type, object_id="source", source_hash="a" * 64, dataset_id="dataset", version_id="v1")


@pytest.mark.parametrize("structure,neighbors_per_site", [
    (Structure.from_spacegroup("Fd-3m", Lattice.cubic(5.43), ["Si"], [[0, 0, 0]]), 4),
    (Structure.from_spacegroup("Fm-3m", Lattice.cubic(3.61), ["Cu"], [[0, 0, 0]]), 12),
    (Structure.from_spacegroup("Fm-3m", Lattice.cubic(5.64), ["Na", "Cl"], [[0, 0, 0], [0.5, 0.5, 0.5]]), 6),
])
def test_source_preview_preserves_sites_and_known_crystal_coordination(structure, neighbors_per_site):
    raw = structure.as_dict()
    before = deepcopy(raw)
    preview = _preview(raw)
    assert preview.issue is None
    assert preview.scene is not None
    scene = preview.scene
    assert validate_viewer_scene(scene).valid
    assert raw == before
    assert [site["xyz"] for site in scene["scene"]["sites"]] == [site["xyz"] for site in raw["sites"]]
    bonds = scene["scene"]["bonds"]
    assert len(bonds) == len(structure) * neighbors_per_site // 2
    degrees = Counter(index for bond in bonds for index in [bond["from"]["site_index"], bond["to"]["site_index"]])
    assert set(degrees.values()) == {neighbors_per_site}
    assert any(any(bond["to"]["image_offset"]) for bond in bonds)
    assert all(bond["authoritative"] is False for bond in bonds)
    if "Na" in structure.composition:
        assert scene["metadata"]["formula"] == "NaCl"
        assert all(structure[bond["from"]["site_index"]].specie != structure[bond["to"]["site_index"]].specie for bond in bonds)
    assert scene["provenance"] == {
        "projection": "source_structure_preview/1.0", "source_hash": "a" * 64,
        "source_object_id": "source", "source_dataset_id": "dataset", "source_version_id": "v1",
        "connection_parameters": {"include_bonds": True, "bond_method": "covalent_radii"}, "scientific_analysis_result": False,
    }


def test_nonperiodic_water_has_two_oh_candidates_without_hh_or_periodic_edges():
    payload = {"symbols": ["O", "H", "H"], "positions": [[0, 0, 0], [0.9572, 0, 0], [-0.2399872, 0.927297, 0]]}
    preview = _preview(payload, "Atoms")
    assert preview.issue is None
    assert preview.scene is not None
    assert validate_viewer_scene(preview.scene).valid
    scene = preview.scene["scene"]
    assert [(bond["from"], bond["to"]) for bond in scene["bonds"]] == [(0, 1), (0, 2)]
    assert scene["lattice"]["pbc"] == [False, False, False]
    assert scene["lattice"]["presentation_only"] is True
    assert scene["sites"][0]["style"]["radius"] > scene["sites"][1]["style"]["radius"]


def test_periodic_atoms_preserve_periodicity_instead_of_becoming_a_molecule():
    preview = _preview({"symbols": ["Si"], "positions": [[0, 0, 0]], "pbc": [True, True, False],
                        "cell": [[2.5, 0, 0], [0, 2.5, 0], [0, 0, 8]]}, "Atoms")
    assert preview.scene is not None
    assert preview.scene["version"] == "viewer_scene.v2"
    bonds = preview.scene["scene"]["bonds"]
    assert len(bonds) == 2
    assert all(bond["from"]["site_index"] == bond["to"]["site_index"] == 0 for bond in bonds)
    assert {tuple(bond["to"]["image_offset"]) for bond in bonds} == {(-1, 0, 0), (0, -1, 0)}


@pytest.mark.parametrize("pbc", [(True, True, True), (True, False, True)])
def test_triclinic_neighbors_match_independent_pymatgen_enumeration(pbc):
    structure = Structure(Lattice([[3.1, 0, 0], [1.1, 3.4, 0], [0.3, 0.4, 3.8]], pbc=pbc),
                          ["Si", "O", "Cu"], [[0.95, 0.02, 0.15], [0.12, 0.98, 0.11], [0.3, 0.25, 0.91]])
    symbols = [site.specie.symbol for site in structure]
    result = covalent_radius_neighbors(symbols, structure.cart_coords, structure.lattice.matrix, list(pbc))
    radii = [element_covalent_radius(symbol) for symbol in symbols]
    centers, points, images, distances = structure.get_neighbor_list(2 * max(radii) * 1.15)
    expected = set()
    for first, second, image, distance in zip(centers, points, images, distances, strict=True):
        if distance <= (radii[first] + radii[second]) * 1.15 + 1e-8:
            key = (int(first), int(second), *(int(value) for value in image))
            reverse = (int(second), int(first), *(-int(value) for value in image))
            expected.add(min(key, reverse))
    actual = {(bond["from"]["site_index"], bond["to"]["site_index"], *bond["to"]["image_offset"]) for bond in result.bonds}
    assert actual == expected
    for bond in result.bonds:
        assert math.isclose(math.hypot(*bond["displacement_cartesian"]), bond["distance_angstrom"], abs_tol=1e-7)


def test_display_cap_keeps_stable_first_pairs_and_full_candidate_count():
    structure = Structure.from_spacegroup("Fm-3m", Lattice.cubic(3.61), ["Cu"], [[0, 0, 0]])
    args = (["Cu"] * len(structure), structure.cart_coords, structure.lattice.matrix, [True] * 3)
    full = covalent_radius_neighbors(*args)
    limited = covalent_radius_neighbors(*args, max_bonds=3)
    assert limited.bonds == full.bonds[:3]
    assert limited.candidate_count == full.candidate_count == 24
    assert covalent_radius_neighbors(*args, max_bonds=0).candidate_count == 24


def test_search_refuses_unbounded_images_and_work_before_neighbor_enumeration():
    with pytest.raises(NeighborPreviewLimit, match="OFFSET_LIMIT"):
        covalent_radius_neighbors(["Si"], [[0, 0, 0]], [[0.01, 0, 0], [0, 0.01, 0], [0, 0, 0.01]], [True] * 3)
    with pytest.raises(NeighborPreviewLimit, match="WORK_LIMIT"):
        covalent_radius_neighbors(["Si"] * 256, [[0, 0, 0]] * 256, [[1, 0, 0], [0, 1, 0], [0, 0, 1]], [True] * 3)


@pytest.mark.parametrize("change", ["large", "disordered", "partial", "fractional", "nonfinite", "unknown"])
def test_unsupported_previews_keep_the_source_unchanged(change):
    raw = Structure(Lattice.cubic(5), ["Si"], [[0, 0, 0]]).as_dict()
    if change == "large":
        raw["sites"] *= 257
    elif change == "disordered":
        raw["sites"][0]["species"] = [{"element": "Si", "occu": 0.5}, {"element": "Ge", "occu": 0.5}]
    elif change == "partial":
        raw["sites"][0]["species"][0]["occu"] = 0.5
    elif change == "fractional":
        raw["sites"][0]["abc"] = [0.5, 0, 0]
    elif change == "nonfinite":
        raw["sites"][0]["xyz"] = [float("inf"), 0, 0]
    else:
        raw["sites"][0]["species"][0]["element"] = "X"
    before = deepcopy(raw)
    result = _preview(raw)
    assert result.scene is None
    assert result.issue
    assert raw == before


def test_missing_reference_radius_is_not_replaced_with_a_fabricated_value():
    for symbol in ("Bk", "Cf", "Mt", "Og", "X", "Unknown"):
        assert element_covalent_radius(symbol) is None
    assert element_covalent_radius("Pa") == 2.0
    assert element_covalent_radius("Cm") == 1.69
    result = _preview({"symbols": ["Og", "H"], "positions": [[0, 0, 0], [0.5, 0, 0]]}, "Atoms")
    assert result.scene is not None
    assert result.scene["scene"]["bonds"] == []
    assert result.scene["warnings"][0]["code"] == "VIEWER_SCENE_RADII_UNAVAILABLE"


def test_registered_radius_method_rejects_conflicting_distance_cutoff():
    validator = Draft202012Validator(get_tool_by_id("structure.viewer_3d").paramsSchema)
    validator.validate({"bond_method": "covalent_radii"})
    validator.validate({"bond_cutoff_angstrom": 3})
    with pytest.raises(ValidationError):
        validator.validate({"bond_method": "covalent_radii", "bond_cutoff_angstrom": 3})
