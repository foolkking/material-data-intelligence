import { describe, expect, it } from "vitest";
import { effectiveReciprocalSelection, EMPTY_RECIPROCAL_SELECTION, reciprocalSelectionReducer } from "./bandBZLinkState";
import type { ReciprocalSelection } from "./bandBZLinkTypes";

const selection=(transactionId:number,pinned:boolean):ReciprocalSelection=>({sourcePanel:"band",kind:"sampled_reciprocal_point",transactionId,pinned,bandArtifactHash:"a".repeat(64),bzArtifactHash:"b".repeat(64),pathVariantId:"variant",qpointIndex:1,branchIndex:2,t:.5});
describe("reciprocal linked selection reducer",()=>{
  it("keeps hover transient, restores pinned selection and ignores stale leave transactions",()=>{let state=reciprocalSelectionReducer(EMPTY_RECIPROCAL_SELECTION,{type:"pin",selection:selection(1,true)});state=reciprocalSelectionReducer(state,{type:"hover",selection:selection(2,false)});expect(effectiveReciprocalSelection(state)?.transactionId).toBe(2);expect(reciprocalSelectionReducer(state,{type:"leave",transactionId:1})).toBe(state);state=reciprocalSelectionReducer(state,{type:"leave",transactionId:2});expect(effectiveReciprocalSelection(state)?.transactionId).toBe(1);});
  it("is idempotent for equivalent controlled selections and clears all stale references on artifact switch",()=>{const first=reciprocalSelectionReducer(EMPTY_RECIPROCAL_SELECTION,{type:"pin",selection:selection(1,true)});const same=reciprocalSelectionReducer(first,{type:"pin",selection:selection(99,true)});expect(same).toBe(first);const cleared=reciprocalSelectionReducer(first,{type:"artifacts_changed"});expect(cleared.pinned).toBeNull();expect(cleared.hover).toBeNull();expect(cleared.revision).toBe(first.revision+1);});
});
