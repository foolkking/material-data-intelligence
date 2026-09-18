"""Validate scientific qualification evidence against canonical Capabilities."""

from __future__ import annotations

import ast
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, computed_field

from mdi_api.research_agent.capabilities.quality_evidence import (
    QUALITY_EVIDENCE_BY_CAPABILITY,
    QUALITY_EVIDENCE_VERSION,
    CapabilityQualityEvidence,
    ReferenceAuthority,
    ScientificEvidenceKind,
    ScientificQualificationLevel,
    scientific_contract_fingerprint,
)


QualityIssueSeverity = Literal["ERROR", "WARNING", "INFO"]
_REFERENCE_AUTHORITIES = {
    ReferenceAuthority.ANALYTICAL,
    ReferenceAuthority.INDEPENDENT_IMPLEMENTATION,
    ReferenceAuthority.PUBLISHED_REFERENCE,
    ReferenceAuthority.CURATED_KNOWN_RESULT,
    ReferenceAuthority.SYNTHETIC_EXACT,
}
_KNOWN_UNITS = {
    "1/angstrom",
    "angstrom",
    "angstrom^-1",
    "angstrom^-3",
    "angstrom^2",
    "angstrom^3",
    "angstrom^2/ps",
    "cm^-1",
    "count",
    "degree",
    "dimensionless",
    "eV",
    "fraction",
    "meV",
    "ps",
    "relative_intensity",
    "states/eV",
    "states/THz",
    "target_unit",
    "THz",
}


class ScientificQualityIssue(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    severity: QualityIssueSeverity
    code: str
    message: str
    capability_id: str | None = None
    evidence_id: str | None = None


class CapabilityQualityInventoryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    capability_id: str
    capability_version: str
    display_name: str
    pack_id: str | None
    tool_ids: list[str]
    adapter_names: list[str]
    result_projector: str | None
    qualification_level: str
    reproducibility: str
    applicability_domains: list[str]
    known_limitations: list[str]
    qualified_contract_fingerprint: str
    current_contract_fingerprint: str
    evidence_fingerprint: str
    evidence_counts: dict[str, int]
    reference_authorities: list[str]
    units: list[str]
    conventions: list[str]
    evidence_refs: list[str]
    status: Literal["VALID", "INCOMPLETE", "STALE"]


class ScientificQualityHealthReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    evidence_version: str
    capability_count: int
    qualification_counts: dict[str, int]
    reference_case_count: int
    invariant_case_count: int
    domain_negative_case_count: int
    adapter_semantics_case_count: int
    artifact_semantics_case_count: int
    result_projection_case_count: int
    interpretation_evaluation_case_count: int
    report_evaluation_case_count: int
    integration_case_count: int
    scientific_defects_discovered: int = 0
    scientific_defects_fixed: int = 0
    issues: list[ScientificQualityIssue]
    capabilities: list[CapabilityQualityInventoryEntry]
    inventory_fingerprint: str

    @computed_field
    @property
    def accepted(self) -> bool:
        return not any(item.severity == "ERROR" for item in self.issues)

    @computed_field
    @property
    def error_count(self) -> int:
        return sum(item.severity == "ERROR" for item in self.issues)


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def _issue(
    issues: list[ScientificQualityIssue],
    severity: QualityIssueSeverity,
    code: str,
    message: str,
    *,
    capability_id: str | None = None,
    evidence_id: str | None = None,
) -> None:
    issues.append(
        ScientificQualityIssue(
            severity=severity,
            code=code,
            message=message,
            capability_id=capability_id,
            evidence_id=evidence_id,
        )
    )


def _test_function_exists(root: Path, node: str) -> tuple[bool, str | None]:
    path_text, separator, function_text = node.partition("::")
    if not separator or not function_text:
        return False, "evidence test_node must use path::function"
    path = root / path_text
    if not path.is_file():
        return False, f"test file does not exist: {path_text}"
    function_name = function_text.split("[", 1)[0]
    try:
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    except (OSError, SyntaxError) as exc:
        return False, f"test file cannot be inspected: {exc}"
    functions = {
        item.name
        for item in ast.walk(tree)
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    if function_name not in functions:
        return False, f"test function does not exist: {function_name}"
    return True, None


def _validate_promotion(
    item: CapabilityQualityEvidence,
    issues: list[ScientificQualityIssue],
) -> None:
    kinds = Counter(link.kind for link in item.evidence)
    independent_references = [
        link
        for link in item.evidence
        if link.kind == ScientificEvidenceKind.REFERENCE
        and link.reference_authority in _REFERENCE_AUTHORITIES
    ]
    regression_references = [
        link
        for link in item.evidence
        if link.kind == ScientificEvidenceKind.REFERENCE
        and link.reference_authority == ReferenceAuthority.REGRESSION_ONLY
    ]
    if (
        item.qualification_level
        in {
            ScientificQualificationLevel.REFERENCE_VALIDATED,
            ScientificQualificationLevel.DOMAIN_VALIDATED,
            ScientificQualificationLevel.CROSS_IMPLEMENTATION_VALIDATED,
        }
        and not independent_references
    ):
        _issue(
            issues,
            "ERROR",
            "QUALIFICATION_WITHOUT_REFERENCE",
            "Scientific qualification requires analytical, independent, published, curated, or exact synthetic reference evidence.",
            capability_id=item.capability_id,
        )
    if regression_references and not independent_references:
        _issue(
            issues,
            "ERROR",
            "REGRESSION_ONLY_PROMOTION",
            "Regression-only output cannot promote scientific qualification.",
            capability_id=item.capability_id,
        )
    if item.qualification_level == ScientificQualificationLevel.DOMAIN_VALIDATED:
        required = {
            ScientificEvidenceKind.REFERENCE,
            ScientificEvidenceKind.INVARIANT,
            ScientificEvidenceKind.DOMAIN_NEGATIVE,
        }
        missing = sorted(kind.value for kind in required if not kinds[kind])
        if missing:
            _issue(
                issues,
                "ERROR",
                "DOMAIN_QUALIFICATION_INCOMPLETE",
                "DOMAIN_VALIDATED requires reference, invariant, and domain-negative evidence: "
                + ", ".join(missing),
                capability_id=item.capability_id,
            )
    if (
        item.qualification_level
        == ScientificQualificationLevel.CROSS_IMPLEMENTATION_VALIDATED
        and not any(
            link.reference_authority == ReferenceAuthority.INDEPENDENT_IMPLEMENTATION
            for link in item.evidence
        )
    ):
        _issue(
            issues,
            "ERROR",
            "CROSS_IMPLEMENTATION_REFERENCE_MISSING",
            "CROSS_IMPLEMENTATION_VALIDATED requires an independent implementation.",
            capability_id=item.capability_id,
        )
    if (
        item.qualification_level
        == ScientificQualificationLevel.EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED
        and not any(
            link.reference_authority
            in {
                ReferenceAuthority.OFFICIAL_LIBRARY_SEMANTICS,
                ReferenceAuthority.EXTERNAL_SOLVER_SEMANTICS,
            }
            for link in item.evidence
        )
    ):
        _issue(
            issues,
            "ERROR",
            "EXTERNAL_SEMANTICS_REFERENCE_MISSING",
            "External implementation semantics status requires explicit library/solver evidence.",
            capability_id=item.capability_id,
        )


def validate_scientific_quality(
    extension_report: Any,
    *,
    registries: Any | None = None,
    evidence_by_capability: dict[str, CapabilityQualityEvidence] | None = None,
    repository_root: Path | None = None,
) -> ScientificQualityHealthReport:
    """Validate quality evidence and generate an inventory over live Capabilities."""

    records = evidence_by_capability or QUALITY_EVIDENCE_BY_CAPABILITY
    root = repository_root or Path(__file__).resolve().parents[5]
    issues: list[ScientificQualityIssue] = []
    extension_by_id = {item.capability_id: item for item in extension_report.capabilities}
    manifests_by_id = {
        item.capability_id: item
        for item in registries.capabilities.list_all()
    } if registries is not None else {}

    missing_records = sorted(set(extension_by_id) - set(records))
    extra_records = sorted(set(records) - set(extension_by_id))
    for capability_id in missing_records:
        _issue(
            issues,
            "ERROR",
            "MISSING_QUALITY_RECORD",
            "Registered Capability has no explicit scientific quality status.",
            capability_id=capability_id,
        )
    for capability_id in extra_records:
        _issue(
            issues,
            "ERROR",
            "ORPHAN_QUALITY_RECORD",
            "Quality record does not resolve to a registered Capability.",
            capability_id=capability_id,
        )

    entries: list[CapabilityQualityInventoryEntry] = []
    unique_evidence: dict[str, Any] = {}
    for capability_id in sorted(set(extension_by_id) & set(records)):
        extension = extension_by_id[capability_id]
        record = records[capability_id]
        manifest = manifests_by_id.get(capability_id)
        current_fingerprint = (
            scientific_contract_fingerprint(manifest)
            if manifest is not None
            else ""
        )
        if manifest is None:
            _issue(
                issues,
                "ERROR",
                "CAPABILITY_MANIFEST_UNAVAILABLE",
                "Current Capability manifest is required for qualification freshness validation.",
                capability_id=capability_id,
            )
        before = sum(item.severity == "ERROR" for item in issues)
        stale = current_fingerprint != record.qualified_contract_fingerprint
        if stale:
            _issue(
                issues,
                "ERROR",
                "STALE_QUALIFICATION",
                "Capability scientific contract changed after the linked evidence was reviewed.",
                capability_id=capability_id,
            )
        if extension.qualification_level != record.qualification_level.value:
            _issue(
                issues,
                "ERROR",
                "QUALIFICATION_SUMMARY_MISMATCH",
                "Capability manifest qualification does not match canonical quality evidence.",
                capability_id=capability_id,
            )
        expected_counts = record.evidence_counts
        summary_mismatches = {
            "evidence_version": (
                extension.qualification_evidence_version,
                QUALITY_EVIDENCE_VERSION,
            ),
            "evidence_fingerprint": (
                extension.qualification_evidence_fingerprint,
                record.evidence_fingerprint,
            ),
            "reference_case_count": (
                extension.qualification_reference_case_count,
                expected_counts.get(ScientificEvidenceKind.REFERENCE.value, 0),
            ),
            "invariant_case_count": (
                extension.qualification_invariant_case_count,
                expected_counts.get(ScientificEvidenceKind.INVARIANT.value, 0),
            ),
            "domain_negative_case_count": (
                extension.qualification_domain_negative_case_count,
                expected_counts.get(
                    ScientificEvidenceKind.DOMAIN_NEGATIVE.value,
                    0,
                ),
            ),
            "result_projection_case_count": (
                extension.qualification_result_projection_case_count,
                expected_counts.get(
                    ScientificEvidenceKind.RESULT_PROJECTION.value,
                    0,
                ),
            ),
            "interpretation_evaluation_count": (
                extension.qualification_interpretation_evaluation_count,
                expected_counts.get(ScientificEvidenceKind.INTERPRETATION.value, 0),
            ),
            "report_evaluation_count": (
                extension.qualification_report_evaluation_count,
                expected_counts.get(ScientificEvidenceKind.REPORT.value, 0),
            ),
            "reproducibility": (
                extension.qualification_reproducibility,
                record.reproducibility,
            ),
        }
        mismatched_fields = sorted(
            key for key, (actual, expected) in summary_mismatches.items()
            if actual != expected
        )
        if mismatched_fields:
            _issue(
                issues,
                "ERROR",
                "QUALIFICATION_EVIDENCE_SUMMARY_MISMATCH",
                "Capability manifest evidence summary differs from the canonical record: "
                + ", ".join(mismatched_fields),
                capability_id=capability_id,
            )
        if sorted(extension.qualification_validated_domains) != sorted(
            record.applicability_domains
        ) or extension.qualification_known_limitations != record.known_limitations:
            _issue(
                issues,
                "ERROR",
                "QUALIFICATION_SCOPE_MISMATCH",
                "Capability applicability or limitation summary differs from quality evidence.",
                capability_id=capability_id,
            )
        _validate_promotion(record, issues)
        for link in record.evidence:
            previous = unique_evidence.get(link.evidence_id)
            if previous is not None and previous != link:
                _issue(
                    issues,
                    "ERROR",
                    "CONFLICTING_EVIDENCE_ID",
                    "The same evidence identity has conflicting definitions.",
                    capability_id=capability_id,
                    evidence_id=link.evidence_id,
                )
            unique_evidence[link.evidence_id] = link
            ok, error = _test_function_exists(root, link.test_node)
            if not ok:
                _issue(
                    issues,
                    "ERROR",
                    "INVALID_EVIDENCE_TEST_NODE",
                    error or "evidence test node is invalid",
                    capability_id=capability_id,
                    evidence_id=link.evidence_id,
                )
            unknown_units = sorted(set(link.units) - _KNOWN_UNITS)
            if link.tolerance is not None and link.tolerance.unit not in _KNOWN_UNITS:
                unknown_units.append(link.tolerance.unit)
            if unknown_units:
                _issue(
                    issues,
                    "ERROR",
                    "UNKNOWN_SCIENTIFIC_UNIT",
                    "Unknown units: " + ", ".join(sorted(set(unknown_units))),
                    capability_id=capability_id,
                    evidence_id=link.evidence_id,
                )
            if link.numeric and link.tolerance is None:
                _issue(
                    issues,
                    "ERROR",
                    "NUMERIC_EVIDENCE_WITHOUT_TOLERANCE",
                    "Numeric evidence requires an explicit scientific tolerance.",
                    capability_id=capability_id,
                    evidence_id=link.evidence_id,
                )
        after = sum(item.severity == "ERROR" for item in issues)
        status: Literal["VALID", "INCOMPLETE", "STALE"]
        status = "STALE" if stale else ("VALID" if before == after else "INCOMPLETE")
        entries.append(
            CapabilityQualityInventoryEntry(
                capability_id=capability_id,
                capability_version=record.capability_version,
                display_name=extension.display_name,
                pack_id=extension.pack_id,
                tool_ids=extension.tool_ids,
                adapter_names=extension.adapter_names,
                result_projector=extension.result_projector,
                qualification_level=record.qualification_level.value,
                reproducibility=record.reproducibility,
                applicability_domains=record.applicability_domains,
                known_limitations=record.known_limitations,
                qualified_contract_fingerprint=record.qualified_contract_fingerprint,
                current_contract_fingerprint=current_fingerprint,
                evidence_fingerprint=record.evidence_fingerprint,
                evidence_counts=record.evidence_counts,
                reference_authorities=sorted(
                    {link.reference_authority.value for link in record.evidence}
                ),
                units=sorted(
                    {
                        unit
                        for link in record.evidence
                        for unit in (
                            *link.units,
                            *([link.tolerance.unit] if link.tolerance else []),
                        )
                    }
                ),
                conventions=sorted(
                    {value for link in record.evidence for value in link.conventions}
                ),
                evidence_refs=sorted({link.test_node for link in record.evidence}),
                status=status,
            )
        )

    total_kinds: Counter[ScientificEvidenceKind] = Counter()
    for link in unique_evidence.values():
        total_kinds[link.kind] += link.case_count
    qualification_counts = Counter(
        item.qualification_level.value for item in records.values()
    )
    fingerprint_payload = [
        item.model_dump(mode="json") for item in sorted(entries, key=lambda row: row.capability_id)
    ]
    return ScientificQualityHealthReport(
        evidence_version=QUALITY_EVIDENCE_VERSION,
        capability_count=len(extension_by_id),
        qualification_counts={
            key: qualification_counts[key] for key in sorted(qualification_counts)
        },
        reference_case_count=total_kinds[ScientificEvidenceKind.REFERENCE],
        invariant_case_count=total_kinds[ScientificEvidenceKind.INVARIANT],
        domain_negative_case_count=total_kinds[ScientificEvidenceKind.DOMAIN_NEGATIVE],
        adapter_semantics_case_count=total_kinds[
            ScientificEvidenceKind.ADAPTER_SEMANTICS
        ],
        artifact_semantics_case_count=total_kinds[
            ScientificEvidenceKind.ARTIFACT_SEMANTICS
        ],
        result_projection_case_count=total_kinds[
            ScientificEvidenceKind.RESULT_PROJECTION
        ],
        interpretation_evaluation_case_count=total_kinds[
            ScientificEvidenceKind.INTERPRETATION
        ],
        report_evaluation_case_count=total_kinds[ScientificEvidenceKind.REPORT],
        integration_case_count=total_kinds[ScientificEvidenceKind.INTEGRATION],
        issues=issues,
        capabilities=entries,
        inventory_fingerprint=_digest(fingerprint_payload),
    )


__all__ = [
    "CapabilityQualityInventoryEntry",
    "ScientificQualityHealthReport",
    "ScientificQualityIssue",
    "validate_scientific_quality",
]
