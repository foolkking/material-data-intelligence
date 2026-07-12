from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from pymatgen.core import Lattice, Structure

from mdi_adapters import StructureViewerSceneAdapter
from mdi_adapters.context import ToolExecutionContext
from mdi_artifact_core import (
    VIEWER_SCENE_MANIFEST_V2_CAPABILITIES,
    VIEWER_SCENE_MANIFEST_V2_SCHEMA_VERSION,
    VIEWER_SCENE_V2_CAPABILITIES,
    validate_viewer_scene,
    validate_viewer_scene_manifest,
)
from mdi_schemas import ArtifactType
from mdi_tool_registry import load_manifests


def test_v2_scene_and_manifest_capabilities_are_exact_and_valid(tmp_path: Path) -> None:
    artifacts = _execute(tmp_path, _orthogonal_structure(), cutoff=1.0)
    scene = artifacts["viewer_scene.json"]
    manifest = artifacts["viewer_scene_manifest.json"]

    assert scene["capabilities"] == VIEWER_SCENE_V2_CAPABILITIES
    assert manifest["schema_version"] == VIEWER_SCENE_MANIFEST_V2_SCHEMA_VERSION
    assert manifest["capabilities"] == VIEWER_SCENE_MANIFEST_V2_CAPABILITIES
    assert manifest["renderer_required"] is False
    assert manifest["webgl_included"] is False
    assert manifest["external_resources"] == "none"
    assert validate_viewer_scene(scene).valid
    assert validate_viewer_scene_manifest(manifest).valid


@pytest.mark.parametrize("field", ["trajectory", "phonon", "volumetric"])
def test_v2_scene_rejects_capability_overclaim(tmp_path: Path, field: str) -> None:
    scene = _execute(tmp_path, _orthogonal_structure(), cutoff=1.0)["viewer_scene.json"]
    invalid = copy.deepcopy(scene)
    invalid["capabilities"][field] = True
    assert "VIEWER_SCENE_CAPABILITIES_INVALID" in validate_viewer_scene(invalid).errors


def test_v2_manifest_rejects_renderer_or_contract_drift(tmp_path: Path) -> None:
    manifest = _execute(tmp_path, _orthogonal_structure(), cutoff=1.0)["viewer_scene_manifest.json"]
    for mutate in (
        lambda value: value["capabilities"].update(scene_contract="phase10f8.viewer_scene.v1"),
        lambda value: value["capabilities"].update(renderer_included=True),
        lambda value: value["capabilities"].update(webgl_included=True),
    ):
        invalid = copy.deepcopy(manifest)
        mutate(invalid)
        assert "VIEWER_SCENE_MANIFEST_CAPABILITIES_INVALID" in validate_viewer_scene_manifest(invalid).errors


def test_v1_contract_remains_valid_without_capabilities() -> None:
    fixture = json.loads(Path("docs/phase10f/fixtures/viewer_scene_v1/valid_optional_bonds.viewer_scene.v1.json").read_text(encoding="utf-8"))
    assert "capabilities" not in fixture
    assert validate_viewer_scene(fixture).valid


@pytest.mark.parametrize(
    "case_id,structure,cutoff,expected_offset",
    [
        ("orthogonal", Structure(Lattice.cubic(10), ["H", "H"], [[0.98, 0, 0], [0.02, 0, 0]]), 1.0, [1, 0, 0]),
        ("triclinic", Structure(Lattice([[4, 0, 0], [1.2, 3.1, 0], [0.7, 0.4, 2.6]]), ["H", "H"], [[0.91, 0.13, 0.77], [0.08, 0.89, 0.12]]), 1.3, [1, -1, 1]),
        ("self_periodic", Structure(Lattice.cubic(1), ["H"], [[0, 0, 0]]), 1.01, None),
    ],
)
def test_topology_identity_is_consistent_across_artifacts(tmp_path: Path, case_id: str, structure: Structure, cutoff: float, expected_offset: list[int] | None) -> None:
    artifacts = _execute(tmp_path / case_id, structure, cutoff=cutoff)
    scene = artifacts["viewer_scene.json"]
    manifest = artifacts["viewer_scene_manifest.json"]
    summary = artifacts["summary.md"]
    recipe = artifacts["recipe.json"]
    bonds = scene["scene"]["bonds"]

    assert bonds
    assert all(item["from"]["image_offset"] == [0, 0, 0] for item in bonds)
    assert all(item["source"] == "distance_cutoff" and item["authoritative"] is False for item in bonds)
    if expected_offset is not None:
        assert bonds[0]["to"]["image_offset"] == expected_offset
    else:
        assert all(item["from"]["site_index"] == item["to"]["site_index"] for item in bonds)
    assert manifest["capabilities"]["scene_contract"] == scene["schema_version"]
    assert recipe["periodic_bond_schema"] == scene["schema_version"]
    assert f"- periodic bond count: {len(bonds)}" in summary


def _orthogonal_structure() -> Structure:
    return Structure(Lattice.cubic(10), ["H", "H"], [[0.98, 0, 0], [0.02, 0, 0]])


def _execute(root: Path, structure: Structure, *, cutoff: float) -> dict[str, object]:
    root.mkdir(parents=True, exist_ok=True)
    context = ToolExecutionContext(
        job_id="job_10f19", project_id="project_10f19", dataset_id="dataset_structure",
        tool_id="structure.viewer_scene", tool_version="1.0.0", adapter_version="1.0.0",
        registry_version=load_manifests().version, artifact_root=root,
        object_store={"structures": [structure]}, resource_limits={"maxStructures": 1, "maxSites": 256, "maxBonds": 2048},
    )
    outputs = StructureViewerSceneAdapter().execute(context, {
        "jobId":"job_10f19", "stepId":"step_001", "toolId":"structure.viewer_scene",
        "inputRefs":[{"refType":"normalized_object","ref":"structures","objectType":"Structure"}],
        "params":{"include_bonds":True,"bond_cutoff_angstrom":cutoff},
        "artifactTypes":[ArtifactType.structure_json.value,ArtifactType.table_json.value,ArtifactType.summary_md.value,ArtifactType.recipe_json.value],
    })
    result: dict[str, object] = {}
    for artifact in outputs:
        raw = (root / artifact.storageKey).read_text(encoding="utf-8")
        result[artifact.name] = json.loads(raw) if artifact.name.endswith(".json") else raw
    return result
