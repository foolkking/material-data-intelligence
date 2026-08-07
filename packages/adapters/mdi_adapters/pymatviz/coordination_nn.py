from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any
import warnings as python_warnings

from pymatgen.core import Structure
from pymatgen.core.local_env import CrystalNN, VoronoiNN

from mdi_artifact_core import ArtifactPayload, content_hash, stable_json_dumps
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext, hashable_material
from ..errors import ToolExecutionError
from ..platform_builtin.structure import PreparedStructures, _BaseStructureAdapter


PYMATGEN_VERSION = "2026.5.4"
PYMATGEN_CORE_VERSION = "2026.5.18"
MAX_ARTIFACT_BYTES = 16 * 1024 * 1024


@dataclass(frozen=True)
class PreparedCoordination:
    structures: dict[str, Structure]
    source_ref: str
    source_hash: str
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class CoordinationResult:
    payload: dict[str, Any]
    summary: str
    recipe: dict[str, Any]


class _CoordinationNNAdapter(_BaseStructureAdapter):
    algorithm_id: str
    artifact_schema: str
    output_name: str
    coordination_semantics: str

    def prepare(
        self,
        context: ToolExecutionContext,
        input_refs: list[Any],
        params: dict[str, Any],
    ) -> PreparedCoordination:
        normalized = self.normalize_params(params)
        prepared: PreparedStructures = super().prepare(
            context,
            input_refs,
            {**params, "maxStructures": normalized["max_structures"]},
        )
        source_ref = _input_ref(input_refs[0]) if input_refs else ""
        if not source_ref:
            raise _error(self.tool_id, "TOOL_INPUT_INVALID", "SITE_IDENTITY_INVALID", "Structure input requires an exact resource ref.")
        for label, structure in prepared.structures.items():
            _validate_n1_structure(self.tool_id, label, structure, normalized["max_sites"])
        source_hash = self._input_hashes[0] if self._input_hashes else content_hash(stable_json_dumps(source_ref))
        return PreparedCoordination(prepared.structures, source_ref, source_hash, tuple(prepared.warnings))

    def run(self, prepared: PreparedCoordination, params: dict[str, Any]) -> CoordinationResult:
        normalized = self.normalize_params(params)
        parameter_hash = content_hash(stable_json_dumps(normalized))
        site_results: list[dict[str, Any]] = []
        unsupported_sites: list[dict[str, Any]] = []
        result_warnings = list(prepared.warnings)
        total_sites = sum(len(structure) for structure in prepared.structures.values())
        retained_rows = 0
        structure_records: list[dict[str, Any]] = []

        for label, structure in sorted(prepared.structures.items()):
            structure_hash = content_hash(stable_json_dumps(hashable_material(structure)))
            structure_records.append(
                {
                    "structureId": label,
                    "structureHash": structure_hash,
                    "formula": structure.composition.reduced_formula,
                    "siteCount": len(structure),
                    "sourceResourceId": prepared.source_ref,
                    "sourceResourceHash": prepared.source_hash,
                }
            )
            algorithm = self.create_algorithm(normalized)
            for site_index in range(len(structure)):
                try:
                    with python_warnings.catch_warnings(record=True) as caught:
                        python_warnings.simplefilter("always")
                        raw_neighbors = algorithm.get_nn_info(structure, site_index)
                    for warning in caught:
                        result_warnings.append(_library_warning_code(self.algorithm_id, str(warning.message)))
                    if len(raw_neighbors) > normalized["max_neighbors_per_site"]:
                        raise _error(
                            self.tool_id,
                            "TOOL_RESOURCE_LIMIT",
                            "NEIGHBOR_CANDIDATE_LIMIT_EXCEEDED",
                            "Algorithm result exceeds max_neighbors_per_site.",
                            siteIndex=site_index,
                            observed=len(raw_neighbors),
                            maximum=normalized["max_neighbors_per_site"],
                        )
                    retained_rows += len(raw_neighbors)
                    if retained_rows > normalized["max_retained_rows"]:
                        raise _error(
                            self.tool_id,
                            "TOOL_RESOURCE_LIMIT",
                            "ARTIFACT_TOO_LARGE",
                            "Coordination result exceeds max_retained_rows.",
                            maximum=normalized["max_retained_rows"],
                        )
                    site_results.append(
                        self._site_result(
                            structure,
                            structure_hash,
                            site_index,
                            raw_neighbors,
                            parameter_hash,
                        )
                    )
                except ToolExecutionError:
                    raise
                except Exception as exc:
                    unsupported_sites.append(
                        {
                            "structureHash": structure_hash,
                            "siteId": _site_id(structure_hash, site_index),
                            "siteIndex": site_index,
                            "reason": self.failure_reason(exc),
                        }
                    )

        successful_sites = len(site_results)
        failed_sites = len(unsupported_sites)
        status = "COMPLETE" if failed_sites == 0 else ("PARTIAL" if successful_sites else "FAILED")
        payload = {
            "artifactType": self.tool_id,
            "schema_version": self.artifact_schema,
            "tool": {"toolId": self.tool_id, "toolVersion": self.context.tool_version, "adapterVersion": self.adapter_version},
            "algorithm": {"algorithmId": self.algorithm_id, "algorithmVersion": PYMATGEN_VERSION},
            "library": {"name": "pymatgen", "version": PYMATGEN_VERSION, "coreVersion": PYMATGEN_CORE_VERSION, "license": "MIT"},
            "resolvedParameters": normalized,
            "fixedParameters": self.fixed_parameters(),
            "parameterHash": parameter_hash,
            "scope": {
                "projectId": self.context.project_id,
                "datasetId": self.context.dataset_id,
                "jobId": self.context.job_id,
                "planId": self.context.plan_id,
                "planVersion": self.context.plan_version,
                "toolCallId": self.context.tool_call_id,
                "sourceResourceId": prepared.source_ref,
                "sourceResourceHash": prepared.source_hash,
            },
            "structures": structure_records,
            "siteResults": sorted(site_results, key=lambda item: (item["structureHash"], item["siteIndex"])),
            "coverage": {
                "status": status,
                "totalSites": total_sites,
                "eligibleSites": total_sites,
                "successfulSites": successful_sites,
                "unsupportedSites": failed_sites,
                "failedSites": failed_sites,
                "zeroNeighborSites": sum(1 for item in site_results if item["neighborCount"] == 0),
                "retainedNeighborRows": retained_rows,
                "ratio": _round(successful_sites / total_sites) if total_sites else 0.0,
            },
            "warnings": sorted(set(result_warnings)),
            "unsupportedSites": unsupported_sites,
            "runtimeDiagnostics": {"algorithmFallback": False, "resultSubstitution": False, "frontendRecomputation": False},
            "provenance": {
                "inputHashes": list(self._input_hashes),
                "resolvedParameterHash": parameter_hash,
                "authority": "registered_backend_adapter",
                "comparisonAuthority": "deterministic_consumer_presentation_only",
            },
            "limits": {
                **{key: normalized[key] for key in ("max_structures", "max_sites", "max_neighbors_per_site", "max_retained_rows")},
                "max_artifact_bytes": MAX_ARTIFACT_BYTES,
                "timeout_seconds": 120,
            },
            "security": {
                "containsJavascript": False,
                "containsHtml": False,
                "externalUrls": [],
                "arbitraryCodeExecution": False,
            },
        }
        encoded = stable_json_dumps(payload)
        if len(encoded.encode("utf-8")) > MAX_ARTIFACT_BYTES:
            raise _error(self.tool_id, "TOOL_RESOURCE_LIMIT", "ARTIFACT_TOO_LARGE", "Coordination Artifact exceeds 16 MiB.")
        return CoordinationResult(payload, _summary(payload), _recipe(self, payload))

    def _site_result(
        self,
        structure: Structure,
        structure_hash: str,
        site_index: int,
        raw_neighbors: list[dict[str, Any]],
        parameter_hash: str,
    ) -> dict[str, Any]:
        neighbors: list[dict[str, Any]] = []
        for item in raw_neighbors:
            neighbor_index = int(item.get("site_index", -1))
            if neighbor_index < 0 or neighbor_index >= len(structure):
                raise _error(self.tool_id, "TOOL_OUTPUT_INVALID", "SITE_INDEX_OUT_OF_RANGE", "Algorithm returned an invalid neighbor site index.")
            image = _periodic_image(item.get("image"), self.tool_id)
            distance = float(getattr(item.get("site"), "nn_distance", math.nan))
            weight = float(item.get("weight", math.nan))
            if not math.isfinite(distance) or distance < 0 or not math.isfinite(weight) or weight < 0:
                raise _error(self.tool_id, "TOOL_OUTPUT_INVALID", "NO_COORDINATION_RESULT", "Algorithm returned a non-finite coordination value.")
            neighbors.append(
                {
                    "neighborIdentity": _neighbor_id(self.algorithm_id, parameter_hash, structure_hash, site_index, neighbor_index, image),
                    "neighborSiteId": _site_id(structure_hash, neighbor_index),
                    "neighborSiteIndex": neighbor_index,
                    "periodicImage": image,
                    "distance": _round(distance),
                    "distanceUnit": "angstrom",
                    "weight": _round(weight),
                }
            )
        neighbors.sort(key=lambda item: (item["neighborSiteIndex"], item["periodicImage"], item["distance"], item["weight"]))
        site = structure[site_index]
        return {
            "structureHash": structure_hash,
            "siteId": _site_id(structure_hash, site_index),
            "siteIndex": site_index,
            "species": str(site.species),
            "fractionalCoordinates": [_round(float(value)) for value in site.frac_coords],
            "coordinationSemantics": self.coordination_semantics,
            "coordinationValue": _round(sum(float(item["weight"]) for item in neighbors)),
            "neighborCount": len(neighbors),
            "neighbors": neighbors,
        }

    def export(self, result: CoordinationResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        requested = set(artifact_types) or {ArtifactType.table_json, ArtifactType.summary_md, ArtifactType.recipe_json}
        payloads: list[ArtifactPayload] = []
        if ArtifactType.table_json in requested:
            payloads.append(ArtifactPayload(artifact_type=ArtifactType.table_json, file_name=self.output_name, content=stable_json_dumps(result.payload), media_type="application/json"))
        if ArtifactType.summary_md in requested:
            payloads.append(ArtifactPayload(artifact_type=ArtifactType.summary_md, file_name="summary.md", content=result.summary, media_type="text/markdown"))
        if ArtifactType.recipe_json in requested:
            payloads.append(ArtifactPayload(artifact_type=ArtifactType.recipe_json, file_name="recipe.json", content=stable_json_dumps(result.recipe), media_type="application/json"))
        return self.export_payloads(
            payloads,
            provenance={
                "artifactType": result.payload["artifactType"],
                "schemaVersion": result.payload["schema_version"],
                "algorithmId": self.algorithm_id,
                "algorithmVersion": PYMATGEN_VERSION,
                "parameterHash": result.payload["parameterHash"],
                "scientificAuthority": "registered_backend_adapter",
            },
        )

    def normalize_params(self, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def create_algorithm(self, params: dict[str, Any]) -> Any:
        raise NotImplementedError

    def fixed_parameters(self) -> dict[str, Any]:
        raise NotImplementedError

    def failure_reason(self, exc: Exception) -> str:
        return "ALGORITHM_FAILED"


class CrystalNNCoordinationAdapter(_CoordinationNNAdapter):
    tool_id = "structure.coordination_crystalnn"
    adapter_version = "0.1.0"
    algorithm_id = "pymatgen.crystalnn"
    artifact_schema = "phase10n1.crystalnn_coordination.v1"
    output_name = "crystalnn_coordination.json"
    coordination_semantics = "crystalnn_weight_sum"

    def normalize_params(self, params: dict[str, Any]) -> dict[str, Any]:
        allowed = {"weighted_cn", "distance_cutoff_low", "distance_cutoff_high", "x_diff_weight", "porous_adjustment", "search_cutoff_angstrom", "max_structures", "max_sites", "max_neighbors_per_site", "max_retained_rows"}
        _reject_unknown(self.tool_id, params, allowed)
        result = {
            "weighted_cn": _bool(params, "weighted_cn", True, self.tool_id),
            "distance_cutoff_low": _number(params, "distance_cutoff_low", 0.5, 0.0, 5.0, self.tool_id),
            "distance_cutoff_high": _number(params, "distance_cutoff_high", 1.0, 0.0, 5.0, self.tool_id),
            "x_diff_weight": _number(params, "x_diff_weight", 3.0, 0.0, 10.0, self.tool_id),
            "porous_adjustment": _bool(params, "porous_adjustment", True, self.tool_id),
            "search_cutoff_angstrom": _number(params, "search_cutoff_angstrom", 7.0, 1.0, 20.0, self.tool_id),
            **_limit_params(params, self.tool_id),
        }
        if result["distance_cutoff_high"] < result["distance_cutoff_low"]:
            raise _error(self.tool_id, "TOOL_PARAM_INVALID", "ALGORITHM_PARAMETER_INVALID", "distance_cutoff_high must be greater than or equal to distance_cutoff_low.")
        return result

    def create_algorithm(self, params: dict[str, Any]) -> CrystalNN:
        return CrystalNN(
            weighted_cn=params["weighted_cn"],
            cation_anion=False,
            distance_cutoffs=(params["distance_cutoff_low"], params["distance_cutoff_high"]),
            x_diff_weight=params["x_diff_weight"],
            porous_adjustment=params["porous_adjustment"],
            search_cutoff=params["search_cutoff_angstrom"],
            fingerprint_length=None,
        )

    def fixed_parameters(self) -> dict[str, Any]:
        return {"cation_anion": False, "fingerprint_length": None}


class VoronoiNNCoordinationAdapter(_CoordinationNNAdapter):
    tool_id = "structure.coordination_voronoinn"
    adapter_version = "0.1.0"
    algorithm_id = "pymatgen.voronoinn"
    artifact_schema = "phase10n1.voronoinn_coordination.v1"
    output_name = "voronoinn_coordination.json"
    coordination_semantics = "voronoinn_solid_angle_weight_sum"

    def normalize_params(self, params: dict[str, Any]) -> dict[str, Any]:
        allowed = {"tol", "cutoff_angstrom", "allow_pathological", "max_structures", "max_sites", "max_neighbors_per_site", "max_retained_rows"}
        _reject_unknown(self.tool_id, params, allowed)
        return {
            "tol": _number(params, "tol", 0.0, 0.0, 1.0, self.tool_id),
            "cutoff_angstrom": _number(params, "cutoff_angstrom", 13.0, 1.0, 20.0, self.tool_id),
            "allow_pathological": _bool(params, "allow_pathological", False, self.tool_id),
            **_limit_params(params, self.tool_id),
        }

    def create_algorithm(self, params: dict[str, Any]) -> VoronoiNN:
        return VoronoiNN(
            tol=params["tol"],
            cutoff=params["cutoff_angstrom"],
            allow_pathological=params["allow_pathological"],
            weight="solid_angle",
            extra_nn_info=True,
            compute_adj_neighbors=True,
        )

    def fixed_parameters(self) -> dict[str, Any]:
        return {"weight": "solid_angle", "extra_nn_info": True, "compute_adj_neighbors": True}

    def failure_reason(self, exc: Exception) -> str:
        message = str(exc).lower()
        return "PATHOLOGICAL_VORONOI_CELL" if "pathological" in message or "voronoi" in message else "ALGORITHM_FAILED"


def _validate_n1_structure(tool_id: str, label: str, structure: Structure, max_sites: int) -> None:
    if len(structure) > max_sites:
        raise _error(tool_id, "TOOL_RESOURCE_LIMIT", "STRUCTURE_TOO_LARGE", "Structure exceeds max_sites.", structure=label, observed=len(structure), maximum=max_sites)
    matrix = structure.lattice.matrix
    if not all(math.isfinite(float(value)) for row in matrix for value in row):
        raise _error(tool_id, "TOOL_INPUT_INVALID", "NON_FINITE_STRUCTURE_VALUE", "Structure lattice contains a non-finite value.")
    for site_index, site in enumerate(structure):
        if not all(math.isfinite(float(value)) for value in site.frac_coords):
            raise _error(tool_id, "TOOL_INPUT_INVALID", "NON_FINITE_STRUCTURE_VALUE", "Structure coordinates contain a non-finite value.", siteIndex=site_index)
        if not site.is_ordered:
            raise _error(tool_id, "TOOL_INPUT_INVALID", "UNSUPPORTED_DISORDER", "N1 coordination does not coerce disordered sites.", siteIndex=site_index)
        occupancy = float(site.species.num_atoms)
        if not math.isclose(occupancy, 1.0, abs_tol=1e-12):
            raise _error(tool_id, "TOOL_INPUT_INVALID", "UNSUPPORTED_PARTIAL_OCCUPANCY", "N1 coordination requires full site occupancy.", siteIndex=site_index)


def _limit_params(params: dict[str, Any], tool_id: str) -> dict[str, int]:
    return {
        "max_structures": _integer(params, "max_structures", 32, 1, 32, tool_id),
        "max_sites": _integer(params, "max_sites", 5000, 1, 5000, tool_id),
        "max_neighbors_per_site": _integer(params, "max_neighbors_per_site", 1000, 1, 1000, tool_id),
        "max_retained_rows": _integer(params, "max_retained_rows", 50000, 1, 50000, tool_id),
    }


def _reject_unknown(tool_id: str, params: dict[str, Any], allowed: set[str]) -> None:
    unknown = sorted(set(params) - allowed)
    if unknown:
        raise _error(tool_id, "TOOL_PARAM_INVALID", "ALGORITHM_PARAMETER_INVALID", "Unknown coordination parameters were rejected.", parameters=unknown)


def _number(params: dict[str, Any], name: str, default: float, minimum: float, maximum: float, tool_id: str) -> float:
    value = params.get(name, default)
    if isinstance(value, bool):
        raise _error(tool_id, "TOOL_PARAM_INVALID", "ALGORITHM_PARAMETER_INVALID", f"{name} must be a finite number.")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise _error(tool_id, "TOOL_PARAM_INVALID", "ALGORITHM_PARAMETER_INVALID", f"{name} must be a finite number.") from exc
    if not math.isfinite(number) or not minimum <= number <= maximum:
        raise _error(tool_id, "TOOL_PARAM_INVALID", "ALGORITHM_PARAMETER_INVALID", f"{name} must be between {minimum} and {maximum}.")
    return number


def _integer(params: dict[str, Any], name: str, default: int, minimum: int, maximum: int, tool_id: str) -> int:
    value = params.get(name, default)
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise _error(tool_id, "TOOL_PARAM_INVALID", "ALGORITHM_PARAMETER_INVALID", f"{name} must be an integer between {minimum} and {maximum}.")
    return value


def _bool(params: dict[str, Any], name: str, default: bool, tool_id: str) -> bool:
    value = params.get(name, default)
    if not isinstance(value, bool):
        raise _error(tool_id, "TOOL_PARAM_INVALID", "ALGORITHM_PARAMETER_INVALID", f"{name} must be a boolean.")
    return value


def _periodic_image(value: Any, tool_id: str) -> list[int]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise _error(tool_id, "TOOL_OUTPUT_INVALID", "NO_COORDINATION_RESULT", "Algorithm returned an invalid periodic image.")
    image: list[int] = []
    for item in value:
        number = float(item)
        integer = int(round(number))
        if not math.isfinite(number) or not math.isclose(number, integer, abs_tol=1e-9):
            raise _error(tool_id, "TOOL_OUTPUT_INVALID", "NO_COORDINATION_RESULT", "Algorithm returned a non-integer periodic image.")
        image.append(integer)
    return image


def _input_ref(value: Any) -> str:
    return str(getattr(value, "ref", value.get("ref", "") if isinstance(value, dict) else ""))


def _site_id(structure_hash: str, site_index: int) -> str:
    return f"site:{structure_hash}:{site_index}"


def _neighbor_id(algorithm_id: str, parameter_hash: str, structure_hash: str, center: int, neighbor: int, image: list[int]) -> str:
    return f"neighbor:{algorithm_id}:{parameter_hash}:{structure_hash}:{center}:{neighbor}:{image[0]},{image[1]},{image[2]}"


def _round(value: float) -> float:
    return round(float(value), 12)


def _library_warning_code(algorithm_id: str, message: str) -> str:
    lowered = message.lower()
    if "oxidation states" in lowered:
        return "CRYSTALNN_OXIDATION_STATES_NOT_DECLARED"
    if "radius" in lowered:
        return "CRYSTALNN_RADIUS_FALLBACK_USED"
    return f"{algorithm_id.upper().replace('.', '_')}_LIBRARY_WARNING"


def _error(tool_id: str, code: str, error_type: str, message: str, **details: Any) -> ToolExecutionError:
    return ToolExecutionError(code=code, message=message, tool_id=tool_id, details={"errorType": error_type, **details})


def _summary(payload: dict[str, Any]) -> str:
    coverage = payload["coverage"]
    return "\n".join(
        [
            "# Algorithm-derived coordination",
            "",
            f"- Tool: `{payload['tool']['toolId']}@{payload['tool']['toolVersion']}`",
            f"- Algorithm: `{payload['algorithm']['algorithmId']}@{payload['algorithm']['algorithmVersion']}`",
            f"- Coverage: {coverage['successfulSites']}/{coverage['totalSites']} sites ({coverage['status']})",
            f"- Parameter hash: `{payload['parameterHash']}`",
            "- Interpretation boundary: neighbor relations are identified by the stated algorithm and are not definitive chemical bonds.",
            "",
        ]
    )


def _recipe(adapter: _CoordinationNNAdapter, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "0.1",
        "recipeId": f"recipe_{adapter.context.tool_call_id}",
        "name": "Algorithm-derived coordination",
        "version": "1",
        "projectId": adapter.context.project_id,
        "sourceJobId": adapter.context.job_id,
        "executionAuthority": "NONE",
        "steps": [
            {
                "stepId": "step_from_adapter",
                "toolId": adapter.tool_id,
                "toolVersion": adapter.context.tool_version,
                "algorithmId": adapter.algorithm_id,
                "algorithmVersion": PYMATGEN_VERSION,
                "params": payload["resolvedParameters"],
                "parameterHash": payload["parameterHash"],
                "sourceResourceId": payload["scope"]["sourceResourceId"],
                "sourceResourceHash": payload["scope"]["sourceResourceHash"],
                "artifactContract": payload["schema_version"],
                "artifactTypes": ["table_json", "summary_md", "recipe_json"],
            }
        ],
    }
