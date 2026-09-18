from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping

import numpy as np
from ase.geometry import find_mic

from mdi_artifact_core import ArtifactPayload, content_hash, stable_json_dumps, validate_trajectory
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError


RDF_TOOL = "trajectory.rdf"
MSD_TOOL = "trajectory.msd"
DIFFUSION_TOOL = "trajectory.diffusion"
TOOL_VERSION = "0.1.0"
RDF_SCHEMA = "phase10n4.trajectory_rdf.v1"
MSD_SCHEMA = "phase10n4.trajectory_msd.v1"
DIFFUSION_SCHEMA = "phase10n4.trajectory_diffusion.v1"
TRAJECTORY_SCHEMA = "phase10g.trajectory.v1"
RDF_ALGORITHM = "mdi.trajectory_rdf_ase_mic_unordered_pair_density@1.0.0"
UNWRAP_ALGORITHM = "mdi.fixed_cell_fractional_minimum_image@1.0.0"
MSD_ALGORITHM = "mdi.multiple_time_origin_msd@1.0.0"
DIFFUSION_ALGORITHM = "mdi.explicit_window_ols_einstein@1.0.0"
CELL_ABS_TOL = 1e-8
CELL_REL_TOL = 1e-8
UNWRAP_FRACTIONAL_STEP_LIMIT = 0.49
MAX_ARTIFACT_BYTES = 32 * 1024 * 1024
MAX_TRAJECTORY_FRAMES = 200
MAX_TRAJECTORY_ATOMS = 5000
MAX_RDF_PAIR_EVALUATIONS = 30_000_000
NUMPY_VERSION = "2.4.6"
SCIPY_VERSION = "1.17.1"
ASE_VERSION = "3.29.0"


@dataclass(frozen=True)
class AnalyticsResult:
    payload: dict[str, Any]
    plot: dict[str, Any]
    summary: str
    recipe: dict[str, Any]


class _TrajectoryAdapter(BaseToolAdapter):
    schema_version: str

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> dict[str, Any]:
        normalized = self.normalize_params(params)
        if len(input_refs) != 1:
            raise _error("TOOL_INPUT_INVALID", "TRAJECTORY_MISSING", "Exactly one immutable trajectory is required.")
        ref = _input_ref(input_refs[0])
        value = context.object_store.get(ref)
        if not isinstance(value, Mapping) and isinstance(getattr(value, "payload", None), Mapping):
            value = value.payload
        if not isinstance(value, Mapping):
            raise _error("TOOL_INPUT_INVALID", "STALE_TRAJECTORY", "The exact trajectory reference is unavailable.", ref=ref)
        trajectory = dict(value)
        validation = validate_trajectory(trajectory)
        if not validation.valid:
            raise _error("TOOL_INPUT_INVALID", _trajectory_error(validation.errors), "The trajectory contract is invalid.", errors=list(validation.errors))
        if trajectory.get("schema_version") != TRAJECTORY_SCHEMA:
            raise _error("TOOL_INPUT_INVALID", "TRAJECTORY_MISSING", "The trajectory contract version is unsupported.")
        if int(trajectory["atoms"]["count"]) > MAX_TRAJECTORY_ATOMS:
            raise _error("TOOL_RESOURCE_LIMIT", "TRAJECTORY_TOO_LARGE", "The trajectory exceeds the N4 atom cap.")
        selected, analysis_window = _select_analysis_window(trajectory, normalized)
        return {
            "source_trajectory": trajectory,
            "selected_trajectory": selected,
            "analysis_window": analysis_window,
        }

    def export(self, result: AnalyticsResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        requested = set(artifact_types) or {ArtifactType.table_json, ArtifactType.plotly_json, ArtifactType.summary_md, ArtifactType.recipe_json}
        payloads: list[ArtifactPayload] = []
        stem = self.tool_id.replace(".", "_")
        if ArtifactType.table_json in requested:
            payloads.append(ArtifactPayload(ArtifactType.table_json, f"{stem}.json", stable_json_dumps(result.payload), "application/json"))
        if ArtifactType.plotly_json in requested:
            payloads.append(ArtifactPayload(ArtifactType.plotly_json, f"{stem}_plot.json", stable_json_dumps(result.plot), "application/json"))
        if ArtifactType.summary_md in requested:
            payloads.append(ArtifactPayload(ArtifactType.summary_md, "summary.md", result.summary, "text/markdown"))
        if ArtifactType.recipe_json in requested:
            payloads.append(ArtifactPayload(ArtifactType.recipe_json, "recipe.json", stable_json_dumps(result.recipe), "application/json"))
        provenance = {
            "schemaVersion": self.schema_version,
            "trajectoryHash": result.payload["trajectory"]["trajectoryHash"],
            "parameterHash": result.payload["parameterHash"],
            "scientificAuthority": "registered_backend_adapter",
            "analysisWindow": dict(result.payload.get("analysisWindow") or {}),
        }
        if self.tool_id == DIFFUSION_TOOL:
            provenance["sourceMsdArtifactChecksum"] = result.payload["sourceMsd"]["artifactChecksum"]
        return self.export_payloads(payloads, provenance=provenance)

    def _base(
        self,
        trajectory: Mapping[str, Any],
        params: Mapping[str, Any],
        *,
        analysis_window: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        parameter_hash = content_hash(stable_json_dumps(params))
        payload = {
            "artifactType": self.tool_id,
            "schema_version": self.schema_version,
            "tool": {"toolId": self.tool_id, "toolVersion": self.context.tool_version, "adapterVersion": self.adapter_version},
            "scope": {"projectId": self.context.project_id, "datasetId": self.context.dataset_id, "jobId": self.context.job_id, "planId": self.context.plan_id, "planVersion": self.context.plan_version, "toolCallId": self.context.tool_call_id},
            "trajectory": {"resourceId": trajectory["trajectory_id"], "trajectoryHash": trajectory["trajectory_id"], "contractVersion": TRAJECTORY_SCHEMA, "frameCount": len(trajectory["frames"]), "atomCount": trajectory["atoms"]["count"]},
            "resolvedParameters": dict(params),
            "parameterHash": parameter_hash,
            "auditedLockedStack": {"numpy": NUMPY_VERSION, "scipy": SCIPY_VERSION, "ase": ASE_VERSION},
            "warnings": [],
            "limitations": [],
            "security": {"containsHtml": False, "containsJavascript": False, "externalUrls": [], "arbitraryCodeExecution": False},
        }
        if analysis_window:
            payload["analysisWindow"] = dict(analysis_window)
        return payload

    def _finish(self, payload: dict[str, Any], plot: dict[str, Any], summary: str) -> AnalyticsResult:
        encoded = stable_json_dumps(payload).encode("utf-8")
        if len(encoded) > MAX_ARTIFACT_BYTES:
            raise _error("TOOL_RESOURCE_LIMIT", "TRAJECTORY_TOO_LARGE", "The N4 Artifact exceeds the output cap.")
        recipe = self.recipe_payload(name=f"{self.tool_id} declarative provenance", params=payload["resolvedParameters"], artifact_types=[ArtifactType.table_json, ArtifactType.plotly_json])
        recipe.update({"executionAuthorized": False, "trajectoryHash": payload["trajectory"]["trajectoryHash"], "parameterHash": payload["parameterHash"]})
        if payload["schema_version"] == DIFFUSION_SCHEMA:
            recipe["sourceMsd"] = dict(payload["sourceMsd"])
        return AnalyticsResult(payload, plot, summary, recipe)


class TrajectoryRdfAdapter(_TrajectoryAdapter):
    tool_id = RDF_TOOL
    adapter_version = TOOL_VERSION
    schema_version = RDF_SCHEMA

    @staticmethod
    def normalize_params(params: Mapping[str, Any]) -> dict[str, Any]:
        allowed = {"r_min_angstrom", "r_max_angstrom", "bin_count", "species_a", "species_b", "window_mode", "frame_start", "frame_end", "time_start_ps", "time_end_ps", "max_pair_evaluations"}
        _unknown(params, allowed, "RDF_PARAMETER_INVALID")
        mode = str(params.get("window_mode", "whole"))
        if mode not in {"whole", "frame", "time"}:
            raise _error("TOOL_PARAM_INVALID", "RDF_PARAMETER_INVALID", "Unsupported RDF window mode.")
        result = {
            "r_min_angstrom": _number(params, "r_min_angstrom", 0.0, 0.0, 30.0),
            "r_max_angstrom": _number(params, "r_max_angstrom", 2.0, 0.01, 30.0),
            "bin_count": _integer(params, "bin_count", 200, 1, 2048),
            "species_a": _optional_species(params.get("species_a")),
            "species_b": _optional_species(params.get("species_b")),
            "window_mode": mode,
            "frame_start": _integer(params, "frame_start", 0, 0, 9999),
            "frame_end": _integer(params, "frame_end", 10000, 1, 10000),
            "time_start_ps": _number(params, "time_start_ps", 0.0, 0.0, 1e12),
            "time_end_ps": _number(params, "time_end_ps", 1e12, 0.0, 1e12),
            "max_pair_evaluations": _integer(
                params,
                "max_pair_evaluations",
                MAX_RDF_PAIR_EVALUATIONS,
                1,
                MAX_RDF_PAIR_EVALUATIONS,
            ),
        }
        if result["r_min_angstrom"] >= result["r_max_angstrom"] or result["frame_start"] >= result["frame_end"] or result["time_start_ps"] >= result["time_end_ps"]:
            raise _error("TOOL_PARAM_INVALID", "RDF_PARAMETER_INVALID", "RDF ranges must be strictly increasing.")
        if (result["species_a"] is None) != (result["species_b"] is None):
            raise _error("TOOL_PARAM_INVALID", "RDF_PARAMETER_INVALID", "Both species must be supplied together.")
        return result

    def run(self, prepared: dict[str, Any], params: dict[str, Any]) -> AnalyticsResult:
        p = self.normalize_params(params)
        trajectory = prepared["selected_trajectory"]
        source_trajectory = prepared["source_trajectory"]
        analysis_window = prepared["analysis_window"]
        frames = trajectory["frames"]
        frame_ids = [
            f"{source_trajectory['trajectory_id']}:frame:{frame['frame_index']}"
            for frame in frames
        ]
        atoms = trajectory["atoms"]["records"]
        species = [str(item["species"]) for item in atoms]
        pair = _species_pair(species, p["species_a"], p["species_b"])
        edges = np.linspace(p["r_min_angstrom"], p["r_max_angstrom"], p["bin_count"] + 1)
        counts = np.zeros(p["bin_count"], dtype=float)
        denominators = np.zeros(p["bin_count"], dtype=float)
        pair_evaluations = 0
        safe_radii: list[float] = []
        for frame in frames:
            cell = _cell(trajectory, frame)
            pbc = tuple(bool(x) for x in trajectory["periodic_boundary"])
            if not any(pbc):
                raise _error("TOOL_INPUT_INVALID", "TRAJECTORY_PBC_INVALID", "Trajectory RDF requires periodic axes.")
            safe = _safe_radius(cell, pbc)
            safe_radii.append(safe)
            if p["r_max_angstrom"] > safe + 1e-10:
                raise _error("TOOL_PARAM_INVALID", "RDF_RADIUS_EXCEEDS_SAFE_CELL_LIMIT", "r_max exceeds the safe periodic radius.", safeRadiusAngstrom=safe)
            xyz = _cartesian_positions(trajectory, frame, cell)
            indexes_a = [i for i, value in enumerate(species) if pair[0] == "*" or value == pair[0]]
            indexes_b = [i for i, value in enumerate(species) if pair[1] == "*" or value == pair[1]]
            if pair == ("*", "*"):
                pair_i, pair_j = np.triu_indices(len(xyz), k=1)
            elif pair[0] == pair[1]:
                pair_i, pair_j = np.triu_indices(len(indexes_a), k=1)
                selected = np.asarray(indexes_a, dtype=int)
                pair_i, pair_j = selected[pair_i], selected[pair_j]
            else:
                pair_i = np.repeat(np.asarray(indexes_a, dtype=int), len(indexes_b))
                pair_j = np.tile(np.asarray(indexes_b, dtype=int), len(indexes_a))
            frame_pair_count = int(pair_i.size)
            if pair_evaluations + frame_pair_count > p["max_pair_evaluations"]:
                raise _error("TOOL_RESOURCE_LIMIT", "TRAJECTORY_TOO_LARGE", "RDF pair-evaluation cap exceeded.")
            pair_evaluations += frame_pair_count
            distances = _pair_distances(xyz[pair_j] - xyz[pair_i], cell, pbc)
            counts += np.histogram(distances, bins=edges)[0]
            volume = abs(float(np.linalg.det(cell)))
            shell = (4.0 * math.pi / 3.0) * (edges[1:] ** 3 - edges[:-1] ** 3)
            if pair == ("*", "*"):
                expected_pairs = len(xyz) * (len(xyz) - 1) / 2.0
            elif pair[0] == pair[1]:
                expected_pairs = len(indexes_a) * (len(indexes_a) - 1) / 2.0
            else:
                expected_pairs = len(indexes_a) * len(indexes_b)
            denominators += expected_pairs * shell / volume
        g = np.divide(counts, denominators, out=np.zeros_like(counts), where=denominators > 0)
        centers = (edges[:-1] + edges[1:]) / 2.0
        payload = self._base(
            source_trajectory,
            p,
            analysis_window=analysis_window,
        )
        pair_id = _identity("rdf-pair", {"trajectory": trajectory["trajectory_id"], "pair": pair, "parameters": payload["parameterHash"]})
        payload.update({
            "algorithm": {"algorithmId": RDF_ALGORITHM, "version": "1.0.0", "library": "ase.geometry.find_mic", "libraryVersion": ASE_VERSION, "histogramLibrary": "numpy", "histogramLibraryVersion": NUMPY_VERSION, "pairSemantics": "unordered", "normalization": "per_frame_number_density_shell_volume"},
            "units": {"r": "angstrom", "gR": "dimensionless"},
            "speciesPair": {"pairId": pair_id, "speciesA": pair[0], "speciesB": pair[1], "ordered": False},
            "window": {
                "mode": analysis_window["mode"],
                "includedFrameIds": frame_ids,
                "startInclusive": True,
                "endExclusive": True,
            },
            "binIds": [_identity("rdf-bin", {"pairId": pair_id, "index": index}) for index in range(len(centers))], "binEdgesAngstrom": _list(edges), "binCentersAngstrom": _list(centers), "gR": _list(g), "pairCounts": [int(x) for x in counts],
            "coverage": {"requestedFrames": len(frames), "includedFrames": len(frames), "excludedFrames": [], "pairSamples": int(pair_evaluations)},
            "cellPolicy": {"latticeMode": trajectory["lattice_mode"], "pbcAxes": trajectory["periodic_boundary"], "minimumSafeRadiusAngstrom": _round(min(safe_radii))},
            "limitations": ["Trajectory RDF is a frame-averaged pair distribution under the stated window and normalization; peaks are not automatically chemical bonds or coordination shells."],
            "runtimeDiagnostics": {"frontendRecomputation": False, "staticRdfAuthorityReused": False},
        })
        plot = _line_plot("Trajectory RDF", centers, [("g(r)", g)], "r / angstrom", "g(r)")
        return self._finish(payload, plot, f"# Trajectory RDF\n\n{len(frames)} frames; pair {pair[0]}-{pair[1]}; g(r) is dimensionless.")


class TrajectoryMsdAdapter(_TrajectoryAdapter):
    tool_id = MSD_TOOL
    adapter_version = TOOL_VERSION
    schema_version = MSD_SCHEMA

    @staticmethod
    def normalize_params(params: Mapping[str, Any]) -> dict[str, Any]:
        allowed = {
            "species",
            "max_lag_count",
            "origin_stride",
            "max_origins_per_lag",
            "drift_correction",
            "window_mode",
            "frame_start",
            "frame_end",
            "time_start_ps",
            "time_end_ps",
        }
        _unknown(params, allowed, "MSD_PARAMETER_INVALID")
        correction = str(params.get("drift_correction", "none"))
        if correction != "none":
            raise _error("TOOL_PARAM_INVALID", "MSD_PARAMETER_INVALID", "Only explicit no-drift-correction is supported.")
        mode = str(params.get("window_mode", "whole"))
        if mode not in {"whole", "frame", "time"}:
            raise _error("TOOL_PARAM_INVALID", "MSD_PARAMETER_INVALID", "Unsupported MSD window mode.")
        result = {
            "species": _optional_species(params.get("species")),
            "max_lag_count": _integer(params, "max_lag_count", 512, 1, 2048),
            "origin_stride": _integer(params, "origin_stride", 1, 1, 1000),
            "max_origins_per_lag": _integer(params, "max_origins_per_lag", 4096, 1, 4096),
            "drift_correction": correction,
            "window_mode": mode,
            "frame_start": _integer(params, "frame_start", 0, 0, 9999),
            "frame_end": _integer(params, "frame_end", 10000, 1, 10000),
            "time_start_ps": _number(params, "time_start_ps", 0.0, 0.0, 1e12),
            "time_end_ps": _number(params, "time_end_ps", 1e12, 0.0, 1e12),
        }
        if result["frame_start"] >= result["frame_end"] or result["time_start_ps"] >= result["time_end_ps"]:
            raise _error("TOOL_PARAM_INVALID", "MSD_PARAMETER_INVALID", "MSD ranges must be strictly increasing.")
        return result

    def run(self, prepared: dict[str, Any], params: dict[str, Any]) -> AnalyticsResult:
        p = self.normalize_params(params)
        trajectory = prepared["selected_trajectory"]
        source_trajectory = prepared["source_trajectory"]
        analysis_window = prepared["analysis_window"]
        times = _physical_times_ps(trajectory, require_constant=True)
        if len(times) < 3:
            raise _error("TOOL_INPUT_INVALID", "MSD_INSUFFICIENT_FRAMES", "MSD requires at least three timed frames.")
        if trajectory["lattice_mode"] != "fixed":
            raise _error("TOOL_INPUT_INVALID", "TRAJECTORY_VARIABLE_CELL_UNSUPPORTED", "Variable-cell MSD is unavailable in N4.")
        cell = _cell(trajectory, trajectory["frames"][0])
        pbc = tuple(bool(x) for x in trajectory["periodic_boundary"])
        species_all = [str(item["species"]) for item in trajectory["atoms"]["records"]]
        selected = [i for i, value in enumerate(species_all) if p["species"] is None or value == p["species"]]
        if not selected:
            raise _error("TOOL_PARAM_INVALID", "RDF_SPECIES_NOT_FOUND", "Requested MSD species is absent.")
        unwrapped, diagnostics = _unwrapped_cartesian(trajectory, cell, pbc)
        max_lag = min(p["max_lag_count"], len(times) - 1)
        lag_times: list[float] = []
        total: list[float] = []
        directional = [[], [], []]
        origins: list[int] = []
        for lag in range(1, max_lag + 1):
            available = list(range(0, len(times) - lag, p["origin_stride"]))[:p["max_origins_per_lag"]]
            delta = unwrapped[np.asarray(available) + lag][:, selected, :] - unwrapped[np.asarray(available)][:, selected, :]
            squared = delta * delta
            directional_values = np.mean(squared, axis=(0, 1))
            lag_times.append(_round(times[lag] - times[0]))
            total.append(_round(float(np.sum(directional_values))))
            for axis in range(3):
                directional[axis].append(_round(float(directional_values[axis])))
            origins.append(len(available))
        payload = self._base(
            source_trajectory,
            p,
            analysis_window=analysis_window,
        )
        series_id = _identity("msd-series", {"trajectory": trajectory["trajectory_id"], "species": p["species"] or "all", "parameters": payload["parameterHash"]})
        payload.update({
            "algorithm": {"algorithmId": MSD_ALGORITHM, "version": "1.0.0", "library": "numpy", "libraryVersion": NUMPY_VERSION, "estimator": "multiple_time_origin", "atomAveraging": True},
            "unwrapping": {"algorithmId": UNWRAP_ALGORITHM, "version": "1.0.0", "library": "numpy", "libraryVersion": NUMPY_VERSION, "serverSide": True, "wrappedCoordinateDirectUse": False, **diagnostics},
            "units": {"lagTime": "picosecond", "msd": "angstrom^2"}, "species": p["species"] or "all", "seriesId": series_id, "atomIds": [trajectory["atoms"]["records"][i]["atom_id"] for i in selected],
            "lagIds": [_identity("msd-lag", {"seriesId": series_id, "index": index}) for index in range(len(lag_times))], "lagTimesPs": lag_times, "totalMsdAngstrom2": total, "directionalMsdAngstrom2": {"x": directional[0], "y": directional[1], "z": directional[2]}, "originCounts": origins,
            "coverage": {
                "frames": len(times),
                "sourceFrames": len(source_trajectory["frames"]),
                "atoms": len(selected),
                "validLags": len(lag_times),
                "minimumOriginCount": min(origins),
            },
            "time": {"source": "trajectory_frame_time", "sourceUnit": trajectory["time"]["unit"], "canonicalUnit": "picosecond", "constantTimestep": True},
            "cellPolicy": {"mode": "fixed", "pbcAxes": trajectory["periodic_boundary"], "variableCellSupported": False},
            "limitations": ["MSD uses Cartesian x/y/z axes and is not automatically crystallographic a/b/c diffusion.", "No center-of-mass drift correction is applied."],
            "runtimeDiagnostics": {"frontendUnwrapping": False, "frontendMsdRecomputation": False},
        })
        plot = _line_plot("Trajectory MSD", lag_times, [("total", total), ("x", directional[0]), ("y", directional[1]), ("z", directional[2])], "lag time / ps", "MSD / angstrom^2")
        return self._finish(payload, plot, f"# Trajectory MSD\n\nMultiple-time-origin MSD for {p['species'] or 'all atoms'} from server-side validated unwrapped coordinates.")


class TrajectoryDiffusionAdapter(_TrajectoryAdapter):
    tool_id = DIFFUSION_TOOL
    adapter_version = TOOL_VERSION
    schema_version = DIFFUSION_SCHEMA

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> dict[str, Any]:
        self.normalize_params(params)
        if len(input_refs) != 1:
            raise _error("TOOL_INPUT_INVALID", "DIFFUSION_MSD_ARTIFACT_MISSING", "Diffusion requires one exact persisted MSD Artifact.")
        ref = _input_ref(input_refs[0])
        payload = context.object_store.get(ref)
        binding = dict(context.artifact_bindings.get(ref) or {})
        if not isinstance(payload, Mapping) or payload.get("schema_version") != MSD_SCHEMA or payload.get("artifactType") != MSD_TOOL:
            raise _error("TOOL_INPUT_INVALID", "DIFFUSION_MSD_ARTIFACT_MISSING", "The exact MSD contract is missing.")
        if not binding.get("artifactId") or not binding.get("checksum"):
            raise _error("TOOL_INPUT_INVALID", "DIFFUSION_MSD_CHECKSUM_MISMATCH", "Persisted MSD identity and checksum are required.")
        return {"msd": dict(payload), "binding": binding}

    @staticmethod
    def normalize_params(params: Mapping[str, Any]) -> dict[str, Any]:
        allowed = {"fit_start_time_ps", "fit_end_time_ps", "direction", "minimum_fit_points", "minimum_fit_duration_ps", "minimum_origin_coverage", "minimum_r_squared", "alpha_min", "alpha_max"}
        _unknown(params, allowed, "DIFFUSION_FIT_WINDOW_INVALID")
        if "fit_start_time_ps" not in params or "fit_end_time_ps" not in params:
            raise _error("TOOL_PARAM_INVALID", "DIFFUSION_FIT_WINDOW_INVALID", "An explicit diffusion fit window is required.")
        direction = str(params.get("direction", "total"))
        if direction not in {"total", "x", "y", "z"}:
            raise _error("TOOL_PARAM_INVALID", "DIFFUSION_FIT_WINDOW_INVALID", "Unknown diffusion direction.")
        result = {"fit_start_time_ps": _number(params, "fit_start_time_ps", 0.0, 0.0, 1e12), "fit_end_time_ps": _number(params, "fit_end_time_ps", 1.0, 0.0, 1e12), "direction": direction, "minimum_fit_points": _integer(params, "minimum_fit_points", 5, 3, 10000), "minimum_fit_duration_ps": _number(params, "minimum_fit_duration_ps", 1.0, 0.0, 1e9), "minimum_origin_coverage": _number(params, "minimum_origin_coverage", 0.2, 0.0, 1.0), "minimum_r_squared": _number(params, "minimum_r_squared", 0.9, 0.0, 1.0), "alpha_min": _number(params, "alpha_min", 0.8, 0.1, 2.0), "alpha_max": _number(params, "alpha_max", 1.2, 0.1, 3.0)}
        if result["fit_start_time_ps"] >= result["fit_end_time_ps"] or result["alpha_min"] >= result["alpha_max"]:
            raise _error("TOOL_PARAM_INVALID", "DIFFUSION_FIT_WINDOW_INVALID", "Diffusion ranges must be strictly increasing.")
        return result

    def run(self, prepared: dict[str, Any], params: dict[str, Any]) -> AnalyticsResult:
        p = self.normalize_params(params)
        msd = prepared["msd"]
        times = np.asarray(msd["lagTimesPs"], dtype=float)
        values = np.asarray(msd["totalMsdAngstrom2"] if p["direction"] == "total" else msd["directionalMsdAngstrom2"][p["direction"]], dtype=float)
        origins = np.asarray(msd["originCounts"], dtype=float)
        mask = (times >= p["fit_start_time_ps"]) & (times <= p["fit_end_time_ps"])
        x, y, origin = times[mask], values[mask], origins[mask]
        status = "DIFFUSIVE_WINDOW_ACCEPTED"
        if len(x) < p["minimum_fit_points"]:
            status = "INSUFFICIENT_POINTS"
        elif float(x[-1] - x[0]) < p["minimum_fit_duration_ps"]:
            status = "INSUFFICIENT_DURATION"
        slope = intercept = r_squared = rmse = alpha = None
        coverage = float(np.min(origin) / np.max(origins)) if len(origin) else 0.0
        if status == "DIFFUSIVE_WINDOW_ACCEPTED" and coverage < p["minimum_origin_coverage"]:
            status = "INSUFFICIENT_ORIGIN_COVERAGE"
        if len(x) >= 2:
            matrix = np.column_stack([x, np.ones(len(x))])
            slope_value, intercept_value = np.linalg.lstsq(matrix, y, rcond=None)[0]
            predicted = slope_value * x + intercept_value
            residual = y - predicted
            ss_res = float(np.sum(residual ** 2))
            ss_tot = float(np.sum((y - np.mean(y)) ** 2))
            r2_value = 1.0 - ss_res / ss_tot if ss_tot > 0 else (1.0 if ss_res == 0 else 0.0)
            slope, intercept, r_squared, rmse = map(_round, (slope_value, intercept_value, r2_value, math.sqrt(ss_res / len(x))))
            positive = (x > 0) & (y > 0)
            if int(np.sum(positive)) >= 3:
                alpha = _round(float(np.linalg.lstsq(np.column_stack([np.log(x[positive]), np.ones(int(np.sum(positive)))]), np.log(y[positive]), rcond=None)[0][0]))
            if status == "DIFFUSIVE_WINDOW_ACCEPTED" and slope_value <= 0:
                status = "NON_POSITIVE_SLOPE"
            elif status == "DIFFUSIVE_WINDOW_ACCEPTED" and r2_value < p["minimum_r_squared"]:
                status = "POOR_LINEAR_FIT"
            elif status == "DIFFUSIVE_WINDOW_ACCEPTED" and alpha is None:
                status = "INSUFFICIENT_MSD_SIGNAL"
            elif status == "DIFFUSIVE_WINDOW_ACCEPTED" and alpha > p["alpha_max"]:
                status = "BALLISTIC_LIKE_WINDOW"
            elif status == "DIFFUSIVE_WINDOW_ACCEPTED" and not (p["alpha_min"] <= alpha <= p["alpha_max"]):
                status = "NON_DIFFUSIVE_WINDOW"
        divisor = 6.0 if p["direction"] == "total" else 2.0
        estimate = _round(float(slope) / divisor) if status == "DIFFUSIVE_WINDOW_ACCEPTED" and slope is not None else None
        trajectory = {"trajectory_id": msd["trajectory"]["trajectoryHash"], "frames": [None] * int(msd["trajectory"]["frameCount"]), "atoms": {"count": int(msd["trajectory"]["atomCount"])} }
        payload = self._base(
            trajectory,
            p,
            analysis_window=msd.get("analysisWindow"),
        )
        window_id = _identity("diffusion-window", {"msdChecksum": prepared["binding"]["checksum"], "start": p["fit_start_time_ps"], "end": p["fit_end_time_ps"], "direction": p["direction"]})
        payload.update({
            "sourceMsd": {"artifactId": prepared["binding"]["artifactId"], "artifactChecksum": prepared["binding"]["checksum"], "contractVersion": MSD_SCHEMA, "toolId": MSD_TOOL, "toolVersion": TOOL_VERSION, "parameterHash": msd["parameterHash"]},
            "algorithm": {"algorithmId": DIFFUSION_ALGORITHM, "version": "1.0.0", "library": "numpy", "libraryVersion": NUMPY_VERSION, "regression": "numpy.linalg.lstsq", "einsteinDivisor": divisor, "automaticWindowOptimization": False},
            "units": {"fitTime": "picosecond", "msd": "angstrom^2", "diffusion": "angstrom^2/picosecond"},
            "fitWindow": {"windowId": window_id, "startPs": p["fit_start_time_ps"], "endPs": p["fit_end_time_ps"], "explicit": True, "pointCount": len(x), "durationPs": _round(float(x[-1] - x[0])) if len(x) else 0.0},
            "fit": {"slopeAngstrom2PerPs": slope, "interceptAngstrom2": intercept, "rSquared": r_squared, "rmseAngstrom2": rmse},
            "regimeDiagnostic": {"diagnosticId": _identity("diffusion-diagnostic", {"windowId": window_id, "status": status}), "status": status, "alpha": alpha, "minimumR2": p["minimum_r_squared"], "alphaRange": [p["alpha_min"], p["alpha_max"]], "originCoverage": _round(coverage)},
            "diffusionEstimate": {"available": estimate is not None, "value": estimate, "unit": "angstrom^2/picosecond", "qualifiedOverSelectedWindow": estimate is not None},
            "coverage": {"msdPointsAvailable": len(times), "fitPoints": len(x), "fitOriginCoverage": _round(coverage)},
            "warnings": [] if estimate is not None else [status],
            "limitations": ["Diffusion is estimated only over the explicitly selected fit window and is not an unconditional long-time bulk diffusion coefficient."],
            "runtimeDiagnostics": {"rawTrajectoryReads": False, "msdRecomputation": False, "frontendFit": False, "automaticWindowOptimization": False},
        })
        fitted = [] if slope is None else [float(slope) * value + float(intercept) for value in x]
        plot = _line_plot("Diffusion fit", x, [("MSD", y), ("persisted fit", fitted)], "lag time / ps", "MSD / angstrom^2")
        return self._finish(payload, plot, f"# Diffusion diagnostic\n\nStatus: {status}. Estimate: {estimate if estimate is not None else 'unavailable'} angstrom^2/ps.")


def _select_analysis_window(
    trajectory: Mapping[str, Any],
    params: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    frames = list(trajectory["frames"])
    mode = str(params.get("window_mode", "whole"))
    times = _physical_times_ps(trajectory, require_constant=False)
    if mode == "frame":
        start = int(params["frame_start"])
        end = int(params["frame_end"])
        if start < 0 or end > len(frames) or start >= end:
            raise _error(
                "TOOL_PARAM_INVALID",
                "TRAJECTORY_ANALYSIS_WINDOW_INVALID",
                "The explicit trajectory frame window is outside the full source.",
                sourceFrameCount=len(frames),
                frameStart=start,
                frameEnd=end,
            )
        selected = frames[start:end]
    elif mode == "time":
        start_time = float(params["time_start_ps"])
        end_time = float(params["time_end_ps"])
        selected = [
            frame
            for frame, time in zip(frames, times, strict=True)
            if start_time <= time < end_time
        ]
    else:
        selected = frames
        if len(frames) > MAX_TRAJECTORY_FRAMES:
            raise _error(
                "TOOL_PARAM_INVALID",
                "TRAJECTORY_ANALYSIS_WINDOW_REQUIRED",
                "An explicit trajectory analysis window is required when the full source exceeds 200 frames.",
                sourceFrameCount=len(frames),
                maximumAnalysisFrames=MAX_TRAJECTORY_FRAMES,
            )
    if not selected:
        raise _error(
            "TOOL_PARAM_INVALID",
            "TRAJECTORY_ANALYSIS_WINDOW_INVALID",
            "The explicit trajectory analysis window contains no frames.",
        )
    if len(selected) > MAX_TRAJECTORY_FRAMES:
        raise _error(
            "TOOL_RESOURCE_LIMIT",
            "TRAJECTORY_ANALYSIS_WINDOW_TOO_LARGE",
            "The explicit trajectory analysis window exceeds the released 200-frame cap.",
            selectedFrameCount=len(selected),
            maximumAnalysisFrames=MAX_TRAJECTORY_FRAMES,
        )
    first_index = int(selected[0]["frame_index"])
    last_index = int(selected[-1]["frame_index"])
    time_by_index = {
        int(frame["frame_index"]): float(time)
        for frame, time in zip(frames, times, strict=True)
    }
    analysis_window = {
        "mode": mode,
        "explicit": mode != "whole",
        "sourceFrameCount": len(frames),
        "selectedFrameCount": len(selected),
        "backendRange": {
            "startFrameInclusive": first_index,
            "endFrameExclusive": last_index + 1,
        },
        "userFacingRange": {
            "firstFrameInclusive": first_index + 1,
            "lastFrameInclusive": last_index + 1,
        },
        "timeRange": {
            "start": _round(time_by_index[first_index]),
            "end": _round(time_by_index[last_index]),
            "unit": "picosecond",
        },
        "sourceTrajectoryId": trajectory["trajectory_id"],
        "silentTruncation": False,
    }
    selected_trajectory = dict(trajectory)
    selected_trajectory["frames"] = selected
    return selected_trajectory, analysis_window


def _physical_times_ps(trajectory: Mapping[str, Any], *, require_constant: bool) -> np.ndarray:
    values = [frame.get("time") for frame in trajectory["frames"]]
    if any(value is None for value in values):
        raise _error("TOOL_INPUT_INVALID", "TRAJECTORY_TIME_MISSING", "Physical frame time is required.")
    scale = {"femtosecond": 0.001, "picosecond": 1.0}.get(trajectory["time"].get("unit"))
    if scale is None:
        raise _error("TOOL_INPUT_INVALID", "TRAJECTORY_TIME_INVALID", "The time unit cannot be converted to picoseconds.")
    result = np.asarray(values, dtype=float) * scale
    delta = np.diff(result)
    if np.any(~np.isfinite(result)) or np.any(delta <= 0):
        raise _error("TOOL_INPUT_INVALID", "TRAJECTORY_TIME_NON_MONOTONIC", "Physical time must be finite and strictly increasing.")
    if require_constant and len(delta) > 1 and not np.allclose(delta, delta[0], rtol=1e-9, atol=1e-12):
        raise _error("TOOL_INPUT_INVALID", "TRAJECTORY_TIME_INVALID", "Irregular physical time is unsupported for production MSD/diffusion.")
    return result


def _unwrapped_cartesian(trajectory: Mapping[str, Any], cell: np.ndarray, pbc: tuple[bool, bool, bool]) -> tuple[np.ndarray, dict[str, Any]]:
    frames = trajectory["frames"]
    cart = np.asarray([_cartesian_positions(trajectory, frame, cell) for frame in frames], dtype=float)
    if trajectory["position_wrapping"] == "unwrapped":
        return cart, {"inputRepresentation": "unwrapped", "ambiguousSteps": 0, "pbcAxes": list(pbc)}
    inverse = np.linalg.inv(cell)
    unwrapped = np.empty_like(cart)
    unwrapped[0] = cart[0]
    ambiguous: list[dict[str, int]] = []
    for frame_index in range(1, len(cart)):
        fractional_delta = (cart[frame_index] - cart[frame_index - 1]) @ inverse
        for axis, periodic in enumerate(pbc):
            if periodic:
                fractional_delta[:, axis] -= np.round(fractional_delta[:, axis])
                bad = np.where(np.abs(fractional_delta[:, axis]) >= UNWRAP_FRACTIONAL_STEP_LIMIT)[0]
                ambiguous.extend({"frameIndex": frame_index, "atomId": int(atom), "axis": axis} for atom in bad)
        unwrapped[frame_index] = unwrapped[frame_index - 1] + fractional_delta @ cell
    if ambiguous:
        raise _error("TOOL_INPUT_INVALID", "UNWRAPPING_AMBIGUOUS", "A frame-to-frame periodic displacement is not uniquely bounded.", cases=ambiguous[:32])
    input_representation = trajectory["position_wrapping"]
    if input_representation == "unknown":
        input_representation = "source_unspecified_minimum_image_continuity"
    return unwrapped, {
        "inputRepresentation": input_representation,
        "sourcePositionWrapping": trajectory["position_wrapping"],
        "continuityAssumption": "bounded_fractional_minimum_image",
        "ambiguousSteps": 0,
        "pbcAxes": list(pbc),
        "fractionalStepLimit": UNWRAP_FRACTIONAL_STEP_LIMIT,
    }


def _cartesian_positions(trajectory: Mapping[str, Any], frame: Mapping[str, Any], cell: np.ndarray) -> np.ndarray:
    values = np.asarray(frame["positions"], dtype=float)
    return values @ cell if trajectory["coordinate_mode"] == "fractional" else values


def _cell(trajectory: Mapping[str, Any], frame: Mapping[str, Any]) -> np.ndarray:
    value = trajectory["fixed_lattice"] if trajectory["lattice_mode"] == "fixed" else frame["lattice"]
    cell = np.asarray(value, dtype=float)
    if cell.shape != (3, 3) or not np.all(np.isfinite(cell)) or abs(float(np.linalg.det(cell))) <= 1e-12:
        raise _error("TOOL_INPUT_INVALID", "TRAJECTORY_CELL_INVALID", "A finite nonsingular cell is required.")
    return cell


def _minimum_image(delta: np.ndarray, cell: np.ndarray, pbc: tuple[bool, bool, bool]) -> np.ndarray:
    vector, _ = find_mic(np.asarray(delta, dtype=float), cell, pbc=pbc)
    return np.asarray(vector, dtype=float)


def _pair_distances(delta: np.ndarray, cell: np.ndarray, pbc: tuple[bool, bool, bool]) -> np.ndarray:
    """Compute bounded batches of minimum-image pair distances."""
    values = np.asarray(delta, dtype=float)
    if values.size == 0:
        return np.empty(0, dtype=float)
    values = values.reshape((-1, 3))
    distances: list[np.ndarray] = []
    for start in range(0, len(values), 16_384):
        minimum_image = _minimum_image(values[start : start + 16_384], cell, pbc)
        distances.append(np.linalg.norm(minimum_image, axis=1))
    return np.concatenate(distances)


def _safe_radius(cell: np.ndarray, pbc: tuple[bool, bool, bool]) -> float:
    inverse = np.linalg.inv(cell)
    spacings = [1.0 / float(np.linalg.norm(inverse[:, axis])) for axis, periodic in enumerate(pbc) if periodic]
    return 0.5 * min(spacings)


def _species_pair(species: list[str], a: Any, b: Any) -> tuple[str, str]:
    if a is None:
        return "*", "*"
    if a not in species or b not in species:
        raise _error("TOOL_PARAM_INVALID", "RDF_SPECIES_NOT_FOUND", "Requested RDF species is absent.")
    return tuple(sorted((str(a), str(b))))


def _line_plot(title: str, x: Any, series: list[tuple[str, Any]], x_title: str, y_title: str) -> dict[str, Any]:
    return {"artifactType": f"{title.lower().replace(' ', '_')}_plot", "schema_version": "phase10n4.trajectory_plot.v1", "data": [{"type": "scatter", "mode": "lines", "name": name, "x": _list(values=x), "y": _list(values=y)} for name, y in series], "layout": {"title": title, "xaxis": {"title": x_title}, "yaxis": {"title": y_title}, "showlegend": True}, "config": {"responsive": True, "displaylogo": False}}


def _input_ref(value: Any) -> str:
    return str(getattr(value, "ref", value.get("ref") if isinstance(value, Mapping) else value))


def _trajectory_error(errors: tuple[str, ...]) -> str:
    mapping = {"TRAJECTORY_ATOM_IDENTITY_MODE_INVALID": "TRAJECTORY_ATOM_IDENTITY_MISSING", "TRAJECTORY_PERIODIC_BOUNDARY_INVALID": "TRAJECTORY_PBC_INVALID", "TRAJECTORY_LATTICE_INVALID": "TRAJECTORY_CELL_INVALID", "TRAJECTORY_ATOM_LIMIT_EXCEEDED": "TRAJECTORY_TOO_LARGE", "TRAJECTORY_FRAME_LIMIT_EXCEEDED": "TRAJECTORY_TOO_LARGE"}
    return mapping.get(errors[0], errors[0]) if errors else "TRAJECTORY_MISSING"


def _optional_species(value: Any) -> str | None:
    if value is None:
        return None
    result = str(value)
    if not result or len(result) > 32 or any(ch not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-_" for ch in result):
        raise _error("TOOL_PARAM_INVALID", "RDF_PARAMETER_INVALID", "Species identity is invalid.")
    return result


def _unknown(params: Mapping[str, Any], allowed: set[str], code: str) -> None:
    unknown = sorted(set(params) - allowed)
    if unknown:
        raise _error("TOOL_PARAM_INVALID", code, "Unknown N4 parameters were rejected.", parameters=unknown)


def _number(params: Mapping[str, Any], key: str, default: float, minimum: float, maximum: float) -> float:
    value = params.get(key, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) or not minimum <= float(value) <= maximum:
        raise _error("TOOL_PARAM_INVALID", "N4_PARAMETER_INVALID", f"{key} is outside its finite bounds.")
    return float(value)


def _integer(params: Mapping[str, Any], key: str, default: int, minimum: int, maximum: int) -> int:
    value = params.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise _error("TOOL_PARAM_INVALID", "N4_PARAMETER_INVALID", f"{key} is outside its integer bounds.")
    return value


def _list(values: Any) -> list[float]:
    return [_round(float(value)) for value in values]


def _round(value: float) -> float:
    return round(float(value), 12)


def _identity(prefix: str, value: Mapping[str, Any]) -> str:
    return f"{prefix}:{content_hash(stable_json_dumps(dict(value)))}"


def _error(code: str, reason: str, message: str, **details: Any) -> ToolExecutionError:
    return ToolExecutionError(code=code, message=message, tool_id="trajectory.analytics", details={"reason": reason, **details})


__all__ = ["TrajectoryDiffusionAdapter", "TrajectoryMsdAdapter", "TrajectoryRdfAdapter"]
