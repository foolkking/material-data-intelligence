import type {
  ValidatedVolumetricGrid,
  VolumeVector3,
  VolumetricSlice,
  VolumetricSliceAxis,
} from "./volumetricViewerTypes";
import { VolumetricViewerError } from "./volumetricViewerTypes";
import { sha256HexSync } from "./volumetricHash";

const EPSILON = 1e-10;

export async function sampleVolumetricSlice(args: Readonly<{
  datasetHash: string;
  fieldHash: string;
  unit: string;
  grid: ValidatedVolumetricGrid;
  dtype: "float32" | "float64";
  fieldBuffer: ArrayBuffer;
  axis: VolumetricSliceAxis;
  fractionalPosition: number;
  maximumOutputValues: number;
}>): Promise<VolumetricSlice> {
  const { grid, axis } = args;
  const values = decodeValues(args.fieldBuffer, args.dtype, product(grid.shape));
  const position = normalizePosition(args.fractionalPosition, grid.boundaryConditions[axis], grid.endpointPolicy, grid.shape[axis]);
  const gridCoordinate = position * axisCoordinateScale(grid, axis);
  const nearest = Math.round(gridCoordinate);
  const exact = Math.abs(gridCoordinate - nearest) <= EPSILON;
  let lowerIndex = exact ? nearest : Math.floor(gridCoordinate);
  let upperIndex = exact ? nearest : lowerIndex + 1;
  let interpolationFactor = exact ? 0 : gridCoordinate - lowerIndex;
  let periodicWrap = false;
  if (grid.boundaryConditions[axis] === "periodic") {
    lowerIndex = modulo(lowerIndex, grid.shape[axis]);
    upperIndex = modulo(upperIndex, grid.shape[axis]);
    periodicWrap = !exact && upperIndex < lowerIndex;
  } else {
    if (lowerIndex < 0 || upperIndex >= grid.shape[axis]) {
      throw new VolumetricViewerError("VOLUME_VIEWER_CONTRACT_INVALID", "Slice position would require non-periodic extrapolation.");
    }
  }
  const [verticalAxis, horizontalAxis] = remainingAxes(axis);
  const height = grid.shape[verticalAxis];
  const width = grid.shape[horizontalAxis];
  if (width * height > args.maximumOutputValues) {
    throw new VolumetricViewerError("VOLUME_VIEWER_BROWSER_CAP_EXCEEDED", "Slice output exceeds the bounded browser value budget.");
  }
  const output = new Float64Array(width * height);
  let minimum = Number.POSITIVE_INFINITY;
  let maximum = Number.NEGATIVE_INFINITY;
  let sum = 0;
  for (let row = 0; row < height; row += 1) {
    for (let column = 0; column < width; column += 1) {
      const lower = coordinate(axis, lowerIndex, verticalAxis, row, horizontalAxis, column);
      const upper = coordinate(axis, upperIndex, verticalAxis, row, horizontalAxis, column);
      const a = values[canonicalOffset(lower[0], lower[1], lower[2], grid.shape)];
      const b = values[canonicalOffset(upper[0], upper[1], upper[2], grid.shape)];
      const value = exact ? a : a + (b - a) * interpolationFactor;
      output[row * width + column] = value;
      minimum = Math.min(minimum, value);
      maximum = Math.max(maximum, value);
      sum += value;
    }
  }
  const domain = domainBasis(grid);
  const planeOrigin = add(grid.origin, scale(domain[axis], position));
  const normal = normalize(cross(domain[horizontalAxis], domain[verticalAxis]));
  const metadata = {
    schema_version: "phase10j6.volumetric_slice.v1",
    dataset_hash: args.datasetHash,
    field_hash: args.fieldHash,
    axis,
    fractional_position: clean(position),
    lower_index: lowerIndex,
    upper_index: upperIndex,
    interpolation_factor: clean(interpolationFactor),
    output_shape: [height, width],
    unit: args.unit,
  };
  const contentHash = hashSlice(metadata, output);
  return Object.freeze({
    schemaVersion: "phase10j6.volumetric_slice.v1",
    sourceDatasetHash: args.datasetHash,
    sourceFieldHash: args.fieldHash,
    axis,
    fractionalPosition: clean(position),
    physicalPosition: clean(position * length(domain[axis])),
    samplingMode: exact ? "exact_grid_plane" : "linear_axis_interpolation",
    lowerIndex,
    upperIndex,
    interpolationFactor: clean(interpolationFactor),
    periodicWrap,
    outputShape: Object.freeze([height, width]) as readonly [number, number],
    plane: Object.freeze({
      origin: Object.freeze(planeOrigin),
      basisU: Object.freeze(domain[horizontalAxis]),
      basisV: Object.freeze(domain[verticalAxis]),
      normal: Object.freeze(normal),
      horizontalAxis,
      verticalAxis,
    }),
    values: output,
    unit: args.unit,
    statistics: Object.freeze({ minimum: clean(minimum), maximum: clean(maximum), mean: clean(sum / output.length) }),
    contentHash,
    provenance: Object.freeze({ algorithm: "phase10j6.lattice_axis_linear.v1", sourceMutated: false }),
  });
}

export function canonicalOffset(i: number, j: number, k: number, shape: readonly [number, number, number]): number {
  if (![i, j, k].every(Number.isSafeInteger) || i < 0 || j < 0 || k < 0 || i >= shape[0] || j >= shape[1] || k >= shape[2]) {
    throw new VolumetricViewerError("VOLUME_VIEWER_CONTRACT_INVALID", "Grid coordinate is outside the canonical field.");
  }
  return ((i * shape[1]) + j) * shape[2] + k;
}

export function domainBasis(grid: ValidatedVolumetricGrid): readonly [VolumeVector3, VolumeVector3, VolumeVector3] {
  return Object.freeze(grid.stepMatrix.map((row, axis) => {
    const count = grid.boundaryConditions[axis] === "periodic" && grid.endpointPolicy === "excluded"
      ? grid.shape[axis]
      : grid.endpointPolicy === "included" ? grid.shape[axis] - 1 : grid.shape[axis];
    return Object.freeze(scale(row, count));
  })) as readonly [VolumeVector3, VolumeVector3, VolumeVector3];
}

export function fractionalToWorld(grid: ValidatedVolumetricGrid, fractional: VolumeVector3): VolumeVector3 {
  const basis = domainBasis(grid);
  return add(add(add(grid.origin, scale(basis[0], fractional[0])), scale(basis[1], fractional[1])), scale(basis[2], fractional[2]));
}

export function probeCanonicalField(args: Readonly<{
  buffer: ArrayBuffer;
  dtype: "float32" | "float64";
  grid: ValidatedVolumetricGrid;
  fractional: VolumeVector3;
}>): Readonly<{ value: number; fractional: VolumeVector3; cartesian: VolumeVector3 }> {
  const values = decodeValues(args.buffer, args.dtype, product(args.grid.shape));
  return probeCanonicalValues({ values, grid: args.grid, fractional: args.fractional });
}

export function probeCanonicalValues(args: Readonly<{
  values: Float32Array | Float64Array;
  grid: ValidatedVolumetricGrid;
  fractional: VolumeVector3;
}>): Readonly<{ value: number; fractional: VolumeVector3; cartesian: VolumeVector3 }> {
  if (args.values.length !== product(args.grid.shape)) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_BYTE_MISMATCH", "Field values do not match the canonical grid shape.");
  const coordinates = args.fractional.map((value, axis) => {
    const normalized = normalizePosition(value, args.grid.boundaryConditions[axis], args.grid.endpointPolicy, args.grid.shape[axis]);
    return normalized * axisCoordinateScale(args.grid, axis as VolumetricSliceAxis);
  });
  const lower = coordinates.map(Math.floor);
  const upper = lower.map((value, axis) => args.grid.boundaryConditions[axis] === "periodic" ? modulo(value + 1, args.grid.shape[axis]) : Math.min(value + 1, args.grid.shape[axis] - 1));
  const factor = coordinates.map((value, axis) => value - lower[axis]);
  let result = 0;
  for (let di = 0; di <= 1; di += 1) for (let dj = 0; dj <= 1; dj += 1) for (let dk = 0; dk <= 1; dk += 1) {
    const i = (di ? upper : lower)[0];
    const j = (dj ? upper : lower)[1];
    const k = (dk ? upper : lower)[2];
    const weight = (di ? factor[0] : 1 - factor[0]) * (dj ? factor[1] : 1 - factor[1]) * (dk ? factor[2] : 1 - factor[2]);
    result += args.values[canonicalOffset(i, j, k, args.grid.shape)] * weight;
  }
  const fractional = Object.freeze([...args.fractional]) as VolumeVector3;
  return Object.freeze({ value: clean(result), fractional, cartesian: Object.freeze(fractionalToWorld(args.grid, fractional)) });
}

function decodeValues(buffer: ArrayBuffer, dtype: "float32" | "float64", count: number): Float32Array | Float64Array {
  const stride = dtype === "float32" ? 4 : 8;
  if (buffer.byteLength !== count * stride) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_BYTE_MISMATCH", "Field bytes do not match the canonical grid shape.");
  const values = dtype === "float32" ? new Float32Array(buffer) : new Float64Array(buffer);
  for (const value of values) if (!Number.isFinite(value)) throw new VolumetricViewerError("VOLUME_VIEWER_PAYLOAD_BYTE_MISMATCH", "Field values must be finite.");
  return values;
}

function normalizePosition(value: number, boundary: "periodic" | "non_periodic", endpoint: ValidatedVolumetricGrid["endpointPolicy"], count: number): number {
  if (!Number.isFinite(value)) throw new VolumetricViewerError("VOLUME_VIEWER_CONTRACT_INVALID", "Slice coordinates must be finite.");
  if (boundary === "periodic") return clean(moduloFloat(value, 1));
  const maximum = endpoint === "included" ? 1 : (count - 1) / count;
  if (value < 0 || value > maximum + EPSILON) throw new VolumetricViewerError("VOLUME_VIEWER_CONTRACT_INVALID", "Slice coordinate is outside the non-periodic sampled domain.");
  return clean(Math.min(value, maximum));
}

function axisCoordinateScale(grid: ValidatedVolumetricGrid, axis: number): number {
  return grid.endpointPolicy === "included" ? grid.shape[axis] - 1 : grid.shape[axis];
}

function remainingAxes(axis: VolumetricSliceAxis): readonly [VolumetricSliceAxis, VolumetricSliceAxis] {
  return ([0, 1, 2] as const).filter((value) => value !== axis) as unknown as readonly [VolumetricSliceAxis, VolumetricSliceAxis];
}

function coordinate(axis: number, axisIndex: number, verticalAxis: number, row: number, horizontalAxis: number, column: number): [number, number, number] {
  const value: [number, number, number] = [0, 0, 0];
  value[axis] = axisIndex;
  value[verticalAxis] = row;
  value[horizontalAxis] = column;
  return value;
}

function hashSlice(metadata: object, values: Float64Array): string {
  const prefix = new TextEncoder().encode(JSON.stringify(metadata));
  const bytes = new Uint8Array(prefix.byteLength + values.byteLength);
  bytes.set(prefix, 0);
  bytes.set(new Uint8Array(values.buffer, values.byteOffset, values.byteLength), prefix.byteLength);
  return sha256HexSync(bytes);
}

function product(shape: readonly number[]): number { return shape.reduce((total, value) => total * value, 1); }
function modulo(value: number, base: number): number { return ((value % base) + base) % base; }
function moduloFloat(value: number, base: number): number { const result = ((value % base) + base) % base; return Math.abs(result - base) <= EPSILON ? 0 : result; }
function scale(value: VolumeVector3, factor: number): VolumeVector3 { return [value[0] * factor, value[1] * factor, value[2] * factor]; }
function add(a: VolumeVector3, b: VolumeVector3): VolumeVector3 { return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]; }
function cross(a: VolumeVector3, b: VolumeVector3): VolumeVector3 { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
function length(value: VolumeVector3): number { return Math.hypot(value[0], value[1], value[2]); }
function normalize(value: VolumeVector3): VolumeVector3 { const magnitude = length(value); if (!(magnitude > EPSILON)) throw new VolumetricViewerError("VOLUME_VIEWER_CONTRACT_INVALID", "Slice plane basis is degenerate."); return scale(value, 1 / magnitude); }
function clean(value: number): number { return Object.is(value, -0) ? 0 : Number(value.toPrecision(15)); }
