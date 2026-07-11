from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = REPO_ROOT / "apps" / "web" / "test" / "generate-viewer-scene-live-adapter-evidence.py"


def test_phase10f13_live_api_runtime_cases_generate_adapter_artifacts(tmp_path: Path) -> None:
    payload = _helper().generate_live_adapter_evidence(tmp_path / "evidence")

    minimal = payload["cases"]["valid_minimal_crystal"]
    multi = payload["cases"]["multi_species_crystal"]
    warning = payload["cases"]["warning_caps"]

    for case in (minimal, multi, warning):
        assert case["planner"]["selected_tool"] == "structure.viewer_scene"
        assert case["planner"]["real_llm_used"] is False
        assert case["worker"]["status"] == "completed"
        assert case["api"]["job"]["status"] == "completed"
        assert case["api"]["tool_calls"][0]["toolId"] == "structure.viewer_scene"
        assert case["artifact_audit"]["viewer_scene_present"] is True
        assert case["artifact_audit"]["manifest_present"] is True
        assert case["artifact_audit"]["canonical_validator"]["valid"] is True
        assert case["artifact_audit"]["manifest_validator"]["valid"] is True
        assert case["source_assertion"]["adapter_generated"] is True
        assert case["source_assertion"]["static_fixture_used"] is False

    assert minimal["preview_expectation"]["site_count"] == 2
    assert multi["preview_expectation"]["species_count"] == 2
    assert "VIEWER_SCENE_CAP_NEAR_LIMIT" in warning["artifact_audit"]["warnings"]
    assert "VIEWER_SCENE_BONDS_TRUNCATED" in warning["artifact_audit"]["warnings"]


def test_phase10f13_invalid_live_request_fails_without_successful_viewer_artifact(tmp_path: Path) -> None:
    payload = _helper().generate_live_adapter_evidence(tmp_path / "evidence")
    invalid = payload["cases"]["invalid_multi_structure_rejected"]

    assert invalid["planner"]["selected_tool"] == "structure.viewer_scene"
    assert invalid["worker"]["status"] == "failed"
    assert invalid["api"]["job"]["status"] == "failed"
    assert invalid["api"]["artifacts"] == []
    assert invalid["artifact_audit"]["viewer_scene_present"] is False
    assert invalid["artifact_audit"]["canonical_validator"]["valid"] is False
    assert invalid["preview_expectation"]["invalid_state"] == "job_failed_before_successful_artifact"
    tool_error = invalid["api"]["tool_calls"][0]["error"]
    assert tool_error["type"] == "ToolExecutionError"
    assert "viewer_scene.v1 adapter accepts exactly one periodic structure" in tool_error["message"]
    assert ":\\" not in tool_error["message"]


def test_phase10f13_schema_compatibility_and_routing_boundaries(tmp_path: Path) -> None:
    payload = _helper().generate_live_adapter_evidence(tmp_path / "evidence")
    compatibility = payload["compatibility"]
    routes = compatibility["routes"]

    assert compatibility["old_tools_registered"] == {
        "structure.viewer_scene_metadata": "structure.viewer_scene_metadata",
        "structure.viewer_export_package": "structure.viewer_export_package",
    }
    assert compatibility["new_tool_registered"] == "structure.viewer_scene"
    assert compatibility["old_schema"] == "phase10d1.viewer_scene.v1"
    assert compatibility["canonical_schema"] == "phase10f8.viewer_scene.v1"
    assert compatibility["migration_performed"] is False
    assert routes["canonical_viewer_scene"] == "structure.viewer_scene"
    assert routes["old_metadata"] == "structure.viewer_scene_metadata"
    assert routes["old_export_package"] == "structure.viewer_export_package"
    assert routes["full_3d_viewer"] != "structure.viewer_scene"
    assert routes["xrd"] == "structure.xrd"
    assert routes["rdf"] == "structure.rdf"
    assert routes["coordination"] == "structure.coordination_hist"
    assert routes["phonon"] != "structure.viewer_scene"


def test_phase10f13_evidence_security_payloads_are_inert(tmp_path: Path) -> None:
    evidence_root = tmp_path / "evidence"
    payload = _helper().generate_live_adapter_evidence(evidence_root)

    assert payload["network_policy"]["result"] == "NO_LIVE_ADAPTER_EXTERNAL_NETWORK_REQUESTS"
    assert payload["malicious_boundary"]["adapter_generated_malicious_fields"] is False
    assert payload["malicious_boundary"]["result"] == "PASS"

    combined = "\n".join(path.read_text(encoding="utf-8") for path in evidence_root.rglob("*") if path.is_file()).lower()
    assert "authorization:" not in combined
    assert "bearer " not in combined
    assert "api_key" not in combined
    assert "secret_key" not in combined

    live_payload = json.loads((evidence_root / "live_payload.json").read_text(encoding="utf-8"))
    for case in live_payload["cases"].values():
        for artifact in case["api"]["artifacts"]:
            raw = json.dumps(artifact.get("content"), sort_keys=True).lower()
            assert "<script" not in raw
            assert "javascript:" not in raw
            assert "http://" not in raw
            assert "https://" not in raw
            assert "new function" not in raw
            assert "eval(" not in raw


def _helper() -> Any:
    spec = importlib.util.spec_from_file_location("viewer_scene_live_adapter_evidence", HELPER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
