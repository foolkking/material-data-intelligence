from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from mdi_api.application.interpretation.grounding import (
    HISTORICAL_GROUNDING_NOTICE,
    project_grounded_communication,
    validate_interpretation,
)
from mdi_api.application.interpretation.projector import AssistantResponseProjector
from mdi_api.db import agent2_scientific_interpretations, scientific_result_snapshots
from mdi_api.domain.interpretation.contracts import ScientificInterpretationOutput
from mdi_api.domain.scientific_results.contracts import ScientificResultBundle


SCIENTIFIC_MESSAGE_UNAVAILABLE = (
    "暂时无法核验这份解读的科学依据。已保存的分析结果仍可查看；可重新读取或重新解读。"
)


def scientific_message_projections(
    message_rows: Sequence[Mapping[str, Any]],
    connection: Any,
    *,
    project_id: str,
) -> dict[str, str]:
    """Share one grounded Markdown read model across session and SSE responses.

    Stored messages, interpretations and results are never rewritten. Two
    batched reads preserve the recorded interpretation/snapshot binding; a
    missing or invalid binding must not fall back to historical raw prose.
    """
    projected: dict[str, str] = {}
    by_interpretation: dict[UUID, list[tuple[str, UUID, UUID | None]]] = {}
    for row in message_rows:
        payload = row.get("payload_json") or {}
        if not isinstance(payload, dict) or (
            row.get("role") != "agent"
            or payload.get("messageKind") != "ASSISTANT_FINAL"
            or payload.get("source") != "agent2_scientific_interpreter"
        ):
            continue
        message_id = str(row["id"])
        projected[message_id] = SCIENTIFIC_MESSAGE_UNAVAILABLE
        try:
            interpretation_id = UUID(str(payload.get("interpretationId")))
            turn_id = UUID(str(payload.get("turnId")))
            snapshot_id = (
                UUID(str(payload["sourceResultSnapshotId"]))
                if "sourceResultSnapshotId" in payload else None
            )
        except (TypeError, ValueError):
            continue
        by_interpretation.setdefault(interpretation_id, []).append(
            (message_id, turn_id, snapshot_id)
        )
    if not by_interpretation:
        return projected
    try:
        interpretations = connection.execute(
            select(agent2_scientific_interpretations).where(
                agent2_scientific_interpretations.c.id.in_(by_interpretation),
                agent2_scientific_interpretations.c.project_id == project_id,
            )
        ).mappings().all()
        snapshots = connection.execute(
            select(scientific_result_snapshots).where(
                scientific_result_snapshots.c.id.in_(
                    [row["result_snapshot_id"] for row in interpretations]
                ),
                scientific_result_snapshots.c.project_id == project_id,
            )
        ).mappings().all()
    except SQLAlchemyError:
        return projected

    snapshots_by_id = {row["id"]: row for row in snapshots}
    projector = AssistantResponseProjector()
    for row in interpretations:
        snapshot = snapshots_by_id.get(row["result_snapshot_id"])
        if (
            snapshot is None
            or str(row["project_id"]) != project_id
            or str(snapshot["project_id"]) != project_id
            or row.get("grounding_status") != "VALID"
        ):
            continue
        try:
            bundle = ScientificResultBundle.model_validate(snapshot["bundle_json"])
            if bundle.project_id != project_id:
                continue
            output = row["output_json"]
            raw = output.get("interpretation") if isinstance(output, dict) else None
            interpretation = project_grounded_communication(
                ScientificInterpretationOutput.model_validate(raw), bundle,
            )
            content = (
                projector.project(
                    interpretation, bundle,
                    effective_relevance=bundle.relevance_status.value, markdown=True,
                )
                if validate_interpretation(interpretation, bundle).valid
                else HISTORICAL_GROUNDING_NOTICE
            )
        except (TypeError, ValueError):
            continue
        for message_id, turn_id, snapshot_id in by_interpretation.get(row["id"], []):
            if turn_id != row.get("research_turn_id"):
                continue
            if snapshot_id is not None and snapshot_id != snapshot["id"]:
                continue
            projected[message_id] = content
    return projected
