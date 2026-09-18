from __future__ import annotations

import math
import re
from decimal import Decimal, InvalidOperation
from typing import Any

from mdi_api.domain.interpretation.contracts import GroundingValidationResult, ScientificInterpretationOutput, numeric_tokens
from mdi_api.application.scientific_reasoning.assessment import ClaimSupportAssessor
from mdi_api.domain.scientific_reasoning.contracts import (
    ProposedScientificClaim,
    ReasoningEvidence,
)


# Keep temperature ``K`` case-sensitive: a lowercase ``k`` in labels such as
# ``k-point`` is not a Kelvin unit and must not trigger unit grounding.
_UNIT = re.compile(
    r"(?<![A-Za-z0-9])(?:(?i:"
    r"(?:Å|angstrom)(?:\^\{?2\}?|²)/(?:ps|picosecond)|"
    r"(?:Å|angstrom)(?:\^\{?2\}?|²)|"
    r"(?:Å|angstrom)(?:\^\{?-?3\}?|⁻³|-3)?|"
    r"picosecond|nm|pm|eV|meV|fs|ps|%|THz|cm-?1|1/s|m\^?2/s"
    r")|K)(?![A-Za-z0-9])"
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
    """Return scientific quantities while excluding presentation numerals.

    Ordered-list prefixes and dimension labels such as ``3D`` are presentation
    metadata rather than scientific measurements. Measured values still go
    through the existing strict fact/value/unit checks below.
    """

    normalized = _UNIT.sub(" ", text or "")
    # ``R^2`` is the ASCII spelling of the already-supported display label
    # ``R²``.  Its exponent is notation, not an independently asserted
    # measured value.  The fitted R-squared value that follows remains subject
    # to the normal exact-fact / bounded-rounding checks.
    normalized = re.sub(
        r"(?i)(?<![A-Za-z0-9])R\s*\^\s*2(?![A-Za-z0-9])",
        "R-squared",
        normalized,
    )
    normalized = re.sub(r"(?m)^\s*\d+[.)、]\s+(?=\S)", " ", normalized)
    normalized = re.sub(
        r"(?i)(?<![A-Za-z0-9])(?:2|3)D(?![A-Za-z0-9])",
        " ",
        normalized,
    )
    return numeric_tokens(normalized)


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
    supported_ids = _support_fact_ids(
        fact_refs=finding.fact_refs,
        evidence_refs=finding.evidence_refs,
        result_item_refs=finding.result_item_refs,
        facts=facts,
        evidence_items=evidence_items,
        result_items=result_items,
    )
    return [facts[fact_id] for fact_id in sorted(supported_ids)]


def _support_fact_ids(
    *,
    fact_refs: list[str],
    evidence_refs: list[str],
    result_item_refs: list[str],
    facts: dict[str, dict[str, Any]],
    evidence_items: dict[str, dict[str, Any]],
    result_items: dict[str, dict[str, Any]],
) -> set[str]:
    """Follow only the bounded persisted support graph for cited roots.

    ScientificResult projections can store a fact edge directly on a Result
    item or behind its Evidence edge.  The provider is allowed to cite either
    form; grounding must therefore follow the existing edges transitively, but
    must never widen from one cited root to unrelated Result items.
    """

    supported_ids = {
        str(ref)
        for ref in fact_refs
        if str(ref) in facts
    }
    pending_results = [
        str(ref)
        for ref in result_item_refs
        if str(ref) in result_items
    ]
    pending_evidence = [
        str(ref)
        for ref in evidence_refs
        if str(ref) in evidence_items
    ]
    seen_results: set[str] = set()
    seen_evidence: set[str] = set()
    while pending_results or pending_evidence:
        while pending_results:
            result_ref = pending_results.pop()
            if result_ref in seen_results:
                continue
            seen_results.add(result_ref)
            item = result_items[result_ref]
            supported_ids.update(
                str(ref)
                for ref in item.get("fact_refs") or []
                if str(ref) in facts
            )
            pending_evidence.extend(
                str(ref)
                for ref in item.get("evidence_refs") or []
                if str(ref) in evidence_items
            )
        while pending_evidence:
            evidence_ref = pending_evidence.pop()
            if evidence_ref in seen_evidence:
                continue
            seen_evidence.add(evidence_ref)
            item = evidence_items[evidence_ref]
            supported_ids.update(
                str(ref)
                for ref in item.get("supports_fact_refs") or []
                if str(ref) in facts
            )
            pending_results.extend(
                str(ref)
                for ref in item.get("supports_result_item_refs") or []
                if str(ref) in result_items
            )
    return supported_ids


class EvidenceReferenceValidator:
    def validate(self, interpretation: ScientificInterpretationOutput, result_bundle: Any) -> GroundingValidationResult:
        bundle = result_bundle.model_dump(mode="json") if hasattr(result_bundle, "model_dump") else dict(result_bundle)
        facts, evidence, result_items = _fact_values(bundle)
        errors: list[str] = []
        for finding in [*interpretation.primary_findings, *interpretation.supporting_findings]:
            refs = [*finding.fact_refs, *finding.evidence_refs, *finding.result_item_refs]
            if (
                not finding.fact_refs
                and not finding.evidence_refs
                and not finding.result_item_refs
            ):
                errors.append(
                    f"{finding.finding_id}: positive finding has no "
                    "fact/evidence/result-item reference"
                )
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
            # Some authoritative categorical scientific values legitimately
            # contain numerals (for example the space-group symbol ``Fd-3m``).
            # Accept only numerals from an exact cited string value that is
            # actually present in the finding; arbitrary nearby numbers remain
            # fail-closed.
            for fact in referenced:
                value = fact.get("value")
                if (
                    isinstance(value, str)
                    and value
                    and value.casefold() in finding.statement.casefold()
                ):
                    supported_numbers.update(
                        _number_key(token)
                        for token in _claim_numeric_tokens(value)
                    )
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


_VIEWER_SCENE_TYPES = {
    "structure.viewer_scene",
    "structure.viewer_scene_metadata",
    "structure.viewer_3d",
}
_VIEWER_SCENE_LANGUAGE = re.compile(
    r"(?i)(?:viewer|scene|visual|render|display|"
    r"查看器|场景|可视化|可视|展示|渲染|打开|呈现|生成)"
)


def _viewer_scene_without_facts_errors(
    interpretation: ScientificInterpretationOutput,
    result_bundle: Any,
) -> list[str]:
    """Limit fact-less structure viewer Results to qualitative scene claims."""

    bundle = (
        result_bundle.model_dump(mode="json")
        if hasattr(result_bundle, "model_dump")
        else dict(result_bundle)
    )
    facts, _, _ = _fact_values(bundle)
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

    def cited_result_ids(finding: Any) -> set[str]:
        result_ids = {
            str(ref)
            for ref in finding.result_item_refs
            if str(ref) in result_items
        }
        pending_results = list(result_ids)
        pending_evidence = [
            str(ref)
            for ref in finding.evidence_refs
            if str(ref) in evidence_items
        ]
        seen_results: set[str] = set()
        seen_evidence: set[str] = set()
        while pending_results or pending_evidence:
            while pending_results:
                result_id = pending_results.pop()
                if result_id in seen_results:
                    continue
                seen_results.add(result_id)
                pending_evidence.extend(
                    str(ref)
                    for ref in result_items[result_id].get("evidence_refs") or []
                    if str(ref) in evidence_items
                )
            while pending_evidence:
                evidence_id = pending_evidence.pop()
                if evidence_id in seen_evidence:
                    continue
                seen_evidence.add(evidence_id)
                for ref in evidence_items[evidence_id].get(
                    "supports_result_item_refs"
                ) or []:
                    result_id = str(ref)
                    if result_id in result_items:
                        if result_id not in result_ids:
                            result_ids.add(result_id)
                            pending_results.append(result_id)
        return result_ids

    errors: list[str] = []
    for finding in [*interpretation.primary_findings, *interpretation.supporting_findings]:
        supported_ids = _support_fact_ids(
            fact_refs=finding.fact_refs,
            evidence_refs=finding.evidence_refs,
            result_item_refs=finding.result_item_refs,
            facts=facts,
            evidence_items=evidence_items,
            result_items=result_items,
        )
        cited_viewer_items = [
            result_items[ref]
            for ref in cited_result_ids(finding)
            if str(result_items[ref].get("result_type") or "") in _VIEWER_SCENE_TYPES
        ]
        if (
            cited_viewer_items
            and not supported_ids
            and not _VIEWER_SCENE_LANGUAGE.search(finding.statement)
        ):
            errors.append(
                f"{finding.finding_id}: fact-less structure viewer Results support "
                "only qualitative scene/display statements"
            )
    return errors


def build_grounding_repair_context(
    interpretation: ScientificInterpretationOutput,
    result_bundle: Any,
    errors: list[str],
) -> list[str]:
    """Build bounded, source-derived repair guidance for one provider retry."""

    bundle = (
        result_bundle.model_dump(mode="json")
        if hasattr(result_bundle, "model_dump")
        else dict(result_bundle)
    )
    facts, _, _ = _fact_values(bundle)
    context: list[str] = []
    for finding in [*interpretation.primary_findings, *interpretation.supporting_findings]:
        referenced = _finding_fact_support(finding, bundle, facts)
        supported_values = [
            fact.get("value")
            for fact in referenced
            if isinstance(fact.get("value"), (int, float))
            and not isinstance(fact.get("value"), bool)
        ]
        supported_numbers = {_number_key(str(value)) for value in supported_values}
        unsupported = [
            token
            for token in _claim_numeric_tokens(finding.statement)
            if _number_key(token) not in supported_numbers
            and not any(
                _numeric_claim_matches_fact(token, value)
                for value in supported_values
            )
        ]
        viewer_without_facts = (
            finding.result_item_refs
            and not referenced
            and any(
                isinstance(item, dict)
                and str(item.get("id") or "") in finding.result_item_refs
                and str(item.get("result_type") or "") in _VIEWER_SCENE_TYPES
                for item in bundle.get("result_items") or []
            )
        )
        if unsupported or viewer_without_facts:
            fact_lines = [
                f"{fact.get('fact_id')}={fact.get('value')}"
                + (f" {fact.get('unit')}" if fact.get("unit") else "")
                for fact in referenced[:16]
            ]
            context.append(
                f"{finding.finding_id}: statement={finding.statement!r}; "
                f"fact_refs={list(finding.fact_refs)}; "
                f"evidence_refs={list(finding.evidence_refs)}; "
                f"result_item_refs={list(finding.result_item_refs)}; "
                f"supported_facts={fact_lines or ['none']}; "
                f"unsupported_numeric_tokens={unsupported or ['none']}. "
                "Rewrite using only the listed facts/refs; for a structure "
                "viewer Result with no facts, keep the finding qualitative "
                "and limited to scene/display availability."
            )
    context.extend(errors[:16])
    return list(dict.fromkeys(context))[:16]


def validate_interpretation(interpretation: ScientificInterpretationOutput, result_bundle: Any) -> GroundingValidationResult:
    errors: list[str] = []
    refs = EvidenceReferenceValidator().validate(interpretation, result_bundle)
    errors.extend(refs.errors)
    quantities = QuantitativeClaimValidator().validate(interpretation, result_bundle)
    errors.extend(quantities.errors)
    errors.extend(_viewer_scene_without_facts_errors(interpretation, result_bundle))
    bundle = result_bundle.model_dump(mode="json") if hasattr(result_bundle, "model_dump") else dict(result_bundle)
    execution = str(bundle.get("execution_status", ""))
    all_text = " ".join([interpretation.answer_lead, *(item.statement for item in [*interpretation.primary_findings, *interpretation.supporting_findings])]).lower()
    if execution == "PARTIAL" and any(term in all_text for term in ("complete analysis", "all steps succeeded", "全部分析均成功", "完整分析已完成")):
        errors.append("partial result cannot be described as complete")
    if interpretation.contract_version == "1.1":
        for finding in [
            *interpretation.primary_findings,
            *interpretation.supporting_findings,
        ]:
            if finding.reasoning_assessment is None:
                errors.append(
                    f"{finding.finding_id}: claim support assessment is required"
                )
            elif not finding.reasoning_assessment.accepted:
                errors.append(
                    f"{finding.finding_id}: scientific claim support was rejected"
                )
    return GroundingValidationResult(valid=not errors, errors=errors)


def project_claim_support_assessments(
    interpretation: ScientificInterpretationOutput,
    result_bundle: Any,
) -> ScientificInterpretationOutput:
    """Attach deterministic claim support without changing scientific facts.

    The provider references the bounded Result graph, but the previous
    projection assessed every claim against a single synthetic ``result_1``.
    That silently changed the grounding contract: a claim citing the
    materials-explorer item was assessed with the composition-space item's
    exploratory limitation and method context.  Build a bounded evidence view
    from the exact references on each finding instead.
    """

    if interpretation.contract_version != "1.1":
        return interpretation
    bundle = (
        result_bundle.model_dump(mode="json")
        if hasattr(result_bundle, "model_dump")
        else dict(result_bundle)
    )
    methods = [
        str(item.get("capability_id") or item.get("tool_id") or "")
        for item in bundle.get("methods") or []
        if str(item.get("capability_id") or item.get("tool_id") or "")
    ]
    method = "; ".join(sorted(set(methods))) or None
    source_scope = "; ".join(
        str(item.get("display_name") or item.get("object_type") or "")
        for item in bundle.get("source_object_refs") or []
        if str(item.get("display_name") or item.get("object_type") or "")
    ) or "current ScientificResult scope"
    limitations = [
        str(item.get("message") or "")
        for item in bundle.get("limitations") or []
        if str(item.get("message") or "")
    ]
    lineage = str(
        (bundle.get("provenance") or {}).get("source_fingerprint")
        or (bundle.get("provenance") or {}).get("job_id")
        or bundle.get("result_id")
        or "current-result"
    )
    facts_by_id = {
        str(item.get("fact_id")): item
        for item in bundle.get("facts") or []
        if isinstance(item, dict) and str(item.get("fact_id") or "")
    }
    result_items = [
        item
        for item in bundle.get("result_items") or []
        if isinstance(item, dict) and str(item.get("id") or "")
    ]
    evidence_items = [
        item
        for item in bundle.get("evidence") or []
        if isinstance(item, dict) and str(item.get("evidence_id") or "")
    ]
    result_aliases = {
        str(item["id"]): f"result_{index}"
        for index, item in enumerate(result_items, start=1)
    }
    result_items_by_id = {str(item["id"]): item for item in result_items}
    evidence_aliases = {
        str(item["evidence_id"]): f"evidence_{index}"
        for index, item in enumerate(evidence_items, start=1)
    }
    evidence_items_by_id = {
        str(item["evidence_id"]): item for item in evidence_items
    }
    fact_aliases = {
        str(item["fact_id"]): f"result_fact_{index}"
        for index, item in enumerate(facts_by_id.values(), start=1)
    }

    def item_capability(item: dict[str, Any]) -> str:
        result_type = str(item.get("result_type") or "")
        return result_type

    def item_methods(item: dict[str, Any]) -> list[str]:
        capability = item_capability(item)
        return sorted(
            {
                value
                for value in methods
                if value == capability or value.removeprefix("agent2.") == capability
            }
        )

    def item_limitations(item: dict[str, Any]) -> list[str]:
        capability = item_capability(item)
        projector_id = f"agent2.{capability}" if capability else ""
        return [
            str(entry.get("message") or "")
            for entry in bundle.get("limitations") or []
            if isinstance(entry, dict)
            and str(entry.get("message") or "")
            and (
                not str(entry.get("source_ref") or "")
                or str(entry.get("source_ref")) in {capability, projector_id}
            )
        ]

    def fact_text(fact: dict[str, Any]) -> str:
        predicate = str(fact.get("predicate") or "fact")
        value = fact.get("value")
        unit = str(fact.get("unit") or "").strip()
        rendered = f"{predicate}={value}"
        return f"{rendered} {unit}".strip()

    evidence: list[ReasoningEvidence] = []
    for item in result_items:
        fact_texts = [
            fact_text(facts_by_id[fact_id])
            for fact_id in item.get("fact_refs") or []
            if str(fact_id) in facts_by_id
        ]
        title = str(item.get("title") or item.get("result_type") or "ScientificResult item")
        evidence.append(
            ReasoningEvidence(
                ref=result_aliases[str(item["id"])],
                origin="COMPUTED",
                text="; ".join([title, *fact_texts])[:12000],
                scope=source_scope,
                method="; ".join(item_methods(item)) or None,
                lineage=lineage,
                limitations=item_limitations(item),
                semantic_tags=(
                    ["EXPLORATORY_OUTLIER"]
                    if item_capability(item) == "data.composition_space"
                    else []
                ),
            )
        )
    for item in evidence_items:
        fact_texts = [
            fact_text(facts_by_id[fact_id])
            for fact_id in item.get("supports_fact_refs") or []
            if str(fact_id) in facts_by_id
        ]
        text = " ".join(
            [
                str(item.get("evidence_type") or "Computed evidence"),
                str(item.get("artifact_locator") or "").strip(),
                *fact_texts,
            ]
        ).strip()
        evidence.append(
            ReasoningEvidence(
                ref=evidence_aliases[str(item["evidence_id"])],
                origin="COMPUTED",
                text=text[:12000] or "Authorized computed evidence.",
                scope=source_scope,
                method=method,
                lineage=lineage,
                limitations=limitations,
            )
        )
    for fact_id, fact in facts_by_id.items():
        evidence.append(
            ReasoningEvidence(
                ref=fact_aliases[fact_id],
                origin="COMPUTED",
                text=fact_text(fact),
                scope=source_scope,
                lineage=lineage,
            )
        )
    assessor = ClaimSupportAssessor()

    def assess(item: Any) -> Any:
        result_refs = [
            result_aliases[str(ref)]
            for ref in item.result_item_refs
            if str(ref) in result_aliases
        ]
        fact_ids = _support_fact_ids(
            fact_refs=[str(ref) for ref in item.fact_refs],
            evidence_refs=[str(ref) for ref in item.evidence_refs],
            result_item_refs=[str(ref) for ref in item.result_item_refs],
            facts=facts_by_id,
            evidence_items=evidence_items_by_id,
            result_items=result_items_by_id,
        )
        fact_refs = [fact_aliases[ref] for ref in sorted(fact_ids)]
        evidence_refs = [
            evidence_aliases[str(ref)]
            for ref in item.evidence_refs
            if str(ref) in evidence_aliases
        ]
        # A result/evidence projection is only a fallback when it cannot be
        # narrowed to an authoritative fact. This prevents result-level
        # exploratory tags and broad limitations from rejecting a claim about
        # an explicitly persisted fact such as composition.invalid_sample_count
        # while retaining fail-closed behavior for genuinely unsupported
        # result-only claims.
        refs = fact_refs or evidence_refs or result_refs
        # ProposedScientificClaim accepts a bounded evidence list. Prefer
        # direct fact references, then evidence/result-item references, while
        # preserving provider order and never widening the authority graph.
        refs = list(dict.fromkeys(refs))[:16]
        assessment = assessor.assess(
            ProposedScientificClaim(
                claim_id=item.finding_id,
                text=item.statement,
                claim_type=item.claim_type,
                support_status=item.support_status,
                evidence_refs=list(dict.fromkeys(refs)) or ["evidence_missing"],
                scope=item.scope or source_scope,
                qualifiers=item.qualifiers,
                limitations=interpretation.limitations,
                comparison_status=item.comparison_status,
                hypothesis_status=item.hypothesis_status,
            ),
            evidence,
        )
        return item.model_copy(update={"reasoning_assessment": assessment})

    return interpretation.model_copy(
        update={
            "primary_findings": [assess(item) for item in interpretation.primary_findings],
            "supporting_findings": [
                assess(item) for item in interpretation.supporting_findings
            ],
        }
    )


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
    only selects the first referenced finding statement as the lead. Contract
    1.1 assessment requirements are intentionally deferred to the following
    claim-assessment projection in the service pipeline.
    """

    validation = validate_interpretation(interpretation, result_bundle)
    answer_lead_error = "answer_lead introduces an unsupported quantitative claim"
    findings = [*interpretation.primary_findings, *interpretation.supporting_findings]
    deferred_assessment_errors = {
        f"{item.finding_id}: claim support assessment is required"
        for item in findings
        if item.reasoning_assessment is None
    }
    actionable_errors = [
        error
        for error in validation.errors
        if error not in deferred_assessment_errors
    ]
    if validation.valid or actionable_errors != [answer_lead_error]:
        return interpretation
    if not findings:
        return interpretation
    projected = interpretation.model_copy(update={"answer_lead": findings[0].statement})
    projected_errors = validate_interpretation(projected, result_bundle).errors
    projected_actionable_errors = [
        error
        for error in projected_errors
        if error not in deferred_assessment_errors
    ]
    return projected if not projected_actionable_errors else interpretation


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
                "statement": _sanitize_grounded_statement(
                    _without_reference_echo(
                        item.statement,
                        [*item.fact_refs, *item.evidence_refs, *item.result_item_refs],
                    )
                )
            }
        )
        for item in interpretation.primary_findings
    ]
    supporting_findings = [
        item.model_copy(
            update={
                "statement": _sanitize_grounded_statement(
                    _without_reference_echo(
                        item.statement,
                        [*item.fact_refs, *item.evidence_refs, *item.result_item_refs],
                    )
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


_VERSION_IDENTIFIER = re.compile(
    r"\bversion\s+(?:[0-9a-f]{8}-[0-9a-f-]{27,}|[0-9a-f]{16,})\b",
    re.IGNORECASE,
)
_UUID_IDENTIFIER = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)
_METHOD_IDENTIFIER = re.compile(
    r"\b(?:method|capability)\.[0-9a-f-]{16,}\b",
    re.IGNORECASE,
)
_OPAQUE_REFERENCE = re.compile(
    r"\b(?:fact|evidence|result[-_.]item|object|version|job|call|artifact|figure|limitation)"
    r"[-_.][A-Za-z0-9-]{16,}\b",
    re.IGNORECASE,
)
_METHOD_VERSION = re.compile(
    r"\b(?:capability|method)\s+version\s+\d+(?:\.\d+)*\b",
    re.IGNORECASE,
)


def _sanitize_grounded_statement(statement: str) -> str:
    """Remove opaque execution metadata from scientific presentation prose.

    Provider text may echo source-version UUIDs or internal method identifiers.
    These are provenance metadata, not scientific quantities.  Keeping them in
    a finding makes the quantitative grounding validator interpret UUID digits
    as measurements.  The canonical Result/manifest still retains the exact
    identifiers; only the user-facing statement is normalized.
    """

    rendered = _VERSION_IDENTIFIER.sub("the recorded source version", statement)
    rendered = _UUID_IDENTIFIER.sub("the recorded source version", rendered)
    rendered = _OPAQUE_REFERENCE.sub("", rendered)
    rendered = _METHOD_IDENTIFIER.sub("the recorded method", rendered)
    rendered = _METHOD_VERSION.sub("the recorded method version", rendered)
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
    "project_claim_support_assessments",
    "project_grounded_communication",
    "validate_interpretation",
    "build_grounding_repair_context",
]
