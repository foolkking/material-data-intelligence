"""Application persistence contract for scientific interpretation records."""

from __future__ import annotations

from typing import Any, ContextManager, Mapping, Protocol

from mdi_schemas import GroundedScientificInterpretation, InterpretationExecutionRecord, ScientificEvidenceBundle


class ScientificInterpretationRepository(Protocol):
    def idempotency_guard(self, job_id: str, mode: str, idempotency_key_hash: str) -> ContextManager[None]:
        ...

    def save_bundle(self, bundle: ScientificEvidenceBundle | Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get_bundle(self, bundle_id: str) -> dict[str, Any]:
        ...

    def save_interpretation(
        self,
        bundle: ScientificEvidenceBundle | Mapping[str, Any],
        interpretation: GroundedScientificInterpretation | Mapping[str, Any],
        execution: InterpretationExecutionRecord | Mapping[str, Any],
    ) -> dict[str, Any]:
        ...

    def get_interpretation(self, interpretation_id: str) -> dict[str, Any]:
        ...

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        ...

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        ...


__all__ = ["ScientificInterpretationRepository"]
