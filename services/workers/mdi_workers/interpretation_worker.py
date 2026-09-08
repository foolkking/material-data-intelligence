from __future__ import annotations

import os
import json

from mdi_api.application.interpretation import interpret_queued_turn
from mdi_api.bootstrap.repository_factory import create_repository_factory
from mdi_api.infrastructure.interpretation.client import FakeStructuredInterpreterClient
from mdi_api.infrastructure.interpretation.service import ScientificInterpretationService


def run_queued_interpretation(turn_id: str) -> dict:
    client = None
    fixture = os.getenv("MDI_AGENT2_INTERPRETATION_FIXTURE_JSON")
    if fixture and os.getenv("MDI_ENV", "").lower() in {"test", "ci"}:
        client = FakeStructuredInterpreterClient(json.loads(fixture))
    factory = create_repository_factory()
    result = interpret_queued_turn(
        turn_id,
        interpreter=ScientificInterpretationService(factory, client=client),
        repository_factory=factory,
    )
    return {**result, "process_id": os.getpid()}


__all__ = ["run_queued_interpretation"]
