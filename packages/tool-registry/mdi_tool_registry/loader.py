from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml

from mdi_schemas import (
    ArtifactType,
    DisplayTarget,
    ImplementationSource,
    MaterialObjectType,
    RegisteredTool,
    ToolCategory,
    ToolDomain,
    ToolInputOption,
    ToolInputSchema,
    ToolOutputSchema,
)


ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST_PATHS = (
    ROOT_DIR / "tool_registry" / "pymatviz_manifest.yaml",
    ROOT_DIR / "tool_registry" / "matterviz_manifest.yaml",
    ROOT_DIR / "tool_registry" / "platform_builtin_manifest.yaml",
)

ALLOWED_STAGES = {"mvp", "v1", "v2"}
ADAPTER_NAME_RE = re.compile(r"^[A-Z][A-Za-z0-9_]*Adapter$")


class ManifestValidationError(ValueError):
    """Raised when a Tool Registry manifest cannot be normalized safely."""


@dataclass(frozen=True)
class ToolRegistry:
    version: str
    tools: tuple[RegisteredTool, ...]

    def get_tool_by_id(self, tool_id: str) -> RegisteredTool:
        for tool in self.tools:
            if tool.toolId == tool_id:
                return tool
        raise KeyError(f"Unknown tool_id: {tool_id}")

    def list_tools(self) -> list[RegisteredTool]:
        return list(self.tools)

    def list_tools_by_stage(self, stage: str) -> list[RegisteredTool]:
        if stage not in ALLOWED_STAGES:
            raise ManifestValidationError(f"Invalid stage: {stage}")
        return [tool for tool in self.tools if tool.stage == stage]

    def list_tools_by_domain(self, domain: str) -> list[RegisteredTool]:
        ToolDomain(domain)
        return [tool for tool in self.tools if tool.domain.value == domain]

    def list_mvp_tools(self) -> list[RegisteredTool]:
        return self.list_tools_by_stage("mvp")

    def planner_snapshot(self) -> Any:
        from .planner_metadata import build_registry_snapshot

        return build_registry_snapshot(self)

    def list_planner_visible_tools(self) -> list[RegisteredTool]:
        from .planner_metadata import planner_visible_tools

        return planner_visible_tools(self)


_REGISTRY: ToolRegistry | None = None


def _enum_values(enum_type: type[Any]) -> set[str]:
    return {item.value for item in enum_type}


def _title_from_tool_id(tool_id: str) -> str:
    return tool_id.replace(".", " ").replace("_", " ").title()


def _domain_from_tool_id(tool_id: str) -> ToolDomain:
    domain = tool_id.split(".", 1)[0]
    return ToolDomain(domain)


def _category_for(entry: dict[str, Any]) -> ToolCategory:
    if entry["tool_id"] in {"structure.trajectory_import", "structure.volumetric_data"}:
        return ToolCategory.parser
    artifact_types = set(entry.get("artifact_types", []))
    source = entry.get("implementation_source")
    if source == "platform_builtin" and not artifact_types.intersection({"plotly_json", "plotly_html"}):
        return ToolCategory.analysis
    return ToolCategory.visualization


def _cost_for(entry: dict[str, Any]) -> str:
    tool_id = entry["tool_id"]
    if tool_id.startswith(("dataset.", "structure.", "trajectory.", "phonon.")):
        return "medium"
    return "low"


def _timeouts_for(entry: dict[str, Any]) -> tuple[int, int]:
    if entry["tool_id"] in {"structure.trajectory_import", "structure.trajectory_viewer", "structure.volumetric_data"}:
        return 120, 300
    if entry["tool_id"] in {"dataset.materials_explorer", "dataset.composition_space"} or entry["tool_id"] in {
        "ml.regression_evaluation",
        "ml.uncertainty_evaluation",
        "ml.classification_evaluation",
    }:
        return 120, 300
    if entry["tool_id"] == "structure.viewer_3d":
        return 90, 180
    if entry["tool_id"].startswith("structure."):
        return 60, 180
    return 30, 120


def _resource_limits_for(entry: dict[str, Any]) -> dict[str, int]:
    tool_id = entry["tool_id"]
    if tool_id == "dataset.composition_space":
        return {
            "maxRows": 100000,
            "maxAnalyzedSamples": 20000,
            "maxElements": 118,
            "maxClusters": 12,
            "maxPlotPoints": 10000,
            "maxOutlierRows": 200,
            "maxColorProperties": 16,
            "maxWarnings": 128,
            "maxArtifactBytes": 16000000,
        }
    if tool_id == "dataset.materials_explorer":
        return {
            "maxRows": 100000,
            "maxColumns": 512,
            "maxProperties": 64,
            "maxCategories": 256,
            "maxTableRows": 200,
            "maxHistogramBins": 100,
            "maxStructures": 256,
            "maxAtomsPerStructure": 5000,
            "maxWarnings": 128,
            "maxArtifactBytes": 8000000,
        }
    if tool_id in {
        "ml.regression_evaluation",
        "ml.uncertainty_evaluation",
        "ml.classification_evaluation",
    }:
        return {
            "maxRows": 100000,
            "maxModels": 16,
            "maxClasses": 64,
            "maxChemistryGroups": 256,
            "maxTableRows": 200,
            "maxPlotPoints": 10000,
            "maxCurvePoints": 5000,
            "maxUncertaintyBins": 50,
            "maxHistogramBins": 100,
            "maxArtifactBytes": 8000000,
        }
    if tool_id == "structure.volumetric_data":
        return {
            "maxSourceBytes": 268435456,
            "maxGridDimension": 512,
            "maxTotalVoxels": 16777216,
            "maxStoredValues": 50331648,
            "maxFieldsPerDataset": 8,
            "maxUncompressedBytesPerField": 268435456,
            "maxDatasetBytes": 536870912,
        }
    if tool_id == "structure.brillouin_zone":
        return {
            "maxStructures": 1,
            "maxAtomsPerStructure": 512,
            "maxVertices": 256,
            "maxEdges": 512,
            "maxFaces": 256,
            "maxVerticesPerFace": 64,
            "maxHighSymmetryPoints": 128,
            "maxAliasesPerPoint": 16,
            "maxPathVariants": 8,
            "maxPathSegments": 256,
            "maxDiscontinuities": 64,
            "maxWarnings": 32,
            "maxProviderMetadataBytes": 16384,
            "maxJsonBytes": 8000000,
            "maxGeneratorSearchRadius": 4,
            "maxCandidatePlanes": 728,
        }
    if tool_id == "phonon.band":
        return {
            "maxAtoms": 512,
            "maxBranches": 1536,
            "maxQpoints": 4096,
            "maxSegments": 256,
            "maxNumericValues": 4000000,
            "maxArtifactBytes": 64000000,
            "maxTableRows": 50000,
        }
    if tool_id == "phonon.dos":
        return {
            "maxAtoms": 512,
            "maxDosPoints": 100000,
            "maxProjectedDosSeries": 512,
            "maxNumericValues": 4000000,
            "maxArtifactBytes": 64000000,
            "maxTableRows": 50000,
        }
    if tool_id == "phonon.band_dos":
        return {
            "maxAtoms": 512,
            "maxBranches": 1536,
            "maxQpoints": 4096,
            "maxDosPoints": 100000,
            "maxProjectedDosSeries": 512,
            "maxVisibleProjections": 4,
            "maxCombinedPlotValues": 1000000,
            "maxPlotTraces": 4096,
            "maxArtifactBytes": 64000000,
            "maxTableRows": 500,
        }
    if tool_id == "phonon.animation":
        return {
            "maxAtoms": 512,
            "maxDisplayedAtoms": 768,
            "maxSupercellAxis": 3,
            "maxVectors": 768,
            "maxTrailPoints": 32,
            "maxArtifactBytes": 16000000,
            "maxPlaybackFps": 30,
        }
    if tool_id in {"structure.trajectory_import", "structure.trajectory_viewer"}:
        return {
            "maxAtoms": 4096,
            "maxFrames": 10000,
            "maxCoordinateValues": 12000000,
            "maxJsonBytes": 64000000,
            "maxDisplayedInstances": 768,
            "maxCacheFrames": 7,
            "maxCacheBytes": 16777216,
            "maxPendingFrameRequests": 1,
            "maxPlaybackFps": 30,
        }
    if tool_id in {"structure.viewer_scene", "structure.viewer_3d"}:
        return {
            "maxStructures": 1,
            "maxAtomsPerStructure": 256,
            "maxSites": 256,
            "maxBonds": 2048,
            "maxSpecies": 32,
            "maxSceneJsonBytes": 1_000_000,
        }
    if tool_id in {"structure.viewer_scene_metadata", "structure.viewer_export_package"}:
        return {
            "maxStructures": 8,
            "maxAtomsPerStructure": 5000,
            "maxSites": 5000,
            "maxBonds": 20000,
            "maxPackageBytes": 5_000_000,
        }
    if tool_id in {"structure.coordination_crystalnn", "structure.coordination_voronoinn"}:
        return {
            "maxStructures": 32,
            "maxAtomsPerStructure": 5000,
            "maxSites": 5000,
            "maxNeighborsPerSite": 1000,
            "maxRetainedRows": 50000,
            "maxArtifactBytes": 16777216,
        }
    if tool_id == "structure.coordination_hist":
        return {
            "maxStructures": 8,
            "maxAtomsPerStructure": 5000,
            "maxSites": 5000,
            "maxNeighborsPerSite": 1000,
        }
    if tool_id == "structure.xrd":
        return {
            "maxStructures": 8,
            "maxAtomsPerStructure": 5000,
            "maxPeaks": 5000,
        }
    if tool_id == "structure.rdf":
        return {
            "maxStructures": 8,
            "maxAtomsPerStructure": 5000,
            "maxSites": 5000,
            "maxBins": 5000,
            "maxNeighborsTotal": 2_000_000,
            "maxPartialPairs": 256,
        }
    if tool_id.startswith("structure.") or tool_id.startswith("trajectory."):
        return {"maxStructures": 8, "maxAtomsPerStructure": 5000, "maxFrames": 200}
    if tool_id.startswith("ml."):
        return {"maxRows": 500000}
    if tool_id.startswith("table."):
        return {"maxRows": 500000}
    if tool_id.startswith("viz."):
        return {"maxRows": 500000, "maxPoints": 50000}
    return {"maxRows": 100000, "maxStructures": 10000}


def _input_schema_for(entry: dict[str, Any]) -> ToolInputSchema:
    tool_id = entry["tool_id"]
    if tool_id == "dataset.composition_space":
        return ToolInputSchema(
            periodicity="any",
            inputOptions=[
                ToolInputOption(
                    name="profile_bound_composition_tables",
                    requiredObjectTypes=[MaterialObjectType.DataFrame],
                    requiredFields=[],
                    description=(
                        "Use exactly one Material Data Profile 2.0 ref and one or two explicitly identified "
                        "DataFrames with canonical material_formula semantics. Optional ML coloring requires an "
                        "explicit sample-bound Phase 10K-3 artifact."
                    ),
                )
            ],
        )
    if tool_id == "dataset.materials_explorer":
        return ToolInputSchema(
            periodicity="any",
            inputOptions=[
                ToolInputOption(
                    name="profile_bound_material_table",
                    requiredObjectTypes=[MaterialObjectType.DataFrame],
                    requiredFields=[],
                    description=(
                        "Use a Profile 2.0 ref plus its explicitly identified DataFrame and optional canonical "
                        "Structure resources. Comparison requires two named resources or one explicit group column."
                    ),
                ),
                ToolInputOption(
                    name="profile_bound_structure_collection",
                    requiredObjectTypes=[MaterialObjectType.Structure],
                    requiredFields=[],
                    description="Use a Profile 2.0 ref plus the matching bounded canonical Structure collection.",
                ),
            ],
        )
    if tool_id in {
        "ml.regression_evaluation",
        "ml.uncertainty_evaluation",
        "ml.classification_evaluation",
    }:
        return ToolInputSchema(
            periodicity="any",
            inputOptions=[
                ToolInputOption(
                    name="profile_bound_ml_result_table",
                    requiredObjectTypes=[MaterialObjectType.DataFrame],
                    requiredFields=[],
                    description=(
                        "Use exactly one Material Data Profile 2.0 ref and the explicitly bound immutable result "
                        "DataFrame. Target, prediction, uncertainty, probability, unit, and sample identities come "
                        "only from the Profile contract."
                    ),
                )
            ],
        )
    if tool_id == "structure.volumetric_data":
        return ToolInputSchema(
            periodicity="any",
            inputOptions=[ToolInputOption(
                name="single_bounded_volumetric_source",
                requiredObjectTypes=[MaterialObjectType.VolumetricData],
                requiredFields=[],
                description="Use exactly one parser-validated bounded VASP volumetric or single-dataset Gaussian CUBE object.",
            )],
        )
    if tool_id == "structure.brillouin_zone":
        return ToolInputSchema(
            inputOptions=[
                ToolInputOption(
                    name="single_periodic_structure",
                    requiredObjectTypes=[MaterialObjectType.Structure],
                    requiredFields=[],
                    description="Use exactly one ordered non-magnetic three-dimensional periodic Structure.",
                )
            ],
            periodicity="periodic_required",
        )
    if tool_id == "phonon.band":
        return ToolInputSchema(
            periodicity="periodic_required",
            inputOptions=[
                ToolInputOption(
                    name="approved_phonon_band",
                    requiredObjectTypes=[MaterialObjectType.PhononBand],
                    description="Use exactly one validated phase10h.phonon_band.v1 object or bounded phonopy band.yaml wrapper.",
                )
            ],
        )
    if tool_id == "phonon.dos":
        return ToolInputSchema(
            periodicity="periodic_required",
            inputOptions=[
                ToolInputOption(
                    name="approved_phonon_dos",
                    requiredObjectTypes=[MaterialObjectType.PhononDos],
                    description="Use exactly one validated phase10h.phonon_dos.v1 object or bounded phonopy DOS text wrapper with explicit structure and projection metadata.",
                )
            ],
        )
    if tool_id == "phonon.band_dos":
        return ToolInputSchema(
            periodicity="periodic_required",
            inputOptions=[
                ToolInputOption(
                    name="approved_phonon_band_and_dos_artifacts",
                    requiredObjectTypes=[MaterialObjectType.PhononBand, MaterialObjectType.PhononDos],
                    description="Use exactly two role-bound artifact references: one validated phase10h.phonon_band.v1 and one validated phase10h.phonon_dos.v1.",
                )
            ],
        )
    if tool_id == "phonon.animation":
        return ToolInputSchema(
            periodicity="periodic_required",
            inputOptions=[
                ToolInputOption(
                    name="approved_structure_band_and_eigenvectors",
                    requiredObjectTypes=[MaterialObjectType.Structure, MaterialObjectType.PhononBand, MaterialObjectType.PhononEigenvector],
                    description="Use exactly three role-bound inert inputs: canonical structure, validated phase10h band, and validated phase10h eigenvector set.",
                )
            ],
        )
    if tool_id in {"structure.trajectory_import", "structure.trajectory_viewer"}:
        return ToolInputSchema(
            periodicity="any",
            inputOptions=[
                ToolInputOption(
                    name="validated_trajectory",
                    requiredObjectTypes=[MaterialObjectType.Trajectory],
                    description="Use exactly one bounded normalized phase10g.trajectory.v1 object.",
                )
            ],
        )
    if tool_id == "composition.ptable_heatmap":
        options = [
            ToolInputOption(
                name="formula_column",
                requiredObjectTypes=[MaterialObjectType.DataFrame],
                requiredFields=[{"role": "formula", "dtype": "string"}],
                description="Use formulas from a table column.",
            ),
            ToolInputOption(
                name="composition_objects",
                requiredObjectTypes=[MaterialObjectType.Composition],
                description="Use normalized Composition objects.",
            ),
            ToolInputOption(
                name="element_value_map",
                requiredObjectTypes=[MaterialObjectType.ElementValueMap],
                description="Use an element-to-value mapping.",
            ),
        ]
        return ToolInputSchema(inputOptions=options)
    if tool_id.startswith("composition."):
        return ToolInputSchema(
            inputOptions=[
                ToolInputOption(
                    name="formula_or_composition_collection",
                    requiredObjectTypes=[MaterialObjectType.DataFrame, MaterialObjectType.Composition],
                    requiredFields=[{"role": "formula", "dtype": "string"}],
                    description="Use formulas from DataFrames or normalized Composition objects.",
                )
            ]
        )
    if tool_id == "structure.structure_3d":
        return ToolInputSchema(
            periodicity="periodic_required",
            inputOptions=[
                ToolInputOption(
                    name="periodic_structures",
                    requiredObjectTypes=[MaterialObjectType.Structure],
                    description="Use one or more periodic pymatgen Structure objects.",
                )
            ],
        )
    if tool_id == "structure.viewer_3d":
        return ToolInputSchema(
            periodicity="periodic_required",
            inputOptions=[
                ToolInputOption(
                    name="single_periodic_structure",
                    requiredObjectTypes=[MaterialObjectType.Structure],
                    description="Use exactly one periodic structure to generate a canonical inert viewer scene.",
                )
            ],
        )
    if tool_id.startswith("structure."):
        return ToolInputSchema(
            periodicity="periodic_required",
            inputOptions=[
                ToolInputOption(
                    name="periodic_structures",
                    requiredObjectTypes=[MaterialObjectType.Structure],
                    description="Use periodic structure objects.",
                )
            ],
        )
    if tool_id.startswith("ml."):
        return ToolInputSchema(
            inputOptions=[
                ToolInputOption(
                    name="ml_results_dataframe",
                    requiredObjectTypes=[MaterialObjectType.DataFrame],
                    requiredFields=[
                        {"role": "target", "dtype": "number"},
                        {"role": "prediction", "dtype": "number"},
                    ],
                    description="Use a DataFrame with target and prediction columns.",
                )
            ]
        )
    if tool_id.startswith("table."):
        return ToolInputSchema(
            inputOptions=[
                ToolInputOption(
                    name="table_dataframe",
                    requiredObjectTypes=[MaterialObjectType.DataFrame],
                    description="Use a DataFrame or table records for descriptive statistics.",
                )
            ]
        )
    if tool_id.startswith("viz."):
        return ToolInputSchema(
            inputOptions=[
                ToolInputOption(
                    name="table_dataframe",
                    requiredObjectTypes=[MaterialObjectType.DataFrame],
                    description="Use a DataFrame or table records for visualization artifacts.",
                )
            ]
        )
    return ToolInputSchema(inputOptions=[])


def _params_schema_for(entry: dict[str, Any]) -> dict[str, Any]:
    tool_id = entry["tool_id"]
    common_coordination_limits = {
        "max_structures": {"type": "integer", "minimum": 1, "maximum": 32, "default": 32},
        "max_sites": {"type": "integer", "minimum": 1, "maximum": 5000, "default": 5000},
        "max_neighbors_per_site": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 1000},
        "max_retained_rows": {"type": "integer", "minimum": 1, "maximum": 50000, "default": 50000},
    }
    if tool_id == "structure.coordination_crystalnn":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "weighted_cn": {"type": "boolean", "default": True},
                "distance_cutoff_low": {"type": "number", "minimum": 0.0, "maximum": 5.0, "default": 0.5},
                "distance_cutoff_high": {"type": "number", "minimum": 0.0, "maximum": 5.0, "default": 1.0},
                "x_diff_weight": {"type": "number", "minimum": 0.0, "maximum": 10.0, "default": 3.0},
                "porous_adjustment": {"type": "boolean", "default": True},
                "search_cutoff_angstrom": {"type": "number", "minimum": 1.0, "maximum": 20.0, "default": 7.0},
                **common_coordination_limits,
            },
        }
    if tool_id == "structure.coordination_voronoinn":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "tol": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.0},
                "cutoff_angstrom": {"type": "number", "minimum": 1.0, "maximum": 20.0, "default": 13.0},
                "allow_pathological": {"type": "boolean", "default": False},
                **common_coordination_limits,
            },
        }
    if tool_id == "dataset.composition_space":
        scalar = {"anyOf": [{"type": "string", "maxLength": 256}, {"type": "number"}, {"type": "boolean"}]}
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "tableObjectId": {"type": "string", "minLength": 1, "maxLength": 256},
                "comparisonMode": {"enum": ["none", "group", "resources"]},
                "groupColumn": {"type": "string", "minLength": 1, "maxLength": 256},
                "groupA": scalar,
                "groupB": scalar,
                "leftObjectId": {"type": "string", "minLength": 1, "maxLength": 256},
                "rightObjectId": {"type": "string", "minLength": 1, "maxLength": 256},
                "projectionDimensions": {"const": 2},
                "clusteringEnabled": {"type": "boolean"},
                "nClusters": {"type": "integer", "minimum": 2, "maximum": 12},
                "randomState": {"type": "integer", "minimum": 0, "maximum": 2147483647},
                "nInit": {"type": "integer", "minimum": 1, "maximum": 100},
                "maxIterations": {"type": "integer", "minimum": 1, "maximum": 1000},
                "tolerance": {"type": "number", "exclusiveMinimum": 0, "maximum": 1},
                "colorBy": {"type": "string", "minLength": 1, "maxLength": 256},
                "maxPlotPoints": {"type": "integer", "minimum": 10, "maximum": 10000},
                "maxOutlierRows": {"type": "integer", "minimum": 1, "maximum": 200},
            },
        }
    if tool_id == "dataset.materials_explorer":
        scalar = {"anyOf": [{"type": "string", "maxLength": 256}, {"type": "number"}, {"type": "boolean"}]}
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "tableObjectId": {"type": "string", "minLength": 1, "maxLength": 256},
                "comparisonMode": {"enum": ["none", "group", "resources"]},
                "groupColumn": {"type": "string", "minLength": 1, "maxLength": 256},
                "groupA": scalar,
                "groupB": scalar,
                "leftObjectId": {"type": "string", "minLength": 1, "maxLength": 256},
                "rightObjectId": {"type": "string", "minLength": 1, "maxLength": 256},
                "maxProperties": {"type": "integer", "minimum": 1, "maximum": 64},
                "maxCategories": {"type": "integer", "minimum": 1, "maximum": 256},
                "maxTableRows": {"type": "integer", "minimum": 1, "maximum": 200},
                "histogramBins": {"type": "integer", "minimum": 4, "maximum": 100},
                "maxStructures": {"type": "integer", "minimum": 1, "maximum": 256},
                "symprec": {"type": "number", "exclusiveMinimum": 0, "maximum": 1},
            },
        }
    if tool_id in {
        "ml.regression_evaluation",
        "ml.uncertainty_evaluation",
        "ml.classification_evaluation",
    }:
        properties: dict[str, Any] = {
            "groupIds": {
                "type": "array",
                "items": {"type": "string", "minLength": 1, "maxLength": 256},
                "maxItems": 32,
                "uniqueItems": True,
            },
            "maxTableRows": {"type": "integer", "minimum": 1, "maximum": 200},
            "maxPlotPoints": {"type": "integer", "minimum": 10, "maximum": 10000},
        }
        if tool_id == "ml.regression_evaluation":
            properties.update(
                {
                    "maxChemistryGroups": {"type": "integer", "minimum": 1, "maximum": 256},
                    "minGroupSize": {"type": "integer", "minimum": 1, "maximum": 1000},
                    "histogramBins": {"type": "integer", "minimum": 4, "maximum": 100},
                }
            )
        elif tool_id == "ml.uncertainty_evaluation":
            properties["uncertaintyBins"] = {"type": "integer", "minimum": 2, "maximum": 50}
        else:
            properties.update(
                {
                    "positiveClass": {
                        "anyOf": [
                            {"type": "string", "maxLength": 256},
                            {"type": "number"},
                            {"type": "boolean"},
                        ]
                    },
                    "maxCurvePoints": {"type": "integer", "minimum": 10, "maximum": 5000},
                }
            )
        return {"type": "object", "additionalProperties": False, "properties": properties}
    if tool_id == "structure.volumetric_data":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "format": {"enum": ["auto", "vasp_volumetric", "gaussian_cube"]},
                "quantity_hint": {"enum": ["auto", "electron_density", "charge_density", "spin_density", "magnetization_density", "electrostatic_potential", "electron_localization_function", "orbital_density", "wavefunction", "generic_scalar"]},
                "field_selection": {"enum": ["all_supported", "total_only", "spin_channels", "first_scalar"]},
                "stored_dtype": {"enum": ["source_or_float64", "float32", "float64"]},
                "compression": {"enum": ["contract_default", "raw_binary", "gzip_binary"]},
                "include_statistics": {"const": True},
                "include_histogram": {"const": False},
                "verify_integrals": {"const": True},
                "allow_partial_dataset": {"const": False},
            },
        }
    if tool_id == "structure.brillouin_zone":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "include_reciprocal_lattice": {"const": True},
                "include_brillouin_zone": {"const": True},
                "include_kpath": {"const": True},
                "standardization": {"const": "contract_default"},
                "kpath_provider": {"const": "contract_default"},
                "time_reversal": {"const": True},
                "symmetry_tolerance_angstrom": {
                    "type": "number",
                    "minimum": 0.0000001,
                    "maximum": 1.0,
                },
                "angle_tolerance_degrees": {
                    "type": "number",
                    "minimum": 0.1,
                    "maximum": 30.0,
                },
                "include_alternative_path_variants": {"const": False},
            },
        }
    if tool_id == "phonon.band":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "source_format": {"enum": ["auto", "phase10h.phonon_band.v1", "phonopy_band_yaml"]},
                "source_frequency_unit": {"enum": ["terahertz", "inverse_centimeter", "millielectronvolt"]},
                "max_table_rows": {"type": "integer", "minimum": 1, "maximum": 50000},
                "plot_kind": {"const": "line"},
            },
        }
    if tool_id == "phonon.dos":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "source_format": {"enum": ["auto", "phase10h.phonon_dos.v1", "phonopy_total_dos", "phonopy_projected_dos"]},
                "source_frequency_unit": {"enum": ["terahertz", "inverse_centimeter", "millielectronvolt"]},
                "source_normalization": {"enum": ["total_modes", "unit_area"]},
                "max_table_rows": {"type": "integer", "minimum": 1, "maximum": 50000},
                "max_plot_values": {"type": "integer", "minimum": 2, "maximum": 250000},
                "plot_kind": {"const": "line"},
            },
        }
    if tool_id == "phonon.band_dos":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "selected_projection_ids": {
                    "type": "array",
                    "maxItems": 4,
                    "uniqueItems": True,
                    "items": {"type": "string", "pattern": "^(atom:[0-9]{1,6}|species:[A-Z][a-z]?)$"},
                },
                "domain_policy": {"enum": ["union", "manual_view"]},
                "manual_frequency_min": {"type": "number", "minimum": -1000000000000, "maximum": 1000000000000},
                "manual_frequency_max": {"type": "number", "minimum": -1000000000000, "maximum": 1000000000000},
                "max_table_rows": {"type": "integer", "minimum": 1, "maximum": 500},
                "layout": {"const": "band_left_dos_right"},
            },
        }
    if tool_id == "phonon.animation":
        return {
            "type": "object",
            "additionalProperties": False,
            "required": ["mode_id"],
            "properties": {
                "mode_id": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "display_scale": {"type": "number", "minimum": 0.01, "maximum": 1.0},
                "initial_phase_radians": {"type": "number", "minimum": -1000000, "maximum": 1000000},
                "playback_cycles_per_second": {"type": "number", "minimum": 0.05, "maximum": 2.0},
                "autoplay": {"type": "boolean"},
                "loop": {"type": "boolean"},
                "supercell_mode": {"enum": ["auto", "manual"]},
                "supercell": {
                    "type": "array", "minItems": 3, "maxItems": 3,
                    "prefixItems": [
                        {"type": "integer", "minimum": 1, "maximum": 3},
                        {"type": "integer", "minimum": 1, "maximum": 3},
                        {"type": "integer", "minimum": 1, "maximum": 3},
                    ],
                },
                "show_vectors": {"type": "boolean"},
                "show_trails": {"type": "boolean"},
                "trail_length": {"type": "integer", "minimum": 1, "maximum": 32},
                "show_bonds": {"type": "boolean"},
                "show_unit_cell": {"type": "boolean"},
                "show_axes": {"type": "boolean"},
                "representation": {"const": "ball_and_stick"},
            },
        }
    if tool_id == "structure.trajectory_import":
        return {"type": "object", "additionalProperties": False, "properties": {}}
    if tool_id == "structure.trajectory_viewer":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "playbackSpeed": {"enum": [0.25, 0.5, 1, 2, 4]},
                "loop": {"type": "boolean"},
                "supercell": {
                    "type": "array",
                    "prefixItems": [
                        {"type": "integer", "minimum": 1, "maximum": 3},
                        {"type": "integer", "minimum": 1, "maximum": 3},
                        {"type": "integer", "minimum": 1, "maximum": 3},
                    ],
                    "minItems": 3,
                    "maxItems": 3,
                },
                "showCell": {"type": "boolean"},
                "clipping": {"type": "boolean"},
                "performanceMode": {"const": "auto"},
                "bondMode": {"const": "none"},
            },
        }
    composition_count_mode = {"enum": ["occurrence", "stoichiometric", "fractional", "composition"]}
    formula_column_props = {
        "formulaColumn": {"type": "string"},
        "compositionColumn": {"type": "string"},
    }
    if tool_id == "composition.formula_statistics":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                **formula_column_props,
                "maxExamples": {"type": "integer", "minimum": 1},
                "strict": {"type": "boolean"},
            },
        }
    if tool_id == "composition.ptable_heatmap":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                **formula_column_props,
                "countMode": composition_count_mode,
                "colorScale": {"type": "string"},
                "log": {"type": "boolean"},
                "normalize": {"type": "boolean"},
                "title": {"type": "string"},
            },
        }
    if tool_id == "composition.elements_hist":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                **formula_column_props,
                "countMode": composition_count_mode,
                "topN": {"type": "integer", "minimum": 1},
                "keepTop": {"type": "integer", "minimum": 1},
                "logY": {"type": "boolean"},
                "showValues": {"anyOf": [{"type": "string"}, {"type": "boolean"}]},
                "title": {"type": "string"},
            },
        }
    if tool_id == "composition.chem_sys_treemap":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                **formula_column_props,
                "groupMode": {"enum": ["chem_sys", "arity", "reduced_formula"]},
                "maxGroups": {"type": "integer", "minimum": 1},
                "showCounts": {"anyOf": [{"type": "string"}, {"type": "boolean"}]},
                "maxCells": {"type": "integer", "minimum": 1},
                "title": {"type": "string"},
            },
        }
    if tool_id == "composition.chem_sys_sunburst":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                **formula_column_props,
                "hierarchy": {
                    "type": "array",
                    "items": {"enum": ["arity", "chem_sys", "reduced_formula"]},
                    "minItems": 1,
                },
                "maxLeafNodes": {"type": "integer", "minimum": 1},
                "title": {"type": "string"},
            },
        }
    if tool_id == "structure.structure_3d":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "colorBy": {"enum": ["element"]},
                "showCell": {"type": "boolean"},
                "showBonds": {"anyOf": [{"type": "boolean"}, {"enum": ["auto"]}]},
                "selectedStructureIds": {"type": "array", "items": {"type": "string"}},
                "maxStructures": {"type": "integer", "minimum": 1},
            },
        }
    if tool_id == "structure.viewer_3d":
        return _viewer_scene_v1_params_schema()
    if tool_id == "structure.viewer_scene_metadata":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": _viewer_scene_params_schema(),
        }
    if tool_id == "structure.viewer_scene":
        return _viewer_scene_v1_params_schema()
    if tool_id == "structure.viewer_export_package":
        properties = {
            **_viewer_scene_params_schema(),
            "includeScene": {"type": "boolean"},
            "include_scene": {"type": "boolean"},
            "includeManifest": {"type": "boolean"},
            "include_manifest": {"type": "boolean"},
            "includeSummary": {"type": "boolean"},
            "include_summary": {"type": "boolean"},
            "includeRecipe": {"type": "boolean"},
            "include_recipe": {"type": "boolean"},
            "maxPackageBytes": {"type": "integer", "minimum": 1, "maximum": 50_000_000},
            "max_package_bytes": {"type": "integer", "minimum": 1, "maximum": 50_000_000},
        }
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": properties,
        }
    if tool_id == "structure.coordination_hist":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "neighbor_policy": {"enum": ["distance_cutoff"]},
                "cutoff_angstrom": {"type": "number", "minimum": 0.1, "maximum": 10.0},
                "max_sites": {"type": "integer", "minimum": 1, "maximum": 5000},
                "max_neighbors_per_site": {"type": "integer", "minimum": 0, "maximum": 1000},
                "include_site_details": {"type": "boolean"},
                "group_by_element": {"type": "boolean"},
                "include_pair_counts": {"type": "boolean"},
                "plot_kind": {"enum": ["bar"]},
            },
        }
    if tool_id == "structure.xrd":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "radiation": {"enum": ["CuKa"]},
                "two_theta_min": {"type": "number", "minimum": 0.0, "maximum": 180.0},
                "two_theta_max": {"type": "number", "minimum": 1.0, "maximum": 180.0},
                "intensity_threshold": {"type": "number", "minimum": 0.0, "maximum": 100.0},
                "peak_merge_tolerance": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "max_peaks": {"type": "integer", "minimum": 1, "maximum": 5000},
                "include_hkl": {"type": "boolean"},
                "plot_kind": {"enum": ["stem"]},
            },
        }
    if tool_id == "structure.rdf":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "r_max_angstrom": {"type": "number", "minimum": 0.5, "maximum": 30.0},
                "bin_width_angstrom": {"type": "number", "minimum": 0.01, "maximum": 1.0},
                "normalization": {"enum": ["number_density"]},
                "include_partial_pairs": {"type": "boolean"},
                "max_partial_pairs": {"type": "integer", "minimum": 1, "maximum": 256},
                "max_sites": {"type": "integer", "minimum": 1, "maximum": 5000},
                "max_bins": {"type": "integer", "minimum": 1, "maximum": 5000},
                "max_neighbors_total": {"type": "integer", "minimum": 1, "maximum": 2000000},
                "plot_kind": {"enum": ["line"]},
            },
        }
    if tool_id == "structure.summary":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "structureColumn": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                "maxStructures": {"type": "integer", "minimum": 1},
                "includeSitesPreview": {"type": "boolean"},
                "maxPreviewSites": {"type": "integer", "minimum": 1},
            },
        }
    if tool_id == "structure.lattice_summary":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "structureColumn": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                "maxStructures": {"type": "integer", "minimum": 1},
                "detectOutliers": {"type": "boolean"},
            },
        }
    if tool_id == "structure.spacegroup_summary":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "structureColumn": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                "symprec": {"type": "number", "exclusiveMinimum": 0},
                "angleTolerance": {"type": "number"},
                "maxStructures": {"type": "integer", "minimum": 1},
            },
        }
    if tool_id == "structure.composition_from_structure":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "structureColumn": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                "maxStructures": {"type": "integer", "minimum": 1},
                "includeRecommendedTools": {"type": "boolean"},
            },
        }
    if tool_id == "structure.preview_metadata":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "structureColumn": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                "maxPreviewSites": {"type": "integer", "minimum": 1},
                "includeCartesian": {"type": "boolean"},
                "includeFractional": {"type": "boolean"},
            },
        }
    if tool_id == "ml.density_scatter":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "targetColumn": {"type": "string"},
                "predictionColumn": {"type": "string"},
                "nBins": {"anyOf": [{"type": "integer", "minimum": 1}, {"type": "boolean"}]},
                "density": {"anyOf": [{"type": "string"}, {"type": "boolean"}, {"type": "null"}]},
                "xLabel": {"type": "string"},
                "yLabel": {"type": "string"},
                "identityLine": {"type": "boolean"},
                "bestFitLine": {"type": "boolean"},
                "stats": {"anyOf": [{"type": "boolean"}, {"type": "object"}]},
                "title": {"type": "string"},
            },
        }
    if tool_id == "ml.error_distribution":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "targetColumn": {"type": "string"},
                "predictionColumn": {"type": "string"},
                "nBins": {"type": "integer", "minimum": 1},
                "topK": {"type": "integer", "minimum": 1},
                "title": {"type": "string"},
            },
        }
    if tool_id == "ml.basic_metrics":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "targetColumn": {"type": "string"},
                "predictionColumn": {"type": "string"},
            },
        }
    if tool_id == "table.numeric_summary":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "numericColumns": {"type": "array", "items": {"type": "string"}},
                "categoricalColumns": {"type": "array", "items": {"type": "string"}},
                "maxCategories": {"type": "integer", "minimum": 1},
            },
        }
    if tool_id == "table.distribution_summary":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "numericColumns": {"type": "array", "items": {"type": "string"}},
                "categoricalColumns": {"type": "array", "items": {"type": "string"}},
                "quantiles": {
                    "type": "array",
                    "items": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "maxCategories": {"type": "integer", "minimum": 1},
            },
        }
    if tool_id == "viz.scatter":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "xColumn": {"type": "string"},
                "yColumn": {"type": "string"},
                "colorColumn": {"type": "string"},
                "hoverColumns": {"type": "array", "items": {"type": "string"}},
                "title": {"type": "string"},
            },
        }
    if tool_id == "viz.histogram":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "column": {"type": "string"},
                "bins": {"type": "integer", "minimum": 1},
                "groupBy": {"type": "string"},
                "title": {"type": "string"},
            },
        }
    if tool_id == "viz.correlation":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "numericColumns": {"type": "array", "items": {"type": "string"}},
                "method": {"enum": ["pearson", "spearman"]},
                "minNonNullCount": {"type": "integer", "minimum": 1},
                "title": {"type": "string"},
            },
        }
    if tool_id == "composition.summary":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "formulaColumn": {"type": "string"},
                "compositionColumn": {"type": "string"},
                "maxSystems": {"type": "integer", "minimum": 1},
            },
        }
    if tool_id == "ml.outlier_table":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "targetColumn": {"type": "string"},
                "predictionColumn": {"type": "string"},
                "topK": {"type": "integer", "minimum": 1},
            },
        }
    return {"type": "object", "additionalProperties": True, "properties": {}}


def _viewer_scene_v1_params_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "include_bonds": {"type": "boolean"},
            "bond_cutoff_angstrom": {"type": "number", "minimum": 0.1, "maximum": 10.0},
            "max_sites": {"type": "integer", "minimum": 1, "maximum": 256},
            "max_bonds": {"type": "integer", "minimum": 0, "maximum": 2048},
            "coordinate_basis": {"enum": ["cartesian_angstrom"]},
            "include_cartesian_positions": {"enum": [True]},
            "include_fractional_positions": {"type": "boolean"},
            "cell_expansion": {
                "type": "array",
                "prefixItems": [{"const": 1}, {"const": 1}, {"const": 1}],
                "minItems": 3,
                "maxItems": 3,
            },
            "style_preset": {"enum": ["default"]},
            "camera_preset": {"enum": ["auto"]},
        },
    }


def _viewer_scene_params_schema() -> dict[str, Any]:
    return {
        "inferBonds": {"type": "boolean"},
        "infer_bonds": {"type": "boolean"},
        "bondTolerance": {"type": "number", "minimum": 0, "maximum": 1},
        "bond_tolerance": {"type": "number", "minimum": 0, "maximum": 1},
        "maxSites": {"type": "integer", "minimum": 1, "maximum": 5000},
        "max_sites": {"type": "integer", "minimum": 1, "maximum": 5000},
        "maxBonds": {"type": "integer", "minimum": 0, "maximum": 20000},
        "max_bonds": {"type": "integer", "minimum": 0, "maximum": 20000},
        "includeCartCoords": {"type": "boolean"},
        "include_cart_coords": {"type": "boolean"},
        "includeFracCoords": {"type": "boolean"},
        "include_frac_coords": {"type": "boolean"},
        "stylePreset": {"enum": ["default"]},
        "style_preset": {"enum": ["default"]},
        "cameraPreset": {"enum": ["auto"]},
        "camera_preset": {"enum": ["auto"]},
    }


def _source_for(entry: dict[str, Any], manifest_path: Path) -> dict[str, Any]:
    source = {
        "manifest": manifest_path.name,
        "package": entry.get("source_package"),
    }
    for key in ("source_function", "source_class", "source_alternatives", "notes"):
        if key in entry:
            source[key] = entry[key]
    return {key: value for key, value in source.items() if value is not None}


def _normalize_entry(entry: dict[str, Any], manifest_path: Path) -> RegisteredTool:
    artifact_types = [ArtifactType(item) for item in entry["artifact_types"]]
    default_timeout, max_timeout = _timeouts_for(entry)
    return RegisteredTool(
        toolId=entry["tool_id"],
        name=_title_from_tool_id(entry["tool_id"]),
        category=_category_for(entry),
        domain=_domain_from_tool_id(entry["tool_id"]),
        implementationSource=ImplementationSource(entry["implementation_source"]),
        description=entry.get("notes") or _title_from_tool_id(entry["tool_id"]),
        version="0.1.0",
        adapter=entry["adapter"],
        inputSchema=_input_schema_for(entry),
        paramsSchema=_params_schema_for(entry),
        outputSchema=ToolOutputSchema(
            primaryArtifactType=artifact_types[0],
            secondaryArtifactTypes=artifact_types[1:],
            displayTarget=DisplayTarget(entry["display_target"]),
        ),
        artifactTypes=artifact_types,
        costLevel=_cost_for(entry),
        defaultTimeoutSec=default_timeout,
        maxTimeoutSec=max_timeout,
        cachePolicy="reuse",
        permissions=["tool.execute"],
        resourceLimits=_resource_limits_for(entry),
        source=_source_for(entry, manifest_path),
        stage=entry["stage"],
    )


def validate_manifest(raw_manifest: dict[str, Any], source: str | Path = "<memory>") -> list[dict[str, Any]]:
    if not isinstance(raw_manifest, dict):
        raise ManifestValidationError(f"{source}: manifest must be a mapping")
    tools = raw_manifest.get("tools")
    if not isinstance(tools, list):
        raise ManifestValidationError(f"{source}: manifest must contain a tools list")

    seen: set[str] = set()
    adapter_errors: list[str] = []
    for idx, entry in enumerate(tools):
        where = f"{source}: tools[{idx}]"
        if not isinstance(entry, dict):
            raise ManifestValidationError(f"{where}: tool entry must be a mapping")
        for required in ("tool_id", "implementation_source", "stage", "adapter", "display_target", "artifact_types"):
            if required not in entry:
                raise ManifestValidationError(f"{where}: missing required field {required}")
        tool_id = entry["tool_id"]
        if tool_id in seen:
            raise ManifestValidationError(f"{where}: duplicate tool_id {tool_id}")
        seen.add(tool_id)
        if entry["stage"] not in ALLOWED_STAGES:
            raise ManifestValidationError(f"{where}: invalid stage {entry['stage']}")
        if entry["implementation_source"] not in _enum_values(ImplementationSource):
            raise ManifestValidationError(f"{where}: invalid implementation_source {entry['implementation_source']}")
        if entry["display_target"] not in _enum_values(DisplayTarget):
            raise ManifestValidationError(f"{where}: invalid display_target {entry['display_target']}")
        if not entry["artifact_types"]:
            raise ManifestValidationError(f"{where}: artifact_types cannot be empty")
        invalid_artifacts = [item for item in entry["artifact_types"] if item not in _enum_values(ArtifactType)]
        if invalid_artifacts:
            raise ManifestValidationError(f"{where}: invalid artifact_types {invalid_artifacts}")
        if not ADAPTER_NAME_RE.match(entry["adapter"]):
            adapter_errors.append(f"{where}: adapter {entry['adapter']} is not a registerable adapter class name")
    if adapter_errors:
        raise ManifestValidationError("; ".join(adapter_errors))
    return tools


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if data is None:
        raise ManifestValidationError(f"{path}: empty manifest")
    return data


def load_manifests(paths: Iterable[str | Path] | None = None) -> ToolRegistry:
    manifest_paths = tuple(Path(path) for path in (paths or DEFAULT_MANIFEST_PATHS))
    all_tools: list[RegisteredTool] = []
    seen_tool_ids: set[str] = set()

    for path in manifest_paths:
        raw_manifest = _load_yaml(path)
        for entry in validate_manifest(raw_manifest, path):
            tool_id = entry["tool_id"]
            if tool_id in seen_tool_ids:
                raise ManifestValidationError(f"Duplicate tool_id across manifests: {tool_id}")
            seen_tool_ids.add(tool_id)
            all_tools.append(_normalize_entry(entry, path))

    return ToolRegistry(version="0.1.0", tools=tuple(all_tools))


def _default_registry() -> ToolRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = load_manifests()
    return _REGISTRY


def get_tool_by_id(tool_id: str) -> RegisteredTool:
    return _default_registry().get_tool_by_id(tool_id)


def list_tools() -> list[RegisteredTool]:
    return _default_registry().list_tools()


def list_tools_by_stage(stage: str) -> list[RegisteredTool]:
    return _default_registry().list_tools_by_stage(stage)


def list_tools_by_domain(domain: str) -> list[RegisteredTool]:
    return _default_registry().list_tools_by_domain(domain)


def list_mvp_tools() -> list[RegisteredTool]:
    return _default_registry().list_mvp_tools()


loadManifests = load_manifests
validateManifest = validate_manifest
getToolById = get_tool_by_id
listTools = list_tools
listToolsByStage = list_tools_by_stage
listToolsByDomain = list_tools_by_domain
listMvpTools = list_mvp_tools
