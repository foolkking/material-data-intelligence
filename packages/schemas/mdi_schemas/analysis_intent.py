from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ANALYSIS_INTENT_SCHEMA_VERSION = "1.0"
ANALYSIS_INTENT_MAX_RAW_GOAL_CHARS = 16_384
ANALYSIS_INTENT_MAX_RESOURCE_REFS = 32
ANALYSIS_INTENT_MAX_SCIENTIFIC_INTENTS = 16
ANALYSIS_INTENT_MAX_TARGET_SEMANTICS = 32
ANALYSIS_INTENT_MAX_DESIRED_OUTPUTS = 32
ANALYSIS_INTENT_MAX_AMBIGUITIES = 32
ANALYSIS_INTENT_MAX_QUESTIONS = 3
ANALYSIS_INTENT_MAX_CLARIFICATION_ROUNDS = 1
ANALYSIS_INTENT_MAX_SERIALIZED_BYTES = 262_144
ANALYSIS_INTENT_MAX_JSON_DEPTH = 12
ANALYSIS_INTENT_MAX_DIAGNOSTICS = 32


class StrictIntentModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AnalysisIntentOutcome(str, Enum):
    ready = "READY"
    needs_clarification = "NEEDS_CLARIFICATION"
    unsupported = "UNSUPPORTED"


class ScientificIntent(str, Enum):
    dataset_overview = "dataset_overview"
    composition_analysis = "composition_analysis"
    property_distribution = "property_distribution"
    dataset_comparison = "dataset_comparison"
    composition_space = "composition_space"
    structure_analysis = "structure_analysis"
    trajectory_analysis = "trajectory_analysis"
    phonon_analysis = "phonon_analysis"
    reciprocal_space_analysis = "reciprocal_space_analysis"
    volumetric_analysis = "volumetric_analysis"
    ml_regression_evaluation = "ml_regression_evaluation"
    ml_uncertainty_evaluation = "ml_uncertainty_evaluation"
    ml_classification_evaluation = "ml_classification_evaluation"
    sample_inspection = "sample_inspection"
    comparison = "comparison"
    anomaly_candidate_review = "anomaly_candidate_review"
    visualization = "visualization"
    report_or_export = "report_or_export"


class DesiredOutput(str, Enum):
    summary = "summary"
    metrics = "metrics"
    plot = "plot"
    table = "table"
    linked_samples = "linked_samples"
    three_dimensional_view = "three_dimensional_view"
    comparison = "comparison"
    warnings = "warnings"
    recipe = "recipe"
    report = "report"
    downloadable_artifact = "downloadable_artifact"


class CapabilityNeed(str, Enum):
    tabular_data = "tabular_data"
    composition_data = "composition_data"
    material_property_data = "material_property_data"
    comparison_groups = "comparison_groups"
    structure_resource = "structure_resource"
    trajectory_resource = "trajectory_resource"
    phonon_resource = "phonon_resource"
    reciprocal_space_resource = "reciprocal_space_resource"
    volumetric_resource = "volumetric_resource"
    regression_semantics = "regression_semantics"
    uncertainty_semantics = "uncertainty_semantics"
    classification_semantics = "classification_semantics"
    sample_identity = "sample_identity"


class IntentBindingOrigin(str, Enum):
    user_explicit = "USER_EXPLICIT"
    profile_exact = "PROFILE_EXACT"
    clarification_answer = "CLARIFICATION_ANSWER"


class AmbiguitySource(str, Enum):
    user_goal = "USER_GOAL"
    data_profile = "DATA_PROFILE"
    resource_selection = "RESOURCE_SELECTION"
    semantic_binding = "SEMANTIC_BINDING"


class ClarificationQuestionType(str, Enum):
    select_one = "SELECT_ONE"
    select_many = "SELECT_MANY"
    confirm = "CONFIRM"


class IntentResourceRef(StrictIntentModel):
    objectId: str = Field(min_length=1, max_length=128)
    objectType: str = Field(min_length=1, max_length=96)
    objectHash: str = Field(min_length=1, max_length=128)
    kind: str = Field(min_length=1, max_length=96)
    origin: IntentBindingOrigin


class IntentDataScope(StrictIntentModel):
    datasetId: str = Field(min_length=1, max_length=64)
    datasetVersion: str = Field(min_length=1, max_length=64)
    profileId: str = Field(min_length=1, max_length=64)
    profileContractVersion: str = Field(min_length=1, max_length=32)
    profileSemanticHash: str = Field(min_length=1, max_length=128)
    resourceRefs: list[IntentResourceRef] = Field(default_factory=list, max_length=ANALYSIS_INTENT_MAX_RESOURCE_REFS)
    sampleIds: list[str] = Field(default_factory=list, max_length=32)
    groupIds: list[str] = Field(default_factory=list, max_length=32)
    modelIds: list[str] = Field(default_factory=list, max_length=32)
    origin: IntentBindingOrigin


class IntentTargetSemantic(StrictIntentModel):
    semanticId: str = Field(min_length=1, max_length=160)
    role: Literal[
        "material_property",
        "regression_target",
        "regression_prediction",
        "regression_uncertainty",
        "classification_target",
        "classification_prediction",
        "class_probability",
        "model_identity",
        "resource_identity",
        "comparison_group",
    ]
    objectId: str = Field(min_length=1, max_length=128)
    column: str | None = Field(default=None, max_length=256)
    unit: str | None = Field(default=None, max_length=64)
    groupId: str | None = Field(default=None, max_length=128)
    seriesId: str | None = Field(default=None, max_length=128)
    origin: IntentBindingOrigin


class AnalysisIntentConstraints(StrictIntentModel):
    includeResourceIds: list[str] = Field(default_factory=list, max_length=32)
    excludeResourceIds: list[str] = Field(default_factory=list, max_length=32)
    includeScientificIntents: list[ScientificIntent] = Field(default_factory=list, max_length=16)
    excludeScientificIntents: list[ScientificIntent] = Field(default_factory=list, max_length=16)
    targetIds: list[str] = Field(default_factory=list, max_length=32)
    modelIds: list[str] = Field(default_factory=list, max_length=32)
    groupIds: list[str] = Field(default_factory=list, max_length=32)
    outputPreferences: list[DesiredOutput] = Field(default_factory=list, max_length=32)
    maxAnalyses: int | None = Field(default=None, ge=1, le=16)
    maxToolCalls: int | None = Field(default=None, ge=1, le=16)
    timePreference: Literal["FAST", "BALANCED", "THOROUGH"] | None = None
    costPreference: Literal["LOW", "BALANCED"] | None = None
    clarificationAllowed: bool = True
    descriptiveOnly: bool = False
    forbidDerivedInterpretation: bool = False


class IntentCandidate(StrictIntentModel):
    value: str = Field(min_length=1, max_length=256)
    label: str = Field(min_length=1, max_length=256)
    semanticId: str = Field(min_length=1, max_length=160)


class IntentAmbiguity(StrictIntentModel):
    code: str = Field(min_length=1, max_length=96)
    field: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=512)
    candidates: list[IntentCandidate] = Field(default_factory=list, max_length=32)
    blocking: bool
    source: AmbiguitySource


class IntentDiagnostic(StrictIntentModel):
    code: str = Field(min_length=1, max_length=96)
    field: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=512)
    source: AmbiguitySource
    boundary: Literal["CURRENT", "FUTURE_SCOPE", "NOT_PLANNED", "EXECUTION_BOUNDARY", "MISSING_DATA"] = "CURRENT"


class ClarificationOption(StrictIntentModel):
    value: str = Field(min_length=1, max_length=256)
    label: str = Field(min_length=1, max_length=256)
    semanticId: str = Field(min_length=1, max_length=160)


class ClarificationQuestion(StrictIntentModel):
    questionId: str = Field(min_length=1, max_length=96)
    code: str = Field(min_length=1, max_length=96)
    prompt: str = Field(min_length=1, max_length=512)
    type: ClarificationQuestionType
    options: list[ClarificationOption] = Field(min_length=1, max_length=32)
    required: bool = True
    bindsTo: str = Field(min_length=1, max_length=128)


class ClarificationAnswer(StrictIntentModel):
    questionId: str = Field(min_length=1, max_length=96)
    selectedValues: list[str] = Field(min_length=1, max_length=32)


class AnalysisIntentClarification(StrictIntentModel):
    round: int = Field(default=0, ge=0, le=ANALYSIS_INTENT_MAX_CLARIFICATION_ROUNDS)
    maxRounds: Literal[1] = 1
    maxQuestionsPerRound: Literal[3] = 3
    questions: list[ClarificationQuestion] = Field(default_factory=list, max_length=ANALYSIS_INTENT_MAX_QUESTIONS)
    answers: list[ClarificationAnswer] = Field(default_factory=list, max_length=ANALYSIS_INTENT_MAX_QUESTIONS)


class IntentAnswerProvenance(StrictIntentModel):
    questionId: str = Field(min_length=1, max_length=96)
    selectedValues: list[str] = Field(min_length=1, max_length=32)


class AnalysisIntentProvenance(StrictIntentModel):
    provider: Literal["deterministic_mock", "openai_compatible"]
    model: str = Field(min_length=1, max_length=128)
    promptVersion: str = Field(min_length=1, max_length=64)
    createdAt: str = Field(min_length=1, max_length=64)
    parentIntentId: str | None = Field(default=None, max_length=96)
    answerBindings: list[IntentAnswerProvenance] = Field(default_factory=list, max_length=ANALYSIS_INTENT_MAX_QUESTIONS)


class AnalysisIntent(StrictIntentModel):
    schemaVersion: Literal["1.0"] = ANALYSIS_INTENT_SCHEMA_VERSION
    intentId: str = Field(min_length=1, max_length=96)
    intentHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    datasetId: str = Field(min_length=1, max_length=64)
    profileId: str = Field(min_length=1, max_length=64)
    rawGoal: str = Field(min_length=1, max_length=ANALYSIS_INTENT_MAX_RAW_GOAL_CHARS)
    normalizedGoal: str = Field(min_length=1, max_length=ANALYSIS_INTENT_MAX_RAW_GOAL_CHARS)
    language: Literal["zh", "en", "mixed", "und"]
    dataScope: IntentDataScope
    scientificIntents: list[ScientificIntent] = Field(default_factory=list, max_length=ANALYSIS_INTENT_MAX_SCIENTIFIC_INTENTS)
    targetSemantics: list[IntentTargetSemantic] = Field(default_factory=list, max_length=ANALYSIS_INTENT_MAX_TARGET_SEMANTICS)
    desiredOutputs: list[DesiredOutput] = Field(default_factory=list, max_length=ANALYSIS_INTENT_MAX_DESIRED_OUTPUTS)
    constraints: AnalysisIntentConstraints = Field(default_factory=AnalysisIntentConstraints)
    requiredCapabilityNeeds: list[CapabilityNeed] = Field(default_factory=list, max_length=16)
    optionalCapabilityNeeds: list[CapabilityNeed] = Field(default_factory=list, max_length=16)
    ambiguities: list[IntentAmbiguity] = Field(default_factory=list, max_length=ANALYSIS_INTENT_MAX_AMBIGUITIES)
    missingFacts: list[IntentDiagnostic] = Field(default_factory=list, max_length=ANALYSIS_INTENT_MAX_DIAGNOSTICS)
    unsupportedReasons: list[IntentDiagnostic] = Field(default_factory=list, max_length=ANALYSIS_INTENT_MAX_DIAGNOSTICS)
    outcome: AnalysisIntentOutcome
    clarification: AnalysisIntentClarification = Field(default_factory=AnalysisIntentClarification)
    provenance: AnalysisIntentProvenance
    warnings: list[IntentDiagnostic] = Field(default_factory=list, max_length=ANALYSIS_INTENT_MAX_DIAGNOSTICS)

    @model_validator(mode="after")
    def validate_outcome_consistency(self) -> "AnalysisIntent":
        blocking = [item for item in self.ambiguities if item.blocking]
        if self.datasetId != self.dataScope.datasetId or self.profileId != self.dataScope.profileId:
            raise ValueError("Intent top-level identity must match dataScope identity.")
        unique_fields = {
            "dataScope.resourceRefs": [item.objectId for item in self.dataScope.resourceRefs],
            "scientificIntents": [item.value for item in self.scientificIntents],
            "targetSemantics": [item.semanticId for item in self.targetSemantics],
            "desiredOutputs": [item.value for item in self.desiredOutputs],
            "requiredCapabilityNeeds": [item.value for item in self.requiredCapabilityNeeds],
            "optionalCapabilityNeeds": [item.value for item in self.optionalCapabilityNeeds],
        }
        for field_name, values in unique_fields.items():
            if len(values) != len(set(values)):
                raise ValueError(f"{field_name} identities must be unique.")
        if self.clarification.round == 0:
            if self.provenance.parentIntentId is not None or self.clarification.answers or self.provenance.answerBindings:
                raise ValueError("Initial Intent cannot contain clarification parent or answer provenance.")
        else:
            if self.provenance.parentIntentId is None:
                raise ValueError("Clarification revision requires a parent Intent identity.")
            if [item.model_dump(mode="json") for item in self.clarification.answers] != [
                item.model_dump(mode="json") for item in self.provenance.answerBindings
            ]:
                raise ValueError("Clarification answers and provenance bindings must match exactly.")
        if self.outcome is AnalysisIntentOutcome.ready:
            if not self.scientificIntents:
                raise ValueError("READY intent requires at least one recognized scientific intent.")
            if blocking or self.missingFacts or self.unsupportedReasons or self.clarification.questions:
                raise ValueError("READY intent cannot contain blocking ambiguity, missing facts, unsupported reasons, or questions.")
        elif self.outcome is AnalysisIntentOutcome.needs_clarification:
            if not self.scientificIntents:
                raise ValueError("NEEDS_CLARIFICATION requires at least one recognized scientific intent.")
            if not blocking or not self.clarification.questions or self.unsupportedReasons:
                raise ValueError("NEEDS_CLARIFICATION requires blocking ambiguity and questions without unsupported reasons.")
            if not self.constraints.clarificationAllowed:
                raise ValueError("Clarification questions are forbidden by the intent constraints.")
            if self.clarification.round >= self.clarification.maxRounds:
                raise ValueError("Clarification limit has already been reached.")
        elif not self.unsupportedReasons:
            raise ValueError("UNSUPPORTED intent requires at least one typed reason.")
        if len({question.questionId for question in self.clarification.questions}) != len(self.clarification.questions):
            raise ValueError("Clarification question IDs must be unique.")
        return self


def canonical_analysis_intent_payload(intent: AnalysisIntent | dict[str, Any]) -> dict[str, Any]:
    payload = intent.model_dump(mode="json") if isinstance(intent, AnalysisIntent) else json.loads(json.dumps(intent))
    payload.pop("intentId", None)
    payload.pop("intentHash", None)
    provenance = payload.get("provenance")
    if isinstance(provenance, dict):
        provenance.pop("createdAt", None)
    return payload


def canonical_analysis_intent_json(intent: AnalysisIntent | dict[str, Any]) -> str:
    return json.dumps(canonical_analysis_intent_payload(intent), ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def compute_analysis_intent_hash(intent: AnalysisIntent | dict[str, Any]) -> str:
    return hashlib.sha256(canonical_analysis_intent_json(intent).encode("utf-8")).hexdigest()


def deterministic_intent_id(intent_hash: str) -> str:
    if len(intent_hash) != 64 or any(char not in "0123456789abcdef" for char in intent_hash):
        raise ValueError("Intent hash must be lowercase SHA-256 hex.")
    return f"intent_{intent_hash[:24]}"


def validate_intent_json_bounds(value: Any) -> None:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    if len(encoded) > ANALYSIS_INTENT_MAX_SERIALIZED_BYTES:
        raise ValueError("AnalysisIntent exceeds the serialized byte cap.")

    def visit(node: Any, depth: int) -> None:
        if depth > ANALYSIS_INTENT_MAX_JSON_DEPTH:
            raise ValueError("AnalysisIntent exceeds the JSON nesting cap.")
        if isinstance(node, dict):
            for child in node.values():
                visit(child, depth + 1)
        elif isinstance(node, list):
            for child in node:
                visit(child, depth + 1)

    visit(value, 1)
