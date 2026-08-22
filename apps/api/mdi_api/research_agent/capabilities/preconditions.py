from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from mdi_api.agent2_errors import RegistryValidationError
from mdi_api.research_agent.schemas import CapabilityManifest, CapabilityPrecondition


@dataclass(frozen=True)
class PreconditionEvaluation:
    passed: bool
    reason_code: str
    detail: str = ""


class CapabilityPreconditionEvaluator(Protocol):
    def evaluate(self, *, manifest: CapabilityManifest, precondition: CapabilityPrecondition, bindings: dict[str, Any], context: Any) -> PreconditionEvaluation: ...


class CapabilityPreconditionRegistry:
    def __init__(self) -> None:
        self._evaluators: dict[str, CapabilityPreconditionEvaluator] = {}

    def register(self, predicate_id: str, evaluator: CapabilityPreconditionEvaluator) -> None:
        if predicate_id in self._evaluators:
            raise RegistryValidationError(f"Duplicate precondition predicate: {predicate_id}")
        self._evaluators[predicate_id] = evaluator

    def require(self, predicate_id: str) -> CapabilityPreconditionEvaluator:
        try:
            return self._evaluators[predicate_id]
        except KeyError as exc:
            raise RegistryValidationError(f"Unknown precondition predicate: {predicate_id}") from exc

    def contains(self, predicate_id: str) -> bool:
        return predicate_id in self._evaluators


class _SimpleEvaluator:
    def __init__(self, predicate_id: str) -> None:
        self.predicate_id = predicate_id

    def evaluate(self, *, manifest: CapabilityManifest, precondition: CapabilityPrecondition, bindings: dict[str, Any], context: Any) -> PreconditionEvaluation:
        if self.predicate_id == "object.available":
            refs = bindings.get(precondition.input_slot or "", [])
            passed = bool(refs) and all(not getattr(ref, "object_type", "").startswith("invalid") for ref in refs)
            return PreconditionEvaluation(passed, "OBJECT_AVAILABLE" if passed else "OBJECT_UNAVAILABLE")
        if self.predicate_id == "object.metadata_present":
            refs = bindings.get(precondition.input_slot or "", [])
            passed = bool(refs)
            return PreconditionEvaluation(passed, "METADATA_PRESENT" if passed else "METADATA_MISSING")
        if self.predicate_id in {"object.semantic_flag", "object.relationship_exists", "result.available", "result.current_or_stale_allowed"}:
            passed = bool(bindings.get(precondition.input_slot or "", []))
            return PreconditionEvaluation(passed, "PREDICATE_PASS" if passed else "PREDICATE_FAIL")
        return PreconditionEvaluation(False, "UNKNOWN_PREDICATE")


def build_default_precondition_registry() -> CapabilityPreconditionRegistry:
    registry = CapabilityPreconditionRegistry()
    for predicate_id in (
        "object.available", "object.metadata_present", "object.semantic_flag",
        "object.relationship_exists", "result.available", "result.current_or_stale_allowed",
    ):
        registry.register(predicate_id, _SimpleEvaluator(predicate_id))
    return registry
