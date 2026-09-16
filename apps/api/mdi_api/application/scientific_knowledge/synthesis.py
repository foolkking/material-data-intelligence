from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from mdi_llm.providers import LLMProviderError

from mdi_api.domain.scientific_knowledge.contracts import LiteratureEvidence
from mdi_api.application.scientific_reasoning.assessment import ClaimSupportAssessor
from mdi_api.domain.scientific_reasoning.contracts import (
    ClaimSupportStatus,
    MethodComparisonStatus,
    ProposedScientificClaim,
    ReasoningEvidence,
    ScientificClaimType,
)
from mdi_api.research_agent.llm.structured_client import StructuredLLMClient


PROMPT_VERSION = "scientific-literature-synthesis/2.0"
_NUMBER = re.compile(
    r"(?<![A-Za-z0-9_.])[-+]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][-+]?\d+)?"
)


class LiteratureSynthesisClaim(BaseModel):
    """A communication claim whose identities are opaque, server-issued refs."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    claim_id: str = Field(pattern=r"^claim_[1-9][0-9]*$")
    statement: str = Field(min_length=1, max_length=3000)
    literature_evidence_refs: list[str] = Field(default_factory=list, max_length=12)
    scientific_result_refs: list[str] = Field(default_factory=list, max_length=12)
    epistemic_status: str = Field(min_length=1, max_length=64)
    claim_type: ScientificClaimType
    support_status: ClaimSupportStatus
    scope: str = Field(min_length=1, max_length=1000)
    qualifiers: list[str] = Field(default_factory=list, max_length=12)
    contradicting_refs: list[str] = Field(default_factory=list, max_length=12)
    comparison_status: MethodComparisonStatus | None = None
    hypothesis_status: str | None = Field(default=None, max_length=64)
    limitations: list[str] = Field(default_factory=list, max_length=12)


class LiteratureSynthesisOutput(BaseModel):
    """Bounded synthesis; never a Result, qualification record, or bibliography."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    summary: str = Field(min_length=1, max_length=4000)
    claims: list[LiteratureSynthesisClaim] = Field(min_length=1, max_length=12)
    contradictions: list[str] = Field(default_factory=list, max_length=12)
    limitations: list[str] = Field(default_factory=list, max_length=12)


class LiteratureSynthesisValidationError(ValueError):
    def __init__(self, codes: tuple[str, ...]) -> None:
        self.codes = codes
        super().__init__("; ".join(codes))


def _project_supported_claims_after_repair(
    output: LiteratureSynthesisOutput,
    error: LiteratureSynthesisValidationError,
) -> LiteratureSynthesisOutput | None:
    """Drop only claim-level reasoning rejections after the one model repair.

    Identity, reference, numeric, and schema failures are never projected away.
    The replacement summary is deterministic and contains only claims that have
    survived the normal validator.
    """

    prefix = "SCIENTIFIC_REASONING_REJECTED:"
    if not error.codes or any(not code.startswith(prefix) for code in error.codes):
        return None
    rejected_ids = {
        code.removeprefix(prefix).split(":", maxsplit=1)[0]
        for code in error.codes
    }
    claims = [claim for claim in output.claims if claim.claim_id not in rejected_ids]
    if not claims:
        return None
    return output.model_copy(
        update={
            "summary": " ".join(claim.statement for claim in claims)[:4000],
            "claims": claims,
            "limitations": [
                *output.limitations,
                (
                    "One or more proposed claims were excluded because the "
                    "authorized evidence did not support their scientific "
                    "strength or scope."
                ),
            ][:12],
        }
    )


def validate_literature_synthesis(
    output: LiteratureSynthesisOutput,
    *,
    literature_evidence: Mapping[str, LiteratureEvidence],
    scientific_results: Mapping[str, Mapping[str, Any]] | None = None,
) -> LiteratureSynthesisOutput:
    """Fail closed on invented identities and ungrounded numeric statements."""

    result_rows = dict(scientific_results or {})
    errors: list[str] = []
    source_text = " ".join(
        (evidence.passage or "") for evidence in literature_evidence.values()
    )
    source_text += " " + " ".join(
        str(row.get("summary") or "") for row in result_rows.values()
    )

    def validate_numbers(text: str, location: str) -> None:
        if any(number not in source_text for number in _NUMBER.findall(text)):
            errors.append(f"UNSUPPORTED_NUMERIC_CLAIM:{location}")

    validate_numbers(output.summary, "summary")
    for index, text in enumerate(output.contradictions, start=1):
        validate_numbers(text, f"contradiction_{index}")
    for index, text in enumerate(output.limitations, start=1):
        validate_numbers(text, f"limitation_{index}")
    for claim in output.claims:
        if not claim.literature_evidence_refs and not claim.scientific_result_refs:
            errors.append(f"CLAIM_WITHOUT_EVIDENCE:{claim.claim_id}")
        if set(claim.literature_evidence_refs) - set(literature_evidence):
            errors.append(f"INVENTED_LITERATURE_REF:{claim.claim_id}")
        if set(claim.scientific_result_refs) - set(result_rows):
            errors.append(f"INVENTED_RESULT_REF:{claim.claim_id}")
        if set(claim.contradicting_refs) - (
            set(literature_evidence) | set(result_rows)
        ):
            errors.append(f"INVENTED_CONTRADICTING_REF:{claim.claim_id}")
        claim_source_text = " ".join(
            (literature_evidence[ref].passage or "")
            for ref in claim.literature_evidence_refs
            if ref in literature_evidence
        )
        claim_source_text += " " + " ".join(
            str(result_rows[ref].get("summary") or "")
            for ref in claim.scientific_result_refs
            if ref in result_rows
        )
        if any(
            number not in claim_source_text
            for number in _NUMBER.findall(claim.statement)
        ):
            errors.append(f"UNSUPPORTED_NUMERIC_CLAIM:{claim.claim_id}")
        for index, text in enumerate(claim.limitations, start=1):
            if any(
                number not in claim_source_text
                for number in _NUMBER.findall(text)
            ):
                errors.append(
                    f"UNSUPPORTED_NUMERIC_CLAIM:{claim.claim_id}.limitation_{index}"
                )
        reasoning_evidence: list[ReasoningEvidence] = []
        for ref in claim.literature_evidence_refs:
            if ref not in literature_evidence:
                continue
            evidence = literature_evidence[ref]
            numeric = list(evidence.numeric_claims)
            reasoning_evidence.append(
                ReasoningEvidence(
                    ref=ref,
                    origin="LITERATURE",
                    text=evidence.passage or "Bounded literature metadata evidence.",
                    scope=(
                        "; ".join(
                            sorted(
                                {
                                    item.material_or_system
                                    for item in numeric
                                    if item.material_or_system
                                }
                            )
                        )
                        or evidence.purpose.value
                    ),
                    method=next(
                        (item.method for item in numeric if item.method),
                        None,
                    ),
                    conditions=[
                        f"{key}={value}"
                        for item in numeric
                        for key, value in sorted(item.conditions.items())
                    ][:16],
                    lineage=str(evidence.work_id),
                    evidence_scope=evidence.scope.value,
                    limitations=(
                        ["Abstract-only evidence."]
                        if evidence.scope.value == "ABSTRACT_ONLY"
                        else []
                    ),
                )
            )
        for ref in claim.scientific_result_refs:
            if ref not in result_rows:
                continue
            row = result_rows[ref]
            reasoning_evidence.append(
                ReasoningEvidence(
                    ref=ref,
                    origin="COMPUTED",
                    text=str(row.get("summary") or "Authorized ScientificResult."),
                    scope=str(row.get("scope") or "current ScientificResult scope"),
                    method=(
                        str(row["method"]) if row.get("method") is not None else None
                    ),
                    conditions=[
                        f"{key}={value}"
                        for key, value in sorted(
                            dict(row.get("conditions") or {}).items()
                        )
                    ][:16],
                    lineage=str(row.get("lineage") or ref),
                    depends_on=[
                        str(value) for value in row.get("depends_on", [])
                    ][:16],
                    limitations=[
                        str(value) for value in row.get("limitations", [])
                    ][:16],
                    semantic_tags=[
                        str(value) for value in row.get("semantic_tags", [])
                    ][:16],
                )
            )
        if reasoning_evidence:
            assessment = ClaimSupportAssessor().assess(
                ProposedScientificClaim(
                    claim_id=claim.claim_id,
                    text=claim.statement,
                    claim_type=claim.claim_type,
                    support_status=claim.support_status,
                    evidence_refs=[
                        *claim.literature_evidence_refs,
                        *claim.scientific_result_refs,
                    ],
                    contradicting_refs=claim.contradicting_refs,
                    scope=claim.scope,
                    qualifiers=claim.qualifiers,
                    limitations=claim.limitations,
                    comparison_status=claim.comparison_status,
                    hypothesis_status=claim.hypothesis_status,
                ),
                reasoning_evidence,
            )
            if not assessment.accepted:
                errors.extend(
                    f"SCIENTIFIC_REASONING_REJECTED:{claim.claim_id}:{code}"
                    for code in assessment.reason_codes
                )
    if errors:
        raise LiteratureSynthesisValidationError(tuple(sorted(set(errors))))
    return output


def _prompt() -> str:
    return (
        Path(__file__).resolve().parent / "prompts" / "literature_synthesis_v1.txt"
    ).read_text(encoding="utf-8")


def _authorized_numeric_tokens(
    *,
    literature_evidence: Mapping[str, LiteratureEvidence],
    scientific_results: Mapping[str, Mapping[str, Any]] | None,
) -> list[str]:
    source_text = " ".join(
        evidence.passage or "" for evidence in literature_evidence.values()
    )
    source_text += " " + " ".join(
        str(row.get("summary") or "")
        for row in (scientific_results or {}).values()
    )
    return sorted(set(_NUMBER.findall(source_text)))


class BoundedLiteratureSynthesisProvider:
    """One evidence-bounded provider call plus at most one guided repair."""

    def __init__(
        self,
        client: StructuredLLMClient,
        *,
        timeout_seconds: float = 90.0,
    ) -> None:
        self.client = client
        self.timeout_seconds = timeout_seconds

    async def synthesize(
        self,
        *,
        research_question: str,
        literature_evidence: Mapping[str, LiteratureEvidence],
        literature_metadata: Mapping[str, Mapping[str, Any]],
        scientific_results: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> tuple[LiteratureSynthesisOutput, Any]:
        if set(literature_evidence) != set(literature_metadata):
            raise ValueError("literature metadata must match authorized evidence refs")
        authorized_numeric_tokens = _authorized_numeric_tokens(
            literature_evidence=literature_evidence,
            scientific_results=scientific_results,
        )
        payload = {
            "research_question": research_question[:4000],
            "literature_evidence": {
                ref: {
                    "title": str(literature_metadata[ref].get("title") or "")[:1000],
                    "citation": str(literature_metadata[ref].get("citation") or "")[
                        :2000
                    ],
                    "publication_status": str(
                        literature_metadata[ref].get("publication_status") or "UNKNOWN"
                    ),
                    "evidence_scope": evidence.scope.value,
                    "support_type": evidence.support_type.value,
                    "passage": evidence.passage,
                }
                for ref, evidence in literature_evidence.items()
            },
            "scientific_results": dict(scientific_results or {}),
            "constraints": {
                "references": "use only the opaque refs present in this payload",
                "source_identity": "do not create DOI, title, author, or source IDs",
                "authority": (
                    "literature is reported external evidence; scientific results "
                    "remain computed evidence; neither changes capability qualification"
                ),
                "numeric_claims": (
                    "use only exact numeric tokens listed in authorized_numeric_tokens; "
                    "do not calculate or state differences, ratios, percentages, ranges, "
                    "or other derived numbers"
                ),
                "authorized_numeric_tokens": authorized_numeric_tokens,
                "claim_reasoning": {
                    "claim_types": [item.value for item in ScientificClaimType],
                    "support_statuses": [item.value for item in ClaimSupportStatus],
                    "causality": (
                        "CAUSAL_CLAIM is not authorized by current platform evidence"
                    ),
                    "mechanism": (
                        "mechanistic interpretation must remain SUGGESTIVE or "
                        "CONSISTENT_WITH and explicitly hypothetical"
                    ),
                    "scope": (
                        "preserve material, method, condition, population and "
                        "LiteratureEvidence inspection scope"
                    ),
                    "independence": (
                        "do not describe common-lineage Results, preprint/published "
                        "versions, or review/primary relations as independent"
                    ),
                },
            },
        }
        first_error: Exception | None = None
        for attempt in range(2):
            try:
                response = await asyncio.wait_for(
                    self.client.generate_structured(
                        role="scientific_literature_synthesizer",
                        system_prompt=_prompt(),
                        input_payload=payload,
                        output_schema=LiteratureSynthesisOutput.model_json_schema(),
                        timeout_seconds=self.timeout_seconds,
                        request_context={
                            "prompt_version": PROMPT_VERSION,
                            "repair_attempted": attempt == 1,
                            "repair": (
                                None
                                if attempt == 0
                                else {
                                    "validation_error": str(first_error)[:1000],
                                    "allowed_literature_refs": sorted(
                                        literature_evidence
                                    ),
                                    "allowed_result_refs": sorted(
                                        (scientific_results or {}).keys()
                                    ),
                                    "scientific_reasoning_repair": (
                                        "remove or weaken every rejected claim; use "
                                        "LIMITATION for propositions that are not "
                                        "established; do not emit supported causal or "
                                        "universal claims; preserve every cited evidence "
                                        "limitation in that claim; a one-source mechanism "
                                        "must be explicitly tentative and SUGGESTIVE"
                                    ),
                                    "authorized_numeric_tokens": (
                                        authorized_numeric_tokens
                                    ),
                                    "numeric_repair": (
                                        "remove every derived number; retain only exact "
                                        "numeric tokens from authorized_numeric_tokens"
                                    ),
                                }
                            ),
                        },
                    ),
                    timeout=self.timeout_seconds,
                )
            except LLMProviderError as exc:
                first_error = exc
                if attempt == 0:
                    continue
                raise LiteratureSynthesisValidationError(
                    ("LITERATURE_SYNTHESIS_INVALID_AFTER_BOUNDED_REPAIR",)
                ) from exc
            try:
                output = LiteratureSynthesisOutput.model_validate(response.parsed)
                validate_literature_synthesis(
                    output,
                    literature_evidence=literature_evidence,
                    scientific_results=scientific_results,
                )
                if attempt == 1 and not response.repair_attempted:
                    response = response.model_copy(update={"repair_attempted": True})
                return output, response
            except (
                LiteratureSynthesisValidationError,
                ValidationError,
                ValueError,
            ) as exc:
                if attempt == 1 and isinstance(
                    exc, LiteratureSynthesisValidationError
                ):
                    projected = _project_supported_claims_after_repair(output, exc)
                    if projected is not None:
                        validate_literature_synthesis(
                            projected,
                            literature_evidence=literature_evidence,
                            scientific_results=scientific_results,
                        )
                        if not response.repair_attempted:
                            response = response.model_copy(
                                update={"repair_attempted": True}
                            )
                        return projected, response
                first_error = exc
        raise LiteratureSynthesisValidationError(
            ("LITERATURE_SYNTHESIS_INVALID_AFTER_BOUNDED_REPAIR",)
        ) from first_error


__all__ = [
    "BoundedLiteratureSynthesisProvider",
    "LiteratureSynthesisClaim",
    "LiteratureSynthesisOutput",
    "LiteratureSynthesisValidationError",
    "PROMPT_VERSION",
    "validate_literature_synthesis",
]
