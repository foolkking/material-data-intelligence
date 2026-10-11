from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Callable
from uuid import NAMESPACE_URL, UUID, uuid5

from mdi_api.agent2_errors import ScientificResultProjectionFailed
from mdi_api.application.scientific_results.figure_titles import scientific_figure_title, scientific_table_title
from mdi_api.application.scientific_results.projectors.base import ScientificResultProjection, ScientificResultProjectionContext
from mdi_api.application.scientific_results.projectors.artifact_payloads import validate_production_payload
from mdi_api.application.scientific_results.projectors.trajectory import trajectory_view_facts
from mdi_api.application.scientific_results.projectors.phonon import phonon_band_facts
from mdi_api.application.scientific_results.projectors.electronic import electronic_selection_facts
from mdi_api.application.scientific_results.projectors.volumetric import volumetric_selection_facts, volumetric_field_limitations
from mdi_api.application.scientific_results.projectors.structure import structure_selection_facts
from mdi_api.application.scientific_results.projectors.table_analysis import valid_table_output, table_facts, table_warnings
from mdi_api.application.scientific_results.projectors.coordination import (
    COORDINATION_PROJECTORS, N2_SCHEMA, coordination_facts, coordination_warnings,
    valid_coordination_payload, validate_local_environment_dependency,
)
from mdi_api.domain.scientific_results.contracts import (
    EvidenceItem,
    FactSourceLocator,
    MethodRecord,
    ProvenanceRecord,
    ResultRelevanceStatus,
    ScientificFigure,
    ScientificFact,
    ScientificLimitation,
    ScientificResultBundle,
    ScientificResultItem,
    ScientificResultRole,
    ScientificTable,
    ScientificWarning,
)
from mdi_artifact_core import (
    BRILLOUIN_ZONE_SCHEMA_VERSION,
    KPATH_SCHEMA_VERSION,
    RECIPROCAL_LATTICE_SCHEMA_VERSION,
    TRAJECTORY_MANIFEST_SCHEMA_VERSION,
    TRAJECTORY_SCHEMA_VERSION,
    TRAJECTORY_SUMMARY_SCHEMA_VERSION,
)
from mdi_material_parsers.trajectory import TRAJECTORY_PARSE_REPORT_SCHEMA_VERSION


def resolve_json_pointer(payload: Any, pointer: str) -> Any:
    current = payload
    if pointer == "/":
        return current
    for raw in pointer.strip("/").split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def _semantic_id(kind: str, *parts: str) -> str:
    return f"{kind}.{uuid5(NAMESPACE_URL, 'mdi-agent2-result:' + ':'.join(parts)).hex}"


def _artifact_id(artifact: dict[str, Any]) -> str:
    return str(artifact.get("id") or artifact.get("artifactId"))


def _schema(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    value = payload.get("schema_version") or payload.get("schemaVersion")
    return str(value) if value else None


@dataclass(frozen=True)
class FactDeclaration:
    predicate: str
    pointer: str
    unit: str | Callable[[dict[str, Any]], str | None] | None = None


@dataclass(frozen=True)
class ProjectorContract:
    projector_id: str
    title: str
    result_type: str
    primary_schemas: tuple[str, ...]
    figure_schemas: tuple[str, ...]
    table_schemas: tuple[str, ...]
    required_primary_schemas: tuple[str, ...] = ()
    accepted_tool_ids: tuple[str, ...] = ()
    required_tool_ids: tuple[str, ...] = ()
    facts: tuple[FactDeclaration, ...] = ()
    fact_builder: Callable[[dict[str, Any], dict[str, Any]], list[ScientificFact]] | None = None
    limitations: tuple[tuple[str, str], ...] = ()
    version: str = "1.1"
    primary_as_table: bool = True


def _fact(
    artifact: dict[str, Any],
    payload: dict[str, Any],
    declaration: FactDeclaration,
    *,
    suffix: str = "",
) -> ScientificFact | None:
    try:
        value = resolve_json_pointer(payload, declaration.pointer)
    except (KeyError, IndexError, TypeError, ValueError):
        return None
    if value is None or isinstance(value, (dict, list, bool)):
        return None
    unit = declaration.unit(payload) if callable(declaration.unit) else declaration.unit
    artifact_id = _artifact_id(artifact)
    return ScientificFact(
        fact_id=_semantic_id("fact", artifact_id, declaration.predicate, declaration.pointer, suffix),
        predicate=declaration.predicate,
        subject_ref=artifact_id,
        value=value,
        unit=unit,
        source=FactSourceLocator(artifact_id=artifact_id, artifact_locator=declaration.pointer),
    )


def _xrd_peak_facts(artifact: dict[str, Any], payload: dict[str, Any]) -> list[ScientificFact]:
    """Expose at most five strongest retained peaks, with original JSON locators."""
    peaks = payload.get("pattern", {}).get("peaks", [])
    def finite(value: Any) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    candidates = [(index, peak) for index, peak in enumerate(peaks)
                  if isinstance(peak, dict) and all(finite(peak.get(key)) for key in
                      ("intensity", "two_theta_deg", "d_spacing_angstrom"))]
    candidates.sort(key=lambda item: (-item[1]["intensity"], item[0]))
    facts = []
    for index, peak in candidates[:5]:
        base = f"/pattern/peaks/{index}"
        declarations = [
            FactDeclaration("xrd.peak.two_theta", f"{base}/two_theta_deg", "degree"),
            FactDeclaration("xrd.peak.intensity", f"{base}/intensity"),
            FactDeclaration("xrd.peak.d_spacing", f"{base}/d_spacing_angstrom", "angstrom"),
            FactDeclaration("xrd.peak.structure", f"{base}/structureId"),
        ]
        # Keep each saved Miller-family component distinct; never invent absent indices.
        hkls = peak.get("hkls", [])
        for family_index, family in enumerate(hkls[:4] if isinstance(hkls, list) else []):
            hkl = family.get("hkl") if isinstance(family, dict) else None
            if not isinstance(hkl, list) or len(hkl) not in (3, 4) or not all(type(v) is int for v in hkl):
                continue
            for axis in range(len(hkl)):
                declarations.append(FactDeclaration(f"xrd.peak.hkl_{family_index}.component_{axis}", f"{base}/hkls/{family_index}/hkl/{axis}"))
        for declaration in declarations:
            fact = _fact(artifact, payload, declaration)
            if fact:
                facts.append(fact.model_copy(update={"subject_ref": f"{_artifact_id(artifact)}:retained-peak-{index}"}))
    return facts


def _ml_facts(artifact: dict[str, Any], payload: dict[str, Any]) -> list[ScientificFact]:
    result: list[ScientificFact] = []
    artifact_id = _artifact_id(artifact)

    def add_sample_fact(
        value: Any,
        *,
        predicate: str,
        pointer: str,
        subject: str,
        unit: str | None = None,
    ) -> None:
        if value is None or isinstance(value, (dict, list, bool)):
            return
        result.append(
            ScientificFact(
                fact_id=_semantic_id("fact", artifact_id, predicate, pointer, subject),
                predicate=predicate,
                subject_ref=subject,
                value=value,
                unit=unit,
                source=FactSourceLocator(
                    artifact_id=artifact_id,
                    artifact_locator=pointer,
                ),
            )
        )

    for index, evaluation in enumerate(payload.get("evaluations") or []):
        unit = evaluation.get("unit")
        metrics = evaluation.get("metrics") or {}
        status = metrics.get("r2Status")
        if ((status == "undefined_constant_target" and metrics.get("r2") is None)
                or (status == "defined" and type(metrics.get("r2")) in (int, float) and math.isfinite(metrics["r2"]))):
            status_fact = _fact(artifact, payload, FactDeclaration("ml.r2_status", f"/evaluations/{index}/metrics/r2Status"))
            if status_fact is not None:
                result.append(status_fact)
        for key, predicate in (
            ("sampleCount", "ml.sample_count"),
            ("mae", "ml.mae"),
            ("rmse", "ml.rmse"),
            ("r2", "ml.r2"),
            ("meanSignedError", "ml.mean_signed_error"),
            ("medianAbsoluteError", "ml.median_absolute_error"),
        ):
            fact = _fact(
                artifact,
                payload,
                FactDeclaration(
                    predicate,
                    f"/evaluations/{index}/metrics/{key}",
                    None if key in {"sampleCount", "r2"} else unit,
                ),
                suffix=str(evaluation.get("taskId") or index),
            )
            if fact is not None:
                result.append(fact)
        # The adapter already ranks these rows deterministically by descending
        # absolute error and stable sample identity. Project a bounded prefix
        # so interpretation can name the real sample and its exact residual
        # without recovering facts from raw Artifact bytes.
        for sample_index, sample in enumerate((evaluation.get("highErrorSamples") or [])[:10]):
            subject = str(sample.get("sampleKey") or sample.get("sampleRef") or f"{artifact_id}:high-error-{sample_index}")
            base = f"/evaluations/{index}/highErrorSamples/{sample_index}"
            for key, predicate, fact_unit in (
                ("sampleRef", "ml.high_error_sample_id", None),
                ("formula", "ml.high_error_formula", None),
                ("target", "ml.high_error_target", unit),
                ("prediction", "ml.high_error_prediction", unit),
                ("residual", "ml.high_error_residual", unit),
                ("absoluteError", "ml.high_error_absolute_error", unit),
            ):
                add_sample_fact(
                    sample.get(key),
                    predicate=predicate,
                    pointer=f"{base}/{key}",
                    subject=subject,
                    unit=fact_unit,
                )
    return result


def _dataset_facts(artifact: dict[str, Any], payload: dict[str, Any]) -> list[ScientificFact]:
    """Project bounded Dataset Explorer scalars into grounded facts.

    The Dataset Explorer artifact already contains the authoritative values
    used by its table/summary views.  Exposing those scalar values here keeps
    interpretation grounded without asking the provider to recover numbers
    from raw Artifact bytes.
    """

    result: list[ScientificFact] = []
    artifact_id = _artifact_id(artifact)

    def add(value: Any, *, predicate: str, pointer: str, subject: str, unit: str | None = None) -> None:
        if value is None or isinstance(value, (dict, list, bool)):
            return
        result.append(
            ScientificFact(
                fact_id=_semantic_id("fact", artifact_id, predicate, pointer, subject),
                predicate=predicate,
                subject_ref=subject,
                value=value,
                unit=unit,
                source=FactSourceLocator(artifact_id=artifact_id, artifact_locator=pointer),
            )
        )

    overview = payload.get("overview") or {}
    coverage = payload.get("coverage") or {}
    composition = payload.get("composition") or {}
    quality = payload.get("quality") or {}
    add(overview.get("sampleCount"), predicate="dataset.sample_count", pointer="/overview/sampleCount", subject=artifact_id, unit="count")
    add(overview.get("propertyCount"), predicate="dataset.property_count", pointer="/overview/propertyCount", subject=artifact_id, unit="count")
    add(coverage.get("totalRows"), predicate="dataset.row_count", pointer="/coverage/totalRows", subject=artifact_id, unit="count")
    add(coverage.get("totalColumns"), predicate="dataset.column_count", pointer="/coverage/totalColumns", subject=artifact_id, unit="count")
    add(composition.get("uniqueFormulaCount"), predicate="dataset.unique_formula_count", pointer="/composition/uniqueFormulaCount", subject=artifact_id, unit="count")
    add(composition.get("coverage", {}).get("valid"), predicate="composition.valid_count", pointer="/composition/coverage/valid", subject=artifact_id, unit="count")
    add(composition.get("coverage", {}).get("invalid"), predicate="composition.invalid_count", pointer="/composition/coverage/invalid", subject=artifact_id, unit="count")
    add(quality.get("invalidFormulaCount"), predicate="quality.invalid_formula_count", pointer="/quality/invalidFormulaCount", subject=artifact_id, unit="count")

    for index, sample in enumerate(payload.get("sampleIndex") or []):
        sample_ref = sample.get("sampleRef")
        subject = str(sample.get("sampleKey") or sample_ref or f"{artifact_id}:row-{index}")
        base = f"/sampleIndex/{index}"
        add(sample_ref, predicate="dataset.sample_id", pointer=f"{base}/sampleRef", subject=subject)
        add(sample.get("formula"), predicate="dataset.formula", pointer=f"{base}/formula", subject=subject)
        for column, value in (sample.get("properties") or {}).items():
            add(value, predicate=f"dataset.sample.{column}", pointer=f"{base}/properties/{column}", subject=subject)

    for property_index, property_item in enumerate((payload.get("properties") or {}).get("properties") or []):
        column = str(property_item.get("column") or "").strip()
        if not column:
            continue
        statistics = property_item.get("statistics") or {}
        unit = property_item.get("unit")
        for name in ("min", "max", "mean", "median"):
            add(
                statistics.get(name),
                predicate=f"dataset.property.{column}.{name}",
                pointer=f"/properties/properties/{property_index}/statistics/{name}",
                subject=f"{artifact_id}:{column}",
                unit=unit,
            )

    return result


def _structure_summary_facts(
    artifact: dict[str, Any],
    payload: dict[str, Any],
) -> list[ScientificFact]:
    result: list[ScientificFact] = []
    artifact_id = _artifact_id(artifact)

    def add(
        value: Any,
        *,
        predicate: str,
        pointer: str,
        subject: str,
        unit: str | None = None,
    ) -> None:
        if value is None or isinstance(value, (dict, list, bool)):
            return
        result.append(
            ScientificFact(
                fact_id=_semantic_id("fact", artifact_id, predicate, pointer, subject),
                predicate=predicate,
                subject_ref=subject,
                value=value,
                unit=unit,
                source=FactSourceLocator(
                    artifact_id=artifact_id,
                    artifact_locator=pointer,
                ),
            )
        )

    for index, structure in enumerate(payload.get("structures") or []):
        subject = str(
            structure.get("structureId")
            or f"{artifact_id}:structure-{index}"
        )
        base = f"/structures/{index}"
        add(
            structure.get("reducedFormula"),
            predicate="structure.reduced_formula",
            pointer=f"{base}/reducedFormula",
            subject=subject,
        )
        add(
            structure.get("numSites"),
            predicate="structure.site_count",
            pointer=f"{base}/numSites",
            subject=subject,
            unit="count",
        )
        lattice = structure.get("lattice") or {}
        for key, predicate, unit in (
            ("a", "structure.lattice_a", "angstrom"),
            ("b", "structure.lattice_b", "angstrom"),
            ("c", "structure.lattice_c", "angstrom"),
            ("alpha", "structure.lattice_alpha", "degree"),
            ("beta", "structure.lattice_beta", "degree"),
            ("gamma", "structure.lattice_gamma", "degree"),
            ("volume", "structure.lattice_volume", "angstrom^3"),
        ):
            add(
                lattice.get(key),
                predicate=predicate,
                pointer=f"{base}/lattice/{key}",
                subject=subject,
                unit=unit,
            )
        symmetry = structure.get("symmetry") or {}
        for key, predicate, unit in (
            ("spacegroupNumber", "structure.spacegroup_number", None),
            ("spacegroupSymbol", "structure.spacegroup_symbol", None),
            ("crystalSystem", "structure.crystal_system", None),
        ):
            add(
                symmetry.get(key),
                predicate=predicate,
                pointer=f"{base}/symmetry/{key}",
                subject=subject,
                unit=unit,
            )
    return result


def _volumetric_facts(artifact: dict[str, Any], payload: dict[str, Any]) -> list[ScientificFact]:
    result: list[ScientificFact] = []
    artifact_id = _artifact_id(artifact)

    def add(value: Any, *, predicate: str, pointer: str, unit: str | None = None) -> None:
        if value is None or isinstance(value, (dict, list)) or (isinstance(value, bool) and predicate != "volumetric.unit_conversion_applied"):
            return
        result.append(
            ScientificFact(
                fact_id=_semantic_id("fact", artifact_id, predicate, pointer),
                predicate=predicate,
                subject_ref=artifact_id,
                value=value,
                unit=unit,
                source=FactSourceLocator(artifact_id=artifact_id, artifact_locator=pointer),
            )
        )

    if _schema(payload) == "phase10j.volumetric_dataset.v1":
        grid = payload["grid"]
        for key in ("length_unit", "coordinate_space", "sample_location", "endpoint_policy"):
            add(grid.get(key), predicate=f"volumetric.{key}", pointer=f"/grid/{key}")
        for index, axis in enumerate("abc"):
            add(grid["shape"][index], predicate=f"volumetric.grid_size_{axis}", pointer=f"/grid/shape/{index}")
            add(grid["boundary_conditions"][index], predicate=f"volumetric.boundary_{axis}", pointer=f"/grid/boundary_conditions/{index}")
        return result

    add(payload.get("field_name"), predicate="volumetric.field_name", pointer="/field_name")
    add(payload.get("quantity"), predicate="volumetric.quantity", pointer="/quantity")
    add(payload.get("value_kind"), predicate="volumetric.value_kind", pointer="/value_kind")
    unit = (payload.get("unit") or {}).get("canonical_unit")
    add(unit, predicate="volumetric.canonical_unit", pointer="/unit/canonical_unit")
    semantics = payload.get("integral_semantics")
    add(semantics, predicate="volumetric.integral_semantics", pointer="/integral_semantics")
    add(payload.get("normalization_semantics"), predicate="volumetric.normalization_semantics", pointer="/normalization_semantics")
    # Integral normalization and unit conversion are separate saved contracts.
    # Equal unit labels do not prove that source values were left unchanged.
    for key, predicate in (
        ("source_unit", "volumetric.source_unit"),
        ("conversion_applied", "volumetric.unit_conversion_applied"),
        ("conversion_factor", "volumetric.unit_conversion_factor"),
    ):
        add((payload.get("unit") or {}).get(key), predicate=predicate, pointer=f"/unit/{key}")
    add((payload.get("statistics") or {}).get("authority"), predicate="volumetric.statistics_authority", pointer="/statistics/authority")
    # Report only the stored integral with an explicitly compatible physical
    # meaning. A potential/ELF integral is not an electron count or a mean.
    integral_unit = {
        ("electron_count", "electron/angstrom^3"): "electron",
        ("elementary_charge", "elementary_charge/angstrom^3"): "elementary_charge",
        ("magnetic_moment", "bohr_magneton/angstrom^3"): "bohr_magneton",
    }.get((semantics, unit))
    potential_unit = unit if payload.get("quantity") in {"local_potential", "electrostatic_potential"} and unit in {
        "electronvolt", "volt", "hartree", "hartree/elementary_charge",
    } else None
    if potential_unit:
        for key, predicate in (("kind", "volumetric.potential_reference"), ("shift_amount", "volumetric.potential_shift")):
            add((payload.get("potential_reference") or {}).get(key), predicate=predicate,
                pointer=f"/potential_reference/{key}", unit=unit if key == "shift_amount" else None)
    for index, component in enumerate((payload.get("statistics") or {}).get("stored_components") or []):
        add(component.get("mean"), predicate="volumetric.mean",
            pointer=f"/statistics/stored_components/{index}/mean", unit=unit)
        add(
            component.get("minimum"),
            predicate="volumetric.minimum",
            pointer=f"/statistics/stored_components/{index}/minimum",
            unit=unit,
        )
        add(
            component.get("maximum"),
            predicate="volumetric.maximum",
            pointer=f"/statistics/stored_components/{index}/maximum",
            unit=unit,
        )
        if integral_unit is not None:
            add(component.get("integral"), predicate="volumetric.integral",
                pointer=f"/statistics/stored_components/{index}/integral", unit=integral_unit)
        elif potential_unit:
            # The stored statistic is sum(value * voxel_volume), even when
            # the source declares cell_average semantics. Never label it a mean.
            add(component.get("integral"), predicate="volumetric.volume_integral",
                pointer=f"/statistics/stored_components/{index}/integral", unit=f"{potential_unit}*angstrom^3")
        elif payload.get("quantity") == "electron_localization_function" and unit == "dimensionless" and semantics == "not_physically_interpreted":
            add(component.get("integral"), predicate="volumetric.volume_integral",
                pointer=f"/statistics/stored_components/{index}/integral", unit="angstrom^3")
    return result


def _ml_uncertainty_facts(artifact: dict[str, Any], payload: dict[str, Any]) -> list[ScientificFact]:
    result: list[ScientificFact] = []
    artifact_id = _artifact_id(artifact)
    for index, evaluation in enumerate(payload.get("evaluations") or []):
        base = f"/evaluations/{index}"
        values = {
            "ml.uncertainty_evaluated_sample_count": (
                (evaluation.get("coverage") or {}).get("evaluatedSamples"),
                "count",
                f"{base}/coverage/evaluatedSamples",
            ),
            "ml.uncertainty_error_pearson": (
                (evaluation.get("association") or {}).get("pearson"),
                None,
                f"{base}/association/pearson",
            ),
            "ml.uncertainty_error_spearman": (
                (evaluation.get("association") or {}).get("spearman"),
                None,
                f"{base}/association/spearman",
            ),
        }
        for predicate, (value, unit, pointer) in values.items():
            if value is None or isinstance(value, (dict, list, bool)):
                continue
            result.append(
                ScientificFact(
                    fact_id=_semantic_id("fact", artifact_id, predicate, pointer, str(index)),
                    predicate=predicate,
                    subject_ref=artifact_id,
                    value=value,
                    unit=unit,
                    source=FactSourceLocator(artifact_id=artifact_id, artifact_locator=pointer),
                )
            )
    return result


def _ml_classification_facts(artifact: dict[str, Any], payload: dict[str, Any]) -> list[ScientificFact]:
    result: list[ScientificFact] = []
    artifact_id = _artifact_id(artifact)
    for index, evaluation in enumerate(payload.get("evaluations") or []):
        metrics = evaluation.get("metrics") or {}
        base = f"/evaluations/{index}/metrics"
        for key, predicate in (
            ("sampleCount", "ml.classification_sample_count"),
            ("accuracy", "ml.classification_accuracy"),
            ("macroPrecision", "ml.classification_macro_precision"),
            ("macroRecall", "ml.classification_macro_recall"),
            ("macroF1", "ml.classification_macro_f1"),
        ):
            value = metrics.get(key)
            if value is None or isinstance(value, (dict, list, bool)):
                continue
            result.append(
                ScientificFact(
                    fact_id=_semantic_id("fact", artifact_id, predicate, f"{base}/{key}", str(index)),
                    predicate=predicate,
                    subject_ref=artifact_id,
                    value=value,
                    unit="count" if key == "sampleCount" else None,
                    source=FactSourceLocator(artifact_id=artifact_id, artifact_locator=f"{base}/{key}"),
                )
            )
    return result


def _trajectory_msd_facts(
    artifact: dict[str, Any], payload: dict[str, Any]
) -> list[ScientificFact]:
    """Expose saved endpoints and origin coverage, never fit or summarize a curve."""

    lag_times = payload.get("lagTimesPs")
    if not isinstance(lag_times, list) or not lag_times:
        return []
    def numeric_series(value: Any) -> bool:
        return isinstance(value, list) and len(value) == len(lag_times) and all(
            isinstance(item, (int, float)) and not isinstance(item, bool) and math.isfinite(item)
            for item in value
        )
    direction = payload.get("directionalMsdAngstrom2", {})
    series = [lag_times, payload.get("totalMsdAngstrom2")]
    series.extend(direction[axis] for axis in "xyz" if isinstance(direction, dict) and axis in direction)
    if "originCounts" in payload:
        series.append(payload["originCounts"])
    if not all(numeric_series(values) for values in series):
        raise ScientificResultProjectionFailed("MSD arrays must retain finite, aligned saved coordinates")
    last_index = len(lag_times) - 1
    facts: list[ScientificFact] = []
    declarations = []
    for boundary, index in (("first", 0), ("last", last_index)):
        declarations.extend([
            FactDeclaration(f"trajectory.msd_{boundary}_lag_time", f"/lagTimesPs/{index}", "picosecond"),
            FactDeclaration(f"trajectory.msd_{boundary}_total", f"/totalMsdAngstrom2/{index}", "angstrom^2"),
            FactDeclaration(f"trajectory.msd_{boundary}_origin_count", f"/originCounts/{index}", "count"),
        ])
        for axis in "xyz":
            declarations.append(FactDeclaration(f"trajectory.msd_{boundary}_{axis}", f"/directionalMsdAngstrom2/{axis}/{index}", "angstrom^2"))
    for declaration in declarations:
        fact = _fact(
            artifact,
            payload,
            declaration,
        )
        if fact is not None:
            facts.append(fact)
    return facts


def _brillouin_zone_facts(
    artifact: dict[str, Any], payload: dict[str, Any]
) -> list[ScientificFact]:
    schema = _schema(payload)
    declarations: tuple[FactDeclaration, ...]
    if schema == RECIPROCAL_LATTICE_SCHEMA_VERSION:
        declarations = (
            FactDeclaration(
                "reciprocal.cell_volume",
                "/cell_volume",
                "angstrom^-3",
            ),
            FactDeclaration(
                "reciprocal.convention",
                "/convention",
            ),
        )
    elif schema == BRILLOUIN_ZONE_SCHEMA_VERSION:
        declarations = (
            FactDeclaration(
                "reciprocal.brillouin_zone_volume",
                "/volume",
                "angstrom^-3",
            ),
            FactDeclaration(
                "reciprocal.brillouin_zone_vertex_count",
                "/topology/vertex_count",
                "count",
            ),
            FactDeclaration(
                "reciprocal.brillouin_zone_edge_count",
                "/topology/edge_count",
                "count",
            ),
            FactDeclaration(
                "reciprocal.brillouin_zone_face_count",
                "/topology/face_count",
                "count",
            ),
        )
    elif schema == KPATH_SCHEMA_VERSION:
        points = payload.get("points")
        if not isinstance(points, list):
            return []
        artifact_id = _artifact_id(artifact)
        return [
            ScientificFact(
                fact_id=_semantic_id(
                    "fact",
                    artifact_id,
                    "reciprocal.high_symmetry_point_count",
                    "/points",
                ),
                predicate="reciprocal.high_symmetry_point_count",
                subject_ref=artifact_id,
                value=len(points),
                unit="count",
                source=FactSourceLocator(
                    artifact_id=artifact_id,
                    artifact_locator="/points",
                ),
            )
        ]
    else:
        return []
    return [
        fact
        for declaration in declarations
        if (fact := _fact(artifact, payload, declaration)) is not None
    ]


def _project(context: ScientificResultProjectionContext, contract: ProjectorContract) -> ScientificResultProjection:
    recognized: list[tuple[dict[str, Any], dict[str, Any], str]] = []
    accepted = {*contract.primary_schemas, *contract.figure_schemas, *contract.table_schemas}
    accepted_tool_ids = set(contract.accepted_tool_ids)
    calls_by_id = {
        str(call.get("id")): call
        for call in context.tool_calls
        if call.get("id") is not None
    }
    for artifact in sorted(context.artifacts, key=_artifact_id):
        payload = context.artifact_payloads.get(_artifact_id(artifact))
        schema = _schema(payload)
        if isinstance(payload, dict) and schema in accepted:
            try:
                validate_production_payload(str(schema), payload)
                if schema == N2_SCHEMA and not valid_coordination_payload(payload):
                    raise ValueError("Invalid saved local-environment geometry")
            except ValueError:
                continue
            if schema == N2_SCHEMA:
                validate_local_environment_dependency(context, artifact, payload)
            recognized.append((artifact, payload, str(schema)))
            continue
        call = calls_by_id.get(
            str(artifact.get("toolCallId") or artifact.get("tool_call_id") or "")
        )
        tool_id = str(
            (call or {}).get("toolId") or (call or {}).get("tool_id") or ""
        )
        if isinstance(payload, dict) and tool_id in accepted_tool_ids:
            if contract.projector_id == "agent2.data.table_analysis":
                if str((call or {}).get("state") or (call or {}).get("status") or "").lower() != "completed":
                    continue
                if not valid_table_output(tool_id, str(artifact.get("type") or ""), payload):
                    continue
            recognized.append((artifact, payload, f"tool:{tool_id}"))

    primary = [
        item
        for item in recognized
        if item[2] in contract.primary_schemas or item[2].startswith("tool:")
    ]
    if not primary:
        raise ScientificResultProjectionFailed(
            f"{contract.projector_id} found no verified production Artifact schema",
            code="RESULT_PROJECTION_NOT_SUPPORTED",
        )
    if contract.required_primary_schemas:
        recognized_primary_schemas = {item[2] for item in primary}
        missing = [
            schema
            for schema in contract.required_primary_schemas
            if schema not in recognized_primary_schemas
        ]
        if missing:
            raise ScientificResultProjectionFailed(
                (
                    f"{contract.projector_id} is missing required verified "
                    f"Artifact schemas: {', '.join(missing)}"
                ),
                code="RESULT_PROJECTION_INCOMPLETE",
            )
    if contract.required_tool_ids:
        recognized_tool_ids = {
            item[2].removeprefix("tool:")
            for item in recognized
            if item[2].startswith("tool:")
            and not (contract.projector_id == "agent2.data.table_analysis"
                     and item[2] == "tool:viz.correlation" and item[0].get("type") != "table_json")
        }
        missing_tools = [
            tool_id
            for tool_id in contract.required_tool_ids
            if tool_id not in recognized_tool_ids
        ]
        if missing_tools:
            raise ScientificResultProjectionFailed(
                (
                    f"{contract.projector_id} is missing required committed "
                    f"Tool outputs: {', '.join(missing_tools)}"
                ),
                code="RESULT_PROJECTION_INCOMPLETE",
            )

    facts: list[ScientificFact] = []
    if contract.projector_id == "agent2.data.table_analysis":
        # Put coefficient/name groups before repetitive descriptive statistics.
        primary.sort(key=lambda item: item[2] != "tool:viz.correlation")
    for artifact, payload, _schema_name in primary:
        facts.extend(filter(None, (_fact(artifact, payload, declaration) for declaration in contract.facts)))
        if contract.fact_builder is not None:
            facts.extend(contract.fact_builder(artifact, payload))
        if contract.projector_id in COORDINATION_PROJECTORS:
            facts.extend(coordination_facts(context, artifact, payload))
        if contract.projector_id == "agent2.structure.viewer_scene":
            facts.extend(structure_selection_facts(context, artifact, payload))
        if contract.projector_id == "agent2.trajectory.viewer_scene" and _schema_name == TRAJECTORY_SCHEMA_VERSION:
            facts.extend(trajectory_view_facts(context, artifact, payload))
        if contract.projector_id == "agent2.phonon.band" and _schema_name == "phase10h.phonon_band.v1":
            facts.extend(phonon_band_facts(context, artifact, payload))
        if contract.projector_id == "agent2.volumetric.data" and _schema_name == "phase10j.volumetric_dataset.v1":
            facts.extend(volumetric_selection_facts(context, artifact, payload))
        if contract.projector_id in {"agent2.electronic.band_structure", "agent2.electronic.dos"}:
            facts.extend(electronic_selection_facts(context, artifact, payload))

    artifact_ids = [_artifact_id(item[0]) for item in recognized]
    evidence = [
        EvidenceItem(
            evidence_id=_semantic_id("evidence", _artifact_id(artifact), schema_name),
            evidence_type="COMMITTED_MACHINE_READABLE_ARTIFACT",
            artifact_id=_artifact_id(artifact),
            artifact_locator="/",
            scientific_object_refs=list(context.source_object_refs),
        )
        for artifact, _payload, schema_name in recognized
    ]
    scope_parts = [context.projection_scope_key] if context.projection_scope_key else []
    item_id = _semantic_id("result-item", context.research_turn_id, contract.projector_id, *scope_parts)
    title = contract.title
    if context.projection_scope_key:
        source_names = [ref.display_name or f"{ref.object_type} · {str(ref.version_id)[:8]}" for ref in context.source_object_refs]
        title = f"{contract.title} · {', '.join(source_names)}"[:512]
    item = ScientificResultItem(
        id=item_id,
        result_type=contract.result_type,
        role=ScientificResultRole.PRIMARY,
        title=title,
        artifact_ids=artifact_ids,
        scientific_object_refs=list(context.source_object_refs),
        fact_refs=[fact.fact_id for fact in facts],
        evidence_refs=[source.evidence_id for source in evidence],
    )
    for source in evidence:
        source.supports_fact_refs = [fact.fact_id for fact in facts if fact.source.artifact_id == source.artifact_id]
        source.supports_result_item_refs = [item_id]

    def figure_facts(artifact: dict[str, Any]) -> list[str]:
        if contract.projector_id != "agent2.data.table_analysis":
            return []
        ids = {_artifact_id(artifact)}
        if contract.projector_id == "agent2.data.table_analysis":
            call_id = artifact.get("toolCallId") or artifact.get("tool_call_id")
            if call_id:
                ids.update(_artifact_id(item) for item, _, _ in recognized
                           if (item.get("toolCallId") or item.get("tool_call_id")) == call_id)
        return [fact.fact_id for fact in facts if fact.source.artifact_id in ids]

    figures = [
        ScientificFigure(
            figure_id=_semantic_id("figure", _artifact_id(artifact), schema_name),
            figure_type=contract.result_type,
            role=ScientificResultRole.PRIMARY,
            title=scientific_figure_title(
                title, [_artifact_id(artifact)], artifacts=context.artifacts,
                calls=context.tool_calls, job_id=str(context.execution_summary.get("job_id") or ""),
                project_id=context.project_id,
            ),
            artifact_ids=[_artifact_id(artifact)],
            fact_refs=figure_facts(artifact),
            evidence_refs=[_semantic_id("evidence", _artifact_id(artifact), schema_name)],
        )
        for artifact, _payload, schema_name in recognized
        if (
            schema_name in contract.figure_schemas
            or (
                schema_name.startswith("tool:")
                and str(artifact.get("type") or "")
                in {"plotly_json", "plotly_html", "preview_png"}
            )
        )
    ]
    tables = [
        ScientificTable(
            table_id=_semantic_id("table", _artifact_id(artifact), schema_name),
            table_type=contract.result_type,
            role=ScientificResultRole.PRIMARY,
            title=scientific_table_title(
                title, [_artifact_id(artifact)], artifacts=context.artifacts,
                calls=context.tool_calls, job_id=str(context.execution_summary.get("job_id") or ""),
                project_id=context.project_id,
            ),
            artifact_ids=[_artifact_id(artifact)],
            fact_refs=[fact.fact_id for fact in facts if fact.source.artifact_id == _artifact_id(artifact)],
            evidence_refs=[_semantic_id("evidence", _artifact_id(artifact), schema_name)],
        )
        for artifact, _payload, schema_name in recognized
        if contract.projector_id != "agent2.structure.viewer_scene" and (
            schema_name in contract.table_schemas
            or (contract.primary_as_table and schema_name in contract.primary_schemas)
            or (
                schema_name.startswith("tool:")
                and str(artifact.get("type") or "")
                in {
                    "table_json",
                    "table_csv",
                    "metrics_json",
                    "structure_json",
                }
            )
        )
    ]

    methods: list[MethodRecord] = []
    steps_by_id = {
        str(step.get("step_id") or step.get("stepId")): step
        for step in context.capability_plan.get("steps") or []
    }
    for call in sorted(context.tool_calls, key=lambda value: str(value.get("stepId") or value.get("step_id"))):
        step_id = str(call.get("stepId") or call.get("step_id"))
        step = steps_by_id.get(step_id) or {}
        methods.append(
            MethodRecord(
                method_id=_semantic_id("method", context.research_turn_id, step_id),
                capability_id=str(step.get("capability_id") or contract.projector_id.removeprefix("agent2.")),
                capability_version=str(step.get("capability_version") or "1.0"),
                tool_id=str(call.get("toolId") or call.get("tool_id") or "") or None,
                parameters=dict(call.get("paramsJson") or call.get("params_json") or call.get("params") or {}),
                source_object_refs=list(context.source_object_refs),
            )
        )

    limitations = [
        ScientificLimitation(
            limitation_id=_semantic_id("limitation", contract.projector_id, code),
            code=code,
            message=message,
            source_ref=contract.projector_id,
        )
        for code, message in contract.limitations
    ]
    for artifact, payload, _schema_name in primary:
        if contract.projector_id == "agent2.volumetric.data":
            existing_codes = {item.code for item in limitations}
            limitations.extend(item for item in volumetric_field_limitations(_artifact_id(artifact), payload) if item.code not in existing_codes)
        for index, message in enumerate(payload.get("limitations") or []):
            limitations.append(
                ScientificLimitation(
                    limitation_id=_semantic_id("limitation", _artifact_id(artifact), str(index), str(message)),
                    code="TOOL_DECLARED_LIMITATION",
                    message=str(message),
                    source_ref=_artifact_id(artifact),
                )
            )

    warnings: list[ScientificWarning] = []
    if contract.projector_id == "agent2.data.table_analysis":
        for artifact, payload, _ in primary:
            warnings.extend(table_warnings(_artifact_id(artifact), payload))
    if contract.projector_id in COORDINATION_PROJECTORS:
        for artifact, payload, _ in primary:
            warnings.extend(coordination_warnings(context, artifact, payload))
    outcome = str(context.execution_summary.get("execution_outcome") or context.execution_summary.get("outcome") or "SUCCESS")
    if outcome == "PARTIAL":
        warnings.append(
            ScientificWarning(
                warning_id=_semantic_id("warning", context.research_turn_id, "partial"),
                code="PARTIAL_EXECUTION",
                message="Only successfully committed scientific outputs are included.",
            )
        )

    bundle = ScientificResultBundle(
        schema_version="1.0",
        result_id=UUID(str(uuid5(NAMESPACE_URL, f"mdi-agent2-result:{context.research_turn_id}:{contract.projector_id}"))),
        project_id=context.project_id,
        research_session_id=context.research_session_id,
        research_turn_id=UUID(str(context.research_turn_id)),
        research_question=context.research_question,
        source_object_refs=list(context.source_object_refs),
        execution_status=outcome,
        relevance_status=ResultRelevanceStatus.CURRENT,
        result_items=[item],
        facts=facts,
        figures=figures,
        tables=tables,
        output_object_refs=[],
        evidence=evidence,
        methods=methods,
        limitations=limitations,
        warnings=warnings,
        provenance=ProvenanceRecord(
            research_turn_id=UUID(str(context.research_turn_id)),
            job_id=str(context.execution_summary.get("job_id") or ""),
            analysis_plan_id=context.analysis_plan_id or str(context.execution_summary.get("analysis_plan_id") or "") or None,
            capability_plan_id=context.capability_plan_id,
            execution_summary_id=str(context.execution_summary.get("id") or "") or None,
            source_object_version_ids=[ref.version_id for ref in context.source_object_refs],
            tool_call_ids=sorted(str(call.get("id")) for call in context.tool_calls),
            artifact_ids=artifact_ids,
            projector_ids=[contract.projector_id],
        ),
        projection_version="agent2.result/1.0",
    )
    return ScientificResultProjection(bundle=bundle, projector_id=contract.projector_id, projector_version=contract.version)


class CanonicalScientificResultProjector:
    version = "1.1"

    def __init__(self, contract: ProjectorContract) -> None:
        self.contract = contract
        self.projector_id = contract.projector_id
        self.version = contract.version

    def project(self, context: ScientificResultProjectionContext) -> ScientificResultProjection:
        return _project(context, self.contract)


def _contracts() -> tuple[ProjectorContract, ...]:
    def count(pointer: str, predicate: str) -> FactDeclaration:
        return FactDeclaration(predicate, pointer, "count")
    return (
        ProjectorContract(
            "agent2.structure.rdf", "径向分布函数", "structure.rdf",
            ("phase10e7.rdf.v1",), ("phase10e7.static_chart.v1",), (),
            facts=(
                count("/structureCount", "rdf.structure_count"),
                count("/limits/bin_count", "rdf.bin_count"),
                FactDeclaration("rdf.r_max", "/parameters/r_max_angstrom", "angstrom"),
                FactDeclaration("rdf.bin_width", "/parameters/bin_width_angstrom", "angstrom"),
                FactDeclaration("rdf.number_density", "/rdf/normalization/number_density_per_angstrom3", "angstrom^-3"),
            ),
            limitations=(("RDF_NO_PROJECTOR_PEAK_DETECTION", "The result projector does not infer peaks or coordination shells from the RDF curve."),),
        ),
        ProjectorContract(
            "agent2.diffraction.theoretical_xrd", "理论 XRD 图谱", "diffraction.xrd.theoretical",
            ("phase10e4.xrd_pattern.v1",), ("phase10e4.static_chart.v1",), (),
            facts=(count("/pattern/peak_count", "xrd.peak_count"), FactDeclaration("xrd.wavelength", "/radiation/wavelength_angstrom", "angstrom"),
                   FactDeclaration("xrd.two_theta_min", "/two_theta_range/0", "degree"),
                   FactDeclaration("xrd.two_theta_max", "/two_theta_range/1", "degree"),
                   FactDeclaration("xrd.intensity_scale", "/pattern/intensity_scale"),
                   count("/limits/peak_count_before_limit", "xrd.peak_count_before_limit")),
            fact_builder=_xrd_peak_facts, version="1.2",
            limitations=(("XRD_THEORETICAL_ONLY", "理论 XRD 来自所提供的周期晶体结构，不是实验测量；不能据此证明物相纯度或把单个位点视为独立衍射来源。"),
                         ("XRD_MODEL_SCOPE", "当前模型不包含峰形展宽或 Rietveld 精修；relative_100 表示每份结构的最高计算峰强度归一到 100，不能用来比较不同结构的绝对强度。"),
                         ("XRD_RETAINED_PEAK_SCOPE", "主要峰事实仅展示已保存峰中强度最高的至多五个峰，每峰至多四组已保存晶面族；峰数量受扫描范围、强度阈值和保留上限约束。")),
        ),
        ProjectorContract(
            "agent2.diffraction.experimental_theoretical_comparison", "实验与理论 XRD 比较", "diffraction.xrd.comparison",
            ("phase10n3.experimental_xrd_comparison.v1",), ("phase10n3.experimental_xrd_comparison_plot.v1",), (),
            facts=(
                count("/residualSummary/matchedCount", "xrd.matched_peak_count"),
                count("/coverage/unmatchedExperimentalPeaks", "xrd.unmatched_experimental_peak_count"),
                count("/coverage/unmatchedTheoreticalPeaks", "xrd.unmatched_theoretical_peak_count"),
                FactDeclaration("xrd.mean_peak_shift", "/residualSummary/meanSignedDeltaTwoTheta", "degree"),
                FactDeclaration("xrd.peak_shift_mae", "/residualSummary/maeDeltaTwoTheta", "degree"),
                FactDeclaration("xrd.peak_shift_rmse", "/residualSummary/rmseDeltaTwoTheta", "degree"),
                FactDeclaration("xrd.max_peak_shift", "/residualSummary/maxAbsoluteDeltaTwoTheta", "degree"),
            ),
        ),
        ProjectorContract(
            "agent2.ml.regression_evaluation", "材料回归评估", "ml.regression.evaluation",
            ("phase10k3.materials_ml_regression.v1",), (), (),
            accepted_tool_ids=(
                "ml.basic_metrics",
                "ml.density_scatter",
                "ml.error_distribution",
                "ml.outlier_table",
            ),
            required_tool_ids=(
                "ml.basic_metrics",
                "ml.density_scatter",
                "ml.error_distribution",
                "ml.outlier_table",
            ),
            fact_builder=_ml_facts, version="1.2",
        ),
        ProjectorContract(
            "agent2.ml.uncertainty_evaluation", "材料预测不确定性", "ml.uncertainty.evaluation",
            ("phase10k3.materials_ml_uncertainty.v1",), (), (), fact_builder=_ml_uncertainty_facts,
        ),
        ProjectorContract(
            "agent2.ml.classification_evaluation", "材料分类评估", "ml.classification.evaluation",
            ("phase10k3.materials_ml_classification.v1",), (), (), fact_builder=_ml_classification_facts,
        ),
        ProjectorContract(
            "agent2.structure.summary", "结构晶格与对称性摘要", "structure.summary",
            ("phase10c1.structure_summary.v2",), (), (),
            accepted_tool_ids=(
                "structure.lattice_summary",
                "structure.preview_metadata",
                "structure.spacegroup_summary",
            ),
            version="1.1",
            fact_builder=_structure_summary_facts,
            limitations=(
                (
                    "STRUCTURE_SUMMARY_SUPPLIED_STRUCTURE_ONLY",
                    "Lattice and symmetry facts describe only the supplied validated structure and do not infer material properties.",
                ),
            ),
        ),
        ProjectorContract(
            "agent2.structure.viewer_scene", "结构查看器场景", "structure.viewer_scene",
            ("phase10f18.viewer_scene.v2", "phase10d1.viewer_scene.v1"),
            ("phase10f18.viewer_scene.v2", "phase10d1.viewer_scene.v1"), (),
            version="1.3", primary_as_table=False,
            accepted_tool_ids=(
                "structure.structure_3d",
                "structure.viewer_3d",
            ),

        ),
        ProjectorContract(
            "agent2.trajectory.viewer_scene", "轨迹查看器产品", "trajectory.viewer",
            (
                TRAJECTORY_SCHEMA_VERSION,
                TRAJECTORY_SUMMARY_SCHEMA_VERSION,
                TRAJECTORY_PARSE_REPORT_SCHEMA_VERSION,
                TRAJECTORY_MANIFEST_SCHEMA_VERSION,
            ), (), (),
            version="1.3",
            primary_as_table=False,
            limitations=(
                ("TRAJECTORY_VIEWER_INERT", "The trajectory viewer product preserves validated trajectory data and launch metadata; it does not compute MSD, diffusion, RDF, or infer dynamic bonds."),
            ),
        ),
        ProjectorContract(
            "agent2.trajectory.msd", "轨迹均方位移", "trajectory.msd",
            ("phase10n4.trajectory_msd.v1",), ("phase10n4.trajectory_plot.v1",), (),
            version="1.2",
            facts=(
                count("/coverage/frames", "trajectory.frame_count"),
                count("/coverage/atoms", "trajectory.msd_atom_count"),
                FactDeclaration("trajectory.msd_species", "/species"),
                count("/trajectory/frameCount", "trajectory.source_frame_count"),
                count("/analysisWindow/selectedFrameCount", "trajectory.analysis_frame_count"),
                count("/analysisWindow/userFacingRange/firstFrameInclusive", "trajectory.analysis_first_frame"),
                count("/analysisWindow/userFacingRange/lastFrameInclusive", "trajectory.analysis_last_frame"),
                FactDeclaration("trajectory.analysis_start_time", "/analysisWindow/timeRange/start", "picosecond"),
                FactDeclaration("trajectory.analysis_end_time", "/analysisWindow/timeRange/end", "picosecond"),
                count("/coverage/validLags", "trajectory.msd_lag_count"),
            ),
            fact_builder=_trajectory_msd_facts,
            limitations=(("MSD_SERIES_NOT_SCALAR_FACTS", "MSD curves remain saved structured data. Scalar facts expose only saved endpoint values and origin counts; they do not establish linearity, isotropy, or a diffusive regime."),),
        ),
        ProjectorContract(
            "agent2.trajectory.diffusion", "轨迹扩散性质", "trajectory.diffusion",
            ("phase10n4.trajectory_diffusion.v1",), ("phase10n4.trajectory_plot.v1",), (),
            version="1.2",
            facts=(
                FactDeclaration("trajectory.diffusion_coefficient", "/diffusionEstimate/value", "angstrom^2/picosecond"),
                count("/trajectory/frameCount", "trajectory.source_frame_count"),
                count("/analysisWindow/selectedFrameCount", "trajectory.analysis_frame_count"),
                count("/analysisWindow/userFacingRange/firstFrameInclusive", "trajectory.analysis_first_frame"),
                count("/analysisWindow/userFacingRange/lastFrameInclusive", "trajectory.analysis_last_frame"),
                FactDeclaration("trajectory.diffusion_fit_start_time", "/fitWindow/startPs", "picosecond"),
                FactDeclaration("trajectory.diffusion_fit_end_time", "/fitWindow/endPs", "picosecond"),
                count("/fitWindow/pointCount", "trajectory.diffusion_fit_point_count"),
                FactDeclaration("trajectory.diffusion_fit_duration", "/fitWindow/durationPs", "picosecond"),
                FactDeclaration("trajectory.diffusion_fit_r2", "/fit/rSquared"),
                FactDeclaration("trajectory.diffusion_fit_rmse", "/fit/rmseAngstrom2", "angstrom^2"),
                FactDeclaration("trajectory.diffusion_regime", "/regimeDiagnostic/status"),
                FactDeclaration("trajectory.diffusion_minimum_duration", "/resolvedParameters/minimum_fit_duration_ps", "picosecond"),
                count("/resolvedParameters/minimum_fit_points", "trajectory.diffusion_minimum_points"),
                FactDeclaration("trajectory.diffusion_origin_coverage", "/regimeDiagnostic/originCoverage"),
                FactDeclaration("trajectory.diffusion_minimum_origin_coverage", "/resolvedParameters/minimum_origin_coverage"),
                FactDeclaration("trajectory.diffusion_minimum_r2", "/resolvedParameters/minimum_r_squared"),
                FactDeclaration("trajectory.diffusion_alpha", "/regimeDiagnostic/alpha"),
                FactDeclaration("trajectory.diffusion_alpha_min", "/resolvedParameters/alpha_min"),
                FactDeclaration("trajectory.diffusion_alpha_max", "/resolvedParameters/alpha_max"),
            ),
            limitations=(("DIFFUSION_REQUIRES_ACCEPTED_WINDOW", "Fit statistics alone do not establish diffusion. A diffusion coefficient is available only when the saved diagnostic accepts the selected window; a rejected window must not be reported as a measured diffusion coefficient."),),
        ),
        ProjectorContract(
            "agent2.phonon.band", "声子能带", "phonon.band",
            ("phase10h.phonon_summary.v1", "phase10h.phonon_band.v1"), ("phase10h1.phonon_band_plot.v1",), ("phase10h1.phonon_band_table.v1",),
            version="1.3", primary_as_table=False,
            facts=(
                count("/branch_count", "phonon.branch_count"), count("/qpoint_count", "phonon.qpoint_count"),
                FactDeclaration("phonon.frequency_min", "/frequency_min", "terahertz"),
                FactDeclaration("phonon.frequency_max", "/frequency_max", "terahertz"),
                count("/imaginary_mode_count", "phonon.imaginary_mode_count"),
            ),
            limitations=(("PHONON_EIGENVECTORS_UNAVAILABLE", "The current band Artifact does not provide eigenvectors or animation authority."),),
        ),
        ProjectorContract(
            "agent2.phonon.dos", "声子态密度", "phonon.dos",
            ("phase10h2.phonon_dos_summary.v1",), ("phase10h2.phonon_dos_plot.v1",), ("phase10h2.phonon_dos_table.v1",),
            facts=(
                FactDeclaration("phonon.dos_frequency_min", "/frequency_min", "terahertz"),
                FactDeclaration("phonon.dos_frequency_max", "/frequency_max", "terahertz"),
                FactDeclaration("phonon.dos_integral", "/observed_integral", "modes"),
                count("/projection_count", "phonon.dos_projection_count"),
            ),
            limitations=(("PHONON_EIGENVECTORS_UNAVAILABLE", "The current DOS Artifact does not provide eigenvectors or animation authority."),),
        ),
        ProjectorContract(
            "agent2.phonon.band_dos", "声子能带与态密度", "phonon.band_dos",
            ("phase10h.phonon_band_dos_summary.v1",), ("phase10h.phonon_band_dos_plot.v1",), ("phase10h.phonon_band_dos_table.v1",),
            facts=(
                FactDeclaration("phonon.frequency_min", "/frequency_min", "terahertz"),
                FactDeclaration("phonon.frequency_max", "/frequency_max", "terahertz"),
                FactDeclaration("phonon.dos_integral", "/dos_integral", "modes"),
                count("/imaginary_band_mode_count", "phonon.imaginary_mode_count"),
            ),
            limitations=(("PHONON_EIGENVECTORS_UNAVAILABLE", "The combined Artifact is a static band/DOS result and does not provide eigenvectors or animation authority."),),
        ),
        ProjectorContract(
            "agent2.structure.brillouin_zone",
            "布里渊区与高对称路径",
            "reciprocal.brillouin_zone",
            (
                RECIPROCAL_LATTICE_SCHEMA_VERSION,
                BRILLOUIN_ZONE_SCHEMA_VERSION,
                KPATH_SCHEMA_VERSION,
            ),
            (BRILLOUIN_ZONE_SCHEMA_VERSION,),
            (RECIPROCAL_LATTICE_SCHEMA_VERSION, KPATH_SCHEMA_VERSION),
            required_primary_schemas=(
                RECIPROCAL_LATTICE_SCHEMA_VERSION,
                BRILLOUIN_ZONE_SCHEMA_VERSION,
                KPATH_SCHEMA_VERSION,
            ),
            fact_builder=_brillouin_zone_facts,
            limitations=(
                (
                    "BRILLOUIN_ZONE_STRUCTURE_BOUND",
                    "The reciprocal-space result is derived only from the exact authorized periodic structure.",
                ),
            ),
        ),
        ProjectorContract(
            "agent2.structure.coordination_hist", "配位数分布", "structure.coordination.hist",
            ("phase10e1.coordination_hist.v1",), ("phase10e1.static_chart.v1",), (),
            facts=(FactDeclaration("structure.coordination_site_count", "/histogram/total_sites", "count"),),
            limitations=(("COORDINATION_HIST_NO_NEW_NEIGHBOR_SEARCH", "The result references the validated coordination Artifact and does not recompute neighbors."),),
        ),
        ProjectorContract(
            "agent2.structure.coordination_analysis",
            "局域配位综合分析",
            "structure.coordination.analysis",
            (),
            (),
            (),
            accepted_tool_ids=(
                "structure.coordination_crystalnn",
                "structure.coordination_hist",
                "structure.coordination_voronoinn",
                "structure.local_environment_polyhedra",
            ),
            required_tool_ids=(
                "structure.coordination_crystalnn",
                "structure.coordination_hist",
                "structure.coordination_voronoinn",
                "structure.local_environment_polyhedra",
            ),
            limitations=(
                (
                    "COORDINATION_METHODS_REPORTED_SEPARATELY",
                    "CrystalNN, VoronoiNN, cutoff histograms, and local-environment polyhedra retain their individual method provenance.",
                ),
            ),
        ),
        *(
            ProjectorContract(
                f"agent2.structure.local_environment_{method}", f"{label} 配位多面体", "structure.local_environment.polyhedra",
                (source_schema, N2_SCHEMA), (N2_SCHEMA,), (),
                required_primary_schemas=(source_schema, N2_SCHEMA), primary_as_table=False,
                limitations=(("LOCAL_ENVIRONMENT_GEOMETRY_ONLY", "配位多面体使用已保存的算法近邻；几何分类和连接不代表确定的化学键、氧化态或结构稳定性。"),),
                version="1.0",
            )
            for method, label, source_schema in (
                ("crystalnn", "CrystalNN", "phase10n1.crystalnn_coordination.v1"),
                ("voronoi", "VoronoiNN", "phase10n1.voronoinn_coordination.v1"),
            )
        ),
        ProjectorContract(
            "agent2.structure.coordination_crystalnn", "CrystalNN 局域配位", "structure.coordination.crystalnn",
            ("phase10n1.crystalnn_coordination.v1",), (), (),
            facts=(FactDeclaration("structure.coordination_successful_sites", "/coverage/successfulSites", "count"),),
            version="1.2",
            limitations=(("COORDINATION_GEOMETRY_ONLY", "配位数与近邻取决于所用算法及参数，不能据此认定化学键或结构稳定性。"),),
        ),
        ProjectorContract(
            "agent2.structure.coordination_voronoinn", "VoronoiNN 局域配位", "structure.coordination.voronoi",
            ("phase10n1.voronoinn_coordination.v1",), (), (),
            facts=(FactDeclaration("structure.coordination_successful_sites", "/coverage/successfulSites", "count"),),
            version="1.2",
            limitations=(("COORDINATION_GEOMETRY_ONLY", "配位数与近邻取决于所用算法及参数，不能据此认定化学键或结构稳定性。"),),
        ),
        ProjectorContract(
            "agent2.trajectory.rdf", "轨迹径向分布函数", "trajectory.rdf",
            ("phase10n4.trajectory_rdf.v1",), ("phase10n4.trajectory_plot.v1",), (),
            facts=(
                FactDeclaration("trajectory.frame_count", "/trajectory/frameCount", "count"),
                FactDeclaration("trajectory.atom_count", "/trajectory/atomCount", "count"),
                count("/analysisWindow/selectedFrameCount", "trajectory.analysis_frame_count"),
                count("/analysisWindow/userFacingRange/firstFrameInclusive", "trajectory.analysis_first_frame"),
                count("/analysisWindow/userFacingRange/lastFrameInclusive", "trajectory.analysis_last_frame"),
                FactDeclaration("trajectory.analysis_start_time", "/analysisWindow/timeRange/start", "picosecond"),
                FactDeclaration("trajectory.analysis_end_time", "/analysisWindow/timeRange/end", "picosecond"),
                FactDeclaration("trajectory.rdf_included_frames", "/coverage/includedFrames", "count"),
                FactDeclaration("trajectory.rdf_pair_samples", "/coverage/pairSamples", "count"),
                FactDeclaration("trajectory.rdf_r_min", "/resolvedParameters/r_min_angstrom", "angstrom"),
                FactDeclaration("trajectory.rdf_r_max", "/resolvedParameters/r_max_angstrom", "angstrom"),
                FactDeclaration("trajectory.rdf_bin_count", "/resolvedParameters/bin_count", "count"),
            ),
            limitations=(("TRAJECTORY_RDF_SERIES_REFERENCED", "RDF series remain bounded structured evidence; the projector does not detect peaks."),),
        ),
        ProjectorContract(
            "agent2.electronic.band_structure", "电子能带", "electronic.band_structure",
            ("phase10n5.electronic_band_structure.v1",), ("phase10n5.electronic_band_plot.v1",), (), version="1.2",
            facts=(FactDeclaration("electronic.band_gap", "/gap/valueEv", "eV"), FactDeclaration("electronic.kpoint_count", "/coverage/kpointCount", "count")),
            limitations=(("ELECTRONIC_DATA_SUPPLIED", "Band values are supplied electronic data; no DFT/GW calculation or interpolation is executed."),),
        ),
        ProjectorContract(
            "agent2.electronic.dos", "电子态密度", "electronic.dos",
            ("phase10n5.electronic_dos.v1",), ("phase10n5.electronic_dos_plot.v1",), (), version="1.2",
            facts=(FactDeclaration("electronic.energy_point_count", "/coverage/energyPointCount", "count"),),
            limitations=(("ELECTRONIC_DATA_SUPPLIED", "DOS values are supplied electronic data; no new electronic calculation is executed."),),
        ),
        ProjectorContract(
            "agent2.data.composition_space", "材料组成空间", "data.composition_space",
            ("phase10k4.composition_space.v1",), ("phase10k4.composition_space_plot.v1",), (),
            facts=(
                count("/coverage/selectedRows", "composition.selected_row_count"),
                count("/coverage/validCompositionSamples", "composition.valid_sample_count"),
                count("/coverage/invalidCompositionSamples", "composition.invalid_sample_count"),
                count("/featureRepresentation/featureDimensions", "composition.feature_dimension_count"),
                count("/projection/dimensions", "composition.projection_dimension_count"),
                count("/projection/rank", "composition.projection_rank"),
                FactDeclaration(
                    "composition.cumulative_explained_variance_ratio",
                    "/projection/cumulativeExplainedVarianceRatio",
                ),
            ),
            limitations=(("COMPOSITION_SPACE_DESCRIPTIVE", "Composition-space projection is descriptive and does not establish material identity or causality."),),
        ),
        ProjectorContract(
            "agent2.data.materials_explorer", "材料数据集探索", "data.materials_explorer",
            ("phase10k2.dataset_materials_explorer.v1",), ("phase10k2.dataset_materials_explorer_plot.v1",), (),
            fact_builder=_dataset_facts,
            limitations=(("MATERIALS_EXPLORER_BOUNDED", "Only the bounded, profile-authorized dataset projection is included."),),
        ),
        ProjectorContract(
            "agent2.data.composition_analysis",
            "材料组成与化学体系分析",
            "data.composition_analysis",
            (),
            (),
            (),
            accepted_tool_ids=(
                "composition.chem_sys_sunburst",
                "composition.chem_sys_treemap",
                "composition.elements_hist",
                "composition.formula_statistics",
                "composition.ptable_heatmap",
                "composition.summary",
                "structure.composition_from_structure",
            ),
            required_tool_ids=(
                "composition.chem_sys_sunburst",
                "composition.chem_sys_treemap",
                "composition.elements_hist",
                "composition.formula_statistics",
                "composition.ptable_heatmap",
                "composition.summary",
                "structure.composition_from_structure",
            ),
            limitations=(
                (
                    "COMPOSITION_ANALYSIS_DESCRIPTIVE",
                    "Composition and chemical-system distributions are descriptive summaries of the supplied authorized table.",
                ),
            ),
        ),
        ProjectorContract(
            "agent2.data.table_analysis",
            "数值表格分布与相关性分析",
            "data.table_analysis",
            (),
            (),
            (),
            fact_builder=table_facts,
            version="1.6",
            accepted_tool_ids=(
                "table.distribution_summary",
                "table.numeric_summary",
                "viz.correlation",
                "viz.histogram",
                "viz.scatter",
            ),
            required_tool_ids=(
                "table.distribution_summary",
                "table.numeric_summary",
                "viz.correlation",
                "viz.histogram",
                "viz.scatter",
            ),
            limitations=(
                (
                    "TABLE_ANALYSIS_DESCRIPTIVE",
                    "Distribution, correlation, and scatter products describe the supplied columns and do not establish causality.",
                ),
            ),
        ),
        ProjectorContract(
            "agent2.volumetric.data", "体数据字段", "volumetric.field",
            ("phase10j.volumetric_field.v1", "phase10j.volumetric_dataset.v1"), (), (),
            fact_builder=_volumetric_facts,
            version="1.9",
            primary_as_table=False,
            limitations=(("VOLUMETRIC_SAVED_FIELD_ONLY", "Conclusions are limited to the saved volumetric field and statistics; rendered surfaces and slices do not independently establish physical properties."),),
        ),
    )


def build_canonical_result_projectors() -> list[CanonicalScientificResultProjector]:
    return [CanonicalScientificResultProjector(contract) for contract in _contracts()]
