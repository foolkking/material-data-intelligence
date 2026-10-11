from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from mdi_api.domain.scientific_results.contracts import ScientificResultBundle


@dataclass(frozen=True)
class ScientificResultProjectionContext:
    project_id: str
    research_session_id: str
    research_turn_id: str
    research_question: str
    execution_summary: dict[str, Any]
    capability_plan: dict[str, Any]
    analysis_plan: dict[str, Any]
    tool_calls: tuple[dict[str, Any], ...]
    artifacts: tuple[dict[str, Any], ...]
    artifact_payloads: dict[str, Any] = field(default_factory=dict)
    source_object_refs: tuple[Any, ...] = ()
    scientific_selections: tuple[dict[str, Any], ...] = ()
    projector_ids: tuple[str, ...] = ()
    projection_scope_key: str = ""
    # Verified row identities; keep them separate from immutable fingerprint inputs.
    analysis_plan_id: str | None = None
    capability_plan_id: str | None = None


@dataclass(frozen=True)
class ScientificResultProjection:
    bundle: ScientificResultBundle
    projector_id: str
    projector_version: str


class ScientificResultProjector(Protocol):
    projector_id: str
    version: str

    def project(self, context: ScientificResultProjectionContext) -> ScientificResultProjection: ...
