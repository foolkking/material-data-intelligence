from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from pymatgen.core import Lattice, Structure

from mdi_adapters import StructureViewer3DAdapter, StructureViewerSceneAdapter
from mdi_adapters.context import ToolExecutionContext
from mdi_adapters.platform_builtin.structure import canonicalize_periodic_bond, periodic_bond_key
from mdi_artifact_core import validate_viewer_scene
from mdi_schemas import ArtifactType
from mdi_tool_registry import load_manifests


def test_periodic_bond_canonicalization_is_symmetric_and_stable() -> None:
    assert canonicalize_periodic_bond(1, 0, (-1, 0, 0)) == (0, 1, (1, 0, 0))
    assert periodic_bond_key(0, 1, (1, 0, 0)) == periodic_bond_key(1, 0, (-1, 0, 0))
    assert canonicalize_periodic_bond(0, 0, (0, 0, 0)) is None
    assert canonicalize_periodic_bond(0, 0, (-1, 0, 0)) == (0, 0, (-1, 0, 0))


@pytest.mark.parametrize("adapter_cls,tool_id", [(StructureViewerSceneAdapter, "structure.viewer_scene"), (StructureViewer3DAdapter, "structure.viewer_3d")])
def test_formal_adapters_emit_identical_orthogonal_cross_boundary_topology(tmp_path: Path, adapter_cls: type, tool_id: str) -> None:
    structure = Structure(Lattice.cubic(10), ["H", "H"], [[0.98, 0, 0], [0.02, 0, 0]])
    scene = _execute(tmp_path, adapter_cls(), tool_id, structure, cutoff=1.0)
    assert scene["version"] == "viewer_scene.v2"
    assert scene["schema_version"] == "phase10f18.viewer_scene.v2"
    bond = scene["scene"]["bonds"][0]
    assert bond["from"] == {"site_index": 0, "image_offset": [0, 0, 0]}
    assert bond["to"] == {"site_index": 1, "image_offset": [1, 0, 0]}
    assert bond["distance_angstrom"] == pytest.approx(0.4)
    assert bond["source"] == "distance_cutoff"
    assert bond["authoritative"] is False
    assert validate_viewer_scene(scene).valid


def test_adapter_emits_triclinic_endpoint_and_self_periodic_bonds(tmp_path: Path) -> None:
    lattice = Lattice([[4, 0, 0], [1.2, 3.1, 0], [0.7, 0.4, 2.6]])
    triclinic = Structure(lattice, ["H", "H"], [[0.91, 0.13, 0.77], [0.08, 0.89, 0.12]])
    scene = _execute(tmp_path / "triclinic", StructureViewerSceneAdapter(), "structure.viewer_scene", triclinic, cutoff=1.3)
    bond = scene["scene"]["bonds"][0]
    assert bond["to"]["image_offset"] == [1, -1, 1]
    assert bond["distance_angstrom"] == pytest.approx(1.264391, abs=1e-6)

    self_scene = _execute(tmp_path / "self", StructureViewerSceneAdapter(), "structure.viewer_scene", Structure(Lattice.cubic(1), ["H"], [[0, 0, 0]]), cutoff=1.01)
    assert len(self_scene["scene"]["bonds"]) == 3
    assert all(item["from"]["site_index"] == item["to"]["site_index"] == 0 for item in self_scene["scene"]["bonds"])
    assert all(item["to"]["image_offset"] != [0, 0, 0] for item in self_scene["scene"]["bonds"])


@pytest.mark.parametrize(
    "mutate,error",
    [
        (lambda bond: bond["to"].update(image_offset=[4, 0, 0]), "VIEWER_SCENE_BOND_ENDPOINT_INVALID"),
        (lambda bond: bond.update(distance_angstrom=99.0), "VIEWER_SCENE_PERIODIC_BOND_DISTANCE_MISMATCH"),
        (lambda bond: bond.update(source="javascript:bad"), "VIEWER_SCENE_PERIODIC_BOND_SOURCE_INVALID"),
        (lambda bond: bond.update(authoritative=True), "VIEWER_SCENE_PERIODIC_BOND_AUTHORITATIVE_INVALID"),
        (lambda bond: bond.update(callback="bad"), "VIEWER_SCENE_PERIODIC_BOND_FIELD_INVALID"),
    ],
)
def test_periodic_contract_rejects_invalid_topology(tmp_path: Path, mutate, error: str) -> None:
    scene = _execute(tmp_path, StructureViewerSceneAdapter(), "structure.viewer_scene", Structure(Lattice.cubic(10), ["H", "H"], [[0.98, 0, 0], [0.02, 0, 0]]), cutoff=1.0)
    invalid = copy.deepcopy(scene)
    mutate(invalid["scene"]["bonds"][0])
    assert error in validate_viewer_scene(invalid).errors


def test_v1_bonds_remain_valid_same_cell_legacy_topology() -> None:
    fixture = json.loads(Path("docs/phase10f/fixtures/viewer_scene_v1/valid_optional_bonds.viewer_scene.v1.json").read_text(encoding="utf-8"))
    assert validate_viewer_scene(fixture).valid


def test_periodic_topology_replay_is_deterministic_and_duplicates_are_rejected(tmp_path: Path) -> None:
    structure = Structure(Lattice.cubic(10), ["H", "H"], [[0.98, 0, 0], [0.02, 0, 0]])
    first = _execute(tmp_path / "first", StructureViewerSceneAdapter(), "structure.viewer_scene", structure, cutoff=1.0)
    second = _execute(tmp_path / "second", StructureViewerSceneAdapter(), "structure.viewer_scene", structure, cutoff=1.0)
    assert first["scene"]["bonds"] == second["scene"]["bonds"]
    duplicate = copy.deepcopy(first)
    duplicate["scene"]["bonds"].append(copy.deepcopy(duplicate["scene"]["bonds"][0]))
    duplicate["caps"]["max_bonds"] = 2
    assert "VIEWER_SCENE_PERIODIC_BOND_DUPLICATE" in validate_viewer_scene(duplicate).errors


def test_periodic_topology_no_bond_and_cap_warning(tmp_path: Path) -> None:
    structure = Structure(Lattice.cubic(1), ["H"], [[0, 0, 0]])
    scene = _execute(tmp_path / "cap", StructureViewerSceneAdapter(), "structure.viewer_scene", structure, cutoff=1.01, max_bonds=1)
    assert len(scene["scene"]["bonds"]) == 1
    assert {item["code"] for item in scene["warnings"]} >= {"VIEWER_SCENE_BONDS_TRUNCATED", "VIEWER_SCENE_BONDS_NON_AUTHORITATIVE"}

    no_bonds = _execute(tmp_path / "none", StructureViewerSceneAdapter(), "structure.viewer_scene", structure, cutoff=1.01, include_bonds=False)
    assert no_bonds["scene"]["bonds"] == []
    assert "VIEWER_SCENE_BONDS_SKIPPED" in {item["code"] for item in no_bonds["warnings"]}


def _execute(root: Path, adapter, tool_id: str, structure: Structure, *, cutoff: float, max_bonds: int = 2048, include_bonds: bool = True) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    context = ToolExecutionContext(
        job_id="job_10f18", project_id="project_10f18", dataset_id="dataset_structure",
        tool_id=tool_id, tool_version="1.0.0", adapter_version="1.0.0",
        registry_version=load_manifests().version, artifact_root=root,
        object_store={"structures": [structure]}, resource_limits={"maxStructures": 1, "maxSites": 256, "maxBonds": 2048},
    )
    artifacts = adapter.execute(context, {
        "jobId":"job_10f18", "stepId":"step_001", "toolId":tool_id,
        "inputRefs":[{"refType":"normalized_object","ref":"structures","objectType":"Structure"}],
        "params":{"include_bonds":include_bonds,"bond_cutoff_angstrom":cutoff,"max_bonds":max_bonds},
        "artifactTypes":[ArtifactType.structure_json.value,ArtifactType.table_json.value,ArtifactType.summary_md.value,ArtifactType.recipe_json.value],
    })
    artifact = next(item for item in artifacts if item.name == "viewer_scene.json")
    return json.loads((root / artifact.storageKey).read_text(encoding="utf-8"))
