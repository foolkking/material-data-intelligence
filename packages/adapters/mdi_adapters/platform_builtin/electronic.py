from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping

from mdi_artifact_core import ArtifactPayload, content_hash, stable_json_dumps
from mdi_artifact_core.electronic_contract import (
    BAND_ARTIFACT_SCHEMA,
    BAND_RESOURCE_SCHEMA,
    DOS_ARTIFACT_SCHEMA,
    DOS_RESOURCE_SCHEMA,
    electronic_resource_hash,
    validate_electronic_band_resource,
    validate_electronic_dos_resource,
)
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError


BAND_TOOL = "electronic.band_structure"
DOS_TOOL = "electronic.dos"
TOOL_VERSION = "0.1.0"
BAND_GAP_ALGORITHM = "mdi.supplied_band_gap_scan@1.0.0"
MAX_ARTIFACT_BYTES = 64 * 1024 * 1024
PYMATGEN_VERSION = "2026.5.4"
NUMPY_VERSION = "2.4.6"
SCIPY_VERSION = "1.17.1"


@dataclass(frozen=True)
class ElectronicResult:
    payload: dict[str, Any]
    plot: dict[str, Any]
    summary: str
    recipe: dict[str, Any]


class _ElectronicAdapter(BaseToolAdapter):
    schema_version: str
    resource_schema: str

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> dict[str, Any]:
        self.normalize_params(params)
        if len(input_refs) != 1:
            raise _error("TOOL_INPUT_INVALID", "ELECTRONIC_RESOURCE_MISSING", "Exactly one supplied electronic resource is required.")
        ref = _ref(input_refs[0])
        value = context.object_store.get(ref)
        if not isinstance(value, Mapping) and isinstance(getattr(value, "payload", None), Mapping):
            value = value.payload
        if not isinstance(value, Mapping):
            raise _error("TOOL_INPUT_INVALID", "STALE_ELECTRONIC_RESOURCE", "The exact electronic resource is unavailable.", ref=ref)
        resource = dict(value)
        validation = self.validate_resource(resource)
        if not validation.valid:
            raise _error("TOOL_INPUT_INVALID", validation.errors[0], "The supplied electronic resource contract is invalid.", errors=list(validation.errors))
        return resource

    def export(self, result: ElectronicResult, artifact_types: list[ArtifactType]) -> list[Artifact]:
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
        return self.export_payloads(payloads, provenance={
            "schemaVersion": self.schema_version,
            "electronicResourceHash": result.payload["sourceResource"]["resourceHash"],
            "calculationIdentity": result.payload["sourceResource"]["calculationIdentity"],
            "parameterHash": result.payload["parameterHash"],
            "scientificAuthority": "supplied_electronic_output_via_registered_backend_adapter",
        })

    def _base(self, resource: Mapping[str, Any], params: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "artifactType": self.tool_id,
            "schemaVersion": self.schema_version,
            "tool": {"toolId": self.tool_id, "toolVersion": self.context.tool_version, "adapterVersion": self.adapter_version},
            "scope": {"projectId": self.context.project_id, "datasetId": self.context.dataset_id, "jobId": self.context.job_id, "planId": self.context.plan_id, "planVersion": self.context.plan_version, "toolCallId": self.context.tool_call_id},
            "sourceResource": {
                "resourceId": resource["resourceId"], "resourceVersion": resource["resourceVersion"],
                "resourceHash": resource["resourceHash"], "resourceContract": resource["schemaVersion"],
                "calculationIdentity": resource["calculationIdentity"], "structureIdentity": resource.get("structureIdentity"),
                "sourceMetadata": resource.get("sourceMetadata", {}),
            },
            "energy": {"unit": "eV", "sourceUnit": resource["energyUnit"], "reference": resource["energyReference"], "fermiEnergyEv": resource.get("fermiEnergyEv"), "frontendAlignmentAuthority": False},
            "spin": {"mode": resource["spinMode"], "channels": ["none"] if resource["spinMode"] == "non_spin_polarized" else ["up", "down"], "frontendMergeAuthority": False},
            "resolvedParameters": dict(params),
            "parameterHash": content_hash(stable_json_dumps(params)),
            "auditedLockedStack": {"pymatgen": PYMATGEN_VERSION, "numpy": NUMPY_VERSION, "scipy": SCIPY_VERSION},
            "warnings": [], "limitations": [],
            "security": {"containsHtml": False, "containsJavascript": False, "externalUrls": [], "arbitraryCodeExecution": False, "dftExecution": False, "externalScientificNetwork": False},
        }

    def _finish(self, payload: dict[str, Any], plot: dict[str, Any], summary: str) -> ElectronicResult:
        if len(stable_json_dumps(payload).encode("utf-8")) > MAX_ARTIFACT_BYTES:
            raise _error("TOOL_RESOURCE_LIMIT", "ELECTRONIC_RESOURCE_TOO_LARGE", "Electronic Artifact exceeds the output cap.")
        recipe = self.recipe_payload(name=f"{self.tool_id} supplied-output provenance", params=payload["resolvedParameters"], artifact_types=[ArtifactType.table_json, ArtifactType.plotly_json])
        recipe.update({
            "executionAuthorized": False,
            "sourceResource": dict(payload["sourceResource"]),
            "energySemantics": dict(payload["energy"]),
            "spinSemantics": dict(payload["spin"]),
            "parameterHash": payload["parameterHash"],
            "electronicCalculationExecution": False,
        })
        return ElectronicResult(payload, plot, summary, recipe)

    @staticmethod
    def normalize_params(params: Mapping[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @staticmethod
    def validate_resource(resource: Mapping[str, Any]):
        raise NotImplementedError


class ElectronicBandStructureAdapter(_ElectronicAdapter):
    tool_id = BAND_TOOL
    adapter_version = TOOL_VERSION
    schema_version = BAND_ARTIFACT_SCHEMA
    resource_schema = BAND_RESOURCE_SCHEMA
    validate_resource = staticmethod(validate_electronic_band_resource)

    @staticmethod
    def normalize_params(params: Mapping[str, Any]) -> dict[str, Any]:
        allowed = {"energy_reference", "gap_threshold_ev", "occupancy_threshold", "energy_tolerance_ev", "max_plot_points"}
        _unknown(params, allowed, "BAND_PARAMETER_INVALID")
        reference = str(params.get("energy_reference", "source"))
        if reference not in {"source", "fermi"}:
            raise _error("TOOL_PARAM_INVALID", "BAND_PARAMETER_INVALID", "Unsupported energy reference.")
        return {
            "energy_reference": reference,
            "gap_threshold_ev": _number(params, "gap_threshold_ev", 1e-5, 0.0, 1.0),
            "occupancy_threshold": _number(params, "occupancy_threshold", 0.5, 0.0, 1.0),
            "energy_tolerance_ev": _number(params, "energy_tolerance_ev", 1e-8, 0.0, 1e-3),
            "max_plot_points": _integer(params, "max_plot_points", 500_000, 1, 500_000),
        }

    def run(self, resource: dict[str, Any], params: dict[str, Any]) -> ElectronicResult:
        p = self.normalize_params(params)
        if p["energy_reference"] == "fermi" and resource.get("fermiEnergyEv") is None:
            raise _error("TOOL_INPUT_INVALID", "ELECTRONIC_FERMI_MISSING", "Fermi-referenced output requires an explicit supplied Fermi energy.")
        base = self._base(resource, p)
        gap = _band_gap(resource, p)
        states = []
        kpoints = resource["kpoints"]
        shift = float(resource.get("fermiEnergyEv") or 0.0) if p["energy_reference"] == "fermi" else 0.0
        bands = []
        for band in sorted(resource["bands"], key=lambda item: (_spin_order(item["spinChannel"]), item["bandId"])):
            energies = [_round(float(value) - shift) for value in band["energiesEv"]]
            band_identity = _identity("band", {"resourceHash": resource["resourceHash"], "spin": band["spinChannel"], "bandId": band["bandId"]})
            bands.append({"bandIdentity": band_identity, "bandId": band["bandId"], "spinChannel": band["spinChannel"], "energiesEv": energies})
            states.extend({"stateId": _identity("band-state", {"bandIdentity": band_identity, "kpointId": point["kpointId"]}), "bandIdentity": band_identity, "bandId": band["bandId"], "spinChannel": band["spinChannel"], "kpointId": point["kpointId"], "energyEv": energy} for point, energy in zip(kpoints, energies, strict=True))
        base.update({
            "algorithm": {"algorithmId": BAND_GAP_ALGORITHM, "version": "1.0.0", "sourceOrderingPreserved": True, "interpolation": False},
            "kpoints": kpoints,
            "pathSegments": resource["pathSegments"],
            "bands": bands,
            "states": states,
            "gap": gap,
            "coverage": {"kpointCount": len(kpoints), "bandCount": len(bands), "stateCount": len(states), "spinChannels": sorted({item["spinChannel"] for item in bands}, key=_spin_order), "fermiAvailable": resource.get("fermiEnergyEv") is not None, "pathSegmentCount": len(resource["pathSegments"])},
            "limitations": ["Band energies and gap facts are derived only from the supplied sampled electronic data; the platform performs no DFT, GW correction, interpolation or projected-band analysis."],
            "runtimeDiagnostics": {"platformDftExecution": False, "bandGenerationFromStructure": False, "frontendBandGapRecomputation": False, "fermiSurfaceGeneration": False},
        })
        plot = _band_plot(base)
        gap_text = "unavailable" if gap["valueEv"] is None else f"{gap['valueEv']} eV ({gap['classification']})"
        return self._finish(base, plot, f"# Supplied electronic band structure\n\nSampled-data gap: {gap_text}. No electronic calculation was executed by the platform.")


class ElectronicDosAdapter(_ElectronicAdapter):
    tool_id = DOS_TOOL
    adapter_version = TOOL_VERSION
    schema_version = DOS_ARTIFACT_SCHEMA
    resource_schema = DOS_RESOURCE_SCHEMA
    validate_resource = staticmethod(validate_electronic_dos_resource)

    @staticmethod
    def normalize_params(params: Mapping[str, Any]) -> dict[str, Any]:
        allowed = {"energy_reference", "include_element_projections", "include_orbital_projections", "max_projection_channels", "max_plot_points"}
        _unknown(params, allowed, "DOS_PARAMETER_INVALID")
        reference = str(params.get("energy_reference", "source"))
        if reference not in {"source", "fermi"}:
            raise _error("TOOL_PARAM_INVALID", "DOS_PARAMETER_INVALID", "Unsupported energy reference.")
        return {
            "energy_reference": reference,
            "include_element_projections": _boolean(params, "include_element_projections", True),
            "include_orbital_projections": _boolean(params, "include_orbital_projections", True),
            "max_projection_channels": _integer(params, "max_projection_channels", 512, 0, 512),
            "max_plot_points": _integer(params, "max_plot_points", 500_000, 1, 500_000),
        }

    def run(self, resource: dict[str, Any], params: dict[str, Any]) -> ElectronicResult:
        p = self.normalize_params(params)
        if p["energy_reference"] == "fermi" and resource.get("fermiEnergyEv") is None:
            raise _error("TOOL_INPUT_INVALID", "ELECTRONIC_FERMI_MISSING", "Fermi-referenced output requires an explicit supplied Fermi energy.")
        shift = float(resource.get("fermiEnergyEv") or 0.0) if p["energy_reference"] == "fermi" else 0.0
        energies = [_round(float(value) - shift) for value in resource["energiesEv"]]
        projections = [item for item in resource.get("projections", []) if (item["projectionKind"] == "element" and p["include_element_projections"]) or (item["projectionKind"] == "orbital" and p["include_orbital_projections"])]
        projections = sorted(projections, key=lambda item: (item["projectionKind"], item["label"], _spin_order(item["spinChannel"]), item["channelId"]))
        if len(projections) > p["max_projection_channels"]:
            raise _error("TOOL_RESOURCE_LIMIT", "DOS_LIMIT_EXCEEDED", "Requested projections exceed the parameter cap.")
        base = self._base(resource, p)
        total = [_dos_channel(item, resource["resourceHash"]) for item in sorted(resource["totalDos"], key=lambda item: (_spin_order(item["spinChannel"]), item["channelId"]))]
        projected = [_dos_channel(item, resource["resourceHash"]) for item in projections]
        base.update({
            "algorithm": {"algorithmId": "mdi.supplied_dos_validation@1.0.0", "version": "1.0.0", "interpolation": False, "smoothing": False, "projectionSummation": False},
            "dosUnitSemantic": resource["dosUnitSemantic"],
            "energiesEv": energies,
            "energyPointIds": [_identity("dos-point", {"resourceHash": resource["resourceHash"], "index": index, "energyEv": value}) for index, value in enumerate(energies)],
            "totalDos": total,
            "projections": projected,
            "projectionCompleteness": resource["projectionCompleteness"],
            "coverage": {"energyPointCount": len(energies), "totalChannelCount": len(total), "projectionCount": len(projected), "providedElements": sorted({item["label"] for item in projected if item.get("projectionKind") == "element"}), "providedOrbitals": sorted({item["label"] for item in projected if item.get("projectionKind") == "orbital"})},
            "limitations": ["DOS values are supplied data. Partial or unknown projection coverage describes only provided channels; no total, electron count, bonding, magnetism or band character is inferred."],
            "runtimeDiagnostics": {"dosGenerationFromStructure": False, "dosGenerationFromBands": False, "frontendDosRecomputation": False, "frontendSpinMerging": False},
        })
        return self._finish(base, _dos_plot(base), f"# Supplied electronic DOS\n\n{len(energies)} energy points; projection completeness {resource['projectionCompleteness']}. No electronic calculation was executed by the platform.")


def _band_gap(resource: Mapping[str, Any], params: Mapping[str, Any]) -> dict[str, Any]:
    fermi = resource.get("fermiEnergyEv")
    occupation_complete = all(isinstance(item.get("occupations"), list) for item in resource["bands"])
    if not occupation_complete and fermi is None:
        return {"status": "UNAVAILABLE", "valueEv": None, "vbm": None, "cbm": None, "directness": "UNAVAILABLE", "classification": "CLASSIFICATION_UNAVAILABLE", "algorithmId": BAND_GAP_ALGORITHM}
    occupied: list[dict[str, Any]] = []
    unoccupied: list[dict[str, Any]] = []
    crossing = False
    for band in resource["bands"]:
        values = [float(value) for value in band["energiesEv"]]
        if fermi is not None and min(values) <= float(fermi) + params["energy_tolerance_ev"] and max(values) >= float(fermi) - params["energy_tolerance_ev"]:
            crossing = True
        for index, energy in enumerate(values):
            state = {"energyEv": _round(energy), "kpointId": resource["kpoints"][index]["kpointId"], "bandId": band["bandId"], "spinChannel": band["spinChannel"]}
            is_occupied = float(band["occupations"][index]) > params["occupancy_threshold"] if occupation_complete else energy <= float(fermi) + params["energy_tolerance_ev"]
            (occupied if is_occupied else unoccupied).append(state)
    if not occupied or not unoccupied:
        return {"status": "UNAVAILABLE", "valueEv": None, "vbm": None, "cbm": None, "directness": "UNAVAILABLE", "classification": "CLASSIFICATION_UNAVAILABLE", "algorithmId": BAND_GAP_ALGORITHM}
    order = lambda item: (_spin_order(item["spinChannel"]), item["kpointId"], item["bandId"])
    vbm_energy = max(item["energyEv"] for item in occupied)
    cbm_energy = min(item["energyEv"] for item in unoccupied)
    vbm = sorted((item for item in occupied if abs(item["energyEv"] - vbm_energy) <= params["energy_tolerance_ev"]), key=order)[0]
    cbm = sorted((item for item in unoccupied if abs(item["energyEv"] - cbm_energy) <= params["energy_tolerance_ev"]), key=order)[0]
    gap = max(0.0, cbm_energy - vbm_energy)
    classification = "METAL_LIKE_UNDER_POLICY" if crossing or gap <= params["gap_threshold_ev"] else "NONZERO_GAP_UNDER_POLICY"
    return {"status": "AVAILABLE", "valueEv": _round(gap), "vbm": vbm, "cbm": cbm, "directness": "DIRECT" if vbm["kpointId"] == cbm["kpointId"] else "INDIRECT", "classification": classification, "gapThresholdEv": params["gap_threshold_ev"], "algorithmId": BAND_GAP_ALGORITHM}


def _band_plot(payload: Mapping[str, Any]) -> dict[str, Any]:
    points = payload["kpoints"]
    traces = [{"type": "scatter", "mode": "lines", "name": f"{item['spinChannel']}:{item['bandId']}", "x": [point["pathDistance"] for point in points], "y": item["energiesEv"], "customdata": [point["kpointId"] for point in points]} for item in payload["bands"]]
    fermi = payload["energy"].get("fermiEnergyEv")
    return {"schemaVersion": "phase10n5.electronic_band_plot.v1", "data": traces, "layout": {"title": {"text": "Supplied electronic band structure"}, "xaxis": {"title": {"text": "Reciprocal path"}}, "yaxis": {"title": {"text": "Energy / eV"}}, "shapes": [] if fermi is None else [{"type": "line", "x0": min(point["pathDistance"] for point in points), "x1": max(point["pathDistance"] for point in points), "y0": fermi, "y1": fermi, "line": {"dash": "dash"}}]}, "pathSegments": payload["pathSegments"], "frontendScientificComputation": False}


def _dos_plot(payload: Mapping[str, Any]) -> dict[str, Any]:
    traces = []
    for item in [*payload["totalDos"], *payload["projections"]]:
        traces.append({"type": "scatter", "mode": "lines", "name": f"{item['spinChannel']}:{item.get('label', item['channelId'])}", "x": item["values"], "y": payload["energiesEv"], "customdata": payload["energyPointIds"]})
    return {"schemaVersion": "phase10n5.electronic_dos_plot.v1", "data": traces, "layout": {"title": {"text": "Supplied electronic DOS"}, "xaxis": {"title": {"text": payload["dosUnitSemantic"]}}, "yaxis": {"title": {"text": "Energy / eV"}}}, "projectionCompleteness": payload["projectionCompleteness"], "frontendScientificComputation": False}


def _dos_channel(item: Mapping[str, Any], resource_hash: str) -> dict[str, Any]:
    result = dict(item)
    result["channelIdentity"] = _identity("dos-channel", {"resourceHash": resource_hash, "spin": item["spinChannel"], "channelId": item["channelId"], "kind": item.get("projectionKind", "total")})
    result["values"] = [_round(float(value)) for value in item["values"]]
    return result


def _identity(prefix: str, value: Mapping[str, Any]) -> str:
    return f"{prefix}:{content_hash(stable_json_dumps(value))}"


def _ref(value: Any) -> str:
    return str(getattr(value, "ref", value.get("ref") if isinstance(value, Mapping) else value))


def _unknown(params: Mapping[str, Any], allowed: set[str], code: str) -> None:
    unknown = sorted(set(params) - allowed)
    if unknown:
        raise _error("TOOL_PARAM_INVALID", code, "Unknown electronic parameters are rejected.", unknown=unknown)


def _number(params: Mapping[str, Any], name: str, default: float, low: float, high: float) -> float:
    value = params.get(name, default)
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)) or not low <= float(value) <= high:
        raise _error("TOOL_PARAM_INVALID", "ELECTRONIC_PARAMETER_INVALID", f"{name} is outside the bounded finite range.")
    return float(value)


def _integer(params: Mapping[str, Any], name: str, default: int, low: int, high: int) -> int:
    value = params.get(name, default)
    if not isinstance(value, int) or isinstance(value, bool) or not low <= value <= high:
        raise _error("TOOL_PARAM_INVALID", "ELECTRONIC_PARAMETER_INVALID", f"{name} is outside the bounded integer range.")
    return value


def _boolean(params: Mapping[str, Any], name: str, default: bool) -> bool:
    value = params.get(name, default)
    if not isinstance(value, bool):
        raise _error("TOOL_PARAM_INVALID", "ELECTRONIC_PARAMETER_INVALID", f"{name} must be boolean.")
    return value


def _spin_order(value: str) -> int:
    return {"none": 0, "up": 1, "down": 2}.get(value, 9)


def _round(value: float) -> float:
    return float(f"{value:.12g}")


def _error(code: str, semantic: str, message: str, **details: Any) -> ToolExecutionError:
    return ToolExecutionError(code=code, message=message, tool_id="electronic", retryable=False, details={"semanticCode": semantic, **details})
