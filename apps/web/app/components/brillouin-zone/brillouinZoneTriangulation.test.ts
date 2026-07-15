import { describe, expect, it } from "vitest";

import { triangulateFace } from "./brillouinZoneTriangulation";

describe("Brillouin face triangulation", () => {
  it("triangulates bounded convex loops on non-axis-aligned planes with matching area", () => {
    const triangle = triangulateFace([[0,0,0],[1,0,0],[0,1,0]],[0,0,1],0.5);
    expect(triangle.indices).toEqual([0,1,2]);
    const square = triangulateFace([[0,0,0],[1,0,1],[1,1,2],[0,1,1]],[-1,-1,1],Math.sqrt(3));
    expect(square.triangleCount).toBe(2);
    expect(square.area).toBeCloseTo(Math.sqrt(3), 10);
    const pentagon = triangulateFace([[1,0,0],[0.3,0.95,0],[-0.8,0.59,0],[-0.8,-0.59,0],[0.3,-0.95,0]],[0,0,1],2.359);
    expect(pentagon.triangleCount).toBe(3);
  });

  it("rejects reversed, duplicate, collinear, non-coplanar, area-mismatched and overlong loops", () => {
    expect(() => triangulateFace([[0,0,0],[0,1,0],[1,0,0]],[0,0,1],0.5)).toThrow("BZ_FACE_WINDING_INVALID");
    expect(() => triangulateFace([[0,0,0],[1,0,0],[1,0,0],[0,1,0]],[0,0,1],0.5)).toThrow("BZ_TRIANGLE_DEGENERATE");
    expect(() => triangulateFace([[0,0,0],[1,0,0],[2,0,0]],[0,0,1],1)).toThrow("BZ_FACE_DEGENERATE");
    expect(() => triangulateFace([[0,0,0],[1,0,0],[0,1,0.01]],[0,0,1],0.5)).toThrow("BZ_FACE_NON_COPLANAR");
    expect(() => triangulateFace([[0,0,0],[1,0,0],[0,1,0]],[0,0,1],2)).toThrow("BZ_FACE_AREA_MISMATCH");
    expect(() => triangulateFace(Array.from({length:65},(_,index)=>[Math.cos(index),Math.sin(index),0] as const),[0,0,1],1)).toThrow("BZ_FACE_INVALID");
  });
});
