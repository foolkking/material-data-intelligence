import fixture from "../../../../../tests/fixtures/volumetric_contract/cubic_constant_scalar.json";
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

  it("rejects relationship metadata that is not backed by derived collinear channels", () => {
    const dataset=structuredClone(fixture.raw_dataset);
    (dataset as { relationships: unknown[] }).relationships=[{relationship_id:"collinear:total_equals_up_plus_down:v1",kind:"total_equals_up_plus_down",input_field_ids:[dataset.fields[0].field_id,dataset.fields[0].field_id],output_field_id:dataset.fields[0].field_id,status:"validated",residual:0}];
    expect(validateVolumetricArtifacts(dataset,fixture.manifest)).toMatchObject({ok:false,errors:expect.arrayContaining(["VOLUME_RELATIONSHIP_INVALID"])});
  });

  it("accepts valid non-uniform boundaries but marks the renderer unsupported", () => {
    const dataset=structuredClone(fixture.raw_dataset);
    dataset.grid.boundary_conditions=["periodic","non_periodic","periodic"];
    const result=validateVolumetricArtifacts(dataset,fixture.manifest);
    expect(result.ok).toBe(true);
    if(result.ok) {
      expect(result.bundle.grid.boundaryConditions).toEqual(["periodic","non_periodic","periodic"]);
      expect(result.bundle.fields[0].supported).toBe(false);
      expect(result.bundle.fields[0].reasons).toContain("mixed_boundary_conditions_unsupported");
    }
  });

  it("distinguishes damaged boundaries and out-of-range inline data as invalid", () => {
    const damaged=structuredClone(fixture.raw_dataset);
    damaged.grid.boundary_conditions=["periodic","broken","periodic"];
    expect(validateVolumetricArtifacts(damaged,fixture.manifest)).toMatchObject({
      ok:false, errors:expect.arrayContaining(["VOLUME_GRID_SCHEMA_INVALID"]),
    });

    const outOfRange=structuredClone(fixture.raw_dataset);
    const inlinePayload=outOfRange.payloads[0] as { encoding: string; inline_values: number[] | null; artifact_name: string | null };
    inlinePayload.encoding="inline_json";
    const inlineValues = Array.from({ length: 64 }, () => 2);
    inlinePayload.inline_values=inlineValues;
    inlinePayload.artifact_name=null;
    inlineValues[0]=99;
    expect(validateVolumetricArtifacts(outOfRange,fixture.manifest)).toMatchObject({
      ok:false, errors:expect.arrayContaining(["VOLUME_PAYLOAD_DATA_INVALID"]),
    });
  });
});
