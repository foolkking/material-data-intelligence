"""Bounded product projections for the Research Intelligence lifecycle.

The execution kernel remains authoritative: this module never creates an
AnalysisPlan, Job, ToolCall, or Artifact.  It provides strict, user-facing
projections around those persisted facts so an eventual LLM role can be
introduced without exposing private reasoning or allowing fabricated
scientific references.
"""

from __future__ import annotations

import json
import re
from typing import Any, Literal, Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


_PRIVATE_OR_TECHNICAL = re.compile(
    r"(?:chain[- ]?of[- ]?thought|思维链|system prompt|private reasoning|"
    r"api[_ -]?key|secret|token count|plan[_ -]?id|job[_ -]?id|toolcall|"
    r"inputref|registry hash|stacktrace)",
    re.IGNORECASE,
)
_CREDENTIAL_KEY = re.compile(r"(?:^|[_-])(api[_-]?key|secret|password|token)(?:$|[_-])", re.IGNORECASE)
_NUMERIC_FACT = re.compile(r"(?<![\w.])[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?")


class _StrictRoleModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ResearchTurnProjection(_StrictRoleModel):
    """Persistable assistant turn projection; never a model thought trace."""

    schemaVersion: Literal["1.0"] = "1.0"
    mode: Literal["answer", "clarify", "analyze", "unsupported"]
    assistantMessage: str = Field(min_length=1, max_length=4096)
    scientificIntent: str | None = Field(default=None, max_length=2048)
    scopeHints: list[str] = Field(default_factory=list, max_length=8)
    planSummary: list[str] = Field(default_factory=list, max_length=16)
    clarificationQuestion: str | None = Field(default=None, max_length=1024)
    sessionTitleCandidate: str | None = Field(default=None, max_length=160)
    groundingRefs: list[str] = Field(default_factory=list, max_length=32)

    @field_validator("assistantMessage", "scientificIntent", "clarificationQuestion", "sessionTitleCandidate")
    @classmethod
    def reject_private_or_technical_text(cls, value: str | None) -> str | None:
        if value and _PRIVATE_OR_TECHNICAL.search(value):
            raise ValueError("Research projection contains private or technical disclosure")
        return value

    @field_validator("scopeHints", "planSummary", "groundingRefs")
    @classmethod
    def reject_credential_values(cls, values: list[str]) -> list[str]:
        if any(_CREDENTIAL_KEY.search(value) for value in values):
            raise ValueError("Research projection contains credential-shaped data")
        return values

    @model_validator(mode="after")
    def validate_mode(self) -> "ResearchTurnProjection":
        if self.mode == "clarify" and not self.clarificationQuestion:
            raise ValueError("Clarification projections require a question")
        if self.mode != "clarify" and self.clarificationQuestion:
            raise ValueError("Only clarification projections may contain a question")
        return self


class ScientificFindingProjection(_StrictRoleModel):
    claimId: str = Field(min_length=1, max_length=96)
    text: str = Field(min_length=1, max_length=4096)
    evidenceIds: list[str] = Field(default_factory=list, max_length=16)
    artifactIds: list[str] = Field(default_factory=list, max_length=16)

    @field_validator("text")
    @classmethod
    def reject_private_text(cls, value: str) -> str:
        if _PRIVATE_OR_TECHNICAL.search(value):
            raise ValueError("Finding contains private or technical disclosure")
        return value


class ScientificInterpreterProjection(_StrictRoleModel):
    """A reader-facing view of a persisted grounded interpretation."""

    schemaVersion: Literal["1.0"] = "1.0"
    title: str = Field(min_length=1, max_length=256)
    assistantSummary: str = Field(min_length=1, max_length=4096)
    findings: list[ScientificFindingProjection] = Field(default_factory=list, max_length=32)
    limitations: list[str] = Field(default_factory=list, max_length=32)
    primaryResultRefs: list[str] = Field(default_factory=list, max_length=32)
    supportingResultRefs: list[str] = Field(default_factory=list, max_length=64)
    evidenceRefs: list[str] = Field(default_factory=list, max_length=128)
    sourceBundleId: str = Field(min_length=1, max_length=96)
    sourceJobId: str = Field(min_length=1, max_length=96)

    @field_validator("title", "assistantSummary")
    @classmethod
    def reject_private_text(cls, value: str) -> str:
        if _PRIVATE_OR_TECHNICAL.search(value):
            raise ValueError("Interpretation projection contains private or technical disclosure")
        return value

    @field_validator("limitations")
    @classmethod
    def reject_private_limitations(cls, values: list[str]) -> list[str]:
        if any(_PRIVATE_OR_TECHNICAL.search(value) for value in values):
            raise ValueError("Interpretation limitations contain private disclosure")
        return values


class ReportComposerProjection(_StrictRoleModel):
    """Immutable editorial payload backed exclusively by existing sources."""

    schemaVersion: Literal["1.0"] = "1.0"
    reportTitle: str = Field(min_length=1, max_length=256)
    researchQuestion: str = Field(min_length=1, max_length=4096)
    summary: str = Field(min_length=1, max_length=4096)
    findingRefs: list[str] = Field(default_factory=list, max_length=32)
    primaryFigureRefs: list[str] = Field(default_factory=list, max_length=16)
    supportingResultRefs: list[str] = Field(default_factory=list, max_length=64)
    evidenceRefs: list[str] = Field(default_factory=list, max_length=128)
    limitations: list[str] = Field(default_factory=list, max_length=32)
    methodSummary: list[str] = Field(default_factory=list, max_length=16)
    sourceBundleId: str = Field(min_length=1, max_length=96)
    sourceJobId: str = Field(min_length=1, max_length=96)

    @field_validator("reportTitle", "researchQuestion", "summary", "limitations", "methodSummary")
    @classmethod
    def reject_private_text(cls, value: Any) -> Any:
        values = value if isinstance(value, list) else [value]
        if any(_PRIVATE_OR_TECHNICAL.search(str(item)) for item in values):
            raise ValueError("Report projection contains private or technical disclosure")
        return value


def orchestrate_research_turn(
    question: str,
    *,
    scope: Mapping[str, Any] | None = None,
    plan: Mapping[str, Any] | None = None,
    provider_payload: Mapping[str, Any] | None = None,
) -> ResearchTurnProjection:
    """Create a bounded turn projection from server facts.

    ``provider_payload`` is deliberately optional.  A future Research Turn
    Orchestrator may provide it after strict JSON validation; the deterministic
    path is the safe default and keeps current offline/local deployments fully
    functional.
    """

    if provider_payload is not None:
        try:
            candidate = ResearchTurnProjection.model_validate(provider_payload)
            if candidate.mode == "analyze" and not plan and not candidate.planSummary:
                raise ValueError("Analyze projection requires a validated plan or plan summary")
            return candidate
        except Exception:
            # Provider output is advisory only.  Fall through to the grounded
            # deterministic projection rather than persisting unvalidated copy.
            pass

    question_text = str(question or "").strip()
    scope = scope or {}
    outcome = str(scope.get("status") or scope.get("outcome") or "").upper()
    dataset = str(scope.get("dataset_name") or scope.get("datasetName") or "当前已选择的数据")
    candidates = scope.get("candidates") or []
    if outcome in {"NEEDS_CLARIFICATION", "CLARIFICATION"}:
        names = [str(item.get("name") or item.get("dataset_name") or "") for item in candidates if isinstance(item, Mapping)]
        question_text = "请选择本次主要分析数据。"
        return ResearchTurnProjection(
            mode="clarify",
            assistantMessage=("这个问题可以使用多个数据集。\n\n" + "\n".join(f"{idx + 1}. {name}" for idx, name in enumerate(names) if name)),
            clarificationQuestion=question_text,
            scopeHints=names[:8],
            sessionTitleCandidate="选择本次分析数据",
        )
    if outcome == "UNSUPPORTED":
        return ResearchTurnProjection(
            mode="unsupported",
            assistantMessage=f"当前数据集“{dataset}”缺少完成这项分析所需的科学属性，因此没有创建分析运行。",
            scientificIntent=question_text[:2048] or None,
            scopeHints=[dataset],
            sessionTitleCandidate=question_text[:160] or "无法进行的分析",
        )

    steps: list[str] = []
    for item in (plan or {}).get("steps") or []:
        if not isinstance(item, Mapping):
            continue
        purpose = str(item.get("userFacingPurpose") or item.get("displayName") or item.get("purpose") or "").strip()
        if purpose and not _PRIVATE_OR_TECHNICAL.search(purpose):
            steps.append(purpose[:512])
    if steps:
        message = f"本次分析将以数据集“{dataset}”为范围。\n\n分析方案：\n" + "\n".join(f"{idx + 1}. {value}" for idx, value in enumerate(steps[:8]))
    else:
        message = f"本次分析将以数据集“{dataset}”为范围。"
    return ResearchTurnProjection(
        mode="analyze",
        assistantMessage=message,
        scientificIntent=question_text[:2048] or None,
        scopeHints=[dataset],
        planSummary=steps[:16],
        sessionTitleCandidate=question_text[:160] or "项目研究",
    )


def project_grounded_interpretation(
    interpretation: Mapping[str, Any],
    *,
    evidence_items: Sequence[Mapping[str, Any]] = (),
    artifact_ids: Sequence[str] = (),
    title: str | None = None,
) -> ScientificInterpreterProjection:
    """Project an existing interpretation and fail closed on dangling refs."""

    allowed_artifacts = {str(value) for value in artifact_ids if str(value)}
    evidence_by_id = {str(item.get("evidenceItemId") or item.get("id")): item for item in evidence_items}
    allowed_evidence = set(evidence_by_id)
    findings: list[ScientificFindingProjection] = []
    for claim in interpretation.get("claims") or []:
        if not isinstance(claim, Mapping):
            continue
        evidence_refs = [str(value) for key in ("subjectEvidenceIds", "supportingEvidenceIds", "limitingEvidenceIds", "contradictingEvidenceIds") for value in claim.get(key) or []]
        if any(value not in allowed_evidence for value in evidence_refs):
            continue
        related_artifacts = sorted({str(evidence_by_id[value].get("sourceArtifactId")) for value in evidence_refs if evidence_by_id[value].get("sourceArtifactId") in allowed_artifacts})
        text = str(claim.get("renderedText") or "").strip()
        if not text or _PRIVATE_OR_TECHNICAL.search(text):
            continue
        findings.append(ScientificFindingProjection(
            claimId=str(claim.get("claimId") or "claim"), text=text,
            evidenceIds=sorted(set(evidence_refs)), artifactIds=related_artifacts,
        ))
    all_evidence = sorted({value for finding in findings for value in finding.evidenceIds})
    primary = sorted({value for finding in findings for value in finding.artifactIds})
    limitations = [str(value) for value in interpretation.get("globalLimitations") or [] if str(value).strip() and not _PRIVATE_OR_TECHNICAL.search(str(value))]
    summary = findings[0].text if findings else "本次分析已生成可复核的科学结果；当前解释没有足够的用户级结论。"
    return ScientificInterpreterProjection(
        title=str(title or "科学结果")[:256],
        assistantSummary=summary,
        findings=findings,
        limitations=limitations[:32],
        primaryResultRefs=primary[:16],
        supportingResultRefs=sorted(allowed_artifacts - set(primary))[:64],
        evidenceRefs=all_evidence[:128],
        sourceBundleId=str(interpretation.get("sourceBundleId") or interpretation.get("bundleId") or "bundle_unavailable"),
        sourceJobId=str(interpretation.get("sourceJobId") or interpretation.get("jobId") or "job_unavailable"),
    )


def compose_grounded_report(
    *,
    research_question: str,
    interpretation: ScientificInterpreterProjection,
    artifact_ids: Sequence[str],
    figure_ids: Sequence[str] = (),
    method_summary: Sequence[str] = (),
) -> ReportComposerProjection:
    """Create a report-editor payload with references validated against inputs."""

    allowed_artifacts = {str(value) for value in artifact_ids if str(value)}
    figures = [str(value) for value in figure_ids if str(value) in allowed_artifacts]
    finding_refs = [finding.claimId for finding in interpretation.findings]
    referenced = set(interpretation.primaryResultRefs + interpretation.supportingResultRefs)
    if not referenced.issubset(allowed_artifacts):
        raise ValueError("Report result reference is not present in the validated artifact set")
    return ReportComposerProjection(
        reportTitle=interpretation.title,
        researchQuestion=str(research_question).strip()[:4096] or "本次研究围绕项目中的材料数据展开。",
        summary=interpretation.assistantSummary,
        findingRefs=finding_refs,
        primaryFigureRefs=figures[:16],
        supportingResultRefs=sorted(referenced - set(figures))[:64],
        evidenceRefs=interpretation.evidenceRefs,
        limitations=interpretation.limitations,
        methodSummary=[str(item).strip()[:512] for item in method_summary if str(item).strip()][:16],
        sourceBundleId=interpretation.sourceBundleId,
        sourceJobId=interpretation.sourceJobId,
    )


def validate_report_composer_projection(
    provider_payload: Mapping[str, Any],
    *,
    grounded: ReportComposerProjection,
) -> ReportComposerProjection:
    """Validate editorial LLM output against an already grounded report.

    The provider may improve wording and ordering, but it cannot introduce a
    new reference or a numeric statement absent from the deterministic source
    projection. Invalid output is rejected so callers can retain ``grounded``.
    """

    candidate = ReportComposerProjection.model_validate(provider_payload)
    reference_fields = (
        "findingRefs",
        "primaryFigureRefs",
        "supportingResultRefs",
        "evidenceRefs",
    )
    for field in reference_fields:
        if not set(getattr(candidate, field)).issubset(set(getattr(grounded, field))):
            raise ValueError(f"Report Composer introduced an ungrounded {field} reference")
    if candidate.sourceBundleId != grounded.sourceBundleId or candidate.sourceJobId != grounded.sourceJobId:
        raise ValueError("Report Composer changed the grounded source identity")
    grounded_numbers = set(_NUMERIC_FACT.findall("\n".join([
        grounded.reportTitle,
        grounded.researchQuestion,
        grounded.summary,
        *grounded.limitations,
        *grounded.methodSummary,
    ])))
    candidate_numbers = set(_NUMERIC_FACT.findall("\n".join([
        candidate.reportTitle,
        candidate.researchQuestion,
        candidate.summary,
        *candidate.limitations,
        *candidate.methodSummary,
    ])))
    if not candidate_numbers.issubset(grounded_numbers):
        raise ValueError("Report Composer introduced an ungrounded numeric statement")
    return candidate


def canonical_role_json(value: Mapping[str, Any]) -> str:
    """Stable JSON for persistence hashes/audit records; never logs secrets."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


__all__ = [
    "ReportComposerProjection",
    "ResearchTurnProjection",
    "ScientificFindingProjection",
    "ScientificInterpreterProjection",
    "canonical_role_json",
    "compose_grounded_report",
    "orchestrate_research_turn",
    "validate_report_composer_projection",
    "project_grounded_interpretation",
]
