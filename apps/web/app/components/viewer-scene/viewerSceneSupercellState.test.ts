import { describe, expect, it } from "vitest";
import { mapViewerSceneForRenderer } from "./viewerSceneRendererMapper";
import { periodicBoundaryScene } from "./viewerScenePeriodicBondTestFixture";
import { buildViewerSupercellState, replayViewerSupercellState } from "./viewerSceneSupercellState";

function scene(){const mapped=mapViewerSceneForRenderer(periodicBoundaryScene());if(!mapped.ok)throw new Error("fixture invalid");return mapped.scene;}

describe("viewer supercell state artifact",()=>{
  it("serializes and replays deterministic renderer-local state",()=>{
    const settings={expansion:[2,2,1] as const,originPolicy:"positive_octant" as const,showPrimaryCell:true,showSupercellBoundary:true,showInternalGrid:false as const};
    const first=buildViewerSupercellState(scene(),settings); const second=buildViewerSupercellState(scene(),settings);
    expect(JSON.stringify(first)).toBe(JSON.stringify(second));
    expect(first).toMatchObject({schema_version:"phase10f24.viewer_supercell_state.v1",counts:{total_cells:4,displayed_atoms:8},policy:{renderer_local:true,structure_mutated:false,canonical_topology_mutated:false},security:{inert_json:true,contains_javascript:false,external_urls:[]}});
    expect(replayViewerSupercellState(scene(),first)).toEqual(settings);
  });
  it("rejects scene mismatch, executable-looking unknown input, and over-budget state",()=>{
    const valid=buildViewerSupercellState(scene(),{expansion:[2,1,1],originPolicy:"positive_octant",showPrimaryCell:true,showSupercellBoundary:true,showInternalGrid:false});
    expect(()=>replayViewerSupercellState(scene(),{...valid,scene:{...valid.scene,resource_id:"other"}})).toThrow("VIEWER_SUPERCELL_STATE_INVALID");
    expect(()=>replayViewerSupercellState(scene(),{...valid,origin_policy:"<script>"})).toThrow("VIEWER_SUPERCELL_STATE_INVALID");
  });
});
