from __future__ import annotations

from uuid import uuid4

from mdi_api.research_agent.orchestration.queue import DisabledAgentTurnQueue, InMemoryAgentTurnQueue


def test_agent_turn_queue_payload_is_only_turn_identity_and_is_idempotent():
    queue = InMemoryAgentTurnQueue()
    turn_id = uuid4()
    first = queue.enqueue_turn(turn_id)
    duplicate = queue.enqueue_turn(turn_id)
    assert first.enqueued is True and duplicate.enqueued is False
    assert queue.pop_next() == turn_id and queue.pop_next() is None
    assert set(first.__dict__) == {"turn_id", "enqueued", "backend", "message"}


def test_disabled_agent_turn_queue_never_performs_work():
    result = DisabledAgentTurnQueue().enqueue_turn(uuid4())
    assert result.enqueued is False and result.backend == "disabled"
