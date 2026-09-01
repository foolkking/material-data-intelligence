from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ReportQualityAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    report_id: str
    scientific_result_snapshot_id: str
    criterion_scores: dict[int, int | None]
    normalized_score: float = Field(ge=0, le=100)
    quality_pass: bool
    limitations: list[str]


def evaluate_report_quality(
    snapshot: dict[str, Any],
    result_bundle: dict[str, Any],
    *,
    result_snapshot_id: str,
) -> ReportQualityAssessment:
    """Score the checked-in 20-point rubric from persisted authority only.

    The evaluator deliberately scores structural/scientific correctness. Human
    review remains necessary for prose elegance and is recorded separately.
    """

    report = dict(snapshot.get("report") or {})
    findings = list(report.get("main_findings") or [])
    facts = list(result_bundle.get("facts") or [])
    figures = list(result_bundle.get("figures") or [])
    tables = list(result_bundle.get("tables") or [])
    evidence = list(result_bundle.get("evidence") or [])
    methods = list(result_bundle.get("methods") or [])
    result_items = list(result_bundle.get("result_items") or [])
    result_limitations = list(result_bundle.get("limitations") or [])
    warnings = list(result_bundle.get("warnings") or [])
    source_refs = list(result_bundle.get("source_object_refs") or [])

    report_fact_refs = {
        str(ref)
        for item in findings
        for ref in item.get("fact_refs") or []
    }
    for section_name in ("discussion", "conclusion"):
        section = report.get(section_name)
        if isinstance(section, dict):
            report_fact_refs.update(str(ref) for ref in section.get("fact_refs") or [])
    authoritative_fact_refs = {str(item.get("fact_id")) for item in facts}
    evidence_refs = {str(item.get("evidence_id")) for item in evidence}
    reported_evidence = {str(item) for item in report.get("evidence_refs") or []}
    report_text = json.dumps(report, ensure_ascii=False)
    contains_raw_dump = any(
        token in report_text
        for token in ('"bundle_json"', '"provider_response"', '"contract_version": {')
    )

    numeric_facts = [
        item for item in facts
        if isinstance(item.get("value"), (int, float)) and not isinstance(item.get("value"), bool)
    ]
    numeric_fact_refs = {str(item.get("fact_id")) for item in numeric_facts}
    referenced_numeric_facts = report_fact_refs & numeric_fact_refs
    numeric_coverage = bool(referenced_numeric_facts) and report_fact_refs.issubset(
        authoritative_fact_refs
    )
    exact_sources = bool(source_refs) and all(
        item.get("object_id") and item.get("version_id") for item in source_refs
    )
    report_sources = list(report.get("data_sources") or [])
    partial = str(result_bundle.get("execution_status")) == "PARTIAL"
    partial_disclosed = not partial or bool(report.get("limitations")) or bool(warnings)

    scores: dict[int, int | None] = {
        1: 2 if report.get("research_question") else 0,
        2: 2 if report.get("research_question") and report.get("summary") else 0,
        3: 2 if exact_sources and report_sources else 0,
        4: 2 if report.get("method_summary") and methods else 0,
        5: 2 if findings else 0,
        6: (2 if numeric_coverage else 0) if numeric_facts else None,
        7: (2 if report.get("primary_figures") else 0) if figures else None,
        8: (2 if result_items and report.get("supporting_results") is not None else 0) if tables else None,
        9: 2 if reported_evidence and reported_evidence.issubset(evidence_refs) else 0,
        10: (
            2
            if report.get("discussion")
            and (
                len(result_items) > 1
                or len(findings) > 1
                or bool(report_fact_refs)
            )
            else 1
        ),
        11: 2 if report.get("discussion") else 0,
        12: 2 if report.get("limitations") or not result_limitations else 0,
        13: 2 if partial_disclosed else 0,
        14: 2 if report.get("conclusion") else 0,
        15: 2 if report.get("next_steps") else None,
        16: 2 if report.get("title") and report.get("summary") else 0,
        17: 2 if findings and report.get("discussion") and report.get("conclusion") else 1,
        18: 0 if contains_raw_dump else 2,
        19: 2 if snapshot.get("grounding_status") == "VALID" else 0,
        20: (
            2
            if exact_sources
            and str(snapshot.get("scientific_result_snapshot_id"))
            == str(result_snapshot_id)
            else 0
        ),
    }
    applicable = [score for score in scores.values() if score is not None]
    normalized = round(100 * sum(applicable) / (2 * len(applicable)), 1)
    critical = {3, 6, 9, 12, 13, 20}
    quality_pass = (
        all(score != 0 for score in applicable)
        and normalized >= 85
        and all(scores[index] in {2, None} for index in critical)
    )
    limitations: list[str] = [
        "Deterministic scoring verifies structure, grounding and provenance; prose elegance requires bounded human review."
    ]
    if scores[7] is None:
        limitations.append("Figure criterion is N/A because the authoritative Result has no Figure.")
    if scores[8] is None:
        limitations.append("Table criterion is N/A because the authoritative Result has no Table.")
    if scores[15] is None:
        limitations.append("Next-steps criterion is N/A because the immutable Report omitted editorial next steps.")
    return ReportQualityAssessment(
        report_id=str(snapshot.get("report_id")),
        scientific_result_snapshot_id=str(snapshot.get("scientific_result_snapshot_id")),
        criterion_scores=scores,
        normalized_score=normalized,
        quality_pass=quality_pass,
        limitations=limitations,
    )


__all__ = ["ReportQualityAssessment", "evaluate_report_quality"]
