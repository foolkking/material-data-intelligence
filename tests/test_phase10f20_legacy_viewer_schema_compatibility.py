from __future__ import annotations

import copy
import json
from pathlib import Path

from mdi_artifact_core import (
    VIEWER_MANIFEST_COMPATIBILITY,
    VIEWER_SCHEMA_COMPATIBILITY,
    compatibility_matrix_snapshot,
    viewer_manifest_compatibility_result,
    viewer_schema_compatibility_result,
)


def test_scene_compatibility_matrix_registers_every_known_schema_once() -> None:
    assert list(VIEWER_SCHEMA_COMPATIBILITY) == [
        "phase10d1.viewer_scene.v1",
        "phase10f8.viewer_scene.v1",
        "phase10f18.viewer_scene.v2",
    ]
    assert [key for key,value in VIEWER_SCHEMA_COMPATIBILITY.items() if value["status"] == "current"] == ["phase10f18.viewer_scene.v2"]
    assert VIEWER_SCHEMA_COMPATIBILITY["phase10d1.viewer_scene.v1"] == {
        "kind":"scene", "status":"deprecated_read_only", "preview_mode":"json_only", "preview_supported":True,
        "renderer_supported":False, "periodic_topology_supported":False, "migration_target":None,
        "migration_policy":"regenerate_from_source_only", "warnings":["VIEWER_SCENE_LEGACY_PHASE10D_SCHEMA"],
        "producer_status":"deprecated_direct_compatibility_only", "new_artifact_generation_allowed":False,
    }
    assert VIEWER_SCHEMA_COMPATIBILITY["phase10f8.viewer_scene.v1"]["status"] == "supported_legacy_same_cell"
    assert VIEWER_SCHEMA_COMPATIBILITY["phase10f8.viewer_scene.v1"]["periodic_topology_supported"] is False
    assert VIEWER_SCHEMA_COMPATIBILITY["phase10f18.viewer_scene.v2"]["producer_status"] == "current_default"
    assert VIEWER_SCHEMA_COMPATIBILITY["phase10f18.viewer_scene.v2"]["new_artifact_generation_allowed"] is True


def test_compatibility_snapshot_is_detached_and_deterministic() -> None:
    first = compatibility_matrix_snapshot()
    second = compatibility_matrix_snapshot()
    assert first == second
    first["scenes"]["phase10f18.viewer_scene.v2"]["status"] = "mutated"
    assert compatibility_matrix_snapshot()["scenes"]["phase10f18.viewer_scene.v2"]["status"] == "current"


def test_phase10d_legacy_scene_is_valid_read_only_and_malicious_content_is_rejected() -> None:
    payload = _phase10d_scene()
    result = viewer_schema_compatibility_result(payload)
    assert result == {
        "schema_version":"phase10d1.viewer_scene.v1", "status":"deprecated_read_only", "preview_supported":True,
        "renderer_supported":False, "periodic_topology_supported":False, "migration_policy":"regenerate_from_source_only",
        "warnings":["VIEWER_SCENE_LEGACY_PHASE10D_SCHEMA"], "valid":True, "errors":[],
    }
    invalid = copy.deepcopy(payload)
    invalid["structure"]["label"] = "<script>blocked</script>"
    assert "VIEWER_SCENE_LEGACY_EXECUTABLE_CONTENT" in viewer_schema_compatibility_result(invalid)["errors"]


def test_canonical_v1_and_current_v2_have_distinct_topology_policies() -> None:
    v1 = json.loads(Path("docs/phase10f/fixtures/viewer_scene_v1/valid_optional_bonds.viewer_scene.v1.json").read_text(encoding="utf-8"))
    v2 = json.loads(Path("docs/phase10f/evidence/phase10f19_periodic_scene_integration/viewer_scene.json").read_text(encoding="utf-8"))
    v1_result = viewer_schema_compatibility_result(v1)
    v2_result = viewer_schema_compatibility_result(v2)
    assert v1_result["valid"] and v1_result["renderer_supported"]
    assert v1_result["periodic_topology_supported"] is False
    assert v1_result["warnings"] == ["VIEWER_SCENE_LEGACY_SAME_CELL_TOPOLOGY"]
    assert v2_result["valid"] and v2_result["status"] == "current"
    assert v2_result["periodic_topology_supported"] is True
    assert v2_result["warnings"] == []


def test_unknown_schema_is_typed_unsupported() -> None:
    result = viewer_schema_compatibility_result({"schema_version":"unknown.viewer.v9"})
    assert result["status"] == "unsupported"
    assert result["valid"] is False
    assert result["warnings"] == ["VIEWER_SCENE_SCHEMA_UNSUPPORTED"]


def test_manifest_matrix_and_pairing_reject_schema_drift() -> None:
    assert list(VIEWER_MANIFEST_COMPATIBILITY) == [
        "phase10d1.viewer_assets_manifest.v1", "phase10f9.viewer_scene_manifest.v1", "phase10f19.viewer_assets_manifest.v2",
    ]
    legacy = viewer_manifest_compatibility_result(_phase10d_manifest(), scene_schema="phase10d1.viewer_scene.v1")
    assert legacy["valid"] and legacy["status"] == "deprecated_read_only"
    assert legacy["periodic_topology_supported"] is False
    mismatch = viewer_manifest_compatibility_result(_phase10d_manifest(), scene_schema="phase10f18.viewer_scene.v2")
    assert mismatch["errors"] == ["VIEWER_MANIFEST_SCENE_SCHEMA_MISMATCH"]
    current = json.loads(Path("docs/phase10f/evidence/phase10f19_periodic_scene_integration/viewer_assets_manifest.json").read_text(encoding="utf-8"))
    current_result = viewer_manifest_compatibility_result(current, scene_schema="phase10f18.viewer_scene.v2")
    assert current_result["valid"] and current_result["status"] == "current"


def test_migration_is_not_implemented_by_design() -> None:
    for schema in ("phase10d1.viewer_scene.v1", "phase10f8.viewer_scene.v1"):
        policy = VIEWER_SCHEMA_COMPATIBILITY[schema]
        assert policy["migration_target"] is None
        assert policy["migration_policy"] == "regenerate_from_source_only"
    assert not hasattr(__import__("mdi_artifact_core"), "migrate_viewer_scene")


def _phase10d_scene() -> dict:
    return {
        "artifactType":"structure.viewer_scene_metadata", "schema_version":"phase10d1.viewer_scene.v1",
        "structure":{"formula":"Si", "site_count":1, "atoms":[]},
        "security":{"contains_javascript":False,"external_urls":[],"external_urls_allowed":False,"artifact_supplied_js_allowed":False},
    }


def _phase10d_manifest() -> dict:
    return {
        "artifactType":"structure.viewer_export_package", "schema_version":"phase10d1.viewer_assets_manifest.v1",
        "renderer":{"included":False,"renderer_type":"none"},
        "security":{"contains_javascript":False,"external_urls":[],"external_urls_allowed":False,"artifact_supplied_js_allowed":False},
    }
