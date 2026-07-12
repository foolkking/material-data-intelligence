import { describe, expect, it } from "vitest";

import minimalScene from "../../../../../docs/phase10f/fixtures/viewer_scene_v1/valid_minimal_crystal.viewer_scene.v1.json";
import multiSpeciesScene from "../../../../../docs/phase10f/fixtures/viewer_scene_v1/valid_multi_species_crystal.viewer_scene.v1.json";
import optionalBondsScene from "../../../../../docs/phase10f/fixtures/viewer_scene_v1/valid_optional_bonds.viewer_scene.v1.json";
import { bondMetrics, cameraFrame, latticeEdges, sceneBounds } from "./viewerSceneRendererGeometry";
import { mapViewerSceneForRenderer } from "./viewerSceneRendererMapper";
import { periodicBoundaryScene } from "./viewerScenePeriodicBondTestFixture";

describe("viewer scene renderer mapper", () => {
  it("maps canonical sites, lattice, species colors, and bounded bonds deterministically", () => {
    const first = mapViewerSceneForRenderer(optionalBondsScene);
    const second = mapViewerSceneForRenderer(optionalBondsScene);
    expect(first).toEqual(second);
    expect(first.ok).toBe(true);
    if (!first.ok) return;
    expect(first.scene.atoms.map((atom) => atom.siteIndex)).toEqual([0, 1]);
    expect(first.scene.atoms[0]).toMatchObject({ element: "Si", occupancy: 1, fractionalPosition: [0, 0, 0] });
    expect(first.scene.source.filename).toBe("valid_optional_bonds.viewer_scene.v1.json");
    expect(first.scene.bonds.map((bond) => bond.id)).toEqual(["bond-0-1"]);
    expect(first.scene.lattice.matrix).toHaveLength(3);
    expect(Object.isFrozen(first.scene)).toBe(true);
    expect(Object.isFrozen(first.scene.atoms)).toBe(true);
  });

  it("uses deterministic renderer-owned fallback appearance for unsafe style hints", () => {
    const payload = structuredClone(multiSpeciesScene) as Record<string, any>;
    payload.scene.sites[0].style = { color: "red;background:url(x)", radius: -10, unknown_renderer_config: { nested: true } };
    const result = mapViewerSceneForRenderer(payload);
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.scene.atoms[0].color).toMatch(/^#[0-9a-f]{6}$/);
    expect(result.scene.atoms[0].radius).toBe(0.72);
    expect(result.scene.atoms[0]).not.toHaveProperty("unknown_renderer_config");
  });

  it("maps explicit cross-boundary endpoints without choosing a new image",()=>{
    const result=mapViewerSceneForRenderer(periodicBoundaryScene());
    expect(result.ok).toBe(true); if(!result.ok)return;
    expect(result.scene.contractVersion).toBe("viewer_scene.v2");
    expect(result.scene.bonds[0]).toMatchObject({fromRef:{siteIndex:0,imageOffset:[0,0,0]},toRef:{siteIndex:1,imageOffset:[1,0,0]},start:[9.8,0,0],end:[10.2,0,0],distanceAngstrom:0.4,source:"distance_cutoff",authoritative:false});
  });

  it("rejects periodic distance spoofing before mapping",()=>{
    const payload=periodicBoundaryScene(); payload.scene.bonds[0].distance_angstrom=9;
    const result=mapViewerSceneForRenderer(payload);
    expect(result.ok).toBe(false);
    expect(result.validation.errors).toContain("VIEWER_SCENE_PERIODIC_BOND_DISTANCE_MISMATCH");
  });

  it("rejects viewer_scene.v2 capability overclaims before consumption",()=>{
    const payload=periodicBoundaryScene(); payload.capabilities.trajectory=true;
    const result=mapViewerSceneForRenderer(payload);
    expect(result.ok).toBe(false);
    expect(result.validation.errors).toContain("VIEWER_SCENE_CAPABILITIES_INVALID");
  });

  it.each([
    ["duplicate site", (payload: any) => { payload.scene.sites[1].index = payload.scene.sites[0].index; }, "VIEWER_SCENE_SITE_INDEX_DUPLICATE"],
    ["invalid bond", (payload: any) => { payload.scene.bonds = [{ from: 0, to: 99 }]; }, "VIEWER_SCENE_BOND_ENDPOINT_INVALID"],
    ["NaN", (payload: any) => { payload.scene.sites[0].xyz[0] = Number.NaN; }, "VIEWER_SCENE_COORDINATE_NON_FINITE"],
    ["Infinity", (payload: any) => { payload.scene.lattice.vectors[0][0] = Number.POSITIVE_INFINITY; }, "VIEWER_SCENE_COORDINATE_NON_FINITE"],
    ["missing lattice", (payload: any) => { delete payload.scene.lattice; }, "VIEWER_SCENE_LATTICE_VECTOR_INVALID"],
    ["shader field", (payload: any) => { payload.scene.fake_shader = "void main(){}"; }, "VIEWER_SCENE_EXECUTABLE_FIELD"],
    ["external URL", (payload: any) => { payload.scene.resource = "https://invalid.example/texture.png"; }, "VIEWER_SCENE_FORBIDDEN_STRING_CONTENT"],
    ["HTML payload", (payload: any) => { payload.scene.html_payload = "<script>blocked</script>"; }, "VIEWER_SCENE_EXECUTABLE_FIELD"],
  ])("rejects %s before renderer mapping", (_label, mutate, expected) => {
    const payload = structuredClone(optionalBondsScene) as Record<string, any>;
    mutate(payload);
    const result = mapViewerSceneForRenderer(payload);
    expect(result.ok).toBe(false);
    expect(result.validation.errors).toContain(expected);
  });

  it("drops zero-length bonds without creating invalid geometry", () => {
    const payload = structuredClone(optionalBondsScene) as Record<string, any>;
    payload.scene.sites[1].xyz = [...payload.scene.sites[0].xyz];
    const result = mapViewerSceneForRenderer(payload);
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.scene.bonds).toEqual([]);
  });

  it("maps a contract-near-cap scene without unbounded growth", () => {
    const payload = structuredClone(minimalScene) as Record<string, any>;
    payload.scene.sites = Array.from({ length: 256 }, (_, index) => ({ index, element: index % 2 ? "Na" : "Cl", label: `site-${index}`, xyz: [index % 16, Math.floor(index / 16), (index % 7) * 0.1] }));
    payload.scene.bonds = Array.from({ length: 2048 }, (_, index) => ({ from: index % 256, to: (index + 1) % 256, distance: 1 }));
    payload.metadata.site_count = 256;
    payload.metadata.species_count = 2;
    payload.metadata.species = ["Cl", "Na"];
    const started = performance.now();
    const result = mapViewerSceneForRenderer(payload);
    const elapsed = performance.now() - started;
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.scene.atoms).toHaveLength(256);
    expect(result.scene.bonds).toHaveLength(2048);
    expect(elapsed).toBeLessThan(1000);
  });

  it("refuses a scene above the aligned renderer and canonical site cap", () => {
    const payload = structuredClone(minimalScene) as Record<string, any>;
    payload.scene.sites = Array.from({ length: 257 }, (_, index) => ({ index, element: "Si", label: `site-${index}`, xyz: [index, 0, 0] }));
    payload.metadata.site_count = 257;
    const result = mapViewerSceneForRenderer(payload);
    expect(result.ok).toBe(false);
    expect(result.validation.errors).toContain("VIEWER_SCENE_SITE_LIMIT_EXCEEDED");
  });
});

describe("viewer scene renderer geometry", () => {
  it("calculates twelve deterministic lattice edges and stable camera bounds", () => {
    const mapped = mapViewerSceneForRenderer(minimalScene);
    expect(mapped.ok).toBe(true);
    if (!mapped.ok) return;
    expect(latticeEdges(mapped.scene.lattice.matrix)).toHaveLength(12);
    const bounds = sceneBounds(mapped.scene);
    const frame = cameraFrame(mapped.scene);
    expect(bounds.radius).toBeGreaterThan(0);
    expect(frame.near).toBeGreaterThan(0);
    expect(frame.far).toBeGreaterThan(frame.near);
    expect(frame.target).toEqual(bounds.center);
  });

  it("computes bond midpoint, direction, and length", () => {
    const mapped = mapViewerSceneForRenderer(optionalBondsScene);
    expect(mapped.ok).toBe(true);
    if (!mapped.ok) return;
    const metrics = bondMetrics(mapped.scene.bonds[0]);
    expect(metrics.length).toBeGreaterThan(0);
    expect(metrics.midpoint).toHaveLength(3);
    expect(Math.hypot(...metrics.direction)).toBeCloseTo(1);
  });
});
