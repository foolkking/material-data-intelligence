from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from mdi_api.config import load_settings
from mdi_api.database import create_repository_factory

from .queue import RedisRQInterpretationQueue


class ScientificInterpretationReconciler:
    """Republish only durable RESULT_READY identities; never reruns execution."""

    def __init__(self, repository_factory=None) -> None:
        self.repository_factory = repository_factory or create_repository_factory()

    def reconcile_turn(self, turn_id: UUID):
        settings = load_settings()
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            status = str(turn["status"])
            stale_interpreting = False
            if status == "INTERPRETING" and turn.get("updated_at") is not None:
                updated_at = turn["updated_at"]
                if updated_at.tzinfo is None:
                    updated_at = updated_at.replace(tzinfo=timezone.utc)
                stale_interpreting = (datetime.now(timezone.utc) - updated_at).total_seconds() > 900
            if status != "RESULT_READY" and not stale_interpreting:
                return {"turn_id": str(turn_id), "republished": False, "reason": "not_result_ready"}
        if settings.queue_backend != "redis" or not settings.agent2_interpretation_enabled:
            return {"turn_id": str(turn_id), "republished": False, "reason": "queue_disabled"}
        result = RedisRQInterpretationQueue(redis_url=settings.redis_url, queue_name=settings.agent2_interpretation_queue_name).enqueue_turn(turn_id)
        return {"turn_id": str(turn_id), "republished": result.enqueued, "backend": result.backend}


__all__ = ["ScientificInterpretationReconciler"]
