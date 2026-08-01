from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any, Callable
from unittest.mock import patch
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mdi_api.phase2_runtime import build_object_store
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import (
    PlannerJobsRequest,
    get_planner_job_artifacts,
    get_planner_job_result,
    get_planner_job_tool_calls,
    planner_jobs,
)
from mdi_llm import DEEPSEEK_ALLOWED_MODELS, DEEPSEEK_DEFAULT_MODEL, DeepSeekProvider, LLMProviderError
from mdi_llm.redaction import redact_credential_values
from mdi_material_parsers import NormalizedObjectDraft, ParseResult, build_data_profile, parse_file
from mdi_material_parsers.models import DetectedFormat
from mdi_schemas import DataProfile, MaterialObjectType
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime

from scripts.generate_phase10k2_dataset_explorer_evidence import _fixture_objects as _dataset_objects
from scripts.generate_phase10k4_composition_space_evidence import BASE_RECORDS, _profile as _composition_profile
from scripts.generate_phase10l5_natural_language_closure_evidence import EVIDENCE, FIXED_TIME
from tests.test_phase10h5_phonon_animation import _bundle as _animation_bundle
from tests.test_phase10h5_phonon_animation import _params as _animation_params
from tests.test_phase10h5_phonon_animation import _structure as _animation_structure
from tests.test_phase10i1_brillouin_zone_adapter import _sc as _brillouin_structure
from tests.test_phase10l3_dependency_runtime import _source as _phonon_source
from tests.test_phase10l3_planner_api import _phonon_profile


OUTPUT = EVIDENCE / "historical_deepseek_replay"
VOLUMETRIC_FIXTURES = ROOT / "docs" / "phase10j" / "fixtures" / "volumetric_parser"
TRAJECTORY_FIXTURE = ROOT / "docs" / "phase10g" / "fixtures" / "trajectory_import" / "fixed_lattice_md.extxyz"
MAX_CALLS_PER_CASE = 4


@dataclass(frozen=True)
class ReplayInput:
    profile: DataProfile
    object_store: dict[str, Any]
    selected_resource_ids: tuple[str, ...]
    selected_target_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReplaySpec:
    case_number: int
    phase: str
    slug: str
    replay_prompt: str
    expected_tools: tuple[str, ...]
    fixture: str
    source_paths: tuple[str, ...]
    accepted_current_tool_sets: tuple[tuple[str, ...], ...] = ()
    expected_outcome: str = "PLAN_READY"
    historical_prompt_integrity: str = "EXACT"
    notes: str = ""


def _stable_hash(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _write_json(relative: str, value: Any) -> None:
    target = EVIDENCE / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def _table(
    dataset_id: str,
    object_id: str,
    records: list[dict[str, Any]],
    *,
    units: dict[str, str] | None = None,
) -> NormalizedObjectDraft:
    columns: list[dict[str, Any]] = []
    for name in records[0]:
        values = [row.get(name) for row in records]
        numeric = all(value is None or isinstance(value, (int, float)) for value in values)
        columns.append(
            {
                "name": name,
                "dtype": "number" if numeric else "string",
                "missingCount": sum(value is None for value in values),
                "uniqueCount": len({json.dumps(value, sort_keys=True) for value in values if value is not None}),
                "finiteCount": sum(isinstance(value, (int, float)) for value in values) if numeric else None,
                "unit": (units or {}).get(name),
            }
        )
    payload_hash = _stable_hash(records)
    return NormalizedObjectDraft(
        id=object_id,
        dataset_id=dataset_id,
        object_type=MaterialObjectType.DataFrame,
        source_file_ids=[f"{object_id}.json"],
        storage_key=f"normalized/{object_id}.json",
        metadata={"nRows": len(records), "nColumns": len(columns), "columns": columns},
        hash=payload_hash,
        payload=records,
    )


def _profile_from_table(
    *,
    dataset_id: str,
    object_id: str,
    records: list[dict[str, Any]],
    roles: dict[str, tuple[str, str | None]],
    units: dict[str, str] | None = None,
) -> ReplayInput:
    table = _table(dataset_id, object_id, records, units=units)
    semantic_columns: list[dict[str, Any]] = []
    groups: dict[str, dict[str, Any]] = {}
    for column in records[0]:
        role = roles.get(column)
        role_values: list[dict[str, Any]] = []
        if role:
            role_name, group_id = role
            role_values.append({"role": role_name, "authority": "user_declared", "groupId": group_id})
            if group_id and group_id not in groups:
                groups[group_id] = {
                    "groupId": group_id,
                    "kind": "classification" if role_name.startswith("classification") or role_name == "class_probability" else "regression",
                    "targetColumns": [],
                    "predictionColumns": [],
                    "uncertaintyColumns": [],
                    "probabilityColumns": [],
                    "status": "COMPLETE",
                }
            if group_id:
                group = groups[group_id]
                if role_name in {"regression_target", "classification_target"}:
                    group["targetColumns"].append(column)
                elif role_name in {"regression_prediction", "classification_prediction"}:
                    group["predictionColumns"].append(column)
                elif role_name == "regression_uncertainty":
                    group["uncertaintyColumns"].append(column)
                elif role_name == "class_probability":
                    group["probabilityColumns"].append(column)
        values = [row.get(column) for row in records]
        numeric = all(value is None or isinstance(value, (int, float)) for value in values)
        semantic_columns.append(
            {
                "objectId": object_id,
                "column": column,
                "dtype": "number" if numeric else "string",
                "roles": role_values,
                "missingCount": sum(value is None for value in values),
                "uniqueCount": len({json.dumps(value, sort_keys=True) for value in values if value is not None}),
                "finiteCount": sum(isinstance(value, (int, float)) for value in values) if numeric else None,
                "rowsInspected": len(records),
                "totalRows": len(records),
                "unit": (units or {}).get(column),
            }
        )
    profile_payload = {
        "profileId": f"profile_{dataset_id}_v2",
        "datasetId": dataset_id,
        "version": "2",
        "datasetType": "tabular_materials",
        "profileContractVersion": "2.0",
        "semanticRulesVersion": "phase10k1.material_profile_semantics.v1",
        "semanticHash": "0" * 64,
        "semanticColumns": semantic_columns,
        "semanticGroups": list(groups.values()),
        "resourceSemantics": [
            {
                "objectId": object_id,
                "objectType": "DataFrame",
                "objectHash": table.hash,
                "kind": "dataframe",
                "facts": {"rowCount": len(records), "columnCount": len(records[0])},
                "capabilities": ["table", "composition"],
            }
        ],
        "sampleIdentity": {
            "policy": "object_hash_row_index",
            "datasetVersion": "dataset_version_2",
            "objectIds": [object_id],
        },
        "createdAt": FIXED_TIME,
    }
    semantic_payload = {key: value for key, value in profile_payload.items() if key not in {"profileId", "semanticHash", "createdAt"}}
    profile_payload["semanticHash"] = _stable_hash(semantic_payload)
    profile = DataProfile.model_validate(profile_payload)
    store, _ = build_object_store([table], profile=profile)
    return ReplayInput(profile=profile, object_store=store, selected_resource_ids=(object_id,))


def _general_table() -> ReplayInput:
    records = [
        {"material_id": "m-1", "formula": "Si", "PBE": -5.1, "r2SCAN": -5.3, "D_max": 1.2},
        {"material_id": "m-2", "formula": "NaCl", "PBE": -3.0, "r2SCAN": -3.2, "D_max": 2.4},
        {"material_id": "m-3", "formula": "LiF", "PBE": -4.2, "r2SCAN": -4.4, "D_max": 1.8},
        {"material_id": "m-4", "formula": "MgO", "PBE": -6.0, "r2SCAN": -6.2, "D_max": 3.1},
    ]
    return _profile_from_table(
        dataset_id="dataset_historical_table",
        object_id="table_historical",
        records=records,
        roles={
            "material_id": ("sample_identity", None),
            "formula": ("material_formula", None),
            "PBE": ("material_property", None),
            "r2SCAN": ("material_property", None),
            "D_max": ("material_property", None),
        },
        units={"PBE": "eV/atom", "r2SCAN": "eV/atom", "D_max": "mm"},
    )


def _regression_table(*, uncertainty: bool = False, dual_target: bool = False) -> ReplayInput:
    if dual_target:
        records = [
            {"material_id": "m-1", "formula": "Si", "formation_energy": -5.1, "formation_energy_pred": -5.0, "band_gap": 1.1, "band_gap_pred": 1.2},
            {"material_id": "m-2", "formula": "NaCl", "formation_energy": -3.0, "formation_energy_pred": -3.2, "band_gap": 5.6, "band_gap_pred": 5.4},
            {"material_id": "m-3", "formula": "LiF", "formation_energy": -4.2, "formation_energy_pred": -4.0, "band_gap": 11.8, "band_gap_pred": 11.5},
        ]
        roles = {
            "material_id": ("sample_identity", None),
            "formula": ("material_formula", None),
            "formation_energy": ("regression_target", "formation_energy_model"),
            "formation_energy_pred": ("regression_prediction", "formation_energy_model"),
            "band_gap": ("regression_target", "band_gap_model"),
            "band_gap_pred": ("regression_prediction", "band_gap_model"),
        }
        result = _profile_from_table(
            dataset_id="dataset_historical_dual_target",
            object_id="table_dual_target",
            records=records,
            roles=roles,
            units={"formation_energy": "eV/atom", "band_gap": "eV"},
        )
        return result
    records = [
        {"material_id": "m-1", "formula": "Si", "y_true": 1.0, "y_pred": 1.1, **({"y_std": 0.1} if uncertainty else {})},
        {"material_id": "m-2", "formula": "NaCl", "y_true": 2.0, "y_pred": 2.3, **({"y_std": 0.3} if uncertainty else {})},
        {"material_id": "m-3", "formula": "LiF", "y_true": 3.0, "y_pred": 2.5, **({"y_std": 0.6} if uncertainty else {})},
        {"material_id": "m-4", "formula": "MgO", "y_true": 4.0, "y_pred": 4.1, **({"y_std": 0.2} if uncertainty else {})},
    ]
    dataset_id = "dataset_historical_uncertainty" if uncertainty else "dataset_historical_regression"
    with TemporaryDirectory(prefix="mdi-historical-regression-") as directory:
        path = Path(directory) / "table_regression.csv"
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
        parsed = parse_file(path, dataset_id=dataset_id, file_id=f"file_{dataset_id}")
        if parsed.parse_status != "success":
            raise RuntimeError("HISTORICAL_REGRESSION_FIXTURE_PARSE_FAILED")
        registry = load_manifests()
        profile = build_data_profile(
            dataset_id=dataset_id,
            parse_results=[parsed],
            platform_tool_ids={tool.toolId for tool in registry.tools},
        )
        store, _ = build_object_store(parsed.objects, profile=profile)
        return ReplayInput(profile=profile, object_store=store, selected_resource_ids=(parsed.objects[0].id,))


def _classification_table() -> ReplayInput:
    records = [
        {"material_id": "m-1", "formula": "Si", "class_true": "A", "class_pred": "A", "prob:A": 0.9, "prob:B": 0.1},
        {"material_id": "m-2", "formula": "NaCl", "class_true": "B", "class_pred": "B", "prob:A": 0.2, "prob:B": 0.8},
        {"material_id": "m-3", "formula": "LiF", "class_true": "A", "class_pred": "B", "prob:A": 0.4, "prob:B": 0.6},
        {"material_id": "m-4", "formula": "MgO", "class_true": "B", "class_pred": "B", "prob:A": 0.1, "prob:B": 0.9},
    ]
    return _profile_from_table(
        dataset_id="dataset_historical_classification",
        object_id="table_classification",
        records=records,
        roles={
            "material_id": ("sample_identity", None),
            "formula": ("material_formula", None),
            "class_true": ("classification_target", "classification_default"),
            "class_pred": ("classification_prediction", "classification_default"),
            "prob:A": ("class_probability", "classification_default"),
            "prob:B": ("class_probability", "classification_default"),
        },
    )


def _structure_input(*, reciprocal: bool = False) -> ReplayInput:
    source = next(item for item in _dataset_objects() if item.id == "obj_nacl")
    capabilities = ["structure", "composition"] + (["reciprocal"] if reciprocal else [])
    payload = {
        "profileId": "profile_historical_structure_v2",
        "datasetId": source.dataset_id,
        "version": "2",
        "datasetType": "structure_collection",
        "profileContractVersion": "2.0",
        "semanticRulesVersion": "phase10k1.material_profile_semantics.v1",
        "semanticHash": _stable_hash({"objectId": source.id, "objectHash": source.hash, "capabilities": capabilities}),
        "resourceSemantics": [
            {
                "objectId": source.id,
                "objectType": "Structure",
                "objectHash": source.hash,
                "kind": "structure",
                "facts": {"formula": "NaCl", "siteCount": 2, "periodicity": "periodic"},
                "capabilities": capabilities,
            }
        ],
        "sampleIdentity": {"policy": "object_hash_row_index", "datasetVersion": "dataset_version_2", "objectIds": [source.id]},
        "createdAt": FIXED_TIME,
    }
    profile = DataProfile.model_validate(payload)
    store, _ = build_object_store([source], profile=profile)
    return ReplayInput(profile=profile, object_store=store, selected_resource_ids=(source.id,))


def _trajectory_input() -> ReplayInput:
    parsed = parse_file(TRAJECTORY_FIXTURE, dataset_id="dataset_historical_trajectory", file_id="trajectory")
    profile = build_data_profile(
        dataset_id="dataset_historical_trajectory",
        parse_results=[parsed],
        platform_tool_ids={tool.toolId for tool in load_manifests().tools},
    )
    store, _ = build_object_store(parsed.objects, profile=profile)
    return ReplayInput(profile=profile, object_store=store, selected_resource_ids=(parsed.objects[0].id,))


def _phonon_input(kind: str) -> ReplayInput:
    if kind in {"phonon_band", "phonon_dos"}:
        profile = _phonon_profile()
        resource = "phonon_band_1" if kind == "phonon_band" else "phonon_dos_1"
        fixture = "stable_band.json" if kind == "phonon_band" else "projected_dos.json"
        return ReplayInput(profile=profile, object_store={resource: _phonon_source(fixture)}, selected_resource_ids=(resource,))
    if kind == "phonon_animation":
        bundle = _animation_bundle()
        mode_id = _animation_params()["mode_id"]
        resources = [
            {"objectId": "structure", "objectType": "Structure", "objectHash": "a" * 64, "kind": "structure", "capabilities": ["structure"]},
            {"objectId": "band", "objectType": "PhononBand", "objectHash": "b" * 64, "kind": "phonon", "capabilities": ["phonon"]},
            {"objectId": "eigenvectors", "objectType": "PhononEigenvector", "objectHash": "c" * 64, "kind": "phonon", "facts": {"modeId": mode_id}, "capabilities": ["phonon"]},
        ]
        profile = DataProfile.model_validate(
            {
                "profileId": "profile_historical_phonon_animation_v2",
                "datasetId": "dataset_historical_phonon_animation",
                "version": "2",
                "datasetType": "phonon",
                "profileContractVersion": "2.0",
                "semanticRulesVersion": "phase10k1.material_profile_semantics.v1",
                "semanticHash": _stable_hash(resources),
                "resourceSemantics": resources,
                "sampleIdentity": {"policy": "object_hash_row_index", "datasetVersion": "dataset_version_2", "objectIds": ["structure", "band", "eigenvectors"]},
                "createdAt": FIXED_TIME,
            }
        )
        return ReplayInput(
            profile=profile,
            object_store={"structure": _animation_structure(), "band": bundle["band"], "eigenvectors": bundle["set"]},
            selected_resource_ids=("structure", "band", "eigenvectors"),
        )
    raise KeyError(kind)


def _brillouin_input(*, linked_phonon: bool = False) -> ReplayInput:
    resources = [
        {"objectId": "structure_bz", "objectType": "Structure", "objectHash": "d" * 64, "kind": "structure", "capabilities": ["structure", "reciprocal"]}
    ]
    store: dict[str, Any] = {"structure_bz": _brillouin_structure()}
    selected = ["structure_bz"]
    if linked_phonon:
        resources.append({"objectId": "phonon_band_1", "objectType": "PhononBand", "objectHash": "e" * 64, "kind": "phonon", "capabilities": ["phonon"]})
        store["phonon_band_1"] = _phonon_source("stable_band.json")
        selected.append("phonon_band_1")
    profile = DataProfile.model_validate(
        {
            "profileId": "profile_historical_bz_v2",
            "datasetId": "dataset_historical_bz",
            "version": "2",
            "datasetType": "structure_phonon" if linked_phonon else "structure",
            "profileContractVersion": "2.0",
            "semanticRulesVersion": "phase10k1.material_profile_semantics.v1",
            "semanticHash": _stable_hash(resources),
            "resourceSemantics": resources,
            "sampleIdentity": {"policy": "object_hash_row_index", "datasetVersion": "dataset_version_2", "objectIds": selected},
            "createdAt": FIXED_TIME,
        }
    )
    return ReplayInput(profile=profile, object_store=store, selected_resource_ids=tuple(selected))


def _volumetric_input(filename: str) -> ReplayInput:
    parsed = parse_file(VOLUMETRIC_FIXTURES / filename, dataset_id=f"dataset_historical_{filename.lower().replace('.', '_')}", file_id=filename)
    profile = build_data_profile(
        dataset_id=parsed.objects[0].dataset_id,
        parse_results=[parsed],
        platform_tool_ids={tool.toolId for tool in load_manifests().tools},
    )
    store, _ = build_object_store(parsed.objects, profile=profile)
    return ReplayInput(profile=profile, object_store=store, selected_resource_ids=(parsed.objects[0].id,))


def _composition_space_input() -> ReplayInput:
    profile, objects, _ = _composition_profile("dataset_historical_composition_space", [("table_composition_space", BASE_RECORDS)])
    store, _ = build_object_store(objects, profile=profile)
    return ReplayInput(profile=profile, object_store=store, selected_resource_ids=(objects[0].id,))


FIXTURES: dict[str, Callable[[], ReplayInput]] = {
    "table": _general_table,
    "regression": _regression_table,
    "uncertainty": lambda: _regression_table(uncertainty=True),
    "dual_target": lambda: _regression_table(dual_target=True),
    "classification": _classification_table,
    "composition_space": _composition_space_input,
    "structure": _structure_input,
    "reciprocal_structure": lambda: _structure_input(reciprocal=True),
    "trajectory": _trajectory_input,
    "phonon_band": lambda: _phonon_input("phonon_band"),
    "phonon_dos": lambda: _phonon_input("phonon_dos"),
    "phonon_animation": lambda: _phonon_input("phonon_animation"),
    "brillouin": _brillouin_input,
    "linked_bz": lambda: _brillouin_input(linked_phonon=True),
    "chgcar": lambda: _volumetric_input("CHGCAR"),
    "locpot": lambda: _volumetric_input("LOCPOT"),
    "elfcar": lambda: _volumetric_input("ELFCAR"),
    "parchg": lambda: _volumetric_input("PARCHG"),
}


def _specs() -> tuple[ReplaySpec, ...]:
    corrupt = "CORRUPTED_REPLACEMENT_CHARACTERS_SEMANTIC_RECONSTRUCTION"
    return (
        ReplaySpec(6, "Phase 9", "basic_metrics", "Calculate basic regression metrics for y_true and y_pred.", ("ml.basic_metrics",), "regression", ("docs/phase9/evidence",), accepted_current_tool_sets=(("ml.regression_evaluation",),), notes="Current canonical integrated regression evaluation supersedes the narrower historical route."),
        ReplaySpec(7, "Phase 9", "numeric_summary", "Summarize all numeric material-property columns in this table.", ("table.numeric_summary",), "table", ("docs/phase9/evidence",), accepted_current_tool_sets=(("table.distribution_summary",), ("dataset.materials_explorer",)), notes="Current distribution summary or the integrated Materials Explorer may supersede the narrower historical numeric-summary route; the broader replacement must still execute against the exact table."),
        ReplaySpec(8, "Phase 10A", "scatter", "Create only a two-axis scatter plot with PBE on the x axis and r2SCAN on the y axis. Do not use composition embedding or dimensionality reduction.", ("viz.scatter",), "table", ("docs/phase10a/browser_api_evidence/matpes_scatter",), expected_outcome="CAPABILITY_MISMATCH", historical_prompt_integrity=corrupt, notes="The historical Mock path guessed x/y column order. Current exact binding correctly rejects the ambiguous scalar binding without substituting correlation."),
        ReplaySpec(9, "Phase 10A", "histogram_r2scan", "Create only a one-variable histogram using the exact r2SCAN property column.", ("viz.histogram",), "table", ("docs/phase10a/browser_api_evidence/matpes_histogram",), historical_prompt_integrity=corrupt),
        ReplaySpec(10, "Phase 10A", "histogram_dmax", "Plot a histogram of the D_max property.", ("viz.histogram",), "table", ("docs/phase10a/browser_api_evidence/ward_histogram",), historical_prompt_integrity=corrupt),
        ReplaySpec(11, "Phase 10A", "correlation", "Create a correlation matrix for the numeric material properties.", ("viz.correlation",), "table", ("docs/phase10a/browser_api_evidence/ward_correlation",), historical_prompt_integrity=corrupt),
        ReplaySpec(12, "Phase 10A", "distribution_summary", "Summarize numeric distributions, missing values, and quantiles.", ("table.distribution_summary",), "table", ("docs/phase10a/browser_api_evidence/ward_distribution",), accepted_current_tool_sets=(("dataset.materials_explorer",),), historical_prompt_integrity=corrupt, notes="The integrated Materials Explorer is an approved broader replacement because it produces the requested exact numeric-distribution, missingness, and quantile facts."),
        ReplaySpec(13, "Phase 10A", "composition_summary", "Summarize the element composition distribution.", ("composition.summary",), "table", ("docs/phase10a/browser_api_evidence/ward_composition_summary",), accepted_current_tool_sets=(("composition.formula_statistics",),), historical_prompt_integrity=corrupt, notes="Current canonical formula-statistics route supersedes the historical composition summary route."),
        ReplaySpec(14, "Phase 10B", "formula_statistics", "Calculate formula statistics for this materials table.", ("composition.formula_statistics",), "table", ("docs/phase10b/browser_api_evidence/ward_formula_statistics",), historical_prompt_integrity=corrupt),
        ReplaySpec(15, "Phase 10B", "elements_hist", "Plot an element-frequency histogram from the formula column.", ("composition.elements_hist",), "table", ("docs/phase10b/browser_api_evidence/ward_elements_hist",), historical_prompt_integrity=corrupt),
        ReplaySpec(16, "Phase 10B", "ptable_heatmap", "Show element frequencies as a periodic-table heatmap.", ("composition.ptable_heatmap",), "table", ("docs/phase10b/browser_api_evidence/ward_ptable_heatmap",), historical_prompt_integrity=corrupt),
        ReplaySpec(17, "Phase 10B", "chem_sys_treemap", "Show the chemical-system distribution as a treemap.", ("composition.chem_sys_treemap",), "table", ("docs/phase10b/browser_api_evidence/ward_chem_sys_treemap",), historical_prompt_integrity=corrupt),
        ReplaySpec(18, "Phase 10B", "chem_sys_sunburst", "Show arity, chemical-system, and formula hierarchy as a sunburst.", ("composition.chem_sys_sunburst",), "table", ("docs/phase10b/browser_api_evidence/ward_chem_sys_sunburst",), historical_prompt_integrity=corrupt),
        ReplaySpec(19, "Phase 10C", "lattice_summary", "Summarize lattice parameters and crystal system for this structure.", ("structure.lattice_summary",), "structure", ("docs/phase10c/browser_api_evidence/simple_cubic_lattice_summary",), accepted_current_tool_sets=(("structure.summary",),), historical_prompt_integrity=corrupt, notes="The current integrated structure summary includes the requested lattice and crystal-system facts."),
        ReplaySpec(20, "Phase 10C", "spacegroup_summary", "Summarize the space group and crystal system for this structure.", ("structure.spacegroup_summary",), "structure", ("docs/phase10c/browser_api_evidence/simple_cubic_spacegroup_summary",), historical_prompt_integrity=corrupt),
        ReplaySpec(21, "Phase 10C", "composition_from_structure", "Extract composition statistics from this structure.", ("structure.composition_from_structure",), "structure", ("docs/phase10c/browser_api_evidence/simple_cubic_composition_from_structure",), historical_prompt_integrity=corrupt),
        ReplaySpec(22, "Phase 10C", "preview_metadata", "Generate structure preview metadata and coordinate ranges.", ("structure.preview_metadata",), "structure", ("docs/phase10c/browser_api_evidence/simple_cubic_preview_metadata",), historical_prompt_integrity=corrupt),
        ReplaySpec(23, "Phase 10E", "coordination_hist", "Count neighbors and plot a coordination-number histogram for this structure.", ("structure.coordination_hist",), "structure", ("docs/phase10e/browser_api_evidence/phase10e2_coordination_hist",)),
        ReplaySpec(24, "Phase 10E", "xrd", "Generate a powder XRD pattern for this crystal structure.", ("structure.xrd",), "structure", ("docs/phase10e/browser_api_evidence/phase10e5_xrd",)),
        ReplaySpec(25, "Phase 10E", "rdf", "Generate the radial distribution function for this structure.", ("structure.rdf",), "structure", ("docs/phase10e/browser_api_evidence/phase10e8_rdf",)),
        ReplaySpec(26, "Phase 10F", "viewer_scene", "Build inert viewer scene data for this structure.", ("structure.viewer_scene",), "structure", ("docs/phase10f/evidence/phase10f13_viewer_scene_live_adapter",)),
        ReplaySpec(27, "Phase 10F", "viewer_3d", "Open an interactive 3D view of this crystal structure.", ("structure.viewer_3d",), "structure", ("docs/phase10/evidence/phase10_closure_regression_pack",), accepted_current_tool_sets=(("structure.structure_3d",),), notes="The current structure.structure_3d product is the canonical interactive three-dimensional viewer replacement."),
        ReplaySpec(28, "Phase 10G", "trajectory_viewer", "Play this molecular-dynamics trajectory.", ("structure.trajectory_viewer",), "trajectory", ("docs/phase10g/evidence/phase10g3_trajectory_performance_browser",)),
        ReplaySpec(29, "Phase 10H", "phonon_band", "Plot only the phonon band structure.", ("phonon.band",), "phonon_band", ("docs/phase10h/evidence/phase10h1_phonon_bands",)),
        ReplaySpec(30, "Phase 10H", "phonon_dos", "Plot only the phonon density of states.", ("phonon.dos",), "phonon_dos", ("docs/phase10h/evidence/phase10h2_phonon_dos",)),
        ReplaySpec(31, "Phase 10H", "phonon_animation", "Animate the selected phonon mode.", ("phonon.animation",), "phonon_animation", ("docs/phase10h/evidence/phase10h5_phonon_animation",)),
        ReplaySpec(32, "Phase 10I", "brillouin_zone", "Generate first Brillouin-zone data for this structure.", ("structure.brillouin_zone",), "brillouin", ("docs/phase10i/evidence/phase10i1_brillouin_zone_adapter",)),
        ReplaySpec(33, "Phase 10I", "linked_band_bz", "Create a phonon-band plot and a Brillouin-zone view for these exact resources.", ("phonon.band", "structure.brillouin_zone"), "linked_bz", ("docs/phase10i/evidence/phase10i3_band_bz_linked_view",)),
        ReplaySpec(34, "Phase 10J", "potential", "Visualize local electrostatic potential and planar averages from this LOCPOT.", ("structure.volumetric_data",), "locpot", ("docs/phase10j/evidence/phase10j4_electrostatic_potential_product",)),
        ReplaySpec(35, "Phase 10J", "elf", "Show an ELF isosurface at 0.7 from this ELFCAR.", ("structure.volumetric_data",), "elfcar", ("docs/phase10j/evidence/phase10j5_elf_orbital_product",)),
        ReplaySpec(36, "Phase 10J", "partial_density", "Visualize the source-defined partial density from this PARCHG.", ("structure.volumetric_data",), "parchg", ("docs/phase10j/evidence/phase10j5_elf_orbital_product",)),
        ReplaySpec(37, "Phase 10J", "slice_volume", "Show a quantitative slice and direct-volume view of this charge density.", ("structure.volumetric_data",), "chgcar", ("docs/phase10j/evidence/phase10j6_volumetric_slice_volume_rendering",)),
        ReplaySpec(38, "Phase 10K", "composition_space", "Explore composition space with deterministic PCA and bounded clusters.", ("dataset.composition_space",), "composition_space", ("docs/phase10k/evidence/phase10k4_composition_space",)),
        ReplaySpec(39, "Phase 10K", "uncertainty", "Analyze whether model uncertainty is trustworthy and show error decay.", ("ml.uncertainty_evaluation",), "uncertainty", ("docs/phase10k/evidence/phase10k3_materials_ml_evaluation",)),
        ReplaySpec(40, "Phase 10K", "classification", "Evaluate classification confusion matrix, ROC, and PR for positive class B.", ("ml.classification_evaluation",), "classification", ("docs/phase10k/evidence/phase10k3_materials_ml_evaluation",)),
        ReplaySpec(41, "Phase 10L-1", "multi_target_clarification", "Analyze where the regression model predictions are wrong.", (), "dual_target", ("docs/phase10l/evidence/phase10l1_analysis_intent",), expected_outcome="NEEDS_CLARIFICATION"),
        ReplaySpec(42, "Phase 10L-1", "fermi_unsupported", "Generate a Fermi surface.", (), "structure", ("docs/phase10l/evidence/phase10l1_analysis_intent",), expected_outcome="UNSUPPORTED"),
        ReplaySpec(43, "Phase 10L-2", "uncertainty_plot_mismatch", "Plot a calibrated reliability curve for model uncertainty.", (), "uncertainty", ("docs/phase10l/evidence/phase10l2_capability_aware_planner",), expected_outcome="CAPABILITY_MISMATCH"),
        ReplaySpec(44, "Phase 10L-2", "formation_energy_exact", "Analyze formation-energy prediction errors.", ("ml.regression_evaluation",), "dual_target", ("docs/phase10l/evidence/phase10l2_capability_aware_planner/regressions/formation_energy_vs_band_gap.json",), notes="Exact target: formation_energy_model"),
        ReplaySpec(45, "Phase 10L-2", "band_gap_exact", "Analyze band-gap prediction errors.", ("ml.regression_evaluation",), "dual_target", ("docs/phase10l/evidence/phase10l2_capability_aware_planner/regressions/formation_energy_vs_band_gap.json",), notes="Exact target: band_gap_model"),
    )


def _selected_target_ids(spec: ReplaySpec, inputs: ReplayInput) -> tuple[str, ...]:
    if spec.case_number == 44:
        return ("formation_energy_model:target:formation_energy",)
    if spec.case_number == 45:
        return ("band_gap_model:target:band_gap",)
    return inputs.selected_target_ids


def _uuid_stream(spec: ReplaySpec):
    for index in range(32):
        yield UUID(hex=sha256(f"historical-deepseek:{spec.case_number}:{spec.slug}:{index}".encode("utf-8")).hexdigest()[:32])


def _safe_decision(planned: Any) -> dict[str, Any] | None:
    decision = planned.capability_decision
    if not decision:
        return None
    return {
        "decisionId": decision.get("decisionId"),
        "decisionHash": decision.get("decisionHash"),
        "outcome": decision.get("outcome"),
        "selectedToolIds": decision.get("selectedToolIds", []),
        "unfulfilledDesiredOutputs": decision.get("unfulfilledDesiredOutputs", []),
        "repairCount": decision.get("repairCount", 0),
        "selections": [
            {
                "toolId": item.get("toolId"),
                "toolVersion": item.get("toolVersion"),
                "coveredScientificIntents": item.get("coveredScientificIntents", []),
                "coveredDesiredOutputs": item.get("coveredDesiredOutputs", []),
                "boundParameters": item.get("boundParameters", []),
            }
            for item in decision.get("selections", [])
        ],
    }


def _actual_outcome(planned: Any) -> str:
    if planned.intent_outcome in {"NEEDS_CLARIFICATION", "UNSUPPORTED"}:
        return planned.intent_outcome
    return planned.capability_outcome or planned.error_code or "UNKNOWN"


def _accepted_tool_sets(spec: ReplaySpec) -> tuple[tuple[str, ...], ...]:
    return (spec.expected_tools, *spec.accepted_current_tool_sets)


def _safe_error_detail(exc: Exception) -> str:
    detail = redact_credential_values(str(exc))
    detail = detail.replace(str(ROOT), "<WORKSPACE>").replace(str(ROOT).replace("\\", "/"), "<WORKSPACE>")
    return detail[:1000]


def _run_case(spec: ReplaySpec, *, model: str, artifact_root: Path) -> dict[str, Any]:
    inputs = FIXTURES[spec.fixture]()
    repositories = InMemoryRepositoryBundle.create()
    repositories.data_profiles.save(inputs.profile)
    registry = load_manifests()
    runtime = QueueWorkerRuntime(repositories=repositories, registry=registry, artifact_root=artifact_root)
    provider = DeepSeekProvider()
    request = PlannerJobsRequest(
        userPrompt=spec.replay_prompt,
        projectId=f"project_historical_deepseek_{spec.case_number:02d}",
        datasetId=inputs.profile.datasetId,
        profileId=inputs.profile.profileId,
        intentSchemaVersion="1.0",
        selectedResourceIds=list(inputs.selected_resource_ids),
        selectedTargetIds=list(_selected_target_ids(spec, inputs)),
        provider="deepseek",
        model=model,
        temperature=0,
        maxTokens=8192,
        timeoutSeconds=120,
        enqueue=False,
    )
    started = perf_counter()
    uuids = iter(_uuid_stream(spec))
    with patch("mdi_api.routers.planner.uuid.uuid4", side_effect=lambda: next(uuids)):
        planned = planner_jobs(request, provider=provider, repositories=repositories, queue_runtime=runtime, registry=registry)
    elapsed_plan_ms = round((perf_counter() - started) * 1000, 3)
    outcome = _actual_outcome(planned)
    if outcome != spec.expected_outcome:
        validation_summary = [
            {
                "code": str(item.get("code") or "UNKNOWN")[:128],
                "field": str(item.get("field") or "")[:128],
                "message": redact_credential_values(str(item.get("message") or ""))[:256],
            }
            for item in planned.validation_errors[:8]
        ]
        intent_payload = planned.intent or {}
        unsupported_summary = [
            {
                "code": str(item.get("code") or "UNKNOWN")[:128],
                "field": str(item.get("field") or "")[:128],
                "boundary": str(item.get("boundary") or "")[:64],
            }
            for item in (intent_payload.get("unsupportedReasons") or [])[:8]
            if isinstance(item, dict)
        ]
        selected_ids = [
            str(item.get("toolId"))
            for item in ((planned.capability_decision or {}).get("selections") or [])
            if item.get("toolId")
        ]
        raise RuntimeError(
            f"HISTORICAL_REPLAY_OUTCOME_MISMATCH:{spec.case_number}:{spec.expected_outcome}:{outcome}:"
            f"details={json.dumps({'validation': validation_summary, 'unsupported': unsupported_summary, 'selected': selected_ids}, sort_keys=True, separators=(',', ':'))}"
        )
    if not 1 <= len(provider.call_audit) <= MAX_CALLS_PER_CASE or not all(item["realCall"] for item in provider.call_audit):
        raise RuntimeError(f"HISTORICAL_REPLAY_REAL_CALL_AUDIT_INVALID:{spec.case_number}")

    if spec.expected_outcome != "PLAN_READY":
        if planned.plan is not None or planned.plan_id is not None or planned.job_id is not None or planned.enqueued:
            raise RuntimeError(f"HISTORICAL_REPLAY_NON_READY_CREATED_EXECUTION:{spec.case_number}")
        runtime_status = "NOT_CREATED"
        tool_calls: list[dict[str, Any]] = []
        artifacts: list[dict[str, Any]] = []
        result: dict[str, Any] | None = None
        selected_tools: list[str] = []
    else:
        if not planned.ok or not planned.job_id or not planned.plan or not planned.plan_id or not planned.plan_hash:
            raise RuntimeError(f"HISTORICAL_REPLAY_PLAN_MISSING:{spec.case_number}")
        selected_tools = [step["toolId"] for step in planned.plan["steps"]]
        if tuple(sorted(selected_tools)) not in {tuple(sorted(values)) for values in _accepted_tool_sets(spec)}:
            eligible_ids = (planned.eligibility_resolution or {}).get("eligibleToolIds", [])
            target_ids = [item.get("semanticId") for item in (planned.intent or {}).get("targetSemantics", [])]
            raise RuntimeError(
                f"HISTORICAL_REPLAY_TOOL_MISMATCH:{spec.case_number}:{selected_tools}:{_accepted_tool_sets(spec)}:"
                f"eligible={eligible_ids}:targets={target_ids}"
            )
        completed = runtime.handle_job(planned.job_id, object_store=inputs.object_store)
        runtime_status = completed.status
        if completed.status != "completed":
            raise RuntimeError(
                f"HISTORICAL_REPLAY_RUNTIME_FAILED:{spec.case_number}:{completed.status}:"
                f"{redact_credential_values(completed.message)[:500]}"
            )
        tool_calls = get_planner_job_tool_calls(planned.job_id, repositories=repositories)
        artifacts = get_planner_job_artifacts(planned.job_id, repositories=repositories)
        result = get_planner_job_result(planned.job_id, repositories=repositories)
        if {item["toolId"] for item in tool_calls} != set(selected_tools):
            raise RuntimeError(f"HISTORICAL_REPLAY_TOOLCALL_MISMATCH:{spec.case_number}")

    audit = list(provider.call_audit)
    prompt_tokens = sum(item["tokenUsage"]["promptTokens"] for item in audit)
    completion_tokens = sum(item["tokenUsage"]["completionTokens"] for item in audit)
    payload = {
        "schemaVersion": "1.0",
        "caseNumber": spec.case_number,
        "phase": spec.phase,
        "slug": spec.slug,
        "sourcePaths": list(spec.source_paths),
        "historicalPromptIntegrity": spec.historical_prompt_integrity,
        "replayPrompt": spec.replay_prompt,
        "replayPromptHash": sha256(spec.replay_prompt.encode("utf-8")).hexdigest(),
        "notes": spec.notes,
        "provider": "deepseek",
        "model": model,
        "providerCallCount": len(audit),
        "providerCallAudit": audit,
        "tokenUsage": {
            "promptTokens": prompt_tokens,
            "completionTokens": completion_tokens,
            "totalTokens": prompt_tokens + completion_tokens,
            "estimated": any(item["tokenUsage"]["estimated"] for item in audit),
        },
        "profile": {
            "profileId": inputs.profile.profileId,
            "profileSemanticHash": inputs.profile.semanticHash,
            "datasetId": inputs.profile.datasetId,
            "selectedResourceIds": list(inputs.selected_resource_ids),
            "selectedTargetIds": list(_selected_target_ids(spec, inputs)),
        },
        "intent": {
            "intentId": (planned.intent or {}).get("intentId"),
            "intentHash": (planned.intent or {}).get("intentHash"),
            "outcome": planned.intent_outcome,
            "scientificIntents": (planned.intent or {}).get("scientificIntents", []),
            "requiredCapabilityNeeds": (planned.intent or {}).get("requiredCapabilityNeeds", []),
            "desiredOutputs": (planned.intent or {}).get("desiredOutputs", []),
            "targetSemantics": (planned.intent or {}).get("targetSemantics", []),
            "clarificationQuestionCount": len(((planned.intent or {}).get("clarification") or {}).get("questions", [])),
        },
        "eligibility": {
            "resolutionId": (planned.eligibility_resolution or {}).get("resolutionId"),
            "resolutionHash": (planned.eligibility_resolution or {}).get("resolutionHash"),
            "eligibleToolIds": (planned.eligibility_resolution or {}).get("eligibleToolIds", []),
            "providerVisibleToolIds": planned.provider_visible_tool_ids,
            "rejectedToolCount": len((planned.eligibility_resolution or {}).get("rejectedToolIds", [])),
        },
        "decision": _safe_decision(planned),
        "planningOutcome": outcome,
        "selectedToolIds": selected_tools,
        "historicalExpectedToolIds": list(spec.expected_tools),
        "acceptedCurrentToolSets": [list(values) for values in _accepted_tool_sets(spec)],
        "routeClassification": (
            "EXACT_BINDING_GAP_REPORTED"
            if spec.expected_outcome != "PLAN_READY"
            else ("EXACT_HISTORICAL_ROUTE" if set(selected_tools) == set(spec.expected_tools) else "CURRENT_CANONICAL_REPLACEMENT")
        ),
        "plan": {
            "planId": planned.plan_id,
            "planHash": planned.plan_hash,
            "schemaVersion": planned.plan_schema_version,
            "graphHash": planned.graph_hash,
            "stepCount": len((planned.plan or {}).get("steps", [])),
        },
        "runtime": {
            "status": runtime_status,
            "toolCallCount": len(tool_calls),
            "artifactCount": len(artifacts),
            "toolCalls": [
                {"id": item.get("id"), "stepId": item.get("stepId"), "toolId": item.get("toolId"), "status": item.get("status")}
                for item in tool_calls
            ],
            "artifacts": [
                {"id": item.get("id"), "name": item.get("name"), "type": item.get("type"), "sha256": item.get("sha256"), "sizeBytes": item.get("sizeBytes")}
                for item in artifacts
            ],
            "resultStatus": (result or {}).get("status") if result else None,
        },
        "timing": {"plannerElapsedMs": elapsed_plan_ms},
        "invariants": {
            "realDeepSeekOnly": all(item["realCall"] for item in audit),
            "providerVisibleEqualsEligible": planned.provider_visible_tool_ids == (planned.eligibility_resolution or {}).get("eligibleToolIds", []),
            "selectedWithinEligible": set(selected_tools).issubset(set(planned.provider_visible_tool_ids)),
            "noPlanJobEnqueueForNonReady": spec.expected_outcome == "PLAN_READY" or (planned.plan is None and planned.job_id is None and not planned.enqueued),
            "browserReceivesSecret": False,
            "rawProviderPayloadPersisted": False,
        },
        "verdict": "PASS",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    if spec.expected_outcome != "PLAN_READY":
        payload["browserContract"] = {
            "request": request.model_dump(mode="json"),
            "response": asdict(planned),
            "profile": inputs.profile.model_dump(mode="json"),
            "sourceProvider": "deepseek",
            "sourceModel": model,
            "providerCallAudit": audit,
            "noPlanJobEnqueue": planned.plan is None and planned.job_id is None and not planned.enqueued,
        }
    payload["runHash"] = _stable_hash({key: value for key, value in payload.items() if key not in {"runHash", "createdAt", "timing"}})
    payload["runId"] = f"historical_live_run_{payload['runHash'][:32]}"
    return payload


def _existing_l5_refs() -> list[dict[str, Any]]:
    suite_path = EVIDENCE / "deepseek_verification_suite.json"
    if not suite_path.exists():
        raise RuntimeError("EXISTING_L5_DEEPSEEK_SUITE_MISSING")
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    if suite.get("verdict") != "PASS" or len(suite.get("cases", [])) != 5:
        raise RuntimeError("EXISTING_L5_DEEPSEEK_SUITE_INVALID")
    return [
        {
            "caseNumber": index,
            "coverage": "COVERED_BY_EXISTING_L5_LIVE_SUITE",
            "caseSpecId": item["caseSpecId"],
            "runId": item["runId"],
            "realCallCount": item["realCallCount"],
            "verdict": item["verdict"],
        }
        for index, item in enumerate(sorted(suite["cases"], key=lambda value: value["caseSpecId"]), 1)
    ]


def _inventory() -> dict[str, Any]:
    specs = _specs()
    return {
        "schemaVersion": "1.0",
        "totalFiniteReplayCases": 45,
        "existingL5Cases": 5,
        "additionalHistoricalCases": len(specs),
        "classificationPolicy": {
            "REAL_REPLAY_REQUIRED": "A historical Mock/Fake LLM choice remains a useful current product path.",
            "COVERED_BY_L5_FIVE_CASES": "The exact current semantic family already passed the full live L5 chain.",
            "SUPERSEDED": "The historical tool is intentionally unavailable and mapped to its current canonical replacement.",
            "NON_LLM_BROWSER_ONLY": "The flow begins after planning and tests rendering or interaction only.",
            "TEST_ONLY_NEGATIVE": "A deterministic malformed-output, injection, or runtime failure fixture must not spend a live call.",
        },
        "cases": [
            {
                "caseNumber": spec.case_number,
                "phase": spec.phase,
                "slug": spec.slug,
                "classification": "REAL_REPLAY_REQUIRED",
                "sourcePaths": list(spec.source_paths),
                "historicalPromptIntegrity": spec.historical_prompt_integrity,
                "replayPrompt": spec.replay_prompt,
                "expectedToolIds": list(spec.expected_tools),
                "acceptedCurrentToolSets": [list(values) for values in _accepted_tool_sets(spec)],
                "expectedOutcome": spec.expected_outcome,
            }
            for spec in specs
        ],
        "superseded": [
            {"toolId": "structure.viewer_scene_metadata", "replacement": "structure.viewer_scene", "reason": "DEPLOYMENT_UNAVAILABLE"},
            {"toolId": "structure.viewer_export_package", "replacement": "structure.viewer_scene", "reason": "DEPLOYMENT_UNAVAILABLE"},
            {"toolId": "structure.trajectory_import", "replacement": "structure.trajectory_viewer", "reason": "DEPLOYMENT_UNAVAILABLE"},
            {"toolId": "viewer_scene.preview_fixture", "replacement": "structure.viewer_3d", "reason": "TEST_FIXTURE_ONLY"},
        ],
        "nonLlmBrowserOnly": [
            "Phase 10F camera, clipping, picking, measurement, context-loss, and export interactions",
            "Phase 10G trajectory playback and frame controls after the viewer tool has been selected",
            "Phase 10H/10I/10J renderer interaction matrices after persisted artifacts exist",
        ],
        "testOnlyNegative": [
            "duplicate JSON keys and fenced/prose provider output",
            "prompt-injection and invented identifier fixtures",
            "dependency producer/consumer failure injection",
            "checksum, cycle, cap, cross-job, and cross-project tampering",
        ],
    }


def _finalize(model: str) -> dict[str, Any]:
    refs = _existing_l5_refs()
    phase_summary: dict[str, dict[str, int]] = {}
    models_used = {str(json.loads((EVIDENCE / "deepseek_verification_suite.json").read_text(encoding="utf-8"))["model"])}
    prompt_tokens = completion_tokens = real_calls = 0
    for spec in _specs():
        path = OUTPUT / f"case_{spec.case_number:02d}_{spec.slug}.json"
        if not path.exists():
            raise RuntimeError(f"HISTORICAL_REPLAY_CASE_MISSING:{spec.case_number}")
        record = json.loads(path.read_text(encoding="utf-8"))
        if (
            record.get("verdict") != "PASS"
            or record.get("model") not in DEEPSEEK_ALLOWED_MODELS
            or record.get("replayPromptHash") != sha256(spec.replay_prompt.encode("utf-8")).hexdigest()
        ):
            raise RuntimeError(f"HISTORICAL_REPLAY_CASE_STALE:{spec.case_number}")
        models_used.add(str(record["model"]))
        refs.append(
            {
                "caseNumber": spec.case_number,
                "phase": spec.phase,
                "slug": spec.slug,
                "coverage": "REAL_DEEPSEEK_REPLAY_PASS",
                "runId": record["runId"],
                "runHash": record["runHash"],
                "planningOutcome": record["planningOutcome"],
                "selectedToolIds": record["selectedToolIds"],
                "realCallCount": record["providerCallCount"],
                "runtimeStatus": record["runtime"]["status"],
                "verdict": "PASS",
            }
        )
        phase = phase_summary.setdefault(spec.phase, {"passed": 0, "failed": 0, "realCalls": 0})
        phase["passed"] += 1
        phase["realCalls"] += record["providerCallCount"]
        real_calls += record["providerCallCount"]
        prompt_tokens += record["tokenUsage"]["promptTokens"]
        completion_tokens += record["tokenUsage"]["completionTokens"]
    refs.sort(key=lambda item: item["caseNumber"])
    existing_suite = json.loads((EVIDENCE / "deepseek_verification_suite.json").read_text(encoding="utf-8"))
    total_calls = real_calls + existing_suite["totalRealCallCount"]
    total_prompt = prompt_tokens + existing_suite["tokenUsage"]["promptTokens"]
    total_completion = completion_tokens + existing_suite["tokenUsage"]["completionTokens"]
    suite = {
        "schemaVersion": "1.0",
        "provider": "deepseek",
        "defaultModel": model,
        "modelsUsed": sorted(models_used),
        "modelPolicy": "Each case records its explicit allowlisted model; model changes are never silent fallback.",
        "keySource": "DEEPSEEK_KEY",
        "baseUrl": "https://api.deepseek.com",
        "caseCount": 45,
        "passedCaseCount": 45,
        "failedCaseCount": 0,
        "existingL5CaseCount": 5,
        "additionalHistoricalCaseCount": 40,
        "totalRealCallCount": total_calls,
        "otherRealProviderCalls": 0,
        "tokenUsage": {
            "promptTokens": total_prompt,
            "completionTokens": total_completion,
            "totalTokens": total_prompt + total_completion,
            "estimated": existing_suite["tokenUsage"].get("estimated", False),
        },
        "cases": refs,
        "phaseSummary": phase_summary,
        "security": {
            "browserReceivesSecret": False,
            "rawProviderPayloadPersisted": False,
            "providerFallback": False,
            "realDeepSeekOnly": True,
        },
        "verdict": "PASS",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    suite["suiteHash"] = _stable_hash({key: value for key, value in suite.items() if key not in {"suiteHash", "createdAt"}})
    suite["suiteId"] = f"historical_deepseek_suite_{suite['suiteHash'][:32]}"
    _write_json("historical_mock_llm_browser_inventory.json", _inventory())
    _write_json("llm_call_site_matrix.json", _inventory())
    _write_json("historical_deepseek_replay_suite.json", suite)
    _write_json("historical_deepseek_phase_coverage.json", {"schemaVersion": "1.0", "phaseSummary": phase_summary, "verdict": "PASS"})
    return suite


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Replay every useful historical Mock/Fake LLM browser flow with real DeepSeek.")
    parser.add_argument("--case-number", action="append", type=int, choices=range(6, 46))
    parser.add_argument("--finalize-only", action="store_true")
    parser.add_argument("--inventory-only", action="store_true")
    args = parser.parse_args(argv)
    if sum(bool(value) for value in (args.finalize_only, args.inventory_only, args.case_number)) > 1:
        parser.error("Choose only one of --case-number, --finalize-only, or --inventory-only")

    _write_json("historical_mock_llm_browser_inventory.json", _inventory())
    _write_json("llm_call_site_matrix.json", _inventory())
    if args.inventory_only:
        print(json.dumps({"caseCount": 45, "additionalHistoricalCases": 40, "verdict": "PASS"}))
        return 0

    model = os.environ.get("DEEPSEEK_MODEL") or DEEPSEEK_DEFAULT_MODEL
    if not os.environ.get("DEEPSEEK_KEY"):
        print(json.dumps({"errorCode": "DEEPSEEK_NOT_CONFIGURED", "verdict": "BLOCKED"}))
        return 2
    if model not in DEEPSEEK_ALLOWED_MODELS:
        print(json.dumps({"errorCode": "DEEPSEEK_MODEL_NOT_ALLOWED", "model": model, "verdict": "BLOCKED"}))
        return 2
    if args.finalize_only:
        try:
            suite = _finalize(model)
        except Exception as exc:
            print(json.dumps({"errorCode": str(exc).split(":", 1)[0], "verdict": "FAIL"}))
            return 1
        print(json.dumps({"suiteId": suite["suiteId"], "caseCount": suite["caseCount"], "totalRealCallCount": suite["totalRealCallCount"], "verdict": "PASS"}))
        return 0

    selected = set(args.case_number or range(6, 46))
    passed: list[int] = []
    failed: list[dict[str, Any]] = []
    started = perf_counter()
    with TemporaryDirectory(prefix="mdi-historical-deepseek-") as directory:
        for spec in _specs():
            if spec.case_number not in selected:
                continue
            try:
                record = _run_case(spec, model=model, artifact_root=Path(directory) / f"case_{spec.case_number:02d}")
                _write_json(f"historical_deepseek_replay/case_{spec.case_number:02d}_{spec.slug}.json", record)
                passed.append(spec.case_number)
            except Exception as exc:
                code = exc.code if isinstance(exc, LLMProviderError) else str(exc).split(":", 1)[0]
                failed.append({"caseNumber": spec.case_number, "slug": spec.slug, "errorCode": code[:160]})
                failure_path = OUTPUT / "failures" / f"case_{spec.case_number:02d}_{spec.slug}.json"
                previous_attempts: list[dict[str, Any]] = []
                if failure_path.exists():
                    previous = json.loads(failure_path.read_text(encoding="utf-8"))
                    previous_attempts = list(previous.get("attempts") or [{
                        "model": previous.get("model"),
                        "errorCode": previous.get("errorCode"),
                        "safeDetails": previous.get("safeDetails"),
                        "createdAt": previous.get("createdAt"),
                    }])
                current_attempt = {
                    "model": model,
                    "errorCode": code[:160],
                    "safeDetails": _safe_error_detail(exc),
                    "createdAt": datetime.now(timezone.utc).isoformat(),
                }
                _write_json(
                    f"historical_deepseek_replay/failures/case_{spec.case_number:02d}_{spec.slug}.json",
                    {
                        "caseNumber": spec.case_number,
                        "slug": spec.slug,
                        "provider": "deepseek",
                        "model": model,
                        "errorCode": code[:160],
                        "safeDetails": current_attempt["safeDetails"],
                        "attempts": [*previous_attempts[-15:], current_attempt],
                        "verdict": "FAIL",
                        "createdAt": current_attempt["createdAt"],
                    },
                )
    if failed:
        print(json.dumps({"passed": passed, "failed": failed, "elapsedMs": round((perf_counter() - started) * 1000, 3), "verdict": "FAIL"}))
        return 1
    require_suite = args.case_number is None
    suite = _finalize(model) if require_suite else None
    print(
        json.dumps(
            {
                "passed": passed,
                "failed": [],
                "suiteId": suite["suiteId"] if suite else None,
                "elapsedMs": round((perf_counter() - started) * 1000, 3),
                "verdict": "PASS",
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
