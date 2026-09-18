from __future__ import annotations

import re
from typing import Iterable

from mdi_api.domain.scientific_reasoning.contracts import (
    ClaimSupportAssessment,
    ClaimSupportStatus,
    MethodComparisonStatus,
    ProposedScientificClaim,
    ReasoningDefectSeverity,
    ReasoningDefectType,
    ReasoningEvidence,
    ScientificClaimType,
    ScientificReasoningOutcome,
)


_STRENGTH_RANK = {
    ClaimSupportStatus.NOT_SUPPORTED: 0,
    ClaimSupportStatus.INSUFFICIENT_EVIDENCE: 1,
    ClaimSupportStatus.CONFLICTED: 2,
    ClaimSupportStatus.SUGGESTIVE: 3,
    ClaimSupportStatus.CONSISTENT_WITH: 4,
    ClaimSupportStatus.SUPPORTED_WITHIN_SCOPE: 5,
    ClaimSupportStatus.DIRECTLY_SUPPORTED: 6,
}
_AUTHORITY_ESCALATION = re.compile(
    r"\b(?:DOMAIN_VALIDATED|REFERENCE_VALIDATED|CROSS_IMPLEMENTATION_VALIDATED|"
    r"capability qualification)\b",
    re.IGNORECASE,
)
_UNIVERSAL_SCOPE = re.compile(
    r"\b(?:all|every|universal|universally|under all conditions|future materials)\b",
    re.IGNORECASE,
)
_INDEPENDENCE_CLAIM = re.compile(
    r"\b(?:independent studies|independent experiments|independent datasets|"
    r"multiple independent)\b",
    re.IGNORECASE,
)
_ABSENCE_GENERALIZATION = re.compile(
    r"\b(?:never been reported|no .* exists anywhere|has never occurred)\b",
    re.IGNORECASE,
)
_CITATION_TRUTH = re.compile(
    r"\b(?:more correct|more true|scientifically superior)\b.*\b(?:cited|citation)",
    re.IGNORECASE,
)
_FIGURE_DETAIL = re.compile(r"\b(?:figure|table|supplement|section)\s*\d+", re.I)
_EQUIVALENT_CONDITIONS = re.compile(
    r"\b(?:equivalent conditions|same conditions|directly comparable)\b", re.I
)
_METHOD_RANKING = re.compile(
    r"\b(?:universally|always|more accurate|superior|best method)\b", re.I
)
_METHOD_EQUIVALENCE = re.compile(
    r"\b(?:methods? (?:are )?(?:equivalent|interchangeable)|"
    r"directly comparable methods?|same scientific definition)\b",
    re.I,
)
_EXPLORATORY_INVALIDITY = re.compile(
    r"\b(?:invalid|delete|discard|unphysical)\b", re.I
)
_EXTERNAL_PROOF = re.compile(
    r"\b(?:independently proves|physically correct|validated solver|solver is correct)\b",
    re.I,
)
_ESTABLISHED_MECHANISM = re.compile(
    r"\b(?:proven|established|definitively|demonstrates the mechanism)\b", re.I
)
_NEGATED_OVERCLAIM = re.compile(
    r"\b(?:does not|do not|cannot|can not|not|insufficient to|fails to)\b"
    r".{0,80}\b(?:establish|prove|demonstrate|generalize|support|conclude|confirm)\b"
    r"|\b(?:not supported|remains unproven|remains hypothetical)\b",
    re.I,
)
_RESTRAINT_LANGUAGE = re.compile(
    r"\b(?:does not|do not|cannot|can not|not|no|insufficient|"
    r"unavailable|unresolved|limited|uncertain)\b",
    re.I,
)
_TENTATIVE_MECHANISM = re.compile(
    r"\b(?:may|might|could|possible|possibly|suggest|consistent with|hypothes)\w*\b",
    re.I,
)
_BOUNDED_COLLECTION = re.compile(
    r"\b(?:dataset|data\s+set|sample(?:s)?|row(?:s)?|record(?:s)?|"
    r"entry|entries|composition(?:s)?)\b",
    re.I,
)
_FINITE_COLLECTION_EVIDENCE = re.compile(
    r"(?:\b(?:count|valid|invalid)\b|"
    r"(?:row|sample|total_rows?|valid|invalid)[_. ]count|"
    r"composition\.(?:valid|invalid)(?:_count)?)",
    re.I,
)


def _contains(texts: Iterable[str], token: str) -> bool:
    needle = token.casefold()
    return any(needle in text.casefold() for text in texts)


def _is_bounded_collection_generalization(
    claim: ProposedScientificClaim,
    selected: Iterable[ReasoningEvidence],
) -> bool:
    """Allow finite ``all`` statements about the supplied collection only.

    ``all materials`` is an unauthorized extrapolation, but statements such
    as ``all compositions in this dataset are valid`` or ``there are no
    invalid samples in this dataset`` are bounded observations when the
    selected computed evidence contains finite validity or count facts. Keep
    this exception lexical and evidence-backed so it cannot weaken the
    generalization guard for a broader population.
    """

    claim_text = " ".join([claim.text, claim.scope, *claim.qualifiers])
    if not _BOUNDED_COLLECTION.search(claim_text):
        return False
    evidence_text = " ".join(item.text for item in selected)
    return bool(_FINITE_COLLECTION_EVIDENCE.search(evidence_text))


def _is_bounded_result_synthesis(
    claim: ProposedScientificClaim,
    selected: Iterable[ReasoningEvidence],
) -> bool:
    """Recognize an explicit finite synthesis over the cited result set.

    Universal-language protection must still reject claims about an
    unrestricted population.  A descriptive statement such as “the RDF, MSD,
    and diffusion results all use the same selected interval”, however, is
    bounded to the named computed outputs and their exact cited evidence.  It
    does not generalize beyond the supplied ScientificResult.
    """

    selected_items = list(selected)
    if (
        claim.claim_type != ScientificClaimType.DESCRIPTIVE_SYNTHESIS
        or not selected_items
        or any(item.origin.value != "COMPUTED" for item in selected_items)
    ):
        return False
    text = " ".join([claim.text, claim.scope, *claim.qualifiers]).casefold()
    bounded_subjects = {
        token
        for token in (
            "result",
            "results",
            "rdf",
            "msd",
            "diffusion",
            "tool",
            "tools",
            "output",
            "outputs",
        )
        if re.search(rf"\b{re.escape(token)}\b", text)
    }
    return bool(
        bounded_subjects
        and re.search(
            r"\b(?:same|selected|supplied|cited|these|those|corresponding)\b",
            text,
        )
    )


def _is_bounded_invalidity_observation(
    claim: ProposedScientificClaim,
    selected: Iterable[ReasoningEvidence],
) -> bool:
    """Distinguish a counted invalid-entry observation from invalidity claims.

    The composition-space evidence is exploratory, so it must not support a
    claim that a material is scientifically invalid.  It can still report the
    authoritative finite ``invalid samples/formulas = 0`` fields produced by
    the dataset-quality projector.
    """

    if claim.claim_type != ScientificClaimType.DIRECT_OBSERVATION:
        return False
    claim_text = " ".join([claim.text, claim.scope, *claim.qualifiers]).casefold()
    if not re.search(
        r"\b(?:sample|samples|formula|formulas|entry|entries|row|rows|"
        r"coverage|count)\b",
        claim_text,
    ):
        return False
    evidence_text = " ".join(item.text for item in selected)
    return bool(
        re.search(
            r"(?:\b(?:invalid|valid|count)\b|"
            r"(?:invalid|valid)[_. ]count)",
            evidence_text,
            re.I,
        )
    )


def _normalized_words(text: str) -> set[str]:
    return {
        word
        for word in re.findall(r"[a-z0-9]+", text.casefold())
        if word
        not in {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "for",
            "from",
            "in",
            "is",
            "it",
            "of",
            "on",
            "or",
            "that",
            "the",
            "this",
            "to",
            "was",
            "with",
        }
    }


def _limitation_is_preserved(
    limitation: str,
    *,
    claim: ProposedScientificClaim,
) -> bool:
    """Recognize a material limitation semantically, not by exact punctuation."""

    claim_fields = [
        claim.text,
        claim.scope,
        *claim.qualifiers,
        *claim.limitations,
    ]
    normalized_limitation = _normalized_words(limitation)
    normalized_claim = _normalized_words(" ".join(claim_fields))
    if normalized_limitation and normalized_limitation <= normalized_claim:
        return True

    limitation_text = limitation.casefold()
    claim_text = " ".join(claim_fields).casefold()
    semantic_boundaries = (
        (("abstract",), ("abstract",)),
        (("method", "depend"), ("method", "depend")),
        (("causal",), ("causal",)),
        (("common lineage", "shared lineage"), ("lineage", "independent")),
        (("solver", "upstream"), ("solver", "upstream", "external")),
        (("phase purity",), ("phase purity",)),
    )
    for limitation_terms, claim_terms in semantic_boundaries:
        if any(term in limitation_text for term in limitation_terms) and any(
            term in claim_text for term in claim_terms
        ):
            return True
    if (
        any(term in limitation_text for term in ("peak", "coordination shell"))
        and any(term in claim_text for term in ("peak", "coordination shell"))
        and _RESTRAINT_LANGUAGE.search(claim_text)
    ):
        return True
    return False


def _limitation_is_material_to_claim(
    limitation: str,
    *,
    claim: ProposedScientificClaim,
) -> bool:
    """Require a limitation only when it constrains this particular claim.

    Result-level limitations can describe one aspect of a heterogeneous
    result. Requiring every finding to repeat every limitation makes otherwise
    direct observations fail closed for an unrelated caveat (for example, a
    no-peak-detection limitation should constrain a peak claim, not an
    independently reported cutoff parameter).
    """

    if claim.claim_type == ScientificClaimType.LIMITATION:
        return True
    limitation_words = _normalized_words(limitation)
    claim_words = _normalized_words(
        " ".join([claim.text, claim.scope, *claim.qualifiers])
    )
    # A limitation can share the domain label with many otherwise independent
    # claims.  For example, "RDF does not infer peaks" constrains a peak or
    # coordination-shell claim, but it does not constrain an independently
    # reported bin count, density, or figure-presence claim merely because all
    # of them mention RDF.
    feature_terms = {"peak", "peaks", "coordination", "shell", "shells"}
    if limitation_words & feature_terms and not claim_words & feature_terms:
        return False
    generic = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
        "in", "is", "it", "of", "on", "or", "that", "the", "this", "to",
        "was", "with", "result", "results", "data", "available", "does",
        "not", "cannot", "curve",
    }
    meaningful_limitation_words = limitation_words - generic
    if meaningful_limitation_words & claim_words:
        return True
    limitation_text = limitation.casefold()
    claim_text = " ".join([claim.text, claim.scope, *claim.qualifiers]).casefold()
    semantic_pairs = (
        (("peak", "coordination shell"), ("peak", "coordination")),
        (("method", "depend"), ("method", "method-dependent")),
        (("cutoff", "range"), ("cutoff", "range", "radius")),
        (("abstract",), ("paper", "literature", "source")),
        (("solver", "upstream"), ("solver", "upstream", "external")),
    )
    return any(
        any(term in limitation_text for term in limitation_terms)
        and any(term in claim_text for term in claim_terms)
        for limitation_terms, claim_terms in semantic_pairs
    )


def _severity(defects: set[ReasoningDefectType]) -> ReasoningDefectSeverity | None:
    if defects & {
        ReasoningDefectType.CAUSAL_OVERCLAIM,
        ReasoningDefectType.SCIENTIFIC_AUTHORITY,
        ReasoningDefectType.DERIVED_NUMBER_INVENTION,
    }:
        return ReasoningDefectSeverity.CRITICAL
    if defects & {
        ReasoningDefectType.MECHANISTIC_OVERCLAIM,
        ReasoningDefectType.METHOD_MISINTERPRETATION,
        ReasoningDefectType.INVALID_COMPARISON,
        ReasoningDefectType.CONTRADICTION_COLLAPSE,
        ReasoningDefectType.HYPOTHESIS_ESCALATION,
        ReasoningDefectType.SOURCE_SCOPE_OVERREACH,
    }:
        return ReasoningDefectSeverity.MAJOR
    if defects:
        return ReasoningDefectSeverity.MODERATE
    return None


class ClaimSupportAssessor:
    """Fail-closed scientific inference policy over authorized evidence."""

    def assess(
        self,
        claim: ProposedScientificClaim,
        evidence: Iterable[ReasoningEvidence],
    ) -> ClaimSupportAssessment:
        evidence_by_ref = {item.ref: item for item in evidence}
        selected = [
            evidence_by_ref[ref]
            for ref in claim.evidence_refs
            if ref in evidence_by_ref
        ]
        errors = sorted(set(claim.evidence_refs) - set(evidence_by_ref))
        reasons: list[str] = []
        qualifiers = list(claim.qualifiers)
        limitations = list(claim.limitations)
        defects: set[ReasoningDefectType] = set()
        status = claim.support_status
        outcome = ScientificReasoningOutcome.SUPPORTED
        comparison: MethodComparisonStatus | None = claim.comparison_status

        if errors or not selected:
            reasons.append("UNKNOWN_OR_MISSING_EVIDENCE_REF")
            defects.add(ReasoningDefectType.QUALITATIVE_SUPPORT)
            status = ClaimSupportStatus.NOT_SUPPORTED
            outcome = ScientificReasoningOutcome.NOT_SUPPORTED

        for item in selected:
            limitations.extend(item.limitations)
            if item.evidence_scope == "ABSTRACT_ONLY":
                limitations.append("Evidence inspection is limited to the abstract.")
            if item.publication_status in {"RETRACTED", "WITHDRAWN"}:
                reasons.append("RETRACTED_OR_WITHDRAWN_SOURCE")
                defects.add(ReasoningDefectType.SCIENTIFIC_AUTHORITY)
                status = ClaimSupportStatus.NOT_SUPPORTED
                outcome = ScientificReasoningOutcome.SCIENTIFIC_AUTHORITY_VIOLATION

        if claim.claim_type == ScientificClaimType.CAUSAL_CLAIM and not any(
            item.causal_authority for item in selected
        ):
            limitations.append("The available evidence does not establish causality.")
            if _NEGATED_OVERCLAIM.search(claim.text) and status in {
                ClaimSupportStatus.INSUFFICIENT_EVIDENCE,
                ClaimSupportStatus.NOT_SUPPORTED,
                ClaimSupportStatus.CONFLICTED,
            }:
                outcome = ScientificReasoningOutcome.INSUFFICIENT_EVIDENCE
            else:
                reasons.append("NO_CAUSAL_INFERENCE_AUTHORITY")
                defects.add(ReasoningDefectType.CAUSAL_OVERCLAIM)
                status = ClaimSupportStatus.NOT_SUPPORTED
                outcome = ScientificReasoningOutcome.INSUFFICIENT_EVIDENCE

        if claim.claim_type == ScientificClaimType.MECHANISTIC_INTERPRETATION:
            if len(selected) < 2:
                limitations.append(
                    "A single evidence item supports only a tentative mechanism."
                )
                if (
                    _STRENGTH_RANK[status]
                    > _STRENGTH_RANK[ClaimSupportStatus.SUGGESTIVE]
                    or not (
                        claim.hypothesis_status
                        or _TENTATIVE_MECHANISM.search(claim.text)
                    )
                ):
                    reasons.append("MECHANISM_EVIDENCE_MISSING")
                    defects.add(ReasoningDefectType.MECHANISTIC_OVERCLAIM)
                    status = ClaimSupportStatus.NOT_SUPPORTED
                    outcome = ScientificReasoningOutcome.INSUFFICIENT_EVIDENCE
                else:
                    qualifiers.extend(["hypothesis", "suggestive"])
                    outcome = ScientificReasoningOutcome.SUPPORTED_ONLY_AS_HYPOTHESIS
            elif _STRENGTH_RANK[status] > _STRENGTH_RANK[
                ClaimSupportStatus.CONSISTENT_WITH
            ]:
                reasons.append("MECHANISM_NOT_DIRECTLY_ESTABLISHED")
                limitations.append(
                    "The mechanism remains a hypothesis; causality is not established."
                )
                qualifiers.extend(["hypothesis", "consistent with"])
                defects.add(ReasoningDefectType.MECHANISTIC_OVERCLAIM)
                status = ClaimSupportStatus.SUGGESTIVE
                outcome = ScientificReasoningOutcome.SUPPORTED_ONLY_AS_HYPOTHESIS
            if _ESTABLISHED_MECHANISM.search(claim.text) and any(
                re.search(r"\b(?:suggest|may|might|consistent with)\b", item.text, re.I)
                for item in selected
            ):
                reasons.append("HYPOTHESIS_WAS_ESCALATED_TO_ESTABLISHED_MECHANISM")
                defects.add(ReasoningDefectType.HYPOTHESIS_ESCALATION)

        restrained_generalization = bool(
            (
                _NEGATED_OVERCLAIM.search(claim.text)
                or (
                    claim.claim_type
                    in {
                        ScientificClaimType.LIMITATION,
                        ScientificClaimType.GENERALIZATION,
                    }
                    and _RESTRAINT_LANGUAGE.search(claim.text)
                )
            )
            and status
            in {
                ClaimSupportStatus.INSUFFICIENT_EVIDENCE,
                ClaimSupportStatus.NOT_SUPPORTED,
                ClaimSupportStatus.CONFLICTED,
            }
        )
        if (
            claim.claim_type == ScientificClaimType.GENERALIZATION
            and restrained_generalization
        ):
            outcome = ScientificReasoningOutcome.INSUFFICIENT_EVIDENCE
        if (
            claim.claim_type == ScientificClaimType.GENERALIZATION
            and not restrained_generalization
            and not _is_bounded_collection_generalization(claim, selected)
            and not all(item.generalization_authority for item in selected)
        ):
            reasons.append("GENERALIZATION_EXCEEDS_EVIDENCE_SCOPE")
            limitations.append(
                "The evidence is limited to the studied system or population."
            )
            defects.add(ReasoningDefectType.SCOPE_EXPANSION)
            status = ClaimSupportStatus.NOT_SUPPORTED
            outcome = ScientificReasoningOutcome.INSUFFICIENT_EVIDENCE

        scopes = sorted({item.scope for item in selected})
        if (
            selected
            and (
                _UNIVERSAL_SCOPE.search(claim.scope)
                or _UNIVERSAL_SCOPE.search(claim.text)
            )
            and not _is_bounded_collection_generalization(claim, selected)
            and not _is_bounded_result_synthesis(claim, selected)
            and not restrained_generalization
            and not all(item.generalization_authority for item in selected)
        ):
            reasons.append("UNIVERSAL_SCOPE_NOT_AUTHORIZED")
            limitations.append("Claim scope must remain within: " + "; ".join(scopes))
            defects.add(ReasoningDefectType.SCOPE_EXPANSION)
            status = ClaimSupportStatus.NOT_SUPPORTED
            outcome = ScientificReasoningOutcome.INSUFFICIENT_EVIDENCE

        if claim.derived_numeric and not claim.derived_fact_ref:
            reasons.append("DERIVED_NUMERIC_FACT_REQUIRES_AUTHORITY")
            limitations.append(
                "A deterministic derived-fact authority is required for this value."
            )
            defects.add(ReasoningDefectType.DERIVED_NUMBER_INVENTION)
            status = ClaimSupportStatus.NOT_SUPPORTED
            outcome = ScientificReasoningOutcome.DERIVATION_REQUIRED

        if _AUTHORITY_ESCALATION.search(claim.text) and any(
            item.origin.value == "LITERATURE" for item in selected
        ):
            reasons.append("LITERATURE_CANNOT_MUTATE_CAPABILITY_QUALIFICATION")
            limitations.append(
                "Literature evidence cannot modify Capability qualification."
            )
            defects.add(ReasoningDefectType.SCIENTIFIC_AUTHORITY)
            status = ClaimSupportStatus.NOT_SUPPORTED
            outcome = ScientificReasoningOutcome.SCIENTIFIC_AUTHORITY_VIOLATION

        if _ABSENCE_GENERALIZATION.search(claim.text):
            reasons.append("ABSENCE_OF_EVIDENCE_IS_NOT_EVIDENCE_OF_ABSENCE")
            qualifiers.append("current bounded search")
            limitations.append(
                "No source found in a bounded search does not establish universal absence."
            )
            defects.add(ReasoningDefectType.SCOPE_EXPANSION)
            status = ClaimSupportStatus.INSUFFICIENT_EVIDENCE
            outcome = ScientificReasoningOutcome.INSUFFICIENT_EVIDENCE

        if _CITATION_TRUTH.search(claim.text):
            reasons.append("CITATION_COUNT_IS_NOT_SCIENTIFIC_TRUTH_AUTHORITY")
            limitations.append(
                "Citation count is a discovery signal, not scientific truth."
            )
            defects.add(ReasoningDefectType.QUALITATIVE_SUPPORT)
            status = ClaimSupportStatus.NOT_SUPPORTED
            outcome = ScientificReasoningOutcome.NOT_SUPPORTED

        if _FIGURE_DETAIL.search(claim.text) and selected and all(
            item.evidence_scope == "ABSTRACT_ONLY" for item in selected
        ):
            reasons.append("ABSTRACT_ONLY_SOURCE_CANNOT_SUPPORT_FULL_TEXT_DETAIL")
            limitations.append(
                "Abstract-only evidence cannot establish figure, table, or method details."
            )
            defects.add(ReasoningDefectType.SOURCE_SCOPE_OVERREACH)
            status = ClaimSupportStatus.NOT_SUPPORTED
            outcome = ScientificReasoningOutcome.INSUFFICIENT_EVIDENCE

        if any("EXPLORATORY_OUTLIER" in item.semantic_tags for item in selected):
            if (
                _EXPLORATORY_INVALIDITY.search(claim.text)
                and not _is_bounded_invalidity_observation(claim, selected)
            ):
                reasons.append("EXPLORATORY_OUTLIER_DOES_NOT_ESTABLISH_INVALIDITY")
                limitations.append(
                    "An exploratory statistical outlier is not evidence of scientific invalidity."
                )
                defects.add(ReasoningDefectType.QUALITATIVE_SUPPORT)
                status = ClaimSupportStatus.NOT_SUPPORTED
                outcome = ScientificReasoningOutcome.NOT_SUPPORTED

        if any(
            "EXTERNAL_IMPLEMENTATION_SEMANTICS" in item.semantic_tags
            for item in selected
        ) and _EXTERNAL_PROOF.search(claim.text):
            reasons.append("EXTERNAL_IMPLEMENTATION_VALIDITY_NOT_ESTABLISHED")
            limitations.append(
                "The platform validates integration semantics, not the upstream solver."
            )
            defects.add(ReasoningDefectType.METHOD_MISINTERPRETATION)
            status = ClaimSupportStatus.NOT_SUPPORTED
            outcome = ScientificReasoningOutcome.NOT_SUPPORTED

        methods = sorted({item.method for item in selected if item.method})
        conditions = {tuple(item.conditions) for item in selected}
        if (
            len(selected) >= 2
            and len(conditions) > 1
            and (
                "contradict" in claim.text.casefold()
                or "correct" in claim.text.casefold()
            )
        ):
            comparison = MethodComparisonStatus.COMPARABLE_WITH_QUALIFIERS
            qualifiers.append("conditions differ")
            limitations.append("The evidence is not directly comparable across conditions.")
            reasons.append("APPARENT_CONTRADICTION_EXPLAINED_BY_CONDITIONS")
            defects.add(ReasoningDefectType.CONTRADICTION_COLLAPSE)
            status = min(
                status,
                ClaimSupportStatus.SUPPORTED_WITHIN_SCOPE,
                key=lambda item: _STRENGTH_RANK[item],
            )
            outcome = ScientificReasoningOutcome.CONDITION_EXPLAINED_DIFFERENCE
        comparison_claim = claim.claim_type in {
            ScientificClaimType.QUANTITATIVE_COMPARISON,
            ScientificClaimType.QUALITATIVE_COMPARISON,
            ScientificClaimType.METHOD_INTERPRETATION,
        }
        if len(selected) >= 2 and comparison_claim:
            if len(conditions) > 1:
                comparison = MethodComparisonStatus.COMPARABLE_WITH_QUALIFIERS
                qualifiers.append("conditions differ")
                limitations.append(
                    "The compared evidence uses different conditions."
                )
                reasons.append("COMPARISON_CONDITIONS_DIFFER")
                if _EQUIVALENT_CONDITIONS.search(claim.text):
                    defects.add(ReasoningDefectType.INVALID_COMPARISON)
                    status = min(
                        status,
                        ClaimSupportStatus.SUPPORTED_WITHIN_SCOPE,
                        key=lambda item: _STRENGTH_RANK[item],
                    )
                    outcome = ScientificReasoningOutcome.SUPPORTED_WITH_QUALIFIERS
                elif (
                    "contradict" in claim.text.casefold()
                    or "correct" in claim.text.casefold()
                ):
                    defects.add(ReasoningDefectType.CONTRADICTION_COLLAPSE)
                    status = min(
                        status,
                        ClaimSupportStatus.SUPPORTED_WITHIN_SCOPE,
                        key=lambda item: _STRENGTH_RANK[item],
                    )
                    outcome = ScientificReasoningOutcome.CONDITION_EXPLAINED_DIFFERENCE
            elif len(methods) > 1:
                comparison = (
                    MethodComparisonStatus.COMPLEMENTARY
                    if _METHOD_RANKING.search(claim.text)
                    else MethodComparisonStatus.METHOD_DEPENDENT_DIFFERENCE
                    if all(item.lineage == selected[0].lineage for item in selected)
                    else MethodComparisonStatus.COMPARABLE_WITH_QUALIFIERS
                )
                qualifiers.append("method-dependent")
                limitations.append("The methods use different scientific definitions.")
                reasons.append("METHODS_DIFFER")
                method_difference_ignored = bool(
                    _METHOD_RANKING.search(claim.text)
                    or _METHOD_EQUIVALENCE.search(claim.text)
                    or claim.comparison_status
                    == MethodComparisonStatus.DIRECTLY_COMPARABLE
                )
                if method_difference_ignored:
                    defects.add(ReasoningDefectType.METHOD_MISINTERPRETATION)
                if _METHOD_RANKING.search(claim.text):
                    status = ClaimSupportStatus.NOT_SUPPORTED
                    outcome = ScientificReasoningOutcome.INSUFFICIENT_EVIDENCE
                else:
                    status = min(
                        status,
                        ClaimSupportStatus.SUPPORTED_WITHIN_SCOPE,
                        key=lambda item: _STRENGTH_RANK[item],
                    )
                    outcome = ScientificReasoningOutcome.METHOD_DEPENDENT_DIFFERENCE

        lineage_groups = {item.lineage for item in selected}
        relation_groups = {item.relation for item in selected if item.relation}
        dependent_refs = {
            ref for item in selected for ref in item.depends_on if ref in evidence_by_ref
        }
        independence_overclaimed = bool(
            _INDEPENDENCE_CLAIM.search(claim.text)
            and (
                len(lineage_groups) < len(selected)
                or len(relation_groups) == 1
                or dependent_refs
            )
        )
        if independence_overclaimed:
            reasons.append("EVIDENCE_HAS_COMMON_ANCESTRY")
            qualifiers.append("shared evidence lineage")
            limitations.append(
                "The cited items are not independent evidence authorities."
            )
            defects.add(ReasoningDefectType.EVIDENCE_DOUBLE_COUNT)
            status = min(
                status,
                ClaimSupportStatus.SUPPORTED_WITHIN_SCOPE,
                key=lambda item: _STRENGTH_RANK[item],
            )

        if (
            len(selected) >= 2
            and len(conditions) <= 1
            and len(methods) <= 1
            and any(
                word in claim.text.casefold()
                for word in ("wrong", "truth", "winner")
            )
        ):
            reasons.append("UNRESOLVED_CONTRADICTION_MUST_BE_PRESERVED")
            limitations.append("The available evidence does not resolve the disagreement.")
            defects.add(ReasoningDefectType.CONTRADICTION_COLLAPSE)
            status = ClaimSupportStatus.CONFLICTED
            outcome = ScientificReasoningOutcome.CONFLICTED

        # Evidence limitations constrain the claim even if the provider omits
        # them. Missing material limitations is itself an assessment defect.
        evidence_limitations = [
            limit for item in selected for limit in item.limitations
        ]
        material_limitations = [
            limit
            for limit in evidence_limitations
            if _limitation_is_material_to_claim(limit, claim=claim)
        ]
        if material_limitations and not all(
            _limitation_is_preserved(limit, claim=claim)
            for limit in material_limitations
        ):
            reasons.append("MATERIAL_EVIDENCE_LIMITATION_OMITTED")
            defects.add(ReasoningDefectType.MISSING_LIMITATION)

        accepted = not defects and not errors
        if not accepted and outcome == ScientificReasoningOutcome.SUPPORTED:
            outcome = ScientificReasoningOutcome.NOT_SUPPORTED
        return ClaimSupportAssessment(
            claim_id=claim.claim_id,
            claim_type=claim.claim_type,
            support_status=status,
            outcome=outcome,
            accepted=accepted,
            supporting_refs=claim.evidence_refs,
            contradicting_refs=claim.contradicting_refs,
            scope=claim.scope,
            method_context=methods,
            comparison_status=comparison,
            required_qualifiers=sorted(set(qualifiers)),
            limitations=sorted(set(limitations)),
            reason_codes=sorted(set(reasons)),
            independent_evidence_groups=len(lineage_groups),
            defects=sorted(defects, key=lambda item: item.value),
            severity=_severity(defects),
        )


__all__ = ["ClaimSupportAssessor"]
