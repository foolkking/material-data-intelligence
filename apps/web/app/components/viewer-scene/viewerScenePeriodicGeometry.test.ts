import { describe, expect, it } from "vitest";

import { cartesianToFractional, determinant, fractionalToCartesian, inverseLattice, minimumImage, periodicAngle, periodicDihedral, periodicSiteKey, translateCartesian } from "./viewerScenePeriodicGeometry";
import type { RenderLattice, RenderVector3 } from "./viewerSceneRendererTypes";
import reference from "../../../../../docs/phase10f/evidence/phase10f17_periodic_crystal_inspection/math/trusted_reference_comparison.json";

const cubic: RenderLattice["matrix"] = [[10,0,0],[0,10,0],[0,0,10]];

describe("periodic lattice mathematics", () => {
  it("uses row lattice vectors and round-trips fractional/cartesian coordinates", () => {
    const triclinic: RenderLattice["matrix"] = [[4,0,0],[1,3,0],[0.5,0.25,2]];
    const frac: RenderVector3 = [0.2,0.3,0.4];
    const cartesian = fractionalToCartesian(frac,triclinic);
    expect(cartesian[0]).toBeCloseTo(1.3,10);
    expect(cartesian[1]).toBeCloseTo(1,10);
    expect(cartesian[2]).toBeCloseTo(0.8,10);
    expect(cartesianToFractional(fractionalToCartesian(frac,triclinic),triclinic)).toEqual(expect.arrayContaining(frac.map((value)=>expect.closeTo(value,10))));
    expect(determinant(triclinic)).toBeCloseTo(24,10);
    expect(inverseLattice(triclinic)).toHaveLength(3);
  });

  it("solves an orthogonal boundary crossing and returns the target image", () => {
    const result=minimumImage([0.98,0,0],[0.02,0,0],cubic);
    expect(result.ok).toBe(true);
    if(result.ok){ expect(result.result.distance).toBeCloseTo(0.4,10); expect(result.result.imageOffset).toEqual([1,0,0]); }
  });

  it("searches beyond component-wise wrapping for a skewed lattice", () => {
    const skewed: RenderLattice["matrix"]=[[1,0,0],[0.9,0.2,0],[0,0,1]];
    const result=minimumImage([0,0,0],[0.49,0.49,0],skewed);
    expect(result.ok).toBe(true);
    if(result.ok){ expect(result.result.imageOffset).toEqual([0,-1,0]); expect(result.result.distance).toBeCloseTo(Math.hypot(0.031,0.102),10); }
  });

  it("matches trusted orthogonal, skewed and triclinic pymatgen references", () => {
    for (const item of reference.cases) {
      const result = minimumImage(item.source_fractional as unknown as RenderVector3, item.target_fractional as unknown as RenderVector3, item.lattice as unknown as RenderLattice["matrix"]);
      expect(result.ok).toBe(true);
      if (result.ok) { expect(result.result.distance).toBeCloseTo(item.distance, 10); expect(result.result.imageOffset).toEqual(item.image_offset); }
    }
  });

  it("uses deterministic lexicographic tie breaking", () => {
    const result=minimumImage([0,0,0],[0.5,0,0],cubic);
    expect(result.ok && result.result.imageOffset).toEqual([-1,0,0]);
  });

  it("rejects singular, ill-conditioned and non-finite lattices", () => {
    expect(minimumImage([0,0,0],[0.2,0,0],[[1,0,0],[2,0,0],[0,0,1]])).toEqual({ok:false,error:"PERIODIC_LATTICE_SINGULAR"});
    expect(minimumImage([0,0,0],[0.2,0,0],[[1,0,0],[0,1e-10,0],[0,0,1]])).toEqual({ok:false,error:"PERIODIC_LATTICE_ILL_CONDITIONED"});
    expect(minimumImage([0,0,0],[Number.NaN,0,0],cubic)).toEqual({ok:false,error:"PERIODIC_COORDINATE_INVALID"});
  });

  it("translates periodic refs and rejects unsafe offsets", () => {
    expect(translateCartesian([1,2,3],[-1,1,0],cubic)).toEqual([-9,12,3]);
    expect(periodicSiteKey({siteIndex:2,imageOffset:[-1,0,1]})).toBe("2:-1:0:1");
    expect(()=>periodicSiteKey({siteIndex:2,imageOffset:[99,0,0]})).toThrow();
  });

  it("applies anchored periodic angle and chain-continuous dihedral rules", () => {
    const positions=new Map<number,RenderVector3>([[0,[0.98,0,0]],[1,[0.02,0,0]],[2,[0.02,0.1,0]],[3,[0.02,0.1,0.1]]]);
    const angle=periodicAngle({siteIndex:1,imageOffset:[0,0,0]},0,2,positions,cubic);
    expect(angle.ok && angle.value).toBeCloseTo(90,10);
    if(angle.ok) expect(angle.refs[0].imageOffset).toEqual([-1,0,0]);
    const dihedral=periodicDihedral({siteIndex:1,imageOffset:[0,0,0]},0,2,3,positions,cubic);
    expect(dihedral.ok && Math.abs(dihedral.value)).toBeCloseTo(90,10);
  });
});
