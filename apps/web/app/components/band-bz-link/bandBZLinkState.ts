import type { ReciprocalSelection, ReciprocalSelectionState } from "./bandBZLinkTypes";

export const EMPTY_RECIPROCAL_SELECTION: ReciprocalSelectionState = Object.freeze({ revision: 0, hover: null, pinned: null });

export type ReciprocalSelectionAction =
  | Readonly<{ type: "hover"; selection: ReciprocalSelection }>
  | Readonly<{ type: "leave"; transactionId: number }>
  | Readonly<{ type: "pin"; selection: ReciprocalSelection }>
  | Readonly<{ type: "clear" }>
  | Readonly<{ type: "artifacts_changed" }>;

export function reciprocalSelectionReducer(state: ReciprocalSelectionState, action: ReciprocalSelectionAction): ReciprocalSelectionState {
  if (action.type === "clear" || action.type === "artifacts_changed") return Object.freeze({ revision: state.revision + 1, hover: null, pinned: null });
  if (action.type === "leave") {
    if (!state.hover || state.hover.transactionId !== action.transactionId) return state;
    return Object.freeze({ ...state, revision: state.revision + 1, hover: null });
  }
  const key = selectionKey(action.selection);
  if (action.type === "hover") {
    if (state.hover && selectionKey(state.hover) === key) return state;
    return Object.freeze({ ...state, revision: state.revision + 1, hover: action.selection });
  }
  if (state.pinned && selectionKey(state.pinned) === key) return state;
  return Object.freeze({ revision: state.revision + 1, hover: null, pinned: action.selection });
}

export function effectiveReciprocalSelection(state: ReciprocalSelectionState): ReciprocalSelection | null {
  return state.hover ?? state.pinned;
}

function selectionKey(value: ReciprocalSelection): string {
  return [value.kind, value.bandArtifactHash, value.bzArtifactHash, value.pathVariantId, value.bzPointId ?? "", value.bzSegmentId ?? "", value.pointOccurrenceId ?? "", value.qpointIndex ?? "", value.branchIndex ?? "", value.modeId ?? "", value.t ?? ""].join(":");
}
