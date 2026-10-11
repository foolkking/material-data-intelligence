import { expect, it, vi } from "vitest";
import { readPlotCoordinates, readPlotNumericMatrix, readPlotNumericVector } from "./workspace-plot-data";

it("decodes signed, unsigned and big-endian source values without changing their precision", () => {
  expect(readPlotNumericVector({ dtype: "i2", bdata: "AQD//w==" })).toEqual([1, -1]);
  expect(readPlotNumericVector({ dtype: ">i2", bdata: "AAH//w==" })).toEqual([1, -1]);
  expect(readPlotNumericVector({ dtype: "u4", bdata: "/////w==" })).toEqual([4294967295]);
  const bytes = Buffer.alloc(16);
  bytes.writeDoubleBE(1.5, 0); bytes.writeDoubleBE(-2.25, 8);
  expect(readPlotNumericVector({ dtype: ">f8", bdata: bytes.toString("base64") })).toEqual([1.5, -2.25]);
});

it("distinguishes encoded missing positions from invalid infinities and finite-only geometry", () => {
  const missing = { dtype: "f8", bdata: "AAAAAAAA+H8=" };
  expect(readPlotCoordinates(missing)).toEqual([null]);
  expect(readPlotNumericVector(missing)).toBeNull();
  expect(readPlotNumericVector(missing, true)).toEqual([null]);
  const bytes = Buffer.alloc(8);
  bytes.writeDoubleLE(Infinity);
  expect(readPlotCoordinates({ dtype: "f8", bdata: bytes.toString("base64") })).toBeNull();
  expect(readPlotCoordinates([Number.NaN])).toBeNull();
});

it("retains vector rank and matrix row order while validating the full declared shape", () => {
  const payload = Object.freeze({ dtype: "i1", bdata: "AQIDBAUG", shape: "2, 3" });
  expect(readPlotNumericMatrix(payload)).toEqual([[1, 2, 3], [4, 5, 6]]);
  expect(readPlotCoordinates(payload)).toBeNull();
  expect(readPlotCoordinates({ ...payload, shape: [6] })).toEqual([1, 2, 3, 4, 5, 6]);
  for (const shape of ["2,2", "1,2,3", "-2,3", "2.0,3", "0,6", [2, "3"], [Number.MAX_SAFE_INTEGER, 6], null]) {
    expect(readPlotNumericMatrix({ ...payload, shape })).toBeNull();
  }
  expect(readPlotNumericMatrix({ dtype: "i1", bdata: "AQIDBAUG" })).toBeNull();
});

it("rejects malformed bytes, partial elements and unsupported dtype encodings", () => {
  for (const bdata of ["", "???", "AQI="]) expect(readPlotCoordinates({ dtype: "f8", bdata })).toBeNull();
  for (const dtype of ["i8", "u8", "f2", "|f8", "object", "f128"]) expect(readPlotCoordinates({ dtype, bdata: "AAAAAAAAAAA=" })).toBeNull();
});

it("rejects oversized encoded data before decoding or allocating its bytes", () => {
  const decoder = vi.spyOn(globalThis, "atob");
  try {
    expect(readPlotCoordinates({ dtype: "i1", bdata: "A".repeat(10_666_672) })).toBeNull();
    expect(decoder).not.toHaveBeenCalled();
  } finally { decoder.mockRestore(); }
});

it("accepts encoded matrix rows and preserves caller-owned plain coordinates", () => {
  const coordinates = Object.freeze(["alpha", null, 1.234567890123]);
  expect(readPlotCoordinates(coordinates)).toEqual(["alpha", null, 1.234567890123]);
  expect(readPlotNumericMatrix([{ dtype: "i1", bdata: "AQID" }, [4, null, 6]])).toEqual([[1, 2, 3], [4, null, 6]]);
});
