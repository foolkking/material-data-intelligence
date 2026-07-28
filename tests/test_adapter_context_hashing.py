from __future__ import annotations

import pandas as pd

from mdi_adapters.context import ToolExecutionContext, hashable_material
from mdi_schemas import DataProfile


def test_dataframe_hash_covers_all_values_index_columns_and_dtypes(tmp_path) -> None:
    context = _context(tmp_path)
    first = pd.DataFrame({"formula": ["Si", "NaCl"], "value": [1.0, 2.0]}, index=[10, 11])
    changed_tail = pd.DataFrame({"formula": ["Si", "NaCl"], "value": [1.0, 3.0]}, index=[10, 11])
    changed_index = first.copy()
    changed_index.index = [10, 12]

    hashes = context.input_hashes([first, changed_tail, changed_index])

    assert len(set(hashes)) == 3
    assert hashes[0] == context.input_hashes([first.copy()])[0]


def test_profile_hash_covers_semantic_revision(tmp_path) -> None:
    context = _context(tmp_path)
    first = _profile("a" * 64)
    second = _profile("b" * 64)

    assert context.input_hashes([first])[0] != context.input_hashes([second])[0]
    assert hashable_material(first)["semanticHash"] == "a" * 64


def test_non_finite_dataframe_values_have_stable_explicit_tokens(tmp_path) -> None:
    context = _context(tmp_path)
    frame = pd.DataFrame({"value": [float("nan"), float("inf"), float("-inf")]})

    assert context.input_hashes([frame])[0] == context.input_hashes([frame.copy()])[0]


def _context(tmp_path) -> ToolExecutionContext:
    return ToolExecutionContext(
        job_id="job_hash",
        project_id="project_hash",
        dataset_id="dataset_hash",
        tool_id="dataset.materials_explorer",
        tool_version="1.0.0",
        adapter_version="1.0.0",
        registry_version="1.0.0",
        artifact_root=tmp_path,
    )


def _profile(semantic_hash: str) -> DataProfile:
    return DataProfile.model_validate(
        {
            "schemaVersion": "0.1",
            "profileId": "profile_hash_v2",
            "datasetId": "dataset_hash",
            "version": "2",
            "datasetType": "table",
            "files": [],
            "objects": [],
            "qualityIssues": [],
            "recommendedTasks": [],
            "profileContractVersion": "2.0",
            "semanticRulesVersion": "phase10k1.semantic_roles.v1",
            "semanticHash": semantic_hash,
            "semanticColumns": [],
            "semanticGroups": [],
            "resourceSemantics": [],
            "analysisReadiness": [],
            "createdAt": "2026-07-28T00:00:00Z",
        }
    )
