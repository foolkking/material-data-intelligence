from __future__ import annotations

from collections import Counter
from typing import Any
from typing import Mapping
from uuid import UUID

from sqlalchemy import Connection, and_, insert, select

from mdi_api.agent2_errors import ScientificResultSnapshotNotFound

from mdi_api.db import (
    research_turns,
    sessions,
    scientific_result_snapshots,
)

from mdi_api.infrastructure.persistence.agent2_common import _Repository, _optional_dict
from mdi_api.domain.scientific_results.contracts import ScientificResultItem


def _context_result_items(value: Any, project_id: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > 128:
        return []
    identities = Counter(str(item.get("id")) for item in value if isinstance(item, dict))
    items = []
    for raw in value:
        try:
            item = ScientificResultItem.model_validate(raw)
        except ValueError:
            continue
        if identities[item.id] != 1 or any(ref.project_id != project_id for ref in item.scientific_object_refs):
            continue
        items.append(item.model_dump(mode="json", include={"id", "title", "result_type", "scientific_object_refs"}))
    return items


class ScientificResultSnapshotRepository(_Repository):
    def add(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            connection.execute(insert(scientific_result_snapshots).values(**values))
            return dict(connection.execute(select(scientific_result_snapshots).where(scientific_result_snapshots.c.id == values["id"])).mappings().one())
        return self._run(run)

    def get_latest_for_turn(self, turn_id: UUID) -> dict[str, Any]:
        statement = select(scientific_result_snapshots).where(
            scientific_result_snapshots.c.research_turn_id == turn_id
        ).order_by(scientific_result_snapshots.c.created_at.desc(), scientific_result_snapshots.c.id.desc()).limit(1)
        def run(connection: Connection) -> dict[str, Any]:
            row = connection.execute(statement).mappings().first()
            if row is None:
                raise ScientificResultSnapshotNotFound(str(turn_id))
            return dict(row)
        return self._run(run)

    def get_by_identity(self, turn_id: UUID, projection_version: str, source_fingerprint: str) -> dict[str, Any] | None:
        statement = select(scientific_result_snapshots).where(and_(
            scientific_result_snapshots.c.research_turn_id == turn_id,
            scientific_result_snapshots.c.projection_version == projection_version,
            scientific_result_snapshots.c.source_fingerprint == source_fingerprint,
        ))
        return self._run(lambda connection: _optional_dict(connection.execute(statement).mappings().first()))

    def get(self, snapshot_id: UUID) -> dict[str, Any]:
        statement = select(scientific_result_snapshots).where(scientific_result_snapshots.c.id == snapshot_id)
        def run(connection: Connection) -> dict[str, Any]:
            row = connection.execute(statement).mappings().first()
            if row is None:
                raise ScientificResultSnapshotNotFound(str(snapshot_id))
            return dict(row)
        return self._run(run)

    def list_for_turn(self, turn_id: UUID) -> list[dict[str, Any]]:
        statement = select(scientific_result_snapshots).where(
            scientific_result_snapshots.c.research_turn_id == turn_id
        ).order_by(scientific_result_snapshots.c.created_at.asc(), scientific_result_snapshots.c.id.asc())
        return self._run(lambda connection: [dict(row) for row in connection.execute(statement).mappings().all()])

    def current_source_locations(self, project_id: str, snapshot_ids: list[UUID]) -> list[dict[str, Any]]:
        """Locate exact saved items without loading scientific values or artifacts."""
        if not snapshot_ids:
            return []
        newer = scientific_result_snapshots.alias("context_source_latest")
        latest_id = (
            select(newer.c.id)
            .where(newer.c.research_turn_id == scientific_result_snapshots.c.research_turn_id)
            .order_by(newer.c.created_at.desc(), newer.c.id.desc())
            .limit(1)
            .correlate(scientific_result_snapshots)
            .scalar_subquery()
        )
        statement = (
            select(
                scientific_result_snapshots.c.id.label("result_snapshot_id"),
                research_turns.c.project_id,
                research_turns.c.research_session_id,
                research_turns.c.id.label("research_turn_id"),
                scientific_result_snapshots.c.bundle_json["project_id"].label("_bundle_project_id"),
                scientific_result_snapshots.c.bundle_json["research_turn_id"].label("_bundle_turn_id"),
                scientific_result_snapshots.c.bundle_json["result_items"].label("_result_items"),
            )
            .select_from(scientific_result_snapshots.join(
                research_turns, scientific_result_snapshots.c.research_turn_id == research_turns.c.id,
            ).join(sessions, research_turns.c.research_session_id == sessions.c.id))
            .where(
                scientific_result_snapshots.c.id.in_(snapshot_ids),
                scientific_result_snapshots.c.project_id == project_id,
                research_turns.c.project_id == project_id,
                sessions.c.project_id == project_id,
                # Turn pages read the latest saved snapshot. Do not send an
                # older citation to a different projection of that result.
                scientific_result_snapshots.c.id == latest_id,
            )
            .order_by(scientific_result_snapshots.c.id)
        )
        def run(connection: Connection) -> list[dict[str, Any]]:
            locations = []
            for row in connection.execute(statement).mappings():
                location = dict(row)
                bundle_project = location.pop("_bundle_project_id")
                bundle_turn = location.pop("_bundle_turn_id")
                raw_items = location.pop("_result_items")
                items = _context_result_items(raw_items, project_id) if (
                    bundle_project == project_id and bundle_turn == str(location["research_turn_id"])
                ) else []
                if items:
                    location["result_items"] = items
                locations.append(location)
            return locations
        return self._run(run)

    def exists_for_turn(self, turn_id: UUID) -> bool:
        statement = select(scientific_result_snapshots.c.id).where(scientific_result_snapshots.c.research_turn_id == turn_id).limit(1)
        return self._run(lambda connection: connection.execute(statement).first() is not None)

    def list_recent_for_session(
        self,
        session_id: str,
        *,
        before_sequence: int,
        limit: int = 6,
    ) -> list[dict[str, Any]]:
        statement = (
            select(scientific_result_snapshots, research_turns.c.sequence_no)
            .join(research_turns, scientific_result_snapshots.c.research_turn_id == research_turns.c.id)
            .where(and_(
                research_turns.c.research_session_id == session_id,
                research_turns.c.sequence_no < before_sequence,
            ))
            .order_by(research_turns.c.sequence_no.desc(), scientific_result_snapshots.c.created_at.desc())
            .limit(limit)
        )
        return self._run(lambda connection: [dict(row) for row in connection.execute(statement).mappings().all()])


__all__ = ['ScientificResultSnapshotRepository']
