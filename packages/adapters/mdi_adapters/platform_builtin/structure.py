from __future__ import annotations

from dataclasses import dataclass
import json
import math
from typing import Any

from pymatgen.core import Lattice, Structure
from pymatgen.core.periodic_table import Element

from mdi_artifact_core import ArtifactPayload, content_hash, stable_json_dumps
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError

try:  # pragma: no cover - exercised through dependency-present path in CI.
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
except Exception:  # pragma: no cover
    SpacegroupAnalyzer = None  # type: ignore[assignment]


@dataclass(frozen=True)
class PreparedStructures:
    structures: dict[str, Structure]
    truncated: bool
    warnings: list[str]


@dataclass(frozen=True)
class StructureAdapterResult:
    payload: dict[str, Any]
    params: dict[str, Any]
    artifact_name: str
    title: str
    primary_artifact_type: ArtifactType
    extra_artifacts: tuple[ExtraJsonArtifact, ...] = ()


@dataclass(frozen=True)
class ExtraJsonArtifact:
    artifact_type: ArtifactType
    file_name: str
    payload: dict[str, Any]


class _BaseStructureAdapter(BaseToolAdapter):
    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedStructures:
        if not self._resolved_inputs:
            raise self._input_error("No structure input was provided.", "empty_structure")

        raw = self._resolved_inputs[0] if len(self._resolved_inputs) == 1 else self._resolved_inputs
        structures = self._coerce_structures(raw)
        if not structures:
            raise self._input_error("Structure collection is empty.", "empty_structure")

        max_structures = int(params.get("maxStructures") or context.resource_limits.get("maxStructures") or 8)
        limited = dict(list(structures.items())[:max_structures])
        truncated = len(structures) > len(limited)
        warnings = [f"Input contained {len(structures)} structures; truncated to {len(limited)}."] if truncated else []
        max_atoms = int(context.resource_limits.get("maxAtomsPerStructure") or 5000)
        for label, structure in limited.items():
            self._validate_structure(label, structure, max_atoms=max_atoms)
        return PreparedStructures(structures=limited, truncated=truncated, warnings=warnings)

    def _coerce_structures(self, raw: Any) -> dict[str, Structure]:
        if isinstance(raw, Structure):
            return {_structure_label(raw, "structure_1"): raw}
        if isinstance(raw, dict) and "structures" in raw:
            return self._coerce_structures(raw["structures"])
        if isinstance(raw, dict) and _looks_like_structure_dict(raw):
            structure = self._coerce_single_structure(raw)
            return {_structure_label(structure, "structure_1"): structure}
        if isinstance(raw, dict):
            return {str(key): self._coerce_single_structure(value) for key, value in raw.items()}
        if isinstance(raw, (list, tuple)):
            return {f"structure_{idx + 1}": self._coerce_single_structure(value) for idx, value in enumerate(raw)}
        return {"structure_1": self._coerce_single_structure(raw)}

    def _coerce_single_structure(self, value: Any) -> Structure:
        if isinstance(value, Structure):
            return value
        if isinstance(value, dict):
            try:
                return Structure.from_dict(value)
            except Exception:
                return _structure_from_normalized_dict(value, tool_id=self.tool_id)
        if isinstance(value, str):
            text = value.strip()
            if not text:
                raise self._input_error("Structure text is empty.", "empty_structure")
            if text.startswith("{"):
                try:
                    return self._coerce_single_structure(json.loads(text))
                except json.JSONDecodeError as exc:
                    raise self._input_error("Structure JSON text could not be parsed.", "structure_parse_failed") from exc
            for fmt in ("cif", "poscar"):
                try:
                    return Structure.from_str(text, fmt=fmt)
                except Exception:
                    continue
            raise self._input_error("Structure text is not supported as CIF or POSCAR.", "unsupported_structure_format")
        raise self._input_error(
            "Structure adapters accept pymatgen Structure objects, Structure dictionaries, or structure text.",
            "unsupported_structure_format",
            input_type=type(value).__name__,
        )

    def _validate_structure(self, label: str, structure: Structure, *, max_atoms: int) -> None:
        if len(structure) == 0:
            raise self._input_error("Structure has no sites.", "empty_structure", structure=label)
        if structure.lattice is None or structure.lattice.volume <= 0:
            raise self._input_error("Structure requires a valid periodic lattice.", "missing_lattice", structure=label)
        if len(structure) > max_atoms:
            raise ToolExecutionError(
                code="TOOL_RESOURCE_LIMIT",
                message="Structure exceeds maxAtomsPerStructure.",
                tool_id=self.tool_id,
                details={"structure": label, "atoms": len(structure), "maxAtomsPerStructure": max_atoms},
            )

    def _input_error(self, message: str, error_type: str, **details: Any) -> ToolExecutionError:
        return ToolExecutionError(
            code="TOOL_INPUT_INVALID",
            message=message,
            tool_id=self.tool_id,
            details={"errorType": error_type, **details},
        )

    def export(self, result: StructureAdapterResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        default_requested = {
            result.primary_artifact_type,
            *(item.artifact_type for item in result.extra_artifacts),
            ArtifactType.summary_md,
            ArtifactType.recipe_json,
        }
        requested = set(artifact_types) or default_requested
        payloads: list[ArtifactPayload] = []
        if result.primary_artifact_type in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=result.primary_artifact_type,
                    file_name=result.artifact_name,
                    content=stable_json_dumps(result.payload),
                    media_type="application/json",
                )
            )
        for extra in result.extra_artifacts:
            if extra.artifact_type in requested:
                payloads.append(
                    ArtifactPayload(
                        artifact_type=extra.artifact_type,
                        file_name=extra.file_name,
                        content=stable_json_dumps(extra.payload),
                        media_type="application/json",
                    )
                )
        if ArtifactType.summary_md in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.summary_md,
                    file_name="summary.md",
                    content=_summary_markdown(result.title, result.payload),
                    media_type="text/markdown",
                )
            )
        if ArtifactType.recipe_json in requested:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.recipe_json,
                    file_name="recipe.json",
                    content=stable_json_dumps(_recipe_payload(self, result, requested)),
                    media_type="application/json",
                )
            )
        return self.export_payloads(
            payloads,
            provenance={
                "adapter": self.tool_id,
                "structureCount": result.payload.get("structureCount", 1),
                "artifactType": result.payload.get("artifactType"),
            },
        )


class StructureSummaryAdapter(_BaseStructureAdapter):
    tool_id = "structure.summary"
    adapter_version = "0.1.0"

    def run(self, prepared: PreparedStructures, params: dict[str, Any]) -> StructureAdapterResult:
        include_sites = bool(params.get("includeSitesPreview", True))
        max_preview_sites = int(params.get("maxPreviewSites") or 20)
        payload = {
            "artifactType": self.tool_id,
            "structureCount": len(prepared.structures),
            "structures": [
                _structure_record(label, structure, include_sites=include_sites, max_preview_sites=max_preview_sites)
                for label, structure in sorted(prepared.structures.items())
            ],
            "warnings": prepared.warnings,
        }
        return StructureAdapterResult(
            payload=payload,
            params=params,
            artifact_name="structure_summary.json",
            title="Structure Summary",
            primary_artifact_type=ArtifactType.structure_json,
        )


class LatticeSummaryAdapter(_BaseStructureAdapter):
    tool_id = "structure.lattice_summary"
    adapter_version = "0.1.0"

    def run(self, prepared: PreparedStructures, params: dict[str, Any]) -> StructureAdapterResult:
        records = [
            {"structureId": label, **_lattice_payload(structure)}
            for label, structure in sorted(prepared.structures.items())
        ]
        payload = {
            "artifactType": self.tool_id,
            "structureCount": len(records),
            "latticeStats": {
                key: _stats([float(record[key]) for record in records])
                for key in ("a", "b", "c", "alpha", "beta", "gamma", "volume")
            },
            "structures": records,
            "outliers": _lattice_outliers(records) if bool(params.get("detectOutliers", True)) else [],
            "warnings": prepared.warnings,
        }
        return StructureAdapterResult(
            payload=payload,
            params=params,
            artifact_name="lattice_summary.json",
            title="Lattice Summary",
            primary_artifact_type=ArtifactType.table_json,
        )


class SpacegroupSummaryAdapter(_BaseStructureAdapter):
    tool_id = "structure.spacegroup_summary"
    adapter_version = "0.1.0"

    def run(self, prepared: PreparedStructures, params: dict[str, Any]) -> StructureAdapterResult:
        if SpacegroupAnalyzer is None:
            raise ToolExecutionError(
                code="TOOL_DEPENDENCY_MISSING",
                message="structure.spacegroup_summary requires pymatgen symmetry support / spglib.",
                tool_id=self.tool_id,
                details={"errorType": "symmetry_dependency_missing"},
            )

        symprec = float(params.get("symprec") or 0.01)
        angle_tolerance = float(params.get("angleTolerance") or 5)
        counts: dict[tuple[int, str, str], int] = {}
        crystal_counts: dict[str, int] = {}
        failed: list[dict[str, Any]] = []
        for label, structure in sorted(prepared.structures.items()):
            try:
                analyzer = SpacegroupAnalyzer(structure, symprec=symprec, angle_tolerance=angle_tolerance)
                number = int(analyzer.get_space_group_number())
                symbol = str(analyzer.get_space_group_symbol())
                crystal_system = str(analyzer.get_crystal_system())
            except Exception as exc:
                failed.append({"structureId": label, "errorType": "symmetry_detection_failed", "message": str(exc)})
                continue
            key = (number, symbol, crystal_system)
            counts[key] = counts.get(key, 0) + 1
            crystal_counts[crystal_system] = crystal_counts.get(crystal_system, 0) + 1

        if not counts:
            raise ToolExecutionError(
                code="TOOL_RUNTIME_ERROR",
                message="No space group could be detected for the provided structures.",
                tool_id=self.tool_id,
                details={"errorType": "symmetry_detection_failed", "failedStructures": failed},
            )

        warnings = list(prepared.warnings)
        if failed:
            warnings.append(f"Space group detection failed for {len(failed)} structure(s).")
        payload = {
            "artifactType": self.tool_id,
            "structureCount": len(prepared.structures),
            "symmetryEngine": "pymatgen/spglib",
            "symprec": symprec,
            "angleTolerance": angle_tolerance,
            "spacegroups": [
                {
                    "number": number,
                    "symbol": symbol,
                    "crystalSystem": crystal_system,
                    "count": count,
                }
                for (number, symbol, crystal_system), count in sorted(counts.items())
            ],
            "crystalSystemCounts": dict(sorted(crystal_counts.items())),
            "failedStructures": failed,
            "warnings": warnings,
        }
        return StructureAdapterResult(
            payload=payload,
            params=params,
            artifact_name="spacegroup_summary.json",
            title="Space Group Summary",
            primary_artifact_type=ArtifactType.table_json,
        )


class StructureCompositionAdapter(_BaseStructureAdapter):
    tool_id = "structure.composition_from_structure"
    adapter_version = "0.1.0"

    def run(self, prepared: PreparedStructures, params: dict[str, Any]) -> StructureAdapterResult:
        element_counts: dict[str, float] = {}
        chemical_systems: dict[str, int] = {}
        formulas: list[dict[str, Any]] = []
        for label, structure in sorted(prepared.structures.items()):
            record = _composition_record(label, structure)
            formulas.append(record)
            chemical_systems[record["chemicalSystem"]] = chemical_systems.get(record["chemicalSystem"], 0) + 1
            for element, amount in record["elementCounts"].items():
                element_counts[element] = element_counts.get(element, 0.0) + float(amount)
        payload = {
            "artifactType": self.tool_id,
            "structureCount": len(prepared.structures),
            "formulaCount": len(formulas),
            "formulas": formulas,
            "elementCounts": _stable_float_map(element_counts),
            "chemicalSystems": dict(sorted(chemical_systems.items())),
            "compositionAdapterCompatible": True,
            "recommendedNextTools": [
                "composition.elements_hist",
                "composition.ptable_heatmap",
                "composition.chem_sys_treemap",
            ]
            if bool(params.get("includeRecommendedTools", True))
            else [],
            "warnings": prepared.warnings,
        }
        return StructureAdapterResult(
            payload=payload,
            params=params,
            artifact_name="structure_composition.json",
            title="Structure Composition",
            primary_artifact_type=ArtifactType.table_json,
        )


class StructurePreviewMetadataAdapter(_BaseStructureAdapter):
    tool_id = "structure.preview_metadata"
    adapter_version = "0.1.0"

    def run(self, prepared: PreparedStructures, params: dict[str, Any]) -> StructureAdapterResult:
        label, structure = next(iter(sorted(prepared.structures.items())))
        max_preview_sites = int(params.get("maxPreviewSites") or 100)
        include_cartesian = bool(params.get("includeCartesian", True))
        include_fractional = bool(params.get("includeFractional", True))
        sites = _sites_preview(
            structure,
            max_sites=max_preview_sites,
            include_cartesian=include_cartesian,
            include_fractional=include_fractional,
        )
        warnings = list(prepared.warnings)
        truncated = len(structure) > len(sites)
        if truncated:
            warnings.append(f"Sites preview truncated to {len(sites)} of {len(structure)} sites.")
        payload = {
            "artifactType": self.tool_id,
            "structureId": label,
            "structureCount": len(prepared.structures),
            "formula": structure.composition.formula,
            "reducedFormula": structure.composition.reduced_formula,
            "numSites": len(structure),
            "elements": _elements(structure),
            "boundingBox": _bounding_box(structure),
            "latticeVectors": _round_nested(structure.lattice.matrix.tolist()),
            "sitesPreview": sites,
            "truncated": truncated,
            "maxPreviewSites": max_preview_sites,
            "warnings": warnings,
        }
        return StructureAdapterResult(
            payload=payload,
            params=params,
            artifact_name="structure_preview_metadata.json",
            title="Structure Preview Metadata",
            primary_artifact_type=ArtifactType.structure_json,
        )


class StructureViewerSceneMetadataAdapter(_BaseStructureAdapter):
    tool_id = "structure.viewer_scene_metadata"
    adapter_version = "0.1.0"

    def run(self, prepared: PreparedStructures, params: dict[str, Any]) -> StructureAdapterResult:
        normalized_params = _viewer_params(params, self.context.resource_limits)
        payload = _viewer_scene_payload(
            prepared,
            params=normalized_params,
            tool_id=self.tool_id,
            context=self.context,
        )
        return StructureAdapterResult(
            payload=payload,
            params=normalized_params,
            artifact_name="viewer_scene.json",
            title="Structure Viewer Scene Metadata",
            primary_artifact_type=ArtifactType.structure_json,
        )


class StructureViewerExportPackageAdapter(_BaseStructureAdapter):
    tool_id = "structure.viewer_export_package"
    adapter_version = "0.1.0"

    def run(self, prepared: PreparedStructures, params: dict[str, Any]) -> StructureAdapterResult:
        normalized_params = _viewer_params(params, self.context.resource_limits)
        scene_payload = _viewer_scene_payload(
            prepared,
            params=normalized_params,
            tool_id="structure.viewer_scene_metadata",
            context=self.context,
        )
        manifest_payload = _viewer_assets_manifest_payload(
            scene_payload,
            params=normalized_params,
            tool_id=self.tool_id,
        )
        return StructureAdapterResult(
            payload=scene_payload,
            params=normalized_params,
            artifact_name="viewer_scene.json",
            title="Structure Viewer Export Package",
            primary_artifact_type=ArtifactType.structure_json,
            extra_artifacts=(
                ExtraJsonArtifact(
                    artifact_type=ArtifactType.table_json,
                    file_name="viewer_assets_manifest.json",
                    payload=manifest_payload,
                ),
            ),
        )


def _looks_like_structure_dict(value: dict[str, Any]) -> bool:
    return ("@module" in value and "@class" in value) or ("lattice" in value and "sites" in value)


def _structure_from_normalized_dict(value: dict[str, Any], *, tool_id: str) -> Structure:
    try:
        lattice_payload = value["lattice"]
        if isinstance(lattice_payload, dict) and "matrix" in lattice_payload:
            lattice = Lattice(lattice_payload["matrix"])
        elif isinstance(lattice_payload, dict):
            lattice = Lattice.from_parameters(
                float(lattice_payload["a"]),
                float(lattice_payload["b"]),
                float(lattice_payload["c"]),
                float(lattice_payload["alpha"]),
                float(lattice_payload["beta"]),
                float(lattice_payload["gamma"]),
            )
        else:
            lattice = Lattice(lattice_payload)
        species: list[str] = []
        coords: list[list[float]] = []
        coords_are_cartesian = False
        for site in value["sites"]:
            species.append(str(site.get("element") or site.get("species") or site.get("label")))
            if "fracCoords" in site:
                coords.append([float(item) for item in site["fracCoords"]])
            elif "cartCoords" in site:
                coords.append([float(item) for item in site["cartCoords"]])
                coords_are_cartesian = True
            else:
                raise KeyError("fracCoords/cartCoords")
        if not species:
            raise ValueError("No structure sites were found.")
        return Structure(lattice, species, coords, coords_are_cartesian=coords_are_cartesian)
    except Exception as exc:
        raise ToolExecutionError(
            code="TOOL_INPUT_INVALID",
            message="Structure dictionary could not be parsed.",
            tool_id=tool_id,
            details={"errorType": "structure_parse_failed", "inputType": type(value).__name__},
        ) from exc


def _structure_label(structure: Structure, fallback: str) -> str:
    formula = structure.composition.reduced_formula
    return formula or fallback


def _structure_record(label: str, structure: Structure, *, include_sites: bool, max_preview_sites: int) -> dict[str, Any]:
    return {
        "structureId": label,
        "sourceFormat": "pymatgen.Structure",
        "formula": structure.composition.formula,
        "reducedFormula": structure.composition.reduced_formula,
        "elements": _elements(structure),
        "elementCounts": _stable_float_map(_element_counts(structure)),
        "numSites": len(structure),
        "numElements": len(_elements(structure)),
        "isPeriodic": bool(structure.lattice and structure.lattice.volume > 0),
        "lattice": _lattice_payload(structure),
        "siteProperties": sorted(structure.site_properties.keys()),
        "sitesPreview": _sites_preview(structure, max_sites=max_preview_sites) if include_sites else [],
        "warnings": [],
    }


def _composition_record(label: str, structure: Structure) -> dict[str, Any]:
    elements = _elements(structure)
    return {
        "structureId": label,
        "formula": structure.composition.formula,
        "reducedFormula": structure.composition.reduced_formula,
        "elements": elements,
        "elementCounts": _stable_float_map(_element_counts(structure)),
        "chemicalSystem": "-".join(elements),
        "numSites": len(structure),
    }


def _lattice_payload(structure: Structure) -> dict[str, Any]:
    lattice = structure.lattice
    return {
        "a": _round(lattice.a),
        "b": _round(lattice.b),
        "c": _round(lattice.c),
        "alpha": _round(lattice.alpha),
        "beta": _round(lattice.beta),
        "gamma": _round(lattice.gamma),
        "volume": _round(lattice.volume),
        "matrix": _round_nested(lattice.matrix.tolist()),
    }


def _sites_preview(
    structure: Structure,
    *,
    max_sites: int,
    include_cartesian: bool = True,
    include_fractional: bool = True,
) -> list[dict[str, Any]]:
    sites: list[dict[str, Any]] = []
    for index, site in enumerate(structure[:max_sites]):
        item: dict[str, Any] = {"index": index, "element": site.species_string}
        if include_fractional:
            item["fracCoords"] = _round_list(site.frac_coords.tolist())
        if include_cartesian:
            item["cartCoords"] = _round_list(site.coords.tolist())
        sites.append(item)
    return sites


def _bounding_box(structure: Structure) -> dict[str, list[float]]:
    coords = structure.cart_coords.tolist()
    if not coords:
        return {"x": [0.0, 0.0], "y": [0.0, 0.0], "z": [0.0, 0.0]}
    axes = list(zip(*coords))
    return {
        axis: [_round(min(values)), _round(max(values))]
        for axis, values in zip(("x", "y", "z"), axes, strict=True)
    }


def _elements(structure: Structure) -> list[str]:
    return sorted({element.symbol for element in structure.composition.elements})


def _element_counts(structure: Structure) -> dict[str, float]:
    return {str(element): float(amount) for element, amount in structure.composition.element_composition.items()}


def _stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {"min": 0.0, "mean": 0.0, "max": 0.0}
    return {
        "min": _round(min(values)),
        "mean": _round(sum(values) / len(values)),
        "max": _round(max(values)),
    }


def _lattice_outliers(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(records) < 4:
        return []
    outliers: list[dict[str, Any]] = []
    for key in ("a", "b", "c", "volume"):
        values = sorted(float(record[key]) for record in records)
        q1 = values[len(values) // 4]
        q3 = values[(len(values) * 3) // 4]
        iqr = q3 - q1
        if iqr <= 0:
            continue
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        for record in records:
            value = float(record[key])
            if value < low or value > high:
                outliers.append(
                    {"structureId": record["structureId"], "field": key, "value": _round(value), "low": _round(low), "high": _round(high)}
                )
    return outliers


def _summary_markdown(title: str, payload: dict[str, Any]) -> str:
    if str(payload.get("schema_version", "")).startswith("phase10d1.viewer_scene"):
        return _viewer_summary_markdown(title, payload)
    lines = [f"# {title}", ""]
    for key in (
        "artifactType",
        "structureCount",
        "formulaCount",
        "structureId",
        "formula",
        "reducedFormula",
        "numSites",
        "symmetryEngine",
    ):
        if key in payload:
            lines.append(f"- {key}: {payload[key]}")
    if "elements" in payload and isinstance(payload["elements"], list):
        lines.append(f"- elements: {', '.join(str(item) for item in payload['elements'])}")
    if "structures" in payload and payload["structures"]:
        labels = [str(item.get("structureId")) for item in payload["structures"][:8]]
        lines.append(f"- structures: {', '.join(labels)}")
    if "spacegroups" in payload and payload["spacegroups"]:
        labels = [f"{item['symbol']} ({item['number']})" for item in payload["spacegroups"][:8]]
        lines.append(f"- spacegroups: {', '.join(labels)}")
    if "recommendedNextTools" in payload and payload["recommendedNextTools"]:
        lines.append(f"- recommended next tools: {', '.join(payload['recommendedNextTools'])}")
    warnings = payload.get("warnings") or []
    lines.append(f"- warnings: {', '.join(str(item) for item in warnings) if warnings else 'none'}")
    return "\n".join(lines) + "\n"


def _stable_float_map(values: dict[str, float]) -> dict[str, float]:
    return {key: _round(float(value)) for key, value in sorted(values.items())}


def _round(value: float) -> float:
    if not math.isfinite(float(value)):
        return 0.0
    return round(float(value), 6)


def _round_list(values: list[Any]) -> list[float]:
    return [_round(float(value)) for value in values]


def _round_nested(values: list[list[Any]]) -> list[list[float]]:
    return [_round_list(list(row)) for row in values]


def _viewer_params(params: dict[str, Any], resource_limits: dict[str, int]) -> dict[str, Any]:
    return {
        "inferBonds": bool(_param(params, "inferBonds", "infer_bonds", True)),
        "bondTolerance": _round(float(_param(params, "bondTolerance", "bond_tolerance", 0.2))),
        "maxSites": int(_param(params, "maxSites", "max_sites", resource_limits.get("maxSites", 500))),
        "maxBonds": int(_param(params, "maxBonds", "max_bonds", resource_limits.get("maxBonds", 2000))),
        "includeCartCoords": bool(_param(params, "includeCartCoords", "include_cart_coords", True)),
        "includeFracCoords": bool(_param(params, "includeFracCoords", "include_frac_coords", True)),
        "stylePreset": str(_param(params, "stylePreset", "style_preset", "default")),
        "cameraPreset": str(_param(params, "cameraPreset", "camera_preset", "auto")),
        "includeScene": bool(_param(params, "includeScene", "include_scene", True)),
        "includeManifest": bool(_param(params, "includeManifest", "include_manifest", True)),
        "includeSummary": bool(_param(params, "includeSummary", "include_summary", True)),
        "includeRecipe": bool(_param(params, "includeRecipe", "include_recipe", True)),
        "maxPackageBytes": int(_param(params, "maxPackageBytes", "max_package_bytes", resource_limits.get("maxPackageBytes", 5_000_000))),
    }


def _param(params: dict[str, Any], camel: str, snake: str, default: Any) -> Any:
    if camel in params:
        return params[camel]
    if snake in params:
        return params[snake]
    return default


def _viewer_scene_payload(
    prepared: PreparedStructures,
    *,
    params: dict[str, Any],
    tool_id: str,
    context: ToolExecutionContext,
) -> dict[str, Any]:
    records = [
        _viewer_structure_record(label, structure, params=params)
        for label, structure in sorted(prepared.structures.items())
    ]
    warnings = list(prepared.warnings)
    for record in records:
        warnings.extend(record["warnings"])
    first = records[0]
    element_colors: dict[str, str] = {}
    element_radii: dict[str, float] = {}
    for record in records:
        for element in record["species"]:
            style = _element_style(element)
            element_colors[element] = style["color"]
            element_radii[element] = style["radius"]
    security = {
        "contains_javascript": False,
        "external_urls": [],
        "external_urls_allowed": False,
        "artifact_supplied_js_allowed": False,
    }
    return {
        "artifactType": "structure.viewer_scene_metadata",
        "schema_version": "phase10d1.viewer_scene.v1",
        "sceneContractVersion": "1.0",
        "tool_id": tool_id,
        "scene_type": "structure_viewer_scene",
        "created_by": "Material Data Intelligence",
        "source": {
            "resource_id": context.dataset_id,
            "resource_type": "normalized_object",
            "filename": "structures",
            "parser": "pymatgen.Structure",
            "parser_version": BaseToolAdapter.dependency_versions().get("pymatgenVersion", "unknown"),
            "dataset_id": context.dataset_id,
            "project_id": context.project_id,
        },
        "structureCount": len(records),
        "structures": records,
        "structure": first,
        "atoms": first["atoms"],
        "bonds": first["bonds"],
        "latticeVectors": first["lattice"]["matrix"],
        "boundingBox": first["boundingBox"],
        "display": _viewer_display(params),
        "camera": _viewer_camera(first),
        "style": {
            "element_colors": dict(sorted(element_colors.items())),
            "element_radii": {key: element_radii[key] for key in sorted(element_radii)},
        },
        "elementStyles": {
            key: {"color": element_colors[key], "radius": element_radii[key]}
            for key in sorted(element_colors)
        },
        "limits": _aggregate_viewer_limits(records, params),
        "resourceCaps": _aggregate_viewer_limits(records, params),
        "truncated": any(record["limits"]["truncated"] for record in records),
        "warnings": _dedupe(warnings),
        "security": security,
    }


def _viewer_structure_record(label: str, structure: Structure, *, params: dict[str, Any]) -> dict[str, Any]:
    warnings: list[str] = []
    max_sites = int(params["maxSites"])
    max_bonds = int(params["maxBonds"])
    atoms = _viewer_atoms(
        structure,
        max_sites=max_sites,
        include_cart_coords=bool(params["includeCartCoords"]),
        include_frac_coords=bool(params["includeFracCoords"]),
        warnings=warnings,
    )
    bonds, bond_count_before_truncation = _viewer_bonds(
        structure,
        atom_count=len(atoms),
        max_bonds=max_bonds,
        infer_bonds=bool(params["inferBonds"]),
        bond_tolerance=float(params["bondTolerance"]),
        warnings=warnings,
    )
    site_truncated = len(structure) > len(atoms)
    bond_truncated = bond_count_before_truncation > len(bonds)
    if site_truncated:
        warnings.append(f"SITES_TRUNCATED: retained {len(atoms)} of {len(structure)} sites.")
    if bond_truncated:
        warnings.append(f"BONDS_TRUNCATED: retained {len(bonds)} of {bond_count_before_truncation} inferred bonds.")
    lattice = _lattice_payload(structure)
    lattice["pbc"] = [bool(item) for item in getattr(structure, "pbc", (True, True, True))]
    lattice["units"] = "angstrom"
    return {
        "structureId": label,
        "formula": structure.composition.reduced_formula,
        "reducedFormula": structure.composition.reduced_formula,
        "site_count": len(structure),
        "siteCount": len(structure),
        "species": _elements(structure),
        "lattice": lattice,
        "atoms": atoms,
        "bonds": bonds,
        "boundingBox": _bounding_box(structure),
        "limits": {
            "max_sites": max_sites,
            "max_bonds": max_bonds,
            "site_count_before_truncation": len(structure),
            "bond_count_before_truncation": bond_count_before_truncation,
            "truncated": site_truncated or bond_truncated,
        },
        "warnings": _dedupe(warnings),
    }


def _viewer_atoms(
    structure: Structure,
    *,
    max_sites: int,
    include_cart_coords: bool,
    include_frac_coords: bool,
    warnings: list[str],
) -> list[dict[str, Any]]:
    atoms: list[dict[str, Any]] = []
    element_counts: dict[str, int] = {}
    for index, site in enumerate(structure[:max_sites]):
        element = _site_element(site)
        element_counts[element] = element_counts.get(element, 0) + 1
        style = _element_style(element)
        atom = {
            "index": index,
            "label": f"{element}{element_counts[element]}",
            "element": element,
            "species_string": site.species_string,
            "occupancy": _round(sum(float(amount) for amount in site.species.values())),
            "display_radius": style["radius"],
            "display_color": style["color"],
        }
        if include_frac_coords:
            atom["frac_coords"] = _round_list(site.frac_coords.tolist())
        if include_cart_coords:
            atom["cart_coords"] = _round_list(site.coords.tolist())
        if len(site.species) > 1:
            warnings.append("PARTIAL_OCCUPANCY_PRESENT: mixed species site encountered.")
        atoms.append(atom)
    return atoms


def _viewer_bonds(
    structure: Structure,
    *,
    atom_count: int,
    max_bonds: int,
    infer_bonds: bool,
    bond_tolerance: float,
    warnings: list[str],
) -> tuple[list[dict[str, Any]], int]:
    if not infer_bonds:
        warnings.append("BONDS_SKIPPED_NO_POLICY: bond inference disabled.")
        return [], 0
    candidates: list[dict[str, Any]] = []
    for i in range(atom_count):
        for j in range(i + 1, atom_count):
            element_i = _site_element(structure[i])
            element_j = _site_element(structure[j])
            threshold = _bond_threshold(element_i, element_j, bond_tolerance)
            distance = _round(float(structure.get_distance(i, j)))
            if distance <= threshold:
                candidates.append(
                    {
                        "from": i,
                        "to": j,
                        "distance": distance,
                        "bond_type": "inferred",
                        "policy": "covalent_radius_sum_with_tolerance",
                    }
                )
    candidates.sort(key=lambda item: (item["from"], item["to"], item["distance"]))
    if max_bonds <= 0:
        if candidates:
            warnings.append("BONDS_TRUNCATED: maxBonds is zero; inferred bonds were omitted.")
        return [], len(candidates)
    return candidates[:max_bonds], len(candidates)


def _site_element(site: Any) -> str:
    try:
        return str(site.specie.symbol)
    except Exception:
        try:
            elements = site.species.elements
            return str(elements[0].symbol) if elements else str(site.species_string)
        except Exception:
            return str(site.species_string)


def _bond_threshold(element_a: str, element_b: str, tolerance: float) -> float:
    return _round(_element_style(element_a)["radius"] + _element_style(element_b)["radius"] + tolerance)


def _element_style(element: str) -> dict[str, Any]:
    colors = {
        "H": "#ffffff",
        "C": "#444444",
        "N": "#3050f8",
        "O": "#ff0d0d",
        "F": "#90e050",
        "Na": "#ab5cf2",
        "Cl": "#1ff01f",
        "Si": "#f0c8a0",
        "Fe": "#e06633",
    }
    try:
        radius = Element(element).covalent_radius
        value = 1.0 if radius is None else float(radius)
    except Exception:
        value = 1.0
    return {"color": colors.get(element, "#888888"), "radius": _round(value)}


def _viewer_display(params: dict[str, Any]) -> dict[str, Any]:
    return {
        "show_unit_cell": True,
        "show_axes": True,
        "show_bonds": bool(params["inferBonds"]),
        "show_labels": False,
        "background": "transparent",
        "representation": "ball_and_stick",
        "style_preset": params["stylePreset"],
        "camera_preset": params["cameraPreset"],
    }


def _viewer_camera(structure_record: dict[str, Any]) -> dict[str, Any]:
    box = structure_record["boundingBox"]
    target = [
        _round((box[axis][0] + box[axis][1]) / 2)
        for axis in ("x", "y", "z")
    ]
    span = max((box[axis][1] - box[axis][0]) for axis in ("x", "y", "z"))
    distance = _round(max(span * 2.5, 1.0))
    return {
        "projection": "perspective",
        "target": target,
        "position": [_round(target[0] + distance), _round(target[1] + distance), _round(target[2] + distance)],
        "up": [0.0, 0.0, 1.0],
        "zoom": 1.0,
    }


def _aggregate_viewer_limits(records: list[dict[str, Any]], params: dict[str, Any]) -> dict[str, Any]:
    site_count = sum(int(record["limits"]["site_count_before_truncation"]) for record in records)
    bond_count = sum(int(record["limits"]["bond_count_before_truncation"]) for record in records)
    return {
        "max_sites": int(params["maxSites"]),
        "max_bonds": int(params["maxBonds"]),
        "site_count_before_truncation": site_count,
        "bond_count_before_truncation": bond_count,
        "truncated": any(bool(record["limits"]["truncated"]) for record in records),
    }


def _viewer_assets_manifest_payload(scene_payload: dict[str, Any], *, params: dict[str, Any], tool_id: str) -> dict[str, Any]:
    scene_json = stable_json_dumps(scene_payload)
    warnings = list(scene_payload.get("warnings") or [])
    warnings.append("VIEWER_RENDERER_NOT_INCLUDED: package contains static metadata only.")
    return {
        "artifactType": "structure.viewer_export_package",
        "schema_version": "phase10d1.viewer_assets_manifest.v1",
        "sceneContractVersion": scene_payload["sceneContractVersion"],
        "package_type": "structure_viewer_static_export",
        "tool_id": tool_id,
        "entry_artifact": "viewer_scene.json",
        "artifacts": [
            {
                "path": "viewer_scene.json",
                "kind": "scene",
                "media_type": "application/json",
                "required": True,
                "sha256": content_hash(scene_json),
                "size_bytes": len(scene_json.encode("utf-8")),
            },
            {"path": "summary.md", "kind": "summary", "media_type": "text/markdown", "required": True},
            {"path": "recipe.json", "kind": "recipe", "media_type": "application/json", "required": True},
        ],
        "renderer": {
            "included": False,
            "renderer_type": "none",
            "future_renderer_contract": "viewer_scene.json",
        },
        "security": {
            "contains_javascript": False,
            "external_urls": [],
            "external_urls_allowed": False,
            "artifact_supplied_js_allowed": False,
        },
        "limits": {
            "max_sites": int(params["maxSites"]),
            "max_bonds": int(params["maxBonds"]),
            "truncated": bool(scene_payload["limits"]["truncated"]),
        },
        "warnings": _dedupe(warnings),
    }


def _viewer_summary_markdown(title: str, payload: dict[str, Any]) -> str:
    manifest_note = "- viewer_assets_manifest.json: generated when using structure.viewer_export_package"
    lines = [
        f"# {title}",
        "",
        "## Input",
        f"- source: {payload['source']['resource_type']}",
        f"- parser: {payload['source']['parser']}",
        f"- formula: {payload['structure']['formula']}",
        f"- site count: {payload['structure']['site_count']}",
        "",
        "## Output",
        "- viewer_scene.json: static scene metadata",
        manifest_note,
        "",
        "## Display",
        f"- representation: {payload['display']['representation']}",
        f"- bonds: {payload['display']['show_bonds']}",
        f"- unit cell: {payload['display']['show_unit_cell']}",
        f"- camera preset: {payload['display']['camera_preset']}",
        "",
        "## Limits",
        f"- max sites: {payload['limits']['max_sites']}",
        f"- max bonds: {payload['limits']['max_bonds']}",
        f"- truncated: {payload['limits']['truncated']}",
        "",
        "## Warnings",
        f"- {', '.join(payload['warnings']) if payload['warnings'] else 'none'}",
        "",
        "## Security",
        "- no artifact JavaScript",
        "- no external URLs",
        "- no WebGL renderer included",
    ]
    return "\n".join(lines) + "\n"


def _recipe_payload(adapter: _BaseStructureAdapter, result: StructureAdapterResult, requested: set[ArtifactType]) -> dict[str, Any]:
    if str(result.payload.get("schema_version", "")).startswith("phase10d1.viewer_scene"):
        return _viewer_recipe_payload(adapter, result, requested)
    return adapter.recipe_payload(
        name=result.title,
        params=result.params,
        artifact_types=sorted(requested, key=lambda item: item.value),
    )


def _viewer_recipe_payload(adapter: _BaseStructureAdapter, result: StructureAdapterResult, requested: set[ArtifactType]) -> dict[str, Any]:
    context = adapter.context
    return {
        "schema_version": "phase10d1.recipe.v1",
        "schemaVersion": "0.1",
        "recipeId": f"recipe_{context.tool_call_id}",
        "name": result.title,
        "tool_id": adapter.tool_id,
        "toolId": adapter.tool_id,
        "inputs": {
            "dataset_id": context.dataset_id,
            "input_hashes": adapter._input_hashes,
        },
        "params": result.params,
        "steps": [
            "parse_structure",
            "normalize_lattice",
            "normalize_sites",
            "infer_or_skip_bonds",
            "build_display_metadata",
            "build_camera_metadata",
            "write_viewer_scene_json",
        ],
        "deterministic": True,
        "dependencies": {
            "new_dependencies_added": False,
            **BaseToolAdapter.dependency_versions(),
        },
        "artifactTypes": [artifact_type.value for artifact_type in sorted(requested, key=lambda item: item.value)],
        "artifacts": [
            result.artifact_name,
            *(extra.file_name for extra in result.extra_artifacts),
            "summary.md",
            "recipe.json",
        ],
    }


def _dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
