from __future__ import annotations

import os
import json
from uuid import UUID

from mdi_api.database import create_repository_factory
from mdi_api.interpretation.client import FakeStructuredInterpreterClient
from mdi_api.interpretation.service import ScientificInterpretationService


def run_queued_interpretation(turn_id: str) -> dict:
    client = None
    fixture = os.getenv("MDI_AGENT2_INTERPRETATION_FIXTURE_JSON")
    if fixture and os.getenv("MDI_ENV", "").lower() in {"test", "ci"}:
        client = FakeStructuredInterpreterClient(json.loads(fixture))
    factory = create_repository_factory()
    row = ScientificInterpretationService(factory, client=client).process_turn(UUID(turn_id))
    with factory.session() as session:
        status = str(session.agent2.research_turns.get(UUID(turn_id))["status"])
    return {"turn_id": turn_id, "interpretation_id": str(row["id"]), "status": status, "process_id": os.getpid()}


__all__ = ["run_queued_interpretation"]
