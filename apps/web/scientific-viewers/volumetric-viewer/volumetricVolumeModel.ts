import type {
  ValidatedVolumetricField,
  ValidatedVolumetricGrid,
  VolumeGpuCapabilities,
  VolumeQuality,
  VolumeTexturePrecision,
  VolumeTransferFunction,
  VolumeVector3,
} from "./volumetricViewerTypes";
import { VOLUMETRIC_BROWSER_CAPS, VolumetricViewerError } from "./volumetricViewerTypes";

export const VOLUME_QUALITY_PRESETS: Readonly<Record<VolumeQuality["id"], VolumeQuality>> = Object.freeze({
  low: Object.freeze({ id: "low", samplesPerVoxel: 0.75, maximumRaySteps: 256, pixelRatioCap: 1 }),
  balanced: Object.freeze({ id: "balanced", samplesPerVoxel: 1.25, maximumRaySteps: 512, pixelRatioCap: 1.5 }),
  high: Object.freeze({ id: "high", samplesPerVoxel: 2, maximumRaySteps: 768, pixelRatioCap: 2 }),
});

export function textureShapeForGrid(shape: readonly [number, number, number]): readonly [number, number, number] {
  return Object.freeze([shape[2], shape[1], shape[0]]) as readonly [number, number, number];
}

export function preflightVolumeMetadata(
  shape: readonly [number, number, number],
  mobile: boolean,
): Readonly<{ supported: boolean; reason: string | null; voxelCount: number; textureBytes: number; textureShape: readonly [number, number, number] }> {
  if (shape.length !== 3 || shape.some((value) => !Number.isSafeInteger(value) || value < 2)) {
    return Object.freeze({ supported: false, reason: "texture_shape_invalid", voxelCount: 0, textureBytes: 0, textureShape: textureShapeForGrid([0, 0, 0]) });
  }
  const voxelCount = product(shape);
  const textureBytes = voxelCount * 4;
  const maximumVoxels = mobile ? VOLUMETRIC_BROWSER_CAPS.maximumVolumeVoxelsMobile : VOLUMETRIC_BROWSER_CAPS.maximumVolumeVoxelsDesktop;
  const reason = !Number.isSafeInteger(voxelCount) || voxelCount > maximumVoxels
    ? "texture_voxel_cap_exceeded"
    : textureBytes > VOLUMETRIC_BROWSER_CAPS.maximumVolumeTextureBytes
      ? "texture_byte_cap_exceeded"
      : null;
  return Object.freeze({ supported: reason === null, reason, voxelCount, textureBytes, textureShape: textureShapeForGrid(shape) });
}

export function inspectVolumeGpuCapabilities(args: Readonly<{
  context: WebGL2RenderingContext | null;
  shape: readonly [number, number, number];
  mobile: boolean;
}>): VolumeGpuCapabilities {
  const metadata = preflightVolumeMetadata(args.shape, args.mobile);
  const textureShape = textureShapeForGrid(args.shape);
  const voxelCount = metadata.voxelCount;
  const textureBytes = metadata.textureBytes;
  const estimatedGpuBytes = textureBytes * 2 + 512 * 4 + VOLUMETRIC_BROWSER_CAPS.maximumVolumeRenderPixels * 8;
  const maximumVoxels = args.mobile ? VOLUMETRIC_BROWSER_CAPS.maximumVolumeVoxelsMobile : VOLUMETRIC_BROWSER_CAPS.maximumVolumeVoxelsDesktop;
  let reason: string | null = null;
  let maximum3dTextureSize = 0;
  let maximumTextureImageUnits = 0;
  let linearFloatFiltering = false;
  if (!metadata.supported) reason = metadata.reason;
  else if (!args.context) reason = "webgl2_unavailable";
  else {
    maximum3dTextureSize = Number(args.context.getParameter(args.context.MAX_3D_TEXTURE_SIZE)) || 0;
    maximumTextureImageUnits = Number(args.context.getParameter(args.context.MAX_TEXTURE_IMAGE_UNITS)) || 0;
    linearFloatFiltering = Boolean(args.context.getExtension("OES_texture_float_linear"));
    if (textureShape.some((value) => value > maximum3dTextureSize)) reason = "texture_dimension_exceeded";
    else if (voxelCount > maximumVoxels) reason = "texture_voxel_cap_exceeded";
    else if (textureBytes > VOLUMETRIC_BROWSER_CAPS.maximumVolumeTextureBytes || estimatedGpuBytes > VOLUMETRIC_BROWSER_CAPS.maximumGpuBytes) reason = "texture_byte_cap_exceeded";
    else if (maximumTextureImageUnits < 2) reason = "texture_image_units_unavailable";
    else if (!linearFloatFiltering) reason = "linear_float_filtering_unavailable";
  }
  return Object.freeze({ supported: reason === null, reason, webgl2: Boolean(args.context), maximum3dTextureSize, maximumTextureImageUnits, linearFloatFiltering, textureShape, textureBytes, estimatedGpuBytes, mobile: args.mobile });
}

export async function prepareVolumeTexture(args: Readonly<{
  buffer: ArrayBuffer;
  dtype: "float32" | "float64";
  valueCount: number;
}>): Promise<Readonly<{ values: Float32Array; precision: VolumeTexturePrecision }>> {
  const stride = args.dtype === "float32" ? 4 : 8;
  if (args.buffer.byteLength !== args.valueCount * stride) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_BYTE_MISMATCH", "Volume bytes do not match field metadata.");
  if (args.dtype === "float64" && args.buffer.byteLength > VOLUMETRIC_BROWSER_CAPS.maximumFloat64ConversionBytes) throw new VolumetricViewerError("VOLUME_VIEWER_BROWSER_CAP_EXCEEDED", "Float64 display conversion exceeds the browser byte cap.");
  const source = args.dtype === "float32" ? new Float32Array(args.buffer) : new Float64Array(args.buffer);
  const values = new Float32Array(source.length);
  let maximumAbsoluteError = 0;
  let maximumRelativeError = 0;
  let squaredError = 0;
  for (let index = 0; index < source.length; index += 1) {
    const original = source[index];
    if (!Number.isFinite(original)) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_BYTE_MISMATCH", "Volume values must be finite.");
    const converted = Math.fround(Object.is(original, -0) ? 0 : original);
    if (!Number.isFinite(converted)) throw new VolumetricViewerError("VOLUME_VIEWER_BROWSER_CAP_EXCEEDED", "Float64 value cannot be represented safely for GPU display.");
    values[index] = converted;
    const error = Math.abs(original - converted);
    maximumAbsoluteError = Math.max(maximumAbsoluteError, error);
    maximumRelativeError = Math.max(maximumRelativeError, error / Math.max(Math.abs(original), 1e-30));
    squaredError += error * error;
  }
  const conversionHash = await sha256(values.buffer);
  return Object.freeze({
    values,
    precision: Object.freeze({
      sourceDtype: args.dtype,
      gpuDtype: "float32",
      conversionApplied: args.dtype === "float64",
      maximumAbsoluteError: clean(maximumAbsoluteError),
      maximumRelativeError: clean(maximumRelativeError),
      rmsError: clean(Math.sqrt(squaredError / Math.max(1, source.length))),
      finiteCount: source.length,
      conversionHash,
    }),
  });
}

export function defaultTransferFunction(field: ValidatedVolumetricField): VolumeTransferFunction {
  const signedSpinChannel = field.spin?.channel === "spin_difference" || field.spin?.channel === "magnetization_x" || field.spin?.channel === "magnetization_y" || field.spin?.channel === "magnetization_z";
  const signed = (field.minimum < 0 && field.maximum > 0) || signedSpinChannel;
  const presetId = field.quantity === "electron_localization_function" ? "elf_localization"
    : field.quantity.includes("potential") ? "potential_source"
      : signed ? "signed_symmetric" : "nonnegative_medium";
  const sourceSpan = field.maximum - field.minimum;
  const span = Math.max(sourceSpan, 1e-12);
  const low = presetId === "elf_localization" ? Math.max(field.minimum, 0.45)
    : presetId === "nonnegative_medium" ? field.minimum + span * 0.15
      : signed ? -Math.max(Math.abs(field.minimum), Math.abs(field.maximum)) : field.minimum;
  const high = presetId === "elf_localization" ? Math.min(field.maximum, 1)
    : signed ? Math.max(Math.abs(field.minimum), Math.abs(field.maximum)) : field.maximum;
  const constantMargin = Math.max(1e-6, Math.abs(field.minimum) * 1e-6);
  const windowLow = sourceSpan === 0 ? field.minimum - constantMargin : low;
  const windowHigh = sourceSpan === 0 ? field.maximum + constantMargin : high;
  return validateTransferFunction({
    version: "phase10j6.transfer_function.v1",
    presetId,
    windowLow,
    windowHigh,
    opacityScale: 0.65,
    paletteId: presetId === "elf_localization" ? "elf_teal_yellow" : signed ? "diverging_blue_red" : presetId === "potential_source" ? "magma" : "viridis",
    zeroPolicy: signed ? "transparent_zero" : "none",
  });
}

export function validateTransferFunction(value: VolumeTransferFunction): VolumeTransferFunction {
  const presets = new Set(["nonnegative_medium", "signed_symmetric", "positive_only", "negative_only", "potential_source", "elf_localization"]);
  const palettes = new Set(["viridis", "diverging_blue_red", "magma", "elf_teal_yellow"]);
  if (value.version !== "phase10j6.transfer_function.v1" || !presets.has(value.presetId) || !palettes.has(value.paletteId)
    || !Number.isFinite(value.windowLow) || !Number.isFinite(value.windowHigh) || value.windowLow >= value.windowHigh
    || !Number.isFinite(value.opacityScale) || value.opacityScale < 0 || value.opacityScale > 1) {
    throw new VolumetricViewerError("VOLUME_VIEWER_CONTRACT_INVALID", "Volume transfer function is outside the application-owned allowlist.");
  }
  return Object.freeze({ ...value });
}

export function rayUnitCubeIntersection(origin: VolumeVector3, direction: VolumeVector3): Readonly<{ entry: number; exit: number } | null> {
  let entry = Number.NEGATIVE_INFINITY;
  let exit = Number.POSITIVE_INFINITY;
  for (let axis = 0; axis < 3; axis += 1) {
    if (Math.abs(direction[axis]) < 1e-12) {
      if (origin[axis] < 0 || origin[axis] > 1) return null;
      continue;
    }
    const first = (0 - origin[axis]) / direction[axis];
    const second = (1 - origin[axis]) / direction[axis];
    entry = Math.max(entry, Math.min(first, second));
    exit = Math.min(exit, Math.max(first, second));
  }
  return exit >= Math.max(entry, 0) ? Object.freeze({ entry: Math.max(entry, 0), exit }) : null;
}

export function clipRayExitAtStructureDepth(
  rayOrigin: VolumeVector3,
  rayDirection: VolumeVector3,
  entry: number,
  exit: number,
  structurePoint: VolumeVector3 | null,
): number {
  if (!structurePoint) return exit;
  const structureDistance =
    (structurePoint[0] - rayOrigin[0]) * rayDirection[0]
    + (structurePoint[1] - rayOrigin[1]) * rayDirection[1]
    + (structurePoint[2] - rayOrigin[2]) * rayDirection[2];
  if (!Number.isFinite(structureDistance) || structureDistance <= entry || structureDistance >= exit) return exit;
  return structureDistance;
}

export function affineVolumeClipPlane(
  origin: VolumeVector3,
  basis: readonly [VolumeVector3, VolumeVector3, VolumeVector3],
  axis: 0 | 1 | 2,
  offset: number,
): Readonly<{ normal: VolumeVector3; constant: number }> {
  const spans = axis === 0 ? [basis[1], basis[2]] : axis === 1 ? [basis[2], basis[0]] : [basis[0], basis[1]];
  const raw = cross(spans[0], spans[1]);
  const orientation = dot(raw, basis[axis]) < 0 ? -1 : 1;
  const length = Math.hypot(...raw);
  if (!Number.isFinite(length) || length <= 1e-12 || !Number.isFinite(offset)) throw new VolumetricViewerError("VOLUME_VIEWER_CONTRACT_INVALID", "Volume clipping requires a finite non-degenerate affine basis.");
  const normal: VolumeVector3 = [raw[0] * orientation / length, raw[1] * orientation / length, raw[2] * orientation / length];
  const point: VolumeVector3 = [origin[0] + basis[axis][0] * offset, origin[1] + basis[axis][1] * offset, origin[2] + basis[axis][2] * offset];
  return Object.freeze({ normal: Object.freeze(normal), constant: -dot(normal, point) });
}

export function sampleCanonicalTexture(args: Readonly<{
  values: Float32Array;
  shape: readonly [number, number, number];
  coordinates: VolumeVector3;
  boundaries: ValidatedVolumetricGrid["boundaryConditions"];
}>): number | null {
  const coordinate = args.coordinates.map((value, axis) => {
    if (args.boundaries[axis] === "periodic") return moduloFloat(value, 1);
    if (value < 0 || value > 1) return null;
    return Math.min(1, Math.max(0, value));
  });
  if (coordinate.some((value) => value === null)) return null;
  const grid = coordinate.map((value, axis) => Number(value) * (args.boundaries[axis] === "periodic" ? args.shape[axis] : args.shape[axis] - 1));
  const lower = grid.map(Math.floor);
  const upper = lower.map((value, axis) => args.boundaries[axis] === "periodic" ? modulo(value + 1, args.shape[axis]) : Math.min(value + 1, args.shape[axis] - 1));
  const t = grid.map((value, axis) => value - lower[axis]);
  let result = 0;
  for (let di = 0; di <= 1; di += 1) for (let dj = 0; dj <= 1; dj += 1) for (let dk = 0; dk <= 1; dk += 1) {
    const i = (di ? upper : lower)[0]; const j = (dj ? upper : lower)[1]; const k = (dk ? upper : lower)[2];
    const weight = (di ? t[0] : 1 - t[0]) * (dj ? t[1] : 1 - t[1]) * (dk ? t[2] : 1 - t[2]);
    result += args.values[((i * args.shape[1]) + j) * args.shape[2] + k] * weight;
  }
  return clean(result);
}

export function correctedOpacity(alphaReference: number, stepLength: number, referenceStep: number): number {
  if (![alphaReference, stepLength, referenceStep].every(Number.isFinite) || alphaReference < 0 || alphaReference > 1 || stepLength < 0 || referenceStep <= 0) {
    throw new VolumetricViewerError("VOLUME_VIEWER_CONTRACT_INVALID", "Opacity correction inputs are invalid.");
  }
  return Math.min(1, Math.max(0, 1 - Math.pow(1 - alphaReference, stepLength / referenceStep)));
}

export function cpuReferenceRayMarch(args: Readonly<{
  values: Float32Array;
  shape: readonly [number, number, number];
  boundaries: ValidatedVolumetricGrid["boundaryConditions"];
  rayOrigin: VolumeVector3;
  rayDirection: VolumeVector3;
  transferFunction: VolumeTransferFunction;
  maximumSteps: number;
}>): Readonly<{ color: readonly [number, number, number]; alpha: number; steps: number }> {
  const hit = rayUnitCubeIntersection(args.rayOrigin, args.rayDirection);
  if (!hit) return Object.freeze({ color: Object.freeze([0, 0, 0]) as readonly [number, number, number], alpha: 0, steps: 0 });
  const voxelLength = Math.hypot(args.rayDirection[0] * args.shape[0], args.rayDirection[1] * args.shape[1], args.rayDirection[2] * args.shape[2]);
  const steps = Math.max(1, Math.min(args.maximumSteps, Math.ceil((hit.exit - hit.entry) * voxelLength)));
  const step = (hit.exit - hit.entry) / steps;
  let alpha = 0; const color = [0, 0, 0]; let executed = 0;
  for (let index = 0; index < steps && alpha < 0.985; index += 1) {
    executed += 1;
    const distance = hit.entry + (index + 0.5) * step;
    const point: VolumeVector3 = [args.rayOrigin[0] + args.rayDirection[0] * distance, args.rayOrigin[1] + args.rayDirection[1] * distance, args.rayOrigin[2] + args.rayDirection[2] * distance];
    const source = sampleCanonicalTexture({ values: args.values, shape: args.shape, coordinates: point, boundaries: args.boundaries });
    if (source === null) continue;
    const normalized = Math.min(1, Math.max(0, (source - args.transferFunction.windowLow) / (args.transferFunction.windowHigh - args.transferFunction.windowLow)));
    const baseAlpha = normalized * args.transferFunction.opacityScale;
    const sampleAlpha = correctedOpacity(baseAlpha, step, 1 / Math.max(...args.shape));
    const sampleColor = volumePalette(normalized, args.transferFunction.paletteId);
    color[0] += (1 - alpha) * sampleAlpha * sampleColor[0]; color[1] += (1 - alpha) * sampleAlpha * sampleColor[1]; color[2] += (1 - alpha) * sampleAlpha * sampleColor[2];
    alpha += (1 - alpha) * sampleAlpha;
  }
  return Object.freeze({ color: Object.freeze(color.map(clean)) as unknown as readonly [number, number, number], alpha: clean(alpha), steps: executed });
}

export function volumePalette(value: number, paletteId: VolumeTransferFunction["paletteId"]): readonly [number, number, number] {
  if (paletteId === "diverging_blue_red") return [value, 0.25 + 0.35 * (1 - Math.abs(value * 2 - 1)), 1 - value];
  if (paletteId === "magma") return [Math.min(1, value * 1.4), value * value * 0.75, 0.2 + value * 0.25];
  if (paletteId === "elf_teal_yellow") return [0.08 + value * 0.92, 0.38 + value * 0.57, 0.42 - value * 0.3];
  return [0.25 + value * 0.55, 0.08 + value * 0.82, 0.35 + (1 - value) * 0.35];
}

async function sha256(buffer: ArrayBuffer): Promise<string> {
  if (!globalThis.crypto?.subtle) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_HASH_MISMATCH", "SHA-256 is unavailable for volume conversion identity.");
  const digest = await globalThis.crypto.subtle.digest("SHA-256", buffer);
  return [...new Uint8Array(digest)].map((value) => value.toString(16).padStart(2, "0")).join("");
}
function product(values: readonly number[]): number { return values.reduce((total, value) => total * value, 1); }
function modulo(value: number, base: number): number { return ((value % base) + base) % base; }
function moduloFloat(value: number, base: number): number { return ((value % base) + base) % base; }
function clean(value: number): number { return Object.is(value, -0) ? 0 : Number(value.toPrecision(12)); }
function cross(a: VolumeVector3, b: VolumeVector3): VolumeVector3 { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
function dot(a: VolumeVector3, b: VolumeVector3): number { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }
