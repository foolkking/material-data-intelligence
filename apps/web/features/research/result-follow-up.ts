import type { Agent2ResearchTurnResult, Agent2TurnInput, Agent2ScientificObjectRef, Agent2TurnResponse } from "../../app/lib/agent2-research-api";

export type ResultResearchAction = "reinterpret" | "rerun";

export function resultFollowUpInput(action: ResultResearchAction, result: Agent2ResearchTurnResult, sourceTurn?: Pick<Agent2TurnResponse, "turn_id" | "user_message"> | null): Agent2TurnInput {
  if (action === "rerun" && (sourceTurn?.turn_id !== result.research_turn_id || !sourceTurn.user_message.content.trim())) {
    throw new Error("暂时无法读取这次研究的原始问题，请重新读取研究记录后再试。");
  }
  const refs = (result.source_object_refs || []).map(requestObjectRef);
  return {
    ...(action === "reinterpret" ? { requested_action: "INTERPRET_RESULT" as const } : {}),
    message: action === "reinterpret"
      ? "请重新解释这份科学结果，突出关键发现、证据与限制；不要重新计算科学结果。"
      : sourceTurn!.user_message.content,
    reply_to_turn_id: result.research_turn_id,
    ui_context: {
      active_object_refs: refs, selection_refs: refs, explicit_object_refs: refs,
      scientific_selections: (result.scientific_selections || []).map(selection => ({ ...selection, object_ref: requestObjectRef(selection.object_ref) })),
      explicit_result_ids: action === "reinterpret" ? [result.result_snapshot_id || result.result_id] : [],
      explicit_finding_refs: [],
    },
  };
}

// Read projections may add display metadata such as version_no. Creation uses
// only the strict scientific reference contract, preserving its exact identity.
function requestObjectRef(ref: Agent2ScientificObjectRef): Agent2ScientificObjectRef {
  return { object_id: ref.object_id, version_id: ref.version_id, project_id: ref.project_id, object_type: ref.object_type,
    ...(ref.display_name !== undefined ? { display_name: ref.display_name } : {}) };
}
