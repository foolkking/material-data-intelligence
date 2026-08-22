from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from mdi_api.agent2_errors import InvalidScientificObjectVersion
from mdi_api.scientific_results.schemas import ScientificResultBundle
from mdi_api.unit_of_work import RepositoryFactory


class ScientificResultSnapshotService:
    def __init__(self, repository_factory: RepositoryFactory) -> None:
        self.repository_factory = repository_factory

    def persist_snapshot(self, bundle: ScientificResultBundle, source_fingerprint: str, *, job_id: str | None = None) -> dict[str, Any]:
        if not source_fingerprint.strip():
            raise ValueError("source_fingerprint is required")
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get(bundle.research_turn_id)
            if turn["project_id"] != bundle.project_id or turn["research_session_id"] != bundle.research_session_id:
                raise InvalidScientificObjectVersion("result bundle scope does not match its ResearchTurn")
            refs = [
                *bundle.source_object_refs,
                *bundle.output_object_refs,
                *[
                    ref
                    for item in bundle.result_items
                    for ref in item.scientific_object_refs
                ],
                *[
                    fact.source.scientific_object_ref
                    for fact in bundle.facts
                    if fact.source.scientific_object_ref is not None
                ],
            ]
            for ref in refs:
                logical = unit.agent2.scientific_objects.get_object(ref.object_id)
                version = unit.agent2.scientific_objects.get_version(ref.version_id)
                if (
                    logical["project_id"] != bundle.project_id
                    or ref.project_id != bundle.project_id
                    or version["scientific_object_id"] != logical["id"]
                    or logical["object_type"] != ref.object_type
                    or version["object_type"] != ref.object_type
                ):
                    raise InvalidScientificObjectVersion(
                        "result bundle contains an unauthorized or inconsistent ScientificObjectRef"
                    )
            existing = unit.agent2.scientific_result_snapshots.get_by_identity(
                bundle.research_turn_id, bundle.projection_version, source_fingerprint
            )
            if existing:
                return existing
            return unit.agent2.scientific_result_snapshots.add({
                "id": uuid4(),
                "project_id": bundle.project_id,
                "research_turn_id": bundle.research_turn_id,
                "job_id": job_id,
                "schema_version": bundle.schema_version,
                "projection_version": bundle.projection_version,
                "execution_status": bundle.execution_status.value,
                "relevance_status": bundle.relevance_status.value,
                "source_fingerprint": source_fingerprint,
                "bundle_json": bundle.model_dump(mode="json"),
            })

    def get_latest_for_turn(self, turn_id: UUID) -> ScientificResultBundle:
        with self.repository_factory.session() as session:
            row = session.agent2.scientific_result_snapshots.get_latest_for_turn(turn_id)
            return ScientificResultBundle.model_validate(row["bundle_json"])

    def list_for_turn(self, turn_id: UUID) -> list[ScientificResultBundle]:
        with self.repository_factory.session() as session:
            return [ScientificResultBundle.model_validate(row["bundle_json"]) for row in session.agent2.scientific_result_snapshots.list_for_turn(turn_id)]
