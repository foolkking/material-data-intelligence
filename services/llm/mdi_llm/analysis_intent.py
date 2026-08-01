"""Versioned AnalysisIntent construction, validation, and clarification.

This module is deliberately upstream of the planner. It classifies and binds a
request to exact DataProfile 2.0 facts, but it does not inspect the Tool
Registry, select tools, or alter AnalysisPlan/Runtime behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import re
from typing import Any, Mapping, Sequence

from pydantic import ValidationError

from mdi_schemas import (
    ANALYSIS_INTENT_MAX_CLARIFICATION_ROUNDS,
    ANALYSIS_INTENT_MAX_QUESTIONS,
    ANALYSIS_INTENT_MAX_RAW_GOAL_CHARS,
    ANALYSIS_INTENT_MAX_RESOURCE_REFS,
    AnalysisIntent,
    AnalysisIntentClarification,
    AnalysisIntentConstraints,
    AnalysisIntentOutcome,
    AnalysisIntentProvenance,
    AmbiguitySource,
    CapabilityNeed,
    ClarificationAnswer,
    ClarificationOption,
    ClarificationQuestion,
    ClarificationQuestionType,
    DataProfile,
    DesiredOutput,
    IntentAmbiguity,
    IntentAnswerProvenance,
    IntentBindingOrigin,
    IntentCandidate,
    IntentDataScope,
    IntentDiagnostic,
    IntentResourceRef,
    IntentTargetSemantic,
    ScientificIntent,
    compute_analysis_intent_hash,
    deterministic_intent_id,
    validate_intent_json_bounds,
)

from .providers import OpenAICompatibleProvider, PlannerUserConfig
from .redaction import redact_credential_values


INTENT_PROMPT_VERSION = "phase10l1.intent.v1"
LLM_INTENT_PROMPT_VERSION = "phase10l5.intent.v5"
DETERMINISTIC_INTENT_MODEL = "bounded-rules-v1"

_DEFAULT_OUTPUTS_BY_INTENT: dict[ScientificIntent, tuple[DesiredOutput, ...]] = {
    ScientificIntent.dataset_overview: (DesiredOutput.summary, DesiredOutput.warnings, DesiredOutput.table),
    ScientificIntent.composition_analysis: (DesiredOutput.summary, DesiredOutput.table),
    ScientificIntent.property_distribution: (DesiredOutput.summary, DesiredOutput.table),
    ScientificIntent.dataset_comparison: (DesiredOutput.summary, DesiredOutput.comparison, DesiredOutput.table),
    ScientificIntent.composition_space: (DesiredOutput.plot, DesiredOutput.table, DesiredOutput.linked_samples),
    ScientificIntent.structure_analysis: (DesiredOutput.summary, DesiredOutput.warnings),
    ScientificIntent.trajectory_analysis: (DesiredOutput.summary, DesiredOutput.plot, DesiredOutput.warnings),
    ScientificIntent.phonon_analysis: (DesiredOutput.summary, DesiredOutput.warnings, DesiredOutput.plot, DesiredOutput.table),
    ScientificIntent.reciprocal_space_analysis: (DesiredOutput.summary, DesiredOutput.plot, DesiredOutput.three_dimensional_view),
    ScientificIntent.volumetric_analysis: (
        DesiredOutput.summary,
        DesiredOutput.warnings,
        DesiredOutput.three_dimensional_view,
        DesiredOutput.plot,
        DesiredOutput.table,
    ),
    ScientificIntent.ml_regression_evaluation: (DesiredOutput.summary, DesiredOutput.warnings, DesiredOutput.metrics),
    ScientificIntent.ml_uncertainty_evaluation: (DesiredOutput.summary, DesiredOutput.warnings, DesiredOutput.metrics),
    ScientificIntent.ml_classification_evaluation: (DesiredOutput.summary, DesiredOutput.warnings, DesiredOutput.metrics),
    ScientificIntent.sample_inspection: (DesiredOutput.summary, DesiredOutput.table, DesiredOutput.linked_samples),
    ScientificIntent.comparison: (DesiredOutput.summary, DesiredOutput.comparison),
    ScientificIntent.anomaly_candidate_review: (DesiredOutput.warnings, DesiredOutput.table, DesiredOutput.linked_samples),
    ScientificIntent.visualization: (DesiredOutput.plot,),
    ScientificIntent.report_or_export: (DesiredOutput.report,),
}


class AnalysisIntentError(ValueError):
    """Typed, user-safe AnalysisIntent failure."""

    def __init__(self, message: str, *, code: str, field: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.field = field


@dataclass(frozen=True)
class AnalysisIntentRequest:
    raw_goal: str
    dataset_id: str
    profile_id: str
    selected_resource_ids: tuple[str, ...] = ()
    selected_target_ids: tuple[str, ...] = ()
    constraints: AnalysisIntentConstraints = field(default_factory=AnalysisIntentConstraints)


@dataclass(frozen=True)
class ClarificationSubmission:
    intent_id: str
    answers: tuple[ClarificationAnswer, ...]
    expected_profile_semantic_hash: str


@dataclass(frozen=True)
class _Classification:
    intents: tuple[ScientificIntent, ...]
    required: tuple[CapabilityNeed, ...]
    optional: tuple[CapabilityNeed, ...]
    outputs: tuple[DesiredOutput, ...]
    required_resource_kind: str | None = None
    ml_kind: str | None = None


_WS = re.compile(r"\s+")
_CJK = re.compile(r"[\u3400-\u9fff]")
_LATIN = re.compile(r"[A-Za-z]")
_PROMPT_INJECTION = re.compile(
    r"ignore\s+(all\s+)?previous\s+instructions|system\s+prompt|忽略.{0,8}(指令|规则)",
    re.IGNORECASE,
)


def normalize_analysis_goal(raw_goal: str) -> str:
    """Apply whitespace-only normalization after mandatory secret redaction."""
    if not isinstance(raw_goal, str):
        raise AnalysisIntentError("The analysis goal must be text.", code="INTENT_GOAL_INVALID", field="rawGoal")
    if len(raw_goal) > ANALYSIS_INTENT_MAX_RAW_GOAL_CHARS:
        raise AnalysisIntentError("The analysis goal exceeds the character cap.", code="INTENT_GOAL_TOO_LONG", field="rawGoal")
    redacted = redact_credential_values(raw_goal)
    normalized = _WS.sub(" ", redacted).strip()
    if not normalized:
        raise AnalysisIntentError("The analysis goal cannot be empty.", code="INTENT_GOAL_EMPTY", field="rawGoal")
    return normalized


def detect_goal_language(goal: str) -> str:
    has_cjk = bool(_CJK.search(goal))
    has_latin = bool(_LATIN.search(goal))
    if has_cjk and has_latin:
        return "mixed"
    if has_cjk:
        return "zh"
    if has_latin:
        return "en"
    return "und"


class AnalysisIntentValidator:
    """Validate identity, profile bindings, caps, and immutable transitions."""

    def validate(
        self,
        intent: AnalysisIntent | Mapping[str, Any],
        *,
        profile: DataProfile,
        parent: AnalysisIntent | None = None,
    ) -> AnalysisIntent:
        try:
            validated = intent if isinstance(intent, AnalysisIntent) else AnalysisIntent.model_validate(intent)
        except Exception as exc:
            raise AnalysisIntentError("AnalysisIntent does not match schema v1.", code="INTENT_SCHEMA_INVALID") from exc

        validate_intent_json_bounds(validated.model_dump(mode="json"))
        expected_hash = compute_analysis_intent_hash(validated)
        if validated.intentHash != expected_hash or validated.intentId != deterministic_intent_id(expected_hash):
            raise AnalysisIntentError("AnalysisIntent identity does not match canonical content.", code="INTENT_HASH_MISMATCH")
        if profile.profileContractVersion != "2.0" or not profile.semanticHash:
            raise AnalysisIntentError("DataProfile 2.0 semantic identity is required.", code="PROFILE_2_REQUIRED")
        if validated.datasetId != profile.datasetId or validated.profileId != profile.profileId:
            raise AnalysisIntentError("AnalysisIntent dataset/profile identity is stale.", code="STALE_PROFILE")
        if validated.dataScope.profileSemanticHash != profile.semanticHash:
            raise AnalysisIntentError("DataProfile semantic hash changed.", code="STALE_PROFILE")
        dataset_version = profile.sampleIdentity.datasetVersion if profile.sampleIdentity else profile.version
        if validated.dataScope.datasetVersion != dataset_version:
            raise AnalysisIntentError("Dataset version changed.", code="STALE_PROFILE")

        resources = {item.objectId: item for item in profile.resourceSemantics}
        for ref in validated.dataScope.resourceRefs:
            current = resources.get(ref.objectId)
            if current is None or (
                current.objectHash != ref.objectHash
                or current.objectType != ref.objectType
                or current.kind != ref.kind
            ):
                raise AnalysisIntentError("A selected resource is stale or unavailable.", code="STALE_RESOURCE")

        target_candidates = {
            item.semanticId: item
            for item in _profile_target_semantic_candidates(profile)
        }
        for target in validated.targetSemantics:
            current = target_candidates.get(target.semanticId)
            if current is None or target.model_dump(mode="json", exclude={"origin"}) != current.model_dump(
                mode="json", exclude={"origin"}
            ):
                raise AnalysisIntentError(
                    "A target semantic is not an exact current Profile fact.",
                    code="INTENT_TARGET_SEMANTIC_INVALID",
                )

        required_needs = set(validated.requiredCapabilityNeeds)
        implied_needs = _required_needs_for_intents(validated.scientificIntents)
        if not implied_needs.issubset(required_needs):
            raise AnalysisIntentError(
                "AnalysisIntent omits a required capability need for its scientific intent.",
                code="INTENT_CAPABILITY_NEED_MISMATCH",
            )
        unavailable_needs = _unavailable_profile_needs(profile, required_needs)
        if unavailable_needs and validated.outcome is not AnalysisIntentOutcome.unsupported:
            raise AnalysisIntentError(
                "AnalysisIntent claims readiness for capability facts absent from the exact Profile.",
                code="INTENT_PROFILE_CAPABILITY_MISSING",
            )

        if validated.normalizedGoal != normalize_analysis_goal(validated.rawGoal):
            raise AnalysisIntentError("normalizedGoal expands or changes rawGoal semantics.", code="INTENT_GOAL_EXPANSION")
        if ScientificIntent.composition_space in validated.scientificIntents and not _contains(
            validated.normalizedGoal,
            "embedding",
            "cluster",
            "composition space",
            "dimensional reduction",
            "聚类",
            "嵌入",
            "成分空间",
            "降维",
        ):
            raise AnalysisIntentError(
                "composition_space requires an explicit embedding, clustering, or composition-space goal.",
                code="INTENT_SEMANTIC_EXPANSION",
            )
        _validate_profile_derived_questions(validated, profile)

        if parent is not None:
            if validated.provenance.parentIntentId != parent.intentId:
                raise AnalysisIntentError("Clarification revision has the wrong parent.", code="INTENT_PARENT_MISMATCH")
            if parent.clarification.round >= ANALYSIS_INTENT_MAX_CLARIFICATION_ROUNDS:
                raise AnalysisIntentError("Clarification limit reached.", code="CLARIFICATION_LIMIT_REACHED")
            if validated.intentId == parent.intentId or validated.intentHash == parent.intentHash:
                raise AnalysisIntentError("Clarification must create an immutable revision.", code="INTENT_REVISION_NOT_IMMUTABLE")
            if validated.datasetId != parent.datasetId or validated.profileId != parent.profileId:
                raise AnalysisIntentError("Clarification cannot change dataset/profile identity.", code="INTENT_SCOPE_CHANGED")
        return validated


class DeterministicAnalysisIntentBuilder:
    """Build auditable intents from allowlisted rules and exact Profile facts."""

    def __init__(self, *, validator: AnalysisIntentValidator | None = None) -> None:
        self.validator = validator or AnalysisIntentValidator()

    def build(
        self,
        request: AnalysisIntentRequest,
        *,
        profile: DataProfile,
        parent: AnalysisIntent | None = None,
        answer_bindings: Sequence[IntentAnswerProvenance] = (),
        created_at: str | None = None,
    ) -> AnalysisIntent:
        _validate_request_identity(request, profile)
        normalized = normalize_analysis_goal(request.raw_goal)
        safe_raw = redact_credential_values(request.raw_goal)
        classification = _specialize_profile_dependent_classification(_classify_goal(normalized), profile)
        unsupported = _unsupported_reasons(normalized)
        warnings: list[IntentDiagnostic] = []
        if safe_raw != request.raw_goal:
            warnings.append(_diagnostic("INTENT_SECRET_REDACTED", "rawGoal", "Credential-shaped text was redacted before persistence."))
        if _PROMPT_INJECTION.search(normalized):
            warnings.append(_diagnostic("INTENT_POLICY_TEXT_INERT", "rawGoal", "Instruction-like text is inert and cannot change system policy."))

        resource_refs, resource_ambiguities, resource_missing, resource_questions = _resolve_resources(
            request,
            profile,
            required_kind=classification.required_resource_kind,
        )
        targets, target_ambiguities, target_missing, target_questions = _resolve_targets(
            request,
            profile,
            ml_kind=classification.ml_kind,
        )
        ambiguities = [*resource_ambiguities, *target_ambiguities]
        generic_profile_needs = set(classification.required) & {
            CapabilityNeed.tabular_data,
            CapabilityNeed.composition_data,
            CapabilityNeed.material_property_data,
            CapabilityNeed.comparison_groups,
            CapabilityNeed.sample_identity,
        }
        unavailable_profile_needs = sorted(
            _unavailable_profile_needs(profile, generic_profile_needs),
            key=lambda item: item.value,
        )
        profile_missing = [
            _diagnostic(
                "PROFILE_CAPABILITY_MISSING",
                "requiredCapabilityNeeds",
                f"The exact DataProfile does not provide {need.value}.",
                boundary="MISSING_DATA",
            )
            for need in unavailable_profile_needs
        ]
        missing = [*resource_missing, *target_missing, *profile_missing]
        questions = [*resource_questions, *target_questions][:ANALYSIS_INTENT_MAX_QUESTIONS]

        if unsupported or missing:
            outcome = AnalysisIntentOutcome.unsupported
            unsupported = [*unsupported, *missing]
            questions = []
            ambiguities = [item for item in ambiguities if not item.blocking]
        elif any(item.blocking for item in ambiguities):
            if request.constraints.clarificationAllowed and questions and parent is None:
                outcome = AnalysisIntentOutcome.needs_clarification
            else:
                outcome = AnalysisIntentOutcome.unsupported
                unsupported = [
                    _diagnostic(
                        "CLARIFICATION_LIMIT_REACHED" if parent else "CLARIFICATION_DISABLED",
                        "clarification",
                        "The remaining ambiguity cannot be resolved within the bounded clarification policy.",
                    )
                ]
                questions = []
        elif not classification.intents:
            outcome = AnalysisIntentOutcome.unsupported
            unsupported = [_diagnostic("INTENT_NOT_RECOGNIZED", "rawGoal", "The request does not map to the supported intent vocabulary.")]
        else:
            outcome = AnalysisIntentOutcome.ready

        origin = IntentBindingOrigin.clarification_answer if parent else IntentBindingOrigin.user_explicit
        scope = IntentDataScope(
            datasetId=profile.datasetId,
            datasetVersion=profile.sampleIdentity.datasetVersion if profile.sampleIdentity else profile.version,
            profileId=profile.profileId,
            profileContractVersion=profile.profileContractVersion or "2.0",
            profileSemanticHash=profile.semanticHash or "",
            resourceRefs=[ref.model_copy(update={"origin": origin}) for ref in resource_refs],
            modelIds=list(request.constraints.modelIds),
            groupIds=list(request.constraints.groupIds),
            origin=origin,
        )
        clarification_round = 1 if parent else 0
        payload: dict[str, Any] = {
            "schemaVersion": "1.0",
            "intentId": "pending",
            "intentHash": "0" * 64,
            "datasetId": profile.datasetId,
            "profileId": profile.profileId,
            "rawGoal": safe_raw,
            "normalizedGoal": normalized,
            "language": detect_goal_language(normalized),
            "dataScope": scope.model_dump(mode="json"),
            "scientificIntents": [value.value for value in classification.intents],
            "targetSemantics": [value.model_copy(update={"origin": origin}).model_dump(mode="json") for value in targets],
            "desiredOutputs": [value.value for value in classification.outputs],
            "constraints": request.constraints.model_dump(mode="json"),
            "requiredCapabilityNeeds": [value.value for value in classification.required],
            "optionalCapabilityNeeds": [value.value for value in classification.optional],
            "ambiguities": [value.model_dump(mode="json") for value in ambiguities],
            "missingFacts": [value.model_dump(mode="json") for value in missing],
            "unsupportedReasons": [value.model_dump(mode="json") for value in unsupported],
            "outcome": outcome.value,
            "clarification": AnalysisIntentClarification(
                round=clarification_round,
                questions=questions,
                answers=[ClarificationAnswer(questionId=value.questionId, selectedValues=value.selectedValues) for value in answer_bindings],
            ).model_dump(mode="json"),
            "provenance": AnalysisIntentProvenance(
                provider="deterministic_mock",
                model=DETERMINISTIC_INTENT_MODEL,
                promptVersion=INTENT_PROMPT_VERSION,
                createdAt=created_at or datetime.now(timezone.utc).isoformat(),
                parentIntentId=parent.intentId if parent else None,
                answerBindings=list(answer_bindings),
            ).model_dump(mode="json"),
            "warnings": [value.model_dump(mode="json") for value in warnings],
        }
        intent_hash = compute_analysis_intent_hash(payload)
        payload["intentHash"] = intent_hash
        payload["intentId"] = deterministic_intent_id(intent_hash)
        intent = AnalysisIntent.model_validate(payload)
        return self.validator.validate(intent, profile=profile, parent=parent)

    def clarify(
        self,
        parent: AnalysisIntent,
        submission: ClarificationSubmission,
        *,
        profile: DataProfile,
    ) -> AnalysisIntent:
        self.validator.validate(parent, profile=profile)
        if submission.intent_id != parent.intentId:
            raise AnalysisIntentError("Clarification intent identity does not match.", code="INTENT_PARENT_MISMATCH")
        if submission.expected_profile_semantic_hash != parent.dataScope.profileSemanticHash:
            raise AnalysisIntentError("The clarification was based on a stale profile.", code="STALE_PROFILE")
        if parent.outcome is not AnalysisIntentOutcome.needs_clarification:
            raise AnalysisIntentError("This intent does not accept clarification.", code="CLARIFICATION_NOT_ALLOWED")
        if parent.clarification.round >= ANALYSIS_INTENT_MAX_CLARIFICATION_ROUNDS:
            raise AnalysisIntentError("Clarification limit reached.", code="CLARIFICATION_LIMIT_REACHED")

        questions = {question.questionId: question for question in parent.clarification.questions}
        answers = {answer.questionId: answer for answer in submission.answers}
        if len(answers) != len(submission.answers) or set(answers) != set(questions):
            raise AnalysisIntentError("Every clarification question requires one unique answer.", code="CLARIFICATION_ANSWER_INVALID")

        selected_resources = list(parent.constraints.includeResourceIds)
        selected_targets = list(parent.constraints.targetIds)
        bindings: list[IntentAnswerProvenance] = []
        for question_id, question in questions.items():
            answer = answers[question_id]
            allowed = {option.value for option in question.options}
            values = list(answer.selectedValues)
            if not values or any(value not in allowed for value in values):
                raise AnalysisIntentError("Clarification answer is not one of the current options.", code="CLARIFICATION_OPTION_INVALID")
            if question.type in {ClarificationQuestionType.select_one, ClarificationQuestionType.confirm} and len(values) != 1:
                raise AnalysisIntentError("This clarification question requires exactly one answer.", code="CLARIFICATION_ANSWER_INVALID")
            if question.bindsTo == "dataScope.resourceRefs":
                selected_resources.extend(values)
            elif question.bindsTo == "targetSemantics":
                selected_targets.extend(values)
            else:
                raise AnalysisIntentError("Clarification binding target is unsupported.", code="CLARIFICATION_BINDING_INVALID")
            bindings.append(IntentAnswerProvenance(questionId=question_id, selectedValues=values))

        revised_constraints = parent.constraints.model_copy(
            update={
                "includeResourceIds": sorted(set(selected_resources)),
                "targetIds": sorted(set(selected_targets)),
            }
        )
        request = AnalysisIntentRequest(
            raw_goal=parent.rawGoal,
            dataset_id=parent.datasetId,
            profile_id=parent.profileId,
            selected_resource_ids=tuple(sorted(set(selected_resources))),
            selected_target_ids=tuple(sorted(set(selected_targets))),
            constraints=revised_constraints,
        )
        return self.build(request, profile=profile, parent=parent, answer_bindings=bindings)


class OpenAICompatibleAnalysisIntentBuilder:
    """Strict JSON LLM intent path with no repair and no Mock fallback."""

    def __init__(
        self,
        provider: OpenAICompatibleProvider,
        *,
        validator: AnalysisIntentValidator | None = None,
    ) -> None:
        self.provider = provider
        self.validator = validator or AnalysisIntentValidator()

    def build(
        self,
        request: AnalysisIntentRequest,
        *,
        profile: DataProfile,
        user_config: PlannerUserConfig | None = None,
    ) -> AnalysisIntent:
        _validate_request_identity(request, profile)
        messages = build_analysis_intent_messages(request, profile=profile)
        response = self.provider.complete_json(
            messages=messages,
            user_config=user_config,
            purpose="INTENT_EXTRACTION",
        )
        raw = response.raw_text
        if not isinstance(raw, str) or raw.strip().startswith("```"):
            raise AnalysisIntentError("LLM Intent output must be one strict JSON object.", code="INTENT_LLM_JSON_INVALID")
        try:
            parsed = json.loads(raw, object_pairs_hook=_reject_duplicate_json_keys)
        except json.JSONDecodeError as exc:
            raise AnalysisIntentError("LLM Intent output is not strict JSON.", code="INTENT_LLM_JSON_INVALID") from exc
        if not isinstance(parsed, dict) or raw.strip() != json.dumps(parsed, ensure_ascii=False, separators=(",", ":")):
            # Whitespace is accepted, but commentary/prose and duplicate trailing values are not.
            try:
                decoder = json.JSONDecoder()
                _, end = decoder.raw_decode(raw.strip())
            except json.JSONDecodeError as exc:
                raise AnalysisIntentError("LLM Intent output is not a single JSON object.", code="INTENT_LLM_JSON_INVALID") from exc
            if raw.strip()[end:].strip():
                raise AnalysisIntentError("LLM Intent output contains extra prose.", code="INTENT_LLM_JSON_INVALID")
        if parsed.get("datasetId") != profile.datasetId or parsed.get("profileId") != profile.profileId:
            raise AnalysisIntentError("LLM Intent invented dataset/profile identity.", code="INTENT_LLM_IDENTITY_INVALID")
        expected_normalized = normalize_analysis_goal(request.raw_goal)
        expected_language = detect_goal_language(expected_normalized)
        if parsed.get("rawGoal") != request.raw_goal:
            raise AnalysisIntentError("LLM Intent changed the exact raw goal.", code="INTENT_LLM_RAW_GOAL_MISMATCH")
        if parsed.get("normalizedGoal") != expected_normalized:
            raise AnalysisIntentError("LLM Intent changed the application-owned normalized goal.", code="INTENT_LLM_NORMALIZED_GOAL_MISMATCH")
        if parsed.get("language") != expected_language:
            raise AnalysisIntentError("LLM Intent changed the application-owned goal language.", code="INTENT_LLM_LANGUAGE_MISMATCH")
        _canonicalize_llm_profile_bindings(parsed, request=request, profile=profile)
        supplied_provenance = parsed.get("provenance")
        if supplied_provenance is not None and (
            not isinstance(supplied_provenance, dict)
            or set(supplied_provenance) - {"provider", "model", "promptVersion", "createdAt", "parentIntentId", "answerBindings"}
        ):
            raise AnalysisIntentError("LLM Intent contains unknown provenance fields.", code="INTENT_LLM_SCHEMA_INVALID")
        parsed["intentId"] = "pending"
        parsed["intentHash"] = "0" * 64
        parsed["provenance"] = {
            "provider": str(getattr(getattr(self.provider, "meta", None), "name", "openai_compatible")),
            "model": response.model,
            "promptVersion": LLM_INTENT_PROMPT_VERSION,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "parentIntentId": None,
            "answerBindings": [],
        }
        try:
            provisional = AnalysisIntent.model_validate(parsed)
        except ValidationError as exc:
            diagnostics = sorted(
                {
                    ".".join(str(part) for part in error.get("loc", ())) + ":" + str(error.get("type") or "invalid")
                    for error in exc.errors(include_url=False, include_context=False, include_input=False)
                }
            )
            bounded = ",".join(diagnostics[:16])
            raise AnalysisIntentError(
                f"LLM Intent failed schema validation at {bounded or 'unknown' }.",
                code="INTENT_LLM_SCHEMA_INVALID",
            ) from exc
        except Exception as exc:
            raise AnalysisIntentError("LLM Intent failed schema validation.", code="INTENT_LLM_SCHEMA_INVALID") from exc
        canonical = provisional.model_dump(mode="json")
        intent_hash = compute_analysis_intent_hash(canonical)
        canonical["intentHash"] = intent_hash
        canonical["intentId"] = deterministic_intent_id(intent_hash)
        intent = AnalysisIntent.model_validate(canonical)
        return self.validator.validate(intent, profile=profile)


def _canonicalize_llm_profile_bindings(
    parsed: dict[str, Any],
    *,
    request: AnalysisIntentRequest,
    profile: DataProfile,
) -> None:
    """Replace provider-authored resource/target choices with Profile-owned facts."""
    try:
        intents = {ScientificIntent(value) for value in parsed.get("scientificIntents", [])}
    except (TypeError, ValueError):
        return
    ml_kind = None
    if ScientificIntent.ml_uncertainty_evaluation in intents:
        ml_kind = "regression_uncertainty"
    elif ScientificIntent.ml_regression_evaluation in intents:
        ml_kind = "regression"
    elif ScientificIntent.ml_classification_evaluation in intents:
        ml_kind = "classification"

    required_kinds = {
        kind
        for intent, kind in {
            ScientificIntent.structure_analysis: "structure",
            ScientificIntent.trajectory_analysis: "trajectory",
            ScientificIntent.phonon_analysis: "phonon",
            ScientificIntent.reciprocal_space_analysis: "reciprocal",
            ScientificIntent.volumetric_analysis: "volumetric",
        }.items()
        if intent in intents
    }
    required_kind = next(iter(required_kinds)) if len(required_kinds) == 1 else None
    resource_refs, resource_ambiguities, resource_missing, resource_questions = _resolve_resources(
        request,
        profile,
        required_kind=required_kind,
    )
    targets, target_ambiguities, target_missing, target_questions = _resolve_targets(
        request,
        profile,
        ml_kind=ml_kind,
    )
    scope = dict(parsed.get("dataScope") or {})
    scope.update(
        {
            "datasetId": profile.datasetId,
            "datasetVersion": profile.sampleIdentity.datasetVersion if profile.sampleIdentity else profile.version,
            "profileId": profile.profileId,
            "profileContractVersion": profile.profileContractVersion,
            "profileSemanticHash": profile.semanticHash,
            "resourceRefs": [item.model_dump(mode="json") for item in resource_refs],
        }
    )
    parsed["dataScope"] = scope
    if ml_kind is not None:
        parsed["targetSemantics"] = [item.model_dump(mode="json") for item in targets]

    questions = [*resource_questions, *target_questions][:ANALYSIS_INTENT_MAX_QUESTIONS]
    ambiguities = [*resource_ambiguities, *target_ambiguities]
    missing = [*resource_missing, *target_missing]
    if missing:
        parsed["ambiguities"] = [item.model_dump(mode="json") for item in ambiguities if not item.blocking]
        parsed["missingFacts"] = [item.model_dump(mode="json") for item in missing]
        parsed["unsupportedReasons"] = [item.model_dump(mode="json") for item in missing]
        parsed["outcome"] = AnalysisIntentOutcome.unsupported.value
        parsed["clarification"] = AnalysisIntentClarification().model_dump(mode="json")
        return
    if not questions or not any(item.blocking for item in ambiguities):
        return

    parsed["ambiguities"] = [item.model_dump(mode="json") for item in ambiguities]
    parsed["missingFacts"] = []
    parsed["unsupportedReasons"] = []
    parsed["outcome"] = AnalysisIntentOutcome.needs_clarification.value
    parsed["clarification"] = {
        "round": 0,
        "questions": [item.model_dump(mode="json") for item in questions],
        "answers": [],
    }


def build_analysis_intent_messages(request: AnalysisIntentRequest, *, profile: DataProfile) -> list[dict[str, str]]:
    """Return bounded, non-executable context for the strict LLM Intent call."""
    profile_facts = {
        "datasetId": profile.datasetId,
        "datasetVersion": profile.sampleIdentity.datasetVersion if profile.sampleIdentity else profile.version,
        "profileId": profile.profileId,
        "profileContractVersion": profile.profileContractVersion,
        "profileSemanticHash": profile.semanticHash,
        "resources": [item.model_dump(mode="json") for item in profile.resourceSemantics[:ANALYSIS_INTENT_MAX_RESOURCE_REFS]],
        "semanticColumns": [item.model_dump(mode="json") for item in profile.semanticColumns[:32]],
        "semanticGroups": [item.model_dump(mode="json") for item in profile.semanticGroups[:32]],
        "targetSemanticCandidates": [
            item.model_dump(mode="json")
            for item in _profile_target_semantic_candidates(profile)[:32]
        ],
    }
    schema = AnalysisIntent.model_json_schema()
    normalized_goal = normalize_analysis_goal(request.raw_goal)
    language = detect_goal_language(normalized_goal)
    output_template = {
        "schemaVersion": "1.0",
        "intentId": "application-owned",
        "intentHash": "0" * 64,
        "datasetId": profile.datasetId,
        "profileId": profile.profileId,
        "rawGoal": redact_credential_values(request.raw_goal),
        "normalizedGoal": normalized_goal,
        "language": language,
        "dataScope": {
            "datasetId": profile.datasetId,
            "datasetVersion": profile_facts["datasetVersion"],
            "profileId": profile.profileId,
            "profileContractVersion": profile.profileContractVersion,
            "profileSemanticHash": profile.semanticHash,
            "resourceRefs": [],
            "sampleIds": [],
            "groupIds": [],
            "modelIds": [],
            "origin": "PROFILE_EXACT",
        },
        "scientificIntents": [],
        "targetSemantics": [],
        "desiredOutputs": [],
        "constraints": {
            "includeResourceIds": list(request.selected_resource_ids),
            "excludeResourceIds": [],
            "includeScientificIntents": [],
            "excludeScientificIntents": [],
            "targetIds": list(request.selected_target_ids),
            "modelIds": [],
            "groupIds": [],
            "outputPreferences": [],
            "maxAnalyses": None,
            "maxToolCalls": None,
            "timePreference": None,
            "costPreference": None,
            "clarificationAllowed": request.constraints.clarificationAllowed,
            "descriptiveOnly": request.constraints.descriptiveOnly,
            "forbidDerivedInterpretation": request.constraints.forbidDerivedInterpretation,
        },
        "requiredCapabilityNeeds": [],
        "optionalCapabilityNeeds": [],
        "ambiguities": [],
        "missingFacts": [],
        "unsupportedReasons": [],
        "outcome": "READY",
        "clarification": {
            "round": 0,
            "maxRounds": 1,
            "maxQuestionsPerRound": 3,
            "questions": [],
            "answers": [],
        },
        "provenance": {
            "provider": "deepseek",
            "model": "application-owned",
            "promptVersion": LLM_INTENT_PROMPT_VERSION,
            "createdAt": "application-owned",
            "parentIntentId": None,
            "answerBindings": [],
        },
        "warnings": [],
    }
    system = (
        "Produce exactly one JSON object matching AnalysisIntent v1. Use placeholder values for intentId, intentHash, "
        "and provenance because the application owns those fields. "
        "Use outputTemplate as the required object shape, replacing semantic placeholder arrays only with exact allowed values. "
        "clarification must always be an object with round, maxRounds, maxQuestionsPerRound, questions, and answers; "
        "for READY use the empty clarification object shown in outputTemplate, never null, an array, a string, or a boolean. "
        "Copy exactRawGoal into rawGoal, exactNormalizedGoal into normalizedGoal, and exactLanguage into language without changes. "
        "Set requiredCapabilityNeeds to the sorted union declared by requiredCapabilityNeedsByScientificIntent for every selected scientific intent. "
        "When the user did not specify a delivery format, set desiredOutputs to the sorted union declared by defaultDesiredOutputsByScientificIntent. "
        "When the raw goal explicitly requests a delivery format, include only the explicitly requested delivery outputs; do not add default summary, table, comparison, report, or warning outputs. "
        "A named chart form such as scatter, histogram, correlation matrix, heatmap, treemap, or sunburst is an explicit visualization request: include visualization and plot, preserve the named form in rawGoal, and do not substitute another chart form. "
        "Composition distribution is composition_analysis, not composition_space. Select composition_space only when the raw goal explicitly asks for "
        "embedding, clustering, or composition space. Do not add visualization merely because a plot-capable tool may exist. "
        "Do not choose tools, execute code, invent identifiers, use Markdown, or add prose. "
        "Only candidates in the supplied DataProfile are valid. Future/Not Planned and arbitrary "
        "code requests must be UNSUPPORTED. READY cannot contain a blocking ambiguity."
    )
    user = json.dumps(
        {
            "rawGoal": redact_credential_values(request.raw_goal),
            "exactRawGoal": redact_credential_values(request.raw_goal),
            "exactNormalizedGoal": normalized_goal,
            "exactLanguage": language,
            "selectedResourceIds": list(request.selected_resource_ids),
            "selectedTargetIds": list(request.selected_target_ids),
            "profile": profile_facts,
            "scientificIntentVocabulary": [value.value for value in ScientificIntent],
            "requiredCapabilityNeedsByScientificIntent": {
                intent.value: sorted(need.value for need in _required_needs_for_intents((intent,)))
                for intent in ScientificIntent
            },
            "defaultDesiredOutputsByScientificIntent": {
                intent.value: sorted(output.value for output in _DEFAULT_OUTPUTS_BY_INTENT.get(intent, ()))
                for intent in ScientificIntent
            },
            "scientificIntentDisambiguation": {
                "composition_analysis": "composition, formula, element or composition distribution facts",
                "composition_space": "only explicit embedding, clustering, dimensional reduction or composition-space requests",
                "property_distribution": "property coverage or distribution facts",
                "visualization": "only an explicit visualization request, never inferred from tool availability",
            },
            "outcomes": [value.value for value in AnalysisIntentOutcome],
            "clarificationPolicy": {"maxRounds": 1, "maxQuestionsPerRound": 3},
            "outputTemplate": output_template,
            "schema": schema,
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _validate_request_identity(request: AnalysisIntentRequest, profile: DataProfile) -> None:
    if request.dataset_id != profile.datasetId or request.profile_id != profile.profileId:
        raise AnalysisIntentError("Requested dataset/profile does not match the exact profile.", code="STALE_PROFILE")
    if profile.profileContractVersion != "2.0" or not profile.semanticHash:
        raise AnalysisIntentError("DataProfile 2.0 semantic identity is required.", code="PROFILE_2_REQUIRED")
    if len(request.selected_resource_ids) > ANALYSIS_INTENT_MAX_RESOURCE_REFS:
        raise AnalysisIntentError("Selected resources exceed the cap.", code="INTENT_RESOURCE_CAP_EXCEEDED")
    if len(set(request.selected_resource_ids)) != len(request.selected_resource_ids):
        raise AnalysisIntentError("Selected resource identities must be unique.", code="INTENT_RESOURCE_DUPLICATE")


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AnalysisIntentError("LLM Intent JSON contains a duplicate field.", code="INTENT_LLM_JSON_INVALID")
        result[key] = value
    return result


def _required_needs_for_intents(intents: Sequence[ScientificIntent]) -> set[CapabilityNeed]:
    mapping: dict[ScientificIntent, tuple[CapabilityNeed, ...]] = {
        ScientificIntent.dataset_overview: (CapabilityNeed.tabular_data,),
        ScientificIntent.composition_analysis: (CapabilityNeed.composition_data,),
        ScientificIntent.property_distribution: (CapabilityNeed.material_property_data,),
        ScientificIntent.dataset_comparison: (CapabilityNeed.comparison_groups,),
        ScientificIntent.composition_space: (CapabilityNeed.tabular_data, CapabilityNeed.composition_data),
        ScientificIntent.structure_analysis: (CapabilityNeed.structure_resource,),
        ScientificIntent.trajectory_analysis: (CapabilityNeed.trajectory_resource,),
        ScientificIntent.phonon_analysis: (CapabilityNeed.phonon_resource,),
        ScientificIntent.reciprocal_space_analysis: (CapabilityNeed.reciprocal_space_resource,),
        ScientificIntent.volumetric_analysis: (CapabilityNeed.volumetric_resource,),
        ScientificIntent.ml_regression_evaluation: (CapabilityNeed.regression_semantics,),
        ScientificIntent.ml_uncertainty_evaluation: (
            CapabilityNeed.regression_semantics,
            CapabilityNeed.uncertainty_semantics,
        ),
        ScientificIntent.ml_classification_evaluation: (CapabilityNeed.classification_semantics,),
        ScientificIntent.sample_inspection: (CapabilityNeed.sample_identity,),
    }
    return {need for intent in intents for need in mapping.get(intent, ())}


def _unavailable_profile_needs(profile: DataProfile, needs: set[CapabilityNeed]) -> set[CapabilityNeed]:
    resource_capabilities = {
        capability.casefold()
        for resource in profile.resourceSemantics
        for capability in resource.capabilities
    }
    resource_kinds = {resource.kind.casefold() for resource in profile.resourceSemantics}
    semantic_roles = {
        role.role
        for column in profile.semanticColumns
        for role in column.roles
    }
    group_kinds = {
        group.kind
        for group in profile.semanticGroups
        if group.status in {"COMPLETE", "AMBIGUOUS"}
    }
    checks = {
        CapabilityNeed.tabular_data: bool(resource_kinds & {"table", "dataframe", "tabular"}) or profile.tableSummary is not None,
        CapabilityNeed.composition_data: "composition" in resource_capabilities or "material_formula" in semantic_roles,
        CapabilityNeed.material_property_data: bool(
            semantic_roles & {"material_property", "regression_target", "classification_target"}
        ),
        CapabilityNeed.comparison_groups: bool(profile.semanticGroups),
        CapabilityNeed.structure_resource: any(_resource_matches(item.kind, item.capabilities, "structure") for item in profile.resourceSemantics),
        CapabilityNeed.trajectory_resource: any(_resource_matches(item.kind, item.capabilities, "trajectory") for item in profile.resourceSemantics),
        CapabilityNeed.phonon_resource: any(_resource_matches(item.kind, item.capabilities, "phonon") for item in profile.resourceSemantics),
        CapabilityNeed.reciprocal_space_resource: any(_resource_matches(item.kind, item.capabilities, "reciprocal") for item in profile.resourceSemantics),
        CapabilityNeed.volumetric_resource: any(_resource_matches(item.kind, item.capabilities, "volumetric") for item in profile.resourceSemantics),
        CapabilityNeed.regression_semantics: "regression" in group_kinds,
        CapabilityNeed.uncertainty_semantics: any(
            group.kind == "regression" and group.status in {"COMPLETE", "AMBIGUOUS"} and group.uncertaintyColumns
            for group in profile.semanticGroups
        ),
        CapabilityNeed.classification_semantics: bool(group_kinds & {"classification", "class_probability"}),
        CapabilityNeed.sample_identity: profile.sampleIdentity is not None,
    }
    return {need for need in needs if not checks.get(need, False)}


def _profile_target_semantic_candidates(profile: DataProfile) -> list[IntentTargetSemantic]:
    candidates: dict[str, IntentTargetSemantic] = {}
    columns = {(item.objectId, item.column): item for item in profile.semanticColumns}
    for column in profile.semanticColumns:
        for role in column.roles:
            if role.role == "material_property":
                semantic_id = f"{column.objectId}:material_property:{column.column}"
                candidates[semantic_id] = IntentTargetSemantic(
                    semanticId=semantic_id,
                    role="material_property",
                    objectId=column.objectId,
                    column=column.column,
                    unit=column.unit,
                    groupId=role.groupId,
                    origin=IntentBindingOrigin.profile_exact,
                )
    for group in profile.semanticGroups:
        if group.status not in {"COMPLETE", "AMBIGUOUS"}:
            continue
        object_ids = sorted(
            {
                item.objectId
                for item in profile.semanticColumns
                if any(role.groupId == group.groupId for role in item.roles)
            }
        )
        object_id = object_ids[0] if object_ids else ""
        roles_and_columns: list[tuple[str, Sequence[str]]] = [
            ("target", group.targetColumns),
            ("prediction", group.predictionColumns),
            ("uncertainty", group.uncertaintyColumns),
            ("probability", group.probabilityColumns),
        ]
        for suffix, names in roles_and_columns:
            for name in names:
                column = columns.get((object_id, name))
                role = {
                    ("regression", "target"): "regression_target",
                    ("regression", "prediction"): "regression_prediction",
                    ("regression", "uncertainty"): "regression_uncertainty",
                    ("classification", "target"): "classification_target",
                    ("classification", "prediction"): "classification_prediction",
                    ("classification", "probability"): "class_probability",
                    ("class_probability", "target"): "classification_target",
                    ("class_probability", "prediction"): "classification_prediction",
                    ("class_probability", "probability"): "class_probability",
                }.get((group.kind, suffix))
                if role is None:
                    continue
                semantic_id = f"{group.groupId}:{suffix}:{name}"
                candidates[semantic_id] = IntentTargetSemantic(
                    semanticId=semantic_id,
                    role=role,
                    objectId=object_id,
                    column=name,
                    unit=column.unit if column else None,
                    groupId=group.groupId,
                    origin=IntentBindingOrigin.profile_exact,
                )
    for resource in profile.resourceSemantics:
        semantic_id = f"resource:{resource.objectId}:{resource.objectHash}"
        candidates[semantic_id] = IntentTargetSemantic(
            semanticId=semantic_id,
            role="resource_identity",
            objectId=resource.objectId,
            origin=IntentBindingOrigin.profile_exact,
        )
    return [candidates[key] for key in sorted(candidates)]


def _validate_profile_derived_questions(intent: AnalysisIntent, profile: DataProfile) -> None:
    resource_options = {
        option.value: option
        for option in (_resource_option(item) for item in profile.resourceSemantics)
    }
    target_options = {
        target.semanticId: ClarificationOption(
            value=target.semanticId,
            label=f"{target.column} ({target.groupId})",
            semanticId=target.semanticId,
        )
        for target in _profile_target_semantic_candidates(profile)
        if target.role in {"regression_target", "classification_target"}
    }
    for question in intent.clarification.questions:
        allowed = resource_options if question.bindsTo == "dataScope.resourceRefs" else target_options if question.bindsTo == "targetSemantics" else None
        if allowed is None or not question.options:
            raise AnalysisIntentError("Clarification binding is not supported.", code="INTENT_QUESTION_INVALID")
        for option in question.options:
            current = allowed.get(option.value)
            if current is None or current != option:
                raise AnalysisIntentError(
                    "Clarification option is not an exact current Profile candidate.",
                    code="INTENT_QUESTION_CANDIDATE_INVALID",
                )
    for ambiguity in intent.ambiguities:
        allowed = resource_options if ambiguity.field == "dataScope.resourceRefs" else target_options if ambiguity.field == "targetSemantics" else None
        if not ambiguity.blocking:
            continue
        if allowed is None or not ambiguity.candidates:
            raise AnalysisIntentError("Blocking ambiguity candidates are invalid.", code="INTENT_AMBIGUITY_INVALID")
        for candidate in ambiguity.candidates:
            current = allowed.get(candidate.value)
            if current is None or (
                current.value != candidate.value
                or current.label != candidate.label
                or current.semanticId != candidate.semanticId
            ):
                raise AnalysisIntentError(
                    "Ambiguity candidate is not an exact current Profile candidate.",
                    code="INTENT_AMBIGUITY_CANDIDATE_INVALID",
                )


def _classify_goal(goal: str) -> _Classification:
    value = goal.casefold()
    intents: list[ScientificIntent] = []
    required: list[CapabilityNeed] = []
    optional: list[CapabilityNeed] = []
    outputs: list[DesiredOutput] = [DesiredOutput.summary, DesiredOutput.warnings]
    required_kind: str | None = None
    ml_kind: str | None = None

    def add_intent(item: ScientificIntent) -> None:
        if item not in intents:
            intents.append(item)

    if _contains(value, "composition", "formula", "element distribution", "组成", "成分", "元素分布"):
        add_intent(ScientificIntent.composition_analysis)
        required.append(CapabilityNeed.composition_data)
    if _contains(value, "property", "distribution", "coverage", "性质", "属性", "分布", "覆盖"):
        add_intent(ScientificIntent.property_distribution)
        required.append(CapabilityNeed.material_property_data)
    if _contains(value, "dataset", "batch", "这批", "数据集", "materials"):
        add_intent(ScientificIntent.dataset_overview)
        required.append(CapabilityNeed.tabular_data)
    if _contains(value, "outlier", "anomal", "异常", "离群"):
        add_intent(ScientificIntent.anomaly_candidate_review)
        optional.append(CapabilityNeed.sample_identity)
        outputs.append(DesiredOutput.linked_samples)
    if _contains(value, "compare", "comparison", "对比", "比较"):
        add_intent(ScientificIntent.comparison)
        optional.append(CapabilityNeed.comparison_groups)
        outputs.append(DesiredOutput.comparison)
    if _contains(value, "embedding", "cluster", "composition space", "聚类", "嵌入", "成分空间"):
        add_intent(ScientificIntent.composition_space)
        required.extend([CapabilityNeed.tabular_data, CapabilityNeed.composition_data])
    if _contains(value, "uncertainty", "calibrat", "不确定性", "可信"):
        add_intent(ScientificIntent.ml_uncertainty_evaluation)
        required.extend([CapabilityNeed.regression_semantics, CapabilityNeed.uncertainty_semantics])
        ml_kind = "regression_uncertainty"
        outputs.append(DesiredOutput.metrics)
    if _contains(value, "regression", "prediction", "residual", "model error", "模型预测", "回归", "残差"):
        add_intent(ScientificIntent.ml_regression_evaluation)
        required.append(CapabilityNeed.regression_semantics)
        ml_kind = ml_kind or "regression"
        outputs.append(DesiredOutput.metrics)
    if _contains(value, "classification", "confusion", "roc", "precision", "分类", "混淆矩阵"):
        add_intent(ScientificIntent.ml_classification_evaluation)
        required.append(CapabilityNeed.classification_semantics)
        ml_kind = "classification"
        outputs.append(DesiredOutput.metrics)
    if ml_kind is None and _contains(
        value,
        "machine learning model",
        "ml model",
        "model performance",
        "机器学习模型",
        "模型表现",
    ):
        ml_kind = "profile_exact"
    structure_review = _contains(value, "reasonable", "reasonableness", "合理", "是否合理")
    if _contains(value, "structure", "crystal", "coordination", "晶体", "结构", "配位"):
        add_intent(ScientificIntent.structure_analysis)
        required.append(CapabilityNeed.structure_resource)
        required_kind = "structure"
        if not structure_review:
            outputs.append(DesiredOutput.three_dimensional_view)
    if _contains(value, "trajectory", "msd", "diffusion", "轨迹", "扩散"):
        add_intent(ScientificIntent.trajectory_analysis)
        required.append(CapabilityNeed.trajectory_resource)
        required_kind = "trajectory"
    if _contains(value, "phonon", "声子"):
        add_intent(ScientificIntent.phonon_analysis)
        required.append(CapabilityNeed.phonon_resource)
        required_kind = "phonon"
    if _contains(value, "brillouin", "reciprocal", "bz", "布里渊", "倒易"):
        add_intent(ScientificIntent.reciprocal_space_analysis)
        required.append(CapabilityNeed.reciprocal_space_resource)
        required_kind = "reciprocal"
    if _contains(value, "charge density", "spin density", "potential", "elf", "orbital", "volum", "电荷密度", "自旋密度", "势能", "体数据"):
        add_intent(ScientificIntent.volumetric_analysis)
        required.append(CapabilityNeed.volumetric_resource)
        required_kind = "volumetric"
        outputs.append(DesiredOutput.three_dimensional_view)
    if _contains(value, "visualize", "plot", "chart", "view", "画图", "可视化", "查看"):
        add_intent(ScientificIntent.visualization)
        outputs.append(DesiredOutput.plot)
    if _contains(value, "report", "export", "download", "报告", "导出", "下载"):
        add_intent(ScientificIntent.report_or_export)
        outputs.extend([DesiredOutput.report, DesiredOutput.downloadable_artifact, DesiredOutput.recipe])
    if intents and DesiredOutput.plot not in outputs and not structure_review:
        outputs.extend([DesiredOutput.plot, DesiredOutput.table])
    return _Classification(
        tuple(intents),
        tuple(dict.fromkeys(required)),
        tuple(dict.fromkeys(optional)),
        tuple(dict.fromkeys(outputs)),
        required_kind,
        ml_kind,
    )


def _specialize_profile_dependent_classification(
    classification: _Classification,
    profile: DataProfile,
) -> _Classification:
    if classification.ml_kind != "profile_exact":
        return classification
    group_kinds = {
        "classification" if item.kind in {"classification", "class_probability"} else item.kind
        for item in profile.semanticGroups
        if item.status == "COMPLETE"
    }
    if group_kinds == {"regression"}:
        return _Classification(
            (*classification.intents, ScientificIntent.ml_regression_evaluation),
            (*classification.required, CapabilityNeed.regression_semantics),
            classification.optional,
            (*classification.outputs, DesiredOutput.metrics),
            classification.required_resource_kind,
            "regression",
        )
    if group_kinds == {"classification"}:
        return _Classification(
            (*classification.intents, ScientificIntent.ml_classification_evaluation),
            (*classification.required, CapabilityNeed.classification_semantics),
            classification.optional,
            (*classification.outputs, DesiredOutput.metrics),
            classification.required_resource_kind,
            "classification",
        )
    return _Classification(
        classification.intents,
        classification.required,
        classification.optional,
        classification.outputs,
        classification.required_resource_kind,
        None,
    )


def _unsupported_reasons(goal: str) -> list[IntentDiagnostic]:
    value = goal.casefold()
    rules = [
        (("fermi surface", "费米面"), "INTENT_FUTURE_FERMI_SURFACE", "Fermi Surface is Future Scope.", "FUTURE_SCOPE"),
        (("bader", "rietveld", "缺陷形成能", "defect formation"), "INTENT_FUTURE_ADVANCED_SCIENCE", "The requested advanced scientific capability is Future Scope.", "FUTURE_SCOPE"),
        (("arbitrary python", "python script", "shell", "filesystem", "任意 python", "脚本", "文件系统"), "INTENT_EXECUTION_BOUNDARY", "Arbitrary code, shell, and filesystem execution are not permitted.", "EXECUTION_BOUNDARY"),
        (("run vasp", "run quantum espresso", "run dft", "hpc", "运行 vasp", "运行 dft", "高性能计算"), "INTENT_EXTERNAL_COMPUTE_UNSUPPORTED", "External scientific compute is outside the current platform boundary.", "FUTURE_SCOPE"),
        (("plugin marketplace", "multi-tenancy", "kubernetes", "插件市场", "多租户"), "INTENT_NOT_PLANNED", "The request belongs to Not Planned product scope.", "NOT_PLANNED"),
    ]
    for terms, code, message, boundary in rules:
        if any(term in value for term in terms):
            return [_diagnostic(code, "rawGoal", message, boundary=boundary)]
    return []


def _resolve_resources(
    request: AnalysisIntentRequest,
    profile: DataProfile,
    *,
    required_kind: str | None,
) -> tuple[list[IntentResourceRef], list[IntentAmbiguity], list[IntentDiagnostic], list[ClarificationQuestion]]:
    resources = list(profile.resourceSemantics)
    by_id = {item.objectId: item for item in resources}
    selected = list(dict.fromkeys([*request.constraints.includeResourceIds, *request.selected_resource_ids]))
    unknown = [value for value in selected if value not in by_id]
    if unknown:
        return [], [], [_diagnostic("RESOURCE_NOT_FOUND", "dataScope.resourceRefs", "A selected resource does not exist.", boundary="MISSING_DATA")], []
    excluded = set(request.constraints.excludeResourceIds)
    candidates = [item for item in resources if item.objectId not in excluded and _resource_matches(item.kind, item.capabilities, required_kind)]
    if selected:
        candidates = [by_id[value] for value in selected if by_id[value].objectId not in excluded]
        if required_kind and not any(_resource_matches(item.kind, item.capabilities, required_kind) for item in candidates):
            return [], [], [_diagnostic("RESOURCE_KIND_MISMATCH", "dataScope.resourceRefs", "The selected resource has the wrong scientific kind.", boundary="MISSING_DATA")], []
    if required_kind and not candidates:
        return [], [], [_diagnostic("REQUIRED_RESOURCE_MISSING", "dataScope.resourceRefs", f"No {required_kind} resource is available.", boundary="MISSING_DATA")], []
    if required_kind and len(candidates) > 1 and not selected:
        options = [_resource_option(item) for item in candidates[:32]]
        ambiguity = IntentAmbiguity(
            code="RESOURCE_SELECTION_AMBIGUOUS",
            field="dataScope.resourceRefs",
            message=f"Multiple {required_kind} resources are available.",
            candidates=[IntentCandidate(value=item.value, label=item.label, semanticId=item.semanticId) for item in options],
            blocking=True,
            source=AmbiguitySource.resource_selection,
        )
        question = ClarificationQuestion(
            questionId=f"select_{required_kind}_resource",
            code="SELECT_RESOURCE",
            prompt=f"Which {required_kind} resource should be analyzed?",
            type=ClarificationQuestionType.select_one,
            options=options,
            bindsTo="dataScope.resourceRefs",
        )
        return [], [ambiguity], [], [question]
    if not required_kind and not selected:
        # Dataset-scoped requests bind all exact table resources, never all project resources.
        candidates = [item for item in resources if _resource_matches(item.kind, item.capabilities, "table")][:ANALYSIS_INTENT_MAX_RESOURCE_REFS]
    refs = [
        IntentResourceRef(
            objectId=item.objectId,
            objectType=item.objectType,
            objectHash=item.objectHash,
            kind=item.kind,
            origin=IntentBindingOrigin.profile_exact if not selected else IntentBindingOrigin.user_explicit,
        )
        for item in candidates[:ANALYSIS_INTENT_MAX_RESOURCE_REFS]
    ]
    return refs, [], [], []


def _resolve_targets(
    request: AnalysisIntentRequest,
    profile: DataProfile,
    *,
    ml_kind: str | None,
) -> tuple[list[IntentTargetSemantic], list[IntentAmbiguity], list[IntentDiagnostic], list[ClarificationQuestion]]:
    if not ml_kind:
        return [], [], [], []
    expected_group_kind = "classification" if ml_kind == "classification" else "regression"
    groups = [group for group in profile.semanticGroups if group.kind == expected_group_kind and group.status in {"COMPLETE", "AMBIGUOUS"}]
    candidates: list[tuple[str, Any, Any]] = []
    columns = {(item.objectId, item.column): item for item in profile.semanticColumns}
    for group in groups:
        object_ids = sorted({item.objectId for item in profile.semanticColumns if any(role.groupId == group.groupId for role in item.roles)})
        object_id = object_ids[0] if object_ids else ""
        for target in group.targetColumns:
            semantic_id = f"{group.groupId}:target:{target}"
            candidates.append((semantic_id, group, columns.get((object_id, target))))
    if not candidates:
        return [], [], [_diagnostic("ML_TARGET_SEMANTICS_MISSING", "targetSemantics", "Required target/prediction semantics are unavailable.", boundary="MISSING_DATA")], []
    selected_ids = set([*request.constraints.targetIds, *request.selected_target_ids])
    selected = [item for item in candidates if item[0] in selected_ids] if selected_ids else []
    if selected_ids and len(selected) != len(selected_ids):
        return [], [], [_diagnostic("TARGET_SEMANTIC_NOT_FOUND", "targetSemantics", "A selected target semantic is stale or unavailable.", boundary="MISSING_DATA")], []
    if len(candidates) > 1 and not selected:
        options = [ClarificationOption(value=semantic_id, label=f"{target} ({group.groupId})", semanticId=semantic_id) for semantic_id, group, _ in candidates[:32] for target in [semantic_id.rsplit(":", 1)[-1]]]
        ambiguity = IntentAmbiguity(
            code="TARGET_SEMANTICS_AMBIGUOUS",
            field="targetSemantics",
            message="Multiple valid model targets are available.",
            candidates=[IntentCandidate(value=item.value, label=item.label, semanticId=item.semanticId) for item in options],
            blocking=True,
            source=AmbiguitySource.semantic_binding,
        )
        question = ClarificationQuestion(
            questionId="select_model_target",
            code="SELECT_TARGET",
            prompt="Which model target should be evaluated?",
            type=ClarificationQuestionType.select_one,
            options=options,
            bindsTo="targetSemantics",
        )
        return [], [ambiguity], [], [question]

    chosen = selected or candidates[:1]
    result: list[IntentTargetSemantic] = []
    for semantic_id, group, column_info in chosen:
        target = semantic_id.rsplit(":", 1)[-1]
        object_id = column_info.objectId if column_info else next((item.objectId for item in profile.semanticColumns if item.column == target), "")
        result.append(
            IntentTargetSemantic(
                semanticId=semantic_id,
                role="classification_target" if group.kind == "classification" else "regression_target",
                objectId=object_id,
                column=target,
                unit=column_info.unit if column_info else None,
                groupId=group.groupId,
                origin=IntentBindingOrigin.profile_exact,
            )
        )
        for prediction in group.predictionColumns:
            result.append(
                IntentTargetSemantic(
                    semanticId=f"{group.groupId}:prediction:{prediction}",
                    role="classification_prediction" if group.kind == "classification" else "regression_prediction",
                    objectId=object_id,
                    column=prediction,
                    groupId=group.groupId,
                    origin=IntentBindingOrigin.profile_exact,
                )
            )
        if ml_kind == "regression_uncertainty":
            if not group.uncertaintyColumns:
                return [], [], [_diagnostic("UNCERTAINTY_SEMANTICS_MISSING", "targetSemantics", "No uncertainty series is bound to the selected model target.", boundary="MISSING_DATA")], []
            for uncertainty in group.uncertaintyColumns:
                result.append(
                    IntentTargetSemantic(
                        semanticId=f"{group.groupId}:uncertainty:{uncertainty}",
                        role="regression_uncertainty",
                        objectId=object_id,
                        column=uncertainty,
                        groupId=group.groupId,
                        origin=IntentBindingOrigin.profile_exact,
                    )
                )
    return result, [], [], []


def _resource_matches(kind: str, capabilities: Sequence[str], required_kind: str | None) -> bool:
    if required_kind is None:
        return True
    aliases = {
        "table": {"table", "dataframe", "tabular"},
        "structure": {"structure"},
        "trajectory": {"trajectory"},
        "phonon": {"phonon"},
        "reciprocal": {"reciprocal", "brillouin_zone"},
        "volumetric": {"volumetric", "volume", "cube"},
    }
    allowed = aliases.get(required_kind, {required_kind})
    return kind.casefold() in allowed or bool({value.casefold() for value in capabilities} & allowed)


def _resource_option(item: Any) -> ClarificationOption:
    return ClarificationOption(value=item.objectId, label=f"{item.kind}: {item.objectId}", semanticId=f"resource:{item.objectId}:{item.objectHash}")


def _diagnostic(
    code: str,
    field: str,
    message: str,
    *,
    boundary: str = "CURRENT",
) -> IntentDiagnostic:
    return IntentDiagnostic(
        code=code,
        field=field,
        message=message,
        source=AmbiguitySource.user_goal if field == "rawGoal" else AmbiguitySource.semantic_binding,
        boundary=boundary,
    )


def _contains(value: str, *terms: str) -> bool:
    return any(term.casefold() in value for term in terms)


__all__ = [
    "AnalysisIntentError",
    "AnalysisIntentRequest",
    "AnalysisIntentValidator",
    "ClarificationSubmission",
    "DeterministicAnalysisIntentBuilder",
    "OpenAICompatibleAnalysisIntentBuilder",
    "build_analysis_intent_messages",
    "detect_goal_language",
    "normalize_analysis_goal",
]
