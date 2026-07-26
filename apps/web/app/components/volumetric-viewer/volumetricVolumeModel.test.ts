import { createHash } from "node:crypto";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { affineVolumeClipPlane, clipRayExitAtStructureDepth, cpuReferenceRayMarch, correctedOpacity, defaultTransferFunction, inspectVolumeGpuCapabilities, preflightVolumeMetadata, prepareVolumeTexture, rayUnitCubeIntersection, sampleCanonicalTexture, textureShapeForGrid, validateTransferFunction } from "./volumetricVolumeModel";
import { VOLUME_FRAGMENT_SHADER } from "./volumetricVolumeShader";
import type { ValidatedVolumetricField, VolumeTransferFunction } from "./volumetricViewerTypes";

beforeEach(() => vi.stubGlobal("crypto", { subtle: { digest: async (_algorithm: string, value: BufferSource) => { const bytes = new Uint8Array(value instanceof ArrayBuffer ? value : value.buffer, value instanceof ArrayBuffer ? 0 : value.byteOffset, value instanceof ArrayBuffer ? value.byteLength : value.byteLength); const digest = createHash("sha256").update(bytes).digest(); return digest.buffer.slice(digest.byteOffset, digest.byteOffset + digest.byteLength); } } }));
afterEach(() => vi.unstubAllGlobals());
const fakeContext = (size = 256, linear = true, textureUnits = 16) => ({ MAX_3D_TEXTURE_SIZE: 0x8073, MAX_TEXTURE_IMAGE_UNITS: 0x8872, getParameter: (parameter: number) => parameter === 0x8872 ? textureUnits : size, getExtension: () => linear ? {} : null }) as unknown as WebGL2RenderingContext;
const transfer: VolumeTransferFunction = { version: "phase10j6.transfer_function.v1", presetId: "nonnegative_medium", windowLow: 0, windowHigh: 1, opacityScale: 0.5, paletteId: "viridis", zeroPolicy: "none" };

describe("Phase 10J-6 volume model", () => {
  it("creates a finite deterministic display window for a constant source field", () => {
    const field = { quantity: "electron_density", minimum: 2, maximum: 2 } as ValidatedVolumetricField;
    const constantTransfer = defaultTransferFunction(field);
    expect(constantTransfer.windowLow).toBeCloseTo(1.999998, 12);
    expect(constantTransfer.windowHigh).toBeCloseTo(2.000002, 12);
    expect(constantTransfer.windowLow).toBeLessThan(constantTransfer.windowHigh);
  });
  it("uses a signed symmetric transfer for a source spin-difference channel even when this sample is positive", () => {
    const field = { quantity: "magnetization_density", minimum: 0.125, maximum: 1, spin: { representation: "collinear", channel: "spin_difference", signConvention: "up minus down", sourceConvention: "source" } } as ValidatedVolumetricField;
    expect(defaultTransferFunction(field)).toMatchObject({ presetId: "signed_symmetric", paletteId: "diverging_blue_red", windowLow: -1, windowHigh: 1, zeroPolicy: "transparent_zero" });
  });
  it("maps canonical ijk values directly to texture width=nz, height=ny, depth=nx", () => { expect(textureShapeForGrid([2, 3, 5])).toEqual([5, 3, 2]); });
  it("rejects over-cap metadata before payload conversion or WebGL allocation", () => { expect(preflightVolumeMetadata([128, 128, 128], false)).toMatchObject({ supported: true, voxelCount: 2_097_152, textureBytes: 8_388_608 }); expect(preflightVolumeMetadata([129, 128, 128], false)).toMatchObject({ supported: false, reason: "texture_voxel_cap_exceeded" }); expect(preflightVolumeMetadata([128, 128, 128], true)).toMatchObject({ supported: false, reason: "texture_voxel_cap_exceeded" }); });
  it("gates WebGL2, dimensions, voxel bytes, and float-linear filtering before allocation", () => {
    expect(inspectVolumeGpuCapabilities({ context: null, shape: [4, 4, 4], mobile: false })).toMatchObject({ supported: false, reason: "webgl2_unavailable" });
    expect(inspectVolumeGpuCapabilities({ context: fakeContext(3), shape: [4, 2, 2], mobile: false })).toMatchObject({ supported: false, reason: "texture_dimension_exceeded" });
    expect(inspectVolumeGpuCapabilities({ context: fakeContext(256, true, 1), shape: [4, 4, 4], mobile: false })).toMatchObject({ supported: false, reason: "texture_image_units_unavailable" });
    expect(inspectVolumeGpuCapabilities({ context: fakeContext(256, false), shape: [4, 4, 4], mobile: false })).toMatchObject({ supported: false, reason: "linear_float_filtering_unavailable" });
    expect(inspectVolumeGpuCapabilities({ context: fakeContext(), shape: [4, 4, 4], mobile: false })).toMatchObject({ supported: true, textureShape: [4, 4, 4], textureBytes: 256 });
    expect(inspectVolumeGpuCapabilities({ context: fakeContext(), shape: [128, 128, 128], mobile: false })).toMatchObject({ supported: true, textureBytes: 8_388_608 });
    expect(inspectVolumeGpuCapabilities({ context: fakeContext(), shape: [129, 128, 128], mobile: false })).toMatchObject({ supported: false, reason: "texture_voxel_cap_exceeded" });
  });
  it("records explicit float64 to float32 display conversion error and hash", async () => {
    const source = new Float64Array([1 / 3, 1e-12, -2.25]); const before = source.slice(); const result = await prepareVolumeTexture({ buffer: source.buffer, dtype: "float64", valueCount: 3 });
    expect(result.precision).toMatchObject({ sourceDtype: "float64", gpuDtype: "float32", conversionApplied: true, finiteCount: 3 }); expect(result.precision.maximumAbsoluteError).toBeGreaterThan(0); expect(result.precision.conversionHash).toMatch(/^[a-f0-9]{64}$/); expect(source).toEqual(before);
  });
  it("samples periodic canonical texture trilinearly without axis transposition", () => {
    const values = new Float32Array(8); for (let i = 0; i < 2; i += 1) for (let j = 0; j < 2; j += 1) for (let k = 0; k < 2; k += 1) values[((i * 2) + j) * 2 + k] = 100 * i + 10 * j + k;
    expect(sampleCanonicalTexture({ values, shape: [2, 2, 2], coordinates: [0.25, 0, 0], boundaries: ["periodic", "periodic", "periodic"] })).toBe(50);
    expect(sampleCanonicalTexture({ values, shape: [2, 2, 2], coordinates: [0, 0, 0.25], boundaries: ["periodic", "periodic", "periodic"] })).toBe(0.5);
  });
  it("uses bounded unit-cube rays, corrected opacity, and front-to-back compositing", () => {
    expect(rayUnitCubeIntersection([-1, 0.5, 0.5], [1, 0, 0])).toEqual({ entry: 1, exit: 2 }); expect(rayUnitCubeIntersection([-1, 2, 0.5], [1, 0, 0])).toBeNull();
    expect(correctedOpacity(0.5, 0.5, 1)).toBeCloseTo(1 - Math.sqrt(0.5));
    const result = cpuReferenceRayMarch({ values: new Float32Array(64).fill(1), shape: [4, 4, 4], boundaries: ["non_periodic", "non_periodic", "non_periodic"], rayOrigin: [-1, 0.5, 0.5], rayDirection: [1, 0, 0], transferFunction: transfer, maximumSteps: 32 }); expect(result.steps).toBeGreaterThan(0); expect(result.steps).toBeLessThanOrEqual(32); expect(result.alpha).toBeGreaterThan(0);
  });

  it("clips volume rays at opaque structure depth without hiding front or rear geometry", () => {
    const origin: readonly [number, number, number] = [-1, 0.5, 0.5];
    const direction: readonly [number, number, number] = [1, 0, 0];
    expect(clipRayExitAtStructureDepth(origin, direction, 1, 2, [-0.25, 0.5, 0.5])).toBe(2);
    expect(clipRayExitAtStructureDepth(origin, direction, 1, 2, [0.4, 0.5, 0.5])).toBeCloseTo(1.4);
    expect(clipRayExitAtStructureDepth(origin, direction, 1, 2, [1.25, 0.5, 0.5])).toBe(2);
    expect(clipRayExitAtStructureDepth(origin, direction, 1, 2, null)).toBe(2);
  });
  it("derives one world-space clipping plane from orthogonal or triclinic affine bases", () => {
    const orthogonal = affineVolumeClipPlane([0, 0, 0], [[2, 0, 0], [0, 3, 0], [0, 0, 4]], 0, 0.25);
    expect(orthogonal.normal).toEqual([1, 0, 0]); expect(orthogonal.constant).toBe(-0.5);
    const basis = [[2, 0, 0], [0.5, 1.5, 0], [0.2, 0.3, 1.2]] as const;
    const triclinic = affineVolumeClipPlane([0.1, -0.2, 0.3], basis, 1, 0.6);
    const point = [0.1 + basis[1][0] * 0.6, -0.2 + basis[1][1] * 0.6, 0.3 + basis[1][2] * 0.6] as const;
    expect(triclinic.normal[0] * point[0] + triclinic.normal[1] * point[1] + triclinic.normal[2] * point[2] + triclinic.constant).toBeCloseTo(0, 12);
    expect(triclinic.normal[0] * basis[1][0] + triclinic.normal[1] * basis[1][1] + triclinic.normal[2] * basis[1][2]).toBeGreaterThan(0);
  });
  it("owns a static bounded GLSL3 shader and rejects arbitrary transfer metadata", () => {
    expect(VOLUME_FRAGMENT_SHADER).toContain("sampler3D"); expect(VOLUME_FRAGMENT_SHADER).toContain("index < 768"); expect(VOLUME_FRAGMENT_SHADER).toContain("vec3(point.z, point.y, point.x)"); expect(VOLUME_FRAGMENT_SHADER).not.toContain("eval");
    expect(() => validateTransferFunction({ ...transfer, windowLow: 1, windowHigh: 0 })).toThrow();
    const field = { quantity: "electron_localization_function", minimum: 0, maximum: 1 } as ValidatedVolumetricField; expect(defaultTransferFunction(field)).toMatchObject({ presetId: "elf_localization", windowLow: 0.45, windowHigh: 1 });
  });
});
