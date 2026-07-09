from __future__ import annotations

import json
from pathlib import Path

from mdi_artifact_core import (
    load_viewer_scene_json,
    validate_viewer_scene,
    validate_viewer_scene_manifest,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "docs" / "phase10f" / "fixtures" / "viewer_scene_v1"
EXPECTED_RESULTS = FIXTURE_DIR / "expected_results.json"
FORBIDDEN_TEXT_MARKERS = (
    "http://",
    "https://",
    "javascript:",
    "<script",
    "</script",
    "<html",
    "eval(",
    "function(",
)


def _expected_results() -> list[dict[str, object]]:
    payload = json.loads(EXPECTED_RESULTS.read_text(encoding="utf-8"))
    return list(payload["results"])


def test_viewer_scene_expected_results_cover_all_scene_fixtures() -> None:
    expected_names = {str(item["fixture_name"]) for item in _expected_results()}
    fixture_names = {
        path.name
        for path in FIXTURE_DIR.glob("*.viewer_scene.v1.json")
        if not path.name.startswith("manifest_")
    }

    assert expected_names == fixture_names


def test_viewer_scene_contract_fixtures_match_expected_results() -> None:
    for item in _expected_results():
        fixture_path = FIXTURE_DIR / str(item["fixture_name"])
        raw = fixture_path.read_text(encoding="utf-8")
        payload = load_viewer_scene_json(fixture_path)

        result = validate_viewer_scene(payload, raw_size_bytes=len(raw.encode("utf-8")))

        assert result.valid is item["expected_validity"], fixture_path.name
        assert result.errors == item["expected_error_codes"], fixture_path.name
        assert result.warnings == item["expected_warning_codes"], fixture_path.name
        assert item["preview_expectation"] == "JSON_ONLY"
        assert item["renderer_expectation"] in {"DEFERRED", "NOT_APPLICABLE"}


def test_viewer_scene_manifest_fixtures_are_valid_and_renderer_free() -> None:
    results_by_fixture = {
        str(item["fixture_name"]): item for item in _expected_results()
    }

    manifest_paths = sorted(FIXTURE_DIR.glob("manifest_*.viewer_scene.v1.json"))
    assert manifest_paths

    for manifest_path in manifest_paths:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        result = validate_viewer_scene_manifest(payload)
        fixture_name = str(payload["fixture_source"])
        expected = results_by_fixture[fixture_name]

        assert result.valid, manifest_path.name
        assert (FIXTURE_DIR / fixture_name).exists()
        assert payload["renderer_required"] is False
        assert payload["preview_mode"] == "json_only"
        assert payload["executable_assets"] == "none"
        assert payload["external_resources"] == "none"
        assert payload["expected_errors"] == expected["expected_error_codes"]
        assert payload["expected_warnings"] == expected["expected_warning_codes"]


def test_viewer_scene_fixtures_have_no_real_external_urls_or_script_text() -> None:
    checked_paths = [
        *FIXTURE_DIR.glob("*.json"),
    ]
    assert checked_paths

    for path in checked_paths:
        raw = path.read_text(encoding="utf-8").lower()
        for marker in FORBIDDEN_TEXT_MARKERS:
            assert marker not in raw, f"{path.name} contains forbidden marker {marker}"


def test_viewer_scene_expected_results_keep_official_pass_claims_false() -> None:
    payload = json.loads(EXPECTED_RESULTS.read_text(encoding="utf-8"))

    assert payload["official_pass_claims"] is False
    for item in payload["results"]:
        assert item["renderer_expectation"] in {"DEFERRED", "NOT_APPLICABLE"}
