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


_REGISTRY: ToolRegistry | None = None


def _enum_values(enum_type: type[Any]) -> set[str]:
    return {item.value for item in enum_type}


def _title_from_tool_id(tool_id: str) -> str:
    return tool_id.replace(".", " ").replace("_", " ").title()


def _domain_from_tool_id(tool_id: str) -> ToolDomain:
    domain = tool_id.split(".", 1)[0]
    return ToolDomain(domain)


def _category_for(entry: dict[str, Any]) -> ToolCategory:
    artifact_types = set(entry.get("artifact_types", []))
    source = entry.get("implementation_source")
    if source == "platform_builtin" and not artifact_types.intersection({"plotly_json", "plotly_html"}):
        return ToolCategory.analysis
    return ToolCategory.visualization


def _cost_for(entry: dict[str, Any]) -> str:
    tool_id = entry["tool_id"]
    if tool_id.startswith(("structure.", "trajectory.", "phonon.")):
        return "medium"
    return "low"


def _timeouts_for(entry: dict[str, Any]) -> tuple[int, int]:
    if entry["tool_id"] == "structure.viewer_3d":
        return 90, 180
    if entry["tool_id"].startswith("structure."):
        return 60, 180
    return 30, 120


def _resource_limits_for(entry: dict[str, Any]) -> dict[str, int]:
    tool_id = entry["tool_id"]
    if tool_id.startswith("structure.") or tool_id.startswith("trajectory."):
        return {"maxStructures": 8, "maxAtomsPerStructure": 5000, "maxFrames": 200}
    if tool_id.startswith("ml."):
        return {"maxRows": 500000}
    if tool_id.startswith("table."):
        return {"maxRows": 500000}
    return {"maxRows": 100000, "maxStructures": 10000}


def _input_schema_for(entry: dict[str, Any]) -> ToolInputSchema:
    tool_id = entry["tool_id"]
    if tool_id == "composition.ptable_heatmap":
        options = [
            ToolInputOption(
                name="formula_column",
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
                    requiredObjectTypes=[MaterialObjectType.Composition, MaterialObjectType.Structure],
                    requiredFields=[{"role": "formula", "dtype": "string"}],
                    description="Use formulas, Composition objects, or structures with compositions.",
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
            periodicity="non_periodic_allowed",
            inputOptions=[
                ToolInputOption(
                    name="structure_or_atoms",
                    requiredObjectTypes=[MaterialObjectType.Structure, MaterialObjectType.Atoms],
                    description="Use a pymatgen Structure or ASE Atoms object for an interactive viewer.",
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
    return ToolInputSchema(inputOptions=[])


def _params_schema_for(entry: dict[str, Any]) -> dict[str, Any]:
    tool_id = entry["tool_id"]
    if tool_id == "composition.ptable_heatmap":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "countMode": {"enum": ["composition", "occurrence"]},
                "colorScale": {"type": "string"},
                "normalize": {"type": "boolean"},
                "title": {"type": "string"},
            },
        }
    if tool_id == "composition.elements_hist":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "countMode": {"enum": ["composition", "occurrence"]},
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
                "showCounts": {"anyOf": [{"type": "string"}, {"type": "boolean"}]},
                "maxCells": {"type": "integer", "minimum": 1},
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
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "selectedStructureId": {"type": "string"},
                "showCell": {"type": "boolean"},
                "showBonds": {"anyOf": [{"type": "boolean"}, {"enum": ["auto"]}]},
                "cameraPreset": {"type": "string"},
            },
        }
    if tool_id == "structure.coordination_hist":
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "cutoff": {"type": "number", "exclusiveMinimum": 0},
                "strategy": {"anyOf": [{"type": "number", "exclusiveMinimum": 0}, {"type": "string"}]},
                "splitMode": {"type": "string"},
                "barMode": {"type": "string"},
                "annotateBars": {"type": "boolean"},
                "maxStructures": {"type": "integer", "minimum": 1},
                "title": {"type": "string"},
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
