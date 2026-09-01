from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

from mdi_api.research_agent.evaluation.runner import AgentEvaluationRunner, EvaluationResult
from mdi_api.research_agent.evaluation.schemas import (
    AgentEvalCase,
    AgentEvalCategory,
    AgentEvalExpectation,
    EvalObjectCandidate,
    EvalResultCandidate,
    ExpectedToolPolicy,
)
from mdi_api.research_agent.orchestration.schemas import ResearchTurnDecision


QUALITY_CORPUS_CONTRACT_VERSION = "phase14r.agent-quality-evaluation/1.0"
_FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "phase14r_quality_v1.json"
_REPOSITORY_ROOT = Path(__file__).resolve().parents[5]


class QualityEvaluationMode(StrEnum):
    ORCHESTRATOR = "ORCHESTRATOR"
    PRODUCT_CONTRACT = "PRODUCT_CONTRACT"


class QualityEvaluationCase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str = Field(pattern=r"^R10-[0-9]{3}$")
    family: str = Field(min_length=1, max_length=64)
    scenario: str = Field(min_length=1, max_length=96)
    mode: QualityEvaluationMode
    category: AgentEvalCategory
    message: str = Field(min_length=1, max_length=4000)
    paraphrases: list[str] = Field(default_factory=list, max_length=8)
    object_candidates: list[EvalObjectCandidate] = Field(default_factory=list)
    result_candidates: list[EvalResultCandidate] = Field(default_factory=list)
    expected: AgentEvalExpectation | None = None
    tool_policy: ExpectedToolPolicy = ExpectedToolPolicy.NOT_APPLICABLE
    invariants: list[str] = Field(default_factory=list, max_length=16)
    evidence_tests: list[str] = Field(min_length=1, max_length=16)
    evaluation_dimensions: list[str] = Field(min_length=1, max_length=16)

    @model_validator(mode="after")
    def validate_mode_contract(self) -> "QualityEvaluationCase":
        if len(set(self.paraphrases)) != len(self.paraphrases):
            raise ValueError("paraphrases must be unique")
        if self.mode == QualityEvaluationMode.ORCHESTRATOR:
            if self.expected is None:
                raise ValueError("orchestrator cases require an expected decision")
            if self.expected.action is None and not self.expected.deterministic_clarification:
                raise ValueError("orchestrator cases require an action or deterministic clarification")
        elif not self.invariants:
            raise ValueError("product-contract cases require explicit invariants")
        return self


class QualityEvaluationCorpus(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_version: Literal["phase14r.agent-quality-evaluation/1.0"] = (
        QUALITY_CORPUS_CONTRACT_VERSION
    )
    corpus_id: Literal["phase14r-r10-v1"]
    cases: list[QualityEvaluationCase] = Field(min_length=24, max_length=64)

    @model_validator(mode="after")
    def validate_case_identity(self) -> "QualityEvaluationCorpus":
        case_ids = [case.case_id for case in self.cases]
        if len(case_ids) != len(set(case_ids)):
            raise ValueError("quality evaluation case ids must be unique")
        return self


class QualityCaseResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str
    passed: bool
    mode: QualityEvaluationMode
    action: str | None = None
    detail: str


def load_phase14r_quality_corpus() -> QualityEvaluationCorpus:
    payload = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    return TypeAdapter(QualityEvaluationCorpus).validate_python(payload)


class QualityEvaluationRunner:
    """Deterministic R10 evaluator; provider calls remain an optional supplement."""

    def __init__(self, agent_runner: AgentEvaluationRunner) -> None:
        self.agent_runner = agent_runner

    def evaluate(self, case: QualityEvaluationCase) -> QualityCaseResult:
        if case.mode == QualityEvaluationMode.PRODUCT_CONTRACT:
            missing = [
                node
                for node in case.evidence_tests
                if not self._evidence_test_exists(node)
            ]
            return QualityCaseResult(
                case_id=case.case_id,
                passed=not missing,
                mode=case.mode,
                detail=(
                    "linked deterministic product-contract evidence"
                    if not missing
                    else f"missing evidence tests: {missing}"
                ),
            )
        fixture = self._agent_fixture(case)
        result = self.agent_runner.evaluate_fixture(fixture)
        return QualityCaseResult(
            case_id=case.case_id,
            passed=result.passed,
            mode=case.mode,
            action=result.action,
            detail=result.detail,
        )

    async def evaluate_live(
        self,
        case: QualityEvaluationCase,
        client: Any,
        *,
        timeout_seconds: float = 60.0,
    ) -> EvaluationResult:
        if case.mode != QualityEvaluationMode.ORCHESTRATOR:
            raise ValueError("live provider evaluation is only valid for orchestrator cases")
        return await self.agent_runner.evaluate_live(
            self._agent_fixture(case),
            client,
            timeout_seconds=timeout_seconds,
        )

    def _agent_fixture(self, case: QualityEvaluationCase) -> AgentEvalCase:
        expected = case.expected
        if expected is None:
            raise ValueError("orchestrator case is missing its expectation")
        decision: dict[str, Any] | None = None
        if not expected.deterministic_clarification:
            action = expected.action
            if action is None:
                raise ValueError("orchestrator case is missing its action")
            subject_keys = expected.selected_scope_ref_keys[:]
            requirements = [
                {
                    "requirement_id": requirement_id,
                    "criticality": "REQUIRED",
                    "subject_ref_keys": subject_keys,
                    "constraints": (
                        expected.constraint_subset if index == 0 else {}
                    ),
                }
                for index, requirement_id in enumerate(expected.requirement_ids)
            ]
            decision = ResearchTurnDecision(
                contract_version="1.0",
                action=action,
                assistant_message="Bounded deterministic quality-evaluation decision.",
                research_objective=(
                    case.message if requirements else None
                ),
                selected_scope_ref_keys=expected.selected_scope_ref_keys,
                scientific_requirements=requirements,
                reusable_result_ref_keys=expected.reusable_result_ref_keys,
                clarification=None,
                confidence="HIGH",
            ).model_dump(mode="json")
        return AgentEvalCase(
            case_id=case.case_id,
            category=case.category,
            message=case.message,
            paraphrases=case.paraphrases or [
                f"{case.message}（改写一）",
                f"{case.message}（改写二）",
                f"{case.message}（改写三）",
            ],
            object_candidates=case.object_candidates,
            result_candidates=case.result_candidates,
            provider_decision=decision,
            expected=expected,
            tool_policy=case.tool_policy,
        )

    @staticmethod
    def _evidence_test_exists(node_id: str) -> bool:
        path_text, separator, test_name = node_id.partition("::")
        if not separator or not test_name.startswith("test_"):
            return False
        path = (_REPOSITORY_ROOT / path_text).resolve()
        try:
            path.relative_to(_REPOSITORY_ROOT)
        except ValueError:
            return False
        if not path.is_file():
            return False
        return f"def {test_name}(" in path.read_text(encoding="utf-8")


__all__ = [
    "QUALITY_CORPUS_CONTRACT_VERSION",
    "QualityCaseResult",
    "QualityEvaluationCase",
    "QualityEvaluationCorpus",
    "QualityEvaluationMode",
    "QualityEvaluationRunner",
    "load_phase14r_quality_corpus",
]
