import { describe, expect, it } from "vitest";
import { buildChargeSpinDensityProduct } from "./chargeSpinDensityProduct";
import type { ValidatedVolumetricBundle, ValidatedVolumetricField, ValidatedVolumetricRelationship } from "./volumetricViewerTypes";

const hash = "a".repeat(64);

function field(name:string, quantity:string, integral:number, channel:ValidatedVolumetricField["spin"] extends infer S ? S : never = null, minimum=0, maximum=8):ValidatedVolumetricField {
  return Object.freeze({ schemaVersion:"phase10j.volumetric_field.v1",fieldId:`field:${name}`,fieldName:name,gridId:"grid",payloadId:`payload:${name}`,quantity,valueKind:"real",fieldRank:"scalar",storedComponentCount:1,unit:quantity==="magnetization_density"?"bohr_magneton/angstrom^3":quantity==="charge_density"?"elementary_charge/angstrom^3":"electron/angstrom^3",sourceUnit:"electron/angstrom^3",normalizationSemantics:"source_native",integralSemantics:quantity==="magnetization_density"?"magnetic_moment":quantity==="charge_density"?"elementary_charge":"electron_count",spin:channel,potentialReference:null,provenance:{sourceSha256:hash,producer:"mdi_volumetric_adapter",producerVersion:"1.1.0",transformations:[]},minimum,maximum,mean:1,standardDeviation:1,rms:1,integral,warnings:[],contentHash:hash });
}

function spin(channel:NonNullable<ValidatedVolumetricField["spin"]>["channel"]):NonNullable<ValidatedVolumetricField["spin"]>{return Object.freeze({representation:"collinear",channel,signConvention:"up minus down",sourceConvention:"validated VASP collinear source"});}

function bundle(fields:readonly ValidatedVolumetricField[],relationships:readonly ValidatedVolumetricRelationship[]=[],warnings:readonly string[]=[]):ValidatedVolumetricBundle {
  return {datasetId:"dataset",datasetContentHash:hash,sourceFormat:"vasp_volumetric",sourceSha256:hash,grid:{schemaVersion:"phase10j.volumetric_grid.v1",gridId:"grid",contentHash:hash,shape:[2,2,2],origin:[0,0,0],stepMatrix:[[1,0,0],[0,1,0],[0,0,1]],sampleLocation:"node",boundaryConditions:["periodic","periodic","periodic"],endpointPolicy:"excluded",periodic:true,structureBinding:null},fields:fields.map((item)=>({field:item,payload:{schemaVersion:"phase10j.volumetric_payload.v1",payloadId:item.payloadId,encoding:"raw_binary",dtype:"float64",gridShape:[2,2,2],valueCount:8,uncompressedBytes:64,compressedBytes:64,logicalSha256:hash,storageSha256:hash,artifactName:"field.f64",inlineValues:null,chunks:[]},supported:true,reasons:[]})),relationships,warnings,manifestContentHash:hash,artifactNames:[]};
}

describe("charge/spin density product model",()=>{
  it("separates electron density from signed electric charge",()=>{
    const electron=buildChargeSpinDensityProduct(bundle([field("total","electron_density",36)]));
    expect(electron).toMatchObject({kind:"electron_density",status:"ready"});
    expect(electron.integralRows[0]).toMatchObject({unit:"electron",interpretation:"electron_count"});
    const charge=buildChargeSpinDensityProduct(bundle([field("charge","charge_density",-2,null,-2,3)]));
    expect(charge).toMatchObject({kind:"signed_charge_density",status:"ready"});
    expect(charge.integralRows[0]).toMatchObject({unit:"elementary_charge",interpretation:"elementary_charge"});
  });

  it("requires both validated relationships before declaring derived collinear channels",()=>{
    const total=field("total","electron_density",36);
    const difference=field("spin_difference","magnetization_density",4.5,spin("spin_difference"),-1,1);
    const up=field("spin_up","spin_density",20.25,spin("spin_up"));
    const down=field("spin_down","spin_density",15.75,spin("spin_down"));
    const relationship=(kind:ValidatedVolumetricRelationship["kind"],output:string):ValidatedVolumetricRelationship=>({relationshipId:kind,kind,inputFieldIds:[up.fieldId,down.fieldId],outputFieldId:output,status:"validated",residual:0});
    const product=buildChargeSpinDensityProduct(bundle([total,difference,up,down],[relationship("spin_difference_equals_up_minus_down",difference.fieldId),relationship("total_equals_up_plus_down",total.fieldId)]));
    expect(product.kind).toBe("collinear_spin");
    expect(product.formulaIds).toEqual(["COLLINEAR_SPIN_UP_V1","COLLINEAR_SPIN_DOWN_V1"]);
    expect(product.modeFieldIds).toEqual({total:total.fieldId,spin_difference:difference.fieldId,spin_up:up.fieldId,spin_down:down.fieldId});
    expect(product.defaultFieldId).toBe(difference.fieldId);
    expect(buildChargeSpinDensityProduct(bundle([total,difference,up,down])).warnings).toContain("VOLUME_COLLINEAR_DERIVED_FIELDS_UNAVAILABLE");
  });

  it("reports augmentation and electron sign anomalies without clipping",()=>{
    const product=buildChargeSpinDensityProduct(bundle([field("total","electron_density",1,null,-0.1,2)],[],["VOLUME_VASP_AUGMENTATION_NOT_INCLUDED"]));
    expect(product.augmentationIncluded).toBe(false);
    expect(product.warnings).toContain("VOLUME_ELECTRON_DENSITY_SIGNIFICANT_NEGATIVE");
  });

  it("keeps unknown scalar quantities in the generic renderer only",()=>{
    expect(buildChargeSpinDensityProduct(bundle([field("scalar","generic_scalar",0)])).kind).toBe("unavailable");
  });
});
