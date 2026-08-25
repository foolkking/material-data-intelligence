from __future__ import annotations

import math
import re
from typing import Any

from .schemas import GroundingValidationResult, ScientificInterpretationOutput, numeric_tokens


# Keep temperature ``K`` case-sensitive: a lowercase ``k`` in labels such as
# ``k-point`` is not a Kelvin unit and must not trigger unit grounding.
_UNIT = re.compile(
    r"(?<![A-Za-z])(?:(?i:Å|angstrom|nm|pm|eV|meV|fs|ps|%|THz|cm-?1|1/s|m\^?2/s)|K)(?![A-Za-z])"
)


def _unit_key(value: str) -> str:
    normalized = value.strip().lower().replace("angstrom", "å")
    return normalized.replace("cm-1", "cm1")


def _number_key(token: str) -> str:
    cleaned = token.replace(",", "").rstrip("%")
    try:
        value = float(cleaned)
    except ValueError:
        return cleaned
    if not math.isfinite(value):
        return cleaned
    return format(value, ".15g")


def _fact_values(bundle: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], set[str], set[str]]:
    facts = {str(item.get("fact_id")): item for item in bundle.get("facts") or []}
    evidence = {str(item.get("evidence_id")) for item in bundle.get("evidence") or []}
    result_items = {str(item.get("id")) for item in bundle.get("result_items") or []}
    return facts, evidence, result_items


class EvidenceReferenceValidator:
    def validate(self, interpretation: ScientificInterpretationOutput, result_bundle: Any) -> GroundingValidationResult:
        bundle = result_bundle.model_dump(mode="json") if hasattr(result_bundle, "model_dump") else dict(result_bundle)
        facts, evidence, result_items = _fact_values(bundle)
        errors: list[str] = []
        for finding in [*interpretation.primary_findings, *interpretation.supporting_findings]:
            refs = [*finding.fact_refs, *finding.evidence_refs, *finding.result_item_refs]
            if not finding.fact_refs and not finding.evidence_refs:
                errors.append(f"{finding.finding_id}: positive finding has no fact/evidence reference")
            if any(ref not in facts for ref in finding.fact_refs):
                errors.append(f"{finding.finding_id}: unknown fact reference")
            if any(ref not in evidence for ref in finding.evidence_refs):
                errors.append(f"{finding.finding_id}: unknown evidence reference")
            if any(ref not in result_items for ref in finding.result_item_refs):
                errors.append(f"{finding.finding_id}: unknown result-item reference")
            if any(not str(ref).strip() for ref in refs):
                errors.append(f"{finding.finding_id}: empty reference")
        if any(ref not in result_items for ref in interpretation.primary_result_refs):
            errors.append("unknown primary result reference")
        if any(ref not in result_items for ref in interpretation.supporting_result_refs):
            errors.append("unknown supporting result reference")
        if not interpretation.primary_result_refs and not interpretation.supporting_result_refs:
            errors.append("interpretation must reference at least one result item")
        return GroundingValidationResult(valid=not errors, errors=errors)


class QuantitativeClaimValidator:
    def validate(self, interpretation: ScientificInterpretationOutput, result_bundle: Any) -> GroundingValidationResult:
        bundle = result_bundle.model_dump(mode="json") if hasattr(result_bundle, "model_dump") else dict(result_bundle)
        facts, _, _ = _fact_values(bundle)
        errors: list[str] = []
        for finding in [*interpretation.primary_findings, *interpretation.supporting_findings]:
            referenced = [facts[ref] for ref in finding.fact_refs if ref in facts]
            supported_numbers = {_number_key(str(fact.get("value"))) for fact in referenced if isinstance(fact.get("value"), (int, float)) and not isinstance(fact.get("value"), bool)}
            claim_numbers = {_number_key(token) for token in numeric_tokens(finding.statement)}
            if not claim_numbers.issubset(supported_numbers):
                errors.append(f"{finding.finding_id}: quantitative claim is not supported by referenced facts")
            units = {_unit_key(item) for item in _UNIT.findall(finding.statement)}
            supported_units = {_unit_key(str(fact.get("unit"))) for fact in referenced if fact.get("unit")}
            if units and not units.issubset(supported_units):
                errors.append(f"{finding.finding_id}: unit is absent from referenced facts")
        finding_numbers = {_number_key(token) for token in numeric_tokens(" ".join(item.statement for item in [*interpretation.primary_findings, *interpretation.supporting_findings]))}
        if not {_number_key(token) for token in numeric_tokens(interpretation.answer_lead)}.issubset(finding_numbers):
            errors.append("answer_lead introduces an unsupported quantitative claim")
        return GroundingValidationResult(valid=not errors, errors=errors)


def validate_interpretation(interpretation: ScientificInterpretationOutput, result_bundle: Any) -> GroundingValidationResult:
    errors: list[str] = []
    refs = EvidenceReferenceValidator().validate(interpretation, result_bundle)
    errors.extend(refs.errors)
    quantities = QuantitativeClaimValidator().validate(interpretation, result_bundle)
    errors.extend(quantities.errors)
    bundle = result_bundle.model_dump(mode="json") if hasattr(result_bundle, "model_dump") else dict(result_bundle)
    execution = str(bundle.get("execution_status", ""))
    all_text = " ".join([interpretation.answer_lead, *(item.statement for item in [*interpretation.primary_findings, *interpretation.supporting_findings])]).lower()
    if execution == "PARTIAL" and any(term in all_text for term in ("complete analysis", "all steps succeeded", "全部分析均成功", "完整分析已完成")):
        errors.append("partial result cannot be described as complete")
    return GroundingValidationResult(valid=not errors, errors=errors)


__all__ = ["EvidenceReferenceValidator", "QuantitativeClaimValidator", "validate_interpretation"]
