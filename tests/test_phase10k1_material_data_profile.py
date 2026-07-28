from __future__ import annotations

import json
from pathlib import Path

from mdi_material_parsers import NormalizedObjectDraft, ParseResult, build_data_profile, parse_file
from mdi_material_parsers.models import DetectedFormat
from mdi_material_parsers.semantic_profile import (
    MAX_PROFILE_OBJECTS,
    MAX_PROFILE_ROWS,
    resolve_column_name,
    stable_sample_reference,
)
from mdi_schemas import DataProfile, MaterialObjectType


def _csv_profile(tmp_path: Path, text: str, *, dataset_id: str = "dataset_semantics") -> DataProfile:
    path = tmp_path / "materials.csv"
    path.write_text(text, encoding="utf-8")
    result = parse_file(path, dataset_id=dataset_id, file_id="file_table")
    assert result.parse_status == "success"
    return build_data_profile(dataset_id=dataset_id, parse_results=[result])


def _readiness(profile: DataProfile, capability: str):
    return next(item for item in profile.analysisReadiness if item.capability == capability)


def test_profile_2_contract_is_additive_and_old_profile_still_loads():
    old = DataProfile(
        profileId="profile_old",
        datasetId="dataset_old",
        version="1",
        datasetType="unknown",
        createdAt="2026-07-28T00:00:00Z",
    )
    assert old.profileContractVersion is None
    assert old.semanticColumns == []
    assert old.analysisReadiness == []


def test_regression_multiple_models_uncertainty_and_formula_parseability(tmp_path):
    profile = _csv_profile(
        tmp_path,
        "material_id,formula,y_true,model_a_pred,model_a_std,model_b_pred,model_b_std\n"
        "s1,Si,1.0,1.1,0.1,0.9,0.2\n"
        "s2,not-a-formula,2.0,2.1,0.2,1.8,0.3\n",
    )

    assert profile.profileContractVersion == "2.0"
    assert profile.sampleIdentity is not None
    assert profile.sampleIdentity.policy == "explicit_column"
    groups = {item.groupId.rsplit(":regression:", 1)[-1]: item for item in profile.semanticGroups}
    assert set(groups) == {"model_a", "model_b"}
    assert all(group.status == "COMPLETE" and group.targetColumns == ["y_true"] for group in groups.values())
    assert groups["model_a"].predictionColumns == ["model_a_pred"]
    assert groups["model_a"].uncertaintyColumns == ["model_a_std"]
    assert groups["model_a"].seriesBindings[0].model_dump() == {
        "seriesId": "model_a",
        "predictionColumn": "model_a_pred",
        "uncertaintyColumns": ["model_a_std"],
    }
    assert groups["model_b"].seriesBindings[0].predictionColumn == "model_b_pred"
    assert groups["model_b"].seriesBindings[0].uncertaintyColumns == ["model_b_std"]
    formula = next(column for column in profile.semanticColumns if column.column == "formula")
    assert formula.roles[0].details == {"validCount": 1, "invalidCount": 1, "inspectedCount": 2, "tooLongCount": 0}
    assert {issue["code"] for issue in profile.qualityIssues} >= {"FORMULA_VALUES_PARTIALLY_INVALID"}
    assert _readiness(profile, "regression_evaluation").dataStatus == "READY"
    assert _readiness(profile, "regression_evaluation").platformStatus == "NOT_EVALUATED"
    assert _readiness(profile, "uncertainty_evaluation").dataStatus == "READY"
    assert _readiness(profile, "uncertainty_evaluation").platformStatus == "NOT_EVALUATED"


def test_multi_target_groups_remain_distinct(tmp_path):
    profile = _csv_profile(
        tmp_path,
        "formation_energy_true,formation_energy_pred,band_gap_true,band_gap_pred\n-1.2,-1.1,1.0,1.1\n",
    )
    groups = {group.groupId.rsplit(":regression:", 1)[-1]: group for group in profile.semanticGroups}
    assert set(groups) == {"band_gap", "formation_energy"}
    assert all(group.status == "COMPLETE" for group in groups.values())


def test_ambiguous_regression_target_is_not_silently_selected(tmp_path):
    profile = _csv_profile(tmp_path, "y_true,target,y_pred\n1,1,1.1\n2,2,2.1\n")
    group = profile.semanticGroups[0]
    assert group.status == "AMBIGUOUS"
    assert group.targetColumns == ["target", "y_true"]
    readiness = _readiness(profile, "regression_evaluation")
    assert readiness.dataStatus == "AMBIGUOUS"
    assert "MULTIPLE_TARGET_COLUMNS" in readiness.reasons


def test_classification_probability_group_and_normalization(tmp_path):
    valid = _csv_profile(
        tmp_path,
        "class_true,class_pred,prob_A,prob_B\nA,A,0.8,0.2\nB,A,0.4,0.6\n",
        dataset_id="dataset_classification",
    )
    group = next(item for item in valid.semanticGroups if item.kind == "classification")
    assert group.status == "COMPLETE"
    assert group.classes == ["a", "b"]
    assert _readiness(valid, "classification_evaluation").dataStatus == "READY"
    assert _readiness(valid, "classification_evaluation").platformStatus == "NOT_EVALUATED"

    invalid = _csv_profile(
        tmp_path,
        "class_true,class_pred,prob_A,prob_B\nA,A,0.9,0.9\n",
        dataset_id="dataset_bad_probabilities",
    )
    bad_group = next(item for item in invalid.semanticGroups if item.kind == "classification")
    assert bad_group.status == "INCOMPLETE"
    assert "PROBABILITY_ROWS_NOT_NORMALIZED" in bad_group.reasons

    probabilities_only = _csv_profile(
        tmp_path,
        "class_true,prob_A,prob_B\nA,0.8,0.2\n",
        dataset_id="dataset_probability_output",
    )
    assert _readiness(probabilities_only, "classification_evaluation").dataStatus == "READY"


def test_false_positive_guards_and_finite_numeric_requirement(tmp_path):
    profile = _csv_profile(
        tmp_path,
        "prediction_date,target_temperature,formula_notes,y_true,y_pred\n"
        "2026-01-01,300,note,NaN,NaN\n",
    )
    roles = {column.column: [role.role for role in column.roles] for column in profile.semanticColumns}
    assert roles["prediction_date"] == []
    assert roles["target_temperature"] == []
    assert roles["formula_notes"] == []
    assert roles["y_true"] == []
    assert roles["y_pred"] == []
    assert _readiness(profile, "regression_evaluation").dataStatus == "MISSING_REQUIRED_DATA"

    invalid_formula = _csv_profile(tmp_path, "formula\nnot-a-formula\n", dataset_id="invalid_formula")
    composition = _readiness(invalid_formula, "composition_summary")
    assert composition.dataStatus == "MISSING_REQUIRED_DATA"
    assert composition.reasons == ["NO_PARSEABLE_FORMULA_VALUES"]


def test_formula_property_dtype_guards_and_declared_authority():
    obj = NormalizedObjectDraft(
        id="obj_declared",
        dataset_id="declared",
        object_type=MaterialObjectType.DataFrame,
        source_file_ids=["declared.csv"],
        storage_key="normalized/declared.json",
        metadata={
            "nRows": 1,
            "nColumns": 4,
            "columns": [
                {"name": "formula", "dtype": "number", "missingCount": 0, "uniqueCount": 1},
                {"name": "energy", "dtype": "string", "missingCount": 0, "uniqueCount": 1},
                {"name": "custom_target", "dtype": "number", "missingCount": 0, "uniqueCount": 1, "declaredRole": "regression_target", "groupId": "declared_group"},
                {"name": "custom_prediction", "dtype": "number", "missingCount": 0, "uniqueCount": 1, "semanticRole": "regression_prediction", "semanticGroupId": "declared_group"},
            ],
        },
        hash="d" * 64,
        payload=[{"formula": 12, "energy": "high", "custom_target": 1.0, "custom_prediction": 1.1}],
    )
    result = ParseResult(
        file_id="declared.csv",
        file_path=Path("declared.csv"),
        detected_format=DetectedFormat.csv,
        parse_status="success",
        objects=[obj],
    )
    profile = build_data_profile(dataset_id="declared", parse_results=[result])
    columns = {column.column: column for column in profile.semanticColumns}
    assert columns["formula"].roles == []
    assert columns["energy"].roles == []
    assert columns["custom_target"].roles[0].authority == "user_declared"
    assert columns["custom_prediction"].roles[0].authority == "explicit_metadata"
    assert columns["custom_target"].roles[0].groupId == "obj_declared:declared_group"
    assert profile.semanticGroups[0].status == "COMPLETE"


def test_semantic_object_group_and_unit_caps_are_enforced():
    objects = []
    for index in range(MAX_PROFILE_OBJECTS + 1):
        objects.append(
            NormalizedObjectDraft(
                id=f"obj_{index:03d}",
                dataset_id="bounded_objects",
                object_type=MaterialObjectType.DataFrame,
                source_file_ids=[f"file_{index:03d}"],
                storage_key=f"normalized/{index:03d}.json",
                metadata={
                    "nRows": 1,
                    "nColumns": 1,
                    "columns": [
                        {
                            "name": "y_pred",
                            "dtype": "number",
                            "missingCount": 0,
                            "uniqueCount": 1,
                            "semanticRole": "regression_prediction",
                            "semanticGroupId": "x" * 129,
                            "unit": "u" * 65,
                        }
                    ],
                },
                hash=f"{index:064x}",
                payload=[{"y_pred": float(index)}],
            )
        )
    result = ParseResult(
        file_id="bounded.json",
        file_path=Path("bounded.json"),
        detected_format=DetectedFormat.json_limited,
        parse_status="success",
        objects=objects,
    )
    profile = build_data_profile(dataset_id="bounded_objects", parse_results=[result])
    assert len(profile.resourceSemantics) == MAX_PROFILE_OBJECTS
    assert len(profile.semanticColumns) == MAX_PROFILE_OBJECTS
    assert all(column.unit is None for column in profile.semanticColumns)
    assert all(
        set(column.ambiguities)
        == {"SEMANTIC_GROUP_ID_EXCEEDS_PROFILE_LIMIT", "UNIT_METADATA_EXCEEDS_PROFILE_LIMIT"}
        for column in profile.semanticColumns
    )
    assert "PROFILE_OBJECT_CAP_APPLIED" in {issue["code"] for issue in profile.qualityIssues}


def test_semantic_authority_and_sample_reference_are_deterministic(tmp_path):
    assert resolve_column_name("y_true", dtype="number")[1] == "canonical_name"
    assert resolve_column_name("actual", dtype="number")[1] == "alias_match"
    assert resolve_column_name("prediction_date", dtype="string") is None
    assert stable_sample_reference(dataset_id="d", dataset_version="2", object_hash="a" * 64, row_index=3) == "d@2:aaaaaaaaaaaaaaaa:3"

    first = _csv_profile(tmp_path, "formula,y_true,y_pred\nSi,1,1.1\n", dataset_id="deterministic")
    second = _csv_profile(tmp_path, "formula,y_true,y_pred\nSi,1,1.1\n", dataset_id="deterministic")
    assert first.semanticHash == second.semanticHash
    assert first.createdAt != second.createdAt


def test_duplicate_or_missing_explicit_sample_ids_use_stable_fallback(tmp_path):
    duplicate = _csv_profile(tmp_path, "material_id,formula\ns1,Si\ns1,NaCl\n", dataset_id="duplicate_ids")
    assert duplicate.sampleIdentity is not None
    assert duplicate.sampleIdentity.policy == "object_hash_row_index"
    assert duplicate.sampleIdentity.explicitColumn is None

    missing = _csv_profile(tmp_path, "material_id,formula\ns1,Si\n,NaCl\n", dataset_id="missing_ids")
    assert missing.sampleIdentity is not None
    assert missing.sampleIdentity.policy == "object_hash_row_index"


def test_legacy_field_roles_remain_exact_while_profile_2_roles_expand(tmp_path):
    profile = _csv_profile(
        tmp_path,
        "material_formula,model_a_pred,class_true,class_pred,true\nSi,1.0,A,A,1.0\n",
        dataset_id="legacy_compatibility",
    )
    legacy_roles = {column["name"]: column["inferredRole"] for column in profile.tableSummary["columns"]}
    assert legacy_roles == {
        "material_formula": None,
        "model_a_pred": None,
        "class_true": None,
        "class_pred": None,
        "true": "target",
    }
    semantic_roles = {column.column: [role.role for role in column.roles] for column in profile.semanticColumns}
    assert semantic_roles["material_formula"] == ["material_formula"]
    assert semantic_roles["model_a_pred"] == ["regression_prediction"]
    assert semantic_roles["class_true"] == ["classification_target"]
    assert semantic_roles["class_pred"] == ["classification_prediction"]


def test_profile_sampling_is_bounded_and_disclosed(tmp_path):
    rows = ["formula,y_true,y_pred"] + [f"Si,{index},{index + 0.1}" for index in range(MAX_PROFILE_ROWS + 3)]
    profile = _csv_profile(tmp_path, "\n".join(rows), dataset_id="bounded")
    assert profile.profileCoverage is not None
    assert profile.profileCoverage.policy == "deterministic_bounded_sample"
    assert profile.profileCoverage.rowsInspected == MAX_PROFILE_ROWS
    assert "PROFILE_ROW_SAMPLE_APPLIED" in profile.profileCoverage.warnings


def test_structure_trajectory_phonon_and_volumetric_resource_bridges(repo_root, tmp_path):
    structure = parse_file(
        repo_root / "tests" / "fixtures" / "structures" / "si.cif",
        dataset_id="resource_bridges",
        file_id="file_structure",
    )
    trajectory = parse_file(
        repo_root / "docs" / "phase10g" / "fixtures" / "trajectory_import" / "fixed_lattice_md.extxyz",
        dataset_id="resource_bridges",
        file_id="file_trajectory",
    )
    volumetric = parse_file(
        repo_root / "docs" / "phase10j" / "fixtures" / "volumetric_parser" / "orthogonal.cube",
        dataset_id="resource_bridges",
        file_id="file_volume",
    )
    phonon_obj = NormalizedObjectDraft(
        id="obj_phonon_band",
        dataset_id="resource_bridges",
        object_type=MaterialObjectType.PhononBand,
        source_file_ids=["file_phonon"],
        storage_key="normalized/phonon.json",
        metadata={"qPointCount": 12, "frequencyCount": 36},
        hash="b" * 64,
        payload={"schema_version": "phase10h.phonon_band.v1"},
    )
    phonon = ParseResult(
        file_id="file_phonon",
        file_path=tmp_path / "phonon.json",
        detected_format=DetectedFormat.json_limited,
        parse_status="success",
        objects=[phonon_obj],
    )

    profile = build_data_profile(
        dataset_id="resource_bridges",
        parse_results=[structure, trajectory, volumetric, phonon],
    )
    capabilities = {capability for resource in profile.resourceSemantics for capability in resource.capabilities}
    assert capabilities >= {"composition", "structure", "trajectory", "phonon", "volumetric"}
    assert profile.trajectorySummary["frameCount"] > 1
    assert profile.phononSummary["resourceKinds"] == ["PhononBand"]
    assert _readiness(profile, "trajectory_visualization").dataStatus == "READY"
    assert _readiness(profile, "phonon_visualization").dataStatus == "READY"
    assert _readiness(profile, "volumetric_visualization").dataStatus == "READY"


def test_profile_json_has_no_executable_or_external_metadata(tmp_path):
    profile = _csv_profile(tmp_path, "formula,y_true,y_pred\nSi,1,1.1\n")
    serialized = json.dumps(profile.model_dump(mode="json"), sort_keys=True)
    lowered = serialized.lower()
    assert "<script" not in lowered
    assert "javascript:" not in lowered
    assert "http://" not in lowered
    assert "https://" not in lowered
