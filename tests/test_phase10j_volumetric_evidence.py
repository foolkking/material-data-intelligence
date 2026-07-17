from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path
import struct

from mdi_artifact_core import (
    validate_volumetric_dataset,
    validate_volumetric_field,
    validate_volumetric_grid,
    validate_volumetric_manifest,
    validate_volumetric_payload,
    volumetric_schema_snapshots,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "phase10j" / "fixtures" / "volumetric_contract"
EVIDENCE = (
    ROOT
    / "docs"
    / "phase10j"
    / "evidence"
    / "phase10j_volumetric_data_contract"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def binary_artifacts(*names: str) -> dict[str, bytes]:
    return {name: (FIXTURES / "binary" / name).read_bytes() for name in names}


def test_evidence_hash_inventory_matches_every_generated_file() -> None:
    inventory = load_json(EVIDENCE / "artifact_hashes.json")
    recorded = {item["name"]: item for item in inventory["files"]}
    expected_paths = sorted(
        path
        for root in (FIXTURES, EVIDENCE)
        for path in root.rglob("*")
        if path.is_file() and path.name != "artifact_hashes.json"
    )
    assert set(recorded) == {path.relative_to(ROOT).as_posix() for path in expected_paths}
    for path in expected_paths:
        item = recorded[path.relative_to(ROOT).as_posix()]
        content = path.read_bytes()
        assert item["bytes"] == len(content)
        assert item["sha256"] == hashlib.sha256(content).hexdigest()


def test_schema_snapshot_and_security_evidence_are_exact() -> None:
    snapshot = load_json(FIXTURES / "schema_snapshots.json")
    assert snapshot == volumetric_schema_snapshots()
    assert set(snapshot["schemas"].values()) == {
        "phase10j.volumetric_grid.v1",
        "phase10j.volumetric_payload.v1",
        "phase10j.volumetric_field.v1",
        "phase10j.volumetric_dataset.v1",
        "phase10j.volumetric_manifest.v1",
    }
    security = load_json(EVIDENCE / "security" / "audit.json")
    assert security["artifact_javascript"] is False
    assert security["executable"] is False
    assert security["external_urls"] == []
    assert security["bounded_decompression"] is True
    assert security["bounded_allocation"] is True
    assert security["secret_scan"] == "NO_SECRET_PATTERN_HITS"


def test_cubic_inline_and_raw_fixture_validate_and_decode_equally() -> None:
    fixture = load_json(FIXTURES / "cubic_constant_scalar.json")
    artifacts = binary_artifacts("cubic-constant.f64")
    assert validate_volumetric_grid(fixture["grid"]).valid
    assert validate_volumetric_payload(fixture["inline_payload"]).valid
    assert validate_volumetric_payload(fixture["raw_payload"], artifacts).valid
    assert validate_volumetric_field(fixture["inline_field"]).valid
    assert validate_volumetric_field(fixture["raw_field"]).valid
    assert validate_volumetric_dataset(fixture["raw_dataset"], artifacts).valid
    assert validate_volumetric_manifest(
        fixture["manifest"], dataset=fixture["raw_dataset"], artifacts=artifacts
    ).valid
    values = [item[0] for item in struct.iter_unpack("<d", artifacts["cubic-constant.f64"])]
    assert values == fixture["values"]
    assert math.fsum(values) * fixture["grid"]["voxel_volume"] == 128.0


def test_gzip_and_chunked_binary_fixtures_validate() -> None:
    trigonometric = load_json(FIXTURES / "periodic_trigonometric_scalar.json")
    trig_artifacts = binary_artifacts("periodic-trigonometric.f64.gz")
    assert validate_volumetric_payload(trigonometric["payload"], trig_artifacts).valid
    assert validate_volumetric_field(trigonometric["field"]).valid
    assert abs(trigonometric["reference"]["cell_integral"]) < 1e-12

    chunked = load_json(FIXTURES / "chunked_payload.json")
    chunk_artifacts = binary_artifacts(
        "chunked.chunk-0000.gz", "chunked.chunk-0001.gz"
    )
    assert validate_volumetric_payload(chunked["payload"], chunk_artifacts).valid
    assert validate_volumetric_dataset(chunked["dataset"], chunk_artifacts).valid
    assert chunked["logical_hash_matches_unchunked"] is True


def test_scientific_fixtures_preserve_declared_semantics() -> None:
    spin = load_json(FIXTURES / "collinear_spin_dataset.json")
    assert validate_volumetric_dataset(spin["dataset"]).valid
    assert {field["field_name"] for field in spin["dataset"]["fields"]} == {
        "up",
        "down",
        "total",
        "difference",
    }
    vector = load_json(FIXTURES / "noncollinear_magnetization.json")
    assert validate_volumetric_field(vector["field"]).valid
    assert vector["field"]["spin"]["component_basis"] == "cartesian"
    complex_scalar = load_json(FIXTURES / "complex_scalar.json")
    assert validate_volumetric_field(complex_scalar["field"]).valid
    assert complex_scalar["field"]["component_labels"] == ["real", "imag"]
    assert (
        complex_scalar["field"]["complex_semantics"]["representation"]
        == "real_imag_interleaved"
    )
    potential = load_json(FIXTURES / "potential_gauge.json")
    assert validate_volumetric_field(potential["field"]).valid
    assert potential["field"]["potential_reference"]["kind"] == "cell_average_zero"


def test_reference_and_negative_evidence_are_replayable() -> None:
    reference = load_json(EVIDENCE / "references" / "independent_math.json")
    assert reference["binary_decoder"] == {
        "count": 64,
        "format": "<d",
        "integral": 128.0,
        "maximum": 2.0,
        "minimum": 2.0,
    }
    assert reference["flatten_2x3x4x2"]["contiguous"] is True
    assert reference["triclinic_coordinate_1_2_3"] == [
        4.916666666666666,
        3.875,
        3.0,
    ]
    replay = load_json(EVIDENCE / "replay" / "determinism.json")
    assert replay["identical"] is True
    assert replay["hashes"] == replay["replay_hashes"]
    negatives = load_json(FIXTURES / "negative_cases.json")
    assert negatives["all_rejected"] is True
    assert all(code != "UNEXPECTED_ACCEPT" for code in negatives["cases"].values())


def test_phase10j_contract_has_no_tool_or_renderer_registration() -> None:
    contract_source = (
        ROOT
        / "packages"
        / "artifact-core"
        / "mdi_artifact_core"
        / "volumetric_contract.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(contract_source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert imports.isdisjoint(
        {"requests", "urllib", "http", "socket", "pickle", "subprocess"}
    )
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert called_names.isdisjoint({"eval", "exec", "compile", "__import__"})
    assert "Three.js" not in contract_source
    assert "WebGL" not in contract_source
    audit = load_json(EVIDENCE / "pre_implementation_audit.json")
    assert audit["tool_registered"] is False
    assert audit["parser_implemented"] is False
    assert audit["renderer_implemented"] is False
    dependency = load_json(EVIDENCE / "dependency_audit.json")
    assert dependency["new_dependencies"] == []
    assert dependency["lockfile_changed"] is False
    assert dependency["network_required"] is False
