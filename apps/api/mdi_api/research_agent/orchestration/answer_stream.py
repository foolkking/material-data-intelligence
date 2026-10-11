"""Turn-fenced public answer drafts; validated messages remain authoritative."""

from __future__ import annotations

from datetime import datetime, timezone
import re
from time import monotonic
from typing import Any
from uuid import UUID, uuid4

from pydantic_core import from_json
from mdi_llm.http_transport import ProviderStreamCancelled
from mdi_llm.redaction import redact_sensitive_text

from mdi_api.research_agent.schemas import ResearchTurnEventType


def public_answer_text(text: str, secret_values: tuple[str, ...] = ()) -> str:
    for secret in secret_values:
        if secret:
            text = text.replace(secret, "***REDACTED***")
    return redact_sensitive_text(text)


class ResearchAnswerPublisher:
    def __init__(self, factory: Any, turn: dict[str, Any]) -> None:
        self.factory = factory
        self.turn_id = UUID(str(turn["id"]))
        self.version = int(turn["row_version"])
        self.response_id = str(uuid4())
        self.raw = ""
        self.sent = ""
        self.latest = ""
        self.revision = 0
        self.last_write = 0.0
        self.last_check = 0.0
        self.active = True
        self.preview_enabled = True
        self.secret_values: tuple[str, ...] = ()

    def feed(self, delta: str, *, secret_values: tuple[str, ...] = ()) -> None:
        if not self.active:
            raise ProviderStreamCancelled()
        now = monotonic()
        # Cancellation must still interrupt small or non-answer chunks that
        # do not qualify for a persisted public update.
        if now - self.last_check >= 0.5:
            with self.factory.session() as session:
                self._check_turn(session.agent2.research_turns.get(self.turn_id))
            self.last_check = now
        if not self.preview_enabled:
            return
        self.raw += delta
        if len(self.raw) > 200_000:
            if self.revision:
                self._write(ResearchTurnEventType.ASSISTANT_RESPONSE_RESET, {"response_id": self.response_id})
            self.preview_enabled = False
            self.raw = ""
            self.revision = 0
            return
        try:
            parsed = from_json(self.raw, allow_partial="trailing-strings", cache_strings=False)
        except ValueError:
            return
        if not isinstance(parsed, dict) or parsed.get("action") != "ANSWER":
            return
        text = parsed.get("assistant_message")
        if not isinstance(text, str) or len(text) > 8000:
            return
        self.secret_values = tuple(value for value in secret_values if value)
        self.latest = public_answer_text(text, self.secret_values)
        # Hold a possible split credential and the unfinished final word until
        # later text makes redaction stable. The saved answer has no holdback.
        holdback = max((len(value) for value in self.secret_values), default=0)
        safe_end = max(0, len(self.latest) - holdback)
        candidate = self.latest[:safe_end]
        candidate = re.sub(r"[A-Za-z0-9_./+=\\-]+$", "", candidate)
        # Publish the first words promptly, then budget updates across the
        # complete 8,000-character answer rather than spending them up front.
        minimum_delta = 8 if not self.revision else 64
        if self.revision >= 128 or now - self.last_write < 0.12 or len(candidate) - len(self.sent) < minimum_delta:
            return
        self._publish(candidate)
        self.last_write = now

    def finish(self, content: str | None, *, action: str) -> None:
        if action != "ANSWER" or not content:
            self.discard()
            return
        if self.revision and self.active:
            self._publish(public_answer_text(content, self.secret_values))
        self.active = False

    def discard(self) -> None:
        if self.active and self.revision:
            self._write(ResearchTurnEventType.ASSISTANT_RESPONSE_RESET, {"response_id": self.response_id})
        self.active = False

    def _publish(self, text: str) -> None:
        if text == self.sent:
            return
        if not text.startswith(self.sent):
            self._write(ResearchTurnEventType.ASSISTANT_RESPONSE_RESET, {"response_id": self.response_id})
            self.response_id = str(uuid4())
            self.revision = 0
            self.sent = ""
        revision = self.revision + 1
        self._write(ResearchTurnEventType.ASSISTANT_RESPONSE_DELTA, {
            "response_id": self.response_id, "revision": revision, "text": text[len(self.sent):],
        })
        self.sent = text
        self.revision = revision

    def _write(self, kind: ResearchTurnEventType, payload: dict[str, Any]) -> None:
        with self.factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get_for_update(self.turn_id)
            self._check_turn(turn)
            unit.agent2.research_turn_events.append_turn_event({
                "id": uuid4(), "turn_id": self.turn_id,
                "sequence_no": unit.agent2.research_turn_events.next_sequence_no(self.turn_id),
                "event_type": kind.value, "payload_json": payload,
                "created_at": datetime.now(timezone.utc),
            })

    def _check_turn(self, turn: dict[str, Any]) -> None:
        if turn["status"] != "ORCHESTRATING" or int(turn["row_version"]) != self.version:
            self.active = False
            raise ProviderStreamCancelled()
