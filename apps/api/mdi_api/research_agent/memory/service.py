from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any
from uuid import UUID, uuid4

from mdi_api.agent2_errors import ResearchSessionProjectMismatch
from mdi_api.research_agent.memory.schemas import ContextScope, ResearchContextItemType, ResearchSessionState, SessionConstraint
from mdi_api.scientific_objects.schemas import ScientificObjectRef


_CUTOFF = re.compile(r"(?:cutoff|截断|截止(?:距离|半径)?)[^0-9]{0,16}(?P<value>[0-9]+(?:\.[0-9]+)?)\s*(?:å|a|angstrom|埃)?", re.I)
_BARE_CUTOFF = re.compile(r"(?:改成|换成|设置为)\s*(?P<value>[0-9]+(?:\.[0-9]+)?)\s*(?:å|a|angstrom|埃)", re.I)
_SESSION_SCOPE = re.compile(r"(?:这个\s*session|本研究会话|后面|以后|接下来|今后|全程|之后都|后续都)")
_CLEAR = re.compile(r"(?:取消|清除|移除|不要再用).{0,20}(?:cutoff|截断|截止)", re.I)


class ResearchSessionMemoryService:
    """Small deterministic mutation service; it never treats model prose as authority."""

    def ensure(self, unit: Any, *, session_id: str, project_id: str) -> dict[str, Any]:
        session = unit.agent2.research_turns.get_session(session_id)
        if session is None or str(session["project_id"]) != project_id:
            raise ResearchSessionProjectMismatch(session_id)
        return unit.agent2.research_session_memory.ensure_state(
            session_id=session_id, project_id=project_id, state_id=uuid4()
        )

    def apply_user_message(self, unit: Any, *, session_id: str, project_id: str, message: str, message_id: str) -> dict[str, Any]:
        state = self.ensure(unit, session_id=session_id, project_id=project_id)
        text = message.strip()
        clear = bool(_CLEAR.search(text))
        match = _CUTOFF.search(text) or _BARE_CUTOFF.search(text)
        is_session = bool(_SESSION_SCOPE.search(text))
        constraints = list(state.get("session_constraints_json") or [])
        if clear and (is_session or "限制" in text or "刚才" in text):
            unit.agent2.research_session_memory.deactivate_items(
                session_id, item_type=ResearchContextItemType.SESSION_CONSTRAINT.value,
                predicate=lambda row: str((row.get("structured_constraint_json") or {}).get("name")) == "cutoff",
            )
            constraints = [item for item in constraints if str(item.get("name")) not in {"cutoff", "cutoff_angstrom"}]
        elif match and is_session:
            value = float(match.group("value"))
            unit.agent2.research_session_memory.deactivate_items(
                session_id, item_type=ResearchContextItemType.SESSION_CONSTRAINT.value,
                predicate=lambda row: str((row.get("structured_constraint_json") or {}).get("name")) == "cutoff",
            )
            constraints = [item for item in constraints if str(item.get("name")) not in {"cutoff", "cutoff_angstrom"}]
            constraints.append({"name": "cutoff_angstrom", "value": value, "unit": "Å", "statement": text})
            unit.agent2.research_session_memory.add_item({
                "id": uuid4(), "session_id": session_id, "project_id": project_id,
                "item_type": ResearchContextItemType.SESSION_CONSTRAINT.value,
                "scope": ContextScope.SESSION.value, "ref_json": None,
                "statement": text, "structured_constraint_json": {"name": "cutoff", "value": value, "unit": "Å"},
                "source_message_id": message_id, "explicitly_requested": True, "active": True,
                "version": 1, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
            })
        values = {"session_constraints_json": constraints}
        if text.lower().startswith(("research goal:", "目标:", "研究目标:")):
            goal = text.split(":", 1)[1].strip()
            values["active_research_goal"] = goal[:2048]
            unit.agent2.research_session_memory.add_item({
                "id": uuid4(), "session_id": session_id, "project_id": project_id,
                "item_type": ResearchContextItemType.RESEARCH_GOAL.value, "scope": ContextScope.SESSION.value,
                "ref_json": None, "statement": goal, "structured_constraint_json": None,
                "source_message_id": message_id, "explicitly_requested": True, "active": True,
                "version": 1, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
            })
        if values != {"session_constraints_json": list(state.get("session_constraints_json") or [])} or "active_research_goal" in values:
            state = unit.agent2.research_session_memory.update_state(
                session_id, expected_version=int(state["version"]), values=values,
            )
        return state

    def get_state(self, unit: Any, *, session_id: str, project_id: str) -> ResearchSessionState:
        row = self.ensure(unit, session_id=session_id, project_id=project_id)
        items = unit.agent2.research_session_memory.list_items(session_id)
        constraints = []
        for item in items:
            if item["item_type"] != ResearchContextItemType.SESSION_CONSTRAINT.value:
                continue
            constraints.append(SessionConstraint(
                id=str(item["id"]), scope=ContextScope(item["scope"]), statement=str(item.get("statement") or "constraint"),
                structured_constraint=item.get("structured_constraint_json"), source_message_id=str(item.get("source_message_id") or ""),
                explicitly_requested=bool(item.get("explicitly_requested", True)), active=bool(item.get("active", True)),
                created_at=item["created_at"], updated_at=item["updated_at"],
            ))
        return ResearchSessionState(
            session_id=session_id, project_id=project_id,
            active_scope_refs=[ScientificObjectRef.model_validate(x) for x in row.get("active_scope_refs_json") or []],
            active_selection_refs=[ScientificObjectRef.model_validate(x) for x in row.get("active_selection_refs_json") or []],
            pinned_object_refs=[ScientificObjectRef.model_validate(x) for x in row.get("pinned_object_refs_json") or []],
            pinned_result_refs=[UUID(str(x)) for x in row.get("pinned_result_refs_json") or []],
            session_constraints=constraints,
            active_research_goal=row.get("active_research_goal"),
            open_questions=list(row.get("open_questions_json") or []), version=int(row["version"]),
            updated_at=row["updated_at"], created_at=row["created_at"],
        )

    def pin_result(self, unit: Any, *, session_id: str, project_id: str, result_id: UUID) -> ResearchSessionState:
        state = self.ensure(unit, session_id=session_id, project_id=project_id)
        snapshot = unit.agent2.scientific_result_snapshots.get(result_id)
        if str(snapshot["project_id"]) != project_id:
            raise ResearchSessionProjectMismatch("result is outside the Research Session project")
        values = list(state.get("pinned_result_refs_json") or [])
        if str(result_id) not in {str(x) for x in values}:
            values.append(str(result_id))
            unit.agent2.research_session_memory.add_item({
                "id": uuid4(), "session_id": session_id, "project_id": project_id,
                "item_type": ResearchContextItemType.PINNED_RESULT.value, "scope": ContextScope.SESSION.value,
                "ref_json": {"result_id": str(result_id)}, "statement": "Pinned result", "structured_constraint_json": None,
                "source_message_id": None, "explicitly_requested": True, "active": True, "version": 1,
                "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
            })
            state = unit.agent2.research_session_memory.update_state(session_id, expected_version=int(state["version"]), values={"pinned_result_refs_json": values})
        return self.get_state(unit, session_id=session_id, project_id=project_id)

    def pin_object(self, unit: Any, *, session_id: str, project_id: str, object_ref: ScientificObjectRef) -> ResearchSessionState:
        state = self.ensure(unit, session_id=session_id, project_id=project_id)
        logical = unit.agent2.scientific_objects.get_object(object_ref.object_id)
        version = unit.agent2.scientific_objects.get_version(object_ref.version_id)
        if str(logical["project_id"]) != project_id or version["scientific_object_id"] != object_ref.object_id or str(version["object_type"]) != object_ref.object_type:
            raise ResearchSessionProjectMismatch("object is outside the Research Session project")
        values = list(state.get("pinned_object_refs_json") or [])
        identity = (str(object_ref.object_id), str(object_ref.version_id))
        if not any((str(item.get("object_id")), str(item.get("version_id"))) == identity for item in values):
            values.append(object_ref.model_dump(mode="json"))
            unit.agent2.research_session_memory.add_item({
                "id": uuid4(), "session_id": session_id, "project_id": project_id,
                "item_type": ResearchContextItemType.PINNED_OBJECT.value, "scope": ContextScope.SESSION.value,
                "ref_json": object_ref.model_dump(mode="json"), "statement": "Pinned object", "structured_constraint_json": None,
                "source_message_id": None, "explicitly_requested": True, "active": True, "version": 1,
                "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
            })
            unit.agent2.research_session_memory.update_state(session_id, expected_version=int(state["version"]), values={"pinned_object_refs_json": values})
        return self.get_state(unit, session_id=session_id, project_id=project_id)

    def unpin_object(self, unit: Any, *, session_id: str, project_id: str, object_ref: ScientificObjectRef) -> ResearchSessionState:
        state = self.ensure(unit, session_id=session_id, project_id=project_id)
        values = [item for item in list(state.get("pinned_object_refs_json") or []) if not (str(item.get("object_id")) == str(object_ref.object_id) and str(item.get("version_id")) == str(object_ref.version_id))]
        unit.agent2.research_session_memory.deactivate_items(session_id, item_type=ResearchContextItemType.PINNED_OBJECT.value, predicate=lambda row: str((row.get("ref_json") or {}).get("object_id")) == str(object_ref.object_id) and str((row.get("ref_json") or {}).get("version_id")) == str(object_ref.version_id))
        if len(values) != len(state.get("pinned_object_refs_json") or []):
            unit.agent2.research_session_memory.update_state(session_id, expected_version=int(state["version"]), values={"pinned_object_refs_json": values})
        return self.get_state(unit, session_id=session_id, project_id=project_id)

    def unpin_result(self, unit: Any, *, session_id: str, project_id: str, result_id: UUID) -> ResearchSessionState:
        state = self.ensure(unit, session_id=session_id, project_id=project_id)
        values = [x for x in list(state.get("pinned_result_refs_json") or []) if str(x) != str(result_id)]
        unit.agent2.research_session_memory.deactivate_items(session_id, item_type=ResearchContextItemType.PINNED_RESULT.value, predicate=lambda row: str((row.get("ref_json") or {}).get("result_id")) == str(result_id))
        if values != list(state.get("pinned_result_refs_json") or []):
            unit.agent2.research_session_memory.update_state(session_id, expected_version=int(state["version"]), values={"pinned_result_refs_json": values})
        return self.get_state(unit, session_id=session_id, project_id=project_id)
