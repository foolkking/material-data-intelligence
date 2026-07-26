import { createHash } from "node:crypto";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { canonicalOffset, domainBasis, fractionalToWorld, probeCanonicalField, sampleVolumetricSlice } from "./volumetricSliceModel";
import { sha256HexSync } from "./volumetricHash";
import type { ValidatedVolumetricGrid } from "./volumetricViewerTypes";

const grid = (overrides: Partial<ValidatedVolumetricGrid> = {}): ValidatedVolumetricGrid => ({
  schemaVersion: "phase10j.volumetric_grid.v1", gridId: "grid", contentHash: "a".repeat(64), shape: [4, 3, 2], origin: [1, 2, 3], stepMatrix: [[1, 0, 0], [0.25, 1, 0], [0.1, 0.2, 1]], sampleLocation: "node", boundaryConditions: ["periodic", "periodic", "periodic"], endpointPolicy: "excluded", periodic: true, structureBinding: null, ...overrides,
});
const values = () => { const output = new Float64Array(24); for (let i = 0; i < 4; i += 1) for (let j = 0; j < 3; j += 1) for (let k = 0; k < 2; k += 1) output[canonicalOffset(i, j, k, [4, 3, 2])] = 100 * i + 10 * j + k; return output; };

beforeEach(() => vi.stubGlobal("crypto", { subtle: { digest: async (_algorithm: string, value: BufferSource) => { const bytes = new Uint8Array(value instanceof ArrayBuffer ? value : value.buffer, value instanceof ArrayBuffer ? 0 : value.byteOffset, value instanceof ArrayBuffer ? value.byteLength : value.byteLength); const digest = createHash("sha256").update(bytes).digest(); return digest.buffer.slice(digest.byteOffset, digest.byteOffset + digest.byteLength); } } }));
afterEach(() => vi.unstubAllGlobals());

describe("Phase 10J-6 canonical lattice slices", () => {
  it("uses k-fast canonical indexing and exact planes for all axes", async () => {
    expect(canonicalOffset(1, 2, 1, [4, 3, 2])).toBe(11);
    for (const axis of [0, 1, 2] as const) {
      const result = await sampleVolumetricSlice({ datasetHash: "d".repeat(64), fieldHash: "f".repeat(64), unit: "e/A3", grid: grid(), dtype: "float64", fieldBuffer: values().buffer, axis, fractionalPosition: axis === 0 ? 0.25 : axis === 1 ? 1 / 3 : 0.5, maximumOutputValues: 100 });
      expect(result.samplingMode).toBe("exact_grid_plane"); expect(result.lowerIndex).toBe(1); expect(result.upperIndex).toBe(1); expect(result.values[0]).toBe(axis === 0 ? 100 : axis === 1 ? 10 : 1); expect(result.contentHash).toMatch(/^[a-f0-9]{64}$/);
    }
  });

  it("interpolates only along the slice normal and wraps periodic boundaries", async () => {
    const middle = await sampleVolumetricSlice({ datasetHash: "d".repeat(64), fieldHash: "f".repeat(64), unit: "e/A3", grid: grid(), dtype: "float64", fieldBuffer: values().buffer, axis: 0, fractionalPosition: 0.125, maximumOutputValues: 100 });
    expect(middle.samplingMode).toBe("linear_axis_interpolation"); expect(middle.interpolationFactor).toBe(0.5); expect(middle.values[0]).toBe(50);
    const wrapped = await sampleVolumetricSlice({ datasetHash: "d".repeat(64), fieldHash: "f".repeat(64), unit: "e/A3", grid: grid(), dtype: "float64", fieldBuffer: values().buffer, axis: 0, fractionalPosition: 0.875, maximumOutputValues: 100 });
    expect(wrapped.periodicWrap).toBe(true); expect(wrapped.lowerIndex).toBe(3); expect(wrapped.upperIndex).toBe(0); expect(wrapped.values[0]).toBe(150);
  });

  it("matches the trusted SHA-256 reference without Worker WebCrypto", () => {
    const bytes = new TextEncoder().encode("abc");
    expect(sha256HexSync(bytes)).toBe(createHash("sha256").update(bytes).digest("hex"));
  });

  it("preserves triclinic affine plane geometry and shifted origin", async () => {
    const source = grid(); const result = await sampleVolumetricSlice({ datasetHash: "d".repeat(64), fieldHash: "f".repeat(64), unit: "e/A3", grid: source, dtype: "float64", fieldBuffer: values().buffer, axis: 0, fractionalPosition: 0.25, maximumOutputValues: 100 });
    expect(domainBasis(source)).toEqual([[4, 0, 0], [0.75, 3, 0], [0.2, 0.4, 2]]); expect(result.plane.origin).toEqual([2, 2, 3]); expect(result.plane.basisU).toEqual([0.2, 0.4, 2]); expect(result.plane.basisV).toEqual([0.75, 3, 0]); expect(fractionalToWorld(source, [0.25, 0.5, 0.5])).toEqual([2.475, 3.7, 4]);
  });

  it("rejects non-periodic extrapolation and output cap bypass", async () => {
    const nonPeriodic = grid({ boundaryConditions: ["non_periodic", "non_periodic", "non_periodic"], periodic: false });
    await expect(sampleVolumetricSlice({ datasetHash: "d".repeat(64), fieldHash: "f".repeat(64), unit: "e/A3", grid: nonPeriodic, dtype: "float64", fieldBuffer: values().buffer, axis: 0, fractionalPosition: 0.99, maximumOutputValues: 100 })).rejects.toMatchObject({ code: "VOLUME_VIEWER_CONTRACT_INVALID" });
    await expect(sampleVolumetricSlice({ datasetHash: "d".repeat(64), fieldHash: "f".repeat(64), unit: "e/A3", grid: grid(), dtype: "float64", fieldBuffer: values().buffer, axis: 0, fractionalPosition: 0.25, maximumOutputValues: 5 })).rejects.toMatchObject({ code: "VOLUME_VIEWER_BROWSER_CAP_EXCEEDED" });
  });

  it("probes the source field trilinearly without mutating it", () => {
    const source = values(); const before = source.slice(); const result = probeCanonicalField({ buffer: source.buffer, dtype: "float64", grid: grid(), fractional: [0.125, 0, 0] });
    expect(result.value).toBe(50); expect(source).toEqual(before); expect(result.cartesian).toEqual([1.5, 2, 3]);
  });
});
