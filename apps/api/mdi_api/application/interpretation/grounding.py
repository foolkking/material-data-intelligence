from __future__ import annotations

import math
import re
from decimal import Decimal, InvalidOperation
from typing import Any

from mdi_api.domain.interpretation.contracts import GroundingValidationResult, ScientificInterpretationOutput, numeric_tokens


# Keep temperature ``K`` case-sensitive: a lowercase ``k`` in labels such as
# ``k-point`` is not a Kelvin unit and must not trigger unit grounding.
_UNIT = re.compile(
    r"(?<![A-Za-z])(?:(?i:"
    r"(?:Å|angstrom)(?:\^\{?2\}?|²)/(?:ps|picosecond)|"
    r"(?:Å|angstrom)(?:\^\{?2\}?|²)|"
    r"(?:Å|angstrom)(?:\^\{?-?3\}?|⁻³|-3)?|"
    r"picosecond|nm|pm|eV|meV|fs|ps|%|THz|cm-?1|1/s|m\^?2/s"
    r")|K)(?![A-Za-z])"
)


def _unit_key(value: str) -> str:
    normalized = (
        value.strip()
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
    # This is spelling normalization only.  No scientific conversion is
    # performed: the persisted canonical phonon unit ``terahertz`` and its
    # standard symbol ``THz`` represent the same unit.
    return {
        "terahertz": "thz",
        "ps": "picosecond",
        "å^2/ps": "å^2/picosecond",
    }.get(normalized, normalized)


def _number_key(token: str) -> str:
    cleaned = token.replace(",", "").rstrip("%")
    try:
        value = float(cleaned)
    except ValueError:
        return cleaned
    if not math.isfinite(value):
        return cleaned
    return format(value, ".15g")


_NUMERIC_LITERAL = re.compile(
    r"^[+-]?(?:(?:\d+(?:\.\d*)?)|(?:\.\d+))(?:[eE][+-]?\d+)?$"
)


def _numeric_claim_matches_fact(token: str, fact_value: int | float) -> bool:
    """Accept only bounded lexical display rounding of an authoritative fact.

    Scientific prose commonly shortens persisted values for readability.  The
    validator still needs to reject arbitrary nearby numbers, unit conversion,
    and unsupported claims, so the tolerance is derived from the token's
    decimal resolution and capped at 1% of the authoritative magnitude.
    """

    cleaned = token.replace(",", "").rstrip("%").strip()
    if not _NUMERIC_LITERAL.fullmatch(cleaned):
        return False
    try:
        claimed = Decimal(cleaned)
        authoritative = Decimal(str(fact_value))
        if not claimed.is_finite() or not authoritative.is_finite():
            return False
        coefficient, _, exponent_text = cleaned.lower().partition("e")
        _, dot, fractional = coefficient.partition(".")
        fraction_digits = len(fractional) if dot else 0
        exponent = int(exponent_text or "0")
        resolution = Decimal(10) ** (exponent - fraction_digits)
        difference = abs(claimed - authoritative)
        relative_cap = max(abs(authoritative) * Decimal("0.01"), Decimal("1e-12"))
        tolerance = min(abs(resolution) / Decimal(2), relative_cap)
        return difference <= tolerance
    except (InvalidOperation, ValueError, OverflowError):
        return False


def _claim_numeric_tokens(text: str) -> list[str]:
    """Return scientific quantities while excluding numeric unit exponents."""

    return numeric_tokens(_UNIT.sub(" ", text or ""))


def _fact_values(bundle: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], set[str], set[str]]:
    facts = {str(item.get("fact_id")): item for item in bundle.get("facts") or []}
    evidence = {str(item.get("evidence_id")) for item in bundle.get("evidence") or []}
    result_items = {str(item.get("id")) for item in bundle.get("result_items") or []}
    return facts, evidence, result_items


def _finding_fact_support(
    finding: Any,
    bundle: dict[str, Any],
    facts: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Resolve the bounded authoritative support graph for one finding.

    Providers sometimes cite the exact Result item or Evidence item while
    omitting one of that item's individual fact IDs. Result items and Evidence
    already persist their fact edges, so following those edges is stricter and
    more truthful than either rejecting a supported claim or accepting prose
    without quantitative authority.
    """

    supported_ids = {
        str(ref)
        for ref in finding.fact_refs
        if str(ref) in facts
    }
    result_items = {
        str(item.get("id")): item
        for item in bundle.get("result_items") or []
        if isinstance(item, dict)
    }
    evidence_items = {
        str(item.get("evidence_id")): item
        for item in bundle.get("evidence") or []
        if isinstance(item, dict)
    }
    for ref in finding.result_item_refs:
        item = result_items.get(str(ref))
        if item:
            supported_ids.update(
                str(fact_ref)
                for fact_ref in item.get("fact_refs") or []
                if str(fact_ref) in facts
            )
    for ref in finding.evidence_refs:
        item = evidence_items.get(str(ref))
        if item:
            supported_ids.update(
                str(fact_ref)
                for fact_ref in item.get("supports_fact_refs") or []
                if str(fact_ref) in facts
            )
    return [facts[fact_id] for fact_id in sorted(supported_ids)]


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
            referenced = _finding_fact_support(finding, bundle, facts)
            supported_values = [
                fact.get("value")
                for fact in referenced
                if isinstance(fact.get("value"), (int, float))
                and not isinstance(fact.get("value"), bool)
            ]
            supported_numbers = {_number_key(str(value)) for value in supported_values}
            claim_tokens = _claim_numeric_tokens(finding.statement)
            unsupported_tokens = [
                token
                for token in claim_tokens
                if _number_key(token) not in supported_numbers
                and not any(
                    _numeric_claim_matches_fact(token, value)
                    for value in supported_values
                )
            ]
            if unsupported_tokens:
                unsupported = ", ".join(sorted({_number_key(token) for token in unsupported_tokens}))
                errors.append(
                    f"{finding.finding_id}: quantitative claim is not supported "
                    f"by referenced facts ({unsupported})"
                )
            units = {_unit_key(item) for item in _UNIT.findall(finding.statement)}
            supported_units = {_unit_key(str(fact.get("unit"))) for fact in referenced if fact.get("unit")}
            if units and not units.issubset(supported_units):
                errors.append(f"{finding.finding_id}: unit is absent from referenced facts")
        finding_numbers = {
            _number_key(token)
            for token in _claim_numeric_tokens(
                " ".join(
                    item.statement
                    for item in [
                        *interpretation.primary_findings,
                        *interpretation.supporting_findings,
                    ]
                )
            )
        }
        if not {
            _number_key(token)
            for token in _claim_numeric_tokens(interpretation.answer_lead)
        }.issubset(finding_numbers):
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


def project_grounded_answer_lead(
    interpretation: ScientificInterpretationOutput,
    result_bundle: Any,
) -> ScientificInterpretationOutput:
    """Replace only an unsupported lead with an already-grounded finding.

    ``answer_lead`` is presentation prose, not an independent scientific
    authority. Providers occasionally add a quantitative summary to the lead
    while returning otherwise valid, fully referenced findings. Keeping that
    text would correctly fail grounding; discarding the whole interpretation
    would make the product control fail despite having a safe deterministic
    projection available.

    This helper never repairs a finding, reference, unit, or Result claim. It
    only selects the first referenced finding statement as the lead, and only
    accepts the projection if the complete interpretation then passes the
    unchanged fail-closed validator.
    """

    validation = validate_interpretation(interpretation, result_bundle)
    if validation.valid or validation.errors != [
        "answer_lead introduces an unsupported quantitative claim"
    ]:
        return interpretation
    findings = [*interpretation.primary_findings, *interpretation.supporting_findings]
    if not findings:
        return interpretation
    projected = interpretation.model_copy(update={"answer_lead": findings[0].statement})
    return projected if validate_interpretation(projected, result_bundle).valid else interpretation


def project_grounded_communication(
    interpretation: ScientificInterpretationOutput,
    result_bundle: Any,
) -> ScientificInterpretationOutput:
    """Keep free-form communication inside the persisted Result boundary.

    Findings already require exact fact/evidence references.  The lead is
    therefore projected from those referenced findings instead of accepting
    additional unreferenced provider prose.  Limitations are projected only
    from authoritative Result limitations; general domain knowledge belongs
    in an explicitly sourced knowledge product, not in a Result explanation.
    """

    bundle = (
        result_bundle.model_dump(mode="json")
        if hasattr(result_bundle, "model_dump")
        else dict(result_bundle)
    )
    primary_findings = [
        item.model_copy(
            update={
                "statement": _without_reference_echo(
                    item.statement,
                    [*item.fact_refs, *item.evidence_refs, *item.result_item_refs],
                )
            }
        )
        for item in interpretation.primary_findings
    ]
    supporting_findings = [
        item.model_copy(
            update={
                "statement": _without_reference_echo(
                    item.statement,
                    [*item.fact_refs, *item.evidence_refs, *item.result_item_refs],
                )
            }
        )
        for item in interpretation.supporting_findings
    ]
    findings = [*primary_findings, *supporting_findings]
    if not findings:
        return interpretation
    lead = _join_finding_statements(
        item.statement
        for item in findings[:2]
        if item.statement.strip()
    )
    limitations = [
        str(item.get("message") or "").strip()
        for item in (bundle.get("limitations") or [])[:16]
        if isinstance(item, dict) and str(item.get("message") or "").strip()
    ]
    projected = interpretation.model_copy(
        update={
            "answer_lead": lead or findings[0].statement,
            "limitations": limitations,
            "primary_findings": primary_findings,
            "supporting_findings": supporting_findings,
        }
    )
    return projected if validate_interpretation(projected, result_bundle).valid else interpretation


def _without_reference_echo(statement: str, refs: list[str]) -> str:
    """Remove only exact bound audit references from user-facing prose."""
    rendered = statement
    normalized_refs = {
        str(value).strip()
        for value in refs
        if str(value).strip()
    }
    for ref in sorted(normalized_refs, key=len, reverse=True):
        rendered = re.sub(
            rf"\s*[\(（]\s*{re.escape(ref)}\s*[\)）]",
            "",
            rendered,
        )
    parenthetical = re.compile(r"\s*[\(（](?P<body>[^()（）]*)[\)）]")

    def remove_reference_only_group(match: re.Match[str]) -> str:
        body = match.group("body")
        matched_refs = [ref for ref in normalized_refs if ref in body]
        if not matched_refs:
            return match.group(0)
        remainder = body
        for ref in matched_refs:
            remainder = remainder.replace(ref, "")
        remainder = re.sub(
            r"(?i)(?:事实|证据|结果|finding|fact|evidence|result)\s*(?:id|标识|引用)?",
            "",
            remainder,
        )
        remainder = re.sub(r"(?i)\band\b|[\s:：,，、;；/&和与]+", "", remainder)
        return "" if not remainder else match.group(0)

    rendered = parenthetical.sub(remove_reference_only_group, rendered)
    rendered = re.sub(
        r"成功识别出\s+([0-9]+)\s+个成功配位位点",
        r"成功识别出 \1 个配位位点",
        rendered,
    )
    return " ".join(rendered.split()).strip()


def _join_finding_statements(statements: Any) -> str:
    parts = [
        str(statement).strip().rstrip("。；; ")
        for statement in statements
        if str(statement).strip()
    ]
    return f"{'；'.join(parts)}。" if parts else ""


__all__ = [
    "EvidenceReferenceValidator",
    "QuantitativeClaimValidator",
    "project_grounded_answer_lead",
    "project_grounded_communication",
    "validate_interpretation",
]
