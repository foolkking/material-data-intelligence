from __future__ import annotations

from mdi_api.application.scientific_reasoning.derived_claims import derived_product_errors

import re
import math
from decimal import Decimal
from typing import Any

from mdi_api.domain.scientific_reports.contracts import ScientificReportOutput
from mdi_api.application.interpretation.grounding import _support_fact_ids, _numeric_claim_matches_fact, exclude_reciprocal_path_labels
from mdi_api.application.scientific_reasoning.follow_ups import report_next_steps_text
from mdi_api.application.scientific_reasoning.units import (
    UNIT_PATTERN as _UNIT,
    canonical_unit as _canonical_unit,
    supported_fact_units,
    exclude_saved_column_labels,
    reference_version_claims,
    parameter_claimed_units,
    exclude_saved_parameter_expressions,
)

_NUMBER = re.compile(r"(?<![A-Za-z0-9_.])[-+]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][-+]?\d+)?%?")


def _numeric_tokens(text: str) -> set[str]:
    """Extract numeric claims while ignoring identifier suffixes such as mat-2.

    Scientific prose frequently names stable samples/rows with hyphenated
    identifiers.  The numeric suffix is not a claim and must not be compared
    with ScientificResult facts.
    """
    text = _UNIT.sub(" ", text or "")
    text = re.sub(r"(?i)(?<![A-Za-z0-9])R\s*\^\s*2(?![A-Za-z0-9])", "R-squared", text)
    tokens: set[str] = set()
    for match in _NUMBER.finditer(text):
        start, end = match.span()
        before = text[start - 1] if start else ""
        after = text[end] if end < len(text) else ""
        prefix = text[max(0, start - 8):start]
        suffix = text[end:min(len(text), end + 8)]
        # Opaque scientific identities (UUIDs, content/version hashes and
        # alphanumeric stable sample/resource ids) are provenance labels, not
        # quantitative claims.  A numeric token directly embedded in such an
        # identifier must not be compared with Result facts.  Preserve normal
        # scientific notation such as ``1e-3`` by only applying this guard
        # when the adjacent alphabetic character is not an exponent marker
        # followed by a numeric exponent.
        exponent_suffix = after in {"e", "E"} and len(suffix) > 1 and (suffix[1].isdigit() or suffix[1] in "+-")
        exponent_prefix = before in {"e", "E"} and prefix and prefix[-2:-1].isdigit()
        if (before.isalpha() and not exponent_prefix) or (after.isalpha() and not exponent_suffix):
            continue
        if before == "-" and prefix and prefix[-2:-1].isalnum():
            continue
        if after == "-" and suffix and suffix[1:2].isalnum():
            continue
        tokens.add(match.group(0).rstrip("%"))
    return tokens


class ReportGroundingValidator:
    def validate(self, report: ScientificReportOutput, *, bundle: Any, interpretation: dict[str, Any]) -> list[str]:
        b = bundle.model_dump(mode="json") if hasattr(bundle, "model_dump") else dict(bundle)
        facts = {str(item.get("fact_id")): item for item in b.get("facts", [])}
        evidence = {str(item.get("evidence_id")): item for item in b.get("evidence", [])}
        items = {str(item.get("id")): item for item in b.get("result_items", [])}
        figures = {str(item.get("figure_id")): item for item in b.get("figures", [])}
        limitations = {str(item.get("limitation_id")): item for item in b.get("limitations", [])}
        data_sources = {f"source_{index}" for index, _ in enumerate(b.get("source_object_refs", []), start=1)}
        interpretation_findings = self._interpretation_finding_ids(interpretation)
        errors: list[str] = []
        if report.next_steps is not None and report.next_steps.text != report_next_steps_text(interpretation, b):
            errors.append("next_steps must copy the source-bound interpretation suggestions exactly or be null")
        narrative_sections = [section for section in (report.discussion, report.conclusion, report.next_steps) if section is not None]
        source_text = " ".join([
            report.summary,
            report.method_summary,
            report.reproducibility_summary,
            *(section.text for section in narrative_sections),
            *(f.statement for f in report.main_findings),
            *(f.caption for f in report.primary_figures),
            *(limitation.statement for limitation in report.limitations),
        ])
        # A report summary is an editorial roll-up of the complete bounded
        # result, so it may cite any authoritative fact from the bundle even
        # when the detailed finding references are narrower.  It still
        # remains fail-closed: every numeric token must match a persisted fact.
        errors.extend(self._numeric_errors(report.summary, list(facts), facts, "summary"))
        for label, section in (
            ("discussion", report.discussion),
            ("conclusion", report.conclusion),
            ("next_steps", report.next_steps),
        ):
            if section is None:
                continue
            errors.extend(self._unknown(f"{label}.fact_refs", section.fact_refs, facts))
            errors.extend(self._unknown(f"{label}.evidence_refs", section.evidence_refs, evidence))
            errors.extend(self._numeric_errors(
                section.text,
                section.fact_refs,
                facts,
                label,
                evidence_refs=section.evidence_refs,
                evidence=evidence,
                result_items=items,
            ))
        for finding in report.main_findings:
            if not (finding.finding_refs or finding.fact_refs or finding.evidence_refs):
                errors.append("main finding lacks an upstream grounding reference")
            errors.extend(self._unknown("finding.fact_refs", finding.fact_refs, facts))
            errors.extend(self._unknown("finding.evidence_refs", finding.evidence_refs, evidence))
            errors.extend(self._unknown("finding.finding_refs", finding.finding_refs, interpretation_findings))
            if (
                finding.reasoning_assessment is not None
                and not finding.reasoning_assessment.accepted
            ):
                errors.append("report finding contains rejected scientific reasoning")
            inherited_findings = [
                interpretation_findings[ref]
                for ref in finding.finding_refs
                if ref in interpretation_findings
            ]
            errors.extend(self._numeric_errors(
                finding.statement,
                [
                    *finding.fact_refs,
                    *(
                        str(ref)
                        for item in inherited_findings
                        for ref in item.get("fact_refs", item.get("factRefs", []))
                    ),
                ],
                facts,
                "finding",
                evidence_refs=[
                    *finding.evidence_refs,
                    *(
                        str(ref)
                        for item in inherited_findings
                        for ref in item.get("evidence_refs", item.get("evidenceRefs", []))
                    ),
                ],
                evidence=evidence,
                result_item_refs=[
                    str(ref)
                    for item in inherited_findings
                    for ref in item.get("result_item_refs", item.get("resultItemRefs", []))
                ],
                result_items=items,
            ))
        for figure in report.primary_figures:
            if figure.figure_ref not in figures:
                errors.append(f"unknown figure reference: {figure.figure_ref}")
            errors.extend(self._unknown("figure.fact_refs", figure.fact_refs, facts))
            errors.extend(self._unknown("figure.evidence_refs", figure.evidence_refs, evidence))
            saved_figure = figures.get(figure.figure_ref, {})
            product_ids = _support_fact_ids(
                fact_refs=saved_figure.get("fact_refs") or [],
                evidence_refs=saved_figure.get("evidence_refs") or [],
                result_item_refs=[], facts=facts, evidence_items=evidence, result_items=items,
            )
            errors.extend(self._numeric_errors(
                figure.caption,
                figure.fact_refs,
                facts,
                "figure",
                evidence_refs=figure.evidence_refs,
                evidence=evidence,
                result_items=items,
                figure_type=str(figures.get(figure.figure_ref, {}).get("figure_type", "")),
                product_support=[facts[ref] for ref in sorted(product_ids)],
            ))
        for item in report.supporting_results:
            if item.result_item_ref not in items:
                errors.append(f"unknown result item reference: {item.result_item_ref}")
        for limitation in report.limitations:
            errors.extend(self._unknown("limitation.source_refs", limitation.source_refs, limitations | evidence))
        errors.extend(self._unknown("report.evidence_refs", report.evidence_refs, evidence))
        errors.extend(self._unknown("report.data_sources", report.data_sources, data_sources))
        if b.get("execution_status") == "PARTIAL" and any(term in source_text.lower() for term in ("complete analysis", "all steps succeeded", "全部分析均成功", "完整分析已完成")):
            errors.append("partial result cannot be described as complete")
        relevance = str(b.get("relevance_status") or "")
        if relevance in {"STALE", "SOURCE_MISSING", "INVALIDATED"} and not any(term in source_text.lower() for term in ("historical", "历史", "stale", "不可访问", "invalidated", "失效")):
            errors.append("historical relevance warning must be preserved")
        return errors

    @staticmethod
    def _interpretation_finding_ids(interpretation: dict[str, Any]) -> dict[str, Any]:
        data = interpretation.get("interpretation") or {}
        return {str(item.get("finding_id")): item for item in [*(data.get("primary_findings") or []), *(data.get("supporting_findings") or [])]}

    @staticmethod
    def _unknown(label: str, refs: list[str], known: dict[str, Any] | set[str]) -> list[str]:
        return [f"{label} contains unknown reference: {ref}" for ref in refs if ref not in known]

    @staticmethod
    def _numeric_errors(
        text: str,
        fact_refs: list[str],
        facts: dict[str, Any],
        label: str,
        *,
        evidence_refs: list[str] | None = None,
        evidence: dict[str, Any] | None = None,
        result_item_refs: list[str] | None = None,
        result_items: dict[str, Any] | None = None,
        figure_type: str = "",
        product_support: list[dict[str, Any]] | None = None,
    ) -> list[str]:
        supported_ids = _support_fact_ids(
            fact_refs=fact_refs, evidence_refs=evidence_refs or [], result_item_refs=result_item_refs or [],
            facts=facts, evidence_items=evidence or {}, result_items=result_items or {},
        )
        referenced = [facts[ref] for ref in sorted(supported_ids)]
        claim_text = exclude_saved_parameter_expressions(exclude_saved_column_labels(text, referenced), referenced)
        version_errors = []
        if any(fact.get("predicate") == "reference.version" for fact in facts.values()):
            claim_text, unsupported_versions = reference_version_claims(claim_text, referenced)
            version_errors = [f"{label} contains an unsupported reference version ({version})"
                              for version in unsupported_versions]
        numbers = _numeric_tokens(claim_text)
        supported = [
            float(fact.get("value"))
            for fact in referenced
            if isinstance(fact.get("value"), (int, float)) and not isinstance(fact.get("value"), bool)
        ]
        # The exact figure's saved graph can establish qualitative product
        # availability, but never supplies unrequested numeric/unit citations.
        errors = [*version_errors, *derived_product_errors(text, [*referenced, *(product_support or [])], label)]
        for token in numbers:
            try:
                value = float(token)
            except ValueError:
                errors.append(f"{label} contains an unsupported numeric claim ({token})")
                continue
            # Reports retain their coarser display rounding (2.84 -> 2.8),
            # but never erase small nonzero quantities with an absolute floor.
            if not any(_numeric_claim_matches_fact(token, candidate, relative_limit=Decimal("0.05")) for candidate in supported):
                errors.append(f"{label} contains an unsupported numeric claim ({token})")
                break
        # The exact persisted figure's type establishes only label semantics;
        # it grants no additional numeric or unit evidence to its caption.
        unit_context = [*referenced, {"predicate": figure_type}] if figure_type else referenced
        unit_claim_text = exclude_reciprocal_path_labels(claim_text or "", unit_context)
        units = {_canonical_unit(unit) for unit in _UNIT.findall(unit_claim_text)} | parameter_claimed_units(unit_claim_text, referenced)
        supported_units = supported_fact_units(referenced)
        unsupported_units = sorted(units - supported_units)
        if unsupported_units:
            errors.append(f"{label} contains an unsupported unit: {', '.join(unsupported_units)}")
        return errors


__all__ = ["ReportGroundingValidator"]
