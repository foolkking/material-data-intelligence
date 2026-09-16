from __future__ import annotations

from typing import Any, Mapping
from uuid import UUID

from sqlalchemy import Connection, and_, insert, select, update

from mdi_api.db import (
    literature_evidence,
    literature_searches,
    literature_snapshots,
    literature_works,
)
from mdi_api.infrastructure.persistence.agent2_common import _Repository


class ScientificKnowledgeRepository(_Repository):
    """Scholarly identity/snapshot persistence; no scientific computation."""

    def save_candidate(self, candidate: Mapping[str, Any]) -> dict[str, Any]:
        work = candidate["work"]
        snapshots = candidate.get("snapshots") or []

        def run(connection: Connection) -> dict[str, Any]:
            existing = connection.execute(
                select(literature_works).where(
                    literature_works.c.canonical_key == work["canonical_key"]
                )
            ).mappings().first()
            if existing is None:
                work_id = work["work_id"]
                connection.execute(
                    insert(literature_works).values(
                        id=work_id,
                        candidate_id=work["candidate_id"],
                        canonical_key=work["canonical_key"],
                        doi=work.get("doi"),
                        arxiv_id=work.get("arxiv_id"),
                        arxiv_version=work.get("arxiv_version"),
                        relations_json=work.get("relations") or [],
                    )
                )
            else:
                work_id = existing["id"]
                connection.execute(
                    update(literature_works)
                    .where(literature_works.c.id == work_id)
                    .values(
                        doi=work.get("doi"),
                        arxiv_id=work.get("arxiv_id"),
                        arxiv_version=work.get("arxiv_version"),
                        relations_json=work.get("relations") or [],
                    )
                )
            for snapshot in snapshots:
                duplicate = connection.execute(
                    select(literature_snapshots.c.id).where(
                        and_(
                            literature_snapshots.c.provider
                            == snapshot["provider"],
                            literature_snapshots.c.provider_record_id
                            == snapshot["provider_record_id"],
                            literature_snapshots.c.raw_metadata_hash
                            == snapshot["raw_metadata_hash"],
                        )
                    )
                ).first()
                if duplicate is not None:
                    continue
                connection.execute(
                    insert(literature_snapshots).values(
                        id=snapshot["snapshot_id"],
                        work_id=work_id,
                        provider=snapshot["provider"],
                        provider_record_id=snapshot["provider_record_id"],
                        provider_roles_json=snapshot["provider_roles"],
                        title=snapshot["title"],
                        authors_json=snapshot["authors"],
                        venue=snapshot.get("venue"),
                        publication_date=snapshot.get("publication_date"),
                        publication_status=snapshot["publication_status"],
                        publication_type=snapshot.get("publication_type"),
                        doi=snapshot.get("doi"),
                        arxiv_id=snapshot.get("arxiv_id"),
                        abstract=snapshot.get("abstract"),
                        retrieved_passages_json=snapshot.get("retrieved_passages") or [],
                        cited_by_count=snapshot.get("cited_by_count"),
                        access_status=snapshot["access_status"],
                        source_url=snapshot.get("source_url"),
                        open_access_url=snapshot.get("open_access_url"),
                        license=snapshot.get("license"),
                        provider_updated_at=snapshot.get("provider_updated_at"),
                        retrieved_at=snapshot["retrieved_at"],
                        provider_field_sources_json=snapshot[
                            "provider_field_sources"
                        ],
                        raw_metadata_hash=snapshot["raw_metadata_hash"],
                        content_hash=snapshot.get("content_hash"),
                    )
                )
            return dict(
                connection.execute(
                    select(literature_works).where(literature_works.c.id == work_id)
                ).mappings().one()
            )

        return self._run(run)

    def get_work_for_candidate(self, candidate_id: str) -> dict[str, Any]:
        statement = select(literature_works).where(
            literature_works.c.candidate_id == candidate_id
        )

        def run(connection: Connection) -> dict[str, Any]:
            row = connection.execute(statement).mappings().first()
            if row is None:
                raise LookupError("Literature candidate not found")
            return dict(row)

        return self._run(run)

    def get_candidate(self, candidate_id: str) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            work = connection.execute(
                select(literature_works).where(
                    literature_works.c.candidate_id == candidate_id
                )
            ).mappings().first()
            if work is None:
                raise LookupError("Literature candidate not found")
            snapshots = connection.execute(
                select(literature_snapshots)
                .where(literature_snapshots.c.work_id == work["id"])
                .order_by(literature_snapshots.c.retrieved_at.asc())
            ).mappings().all()
            return {"work": dict(work), "snapshots": [dict(row) for row in snapshots]}

        return self._run(run)

    def get_work(self, work_id: UUID) -> dict[str, Any]:
        statement = select(literature_works).where(literature_works.c.id == work_id)

        def run(connection: Connection) -> dict[str, Any]:
            row = connection.execute(statement).mappings().first()
            if row is None:
                raise LookupError("Literature work not found")
            return dict(row)

        return self._run(run)

    def list_snapshots(self, work_id: UUID) -> list[dict[str, Any]]:
        statement = (
            select(literature_snapshots)
            .where(literature_snapshots.c.work_id == work_id)
            .order_by(literature_snapshots.c.retrieved_at.asc())
        )
        return self._run(
            lambda connection: [
                dict(row) for row in connection.execute(statement).mappings().all()
            ]
        )

    def get_snapshot(self, snapshot_id: UUID) -> dict[str, Any]:
        statement = select(literature_snapshots).where(
            literature_snapshots.c.id == snapshot_id
        )

        def run(connection: Connection) -> dict[str, Any]:
            row = connection.execute(statement).mappings().first()
            if row is None:
                raise LookupError("Literature snapshot not found")
            return dict(row)

        return self._run(run)

    def save_search(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            connection.execute(insert(literature_searches).values(**values))
            return dict(
                connection.execute(
                    select(literature_searches).where(
                        literature_searches.c.id == values["id"]
                    )
                ).mappings().one()
            )

        return self._run(run)

    def get_search(self, search_id: UUID) -> dict[str, Any]:
        statement = select(literature_searches).where(
            literature_searches.c.id == search_id
        )

        def run(connection: Connection) -> dict[str, Any]:
            row = connection.execute(statement).mappings().first()
            if row is None:
                raise LookupError("Literature search not found")
            return dict(row)

        return self._run(run)

    def find_latest_search(
        self, *, project_id: str, query_fingerprint: str
    ) -> dict[str, Any] | None:
        statement = (
            select(literature_searches)
            .where(
                and_(
                    literature_searches.c.project_id == project_id,
                    literature_searches.c.query_fingerprint == query_fingerprint,
                )
            )
            .order_by(literature_searches.c.created_at.desc())
            .limit(1)
        )
        return self._run(
            lambda connection: (
                dict(row)
                if (
                    row := connection.execute(statement).mappings().first()
                )
                is not None
                else None
            )
        )

    def save_evidence(self, values: Mapping[str, Any]) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            connection.execute(insert(literature_evidence).values(**values))
            return dict(
                connection.execute(
                    select(literature_evidence).where(
                        literature_evidence.c.id == values["id"]
                    )
                ).mappings().one()
            )

        return self._run(run)

    def get_evidence(self, evidence_id: UUID) -> dict[str, Any]:
        statement = select(literature_evidence).where(
            literature_evidence.c.id == evidence_id
        )

        def run(connection: Connection) -> dict[str, Any]:
            row = connection.execute(statement).mappings().first()
            if row is None:
                raise LookupError("Literature evidence not found")
            return dict(row)

        return self._run(run)

    def list_evidence_for_turn(self, turn_id: UUID) -> list[dict[str, Any]]:
        statement = (
            select(literature_evidence)
            .where(literature_evidence.c.research_turn_id == turn_id)
            .order_by(literature_evidence.c.selected_at.asc())
        )
        return self._run(
            lambda connection: [
                dict(row) for row in connection.execute(statement).mappings().all()
            ]
        )


__all__ = ["ScientificKnowledgeRepository"]
