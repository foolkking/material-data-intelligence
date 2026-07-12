import { describe, expect, it } from "vitest";

import minimalScene from "../../../../../docs/phase10f/fixtures/viewer_scene_v1/valid_minimal_crystal.viewer_scene.v1.json";
import { mapViewerSceneForRenderer } from "./viewerSceneRendererMapper";
import { derivePeriodicSupercell, supercellOffsets } from "./viewerSceneSupercell";

function scene() { const mapped=mapViewerSceneForRenderer(minimalScene); if(!mapped.ok) throw new Error("fixture invalid"); return mapped.scene; }

describe("bounded periodic supercell derivation", () => {
  it("generates deterministic positive offsets",()=>expect(supercellOffsets([2,2,1])).toEqual([[0,0,0],[0,1,0],[1,0,0],[1,1,0]]));

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

  it("rejects invalid repeats and over-cap derived scenes without truncation",()=>{
    expect(derivePeriodicSupercell(scene(),[4,1,1]).ok).toBe(false);
    const canonical=scene();
    const atoms=Array.from({length:256},(_,index)=>Object.freeze({...canonical.atoms[0],siteIndex:index,ref:Object.freeze({siteIndex:index,imageOffset:Object.freeze([0,0,0] as const)}),id:`site-${index}`}));
    const large=Object.freeze({...canonical,atoms:Object.freeze(atoms)});
    const result=derivePeriodicSupercell(large,[3,3,3]);
    expect(result).toMatchObject({ok:false,error:"PERIODIC_DERIVED_SITE_LIMIT_EXCEEDED",requestedSites:6912});
  });
});
