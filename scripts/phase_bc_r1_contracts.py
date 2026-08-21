"""Repository-grounded Phase B/C-R1 qualification contract policy.

This module is non-production audit authority.  It deliberately separates
per-scenario execution assertions from campaign coverage associations.
"""

from __future__ import annotations

from typing import Any


OLD_PACKAGE_NAME = "Phase_B_Closure_Phase_C_Contract_Normalized_PARAPHRASE_COVERAGE_FIXED.zip"
OLD_PACKAGE_SHA256 = "3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952"
NEW_PACKAGE_NAME = "Phase_BC_R1_Qualification_Authority_Reconciled.zip"
CASE_SCHEMA_VERSION = "QualificationCaseManifest/1.1"
ROOT_SCHEMA_VERSION = "PhaseBClosurePhaseCContractManifest/1.1"
PLAN_STEP_CAP = 4

PLATFORM_ARTIFACT_PRODUCERS = {
    "analysis_plan_json": "PLATFORM_VALIDATED_ANALYSIS_PLAN",
    "report_html": "PLATFORM_REPORT_FINALIZATION",
    "report_md": "PLATFORM_REPORT_FINALIZATION",
    "recipe_json": "PLATFORM_DECLARATIVE_RECIPE",
}

SEMANTIC_OBJECT_TYPES = {
    "materials_tabular_dataset": {"DataFrame"},
    "regression_result_table": {"DataFrame"},
    "uncertainty_result_table": {"DataFrame"},
    "classification_result_table": {"DataFrame"},
    "crystal_structure": {"Structure"},
    "atomic_structure": {"Atoms"},
    "experimental_xrd": {"DataFrame"},
    "trajectory": {"Trajectory"},
    "phonon_band": {"PhononBand"},
    "phonon_dos": {"PhononDos"},
    "volumetric_field": {"VolumetricData"},
    "electronic_band": {"ElectronicBand"},
    "electronic_dos": {"ElectronicDos"},
    "contained_supported_resources": {"DataFrame"},
}


def turn(turn_id: str, question: str, tools: list[str], plan_version: str = "0.1") -> dict[str, Any]:
    return {
        "turnId": turn_id,
        "question": question,
        "requiredExecutionTools": tools,
        "planVersionExpected": plan_version,
        "maxRequiredStepCount": len(tools),
    }


CASE_POLICIES: dict[str, dict[str, Any]] = {
    "Q-DATASET-001": {
        "required": ["dataset.composition_space", "dataset.materials_explorer"],
        "allowed": [],
        "turns": [
            turn("overview", "Explore this materials dataset and summarize its quality.", ["dataset.materials_explorer"]),
            turn("composition-map", "Map the composition space represented by this materials dataset.", ["dataset.composition_space"]),
        ],
        "outcome": "A quality-aware table overview and a composition-space map from the supplied table.",
        "reason": "The two requested user outcomes are independent and are qualified as two bounded turns.",
    },
    "Q-COMPOSITION-001": {
        "required": ["composition.chem_sys_sunburst", "composition.elements_hist", "composition.formula_statistics"],
        "allowed": ["composition.chem_sys_treemap", "composition.ptable_heatmap", "composition.summary"],
        "explicitForbidden": ["structure.composition_from_structure"],
        "turns": [
            turn("formula-summary", "Summarize the formulas in this materials table.", ["composition.formula_statistics"]),
            turn("element-distribution", "Show the element distribution in this materials table.", ["composition.elements_hist"]),
            turn("chemical-system-distribution", "Show the chemical-system distribution in this materials table.", ["composition.chem_sys_sunburst"]),
        ],
        "outcome": "Formula statistics plus element and chemical-system distributions from table formula semantics only.",
        "reason": "CSV provides DataFrame/formula semantics but no periodic Structure; three independent requested views are modeled as bounded turns.",
    },
    "Q-TABLE-001": {
        "required": ["table.numeric_summary", "viz.correlation", "viz.histogram", "viz.scatter"],
        "allowed": ["table.distribution_summary"],
        "turns": [
            turn("numeric-summary", "Summarize the numeric properties in this table.", ["table.numeric_summary"]),
            turn("distribution", "Show the distributions of the numeric properties.", ["viz.histogram"]),
            turn("correlation", "Show correlations among the numeric properties.", ["viz.correlation"]),
            turn("scatter", "Show a scatter plot for the selected numeric properties.", ["viz.scatter"]),
        ],
        "outcome": "Numeric summary, distributions, correlations, and an explicitly selected scatter view.",
        "reason": "Each requested view is independently selectable and no single Plan is inflated beyond minimal coverage semantics.",
    },
    "Q-ML-REG-001": {
        "required": ["ml.regression_evaluation"],
        "allowed": ["ml.basic_metrics", "ml.density_scatter", "ml.error_distribution", "ml.outlier_table"],
        "turns": [turn("regression-evaluation", "Evaluate these supplied predictions and explain the largest errors and limitations.", ["ml.regression_evaluation"])],
        "outcome": "Evaluation of source-supplied targets and predictions, including linked high-error samples and limitations.",
        "reason": "The product composite is the minimal user-level execution; lower-level views remain optional auxiliaries.",
    },
    "Q-ML-UNC-001": {
        "required": ["ml.uncertainty_evaluation"],
        "allowed": [],
        "turns": [turn("uncertainty-evaluation", "Assess whether the supplied uncertainties are informative for these predictions.", ["ml.uncertainty_evaluation"])],
        "outcome": "Diagnostics over source-supplied prediction and uncertainty columns without calibration authority.",
        "reason": "One composite Tool matches the complete user-visible outcome.",
    },
    "Q-ML-CLASS-001": {
        "required": ["ml.classification_evaluation"],
        "allowed": [],
        "turns": [turn("classification-evaluation", "Evaluate these supplied material-class predictions and summarize their limitations.", ["ml.classification_evaluation"])],
        "outcome": "Evaluation of source-supplied classes, predictions, and probabilities with explicit limitations.",
        "reason": "One composite Tool matches the complete user-visible outcome.",
    },
    "Q-STRUCTURE-001": {
        "required": ["structure.lattice_summary", "structure.spacegroup_summary", "structure.summary", "structure.viewer_3d"],
        "allowed": ["structure.preview_metadata", "structure.structure_3d", "structure.viewer_scene"],
        "turns": [
            turn("structure-summary", "Summarize this crystal structure.", ["structure.summary"]),
            turn("lattice", "Summarize the lattice of this crystal structure.", ["structure.lattice_summary"]),
            turn("symmetry", "Summarize the symmetry of this crystal structure.", ["structure.spacegroup_summary"]),
            turn("viewer", "Show this crystal structure in the supported periodic 3D viewer.", ["structure.viewer_3d"]),
        ],
        "outcome": "Structure, lattice, symmetry, and one canonical inert periodic 3D viewer result.",
        "reason": "The four independent requested surfaces are modeled as bounded turns; alternative viewers are optional, not cumulative PASS requirements.",
    },
    "Q-ATOMIC-VIEW-001": {
        "required": [],
        "allowed": [],
        "explicitForbidden": ["structure.structure_3d", "structure.viewer_3d", "structure.viewer_scene"],
        "turns": [],
        "caseType": "EXPECTED_REJECTION",
        "supportDisposition": "UNSUPPORTED",
        "analysisExecutionExpected": False,
        "outcome": "A typed pre-Plan disclosure that current registered 3D viewers require a periodic Structure and will not infer one from non-periodic XYZ.",
        "reason": "The asset parses as non-periodic Atoms while every current registered 3D structure viewer requires periodic Structure.",
    },
    "Q-COORD-001": {
        "required": ["structure.coordination_crystalnn", "structure.coordination_voronoinn", "structure.local_environment_polyhedra"],
        "allowed": ["structure.coordination_hist"],
        "turns": [
            turn("crystalnn", "Inspect CrystalNN coordination and its local-environment polyhedra.", ["structure.coordination_crystalnn", "structure.local_environment_polyhedra"], "0.2"),
            turn("voronoinn", "Inspect VoronoiNN coordination and its local-environment polyhedra.", ["structure.coordination_voronoinn", "structure.local_environment_polyhedra"], "0.2"),
        ],
        "outcome": "Separate exact CrystalNN and VoronoiNN coordination evidence, each bound to its own polyhedra result for comparison.",
        "reason": "Each local-environment consumer has one exact producer; the two algorithms are separate bounded turns.",
    },
    "Q-XRD-001": {
        "required": ["structure.experimental_xrd_comparison", "structure.xrd"],
        "allowed": [],
        "turns": [turn("xrd-comparison", "Compare the supplied experimental XRD peaks with the theoretical pattern for this structure.", ["structure.experimental_xrd_comparison", "structure.xrd"], "0.2")],
        "outcome": "A wavelength-compatible experimental/theoretical comparison without phase confirmation or refinement.",
        "reason": "The consumer is bound to the exact theoretical pattern and supplied experimental resource.",
    },
    "Q-STRUCTURE-RDF-001": {
        "required": ["structure.rdf"],
        "allowed": [],
        "turns": [turn("structure-rdf", "Show the radial distribution function for this structure.", ["structure.rdf"])],
        "outcome": "A structure RDF over the supplied periodic structure.",
        "reason": "One Tool exactly matches the requested result.",
    },
    "Q-TRAJECTORY-001": {
        "required": ["structure.trajectory_viewer", "trajectory.diffusion", "trajectory.msd", "trajectory.rdf"],
        "allowed": [],
        "canonicalQuestion": "Show this trajectory and its RDF and MSD, then estimate diffusion over the full supplied time range.",
        "paraphraseQuestion": "Please show this trajectory and its RDF and MSD, then estimate diffusion over the full supplied time range.",
        "turns": [
            turn("trajectory-view", "Show this trajectory in the supported trajectory viewer.", ["structure.trajectory_viewer"]),
            turn("trajectory-analytics", "Show its RDF and MSD and estimate diffusion over the full supplied time range.", ["trajectory.diffusion", "trajectory.msd", "trajectory.rdf"], "0.2"),
        ],
        "outcome": "Trajectory view plus RDF, MSD, and a diffusion estimate over the explicitly selected full supplied time range.",
        "reason": "The old wording required an unspecified fit window; the corrected prompt selects the repository-supported full-range option and separates the viewer from analytics.",
    },
    "Q-PHONON-001": {
        "required": ["phonon.band", "phonon.band_dos", "phonon.dos", "structure.brillouin_zone"],
        "allowed": [],
        "turns": [turn("phonon-and-bz", "Show the supplied phonon bands and DOS together with matching Brillouin-zone context.", ["phonon.band", "phonon.band_dos", "phonon.dos", "structure.brillouin_zone"], "0.2")],
        "outcome": "Typed band and DOS producers, their compatible combined view, and structure-derived reciprocal context.",
        "reason": "The four-step dependency-aware Plan is exactly at, not above, the released cap.",
    },
    "Q-VOLUME-001": {
        "required": ["structure.volumetric_data"],
        "allowed": [],
        "turns": [turn("volumetric-view", "Inspect this supplied volumetric grid and show its supported slice and volume views.", ["structure.volumetric_data"])],
        "outcome": "Persisted bounded volumetric bundle rendered through the current volume viewer contracts.",
        "reason": "One Tool owns the complete bounded volumetric artifact family.",
    },
    "Q-ELECTRONIC-001": {
        "required": ["electronic.band_structure", "electronic.dos"],
        "allowed": [],
        "turns": [turn("electronic-band-dos", "Inspect the supplied electronic band structure and DOS, including gap, spin, projection, and compatibility limitations.", ["electronic.band_structure", "electronic.dos"])],
        "outcome": "Band and DOS results from compatible source-supplied calculation identity, energy reference, and units.",
        "reason": "Both supplied resources are explicitly requested and independently selectable within the Plan cap.",
    },
    "Q-ARCHIVE-001": {
        "required": ["dataset.materials_explorer"],
        "allowed": [],
        "turns": [turn("archive-table", "Import this bounded ZIP archive and inspect the supported materials table it contains.", ["dataset.materials_explorer"])],
        "outcome": "Bounded ZIP dispatch to the contained supported table, with ZIP retained as container rather than scientific semantic kind.",
        "reason": "The question asks for table inspection, not composition-space analysis.",
    },
}


def all_primary_case_ids() -> list[str]:
    return list(CASE_POLICIES)
