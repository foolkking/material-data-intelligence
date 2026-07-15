import { describe, expect, it } from "vitest";

import bccManifest from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/bcc/manifest.json";
import bccReciprocal from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/bcc/reciprocal_lattice.json";
import bccZone from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/bcc/brillouin_zone.json";
import bccKpath from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/bcc/kpath.json";
import fccManifest from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/fcc/manifest.json";
import fccReciprocal from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/fcc/reciprocal_lattice.json";
import fccZone from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/fcc/brillouin_zone.json";
import fccKpath from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/fcc/kpath.json";
import hexManifest from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/hexagonal/manifest.json";
import hexReciprocal from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/hexagonal/reciprocal_lattice.json";
import hexZone from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/hexagonal/brillouin_zone.json";
import hexKpath from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/hexagonal/kpath.json";
import scManifest from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/simple_cubic/manifest.json";
import scReciprocal from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/simple_cubic/reciprocal_lattice.json";
import scZone from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/simple_cubic/brillouin_zone.json";
import scKpath from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/simple_cubic/kpath.json";
import triManifest from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/triclinic/manifest.json";
import triReciprocal from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/triclinic/reciprocal_lattice.json";
import triZone from "../../../../../docs/phase10i/fixtures/brillouin_zone_v1/triclinic/brillouin_zone.json";
import { mapBrillouinZoneArtifacts } from "./brillouinZoneMapper";

const cases = [
  ["simple cubic", scReciprocal, scZone, scKpath, scManifest],
  ["BCC", bccReciprocal, bccZone, bccKpath, bccManifest],
  ["FCC", fccReciprocal, fccZone, fccKpath, fccManifest],
  ["hexagonal", hexReciprocal, hexZone, hexKpath, hexManifest],
] as const;

describe("Brillouin zone renderer mapper", () => {
  it.each(cases)("maps validated %s artifacts without recomputing reciprocal geometry", (_name, reciprocal, zone, kpath, manifest) => {
    const result = mapBrillouinZoneArtifacts({ reciprocal, zone, kpath, manifest });
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.scene.convention).toBe("physics_2pi");
    expect(result.scene.units).toBe("angstrom^-1");
    expect(result.scene.vertices.map((item) => item.id)).toEqual(zone.vertices.map((item) => item.vertex_id));
    expect(result.scene.edges.map((item) => item.id)).toEqual(zone.edges.map((item) => item.edge_id));
    expect(result.scene.faces.reduce((sum,item)=>sum+item.triangleVertexIndices.length/3,0)).toBe(zone.faces.reduce((sum,item)=>sum+item.vertex_ids.length-2,0));
    expect(result.scene.visualScale).toBeGreaterThan(0);
  });

  it("maps a validated triclinic zone without a k-path and reports the explicit unavailable state", () => {
    const manifest = structuredClone(triManifest) as Record<string, unknown>;
    manifest.artifacts = (manifest.artifacts as Array<{name:string}>).filter((item)=>item.name!=="kpath.json");
    const capabilities = manifest.capabilities as Record<string, unknown>;
    capabilities.high_symmetry_kpath = false;
    const result = mapBrillouinZoneArtifacts({ reciprocal: triReciprocal, zone: triZone, manifest });
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.scene.points).toHaveLength(0);
    expect(result.warnings).toContain("BZ_KPATH_UNAVAILABLE");
  });

  it("rejects hash, convention, topology, numeric, security and cap failures before rendering", () => {
    const invalidHash = structuredClone(scManifest); invalidHash.artifacts[1].sha256 = "f".repeat(64);
    expect(mapBrillouinZoneArtifacts({reciprocal:scReciprocal,zone:scZone,kpath:scKpath,manifest:invalidHash})).toMatchObject({ok:false,code:"BZ_RENDERER_VALIDATION_FAILED"});
    const invalidUnit = structuredClone(scReciprocal); invalidUnit.units = "nanometer^-1";
    expect(mapBrillouinZoneArtifacts({reciprocal:invalidUnit,zone:scZone,kpath:scKpath,manifest:scManifest})).toMatchObject({ok:false});
    const invalidFace = structuredClone(scZone); invalidFace.faces[0].vertex_ids[0] = "missing";
    expect(mapBrillouinZoneArtifacts({reciprocal:scReciprocal,zone:invalidFace,kpath:scKpath,manifest:scManifest})).toMatchObject({ok:false});
    const nonFinite = structuredClone(scZone); nonFinite.vertices[0].cartesian_coordinates[0] = Number.NaN;
    expect(mapBrillouinZoneArtifacts({reciprocal:scReciprocal,zone:nonFinite,kpath:scKpath,manifest:scManifest})).toMatchObject({ok:false});
    const injected = structuredClone(scKpath) as typeof scKpath & {shader?:string}; injected.shader = "void main(){}";
    expect(mapBrillouinZoneArtifacts({reciprocal:scReciprocal,zone:scZone,kpath:injected,manifest:scManifest})).toMatchObject({ok:false});
    const overCap = structuredClone(scZone); overCap.vertices = Array.from({length:257},()=>overCap.vertices[0]);
    expect(mapBrillouinZoneArtifacts({reciprocal:scReciprocal,zone:overCap,kpath:scKpath,manifest:scManifest})).toMatchObject({ok:false,code:"BZ_RENDERER_RESOURCE_LIMIT"});
  });

  it("does not mutate unknown executable fields into renderer state", () => {
    const payload = structuredClone(scZone) as typeof scZone & {renderer?:{module:string}};
    payload.renderer = {module:"https://example.test/renderer.js"};
    const before = JSON.stringify(payload);
    const result = mapBrillouinZoneArtifacts({reciprocal:scReciprocal,zone:payload,kpath:scKpath,manifest:scManifest});
    expect(result.ok).toBe(false);
    expect(JSON.stringify(payload)).toBe(before);
  });
});
