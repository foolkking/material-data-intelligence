/** Saved Plotly arrays use row-major binary values and optional shape metadata.
 * Share decoding across drawing, numeric inspection and report export. */
export type PlotCoordinate = number | string | null;
const MAX_TYPED_ARRAY_BYTES = 8_000_000;

export function readPlotCoordinates(value: unknown): PlotCoordinate[] | null {
  if (Array.isArray(value)) return value.every(item => item === null || typeof item === "string" || typeof item === "number" && Number.isFinite(item)) ? value : null;
  return readPlotNumericVector(value, true);
}

export function readPlotNumericVector(value: unknown, allowMissing: true): Array<number | null> | null;
export function readPlotNumericVector(value: unknown, allowMissing?: false): number[] | null;
export function readPlotNumericVector(value: unknown, allowMissing = false): Array<number | null> | null {
  if (Array.isArray(value)) return value.every(item => allowMissing && item === null || typeof item === "number" && Number.isFinite(item)) ? value : null;
  const decoded = decodePlotlyArray(value, 1);
  if (!decoded || !allowMissing && decoded.values.includes(null)) return null;
  return decoded.values;
}

export function readPlotNumericMatrix(value: unknown): Array<Array<number | null>> | null {
  if (Array.isArray(value)) {
    const rows = value.map(row => readPlotNumericVector(row, true));
    return rows.every(row => row !== null) ? rows as Array<Array<number | null>> : null;
  }
  const decoded = decodePlotlyArray(value, 2);
  if (!decoded) return null;
  const width = decoded.shape[1];
  return Array.from({ length: decoded.shape[0] }, (_, index) => decoded.values.slice(index * width, (index + 1) * width));
}

function decodePlotlyArray(value: unknown, rank: 1 | 2): { values: Array<number | null>; shape: number[] } | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const encoded = value as Record<string, unknown>;
  const dtype = typeof encoded.dtype === "string" ? encoded.dtype : "";
  const bdata = typeof encoded.bdata === "string" ? encoded.bdata : "";
  const match = /^([<>=|]?)([fiu])([1248])$/.exec(dtype);
  if (!match || !bdata || bdata.length > Math.ceil(MAX_TYPED_ARRAY_BYTES / 3) * 4 || !/^[A-Za-z0-9+/]*={0,2}$/.test(bdata)) return null;
  const kind = match[2], bytesPerValue = Number(match[3]);
  if ((kind === "f" && ![4, 8].includes(bytesPerValue)) || (kind !== "f" && ![1, 2, 4].includes(bytesPerValue)) || match[1] === "|" && bytesPerValue !== 1) return null;
  let bytes: Uint8Array;
  try {
    const decoded = atob(bdata);
    if (!decoded.length || decoded.length > MAX_TYPED_ARRAY_BYTES || decoded.length % bytesPerValue !== 0) return null;
    bytes = Uint8Array.from(decoded, character => character.charCodeAt(0));
  } catch { return null; }
  const count = bytes.byteLength / bytesPerValue;
  const shape = readShape(encoded.shape, count);
  if (!shape || shape.length !== rank) return null;
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const littleEndian = match[1] !== ">";
  const values: Array<number | null> = [];
  for (let offset = 0; offset < bytes.byteLength; offset += bytesPerValue) {
    const item = kind === "f"
      ? (bytesPerValue === 4 ? view.getFloat32(offset, littleEndian) : view.getFloat64(offset, littleEndian))
      : kind === "i"
        ? (bytesPerValue === 1 ? view.getInt8(offset) : bytesPerValue === 2 ? view.getInt16(offset, littleEndian) : view.getInt32(offset, littleEndian))
        : (bytesPerValue === 1 ? view.getUint8(offset) : bytesPerValue === 2 ? view.getUint16(offset, littleEndian) : view.getUint32(offset, littleEndian));
    // Plotly's NumPy encoding retains NaN as a missing position. Infinity is
    // invalid, and geometry callers independently require fully finite vectors.
    if (Number.isNaN(item)) values.push(null);
    else if (!Number.isFinite(item)) return null;
    else values.push(item);
  }
  return { values, shape };
}

function readShape(value: unknown, count: number): number[] | null {
  if (value === undefined) return [count];
  let shape: unknown[];
  if (typeof value === "string" && /^\s*\d+\s*(?:,\s*\d+\s*)?$/.test(value)) shape = value.split(",").map(Number);
  else if (Array.isArray(value)) shape = value;
  else return null;
  if (shape.length < 1 || shape.length > 2 || !shape.every(size => Number.isSafeInteger(size) && Number(size) > 0)) return null;
  const dimensions = shape as number[];
  return dimensions.reduce((product, size) => product * size, 1) === count ? dimensions : null;
}
