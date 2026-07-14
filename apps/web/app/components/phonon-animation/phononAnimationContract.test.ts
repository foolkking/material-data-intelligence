import {describe,expect,it} from "vitest";
import {animationDisplacements,validatePhononAnimation} from "./phononAnimationContract";
import {mapPhononAnimationFrame} from "./phononAnimationMapper";
import {phononAnimationFixture} from "./phononAnimationTestFixture";

describe("phonon animation contract and mapper",()=>{
  it("validates the closed inert package",()=>{expect(validatePhononAnimation(phononAnimationFixture())).toEqual({valid:true,errors:[]});});
  it("matches non-Gamma replica phase and 2pi periodicity",()=>{const value=phononAnimationFixture();const origin=animationDisplacements(value,0,[0,0,0]);const replica=animationDisplacements(value,0,[1,0,0]);const full=animationDisplacements(value,2*Math.PI,[0,0,0]);expect(replica[0][0]).toBeCloseTo(-origin[0][0],10);expect(full[0][0]).toBeCloseTo(origin[0][0],10);});
  it("allows the zero displacement quarter-cycle node",()=>{const vectors=animationDisplacements(phononAnimationFixture(),Math.PI/2,[0,0,0]);expect(Math.max(...vectors.flat().map(Math.abs))).toBeLessThan(1e-10);});
  it("preserves periodic identity and reference/current positions",()=>{const mapped=mapPhononAnimationFrame(phononAnimationFixture(),0);expect(mapped.scene.atoms).toHaveLength(4);expect(mapped.scene.atoms.map((atom)=>atom.ref)).toContainEqual({siteIndex:0,imageOffset:[1,0,0]});expect(mapped.scene.atoms[0].position[0]-mapped.scene.atoms[0].canonicalPosition[0]).toBeCloseTo(.15,10);expect(mapped.vectors).toHaveLength(4);expect(mapped.scene.bonds).toHaveLength(2);});
  it("rejects noncommensurate, malformed, and executable payloads",()=>{const noncommensurate=structuredClone(phononAnimationFixture());noncommensurate.supercell.repeat=[1,1,1];noncommensurate.supercell.displayed_atom_count=2;expect(validatePhononAnimation(noncommensurate).errors).toContain("PHONON_ANIMATION_NONCOMMENSURATE");const unsafe=structuredClone(phononAnimationFixture());unsafe.structure.formula="<script>alert(1)</script>";expect(validatePhononAnimation(unsafe).errors).toContain("PHONON_ANIMATION_EXTERNAL_CONTENT_FORBIDDEN");const callback=structuredClone(phononAnimationFixture()) as any;callback.callback="evil";expect(validatePhononAnimation(callback).valid).toBe(false);});
});
