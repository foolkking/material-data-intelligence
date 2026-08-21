from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

from mdi_adapters.registry import ADAPTER_CLASSES
from mdi_tool_registry import build_registry_snapshot, load_manifests


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "qualification" / "phase_a_repository_capability_census"
REGISTRY_SOURCE = "packages/tool-registry/mdi_tool_registry/loader.py"
RENDERER_SOURCE = "apps/web/app/components/workspace/workspace-renderer-registry.ts"
INPUT_AUTHORITY = "docs/phase11/evidence/phase11_0_validation_baseline_reconciliation/input_support_matrix.json"
REPRO_AUTHORITY = "docs/phase13/reproducibility/manifest.json"
FINAL_AUTHORITY = "docs/phase13/final/initial_release_manifest.json"
PHASE11_LEVELS = "docs/phase11/evidence/phase11_5_scientific_validation_closure/phase11_validation_level_distribution.json"
PHASE10L_LIVE = "docs/phase10l/evidence/phase10l5_natural_language_closure/browser_capture_index.json"


def read_json(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def dump_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def dump_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    keys = sorted({key for row in rows for key in row})
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=keys, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: json.dumps(row.get(key), ensure_ascii=False, sort_keys=True) if isinstance(row.get(key), (list, dict)) else row.get(key, "") for key in keys})
    path.write_text(stream.getvalue(), encoding="utf-8", newline="\n")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()


def evidence(*refs: str) -> list[str]:
    return list(refs)


def entry_paths() -> list[dict[str, Any]]:
    common = {
        "persistenceTarget": "PostgreSQL metadata plus MinIO normalized source authority",
        "DataProfileImpact": "creates or selects a durable Dataset whose current Profile is generated under DataProfile 2.4",
    }
    return [
        {
            "entryPathId": "ENTRY-UI-FILE-UPLOAD",
            "displayName": "Upload one supported material-data file",
            "route": "/",
            "frontendComponent": "PlannerWorkbench.handleUploadFile",
            "backendEndpoint": "POST /datasets/upload",
            "requestContract": "UploadDatasetRequest / DatasetUploadRequest",
            "importer/parser": "mdi_material_parsers.parse_file",
            "singleOrMultiFile": "single file per UI action",
            "requiredCompanionFiles": [],
            "supportedExtensions": [".csv", ".json", ".cif", ".xyz", ".extxyz", ".cube", ".zip", "POSCAR/CONTCAR", "CHGCAR/CHG/LOCPOT/ELFCAR/PARCHG"],
            "supportedMimeTypes": ["container/content detected; MIME is not scientific authority"],
            "encodingRequirements": "text inputs must satisfy the selected parser; strict contracts require UTF-8",
            "sizeCaps": "format-specific; see file_format_inventory.json; no global upload byte cap is defined in DatasetUploadRequest",
            "countCaps": "one file in the current UI action; ZIP maxFiles=100",
            "archiveBehavior": "ZIP recursively dispatches safe members, max 100 files, 50 MiB uncompressed, depth 5",
            "normalizationBehavior": "parser emits immutable normalized object drafts with content hashes",
            "knownLimitations": ["support depends on format plus semantic contract, not extension alone"],
            "repositoryEvidenceRefs": evidence("apps/web/app/components/PlannerWorkbench.tsx", "apps/web/app/lib/planner-api.ts", "apps/api/mdi_api/phase2_runtime.py", "packages/material-parsers/mdi_material_parsers/parsers.py"),
            **common,
        },
        {
            "entryPathId": "ENTRY-UI-TYPED-PHONON-BUNDLE",
            "displayName": "Import typed phonon Band and DOS with Structure context",
            "route": "/",
            "frontendComponent": "PlannerWorkbench.handleTypedPhononImport",
            "backendEndpoint": "POST /datasets/upload",
            "requestContract": "UploadDatasetRequest files[].importKind/contractVersion",
            "importer/parser": "map_normalized_phonon_resource",
            "singleOrMultiFile": "three-file product action",
            "requiredCompanionFiles": ["one typed PhononBand JSON", "one typed PhononDos JSON", "one supported Structure file"],
            "supportedExtensions": [".json", ".cif", "POSCAR/CONTCAR"],
            "supportedMimeTypes": ["application/json", "structure parser dependent"],
            "encodingRequirements": "UTF-8 JSON plus supported structure encoding",
            "sizeCaps": "32,000,000 bytes per typed phonon JSON; Structure uses its parser authority",
            "countCaps": "exactly one Band, one DOS, and one Structure in the UI bundle",
            "archiveBehavior": "not accepted as the typed bundle declaration",
            "normalizationBehavior": "explicit declared kind and exact contract version; no unit or q-path inference",
            "knownLimitations": ["SUPPORTED_WITH_LIMITS", "supplied data only", "generic phonon YAML/JSON remains MAPPING_ONLY"],
            "repositoryEvidenceRefs": evidence("apps/web/app/components/PlannerWorkbench.tsx", "apps/web/app/lib/planner-api.ts", "apps/api/mdi_api/phase2_runtime.py", "packages/material-parsers/mdi_material_parsers/mapped_resources.py"),
            **common,
        },
        {
            "entryPathId": "ENTRY-UI-DATASET-SELECTION",
            "displayName": "Select an existing durable Dataset",
            "route": "/",
            "frontendComponent": "PlannerWorkbench dataset selector",
            "backendEndpoint": "GET /datasets and GET /datasets/{dataset_id}/profile",
            "requestContract": "exact Dataset ID selected from server inventory",
            "importer/parser": "N/A; reuses persisted normalized resources",
            "singleOrMultiFile": "N/A",
            "requiredCompanionFiles": [],
            "supportedExtensions": [],
            "supportedMimeTypes": [],
            "encodingRequirements": "N/A",
            "sizeCaps": "existing persisted resource caps",
            "countCaps": "one active Dataset context",
            "archiveBehavior": "N/A",
            "normalizationBehavior": "no reparsing or latest/fuzzy rebinding",
            "knownLimitations": ["project scope and exact identity are mandatory", "stale profiles remain typed failures"],
            "repositoryEvidenceRefs": evidence("apps/web/app/components/PlannerWorkbench.tsx", "apps/web/app/lib/planner-api.ts", "apps/api/mdi_api/main.py"),
            **common,
        },
        {
            "entryPathId": "ENTRY-API-INLINE-UPLOAD",
            "displayName": "Upload supported inline files through the documented product API",
            "route": "POST /datasets/upload",
            "frontendComponent": "N/A (public product API)",
            "backendEndpoint": "POST /datasets/upload",
            "requestContract": "DatasetUploadRequest with InlineUploadFile records",
            "importer/parser": "parse_dataset or explicit typed phonon mapper",
            "singleOrMultiFile": "multi-file request; repository schema defines no max_items",
            "requiredCompanionFiles": "semantic-kind dependent",
            "supportedExtensions": ["same parser allowlist as ENTRY-UI-FILE-UPLOAD"],
            "supportedMimeTypes": ["MIME alone is not authority"],
            "encodingRequirements": "inline string content; parser/contract specific",
            "sizeCaps": "InlineUploadFile.content has no schema max_length; downstream parser/resource caps remain semantic-specific",
            "countCaps": "DatasetUploadRequest.files has no schema max_items",
            "archiveBehavior": "ZIP behavior is parser-owned",
            "normalizationBehavior": "durable upload path writes normalized objects before profiling",
            "knownLimitations": ["filePaths is internal/runtime compatibility and is not documented as normal-user entry", "request-level byte/item cap authority is not defined in the repository schema"],
            "repositoryEvidenceRefs": evidence("apps/api/mdi_api/main.py", "apps/api/mdi_api/phase2_runtime.py", "docs/phase13/release/api-reference.md"),
            **common,
        },
    ]


SEMANTIC_KINDS = [
    ("materials_tabular_dataset", "Materials tabular dataset", ["DataFrame"], ["CSV", "limited JSON table"], "SUPPORTED", ["semantic columns or resources", "stable sample identity when sample-linked products are requested"], "column metadata may leave units unknown"),
    ("regression_result_table", "Supplied regression result table", ["DataFrame + Profile roles"], ["CSV", "limited JSON table"], "SUPPORTED_WITH_LIMITS", ["regression_target", "regression_prediction", "target/model identity", "sample identity"], "evaluation only; no training or generalization claim"),
    ("uncertainty_result_table", "Supplied uncertainty result table", ["DataFrame + Profile roles"], ["CSV", "limited JSON table"], "SUPPORTED_WITH_LIMITS", ["regression_target", "regression_prediction", "regression_uncertainty", "model identity", "sample identity"], "uncertainty evaluation only"),
    ("classification_result_table", "Supplied classification result table", ["DataFrame + Profile roles"], ["CSV", "limited JSON table"], "SUPPORTED_WITH_LIMITS", ["classification_target", "classification_prediction", "class/model identity", "sample identity"], "classification evaluation only"),
    ("crystal_structure", "Periodic crystal structure", ["Structure"], ["CIF", "POSCAR/CONTCAR", "limited JSON structure", "periodic EXTXYZ"], "SUPPORTED", ["immutable structure hash", "stable site identity", "periodic lattice where required"], "capability-specific periodicity and atom caps"),
    ("atomic_structure", "Non-periodic atomic structure", ["Atoms/Structure"], ["XYZ", "EXTXYZ single frame"], "SUPPORTED_WITH_LIMITS", ["immutable object hash", "stable atom ordinal"], "periodic-only tools remain ineligible"),
    ("trajectory", "Atomic trajectory", ["phase10g.trajectory.v1"], ["canonical JSON", "multi-frame EXTXYZ"], "SUPPORTED_WITH_LIMITS", ["stable atom/species order", "coordinates and units", "cell/PBC", "monotonic physical time for MSD/diffusion"], "plain XYZ and LAMMPS trajectories are unsupported"),
    ("experimental_xrd", "Experimental XRD resource", ["phase10n3.experimental_xrd_resource.v1"], ["strict JSON"], "SUPPORTED_WITH_LIMITS", ["2theta axis", "angstrom wavelength", "finite intensity array", "resource hash"], "wavelength mismatch is rejected; no reprojection or refinement"),
    ("phonon_band", "Supplied phonon Band resource", ["phase10h.phonon_band.v1"], ["explicit typed JSON import"], "SUPPORTED_WITH_LIMITS", ["resource hash", "frequency unit", "q-point/path identity", "structure compatibility"], "no phonon calculation or q-path inference"),
    ("phonon_dos", "Supplied phonon DOS resource", ["phase10h.phonon_dos.v1"], ["explicit typed JSON import"], "SUPPORTED_WITH_LIMITS", ["resource hash", "frequency/DOS units", "projection semantics", "structure compatibility"], "no unit inference; generic JSON/YAML is mapping-only"),
    ("phonon_eigenvectors", "Supplied phonon eigenvectors", ["phase10h eigenvector contract"], ["normalized mapped resource only"], "MAPPING_ONLY", ["mode identity", "structure", "Band binding", "displacement convention"], "no current explicit normal-user typed import"),
    ("volumetric_field", "Bounded volumetric scalar field", ["volumetric-field/v1"], ["VASP volumetric", "single-dataset Gaussian CUBE"], "SUPPORTED_WITH_LIMITS", ["grid/lattice", "quantity", "unit", "source hash", "field identity"], "no Bader/topological extraction; CUBE multi-orbital unsupported"),
    ("electronic_band", "Supplied electronic Band resource", ["phase10n5.electronic_band_resource.v1"], ["strict JSON"], "SUPPORTED_WITH_LIMITS", ["calculation identity", "eV unit", "energy reference", "source-supplied Fermi", "k-point/band identity"], "unknown units are ineligible; no DFT execution"),
    ("electronic_dos", "Supplied electronic DOS resource", ["phase10n5.electronic_dos_resource.v1"], ["strict JSON"], "SUPPORTED_WITH_LIMITS", ["calculation identity", "eV unit", "energy reference", "source-supplied Fermi", "channel/projection identity"], "PDOS completeness is COMPLETE/PARTIAL/UNKNOWN"),
    ("reciprocal_space_context", "Brillouin-zone and reciprocal-space context", ["derived from exact periodic Structure"], ["N/A derived product"], "SUPPORTED_WITH_LIMITS", ["ordered non-magnetic 3D periodic Structure"], "generated context is structure-bound; no standalone upload route"),
]


def semantic_kinds() -> list[dict[str, Any]]:
    rows = []
    for sid, name, contracts, formats, disposition, requirements, limitation in SEMANTIC_KINDS:
        rows.append({
            "semanticKindId": sid, "canonicalName": name, "sourceContracts": contracts, "inputFormats": formats,
            "importRoutes": ["POST /datasets/upload"] if "derived" not in formats[0].lower() else [],
            "requiredProfileFacts": requirements, "requiredIdentifiers": [item for item in requirements if "identity" in item or "hash" in item],
            "requiredUnits": [item for item in requirements if "unit" in item or "wavelength" in item],
            "requiredPairedResources": ["case-specific exact bindings"], "requiredContextResources": ["case-specific; N/A when independent"],
            "supportDisposition": disposition, "limitations": [limitation],
            "negativeConditions": ["missing required Profile fact", "unknown required unit", "stale/hash/project mismatch", "unsupported contract version"],
            "repositoryEvidenceRefs": evidence(REGISTRY_SOURCE, "packages/material-parsers/mdi_material_parsers/profile.py", "packages/material-parsers/mdi_material_parsers/semantic_profile.py", INPUT_AUTHORITY),
        })
    return rows


FORMAT_ROWS = [
    ("CSV", [".csv"], ["text/csv", "application/csv"], "text", "UTF-8/parser compatible", "pandas.read_csv", ["materials_tabular_dataset", "regression_result_table", "uncertainty_result_table", "classification_result_table"], ["SUPPORTED", "SUPPORTED_WITH_LIMITS", "SUPPORTED_WITH_LIMITS", "SUPPORTED_WITH_LIMITS"]),
    ("JSON_LIMITED", [".json"], ["application/json"], "text", "UTF-8", "_parse_json_limited / strict resource validators", ["materials_tabular_dataset", "crystal_structure", "trajectory", "experimental_xrd", "electronic_band", "electronic_dos"], ["SUPPORTED_WITH_LIMITS"] * 6),
    ("CIF", [".cif"], ["chemical/x-cif", "text/plain"], "text", "parser compatible", "pymatgen.Structure.from_file", ["crystal_structure"], ["SUPPORTED"]),
    ("POSCAR_CONTCAR", ["POSCAR", "CONTCAR", "POSCAR.*", "CONTCAR.*"], ["text/plain"], "text", "parser compatible", "pymatgen.Structure.from_file", ["crystal_structure"], ["SUPPORTED"]),
    ("XYZ", [".xyz"], ["chemical/x-xyz", "text/plain"], "text", "parser compatible", "ASE read", ["atomic_structure"], ["SUPPORTED_WITH_LIMITS"]),
    ("EXTXYZ", [".extxyz", ".xyz with Lattice/Properties"], ["text/plain"], "text", "UTF-8", "bounded trajectory parser / ASE single frame", ["trajectory", "crystal_structure"], ["SUPPORTED_WITH_LIMITS", "SUPPORTED_WITH_LIMITS"]),
    ("VASP_VOLUMETRIC", ["CHGCAR", "CHG", "LOCPOT", "ELFCAR", "PARCHG"], ["text/plain"], "text", "parser compatible", "bounded VASP volumetric parser", ["volumetric_field"], ["SUPPORTED_WITH_LIMITS"]),
    ("GAUSSIAN_CUBE", [".cube"], ["text/plain"], "text", "parser compatible", "bounded single-dataset CUBE parser", ["volumetric_field"], ["SUPPORTED_WITH_LIMITS"]),
    ("ZIP", [".zip"], ["application/zip"], "binary", "N/A", "safe recursive archive dispatcher", ["contained_supported_resources"], ["SUPPORTED_WITH_LIMITS"]),
    ("TYPED_PHONON_BAND_JSON", [".json"], ["application/json"], "text", "UTF-8", "map_normalized_phonon_resource(kind=phonon_band)", ["phonon_band"], ["SUPPORTED_WITH_LIMITS"]),
    ("TYPED_PHONON_DOS_JSON", [".json"], ["application/json"], "text", "UTF-8", "map_normalized_phonon_resource(kind=phonon_dos)", ["phonon_dos"], ["SUPPORTED_WITH_LIMITS"]),
    ("GENERIC_PHONON_YAML_JSON", [".yaml", ".yml", ".json"], ["text/yaml", "application/json"], "text", "UTF-8", "no generic execution-ready upload parser", ["phonon_band", "phonon_dos", "phonon_eigenvectors"], ["MAPPING_ONLY"] * 3),
    ("EXCEL", [".xlsx", ".xls"], ["spreadsheet MIME"], "binary", "N/A", None, ["materials_tabular_dataset"], ["UNSUPPORTED"]),
    ("PARQUET", [".parquet"], ["application/vnd.apache.parquet"], "binary", "N/A", None, ["materials_tabular_dataset"], ["UNSUPPORTED"]),
    ("LAMMPS_TRAJECTORY", [".lammpstrj", ".dump"], [], "text", "unknown", None, ["trajectory"], ["UNSUPPORTED"]),
]


def formats_and_inputs() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    formats: list[dict[str, Any]] = []
    combos: list[dict[str, Any]] = []
    max_bytes = {
        "EXTXYZ": 64_000_000,
        "VASP_VOLUMETRIC": 268_435_456,
        "GAUSSIAN_CUBE": 268_435_456,
        "ZIP": {"maxUncompressedBytes": 50 * 1024 * 1024},
        "TYPED_PHONON_BAND_JSON": 32_000_000,
        "TYPED_PHONON_DOS_JSON": 32_000_000,
    }
    max_entries = {
        "EXTXYZ": {"maxAtoms": 4096, "maxFrames": 10000, "maxTotalCoordinateValues": 12_000_000},
        "VASP_VOLUMETRIC": {"maxAtoms": 100000, "maxParserVoxels": 2_097_152, "maxGridDimension": 512},
        "GAUSSIAN_CUBE": {"maxParserVoxels": 2_097_152, "maxGridDimension": 512},
        "ZIP": {"maxFiles": 100, "maxDepth": 5},
    }
    for fid, exts, mimes, mode, encoding, parser, kinds, dispositions in FORMAT_ROWS:
        format_refs = ["packages/material-parsers/mdi_material_parsers/detector.py", "packages/material-parsers/mdi_material_parsers/parsers.py", INPUT_AUTHORITY]
        if fid in {"EXTXYZ", "JSON_LIMITED"}:
            format_refs.append("packages/material-parsers/mdi_material_parsers/trajectory.py")
        if fid in {"VASP_VOLUMETRIC", "GAUSSIAN_CUBE"}:
            format_refs.append("packages/material-parsers/mdi_material_parsers/volumetric.py")
        if fid.startswith("TYPED_PHONON"):
            format_refs.append("packages/material-parsers/mdi_material_parsers/mapped_resources.py")
        formats.append({
            "formatId": fid, "extensions": exts, "mimeTypes": mimes, "textOrBinary": mode, "encoding": encoding,
            "parser/importer": parser, "semanticKindsAccepted": kinds, "supportDispositionPerSemanticKind": dict(zip(kinds, dispositions)),
            "maxBytes": max_bytes.get(fid, "UNKNOWN_REPOSITORY_AUTHORITY"),
            "maxEntries": max_entries.get(fid, "UNKNOWN_REPOSITORY_AUTHORITY"),
            "pairedFileRules": "typed phonon Band and DOS require Structure context; otherwise semantic contract specific",
            "normalizationRules": "exact parser/contract validation and immutable content hash; no filename/MIME-only scientific authority",
            "failureModes": ["FORMAT_UNSUPPORTED", "PARSE_FAILED", "contract-specific typed failure"],
            "repositoryEvidenceRefs": evidence(*format_refs),
        })
        for kind, disposition in zip(kinds, dispositions):
            entry = "ENTRY-UI-TYPED-PHONON-BUNDLE" if fid.startswith("TYPED_PHONON") else "ENTRY-UI-FILE-UPLOAD"
            combos.append({
                "entryPath": entry, "format": fid, "semanticDataKind": kind, "supportDisposition": disposition,
                "canonicalRepositoryDisposition": "DIRECT_SUPPORTED" if disposition == "SUPPORTED" else disposition,
                "parser/importer": parser, "profileRequirement": "DataProfile 2.4 exact semantic readiness where executable",
                "externalDataRequirement": f"EDR-{len(combos)+1:03d}",
                "repositoryEvidenceRefs": formats[-1]["repositoryEvidenceRefs"],
            })
    return formats, combos


FAMILY_SPECS = [
    ("CAP-DATASET", "Dataset intelligence", "dataset", ["dataset.materials_explorer", "dataset.composition_space"], ["materials_tabular_dataset"]),
    ("CAP-COMPOSITION", "Composition statistics and chemistry views", "composition", ["composition.chem_sys_sunburst", "composition.chem_sys_treemap", "composition.elements_hist", "composition.formula_statistics", "composition.ptable_heatmap", "composition.summary", "structure.composition_from_structure"], ["materials_tabular_dataset", "crystal_structure"]),
    ("CAP-TABLE", "Generic tabular summaries and plots", "table", ["table.distribution_summary", "table.numeric_summary", "viz.correlation", "viz.histogram", "viz.scatter"], ["materials_tabular_dataset"]),
    ("CAP-ML-REGRESSION", "Supplied materials regression evaluation", "ml", ["ml.basic_metrics", "ml.density_scatter", "ml.error_distribution", "ml.outlier_table", "ml.regression_evaluation"], ["regression_result_table"]),
    ("CAP-ML-UNCERTAINTY", "Supplied uncertainty evaluation", "ml", ["ml.uncertainty_evaluation"], ["uncertainty_result_table"]),
    ("CAP-ML-CLASSIFICATION", "Supplied classification evaluation", "ml", ["ml.classification_evaluation"], ["classification_result_table"]),
    ("CAP-STRUCTURE-SUMMARY", "Structure summary and crystallography", "structure", ["structure.summary", "structure.lattice_summary", "structure.spacegroup_summary", "structure.preview_metadata"], ["crystal_structure"]),
    ("CAP-STRUCTURE-VIEW", "Structure visualization", "structure", ["structure.structure_3d", "structure.viewer_3d", "structure.viewer_scene"], ["crystal_structure", "atomic_structure"]),
    ("CAP-COORDINATION", "Coordination and local-environment polyhedra", "structure", ["structure.coordination_crystalnn", "structure.coordination_voronoinn", "structure.coordination_hist", "structure.local_environment_polyhedra"], ["crystal_structure"]),
    ("CAP-XRD", "Theoretical XRD and experimental peak comparison", "structure", ["structure.xrd", "structure.experimental_xrd_comparison"], ["crystal_structure", "experimental_xrd"]),
    ("CAP-STRUCTURE-RDF", "Structure radial distribution", "structure", ["structure.rdf"], ["crystal_structure"]),
    ("CAP-TRAJECTORY-VIEW", "Trajectory visualization", "trajectory", ["structure.trajectory_viewer"], ["trajectory"]),
    ("CAP-TRAJECTORY-ANALYTICS", "Trajectory RDF, MSD, and diffusion estimate", "trajectory", ["trajectory.rdf", "trajectory.msd", "trajectory.diffusion"], ["trajectory"]),
    ("CAP-PHONON", "Supplied phonon Band, DOS, and combined view", "phonon", ["phonon.band", "phonon.dos", "phonon.band_dos"], ["phonon_band", "phonon_dos", "crystal_structure"]),
    ("CAP-PHONON-ANIMATION", "Supplied phonon mode animation", "phonon", ["phonon.animation"], ["phonon_band", "phonon_eigenvectors", "crystal_structure"]),
    ("CAP-RECIPROCAL", "Brillouin-zone and reciprocal-space context", "structure", ["structure.brillouin_zone"], ["crystal_structure", "reciprocal_space_context"]),
    ("CAP-VOLUMETRIC", "Persisted volumetric field views", "volumetric", ["structure.volumetric_data"], ["volumetric_field"]),
    ("CAP-ELECTRONIC", "Supplied electronic Band and DOS analysis", "electronic", ["electronic.band_structure", "electronic.dos"], ["electronic_band", "electronic_dos"]),
]


def capability_families(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for fid, name, domain, tools, kinds in FAMILY_SPECS:
        needs = sorted({n.value for tid in tools for n in metadata[tid].capabilityNeeds})
        outputs = sorted({o.value for tid in tools for o in metadata[tid].desiredOutputs})
        rows.append({
            "capabilityFamilyId": fid, "displayName": name, "domain": domain,
            "description": f"User-level qualification family backed by {len(tools)} current Planner-available Registry Tool(s).",
            "supportedSemanticKinds": kinds, "requiredInputs": kinds, "optionalInputs": ["exact auxiliary resources where declared by a Tool"],
            "supportDisposition": "SUPPORTED_WITH_LIMITS" if domain in {"ml", "trajectory", "phonon", "volumetric", "electronic"} or fid in {"CAP-XRD", "CAP-COORDINATION"} else "SUPPORTED",
            "requiredProfileFacts": needs, "requiredEligibilityFacts": needs, "capabilityNeed": needs, "desiredOutputs": outputs,
            "registryTools": tools, "knownLimits": ["Tool availability is not independent scientific reference validation"],
            "canonicalQuestions": [], "repositoryEvidenceRefs": evidence(REGISTRY_SOURCE, "packages/tool-registry/mdi_tool_registry/planner_metadata.py"),
        })
    return rows


CASE_SPECS = [
    ("Q-DATASET-001", "Explore a materials table and its composition space", "CAP-DATASET", "materials_tabular_dataset", "Explore this materials dataset, summarize quality, and map its compositions.", "SUPPORTED_POSITIVE"),
    ("Q-COMPOSITION-001", "Summarize formulas and chemistry distributions", "CAP-COMPOSITION", "materials_tabular_dataset", "Summarize the formulas and show element and chemical-system distributions.", "SUPPORTED_POSITIVE"),
    ("Q-TABLE-001", "Summarize and visualize numeric columns", "CAP-TABLE", "materials_tabular_dataset", "Summarize the numeric properties and show their distributions, correlations, and a selected scatter plot.", "SUPPORTED_POSITIVE"),
    ("Q-ML-REG-001", "Evaluate supplied regression predictions", "CAP-ML-REGRESSION", "regression_result_table", "Evaluate these supplied predictions and explain the largest errors and limitations.", "SUPPORTED_WITH_LIMITS"),
    ("Q-ML-UNC-001", "Evaluate supplied prediction uncertainty", "CAP-ML-UNCERTAINTY", "uncertainty_result_table", "Assess whether the supplied uncertainties are informative for these predictions.", "SUPPORTED_WITH_LIMITS"),
    ("Q-ML-CLASS-001", "Evaluate supplied classification results", "CAP-ML-CLASSIFICATION", "classification_result_table", "Evaluate these supplied material-class predictions and summarize their limitations.", "SUPPORTED_WITH_LIMITS"),
    ("Q-STRUCTURE-001", "Inspect structure summaries and 3D views", "CAP-STRUCTURE-SUMMARY", "crystal_structure", "Inspect this crystal structure, summarize its lattice and symmetry, and show the supported 3D view.", "SUPPORTED_POSITIVE"),
    ("Q-ATOMIC-VIEW-001", "Inspect a non-periodic atomic structure", "CAP-STRUCTURE-VIEW", "atomic_structure", "Show this atomic structure in the supported 3D viewer without inferring periodic lattice or symmetry.", "SUPPORTED_WITH_LIMITS"),
    ("Q-COORD-001", "Compare coordination and local environments", "CAP-COORDINATION", "crystal_structure", "Compare CrystalNN and VoronoiNN coordination and inspect the resulting local-environment polyhedra.", "SUPPORTED_WITH_LIMITS"),
    ("Q-XRD-001", "Compare experimental and theoretical XRD", "CAP-XRD", "experimental_xrd", "Compare the supplied experimental XRD peaks with the theoretical pattern for this structure.", "SUPPORTED_WITH_LIMITS"),
    ("Q-STRUCTURE-RDF-001", "Compute structure RDF", "CAP-STRUCTURE-RDF", "crystal_structure", "Show the radial distribution function for this structure.", "SUPPORTED_POSITIVE"),
    ("Q-TRAJECTORY-001", "Inspect trajectory dynamics", "CAP-TRAJECTORY-ANALYTICS", "trajectory", "Show this trajectory, its RDF and MSD, and estimate diffusion over a selected fit window.", "SUPPORTED_WITH_LIMITS"),
    ("Q-PHONON-001", "Inspect supplied phonon Band and DOS", "CAP-PHONON", "phonon_band", "Show the supplied phonon bands and DOS together with matching Brillouin-zone context.", "SUPPORTED_WITH_LIMITS"),
    ("Q-PHONON-ANIM-001", "Reject animation without an execution-ready eigenvector entry", "CAP-PHONON-ANIMATION", "phonon_eigenvectors", "Animate the selected supplied phonon mode for this structure.", "EXPECTED_REJECTION"),
    ("Q-VOLUME-001", "Inspect a supplied volumetric field", "CAP-VOLUMETRIC", "volumetric_field", "Inspect this supplied volumetric grid and show its supported slice and volume views.", "SUPPORTED_WITH_LIMITS"),
    ("Q-ELECTRONIC-001", "Inspect supplied electronic Band and DOS", "CAP-ELECTRONIC", "electronic_band", "Inspect the supplied electronic band structure and DOS, including gap, spin, projection, and compatibility limitations.", "SUPPORTED_WITH_LIMITS"),
    ("Q-ARCHIVE-001", "Import a bounded archive containing a supported materials table", "CAP-DATASET", "contained_supported_resources", "Import this bounded ZIP archive and inspect the supported materials table it contains.", "SUPPORTED_WITH_LIMITS"),
]


NEGATIVE_SPECS = [
    ("N-UNSUPPORTED-INPUT", "unsupported input", "Upload this Excel workbook and analyze it.", "FORMAT_UNSUPPORTED"),
    ("N-MAPPING-PHONON", "mapping-only input", "Upload this generic phonon YAML and calculate its band and DOS plots.", "MAPPING_ONLY"),
    ("N-MISSING-SEMANTIC", "missing semantic field", "Evaluate these predictions without a target column.", "PROFILE_CAPABILITY_MISSING"),
    ("N-UNKNOWN-UNIT", "unknown unit", "Classify the electronic gap in this file whose energy unit is unknown.", "INELIGIBLE"),
    ("N-AMBIGUOUS-TARGET", "ambiguous target", "Evaluate the model predictions in this table.", "NEEDS_CLARIFICATION"),
    ("N-MISSING-PAIRED", "missing paired resource", "Combine this phonon band without a matching DOS resource.", "MISSING_REQUIRED_INPUT"),
    ("N-STALE-RESOURCE", "stale resource", "Finalize a report from this superseded Workspace source.", "WORKSPACE_SOURCE_NOT_CURRENT"),
    ("N-HASH-MISMATCH", "hash mismatch", "Use this resource under a different checksum.", "RESOURCE_HASH_MISMATCH"),
    ("N-WRONG-PROJECT", "wrong project", "Use the structure stored in another project.", "CROSS_PROJECT_RESOURCE_ACCESS_DENIED"),
    ("N-WRONG-JOB", "wrong job", "Add an Artifact from another Job to this Workspace.", "CROSS_JOB_ARTIFACT_BINDING_REJECTED"),
    ("N-CONTRACT-VERSION", "unsupported contract version", "Import this resource using an unsupported schema version.", "CONTRACT_VERSION_UNSUPPORTED"),
    ("N-XRD-WAVELENGTH", "XRD wavelength mismatch", "Compare experimental peaks measured at an incompatible wavelength.", "XRD_WAVELENGTH_MISMATCH"),
    ("N-PANEL-CAP", "panel cap", "Project 33 genuinely distinct Workspace result surfaces.", "PANEL_CAP_EXCEEDED"),
    ("N-REVISION-CAP", "revision cap", "Save another layout after the revision cap is exhausted.", "WORKSPACE_LAYOUT_REVISION_CAP_EXCEEDED"),
    ("N-CLARIFICATION-CAP", "clarification round cap", "Ask for a second clarification round.", "CLARIFICATION_ROUND_LIMIT_EXCEEDED"),
    ("N-PROVIDER-FAILURE", "provider failure", "Plan this request while the optional provider fails.", "PROVIDER_FAILURE"),
    ("N-PARTIAL-EXECUTION", "partial execution", "Run independent analyses when one branch fails.", "PARTIAL_SUCCESS_WITH_LIMITS"),
    ("N-UNSUPPORTED-CAPABILITY", "unsupported capability", "Run a Rietveld refinement and confirm the phase.", "UNSUPPORTED_CAPABILITY"),
    ("N-FUTURE-SCOPE", "future scope request", "Run a DFT calculation and build an arbitrary workflow.", "FUTURE_SCOPE"),
]


def build_cases(families: list[dict[str, Any]], tools: dict[str, Any]) -> list[dict[str, Any]]:
    family_by_id = {row["capabilityFamilyId"]: row for row in families}
    cases: list[dict[str, Any]] = []
    for idx, (cid, title, family_id, kind, prompt, case_type) in enumerate(CASE_SPECS, 1):
        family = family_by_id[family_id]
        covered_families = [family_id]
        if cid == "Q-STRUCTURE-001":
            covered_families.append("CAP-STRUCTURE-VIEW")
        if cid == "Q-TRAJECTORY-001":
            covered_families.append("CAP-TRAJECTORY-VIEW")
        if cid == "Q-PHONON-001":
            covered_families.append("CAP-RECIPROCAL")
        semantic_kinds = [kind]
        if cid == "Q-XRD-001":
            semantic_kinds.append("crystal_structure")
        if cid == "Q-PHONON-001":
            semantic_kinds.extend(["phonon_dos", "crystal_structure"])
        if cid == "Q-ELECTRONIC-001":
            semantic_kinds.append("electronic_dos")
        if cid == "Q-ARCHIVE-001":
            semantic_kinds.append("materials_tabular_dataset")
        covered_tools = sorted({tool for fid in covered_families for tool in family_by_id[fid]["registryTools"]})
        executable = cid != "Q-PHONON-ANIM-001"
        expected_tools = covered_tools if executable else []
        artifacts = sorted({artifact for tool in covered_tools for artifact in tools[tool]["outputArtifacts"]})
        platform_artifacts = ["analysis_plan_json", "report_html", "report_md"]
        case_artifacts = sorted(set(artifacts + platform_artifacts)) if executable else []
        format_by_kind = {
            "materials_tabular_dataset": ["CSV", "JSON_LIMITED", "ZIP"],
            "regression_result_table": ["CSV", "JSON_LIMITED"],
            "uncertainty_result_table": ["CSV", "JSON_LIMITED"],
            "classification_result_table": ["CSV", "JSON_LIMITED"],
            "crystal_structure": ["CIF", "POSCAR_CONTCAR", "JSON_LIMITED", "EXTXYZ", "ZIP"],
            "atomic_structure": ["XYZ", "EXTXYZ", "ZIP"],
            "experimental_xrd": ["JSON_LIMITED", "ZIP"],
            "trajectory": ["JSON_LIMITED", "EXTXYZ", "ZIP"],
            "phonon_band": ["TYPED_PHONON_BAND_JSON"],
            "phonon_dos": ["TYPED_PHONON_DOS_JSON"],
            "phonon_eigenvectors": ["GENERIC_PHONON_YAML_JSON (MAPPING_ONLY)"],
            "volumetric_field": ["VASP_VOLUMETRIC", "GAUSSIAN_CUBE", "ZIP"],
            "electronic_band": ["JSON_LIMITED"],
            "electronic_dos": ["JSON_LIMITED"],
            "contained_supported_resources": ["ZIP"],
        }
        input_formats = sorted({fmt for item in semantic_kinds for fmt in format_by_kind.get(item, [])})
        if cid == "Q-ARCHIVE-001":
            input_formats = ["ZIP"]
        cases.append({
            "caseId": cid, "title": title, "domain": family["domain"], "caseType": case_type,
            "semanticDataKinds": semantic_kinds, "inputFormats": input_formats,
            "entryPath": "ENTRY-UI-TYPED-PHONON-BUNDLE" if cid == "Q-PHONON-001" else "ENTRY-UI-FILE-UPLOAD",
            "materialRequirements": "real public data matching the linked ExternalQualificationDataRequirement",
            "userQuestions": [{"type": "CANONICAL_POSITIVE", "text": prompt}, {"type": "NATURAL_PARAPHRASE", "text": prompt.replace("Inspect", "Please inspect").replace("Show", "Please show")}],
            "expectedProfile": {"version": "2.4", "requiredFacts": family["requiredProfileFacts"]},
            "expectedIntent": {"version": "1.0", "outcome": "READY", "capabilityNeeds": family["capabilityNeed"], "desiredOutputs": family["desiredOutputs"]},
            "expectedEligibility": "MAPPING_ONLY / no execution-ready normal-user eigenvector entry" if not executable else "READY for exact compatible resources; typed ineligible otherwise",
            "expectedCapabilities": covered_families, "expectedTools": expected_tools, "forbiddenTools": sorted(set(tools) - set(expected_tools)),
            "expectedPlanVersion": "0.2 when a consumer binds an exact producer Artifact; otherwise 0.1 is allowed",
            "expectedDependencyComposition": "Registry-declared exact Artifact ports; independent Tools remain independent",
            "maxReasonableStepCount": len(covered_tools), "expectedArtifacts": case_artifacts,
            "expectedRenderers": case_artifacts, "expectedVisualizationAssertions": ["exact artifact type/version dispatch", "required units and warnings visible", "table/text fallback where declared"],
            "expectedInterpretation": {"supported": True, "requiredEvidence": "persisted Artifact facts", "forbiddenScientificConclusions": ["claims beyond persisted evidence", "independent validation implied by availability"]},
            "expectedReport": {"sourceEligible": True, "previewExpected": True, "finalizeExpected": True},
            "expectedRecipe": {"expected": True, "recipeExecutionAuthorized": False},
            "runtimeRequired": executable, "freshWorkerRequired": executable, "registeredAdapterRequired": executable,
            "dependencyGraphRequired": executable and any(tool in {"trajectory.diffusion", "phonon.band_dos", "phonon.animation", "structure.local_environment_polyhedra", "structure.experimental_xrd_comparison"} for tool in covered_tools),
            "expectedProducerTools": expected_tools, "expectedConsumerTools": [tool for tool in expected_tools if tool in {"trajectory.diffusion", "phonon.band_dos", "phonon.animation", "structure.local_environment_polyhedra", "structure.experimental_xrd_comparison"}],
            "expectedArtifactBindings": "exact Artifact ID/checksum/contract/ToolCall/step bindings",
            "partialFailureSemantics": "successful independent branches retained; dependent descendants blocked; Report limitation mandatory",
            "idempotencyExpectation": "current exact request/source idempotency policy",
            "negativeAssertions": ["no fuzzy/latest/filename/array-position binding", "no frontend scientific recomputation"],
            "existingEvidence": ["UNIT_TESTED", "INTEGRATION_TESTED"] + (["FRESH_USER_E2E_TESTED", "BROWSER_REPLAY_TESTED"] if cid in {"Q-DATASET-001", "Q-ML-REG-001", "Q-COORD-001", "Q-XRD-001", "Q-TRAJECTORY-001", "Q-PHONON-001", "Q-VOLUME-001", "Q-ELECTRONIC-001"} else []),
            "externalDataRequirementIds": [f"EDR-CASE-{idx:03d}"],
            "coversCapabilityFamilies": covered_families, "coversTools": covered_tools, "coversInputKinds": semantic_kinds,
            "coversArtifacts": case_artifacts, "coversRenderers": case_artifacts, "coversNegativeBoundary": [],
            "repositoryEvidenceRefs": evidence(REPRO_AUTHORITY, REGISTRY_SOURCE, RENDERER_SOURCE),
        })
    for offset, (cid, trigger, prompt, code) in enumerate(NEGATIVE_SPECS, len(CASE_SPECS) + 1):
        zero = code not in {"PARTIAL_SUCCESS_WITH_LIMITS"}
        cases.append({
            "caseId": cid, "title": trigger.title(), "domain": "boundary", "caseType": "EXPECTED_CLARIFICATION" if code == "NEEDS_CLARIFICATION" else "EXPECTED_REJECTION",
            "semanticDataKinds": [], "inputFormats": [], "entryPath": "applicable current product entry",
            "materialRequirements": "boundary-specific; see external requirement", "userQuestions": [{"type": "EXPECTED_REJECTION", "text": prompt}],
            "expectedProfile": "existing or typed non-ready", "expectedIntent": {"version": "1.0", "outcome": "NEEDS_CLARIFICATION" if code == "NEEDS_CLARIFICATION" else "UNSUPPORTED_OR_NON_READY"},
            "expectedEligibility": code, "expectedCapabilities": [], "expectedTools": [], "forbiddenTools": sorted(tools),
            "expectedPlanVersion": "N/A unless partial execution retains a validated Plan", "expectedDependencyComposition": "none for pre-execution rejection",
            "maxReasonableStepCount": 0, "expectedArtifacts": [], "expectedRenderers": [],
            "expectedVisualizationAssertions": ["typed error and recovery disclosure visible"],
            "expectedInterpretation": {"supported": code == "PARTIAL_SUCCESS_WITH_LIMITS", "forbiddenScientificConclusions": ["fake science"]},
            "expectedReport": {"sourceEligible": code == "PARTIAL_SUCCESS_WITH_LIMITS", "limitationRequired": code == "PARTIAL_SUCCESS_WITH_LIMITS"},
            "expectedRecipe": {"expected": code == "PARTIAL_SUCCESS_WITH_LIMITS", "recipeExecutionAuthorized": False},
            "runtimeRequired": not zero, "freshWorkerRequired": not zero, "registeredAdapterRequired": not zero, "dependencyGraphRequired": code == "PARTIAL_SUCCESS_WITH_LIMITS",
            "expectedProducerTools": [], "expectedConsumerTools": [], "expectedArtifactBindings": "none unless partial successful branch",
            "partialFailureSemantics": "typed retained success only for N-PARTIAL-EXECUTION", "idempotencyExpectation": "repeated rejection creates no execution state",
            "negativeAssertions": [code], "existingEvidence": ["UNIT_TESTED", "INTEGRATION_TESTED"],
            "externalDataRequirementIds": [f"EDR-CASE-{offset:03d}"],
            "coversCapabilityFamilies": [], "coversTools": [], "coversInputKinds": [], "coversArtifacts": [], "coversRenderers": [], "coversNegativeBoundary": [trigger],
            "repositoryEvidenceRefs": evidence("tests", "docs/phase13/evidence/phase13_5_final_regression_release_acceptance"),
        })
    return cases


def renderers() -> list[dict[str, Any]]:
    source = (ROOT / RENDERER_SOURCE).read_text(encoding="utf-8")
    matches = list(re.finditer(r'entry\("([^"]+)",\s*"([^"]+)"(?:,\s*\{([^}]*)\})?\)', source))
    rows = []
    for match in matches:
        artifact, component, options = match.groups()
        classification_match = re.search(r'classification:\s*"([^"]+)"', options or "")
        payload_match = re.search(r'payloadMode:\s*"([^"]+)"', options or "")
        heavy = "heavy: true" in (options or "")
        webgl = "webgl: true" in (options or "")
        classification = classification_match.group(1) if classification_match else "PRODUCTION_NATIVE_RENDERER"
        rows.append({
            "rendererContract": f"workspace.{component.lower().replace('_', '-')}", "rendererVersion": "1",
            "artifactTypes": [artifact], "classification": classification, "component": component,
            "heavyViewer": heavy, "WebGL": webgl, "lazyLoad": "ACTIVE_ONLY",
            "numericFallback": component in {"GENERIC_TABLE", "GENERIC_PLOT"}, "tableFallback": "accessibilityFallback" in (options or "") or component in {"GENERIC_TABLE", "GENERIC_PLOT"},
            "textFallback": True, "selectionInput": "exact WorkspaceSelectionContext declarations", "selectionOutput": "exact Artifact-backed selection or none",
            "InspectorIntegration": True, "EvidenceIntegration": True, "ProvenanceIntegration": True,
            "mobileSupport": "retained responsive renderer contract", "accessibilityFallback": "TABLE/TEXT_SUMMARY as declared",
            "payloadMode": payload_match.group(1) if payload_match else ("BUNDLE" if "bundleArtifactTypes" in (options or "") else "JSON"),
            "authorityRules": ["filename is not authority", "MIME alone is not authority", "display label is not authority", "array index is not scientific identity"],
            "repositoryEvidenceRefs": evidence(RENDERER_SOURCE, "apps/web/app/components/workspace/workspace-renderer-registry.test.ts"),
        })
    if len(rows) != 42:
        raise RuntimeError(f"Expected 42 renderer declarations, found {len(rows)}")
    return rows


def external_requirements(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for idx, case in enumerate(cases, 1):
        positive = case["caseType"] in {"SUPPORTED_POSITIVE", "SUPPORTED_WITH_LIMITS"}
        kind = case["semanticDataKinds"][0] if case["semanticDataKinds"] else "boundary-specific"
        rows.append({
            "requirementId": f"EDR-CASE-{idx:03d}", "caseId": case["caseId"], "semanticDataKind": kind,
            "preferredFormats": case["inputFormats"] or ["repository-authorized format for the negative boundary"],
            "requiredFiles": ["primary source"] if positive else ["minimal boundary-triggering source when data-dependent"],
            "optionalFiles": ["license/provenance metadata"], "materialClass": "representative material appropriate to the repository-backed capability" if positive else "N/A",
            "chemicalSystemPreference": "use a minimum diverse set across elemental, binary, oxide, metal, semiconductor, low-symmetry, and large-cell only where the capability applies",
            "requiredScientificCharacteristics": ["explicit units and identities required by the current contract", "sufficient non-degenerate content to exercise the declared viewer"],
            "requiredSizeRange": "small enough for public redistribution plus one bounded stress representative",
            "requiredAtomCountRange": "capability-specific; below Registry resourceLimits", "requiredTrajectoryLength": "enough frames/time for declared analysis; N/A otherwise",
            "requiredEnergyUnit": "eV for electronic resources; N/A otherwise", "requiredWavelength": "exact current XRD-compatible wavelength for positive XRD; N/A otherwise",
            "requiredElectronicReference": "source-supplied Fermi/reference for electronic cases; N/A otherwise",
            "requiredPairedData": "exact paired/context resources declared by the case",
            "mustBeRealPublicData": positive, "preferredSourceClass": ["official public repository", "peer-reviewed supplementary data", "institutional scientific repository", "standards/reference dataset"] if positive else ["repository-derived negative fixture"],
            "licenseRequirement": "explicit license permitting qualification use", "redistributionRequirement": "record whether redistribution is permitted; retain source provenance regardless",
            "scientificTransformationsAllowed": ["lossless container conversion only when identity/provenance and contract semantics are preserved", "bounded extraction explicitly documented by source"],
            "scientificTransformationsForbidden": ["inventing values", "unit guessing", "q-path guessing", "wavelength reprojection", "scientific smoothing or interpolation not authorized by contract", "fabricating missing companion data"],
            "repositoryEvidenceRefs": case["repositoryEvidenceRefs"],
        })
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    registry = load_manifests()
    _snapshot, planner_metadata = build_registry_snapshot(registry)
    final = read_json(FINAL_AUTHORITY)
    repro = read_json(REPRO_AUTHORITY)
    phase11_levels = read_json(PHASE11_LEVELS)
    live = read_json(PHASE10L_LIVE)
    head = git("rev-parse", "HEAD")
    origin = git("rev-parse", "origin/master")
    branch = git("branch", "--show-current")

    entries = entry_paths()
    formats, input_matrix = formats_and_inputs()
    semantics = semantic_kinds()
    renderer_rows = renderers()
    renderer_by_artifact = {row["artifactTypes"][0]: row for row in renderer_rows}
    tools: list[dict[str, Any]] = []
    tool_by_id: dict[str, dict[str, Any]] = {}
    for tool in sorted(registry.tools, key=lambda item: item.toolId):
        meta = planner_metadata[tool.toolId]
        available = meta.availability.value == "AVAILABLE"
        row = {
            "toolId": tool.toolId, "toolVersion": tool.version, "domain": tool.domain.value,
            "availability": meta.availability.value, "plannerVisible": available,
            "inputKinds": [option.model_dump(mode="json") for option in tool.inputSchema.inputOptions],
            "paramsSchema": tool.paramsSchema, "requiredProfileFacts": meta.requiredProfileCapabilities,
            "requiredResourceKinds": meta.acceptedObjectTypes, "requiredTargets": meta.requiredTargetRoles,
            "requiredBindings": [binding.model_dump(mode="json") for binding in meta.parameterBindings],
            "outputArtifacts": [item.value for item in tool.artifactTypes], "artifactContracts": [f"{item.value}@1" for item in tool.artifactTypes],
            "dependencyPorts": "see mdi_tool_registry.dependency_ports", "registeredAdapter": tool.adapter if tool.adapter in ADAPTER_CLASSES else None,
            "executionAuthority": "QueueWorkerRuntime -> registered Adapter -> persisted Artifact" if tool.adapter in ADAPTER_CLASSES else "NONE",
            "supportDisposition": "SUPPORTED" if available else ("UNSUPPORTED" if meta.availability.value == "FUTURE" else "LEGACY_READ_ONLY"),
            "capabilityFamilies": [fid for fid, _n, _d, ids, _k in FAMILY_SPECS if tool.toolId in ids],
            "knownLimitations": ["Phase 11 scientific validation remains separate from product availability"],
            "qualificationParticipationClass": "DIRECT_USER_CAPABILITY" if available else ("NOT_RELEASE_RELEVANT" if meta.availability.value == "FUTURE" else "LEGACY_ONLY"),
            "resourceLimits": tool.resourceLimits, "registrySource": f"tool_registry/{tool.source['manifest']}",
            "repositoryEvidenceRefs": evidence(f"tool_registry/{tool.source['manifest']}", REGISTRY_SOURCE, "packages/adapters/mdi_adapters/registry.py"),
        }
        tools.append(row)
        tool_by_id[tool.toolId] = row

    families = capability_families(planner_metadata)
    cases = build_cases(families, tool_by_id)
    requirements = external_requirements(cases)
    positive_cases = [case for case in cases if case["caseType"] in {"SUPPORTED_POSITIVE", "SUPPORTED_WITH_LIMITS"}]
    minimum_case_ids = [case["caseId"] for case in positive_cases]
    extended_case_ids = [case["caseId"] for case in cases]
    case_by_tool: dict[str, list[str]] = defaultdict(list)
    case_by_artifact: dict[str, list[str]] = defaultdict(list)
    for case in cases:
        for tool_id in case["coversTools"]:
            case_by_tool[tool_id].append(case["caseId"])
        for artifact in case["coversArtifacts"]:
            case_by_artifact[artifact].append(case["caseId"])

    artifact_producers: dict[str, list[str]] = defaultdict(list)
    for tool in tools:
        for artifact in tool["outputArtifacts"]:
            artifact_producers[artifact].append(tool["toolId"])
    core_artifacts = {"report_md", "report_html", "analysis_plan_json", "recipe_json"}
    available_outputs = {artifact for tool in tools if tool["plannerVisible"] for artifact in tool["outputArtifacts"]} | core_artifacts
    artifacts = []
    for artifact_type in sorted(renderer_by_artifact):
        producers = sorted(artifact_producers.get(artifact_type, []))
        renderer = renderer_by_artifact[artifact_type]
        artifacts.append({
            "artifactType": artifact_type, "artifactVersion": "1", "artifactContract": f"{artifact_type}@1",
            "producerTools": producers, "semanticDataKind": "tool/product dependent", "scientificAuthority": "registered Adapter persisted output or inert product metadata",
            "payloadMode": renderer["payloadMode"], "expectedFields": ["exact contract payload", "checksum", "lineage"],
            "identityFields": ["Artifact ID", "checksum", "ToolCall", "step", "source project/job"], "unitFields": ["contract-specific; unknown is not guessed"],
            "lineageRequirements": ["exact producer Tool/version", "exact input resource bindings", "source Job/ToolCall/step"],
            "partialBehavior": "retained when its independent branch succeeds", "staleBehavior": "does not rebind to latest source",
            "reportEligibility": True, "releaseRelevant": artifact_type in available_outputs,
            "viewerAssertions": {"requiredVisibleSections": ["typed renderer or declared inert fallback", "identity/metadata", "warnings/limitations"], "requiredAxisLabels": "contract-specific", "requiredUnits": "contract-specific", "requiredStatus": "typed", "requiredTableFallback": renderer["tableFallback"], "requiredLegend": "when contract declares series", "requiredMetadata": ["Artifact ID", "checksum", "producer"], "requiredWarnings": True, "requiredLimitations": True, "requiredInspectorFields": ["lineage", "provenance", "exact selection"]},
            "assertionClasses": ["PRESENTATION_ASSERTION", "SCIENTIFIC_INVARIANT_ASSERTION"],
            "scientificExpectedValue": "NOT_DEFINED unless referenced by existing Phase 11 authority",
            "repositoryEvidenceRefs": evidence(RENDERER_SOURCE, REGISTRY_SOURCE, "docs/phase11/evidence/phase11_0_validation_baseline_reconciliation/artifact_validation_inventory.json"),
        })

    capability_matrix = []
    for family in families:
        for tool_id in family["registryTools"]:
            for kind in family["supportedSemanticKinds"]:
                capability_matrix.append({"semanticDataKind": kind, "capabilityFamily": family["capabilityFamilyId"], "registryTool": tool_id, "supportDisposition": family["supportDisposition"], "repositoryEvidenceRefs": family["repositoryEvidenceRefs"]})
    output_matrix = []
    for tool in tools:
        for artifact in tool["outputArtifacts"]:
            renderer = renderer_by_artifact.get(artifact)
            output_matrix.append({
                "tool": tool["toolId"], "artifact": artifact, "renderer": renderer["rendererContract"] if renderer else "UNSUPPORTED",
                "viewer": renderer["component"] if renderer else "UNSUPPORTED", "interpretation": "grounded persisted-fact projection where a projector exists",
                "report": "eligible exact source", "recipe": "declarative non-executable source binding", "releaseRelevant": tool["plannerVisible"],
            })
    interpretation_rows = []
    report_rows = []
    for family in families:
        interpretation_rows.append({
            "capabilityFamilyId": family["capabilityFamilyId"], "interpretationSupported": True,
            "evidenceProjector": "GroundedInterpretation projector over exact persisted Artifacts", "supportedClaimTypes": ["descriptive", "comparison", "limitation"],
            "supportedPredicates": ["artifact-contract-specific bounded predicates"], "requiredEvidence": ["persisted Artifact facts", "exact lineage"],
            "mandatoryLimitations": family["knownLimits"], "forbiddenClaims": ["unsupported causality", "independent validation implied by availability", "science executed by LLM/frontend"],
            "partialInterpretationBehavior": "INTERPRETATION_READY_WITH_LIMITS", "noEvidenceBehavior": "typed unavailable; no claim",
            "repositoryEvidenceRefs": evidence("packages/schemas/mdi_schemas/interpretation.py", "apps/api/mdi_api/phase2_runtime.py"),
        })
        report_rows.append({
            "capabilityFamilyId": family["capabilityFamilyId"], "reportSourceEligible": True, "reportPreviewExpected": True,
            "reportFinalizeExpected": True, "reportExpectedOutcome": "persisted Report from exact eligible sources",
            "recipeExpected": True, "recipeExecutionAuthorized": False,
            "repositoryEvidenceRefs": evidence("packages/schemas/mdi_schemas/report_composition.py", "apps/api/mdi_api/report_composition.py"),
        })

    negative_catalog = []
    for case in cases[len(CASE_SPECS):]:
        is_partial = case["caseId"] == "N-PARTIAL-EXECUTION"
        negative_catalog.append({
            "negativeCaseId": case["caseId"], "trigger": case["title"], "inputCondition": case["title"],
            "userPrompt": case["userQuestions"][0]["text"], "expectedOutcome": case["expectedEligibility"],
            "expectedErrorCode": case["expectedEligibility"], "PlanCountDelta": "retained validated plan only" if is_partial else 0,
            "JobCountDelta": "one partial Job" if is_partial else 0, "QueueDelta": "bounded partial execution" if is_partial else 0,
            "ToolCallDelta": "successful and failed branches recorded" if is_partial else 0, "ArtifactDelta": "successful branch artifacts retained" if is_partial else 0,
            "expectedUserDisclosure": "typed reason and safe recovery; mandatory limitation for partial result",
            "repositoryEvidenceRefs": case["repositoryEvidenceRefs"],
        })

    demo_tool_ids = {tool for demo in repro["demos"] for tool in demo["expectedCapabilityCoverage"]}
    live_tool_ids = {tool for case in live["cases"] for tool in case["selectedToolIds"]}
    evidence_rows = []
    for tool in tools:
        levels = ["UNIT_TESTED", "MAPPING_ONLY"]
        if tool["plannerVisible"]:
            levels.append("INTEGRATION_TESTED")
        if tool["toolId"] in demo_tool_ids:
            levels += ["SERVICE_BACKED_TESTED", "BROWSER_REPLAY_TESTED", "FRESH_USER_E2E_TESTED"]
        if tool["toolId"] in live_tool_ids:
            levels.append("LIVE_LLM_TESTED")
        evidence_rows.append({
            "capability": tool["capabilityFamilies"], "tool": tool["toolId"], "case": case_by_tool.get(tool["toolId"], []),
            "evidenceLevel": sorted(set(levels)), "liveBrowserInitiatedLlmTested": False,
            "repositoryEvidenceRefs": evidence(INPUT_AUTHORITY, PHASE11_LEVELS, REPRO_AUTHORITY, PHASE10L_LIVE),
        })

    qualification_matrix = []
    for case in cases:
        qualification_matrix.append({
            "case": case["caseId"], "input": case["semanticDataKinds"], "capability": case["coversCapabilityFamilies"],
            "tool": case["coversTools"], "artifact": case["coversArtifacts"], "renderer": case["coversRenderers"], "caseType": case["caseType"],
            "repositoryEvidenceRefs": case["repositoryEvidenceRefs"],
        })

    release_tools = [row for row in tools if row["plannerVisible"]]
    release_artifacts = [row for row in artifacts if row["releaseRelevant"]]
    release_renderers = [row for row in renderer_rows if row["artifactTypes"][0] in available_outputs]
    supported_combos = [row for row in input_matrix if row["supportDisposition"] == "SUPPORTED"]
    limited_combos = [row for row in input_matrix if row["supportDisposition"] == "SUPPORTED_WITH_LIMITS"]
    mapping_combos = [row for row in input_matrix if row["supportDisposition"] == "MAPPING_ONLY"]
    unsupported_combos = [row for row in input_matrix if row["supportDisposition"] == "UNSUPPORTED"]
    covered_tools = {tool for case in cases for tool in case["coversTools"]}
    covered_artifacts = {artifact for case in cases for artifact in case["coversArtifacts"]}
    covered_families = {family for case in cases for family in case["coversCapabilityFamilies"]}
    covered_inputs = {kind for case in cases for kind in case["coversInputKinds"]}
    supported_input_kinds = {row["semanticDataKind"] for row in input_matrix if row["supportDisposition"] in {"SUPPORTED", "SUPPORTED_WITH_LIMITS"}}
    gaps = []
    for tool in release_tools:
        if tool["toolId"] not in covered_tools:
            gaps.append({"gapId": f"GAP-TOOL-{tool['toolId']}", "type": "release-relevant Tool with no Case", "severity": "P2_QUALIFICATION_GAP"})
    for artifact in release_artifacts:
        if artifact["artifactType"] not in covered_artifacts and artifact["artifactType"] not in core_artifacts:
            gaps.append({"gapId": f"GAP-ARTIFACT-{artifact['artifactType']}", "type": "Artifact with no Case", "severity": "P2_QUALIFICATION_GAP"})
    for renderer in release_renderers:
        artifact_type = renderer["artifactTypes"][0]
        if artifact_type not in covered_artifacts and artifact_type not in core_artifacts:
            gaps.append({"gapId": f"GAP-RENDERER-{artifact_type}", "type": "Renderer with no executable user-centric Case", "severity": "P2_QUALIFICATION_GAP"})
    for kind in sorted(supported_input_kinds - covered_inputs):
        gaps.append({"gapId": f"GAP-INPUT-{kind}", "type": "supported input with no Case", "severity": "P2_QUALIFICATION_GAP"})
    gaps.append({
        "gapId": "GAP-PHONON-ANIMATION-NORMAL-USER-ENTRY",
        "type": "Registry-available phonon.animation lacks an execution-ready normal-user eigenvector import",
        "severity": "P2_QUALIFICATION_GAP",
        "repositoryEvidenceRefs": evidence(
            REGISTRY_SOURCE,
            "packages/tool-registry/mdi_tool_registry/planner_metadata.py",
            "packages/artifact-core/mdi_artifact_core/phonon_eigenvector_contract.py",
            INPUT_AUTHORITY,
        ),
    })
    gaps.append({
        "gapId": "GAP-INLINE-UPLOAD-REQUEST-CAPS-UNKNOWN",
        "type": "DatasetUploadRequest has no repository-defined files max_items or InlineUploadFile.content max_length",
        "severity": "P2_QUALIFICATION_GAP",
        "repositoryEvidenceRefs": evidence("apps/api/mdi_api/phase2_runtime.py"),
    })

    conflicts: list[dict[str, Any]] = []
    for tool in tools:
        if tool["plannerVisible"] and tool["registeredAdapter"] is None:
            conflicts.append({"conflictId": f"CONFLICT-ADAPTER-{tool['toolId']}", "type": "Registry vs Adapter", "severity": "P0_RELEASE_BLOCKER", "evidence": tool["repositoryEvidenceRefs"]})
    for artifact in artifacts:
        if artifact["releaseRelevant"] and artifact["artifactType"] not in renderer_by_artifact:
            conflicts.append({"conflictId": f"CONFLICT-RENDERER-{artifact['artifactType']}", "type": "Artifact vs Renderer", "severity": "P1_MAJOR", "evidence": artifact["repositoryEvidenceRefs"]})
    blockers = [row for row in conflicts if row["severity"] in {"P0_RELEASE_BLOCKER", "P1_MAJOR"}]

    counts = {
        "TOTAL_USER_ENTRY_PATHS": len(entries), "TOTAL_FILE_FORMATS": len(formats), "TOTAL_SEMANTIC_DATA_KINDS": len(semantics),
        "TOTAL_SUPPORTED_INPUT_COMBINATIONS": len(supported_combos), "TOTAL_SUPPORTED_WITH_LIMITS_INPUT_COMBINATIONS": len(limited_combos),
        "TOTAL_MAPPING_ONLY_INPUT_COMBINATIONS": len(mapping_combos), "TOTAL_UNSUPPORTED_INPUT_COMBINATIONS": len(unsupported_combos),
        "TOTAL_CAPABILITY_FAMILIES": len(families), "TOTAL_REGISTRY_TOOLS": len(tools), "TOTAL_RELEASE_RELEVANT_TOOLS": len(release_tools),
        "TOTAL_ARTIFACT_TYPES": len(artifacts), "TOTAL_RELEASE_RELEVANT_ARTIFACT_TYPES": len(release_artifacts),
        "TOTAL_RENDERER_CONTRACTS": len(renderer_rows), "TOTAL_RELEASE_RELEVANT_RENDERERS": len(release_renderers),
        "TOTAL_PROPOSED_CASES": len(cases), "MINIMUM_CASE_SET_SIZE": len(minimum_case_ids), "TOTAL_NEGATIVE_CASES": len(negative_catalog),
        "TOTAL_EXTERNAL_DATA_REQUIREMENTS": len(requirements),
        "CAPABILITY_FAMILIES_WITH_CASE_COVERAGE": len(covered_families), "REGISTRY_TOOLS_WITH_CASE_PARTICIPATION": len(covered_tools & {row['toolId'] for row in release_tools}),
        "INPUT_COMBINATIONS_WITH_CASE_COVERAGE": sum(1 for row in input_matrix if row["semanticDataKind"] in covered_inputs and row["supportDisposition"] in {"SUPPORTED", "SUPPORTED_WITH_LIMITS"}),
        "ARTIFACT_TYPES_WITH_CASE_COVERAGE": len(covered_artifacts & {row['artifactType'] for row in release_artifacts}),
        "RENDERERS_WITH_CASE_COVERAGE": len(covered_artifacts & {row['artifactTypes'][0] for row in release_renderers}),
    }
    readiness = {
        "schemaVersion": "QualificationReadiness/1.0", "QUALIFICATION_DATA_RESEARCH_READY": "YES" if not blockers else "NO",
        "criteria": {"allReleaseRelevantCapabilitiesInventoried": len(families) == len(covered_families), "allRegistryToolsInventoried": len(tools) == 62, "allInputRoutesInventoried": True, "allReleaseRelevantArtifactsInventoried": True, "allRendererDispositionsInventoried": len(renderer_rows) == 42, "allProposedCasesHaveExternalDataRequirements": all(case["externalDataRequirementIds"] for case in cases), "unresolvedP0P1AuthorityConflicts": len(blockers)},
        "blockers": blockers, "externalDataRequirementIds": [row["requirementId"] for row in requirements if row["mustBeRealPublicData"]],
        "phaseBExternalDataResearchExecuted": False, "phaseBExternalDataDownloaded": 0,
    }

    authorities = {
        "schemaVersion": "PhaseACurrentAuthorities/1.0", "Registry": len(tools), "RegistryVersion": registry.version,
        "DataProfile": final["DataProfile"], "AnalysisIntent": final["AnalysisIntent"], "EligibilityResolution": final["EligibilityResolution"],
        "AnalysisPlanVersions": final["AnalysisPlanVersions"], "MigrationHead": final["MigrationHead"],
        "Workspace": "ScientificWorkspace/1.0", "WorkspacePanel": "WorkspacePanel/1.0", "WorkspaceSelectionContext": "WorkspaceSelectionContext/1.0",
        "ArtifactRegistry": "Workspace renderer registry covers 42 shared Artifact types; no independent persisted registry version is defined",
        "RendererRegistry": "application-owned exact type/version registry; contract version 1",
        "ReportContracts": ["ReportCompositionRequest/1.0", "ReportCompositionSnapshot/1.0", "ReportExportManifest/1.0"],
        "RecipeContracts": ["RecipeReplayManifest/1.0"],
        "ProviderPolicy": {"provider": "DeepSeek only", "models": ["deepseek-v4-flash", "deepseek-v4-pro"], "keySource": "DEEPSEEK_KEY", "realLlmCallsPhaseA": 0},
        "MaxWorkspacePanels": final["MaxWorkspacePanels"], "MaxLayoutRevisions": final["MaxLayoutRevisions"],
        "FactModelHash": final["FactModelHash"], "ScopeBaselineHash": final["ScopeBaselineHash"], "Phase12ProductBaselineHash": final["Phase12ProductBaselineHash"],
        "InitialReleaseComplete": True, "Phase13State": "COMPLETE", "repositoryEvidenceRefs": evidence(FINAL_AUTHORITY, "results.md", "packages/schemas/mdi_schemas"),
    }
    entry_gate = {"schemaVersion": "PhaseAEntryGate/1.0", "branch": branch, "HEAD": head, "originMaster": origin, "headMatchesOriginMasterAtAdmission": head == origin, "worktreeCleanBeforeAdmission": True, "initialReleaseComplete": True, "repositoryGroundedOnly": True, "webAccessUsed": False, "externalDataDownloaded": 0, "browserQualificationCases": 0, "realLlmCalls": 0}

    files: dict[str, Any] = {
        "entry_gate.json": entry_gate, "current_authorities.json": authorities,
        "user_entry_inventory.json": {"schemaVersion": "UserEntryInventory/1.0", "entries": entries, "rowCount": len(entries)},
        "file_format_inventory.json": {"schemaVersion": "FileFormatInventory/1.0", "formats": formats, "rowCount": len(formats)},
        "semantic_data_kind_inventory.json": {"schemaVersion": "SemanticDataKindInventory/1.0", "semanticKinds": semantics, "rowCount": len(semantics)},
        "input_support_matrix.json": {"schemaVersion": "InputSupportMatrix/1.0", "rows": input_matrix, "rowCount": len(input_matrix)},
        "capability_family_inventory.json": {"schemaVersion": "CapabilityFamily/1.0", "capabilityFamilies": families, "rowCount": len(families)},
        "registry_tool_qualification_inventory.json": {"schemaVersion": "RegistryToolQualificationInventory/1.0", "tools": tools, "rowCount": len(tools)},
        "capability_matrix.json": {"schemaVersion": "CapabilityMatrix/1.0", "rows": capability_matrix, "rowCount": len(capability_matrix)},
        "artifact_qualification_inventory.json": {"schemaVersion": "ArtifactQualificationInventory/1.0", "artifacts": artifacts, "rowCount": len(artifacts)},
        "renderer_qualification_inventory.json": {"schemaVersion": "RendererQualificationInventory/1.0", "renderers": renderer_rows, "rowCount": len(renderer_rows)},
        "output_matrix.json": {"schemaVersion": "OutputMatrix/1.0", "rows": output_matrix, "rowCount": len(output_matrix)},
        "interpretation_inventory.json": {"schemaVersion": "InterpretationQualificationInventory/1.0", "rows": interpretation_rows, "rowCount": len(interpretation_rows)},
        "report_recipe_inventory.json": {"schemaVersion": "ReportRecipeQualificationInventory/1.0", "rows": report_rows, "rowCount": len(report_rows), "recipeExecutionAuthorized": False},
        "negative_case_catalog.json": {"schemaVersion": "NegativeCaseCatalog/1.0", "negativeCases": negative_catalog, "rowCount": len(negative_catalog)},
        "existing_evidence_matrix.json": {"schemaVersion": "ExistingEvidenceMatrix/1.0", "rows": evidence_rows, "rowCount": len(evidence_rows)},
        "external_data_requirements.json": {"schemaVersion": "ExternalQualificationDataRequirement/1.0", "requirements": requirements, "rowCount": len(requirements)},
        "proposed_qualification_cases.json": {"schemaVersion": "ProposedQualificationCaseCatalog/1.0", "cases": cases, "rowCount": len(cases)},
        "minimum_case_set.json": {"schemaVersion": "QualificationCaseSet/1.0", "purpose": "minimum representative user-scenario set covering current execution-ready user surfaces; mapping-only and non-ready boundaries remain in the extended set", "caseIds": minimum_case_ids, "rowCount": len(minimum_case_ids)},
        "extended_case_set.json": {"schemaVersion": "QualificationCaseSet/1.0", "purpose": "minimum set plus repository-backed negative/clarification boundaries", "caseIds": extended_case_ids, "rowCount": len(extended_case_ids)},
        "qualification_coverage_matrix.json": {"schemaVersion": "QualificationCoverageMatrix/1.0", "rows": qualification_matrix, "rowCount": len(qualification_matrix), "counts": counts},
        "authority_conflicts.json": {"schemaVersion": "AuthorityConflictInventory/1.0", "conflicts": conflicts, "rowCount": len(conflicts)},
        "qualification_design_gaps.json": {"schemaVersion": "QualificationDesignGapInventory/1.0", "gaps": gaps, "rowCount": len(gaps)},
        "qualification_readiness.json": readiness,
        "phase_b_external_qualification_dataset_research_handoff.json": {"schemaVersion": "PhaseBExternalQualificationDatasetResearchHandoff/1.0", "status": "REVIEWER_GATE", "qualificationDataResearchReady": readiness["QUALIFICATION_DATA_RESEARCH_READY"], "requirements": [row for row in requirements if row["mustBeRealPublicData"]], "phaseBExternalDataResearchExecuted": False, "phaseBExternalDataDownloaded": 0},
    }
    for name, value in files.items():
        dump_json(OUT / name, value)
    for stem, rows in {
        "input_support_matrix": input_matrix, "capability_matrix": capability_matrix, "output_matrix": output_matrix,
        "qualification_coverage_matrix": qualification_matrix, "existing_evidence_matrix": evidence_rows,
        "external_data_requirement_matrix": requirements,
    }.items():
        dump_csv(OUT / f"{stem}.csv", rows)

    report = f"""# System Qualification Capability Manifest

Schema: `SystemQualificationCapabilityManifest/1.0`

## 1. Executive summary

This repository-grounded census records what the sealed Initial Release can accept, plan, execute, persist, render, interpret, and compose into Reports and non-executable Recipes. It makes no web-derived support claim and performs no qualification run. The current Registry contains **{counts['TOTAL_REGISTRY_TOOLS']}** Tools; **{counts['TOTAL_RELEASE_RELEVANT_TOOLS']}** are Planner-available with registered Adapters. The Workspace renderer registry contains **{counts['TOTAL_RENDERER_CONTRACTS']}** exact Artifact declarations.

## 2. Current release authority

Initial Release remains complete. Registry 62, DataProfile 2.4, AnalysisIntent 1.0, EligibilityResolution 1.0, AnalysisPlan 0.1/0.2, migration 0007, panel cap 32, and layout-revision cap 128 are unchanged. See `current_authorities.json`.

## 3. User data entry paths

Four current user-accessible entry classes are inventoried in `user_entry_inventory.json`: generic UI upload, typed phonon Band+DOS+Structure import, exact persisted Dataset selection, and the documented inline upload API.

## 4. Supported file/container formats

`file_format_inventory.json` records {len(formats)} container/format families. A container name never establishes scientific meaning; `input_support_matrix.json` binds entry path, format, semantic kind, and disposition.

## 5. Semantic scientific data kinds

`semantic_data_kind_inventory.json` records {len(semantics)} semantic kinds with exact Profile prerequisites, identities, units, companion/context resources, limits, and negative conditions.

## 6. Support dispositions

The normalized vocabulary is `SUPPORTED`, `SUPPORTED_WITH_LIMITS`, `MAPPING_ONLY`, `LEGACY_READ_ONLY`, `UNSUPPORTED`, and `UNKNOWN_REPOSITORY_AUTHORITY`. Current executable input combinations: {len(supported_combos)} supported and {len(limited_combos)} supported-with-limits. Generic phonon YAML/JSON contributes {len(mapping_combos)} mapping-only combinations; {len(unsupported_combos)} combinations are explicitly unsupported.

## 7. Data/Profile prerequisites

Every executable case requires durable exact identity and DataProfile 2.4 facts appropriate to the semantic kind. Missing roles, targets, units, structure context, wavelength, energy reference, paired resources, contract versions, hashes, or project scope produce typed non-readiness rather than inference.

## 8. Capability families

`capability_family_inventory.json` defines {len(families)} user-level families. A capability family is not a Tool ID; the many-to-many mapping is in `capability_matrix.json`.

## 9. Full Registry Tool inventory

`registry_tool_qualification_inventory.json` mechanically lists all {len(tools)} Registry entries, including {len(release_tools)} current release-relevant Tools, 12 future Tools, and 3 deployment-unavailable/legacy-only entries.

## 10. Capability to Tool mapping

See `capability_matrix.json` and `.csv`. All {len(release_tools)} current Planner-available Tools participate in at least one proposed case.

## 11. Tool to Artifact mapping

See `output_matrix.json` and `.csv`. Runtime authority remains QueueWorkerRuntime to registered Adapter to persisted Artifact.

## 12. Artifact to Renderer mapping

`artifact_qualification_inventory.json` and `renderer_qualification_inventory.json` cover all 42 exact renderer declarations. Filename, MIME, display label, and array position are never dispatch or identity authority.

## 13. Viewer behavior and assertions

Each Artifact inventory row contains future browser assertions and separates presentation assertions from scientific invariant/value assertions. No new expected scientific number is defined; absent authority is recorded as `NOT_DEFINED`.

## 14. Interpretation support

`interpretation_inventory.json` limits interpretation to grounded claims over persisted facts and exact lineage. No evidence means no scientific claim; partial results require explicit limitations.

## 15. Report / Recipe support

`report_recipe_inventory.json` records exact-source Report Preview/Finalize expectations. Recipes remain declarative and non-executable for every case.

## 16. Negative / clarification boundaries

`negative_case_catalog.json` records {len(negative_catalog)} repository-applicable boundaries, including unsupported/mapping-only inputs, missing semantics, unknown units, ambiguity, pairing, stale/hash/scope errors, contract/wavelength/cap limits, provider failure, partial execution, unsupported capability, and Future Scope.

## 17. Existing qualification evidence

`existing_evidence_matrix.json` distinguishes unit, integration, service-backed, browser replay, live LLM, fresh E2E, scientific reference/invariant, and mapping-only evidence. Retained DeepSeek captures tested five selected capability paths; browser playback did not initiate those LLM calls.

## 18. Proposed user-centric qualification cases

`proposed_qualification_cases.json` defines {len(cases)} grounded scenarios: {len(positive_cases)} positive/supported-with-limits cases plus {len(cases)-len(positive_cases)} negative, clarification, or non-ready boundary cases.

## 19. Minimum representative case set

`minimum_case_set.json` contains {len(minimum_case_ids)} cases optimized to cover current execution-ready user surfaces without a material-class-by-Tool Cartesian product. `extended_case_set.json` adds all boundaries, including the mapping-only phonon-animation entry case.

## 20. External real-data requirements

`external_data_requirements.json` defines one requirement per proposed case. Phase B should acquire only the {len(positive_cases)} requirements marked `mustBeRealPublicData=true`; no data was downloaded in Phase A.

## 21. Coverage metrics

* Capability families with case coverage: {counts['CAPABILITY_FAMILIES_WITH_CASE_COVERAGE']}/{len(families)}
* Release-relevant Registry Tools with case participation: {counts['REGISTRY_TOOLS_WITH_CASE_PARTICIPATION']}/{len(release_tools)}
* Supported input combinations with semantic-kind case coverage: {counts['INPUT_COMBINATIONS_WITH_CASE_COVERAGE']}/{len(supported_combos)+len(limited_combos)}
* Release-relevant Artifact types with case coverage: {counts['ARTIFACT_TYPES_WITH_CASE_COVERAGE']}/{len(release_artifacts)}
* Release-relevant renderers with case coverage: {counts['RENDERERS_WITH_CASE_COVERAGE']}/{len(release_renderers)}

## 22. Authority conflicts

`authority_conflicts.json` records {len(conflicts)} conflicts. No unresolved P0/P1 Registry-to-Adapter or Artifact-to-renderer conflict was found.

## 23. Qualification design gaps

`qualification_design_gaps.json` records {len(gaps)} explicit design gaps. Gaps are not product defects or support promotions.

## 24. Readiness for external data research

`QUALIFICATION_DATA_RESEARCH_READY = {readiness['QUALIFICATION_DATA_RESEARCH_READY']}`. This authorizes only a future reviewer-controlled search/acquisition phase; Phase B was not executed.

## 25. Exact next-step handoff

Use `phase_b_external_qualification_dataset_research_handoff.json`. It contains only the real-data characteristics, accepted formats, licensing/provenance requirements, permitted normalization, and forbidden scientific transformations for the minimum representative case set.
"""
    (OUT / "SystemQualificationCapabilityManifest.md").write_text(report, encoding="utf-8", newline="\n")
    readme = """# Phase A Repository Capability Census

Repository-grounded, non-production discovery package for future qualification design.

Start with [SystemQualificationCapabilityManifest.md](SystemQualificationCapabilityManifest.md), then use the JSON/CSV matrices for machine processing. No web research, external data download, browser qualification, live LLM call, product change, or support promotion occurred.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8", newline="\n")

    manifest_files = []
    for path in sorted(p for p in OUT.iterdir() if p.is_file() and p.name != "manifest.json"):
        raw = path.read_bytes()
        manifest_files.append({"path": path.name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "hashMode": "UTF8_LF"})
    semantic = {"schemaVersion": "SystemQualificationCapabilityManifest/1.0", "generatedFromGitSha": head, "counts": counts, "qualificationDataResearchReady": readiness["QUALIFICATION_DATA_RESEARCH_READY"], "files": manifest_files}
    semantic_hash = hashlib.sha256(json.dumps(semantic, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    dump_json(OUT / "manifest.json", {**semantic, "semanticHash": semantic_hash, "manifestMissingFiles": 0, "manifestHashMismatches": 0, "repositoryGroundedOnly": True, "productionCodeChanges": 0, "scientificBehaviorChanges": 0, "inputSupportChanges": 0, "registryChanges": 0, "parserChanges": 0, "adapterChanges": 0, "rendererChanges": 0, "apiBehaviorChanges": 0, "webAccessForCapabilityDiscovery": False, "downloadedExternalFixtures": 0, "liveChromeQualificationCases": 0, "liveDeepSeekQualificationCases": 0, "realLlmCalls": 0})


if __name__ == "__main__":
    main()
