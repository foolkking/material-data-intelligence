import { describe, expect, it } from "vitest";

import { mapViewerSceneForRenderer } from "./viewerSceneRendererMapper";
import { buildViewerMeasurementArtifact } from "./viewerSceneMeasurementArtifact";
import { periodicBoundaryScene } from "./viewerScenePeriodicBondTestFixture";

describe("viewer measurement artifact", () => {
  it("serializes deterministic inert explicit-image measurement provenance", () => {
    const mapped = mapViewerSceneForRenderer(periodicBoundaryScene());
    expect(mapped.ok).toBe(true);
    if (!mapped.ok) return;
    const refs = [{siteIndex:0,imageOffset:[0,0,0] as const},{siteIndex:1,imageOffset:[1,0,0] as const}];
    const result = {kind:"distance" as const,siteIndices:[0,1] as const,value:0.40000000001,unit:"angstrom" as const};
    const first = buildViewerMeasurementArtifact(mapped.scene,"displayed_positions",refs,result);
    const second = buildViewerMeasurementArtifact(mapped.scene,"displayed_positions",refs,result);
    expect(JSON.stringify(first)).toBe(JSON.stringify(second));
    expect(first.measurement).toMatchObject({value:0.4,points:refs});
    expect(first.policy).toMatchObject({structure_mutated:false,topology_mutated:false});
    expect(first.security).toEqual({inert_json:true,artifact_javascript:false,external_urls:false});
  });

  it("rejects invalid periodic identities", () => {
    const mapped = mapViewerSceneForRenderer(periodicBoundaryScene());
    if (!mapped.ok) throw new Error("fixture invalid");
    expect(() => buildViewerMeasurementArtifact(mapped.scene,"displayed_positions",[{siteIndex:0,imageOffset:[0,0,0]},{siteIndex:1,imageOffset:[99,0,0]}],{kind:"distance",siteIndices:[0,1],value:1,unit:"angstrom"})).toThrow("VIEWER_MEASUREMENT_ARTIFACT_INVALID");
  });
});
