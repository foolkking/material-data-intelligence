from __future__ import annotations

import json
import zipfile
import pytest

from pymatgen.core import Lattice, Structure

from mdi_material_parsers import DetectedFormat, build_data_profile, detect_format, parse_dataset, parse_file
from mdi_schemas import DataProfile, MaterialObjectType


def test_detects_supported_mvp_formats(repo_root):
    assert detect_format(repo_root / "tests" / "fixtures" / "structures" / "si.cif") == DetectedFormat.cif
    assert detect_format(repo_root / "tests" / "fixtures" / "structures" / "POSCAR") == DetectedFormat.poscar
    assert detect_format(repo_root / "tests" / "fixtures" / "tables" / "ml_results.csv") == DetectedFormat.csv
    assert detect_format(repo_root / "tests" / "fixtures" / "structures" / "plain.xyz") == DetectedFormat.xyz


def test_parse_cif_and_poscar_to_structure_objects(repo_root):
    paths = [
        repo_root / "tests" / "fixtures" / "structures" / "si.cif",
        repo_root / "tests" / "fixtures" / "structures" / "POSCAR",
    ]
    results, objects = parse_dataset(paths, dataset_id="dataset_structures")

    assert [result.parse_status for result in results] == ["success", "success"]
    assert [obj.object_type for obj in objects] == [MaterialObjectType.Structure, MaterialObjectType.Structure]
    assert all(obj.metadata["periodicity"] == "periodic" for obj in objects)
    assert {obj.metadata["formula"] for obj in objects} == {"Si"}


def test_parse_csv_and_build_ml_profile(repo_root):
    result = parse_file(
        repo_root / "tests" / "fixtures" / "tables" / "ml_results.csv",
        dataset_id="dataset_ml",
        file_id="file_ml",
    )
    profile = build_data_profile(dataset_id="dataset_ml", parse_results=[result])

    assert result.parse_status == "success"
    assert result.objects[0].object_type == MaterialObjectType.DataFrame
    assert profile.datasetType == "ml_results"
    assert profile.tableSummary["nRows"] == 3
    assert profile.tableSummary["inferredTask"] == "regression"
    assert {column["inferredRole"] for column in profile.tableSummary["columns"]} >= {"formula", "target", "prediction"}
    assert profile.recommendedTasks[0]["taskId"] == "ml.evaluation"
    assert profile.recommendedTasks[0]["availableNow"] is False
    assert profile.recommendedTasks[0]["platformStatus"] == "NOT_EVALUATED"
    assert "planned" not in profile.recommendedTasks[0]["reason"]


@pytest.mark.parametrize("tools,available", [(None, False), (set(), False), ({"ml.regression_evaluation"}, False), ("full", True)])
def test_regression_recommendation_uses_current_registry_and_complete_semantic_groups(repo_root, tools, available):
    from mdi_material_parsers.profile import REGRESSION_RECOMMENDATION_TOOLS
    tool_ids = set(REGRESSION_RECOMMENDATION_TOOLS) if tools == "full" else tools
    result = parse_file(repo_root / "tests/fixtures/tables/ml_results.csv", dataset_id="ml", file_id="ml")
    profile = build_data_profile(dataset_id="ml", parse_results=[result], platform_tool_ids=tool_ids)
    recommendation = next(t for t in profile.recommendedTasks if t["taskId"] == "ml.evaluation")
    assert recommendation["availableNow"] is available
    assert recommendation["dataStatus"] == "READY"
    assert set(recommendation["requiredTools"]) == set(REGRESSION_RECOMMENDATION_TOOLS)


@pytest.mark.parametrize("columns,rows,status", [
    ("y_true,y_pred", "1,1.1", "READY"),
    ("y_true,target,y_pred", "1,2,1.1", "AMBIGUOUS"),
    ("y_true", "1", "MISSING_REQUIRED_DATA"),
])
def test_regression_recommendation_is_not_inferred_from_the_first_table(tmp_path, columns, rows, status):
    from mdi_material_parsers.profile import REGRESSION_RECOMMENDATION_TOOLS
    ordinary = tmp_path / "ordinary.csv"; ordinary.write_text("name,count\nsample,3\n")
    regression = tmp_path / "regression.csv"; regression.write_text(f"{columns}\n{rows}\n")
    parsed = [parse_file(path, dataset_id="ml", file_id=f"file-{i}") for i, path in enumerate([ordinary, regression])]
    profile = build_data_profile(dataset_id="ml", parse_results=parsed, platform_tool_ids=set(REGRESSION_RECOMMENDATION_TOOLS))
    task = next(t for t in profile.recommendedTasks if t["taskId"] == "ml.evaluation")
    assert task["dataStatus"] == status
    assert task["availableNow"] is (status == "READY")


@pytest.mark.parametrize("durable", [False, True])
def test_profile_api_projects_current_recommendation_without_mutating_saved_execution_profile(monkeypatch, repo_root, durable):
    from types import SimpleNamespace as NS
    from mdi_api.infrastructure.phase2 import runtime as api
    from mdi_material_parsers.profile import REGRESSION_RECOMMENDATION_TOOLS
    parsed = parse_file(repo_root / "tests/fixtures/tables/ml_results.csv", dataset_id="ml", file_id="ml")
    saved = build_data_profile(dataset_id="ml", parse_results=[parsed]).model_dump(mode="json")
    saved["recommendedTasks"] = [{"taskId": "ml.evaluation", "availableNow": False, "reason": "planned"}, {"taskId": "custom", "label": "Keep me"}]
    before = json.dumps(saved)
    runtime = NS(datasets={} if durable else {"ml": object()}, registry=NS(tools=[NS(toolId=t) for t in REGRESSION_RECOMMENDATION_TOOLS]),
                 get_dataset_profile=lambda _: saved, create_dataset_profile=lambda _: {**saved, "profileGenerated": True},
                 get_dataset_profile_model=lambda _: DataProfile.model_validate(saved))
    repositories = NS(datasets=NS(get=lambda _: {}), data_profiles=NS(list_for_dataset=lambda _: [saved]))
    monkeypatch.setattr(api, "get_phase2_runtime", lambda: runtime)
    monkeypatch.setattr(api, "_durable_read_repositories", lambda: repositories)
    for reader in [api.get_phase2_dataset_profile, api.create_phase2_dataset_profile]:
        output = reader("ml")
        assert next(t for t in output["recommendedTasks"] if t["taskId"] == "ml.evaluation")["availableNow"] is True
        assert {k: v for k, v in output.items() if k not in {"recommendedTasks", "profileGenerated"}} == {k: v for k, v in saved.items() if k != "recommendedTasks"}
        assert output["recommendedTasks"][0] == {"taskId": "custom", "label": "Keep me"}
    assert api.get_phase2_dataset_profile_model("ml").recommendedTasks[0]["reason"] == "planned"
    assert json.dumps(saved) == before


def test_parse_json_limited_structure(tmp_path):
    structure = Structure(Lattice.cubic(3), ["Si"], [[0, 0, 0]])
    path = tmp_path / "structure.json"
    path.write_text(json.dumps(structure.as_dict()), encoding="utf-8")

    result = parse_file(path, dataset_id="dataset_json", file_id="file_json")

    assert result.parse_status == "success"
    assert result.detected_format == DetectedFormat.json_limited
    assert result.objects[0].object_type == MaterialObjectType.Structure
    assert result.objects[0].metadata["formula"] == "Si"


def test_parse_extxyz_with_lattice_to_periodic_structure(repo_root):
    result = parse_file(
        repo_root / "tests" / "fixtures" / "structures" / "si_lattice.extxyz",
        dataset_id="dataset_extxyz",
        file_id="file_extxyz",
    )
    profile = build_data_profile(dataset_id="dataset_extxyz", parse_results=[result])

    assert result.detected_format == DetectedFormat.extxyz
    assert result.parse_status == "success"
    assert result.objects[0].object_type == MaterialObjectType.Structure
    assert result.objects[0].metadata["periodicity"] == "periodic"
    assert profile.datasetType == "structure_collection"


def test_build_structure_profile_and_recommendations(repo_root):
    result = parse_file(
        repo_root / "tests" / "fixtures" / "structures" / "si.cif",
        dataset_id="dataset_profile",
        file_id="file_cif",
    )
    profile = build_data_profile(dataset_id="dataset_profile", parse_results=[result])

    assert profile.datasetType == "structure_collection"
    assert profile.structureSummary["nStructures"] == 1
    assert profile.structureSummary["elements"] == ["Si"]
    assert {task["taskId"] for task in profile.recommendedTasks} == {"composition.overview", "structure.viewer"}


def test_plain_xyz_detected_but_not_normalized_as_periodic_structure(repo_root):
    result = parse_file(
        repo_root / "tests" / "fixtures" / "structures" / "plain.xyz",
        dataset_id="dataset_xyz",
        file_id="file_xyz",
    )
    profile = build_data_profile(dataset_id="dataset_xyz", parse_results=[result])

    assert result.detected_format == DetectedFormat.xyz
    assert result.parse_status == "success"
    assert result.objects[0].object_type == MaterialObjectType.Atoms
    assert result.objects[0].metadata["periodicity"] == "non_periodic"
    assert all(obj["objectType"] != MaterialObjectType.Structure.value for obj in profile.objects)
    assert profile.qualityIssues[0]["code"] == "NON_PERIODIC_ATOMS"


def test_parse_zip_with_unsafe_member_paths(repo_root, tmp_path):
    archive_path = tmp_path / "bundle.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.write(repo_root / "tests" / "fixtures" / "structures" / "si.cif", arcname="safe/si.cif")
        archive.writestr("../evil.txt", "nope")

    result = parse_file(archive_path, dataset_id="dataset_zip", file_id="file_zip")

    assert result.detected_format == DetectedFormat.archive
    assert result.parse_status == "partial"
    assert result.error_code == "ARCHIVE_PARTIAL_OR_UNSUPPORTED"
    assert len(result.objects) == 1
    assert result.objects[0].object_type == MaterialObjectType.Structure
