import type { ValidatedVolumetricBundle, ValidatedVolumetricField } from "./volumetricViewerTypes";

export type ChargeSpinProductKind = "electron_density" | "signed_charge_density" | "collinear_spin" | "non_collinear" | "unavailable";

export type ChargeSpinDensityProduct = Readonly<{
  kind: ChargeSpinProductKind;
  title: string;
  status: "ready" | "deferred" | "unavailable";
  defaultFieldId: string | null;
  modeFieldIds: Readonly<Record<string, string>>;
  presets: readonly Readonly<{ id: "low" | "medium" | "high"; label: string; absoluteIsovalue: number }>[];
  warnings: readonly string[];
  augmentationIncluded: boolean;
  integralRows: readonly Readonly<{ fieldId: string; label: string; value: number; unit: string; interpretation: string }>[];
  formulaIds: readonly string[];
}>;

export function buildChargeSpinDensityProduct(bundle: ValidatedVolumetricBundle): ChargeSpinDensityProduct {
  const fields = bundle.fields.filter((item) => item.supported).map((item) => item.field);
  const byChannel = new Map(fields.filter((field) => field.spin).map((field) => [field.spin!.channel, field]));
  const total = fields.find((field) => field.quantity === "electron_density" && field.fieldName === "total") ?? fields.find((field) => field.quantity === "electron_density");
  const charge = fields.find((field) => field.quantity === "charge_density");
  const spin = byChannel.get("spin_difference");
  const up = byChannel.get("spin_up");
  const down = byChannel.get("spin_down");
  const vector = byChannel.get("magnetization_vector");
  const warnings = [...bundle.warnings];
  const augmentationIncluded = !warnings.includes("VOLUME_VASP_AUGMENTATION_NOT_INCLUDED");

  if (total && spin) {
    const relationshipKinds = new Set(bundle.relationships.filter((item) => item.status === "validated" && item.residual === 0).map((item) => item.kind));
    const derivedReady = Boolean(up && down && relationshipKinds.has("total_equals_up_plus_down") && relationshipKinds.has("spin_difference_equals_up_minus_down"));
    if (!derivedReady) warnings.push("VOLUME_COLLINEAR_DERIVED_FIELDS_UNAVAILABLE");
    const modes: Record<string, string> = { total: total.fieldId, spin_difference: spin.fieldId };
    if (up) modes.spin_up = up.fieldId;
    if (down) modes.spin_down = down.fieldId;
    return freeze({
      kind: "collinear_spin", title: "Collinear charge / spin density", status: "ready", defaultFieldId: spin.fieldId,
      modeFieldIds: modes, presets: presets(spin, true), warnings, augmentationIncluded,
      integralRows: integralRows([total, spin, ...(up && down ? [up, down] : [])]),
      formulaIds: derivedReady ? ["COLLINEAR_SPIN_UP_V1", "COLLINEAR_SPIN_DOWN_V1"] : [],
    });
  }
  if (charge) return freeze({ kind:"signed_charge_density", title:"Signed charge density", status:"ready", defaultFieldId:charge.fieldId, modeFieldIds:{ charge:charge.fieldId }, presets:presets(charge,true), warnings, augmentationIncluded, integralRows:integralRows([charge]), formulaIds:[] });
  if (total) {
    const tolerance = Math.max(1e-12, Math.max(Math.abs(total.minimum), Math.abs(total.maximum)) * 1e-10);
    if (total.minimum < -tolerance) warnings.push("VOLUME_ELECTRON_DENSITY_SIGNIFICANT_NEGATIVE");
    else if (total.minimum < 0) warnings.push("VOLUME_ELECTRON_DENSITY_NUMERIC_NEGATIVE");
    return freeze({ kind:"electron_density", title:"Electron density", status:"ready", defaultFieldId:total.fieldId, modeFieldIds:{ total:total.fieldId }, presets:presets(total,false), warnings, augmentationIncluded, integralRows:integralRows([total]), formulaIds:[] });
  }
  if (vector) return freeze({ kind:"non_collinear", title:"Non-collinear magnetization", status:"deferred", defaultFieldId:null, modeFieldIds:{}, presets:[], warnings:[...warnings,"VOLUME_NONCOLLINEAR_PRODUCT_DEFERRED"], augmentationIncluded, integralRows:integralRows([vector]), formulaIds:[] });
  return freeze({ kind:"unavailable", title:"Generic volumetric field", status:"unavailable", defaultFieldId:null, modeFieldIds:{}, presets:[], warnings:[...warnings,"VOLUME_CHARGE_SPIN_PRODUCT_UNAVAILABLE"], augmentationIncluded, integralRows:[], formulaIds:[] });
}

function presets(field: ValidatedVolumetricField, signed: boolean) {
  const magnitude = signed ? Math.max(Math.abs(field.minimum), Math.abs(field.maximum)) : Math.max(field.maximum, Number.EPSILON);
  return Object.freeze(([0.1, 0.25, 0.5] as const).map((fraction, index) => Object.freeze({ id:(["low","medium","high"] as const)[index], label:(["Low","Medium","High"] as const)[index], absoluteIsovalue:magnitude*fraction })));
}

function integralRows(fields: readonly ValidatedVolumetricField[]) {
  return Object.freeze(fields.map((field) => Object.freeze({ fieldId:field.fieldId, label:field.fieldName, value:field.integral, unit:integralUnit(field), interpretation:field.integralSemantics })));
}

function integralUnit(field: ValidatedVolumetricField) {
  if (field.integralSemantics === "electron_count") return "electron";
  if (field.integralSemantics === "elementary_charge") return "elementary_charge";
  if (field.integralSemantics === "magnetic_moment") return "bohr_magneton";
  return field.unit;
}

function freeze(value: Omit<ChargeSpinDensityProduct, never>): ChargeSpinDensityProduct {
  return Object.freeze({ ...value, modeFieldIds:Object.freeze({ ...value.modeFieldIds }), presets:Object.freeze([...value.presets]), warnings:Object.freeze([...new Set(value.warnings)].sort()), integralRows:Object.freeze([...value.integralRows]), formulaIds:Object.freeze([...value.formulaIds]) });
}
