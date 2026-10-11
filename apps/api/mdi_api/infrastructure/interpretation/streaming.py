"""Publish complete, grounded findings while the interpreter is still running."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from time import monotonic
from typing import Any, Callable
from uuid import UUID, uuid4

from pydantic import ValidationError
from mdi_llm.http_transport import ProviderStreamCancelled

from mdi_api.application.interpretation.grounding import (
    project_claim_support_assessments,
    project_grounded_communication,
    validate_interpretation,
)
from mdi_api.application.interpretation.projector import AssistantResponseProjector
from mdi_api.domain.interpretation.contracts import ScientificInterpretationOutput
from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
from mdi_api.research_agent.orchestration.answer_stream import public_answer_text
from mdi_api.research_agent.schemas import ResearchTurnEventType


def completed_interpretation_parts(raw: str) -> dict[str, Any]:
    """Read closed JSON values only; an unfinished finding has no authority.

    A partial-JSON decoder would synthesize missing optional qualifiers and
    references. Walk the two finding arrays explicitly so an item is available
    only after its closing brace, even when the surrounding array is unfinished.
    All buffers and finding counts are bounded by the publisher/provider schema.
    """
    decoder = json.JSONDecoder()
    text = raw.lstrip()
    if text.startswith("```"):
        if "\n" not in text:
            return {}
        text = text.split("\n", 1)[1].lstrip()
    if not text.startswith("{"):
        return {}
    parts: dict[str, Any] = {}
    seen: set[str] = set()
    position = 1

    def whitespace(index: int) -> int:
        while index < len(text) and text[index] in " \t\r\n":
            index += 1
        return index

    try:
        while True:
            position = whitespace(position)
            if position >= len(text) or text[position] == "}":
                return parts
            key, position = decoder.raw_decode(text, position)
            if not isinstance(key, str) or key in seen:
                raise ValueError("ambiguous interpretation fields")
            seen.add(key)
            position = whitespace(position)
            if position >= len(text):
                return parts
            if text[position] != ":":
                raise ValueError("invalid interpretation field")
            position = whitespace(position + 1)
            if key in {"primary_findings", "supporting_findings"}:
                if position >= len(text):
                    return parts
                if text[position] != "[":
                    raise ValueError("invalid finding collection")
                items: list[Any] = []
                parts[key] = items
                position += 1
                while True:
                    position = whitespace(position)
                    if position >= len(text):
                        return parts
                    if text[position] == "]":
                        position += 1
                        break
                    item, position = decoder.raw_decode(text, position)
                    if not isinstance(item, dict):
                        raise ValueError("invalid finding")
                    items.append(item)
                    if len(items) > (8 if key == "primary_findings" else 16):
                        raise ValueError("too many findings")
                    position = whitespace(position)
                    if position >= len(text):
                        return parts
                    if text[position] == "]":
                        position += 1
                        break
                    if text[position] != ",":
                        raise ValueError("invalid finding delimiter")
                    position += 1
            else:
                value, position = decoder.raw_decode(text, position)
                if key in {"contract_version", "primary_result_refs", "supporting_result_refs"}:
                    parts[key] = value
            position = whitespace(position)
            if position >= len(text) or text[position] == "}":
                return parts
            if text[position] != ",":
                raise ValueError("invalid interpretation delimiter")
            position += 1
    except json.JSONDecodeError:
        return parts


class InterpretationStreamPublisher:
    """A public preview owns the exact INTERPRETING claim, never the Result."""

    def __init__(
        self, factory: Any, *, turn_id: UUID, claim_version: int,
        bundle: ScientificResultBundle, relevance: str,
        normalize: Callable[[Any], Any],
    ) -> None:
        self.factory = factory
        self.turn_id = turn_id
        self.version = claim_version
        self.bundle = bundle
        self.relevance = relevance
        self.normalize = normalize
        self.response_id = str(uuid4())
        self.revision = 0
        self.raw = ""
        self.sent = ""
        self.enabled = True
        self.last_check = 0.0
        self.last_parts = ""
        self.secret_values: tuple[str, ...] = ()
        # A reclaimed worker must withdraw the earlier claim's public preview
        # even if the replacement provider has not produced its first finding.
        with self.factory.unit_of_work() as unit:
            self._check(unit.agent2.research_turns.get_for_update(turn_id))
            events = unit.agent2.research_turn_events.list_for_turn(turn_id)
            previous = next((event for event in reversed(events) if event["event_type"] in {
                ResearchTurnEventType.ASSISTANT_RESPONSE_DELTA.value,
                ResearchTurnEventType.ASSISTANT_RESPONSE_RESET.value,
            }), None)
            if previous and previous["event_type"] == ResearchTurnEventType.ASSISTANT_RESPONSE_DELTA.value:
                self._append(unit, ResearchTurnEventType.ASSISTANT_RESPONSE_RESET,
                             {"response_id": previous["payload_json"]["response_id"]})

    def feed(self, delta: str, *, secret_values: tuple[str, ...] = ()) -> None:
        now = monotonic()
        if now - self.last_check >= 0.5:
            with self.factory.session() as session:
                self._check(session.agent2.research_turns.get(self.turn_id))
            self.last_check = now
        if not self.enabled:
            return
        self.secret_values = tuple(value for value in secret_values if value)
        self.raw += delta
        if len(self.raw) > 200_000:
            self.discard()
            return
        try:
            parts = completed_interpretation_parts(self.raw)
        except ValueError:
            self.discard()
            return
        signature = json.dumps(parts, ensure_ascii=False, sort_keys=True)
        if signature == self.last_parts:
            return
        self.last_parts = signature
        if not isinstance(parts.get("contract_version"), str) or parts["contract_version"] not in {"1.0", "1.1"}:
            return
        findings = [*parts.get("primary_findings", []), *parts.get("supporting_findings", [])]
        ids = [item.get("finding_id") for item in findings]
        if len(ids) != len(set(str(value) for value in ids)):
            self.discard()
            return
        statements: list[str] = []
        for finding in findings:
            try:
                payload = self.normalize({
                    "contract_version": parts["contract_version"], "title": "分析结果",
                    "answer_lead": finding.get("statement", ""), "primary_findings": [finding],
                    "primary_result_refs": finding.get("result_item_refs") or parts.get("primary_result_refs", []),
                    "supporting_result_refs": parts.get("supporting_result_refs", []),
                })
                output = ScientificInterpretationOutput.model_validate(payload)
                output = project_claim_support_assessments(output, self.bundle)
                output = project_grounded_communication(output, self.bundle, project_suggestions=False)
                if validate_interpretation(output, self.bundle).valid:
                    statements.append(output.primary_findings[0].statement.strip())
            except (ValidationError, TypeError, ValueError):
                continue
        if not statements:
            return
        # The Result's execution/source qualifications precede the first claim.
        # Provider-authored lead, title, reasoning and unfinished text stay private.
        prefix = ["## 分析结果"]
        notice = AssistantResponseProjector._status_notice(self.bundle.execution_status.value, self.relevance)
        if notice:
            prefix.append(notice)
        qualifications = list(dict.fromkeys(
            item.message.strip() for item in [*self.bundle.limitations, *self.bundle.warnings] if item.message.strip()
        ))
        if qualifications:
            prefix.append("\n".join(f"> {line}" for item in qualifications for line in item.splitlines()))
        candidate = public_answer_text("\n\n".join([*prefix, *statements]), self.secret_values)
        if candidate == self.sent:
            return
        if len(candidate) > 16_000 or self.revision >= 128:
            self.discard()
            return
        if not candidate.startswith(self.sent):
            self._write(ResearchTurnEventType.ASSISTANT_RESPONSE_RESET, {"response_id": self.response_id})
            self.response_id = str(uuid4())
            self.revision = 0
            self.sent = ""
        revision = self.revision + 1
        self._write(ResearchTurnEventType.ASSISTANT_RESPONSE_DELTA, {
            "response_id": self.response_id, "revision": revision, "text": candidate[len(self.sent):],
            "claim_version": self.version, "response_kind": "SCIENTIFIC_INTERPRETATION",
        })
        self.revision = revision
        self.sent = candidate

    def discard(self) -> None:
        if self.revision:
            self._write(ResearchTurnEventType.ASSISTANT_RESPONSE_RESET, {"response_id": self.response_id})
        self.revision = 0
        self.raw = ""
        self.sent = ""
        self.enabled = False

    def _check(self, turn: dict[str, Any]) -> None:
        if turn["status"] != "INTERPRETING" or int(turn["row_version"]) != self.version:
            raise ProviderStreamCancelled()

    def _write(self, kind: ResearchTurnEventType, payload: dict[str, Any]) -> None:
        with self.factory.unit_of_work() as unit:
            self._check(unit.agent2.research_turns.get_for_update(self.turn_id))
            self._append(unit, kind, payload)

    def _append(self, unit: Any, kind: ResearchTurnEventType, payload: dict[str, Any]) -> None:
        unit.agent2.research_turn_events.append_turn_event({
            "id": uuid4(), "turn_id": self.turn_id,
            "sequence_no": unit.agent2.research_turn_events.next_sequence_no(self.turn_id),
            "event_type": kind.value, "payload_json": payload,
            "created_at": datetime.now(timezone.utc),
        })
