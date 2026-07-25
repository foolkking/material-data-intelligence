import { describe, expect, it } from "vitest";

import {
  buildElfOrbitalProduct,
  detectElfOrbitalProduct,
  validateElfOrbitalValues,
} from "./elfOrbitalProduct";
import type {
  ValidatedVolumetricBundle,
  ValidatedVolumetricField,
} from "./volumetricViewerTypes";

const hash = "a".repeat(64);

function field(
  quantity: string,
  unit: string,
  minimum = 0,
  maximum = 1,
  integral = 4,
): ValidatedVolumetricField {
  return Object.freeze({
    schemaVersion: "phase10j.volumetric_field.v1", fieldId: `field:${quantity}`,
    fieldName: quantity, gridId: "grid", payloadId: `payload:${quantity}`, quantity,
    valueKind: "real", fieldRank: "scalar", storedComponentCount: 1, unit, sourceUnit: unit,
    normalizationSemantics: "source_native",
    integralSemantics: quantity === "orbital_density" ? "electron_count" : "not_physically_interpreted",
    potentialReference: null, spin: null,
    provenance: { sourceSha256: hash, producer: "mdi_volumetric_adapter", producerVersion: "1.1.0", transformations: [] },
    minimum, maximum, mean: (minimum + maximum) / 2, standardDeviation: 0.25, rms: 0.5,
    integral, warnings: [], contentHash: hash,
  });
}

function bundle(fields: readonly ValidatedVolumetricField[], sourceFormat = "vasp_volumetric"): ValidatedVolumetricBundle {
  return {
    datasetId: "dataset", datasetContentHash: hash, sourceFormat, sourceSha256: hash,
    grid: { schemaVersion: "phase10j.volumetric_grid.v1", gridId: "grid", contentHash: hash,
      shape: [2, 2, 2], origin: [0, 0, 0], stepMatrix: [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
      sampleLocation: "node", boundaryConditions: ["periodic", "periodic", "periodic"],
      endpointPolicy: "excluded", periodic: true, structureBinding: null },
    fields: fields.map((item) => ({ field: item, payload: { schemaVersion: "phase10j.volumetric_payload.v1",
      payloadId: item.payloadId, encoding: "raw_binary", dtype: "float64", gridShape: [2, 2, 2],
      valueCount: 8, uncompressedBytes: 64, compressedBytes: 64, logicalSha256: hash,
      storageSha256: hash, artifactName: "field.f64", inlineValues: null, chunks: [] },
      supported: true, reasons: [] })),
    relationships: [], warnings: [], manifestContentHash: hash, artifactNames: ["field.f64"],
  };
}

describe("Phase 10J-5 ELF/orbital product", () => {
  it("accepts only exact real scalar ELF and orbital-density quantities", () => {
    expect(detectElfOrbitalProduct(bundle([field("electron_localization_function", "dimensionless")]))).toMatchObject({ kind: "elf", reasons: [] });
    expect(detectElfOrbitalProduct(bundle([field("orbital_density", "electron/angstrom^3")]))).toMatchObject({ kind: "orbital_density", reasons: [] });
    expect(detectElfOrbitalProduct(bundle([field("generic_scalar", "dimensionless")]))).toMatchObject({ kind: "unavailable", reasons: ["ELF_ORBITAL_PRODUCT_QUANTITY_UNAVAILABLE"] });
    expect(detectElfOrbitalProduct(bundle([field("electron_localization_function", "electronvolt")]))).toMatchObject({ field: null, reasons: ["ELF_PRODUCT_UNIT_INVALID"] });
  });

  it("validates ELF range without clamping source values", () => {
    const valid = validateElfOrbitalValues(new Float64Array([0, 0.5, 1]), "float64", "elf", hash);
    expect(valid).toMatchObject({ status: "VALID_RANGE", belowZeroCount: 0, aboveOneCount: 0 });
    const noise = validateElfOrbitalValues(new Float32Array([-1e-7, 1 + 1e-7]), "float32", "elf", hash);
    expect(noise).toMatchObject({ status: "NUMERIC_TOLERANCE_WARNING", belowZeroCount: 1, aboveOneCount: 1 });
    expect(noise.minimum).toBeLessThan(0);
    expect(noise.maximum).toBeGreaterThan(1);
    expect(validateElfOrbitalValues([-0.1, 0.5, 1.2], "float64", "elf", hash).status).toBe("SOURCE_RANGE_ANOMALY");
    expect(validateElfOrbitalValues([0, Number.NaN], "float64", "elf", hash).status).toBe("INVALID_NON_FINITE");
  });

  it("validates orbital non-negativity without absolute value, square, or normalization", () => {
    const noise = validateElfOrbitalValues(new Float32Array([-1e-7, 0.5]), "float32", "orbital_density", hash);
    expect(noise).toMatchObject({ status: "NUMERIC_TOLERANCE_WARNING", negativeCount: 1 });
    expect(noise.minimum).toBeLessThan(0);
    expect(validateElfOrbitalValues([-0.01, 0.5], "float64", "orbital_density", hash).status).toBe("SOURCE_RANGE_ANOMALY");
  });

  it("uses neutral exact ELF presets and preserves full-cell integral semantics", () => {
    const product = buildElfOrbitalProduct(bundle([field("electron_localization_function", "dimensionless", 0, 1, 3.75)]));
    expect(product).toMatchObject({ kind: "elf", title: "Electron Localization Function", integral: 3.75, integralUnit: "angstrom^3" });
    expect(product.presets.map((item) => item.exactIsovalue)).toEqual([0.5, 0.7, 0.8, 0.9]);
    expect(product.presets.every((item) => item.version === "ELF_ORBITAL_PRESETS_V1" && item.interpretation === "display_contour_only")).toBe(true);
    expect(product.integralInterpretation).toContain("not an electron count");
  });

  it("discloses unavailable PARCHG identity instead of inferring from filename", () => {
    const product = buildElfOrbitalProduct(bundle([field("orbital_density", "electron/angstrom^3", 0, 2, 0.75)]));
    expect(product).toMatchObject({
      kind: "orbital_density", title: "Source-defined partial density",
      identity: { completeness: "UNAVAILABLE", orbitalId: null, bandIndex: null, kPointIndex: null, occupancy: null },
      integral: 0.75,
    });
    expect(product.warnings).toContain("ORBITAL_SOURCE_IDENTITY_UNAVAILABLE");
    expect(product.integralInterpretation).toContain("not automatically an occupancy");
  });

  it("maps the explicitly selected field in a mixed ELF and orbital dataset", () => {
    const elf = field("electron_localization_function", "dimensionless");
    const orbital = field("orbital_density", "electron/angstrom^3", 0, 2, 0.75);
    const source = bundle([elf, orbital]);
    expect(buildElfOrbitalProduct(source, null, elf.fieldId).kind).toBe("elf");
    expect(buildElfOrbitalProduct(source, null, orbital.fieldId)).toMatchObject({
      kind: "orbital_density",
      sourceFieldId: orbital.fieldId,
      identity: { completeness: "UNAVAILABLE" },
    });
  });

  it("keeps signed real amplitudes and complex wavefunctions outside this product", () => {
    expect(buildElfOrbitalProduct(bundle([field("wavefunction", "angstrom^-3")])).status).toBe("unavailable");
    expect(buildElfOrbitalProduct(bundle([field("custom_declared", "custom_declared", -1, 1)])).status).toBe("unavailable");
  });

  it("is deterministic and never grants artifact execution or filename authority", () => {
    const source = bundle([field("orbital_density", "angstrom^-3")], "gaussian_cube");
    const first = buildElfOrbitalProduct(source);
    const second = buildElfOrbitalProduct(source);
    expect(second).toEqual(first);
    expect(first.security).toEqual({ sourceImmutable: true, artifactCode: false, externalResources: false, arbitraryNormalization: false, filenameAuthority: false });
  });
});
