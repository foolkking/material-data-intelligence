import fixture from "../../../../../docs/phase10j/fixtures/volumetric_contract/cubic_constant_scalar.json";
import { describe, expect, it } from "vitest";

import { validateVolumetricArtifacts } from "./volumetricValidation";

describe("Phase 10J-2 volumetric compatibility gate", () => {
  it("maps the canonical Phase 10J dataset and manifest immutably", () => {
    const result=validateVolumetricArtifacts(fixture.raw_dataset,fixture.manifest);
    expect(result.ok).toBe(true);
    if(!result.ok)return;
    expect(result.bundle.grid.shape).toEqual([4,4,4]);
    expect(result.bundle.fields).toHaveLength(1);
    expect(result.bundle.fields[0].supported).toBe(true);
    expect(Object.isFrozen(result.bundle)).toBe(true);
  });

  it("rejects unknown executable metadata before Worker or WebGL", () => {
    const dataset=structuredClone(fixture.raw_dataset) as Record<string,unknown>;
    (dataset as Record<string,unknown>).shader="artifact supplied";
    expect(validateVolumetricArtifacts(dataset,fixture.manifest)).toMatchObject({ok:false,errors:["VOLUME_DATASET_SCHEMA_INVALID"]});
  });

  it("keeps an otherwise valid non-scalar field out of the isosurface path", () => {
    const dataset=structuredClone(fixture.raw_dataset);
    dataset.fields[0].value_kind="complex";
    dataset.fields[0].stored_component_count=2;
    const result=validateVolumetricArtifacts(dataset,fixture.manifest);
    expect(result.ok).toBe(true);
    if(result.ok)expect(result.bundle.fields[0].reasons).toContain("real_scalar_required");
  });

  it("rejects manifest capability escalation", () => {
    const manifest=structuredClone(fixture.manifest);
    manifest.capabilities.renderer_included=true;
    const result=validateVolumetricArtifacts(fixture.raw_dataset,manifest);
    expect(result).toMatchObject({ok:false,errors:expect.arrayContaining(["VOLUME_MANIFEST_SECURITY_INVALID"])});
  });
});
