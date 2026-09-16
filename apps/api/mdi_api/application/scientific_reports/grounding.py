from __future__ import annotations

import re
import math
from typing import Any

from mdi_api.domain.scientific_reports.contracts import ScientificReportOutput

_NUMBER = re.compile(r"(?<![A-Za-z0-9_.])[-+]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][-+]?\d+)?%?")
# Keep temperature ``K`` case-sensitive.  Electronic reports commonly use
# ``k-point``/``k 点`` labels; treating the lowercase ``k`` as Kelvin makes
# an otherwise grounded report fail closed for the wrong reason.
_UNIT = re.compile(
    r"(?<![A-Za-z0-9])(?:(?i:"
    r"(?:Å|angstrom)(?:\^\{?2\}?|²)/(?:ps|picosecond)|"
    r"(?:Å|angstrom)(?:\^\{?2\}?|²)|"
    r"(?:Å|angstrom)(?:\^\{?-?3\}?|⁻³|-3)?|"
    r"picosecond|nm|pm|eV|meV|fs|ps|%|THz|terahertz|cm-?1|1/s|m\^?2/s"
    r")|K)(?![A-Za-z0-9])"
)


def _canonical_unit(value: object) -> str:
    normalized = (
        str(value)
        .strip()
        .lower()
        .replace("angstrom", "å")
        .replace("⁻³", "^-3")
        .replace("²", "^2")
        .replace("{", "")
        .replace("}", "")
        .replace(" ", "")
    )
    normalized = re.sub(r"^(å)-3$", r"\1^-3", normalized)
    normalized = normalized.replace("cm-1", "cm1")
    return {
        "terahertz": "thz",
        "ps": "picosecond",
        "å^2/ps": "å^2/picosecond",
    }.get(normalized, normalized)


def _numeric_tokens(text: str) -> set[str]:
    """Extract numeric claims while ignoring identifier suffixes such as mat-2.

    Scientific prose frequently names stable samples/rows with hyphenated
    identifiers.  The numeric suffix is not a claim and must not be compared
    with ScientificResult facts.
    """
    text = _UNIT.sub(" ", text or "")
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
            errors.extend(self._numeric_errors(
                figure.caption,
                figure.fact_refs,
                facts,
                "figure",
                evidence_refs=figure.evidence_refs,
                evidence=evidence,
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
    ) -> list[str]:
        numbers = _numeric_tokens(text)
        supported_ids = {ref for ref in fact_refs if ref in facts}
        for ref in evidence_refs or []:
            item = (evidence or {}).get(ref)
            if item:
                supported_ids.update(
                    str(fact_ref)
                    for fact_ref in item.get("supports_fact_refs") or []
                    if str(fact_ref) in facts
                )
        for ref in result_item_refs or []:
            item = (result_items or {}).get(ref)
            if item:
                supported_ids.update(
                    str(fact_ref)
                    for fact_ref in item.get("fact_refs") or []
                    if str(fact_ref) in facts
                )
        referenced = [facts[ref] for ref in sorted(supported_ids)]
        supported = [
            float(fact.get("value"))
            for fact in referenced
            if isinstance(fact.get("value"), (int, float)) and not isinstance(fact.get("value"), bool)
        ]
        errors = []
        for token in numbers:
            try:
                value = float(token)
            except ValueError:
                errors.append(f"{label} contains an unsupported numeric claim")
                continue
            decimals = len(token.split(".", 1)[1]) if "." in token else 0
            if not any(
                math.isclose(value, candidate, rel_tol=1e-9, abs_tol=1e-9)
                or round(candidate, decimals) == round(value, decimals)
                for candidate in supported
            ):
                errors.append(f"{label} contains an unsupported numeric claim")
                break
        units = {_canonical_unit(unit) for unit in _UNIT.findall(text or "")}
        supported_units = {_canonical_unit(fact.get("unit")) for fact in referenced if fact.get("unit")}
        unsupported_units = sorted(units - supported_units)
        if unsupported_units:
            errors.append(f"{label} contains an unsupported unit: {', '.join(unsupported_units)}")
        return errors


__all__ = ["ReportGroundingValidator"]
