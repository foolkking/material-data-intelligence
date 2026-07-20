import fixture from "../../../../../docs/phase10j/fixtures/volumetric_contract/cubic_constant_scalar.json";
import { describe, expect, it } from "vitest";
import { mapVolumetricStructureOverlay } from "./volumetricOverlayMapper";
import { validateVolumetricArtifacts } from "./volumetricValidation";

const validation = validateVolumetricArtifacts(fixture.raw_dataset, fixture.manifest);
if (!validation.ok) throw new Error("fixture must validate");
const hash = "a".repeat(64);
const overlay = {
  schema_version: "phase10j2.volumetric_structure_overlay.v1", overlay_id: `volume-overlay:${hash}`,
  grid_id: validation.bundle.grid.gridId, grid_content_hash: validation.bundle.grid.contentHash,
  kind: "periodic_viewer_scene", viewer_scene: null, atom_records: [], unavailable_reason: "periodic_structure_overlay_unavailable",
  security: { contains_css:false, contains_executable:false, contains_html:false, contains_javascript:false, contains_shader:false, external_urls_allowed:false, renderer_included:false }, content_hash: hash,
};

describe("volumetric structure overlay mapper", () => {
  it("preserves unavailable periodic identity without fabricating atoms", () => {
    const result = mapVolumetricStructureOverlay(overlay, validation.bundle);
    expect(result).toMatchObject({ ok:true, overlay:{ kind:"periodic_viewer_scene", atoms:[], unavailableReason:"periodic_structure_overlay_unavailable" } });
  });
  it("rejects content identity, URL, and security escalation", () => {
    expect(mapVolumetricStructureOverlay({ ...overlay, overlay_id:"volume-overlay:"+"b".repeat(64) }, validation.bundle)).toMatchObject({ ok:false });
    expect(mapVolumetricStructureOverlay({ ...overlay, unavailable_reason:"https://example.invalid" }, validation.bundle)).toMatchObject({ ok:false });
    expect(mapVolumetricStructureOverlay({ ...overlay, security:{ ...overlay.security, renderer_included:true } }, validation.bundle)).toMatchObject({ ok:false });
  });
});
