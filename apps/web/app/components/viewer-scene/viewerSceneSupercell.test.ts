import { describe, expect, it } from "vitest";

import minimalScene from "../../../../../tests/fixtures/viewer_scene_v1/valid_minimal_crystal.viewer_scene.v1.json";
import { mapViewerSceneForRenderer } from "./viewerSceneRendererMapper";
import { derivePeriodicSupercell, estimatePeriodicSupercell, supercellOffsets, validSupercellRepeat } from "./viewerSceneSupercell";
import { periodicBoundaryScene } from "./viewerScenePeriodicBondTestFixture";

function scene() { const mapped=mapViewerSceneForRenderer(minimalScene); if(!mapped.ok) throw new Error("fixture invalid"); return mapped.scene; }

describe("bounded periodic supercell derivation", () => {
  it("generates deterministic positive offsets",()=>expect(supercellOffsets([2,2,1])).toEqual([[0,0,0],[0,1,0],[1,0,0],[1,1,0]]));

  it("strictly validates expansion without coercion",()=>{
    expect(validSupercellRepeat([2,2,1])).toBe(true);
    for (const invalid of [[0,1,1],[-1,1,1],[1.5,1,1],["2",1,1],[4,1,1],[Number.NaN,1,1],[Number.POSITIVE_INFINITY,1,1]]) expect(validSupercellRepeat(invalid)).toBe(false);
  });

  it("preflights interactive, degraded, and refused budgets before allocation",()=>{
    expect(estimatePeriodicSupercell(scene(),[2,2,2])).toMatchObject({totalCells:8,displayedAtoms:8,mode:"interactive",error:null});
    const canonical=scene();
    const atoms=Array.from({length:64},(_,index)=>Object.freeze({...canonical.atoms[0],siteIndex:index,ref:Object.freeze({siteIndex:index,imageOffset:Object.freeze([0,0,0] as const)}),id:`site-${index}`}));
    expect(estimatePeriodicSupercell(Object.freeze({...canonical,atoms:Object.freeze(atoms)}),[3,3,1])).toMatchObject({displayedAtoms:576,mode:"interactive"});
    const maxAtoms=Array.from({length:256},(_,index)=>Object.freeze({...canonical.atoms[0],siteIndex:index,ref:Object.freeze({siteIndex:index,imageOffset:Object.freeze([0,0,0] as const)}),id:`site-${index}`}));
    expect(estimatePeriodicSupercell(Object.freeze({...canonical,atoms:Object.freeze(maxAtoms)}),[2,2,2])).toMatchObject({displayedAtoms:2048,mode:"degraded",warnings:["VIEWER_SUPERCELL_DEGRADED_MODE"]});
    expect(estimatePeriodicSupercell(Object.freeze({...canonical,atoms:Object.freeze(maxAtoms)}),[3,3,3])).toMatchObject({displayedAtoms:6912,mode:"refused",error:"VIEWER_SUPERCELL_ATOM_BUDGET_EXCEEDED"});
  });

  it.each([[[1,1,1],1],[[2,2,2],8],[[3,3,3],27]] as const)("derives %j without mutating the canonical scene",(repeat,multiplier)=>{
    const canonical=scene(); const result=derivePeriodicSupercell(canonical,repeat);
    expect(result.ok).toBe(true); if(!result.ok)return;
    expect(result.scene.atoms).toHaveLength(canonical.atoms.length*multiplier);
    expect(result.scene.supercellRepeat).toEqual(repeat);
    expect(canonical.atoms).toHaveLength(1);
    expect(new Set(result.scene.atoms.map((atom)=>`${atom.ref.siteIndex}:${atom.ref.imageOffset.join(":")}`)).size).toBe(result.scene.atoms.length);
  });

  it("replicates only provable same-cell bonds with periodic endpoint refs",()=>{
    const canonical=scene(); const result=derivePeriodicSupercell(canonical,[2,1,1]);
    expect(result.ok).toBe(true); if(!result.ok)return;
    expect(result.scene.bonds).toHaveLength(canonical.bonds.length*2);
    expect(result.scene.bonds.every((bond)=>bond.fromRef.imageOffset.join()===bond.toRef.imageOffset.join())).toBe(true);
  });

  it("adds bounded selected-site neighbor images",()=>{
    const result=derivePeriodicSupercell(scene(),[1,1,1],0);
    expect(result.ok).toBe(true); if(!result.ok)return;
    expect(result.scene.atoms).toHaveLength(27);
  });

  it.each([0, 1])("shows the full neighbor endpoints of canonical site %s without unrelated copies", index => {
    const mapped = mapViewerSceneForRenderer(periodicBoundaryScene());
    if (!mapped.ok) throw new Error("fixture invalid");
    const before = JSON.stringify(mapped.scene);
    const result = derivePeriodicSupercell(mapped.scene, [1, 1, 1], { mode: "neighbors", center: { siteIndex: index, imageOffset: [0, 0, 0] } });
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.scene.atoms).toHaveLength(3);
    expect(result.scene.bonds).toHaveLength(1);
    const bond = result.scene.bonds[0];
    expect(Math.hypot(...bond.displacementCartesian)).toBeCloseTo(0.4);
    expect(bond.distanceAngstrom).toBe(0.4);
    expect(result.scene.atoms.some(atom => atom.siteIndex === 1 - index && atom.ref.imageOffset[0] === (index ? -1 : 1))).toBe(true);
    expect(JSON.stringify(mapped.scene)).toBe(before);
  });

  it("retains both directions of a periodic self-neighbor", () => {
    const mapped = mapViewerSceneForRenderer(periodicBoundaryScene());
    if (!mapped.ok) throw new Error("fixture invalid");
    const first = mapped.scene.atoms[0];
    const canonical = { ...mapped.scene, atoms: [first], bonds: [{ ...mapped.scene.bonds[0],
      toSiteIndex: 0, toRef: { siteIndex: 0, imageOffset: [1, 0, 0] as const },
      start: first.position, end: [19.8, 0, 0] as const, distanceAngstrom: 10, displacementCartesian: [10, 0, 0] as const }] };
    const result = derivePeriodicSupercell(canonical, [1, 1, 1], { mode: "neighbors", center: { siteIndex: 0, imageOffset: [0, 0, 0] } });
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.scene.atoms).toHaveLength(3);
    expect(result.scene.bonds).toHaveLength(2);
    expect(result.scene.bonds.map(bond => bond.toRef.imageOffset[0]).sort()).toEqual([-1, 1]);
    expect(result.scene.bonds.every(bond => Math.abs(Math.hypot(...bond.displacementCartesian) - 10) < 1e-8)).toBe(true);
  });

  it("restores an exact boundary image without growing another shell and rejects unbounded neighborhoods", () => {
    const mapped = mapViewerSceneForRenderer(periodicBoundaryScene());
    if (!mapped.ok) throw new Error("fixture invalid");
    const center = { siteIndex: 0, imageOffset: [3, 0, 0] as const };
    const image = derivePeriodicSupercell(mapped.scene, [1, 1, 1], { mode: "image", center });
    expect(image.ok).toBe(true);
    if (!image.ok) return;
    expect(image.scene.atoms).toHaveLength(3);
    expect(image.scene.atoms.some(atom => atom.siteIndex === 0 && atom.ref.imageOffset[0] === 3)).toBe(true);
    expect(derivePeriodicSupercell(mapped.scene, [1, 1, 1], { mode: "neighbors", center })).toMatchObject({ ok: false, error: "PERIODIC_NEIGHBOR_IMAGE_LIMIT_EXCEEDED" });
  });

  it("replicates complete cross-boundary edges without floating or duplicate bonds",()=>{
    const mapped=mapViewerSceneForRenderer(periodicBoundaryScene()); if(!mapped.ok)throw new Error("fixture invalid");
    const one=derivePeriodicSupercell(mapped.scene,[1,1,1]); expect(one.ok).toBe(true); if(one.ok)expect(one.scene.bonds).toHaveLength(0);
    const two=derivePeriodicSupercell(mapped.scene,[2,1,1]); expect(two.ok).toBe(true); if(!two.ok)return;
    expect(two.scene.bonds).toHaveLength(1);
    expect(two.scene.bonds[0]).toMatchObject({fromRef:{siteIndex:0,imageOffset:[0,0,0]},toRef:{siteIndex:1,imageOffset:[1,0,0]}});
    expect(new Set(two.scene.bonds.map((bond)=>bond.id)).size).toBe(two.scene.bonds.length);
  });

  it("rejects invalid repeats and over-cap derived scenes without truncation",()=>{
    expect(derivePeriodicSupercell(scene(),[4,1,1]).ok).toBe(false);
    const canonical=scene();
    const atoms=Array.from({length:256},(_,index)=>Object.freeze({...canonical.atoms[0],siteIndex:index,ref:Object.freeze({siteIndex:index,imageOffset:Object.freeze([0,0,0] as const)}),id:`site-${index}`}));
    const large=Object.freeze({...canonical,atoms:Object.freeze(atoms)});
    const result=derivePeriodicSupercell(large,[3,3,3]);
    expect(result).toMatchObject({ok:false,error:"PERIODIC_DERIVED_SITE_LIMIT_EXCEEDED",requestedSites:6912});
  });
});
