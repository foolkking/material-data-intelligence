from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import median
from typing import Any, Mapping

from scipy.signal import find_peaks

from mdi_artifact_core import ArtifactPayload, content_hash, stable_json_dumps
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError


TOOL_ID = "structure.experimental_xrd_comparison"
TOOL_VERSION = "0.1.0"
ARTIFACT_SCHEMA = "phase10n3.experimental_xrd_comparison.v1"
RESOURCE_SCHEMA = "phase10n3.experimental_xrd_resource.v1"
THEORETICAL_SCHEMA = "phase10e4.xrd_pattern.v1"
THEORETICAL_TOOL = "structure.xrd"
DETECTOR_ID = "mdi.experimental_xrd_peak_detection@1.0.0"
MATCHER_ID = "mdi.xrd_ordered_position_match@1.0.0"
SCIPY_VERSION = "1.17.1"
WAVELENGTH_TOLERANCE_ANGSTROM = 1e-6


@dataclass(frozen=True)
class PreparedExperimentalXrd:
    resource: dict[str, Any]
    theoretical: dict[str, Any]
    theoretical_binding: dict[str, Any]


@dataclass(frozen=True)
class ExperimentalXrdComparisonResult:
    payload: dict[str, Any]
    plot: dict[str, Any]
    summary: str
    recipe: dict[str, Any]


class ExperimentalXrdComparisonAdapter(BaseToolAdapter):
    tool_id = TOOL_ID
    adapter_version = TOOL_VERSION

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedExperimentalXrd:
        normalized = self.normalize_params(params)
        if len(input_refs) != 2:
            raise _error("TOOL_INPUT_INVALID", "EXPERIMENTAL_XRD_MISSING", "N3 requires one experimental Resource and one theoretical XRD Artifact.")
        resource: dict[str, Any] | None = None
        theoretical: dict[str, Any] | None = None
        theoretical_ref = ""
        for input_ref in input_refs:
            ref = _input_ref(input_ref)
            value = context.object_store.get(ref)
            if value is None:
                raise _error("TOOL_INPUT_INVALID", "STALE_EXPERIMENTAL_RESOURCE", "An exact N3 input reference is unavailable.", ref=ref)
            if isinstance(value, Mapping) and value.get("schemaVersion") == RESOURCE_SCHEMA:
                resource = dict(value)
            elif isinstance(value, Mapping) and value.get("schema_version") == THEORETICAL_SCHEMA:
                theoretical = dict(value)
                theoretical_ref = ref
            else:
                raise _error("TOOL_INPUT_INVALID", "THEORETICAL_XRD_CONTRACT_UNSUPPORTED", "N3 input contracts are exact and unsupported inputs are rejected.", ref=ref)
        if resource is None:
            raise _error("TOOL_INPUT_INVALID", "EXPERIMENTAL_XRD_MISSING", "The experimental XRD Resource is missing.")
        if theoretical is None:
            raise _error("TOOL_INPUT_INVALID", "THEORETICAL_XRD_MISSING", "The persisted theoretical XRD Artifact is missing.")
        binding = dict(context.artifact_bindings.get(theoretical_ref) or {})
        _validate_resource(resource, normalized)
        _validate_theoretical(theoretical, binding, context)
        experimental_wavelength = float(resource["wavelength"]["value"])
        theoretical_wavelength = float(theoretical["radiation"]["wavelength_angstrom"])
        if abs(experimental_wavelength - theoretical_wavelength) > WAVELENGTH_TOLERANCE_ANGSTROM:
            raise _error(
                "TOOL_INPUT_INVALID",
                "XRD_WAVELENGTH_MISMATCH",
                "Experimental and theoretical wavelengths are incompatible.",
                experimentalWavelength=experimental_wavelength,
                theoreticalWavelength=theoretical_wavelength,
                unit="angstrom",
            )
        return PreparedExperimentalXrd(resource, theoretical, binding)

    def run(self, prepared: PreparedExperimentalXrd, params: dict[str, Any]) -> ExperimentalXrdComparisonResult:
        normalized = self.normalize_params(params)
        parameter_hash = content_hash(stable_json_dumps(normalized))
        detector_parameters = {
            key: normalized[key]
            for key in ("normalization", "minimum_prominence", "minimum_relative_height", "minimum_peak_separation_deg", "max_detected_peaks")
        }
        detector_parameter_hash = content_hash(stable_json_dumps(detector_parameters))
        matcher_parameters = {
            key: normalized[key]
            for key in ("matching_tolerance_deg", "max_matching_candidates", "max_output_matches")
        }
        matcher_parameter_hash = content_hash(stable_json_dumps(matcher_parameters))

        experimental = _detect_experimental_peaks(prepared.resource, detector_parameters, detector_parameter_hash)
        theoretical = _theoretical_peaks(prepared.theoretical, prepared.theoretical_binding, normalized["max_theoretical_peaks"])
        matches, unmatched_experimental, unmatched_theoretical, candidate_count = _match_peaks(
            experimental["peaks"], theoretical, matcher_parameters, matcher_parameter_hash
        )
        residuals = _residual_summary(matches)
        experimental_count = len(experimental["peaks"])
        theoretical_count = len(theoretical)
        match_count = len(matches)
        warnings = list(experimental["warnings"])
        if match_count == 0:
            warnings.append("XRD_ZERO_MATCHES")
        payload = {
            "artifactType": TOOL_ID,
            "schema_version": ARTIFACT_SCHEMA,
            "tool": {"toolId": TOOL_ID, "toolVersion": self.context.tool_version, "adapterVersion": self.adapter_version},
            "scope": {
                "projectId": self.context.project_id,
                "datasetId": self.context.dataset_id,
                "jobId": self.context.job_id,
                "planId": self.context.plan_id,
                "planVersion": self.context.plan_version,
                "toolCallId": self.context.tool_call_id,
            },
            "experimentalResource": {
                "resourceId": prepared.resource["resourceId"],
                "resourceVersion": prepared.resource["resourceVersion"],
                "resourceHash": prepared.resource["resourceHash"],
                "pointCount": len(prepared.resource["twoTheta"]),
                "twoThetaUnit": "degree",
                "intensitySemantic": prepared.resource["intensitySemantic"],
                "wavelength": float(prepared.resource["wavelength"]["value"]),
                "wavelengthUnit": "angstrom",
            },
            "theoreticalArtifact": {
                "artifactId": prepared.theoretical_binding["artifactId"],
                "artifactChecksum": prepared.theoretical_binding["checksum"],
                "artifactContractVersion": THEORETICAL_SCHEMA,
                "toolId": THEORETICAL_TOOL,
                "toolVersion": str(prepared.theoretical_binding.get("toolVersion") or TOOL_VERSION),
                "structureIdentities": sorted({str(item["structureId"]) for item in theoretical}),
                "wavelength": float(prepared.theoretical["radiation"]["wavelength_angstrom"]),
                "wavelengthUnit": "angstrom",
            },
            "units": {"twoTheta": "degree", "wavelength": "angstrom", "residual": "degree"},
            "normalization": normalized["normalization"],
            "peakDetector": {
                "algorithmId": DETECTOR_ID,
                "library": "scipy",
                "libraryVersion": SCIPY_VERSION,
                "parameters": detector_parameters,
                "parameterHash": detector_parameter_hash,
                "independentOfTheoreticalMatching": True,
            },
            "matcher": {
                "algorithmId": MATCHER_ID,
                "parameters": matcher_parameters,
                "parameterHash": matcher_parameter_hash,
                "oneToOne": True,
                "primaryCost": "absolute_delta_two_theta",
                "intensityAuthority": False,
                "candidateCount": candidate_count,
            },
            "resolvedParameters": normalized,
            "parameterHash": parameter_hash,
            "experimentalSeries": _display_series(experimental["series"], limit=50_000),
            "experimentalPeaks": experimental["peaks"],
            "theoreticalPeaks": theoretical,
            "matches": matches,
            "unmatchedExperimentalPeaks": unmatched_experimental,
            "unmatchedTheoreticalPeaks": unmatched_theoretical,
            "residualSummary": residuals,
            "coverage": {
                "experimentalPoints": len(prepared.resource["twoTheta"]),
                "experimentalDetectedPeaks": experimental_count,
                "theoreticalPeaksConsidered": theoretical_count,
                "matchedPairs": match_count,
                "unmatchedExperimentalPeaks": len(unmatched_experimental),
                "unmatchedTheoreticalPeaks": len(unmatched_theoretical),
                "experimentalMatchedFraction": _round(match_count / experimental_count) if experimental_count else 0.0,
                "theoreticalMatchedFraction": _round(match_count / theoretical_count) if theoretical_count else 0.0,
                "excludedPoints": 0,
            },
            "warnings": sorted(set(warnings)),
            "limitations": [
                "Peak correspondence is reported only under the stated matching tolerance.",
                "This is not Rietveld refinement or definitive phase identification.",
                "Theoretical hkl values are metadata of matched theoretical peaks, not experimental indexing.",
            ],
            "runtimeDiagnostics": {
                "theoreticalXrdReimplementation": False,
                "matchOptimizedPeakDetection": False,
                "automaticPatternShift": False,
                "latticeRefinement": False,
                "structureRefinement": False,
                "rietveldRefinement": False,
                "phaseFractionRefinement": False,
                "automaticPhaseIdentification": False,
            },
            "provenance": {
                "scientificAuthority": "registered_backend_adapter",
                "theoreticalAuthority": f"{THEORETICAL_TOOL}/{THEORETICAL_SCHEMA}",
                "experimentalResourceHash": prepared.resource["resourceHash"],
                "theoreticalArtifactChecksum": prepared.theoretical_binding["checksum"],
                "parameterHash": parameter_hash,
            },
            "security": {"containsHtml": False, "containsJavascript": False, "externalUrls": [], "arbitraryCodeExecution": False},
        }
        encoded = stable_json_dumps(payload).encode("utf-8")
        if len(encoded) > normalized["max_output_bytes"]:
            raise _error("TOOL_RESOURCE_LIMIT", "EXPERIMENTAL_XRD_TOO_LARGE", "N3 Artifact exceeds max_output_bytes.")
        return ExperimentalXrdComparisonResult(payload, _plot_payload(payload), _summary(payload), _recipe(self, payload))

    def export(self, result: ExperimentalXrdComparisonResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
        requested = set(artifact_types) or {ArtifactType.table_json, ArtifactType.plotly_json, ArtifactType.summary_md, ArtifactType.recipe_json}
        payloads: list[ArtifactPayload] = []
        if ArtifactType.table_json in requested:
            payloads.append(ArtifactPayload(ArtifactType.table_json, "experimental_xrd_comparison.json", stable_json_dumps(result.payload), "application/json"))
        if ArtifactType.plotly_json in requested:
            payloads.append(ArtifactPayload(ArtifactType.plotly_json, "experimental_xrd_comparison_plot.json", stable_json_dumps(result.plot), "application/json"))
        if ArtifactType.summary_md in requested:
            payloads.append(ArtifactPayload(ArtifactType.summary_md, "summary.md", result.summary, "text/markdown"))
        if ArtifactType.recipe_json in requested:
            payloads.append(ArtifactPayload(ArtifactType.recipe_json, "recipe.json", stable_json_dumps(result.recipe), "application/json"))
        return self.export_payloads(payloads, provenance={
            "artifactType": TOOL_ID,
            "schemaVersion": ARTIFACT_SCHEMA,
            "experimentalResourceHash": result.payload["experimentalResource"]["resourceHash"],
            "theoreticalArtifactChecksum": result.payload["theoreticalArtifact"]["artifactChecksum"],
            "parameterHash": result.payload["parameterHash"],
            "scientificAuthority": "registered_backend_adapter",
        })

    @staticmethod
    def normalize_params(params: Mapping[str, Any]) -> dict[str, Any]:
        allowed = {
            "normalization", "minimum_prominence", "minimum_relative_height",
            "minimum_peak_separation_deg", "max_detected_peaks", "matching_tolerance_deg",
            "max_matching_candidates", "max_theoretical_peaks", "max_output_matches",
            "max_output_bytes",
        }
        unknown = sorted(set(params) - allowed)
        if unknown:
            raise _error("TOOL_PARAM_INVALID", "XRD_PEAK_DETECTION_PARAMETER_INVALID", "Unknown N3 parameters were rejected.", parameters=unknown)
        normalization = str(params.get("normalization", "max_to_1"))
        if normalization not in {"none", "max_to_1", "max_to_100"}:
            raise _error("TOOL_PARAM_INVALID", "XRD_PEAK_DETECTION_PARAMETER_INVALID", "Unsupported normalization.")
        return {
            "normalization": normalization,
            "minimum_prominence": _number(params, "minimum_prominence", 0.05, 0.0, 1.0),
            "minimum_relative_height": _number(params, "minimum_relative_height", 0.0, 0.0, 1.0),
            "minimum_peak_separation_deg": _number(params, "minimum_peak_separation_deg", 0.1, 0.0, 10.0),
            "max_detected_peaks": _integer(params, "max_detected_peaks", 10_000, 1, 10_000),
            "matching_tolerance_deg": _number(params, "matching_tolerance_deg", 0.15, 0.001, 2.0),
            "max_matching_candidates": _integer(params, "max_matching_candidates", 200_000, 1, 200_000),
            "max_theoretical_peaks": _integer(params, "max_theoretical_peaks", 20_000, 1, 20_000),
            "max_output_matches": _integer(params, "max_output_matches", 10_000, 1, 10_000),
            "max_output_bytes": _integer(params, "max_output_bytes", 32 * 1024 * 1024, 1024, 32 * 1024 * 1024),
        }


def _input_ref(value: Any) -> str:
    return str(getattr(value, "ref", value.get("ref") if isinstance(value, Mapping) else ""))


def _validate_resource(resource: Mapping[str, Any], params: Mapping[str, Any]) -> None:
    required = {"schemaVersion", "resourceId", "resourceVersion", "resourceHash", "xAxis", "twoTheta", "intensity", "intensitySemantic", "wavelength"}
    if set(resource) - (required | {"metadata"}) or not required.issubset(resource):
        raise _error("TOOL_INPUT_INVALID", "EXPERIMENTAL_XRD_INVALID_AXIS", "Experimental XRD Resource fields are strict.")
    axis = resource.get("xAxis")
    wavelength = resource.get("wavelength")
    if axis != {"kind": "two_theta", "unit": "degree"}:
        raise _error("TOOL_INPUT_INVALID", "EXPERIMENTAL_XRD_INVALID_AXIS", "Only explicit degree two_theta is supported.")
    if not isinstance(wavelength, Mapping) or set(wavelength) != {"value", "unit"}:
        raise _error("TOOL_INPUT_INVALID", "XRD_WAVELENGTH_MISSING", "Explicit wavelength metadata is required.")
    if wavelength.get("unit") != "angstrom" or not _finite_positive(wavelength.get("value")):
        raise _error("TOOL_INPUT_INVALID", "XRD_WAVELENGTH_INVALID", "Wavelength must be finite positive Angstrom.")
    if resource.get("intensitySemantic") not in {"counts", "relative_intensity", "normalized_relative_intensity", "arbitrary_relative_unit"}:
        raise _error("TOOL_INPUT_INVALID", "EXPERIMENTAL_XRD_INVALID_INTENSITY", "Intensity semantics are unsupported.")
    x = resource.get("twoTheta")
    y = resource.get("intensity")
    if not isinstance(x, list) or not isinstance(y, list) or len(x) != len(y) or len(x) < 3:
        raise _error("TOOL_INPUT_INVALID", "EXPERIMENTAL_XRD_INVALID_AXIS", "Experimental arrays must have equal length and at least three points.")
    if len(x) > 200_000:
        raise _error("TOOL_RESOURCE_LIMIT", "EXPERIMENTAL_XRD_TOO_LARGE", "Experimental point cap exceeded.")
    if any(not _finite(item) for item in x + y):
        raise _error("TOOL_INPUT_INVALID", "EXPERIMENTAL_XRD_NON_FINITE", "Experimental arrays contain non-finite values.")
    if any(float(left) >= float(right) for left, right in zip(x, x[1:])):
        raise _error("TOOL_INPUT_INVALID", "EXPERIMENTAL_XRD_INVALID_AXIS", "twoTheta must be strictly increasing; sorting and duplicate merging are not implicit.")
    if min(float(item) for item in x) < 0.0 or max(float(item) for item in x) > 180.0:
        raise _error("TOOL_INPUT_INVALID", "EXPERIMENTAL_XRD_INVALID_AXIS", "twoTheta must be within 0 to 180 degree.")
    if any(float(item) < 0.0 for item in y) or max(float(item) for item in y) <= 0.0:
        raise _error("TOOL_INPUT_INVALID", "EXPERIMENTAL_XRD_INVALID_INTENSITY", "Intensity must be non-negative and not zero-only.")
    expected_hash = content_hash(stable_json_dumps(_resource_hash_material(resource)))
    if str(resource.get("resourceHash")) != expected_hash:
        raise _error("TOOL_INPUT_INVALID", "STALE_EXPERIMENTAL_RESOURCE", "Experimental Resource hash does not match its exact scientific content.")


def _resource_hash_material(resource: Mapping[str, Any]) -> dict[str, Any]:
    return {key: resource[key] for key in ("schemaVersion", "resourceId", "resourceVersion", "xAxis", "twoTheta", "intensity", "intensitySemantic", "wavelength")}


def _validate_theoretical(payload: Mapping[str, Any], binding: Mapping[str, Any], context: ToolExecutionContext) -> None:
    if payload.get("artifactType") != THEORETICAL_TOOL or payload.get("schema_version") != THEORETICAL_SCHEMA:
        raise _error("TOOL_INPUT_INVALID", "THEORETICAL_XRD_CONTRACT_UNSUPPORTED", "The theoretical XRD contract is unsupported.")
    if binding.get("artifactContractVersion") != THEORETICAL_SCHEMA or not binding.get("artifactId") or not binding.get("checksum"):
        raise _error("TOOL_INPUT_INVALID", "THEORETICAL_XRD_CHECKSUM_MISMATCH", "Exact theoretical Artifact binding metadata is required.")
    if binding.get("projectId") not in {None, context.project_id}:
        raise _error("TOOL_INPUT_INVALID", "FOREIGN_PROJECT_SOURCE", "Theoretical Artifact belongs to another Project.")
    if binding.get("jobId") not in {None, context.job_id}:
        raise _error("TOOL_INPUT_INVALID", "FOREIGN_JOB_SOURCE", "Theoretical Artifact belongs to another Job.")
    if binding.get("payloadChecksum") not in {None, content_hash(stable_json_dumps(payload))}:
        raise _error("TOOL_INPUT_INVALID", "THEORETICAL_XRD_CHECKSUM_MISMATCH", "Theoretical payload checksum does not match its binding.")
    radiation = payload.get("radiation")
    pattern = payload.get("pattern")
    if not isinstance(radiation, Mapping) or not _finite_positive(radiation.get("wavelength_angstrom")):
        raise _error("TOOL_INPUT_INVALID", "XRD_WAVELENGTH_INVALID", "The theoretical wavelength is invalid.")
    if not isinstance(pattern, Mapping) or not isinstance(pattern.get("peaks"), list):
        raise _error("TOOL_INPUT_INVALID", "THEORETICAL_XRD_CONTRACT_UNSUPPORTED", "Theoretical peak data is missing.")


def _normalize(values: list[float], method: str) -> list[float]:
    maximum = max(values)
    if method == "none":
        return [_round(value) for value in values]
    scale = 1.0 if method == "max_to_1" else 100.0
    return [_round(value / maximum * scale) for value in values]


def _detect_experimental_peaks(resource: Mapping[str, Any], params: Mapping[str, Any], parameter_hash: str) -> dict[str, Any]:
    x = [float(item) for item in resource["twoTheta"]]
    original = [float(item) for item in resource["intensity"]]
    normalized = _normalize(original, str(params["normalization"]))
    detector_scale = 100.0 if params["normalization"] == "max_to_100" else (max(normalized) if params["normalization"] == "none" else 1.0)
    prominence = float(params["minimum_prominence"]) * detector_scale
    height = float(params["minimum_relative_height"]) * detector_scale
    indices, properties = find_peaks(normalized, prominence=prominence, height=height)
    candidates = [
        {
            "sourceIndex": int(index),
            "twoTheta": x[int(index)],
            "originalIntensity": original[int(index)],
            "normalizedIntensity": normalized[int(index)],
            "prominence": float(properties["prominences"][position]),
        }
        for position, index in enumerate(indices)
    ]
    candidates.sort(key=lambda item: (-item["prominence"], -item["normalizedIntensity"], item["twoTheta"], item["sourceIndex"]))
    retained: list[dict[str, Any]] = []
    separation = float(params["minimum_peak_separation_deg"])
    for candidate in candidates:
        if all(abs(candidate["twoTheta"] - item["twoTheta"]) >= separation for item in retained):
            retained.append(candidate)
    if len(retained) > int(params["max_detected_peaks"]):
        raise _error("TOOL_RESOURCE_LIMIT", "XRD_PEAK_LIMIT_EXCEEDED", "Detected peak cap exceeded.")
    retained.sort(key=lambda item: (item["twoTheta"], -item["prominence"], item["sourceIndex"]))
    peaks = []
    for ordinal, item in enumerate(retained):
        identity = content_hash(stable_json_dumps({
            "resourceHash": resource["resourceHash"], "detector": DETECTOR_ID,
            "parameterHash": parameter_hash, "ordinal": ordinal, "twoTheta": _round(item["twoTheta"]),
        }))
        peaks.append({
            "peakId": f"experimental-peak:{identity}", "ordinal": ordinal,
            **{key: _round(value) if isinstance(value, float) else value for key, value in item.items()},
            "twoThetaUnit": "degree", "detectorParameterHash": parameter_hash,
        })
    return {
        "series": {"twoTheta": [_round(item) for item in x], "originalIntensity": [_round(item) for item in original], "normalizedIntensity": normalized},
        "peaks": peaks,
        "warnings": [],
    }


def _theoretical_peaks(payload: Mapping[str, Any], binding: Mapping[str, Any], limit: int) -> list[dict[str, Any]]:
    source = list(payload["pattern"]["peaks"])
    if len(source) > limit:
        raise _error("TOOL_RESOURCE_LIMIT", "XRD_PEAK_LIMIT_EXCEEDED", "Theoretical peak cap exceeded.")
    canonical = sorted(source, key=lambda item: (float(item["two_theta_deg"]), -float(item["intensity"]), float(item["d_spacing_angstrom"]), str(item["structureId"]), stable_json_dumps(item.get("hkls") or [])))
    occurrences: dict[str, int] = {}
    result: list[dict[str, Any]] = []
    for item in canonical:
        material = {
            "artifactChecksum": binding["checksum"], "structureId": str(item["structureId"]),
            "twoTheta": _round(float(item["two_theta_deg"])), "intensity": _round(float(item["intensity"])),
            "dSpacing": _round(float(item["d_spacing_angstrom"])), "hkls": item.get("hkls") or [],
        }
        key = stable_json_dumps(material)
        occurrence = occurrences.get(key, 0)
        occurrences[key] = occurrence + 1
        peak_id = content_hash(stable_json_dumps({**material, "occurrence": occurrence}))
        result.append({
            "peakId": f"theoretical-peak:{peak_id}", "structureId": material["structureId"],
            "twoTheta": material["twoTheta"], "relativeIntensity": material["intensity"],
            "dSpacing": material["dSpacing"], "dSpacingUnit": "angstrom", "hkls": material["hkls"],
            "twoThetaUnit": "degree", "sourceArtifactId": str(binding["artifactId"]),
            "sourceArtifactChecksum": str(binding["checksum"]),
        })
    return result


def _match_peaks(experimental: list[dict[str, Any]], theoretical: list[dict[str, Any]], params: Mapping[str, Any], parameter_hash: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], int]:
    tolerance = float(params["matching_tolerance_deg"])
    candidates: list[tuple[float, str, str, int, int]] = []
    left = 0
    for exp_index, exp in enumerate(experimental):
        while left < len(theoretical) and float(theoretical[left]["twoTheta"]) < float(exp["twoTheta"]) - tolerance:
            left += 1
        index = left
        while index < len(theoretical) and float(theoretical[index]["twoTheta"]) <= float(exp["twoTheta"]) + tolerance:
            delta = float(exp["twoTheta"]) - float(theoretical[index]["twoTheta"])
            candidates.append((abs(delta), str(exp["peakId"]), str(theoretical[index]["peakId"]), exp_index, index))
            if len(candidates) > int(params["max_matching_candidates"]):
                raise _error("TOOL_RESOURCE_LIMIT", "XRD_MATCH_CANDIDATE_LIMIT_EXCEEDED", "Matching candidate cap exceeded.")
            index += 1
    candidates.sort()
    used_exp: set[int] = set()
    used_theory: set[int] = set()
    matches: list[dict[str, Any]] = []
    for _, _, _, exp_index, theory_index in candidates:
        if exp_index in used_exp or theory_index in used_theory:
            continue
        if len(matches) >= int(params["max_output_matches"]):
            raise _error("TOOL_RESOURCE_LIMIT", "XRD_MATCH_CANDIDATE_LIMIT_EXCEEDED", "Output match cap exceeded.")
        used_exp.add(exp_index)
        used_theory.add(theory_index)
        exp = experimental[exp_index]
        theory = theoretical[theory_index]
        delta = _round(float(exp["twoTheta"]) - float(theory["twoTheta"]))
        match_id = content_hash(stable_json_dumps({"experimentalPeakId": exp["peakId"], "theoreticalPeakId": theory["peakId"], "parameterHash": parameter_hash}))
        matches.append({
            "matchId": f"xrd-match:{match_id}", "experimentalPeakId": exp["peakId"],
            "theoreticalPeakId": theory["peakId"], "experimentalTwoTheta": exp["twoTheta"],
            "experimentalIntensity": exp["normalizedIntensity"], "theoreticalTwoTheta": theory["twoTheta"],
            "theoreticalIntensity": theory["relativeIntensity"], "theoreticalHkls": theory["hkls"],
            "signedDeltaTwoTheta": delta, "absoluteDeltaTwoTheta": _round(abs(delta)),
            "twoThetaUnit": "degree", "matchingTolerance": tolerance, "matchingAlgorithm": MATCHER_ID,
            "matchingParameterHash": parameter_hash,
        })
    matches.sort(key=lambda item: (item["experimentalTwoTheta"], item["theoreticalTwoTheta"], item["matchId"]))
    return matches, [item for index, item in enumerate(experimental) if index not in used_exp], [item for index, item in enumerate(theoretical) if index not in used_theory], len(candidates)


def _residual_summary(matches: list[dict[str, Any]]) -> dict[str, Any]:
    if not matches:
        return {"matchedCount": 0, "meanSignedDeltaTwoTheta": None, "maeDeltaTwoTheta": None, "rmseDeltaTwoTheta": None, "maxAbsoluteDeltaTwoTheta": None, "medianAbsoluteDeltaTwoTheta": None, "unit": "degree"}
    signed = [float(item["signedDeltaTwoTheta"]) for item in matches]
    absolute = [abs(item) for item in signed]
    return {
        "matchedCount": len(matches), "meanSignedDeltaTwoTheta": _round(sum(signed) / len(signed)),
        "maeDeltaTwoTheta": _round(sum(absolute) / len(absolute)),
        "rmseDeltaTwoTheta": _round(math.sqrt(sum(item * item for item in signed) / len(signed))),
        "maxAbsoluteDeltaTwoTheta": _round(max(absolute)), "medianAbsoluteDeltaTwoTheta": _round(median(absolute)), "unit": "degree",
    }


def _plot_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    series = payload["experimentalSeries"]
    theory = payload["theoreticalPeaks"]
    return {
        "artifactType": "structure.experimental_xrd_comparison_plot",
        "schema_version": "phase10n3.experimental_xrd_comparison_plot.v1",
        "tool_id": TOOL_ID,
        "x_axis": {"label": "2theta (degree)", "unit": "degree"},
        "series": [
            {"name": "Experimental", "kind": "line", "x": series["twoTheta"], "y": series["normalizedIntensity"]},
            {"name": "Theoretical peaks", "kind": "stick", "x": [item["twoTheta"] for item in theory], "y": [item["relativeIntensity"] for item in theory]},
        ],
        "markers": {"experimentalPeaks": payload["experimentalPeaks"], "matches": payload["matches"]},
        "security": payload["security"],
    }


def _display_series(series: Mapping[str, list[float]], *, limit: int) -> dict[str, Any]:
    two_theta = series["twoTheta"]
    intensity = series["normalizedIntensity"]
    if len(two_theta) <= limit:
        return {"twoTheta": two_theta, "normalizedIntensity": intensity, "sourcePointCount": len(two_theta), "displayDownsampled": False}
    last = len(two_theta) - 1
    indices = sorted({round(index * last / (limit - 1)) for index in range(limit)})
    return {
        "twoTheta": [two_theta[index] for index in indices],
        "normalizedIntensity": [intensity[index] for index in indices],
        "sourcePointCount": len(two_theta),
        "displayDownsampled": True,
    }


def _summary(payload: Mapping[str, Any]) -> str:
    coverage = payload["coverage"]
    residual = payload["residualSummary"]
    return "\n".join([
        "# Experimental XRD Comparison", "", "## Correspondence",
        f"- tolerance: +/- {payload['matcher']['parameters']['matching_tolerance_deg']} degree 2theta",
        f"- matched pairs: {coverage['matchedPairs']}",
        f"- unmatched experimental peaks: {coverage['unmatchedExperimentalPeaks']}",
        f"- unmatched theoretical peaks: {coverage['unmatchedTheoreticalPeaks']}",
        f"- MAE delta 2theta: {residual['maeDeltaTwoTheta']}", "", "## Limit",
        "This is a bounded peak-correspondence comparison, not Rietveld refinement or definitive phase identification.", "",
    ])


def _recipe(adapter: ExperimentalXrdComparisonAdapter, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "0.1", "recipeId": f"recipe_{adapter.context.tool_call_id}",
        "name": "Experimental XRD Comparison", "toolId": TOOL_ID, "toolVersion": adapter.context.tool_version,
        "inputs": {"experimentalResource": payload["experimentalResource"], "theoreticalArtifact": payload["theoreticalArtifact"]},
        "params": payload["resolvedParameters"], "dependencyBindings": [{"artifactId": payload["theoreticalArtifact"]["artifactId"], "checksum": payload["theoreticalArtifact"]["artifactChecksum"]}],
        "detector": payload["peakDetector"], "matcher": payload["matcher"], "declarative": True,
        "executionAuthority": False, "createsPlan": False, "createsJob": False, "enqueuesTool": False,
    }


def _number(params: Mapping[str, Any], key: str, default: float, minimum: float, maximum: float) -> float:
    value = params.get(key, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) or not minimum <= float(value) <= maximum:
        code = "XRD_MATCH_TOLERANCE_INVALID" if key == "matching_tolerance_deg" else "XRD_PEAK_DETECTION_PARAMETER_INVALID"
        raise _error("TOOL_PARAM_INVALID", code, f"{key} is outside its finite bounds.")
    return float(value)


def _integer(params: Mapping[str, Any], key: str, default: int, minimum: int, maximum: int) -> int:
    value = params.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise _error("TOOL_PARAM_INVALID", "XRD_PEAK_DETECTION_PARAMETER_INVALID", f"{key} is outside its integer bounds.")
    return value


def _finite(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(float(value))


def _finite_positive(value: Any) -> bool:
    return _finite(value) and float(value) > 0.0


def _round(value: float) -> float:
    return round(float(value), 12)


def _error(code: str, error_type: str, message: str, **details: Any) -> ToolExecutionError:
    return ToolExecutionError(code=code, message=message, tool_id=TOOL_ID, details={"errorType": error_type, **details})
