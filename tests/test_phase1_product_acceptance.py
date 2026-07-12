from __future__ import annotations

import json
import zipfile

from pymatgen.core import Structure

from mdi_api.phase1_demo import (
    PHASE1_TOOL_ORDER,
    get_phase1_job_artifacts,
    get_phase1_job_events,
    run_phase1_demo,
)
from mdi_schemas import ArtifactType


def test_phase1_mvp_product_flow_acceptance(tmp_path, repo_root):
    fixture_paths = _phase1_fixture_paths(tmp_path, repo_root)
    artifact_root = tmp_path / "artifacts"

    result = run_phase1_demo(
        fixture_paths,
        user_prompt="Analyze composition, structure quality, and ML prediction errors.",
        artifact_root=artifact_root,
    )

    assert result.project["status"] == "created"
    assert result.dataset["status"] == "profile_ready"

    formats = {item["detectedFormat"] for item in result.uploaded_files}
    assert {"cif", "poscar", "csv", "archive", "json_limited", "xyz", "extxyz"}.issubset(formats)
    assert any(item["status"] == "success" for item in result.uploaded_files)

    assert result.data_profile.structureSummary is not None
    assert result.data_profile.structureSummary["nStructures"] >= 4
    assert result.data_profile.tableSummary is not None
    assert result.data_profile.tableSummary["inferredTask"] == "regression"
    assert result.data_profile.qualityIssues

    planned_tools = [step.toolId for step in result.plan.steps]
    assert planned_tools == list(PHASE1_TOOL_ORDER)
    assert len(result.plan_summary["steps"]) == 10
    assert {"composition", "structure", "ml"} == {tool_id.split(".", 1)[0] for tool_id in planned_tools}

    artifact_types = {artifact.type for artifact in result.artifacts}
    assert {
        ArtifactType.analysis_plan_json,
        ArtifactType.plotly_json,
        ArtifactType.plotly_html,
        ArtifactType.preview_png,
            ArtifactType.structure_json,
        ArtifactType.metrics_json,
        ArtifactType.table_json,
        ArtifactType.table_csv,
        ArtifactType.summary_md,
        ArtifactType.recipe_json,
        ArtifactType.report_md,
        ArtifactType.report_html,
    }.issubset(artifact_types)
    assert ArtifactType.matterviz_html not in artifact_types

    for artifact in result.artifacts:
        path = artifact_root / artifact.storageKey
        assert path.exists(), artifact.storageKey
        assert artifact.metadata.createdAt
        assert artifact.contentHash

    preview = next(artifact for artifact in result.artifacts if artifact.type == ArtifactType.preview_png)
    assert (artifact_root / preview.storageKey).read_bytes().startswith(b"\x89PNG")

    event_types = [event.eventType for event in result.events]
    for required in (
        "upload.started",
        "file.detected",
        "file.parsed",
        "profile.ready",
        "analysis.requested",
        "plan.generated",
        "tool.started",
        "artifact.ready",
        "report.ready",
        "job.completed",
    ):
        assert required in event_types
    assert event_types.count("tool.started") == 10

    assert get_phase1_job_events(result.job_id)
    assert any(item["type"] == "report_html" for item in get_phase1_job_artifacts(result.job_id))


def _phase1_fixture_paths(tmp_path, repo_root):
    structures = repo_root / "tests" / "fixtures" / "structures"
    tables = repo_root / "tests" / "fixtures" / "tables"

    structure = Structure.from_file(structures / "si.cif")
    json_path = tmp_path / "si_structure.json"
    json_path.write_text(json.dumps(structure.as_dict()), encoding="utf-8")

    zip_path = tmp_path / "structure_bundle.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.write(structures / "si.cif", arcname="nested/si.cif")

    return [
        structures / "si.cif",
        structures / "POSCAR",
        tables / "ml_results.csv",
        zip_path,
        json_path,
        structures / "plain.xyz",
        structures / "si_lattice.extxyz",
    ]
