import { Agent2ReadError, getAgent2ResearchTurn, getAgent2ResearchTurnResult, type Agent2ResearchTurnResult, type Agent2ScientificObjectRef, type Agent2ScientificSelection, type Agent2TurnDetail } from "../../app/lib/agent2-research-api";
import { readSessionRequest } from "./session-management";

export class BranchSourceError extends Error {
  constructor() { super("原研究的问题或来源暂时无法确认。草稿已保留，请重新读取后再提交。"); this.name = "BranchSourceError"; }
}

function validateRefs(refs: Agent2ScientificObjectRef[], projectId: string) {
  if (!Array.isArray(refs) || refs.some((ref) => !ref || ref.project_id !== projectId || !ref.object_id || !ref.version_id || !ref.object_type)) throw new BranchSourceError();
}
function validateSelections(selections: Agent2ScientificSelection[], projectId: string) {
  if (!Array.isArray(selections)) throw new BranchSourceError();
  for (const selection of selections) {
    if (!selection || selection.contract_version !== "1.0" || !selection.viewer_id || !selection.selection_type || !selection.semantic_locator) throw new BranchSourceError();
    validateRefs([selection.object_ref], projectId);
  }
}
export function validateBranchTurn(turn: Agent2TurnDetail, projectId: string, sessionId: string, turnId: string) {
  if (!turn || turn.turn_id !== turnId || turn.project_id !== projectId || turn.research_session_id !== sessionId ||
      typeof turn.user_message?.content !== "string" || !turn.user_message.content.trim()) throw new BranchSourceError();
  if (turn.context) {
    validateRefs(turn.context.scope, projectId); validateRefs(turn.context.selection, projectId);
    validateSelections(turn.context.scientific_selection, projectId);
  }
  return turn;
}
export function validateBranchResult(result: Agent2ResearchTurnResult, projectId: string, turnId: string) {
  if (!result || result.research_turn_id !== turnId || typeof result.result_id !== "string" || !result.result_id) throw new BranchSourceError();
  validateRefs(result.source_object_refs, projectId); validateSelections(result.scientific_selections || [], projectId);
  return result;
}
export async function readBranchTurn(projectId: string, sessionId: string, turnId: string, signal: AbortSignal) {
  try {
    return validateBranchTurn(await readSessionRequest((requestSignal) => getAgent2ResearchTurn(turnId, { signal: requestSignal }), signal), projectId, sessionId, turnId);
  } catch { throw new BranchSourceError(); }
}
export async function readBranchResult(projectId: string, turnId: string, signal: AbortSignal) {
  try {
    return validateBranchResult(await readSessionRequest((requestSignal) => getAgent2ResearchTurnResult(turnId, { signal: requestSignal }), signal), projectId, turnId);
  } catch (reason) {
    if (reason instanceof Agent2ReadError && reason.status === 404) return null;
    if (reason instanceof Agent2ReadError && reason.status === 409 && reason.code === "SCIENTIFIC_RESULT_NOT_READY") {
      // A conversational terminal Turn has no scientific snapshot. Confirm the
      // exact source before allowing continuation; a pending or unread result
      // must not silently become an empty context.
      try {
        const turn = await readSessionRequest(requestSignal => getAgent2ResearchTurn(turnId, { signal: requestSignal }), signal);
        if (turn.research_session_id && ["ANSWERED", "NEEDS_CLARIFICATION", "UNSUPPORTED", "PLAN_REJECTED"].includes(turn.status)) {
          validateBranchTurn(turn, projectId, turn.research_session_id, turnId);
          return null;
        }
      } catch { /* Preserve the recoverable source error below. */ }
    }
    throw new BranchSourceError();
  }
}
