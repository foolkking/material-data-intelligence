import { describe, expect, it } from "vitest";

import { formatMeasurement, measureAngle, measureDihedral, measureDistance } from "./viewerSceneMeasurements";

describe("viewer scene measurements", () => {
  it("measures Cartesian distance in angstrom", () => {
    const result = measureDistance([0, 1], [[0, 0, 0], [3, 4, 0]]);
    expect(result.ok && result.result.value).toBe(5);
    expect(result.ok && result.result.unit).toBe("angstrom");
  });

  it.each([[0, [1, 0, 0], [0, 0, 0], [2, 0, 0]], [90, [1, 0, 0], [0, 0, 0], [0, 1, 0]], [180, [1, 0, 0], [0, 0, 0], [-1, 0, 0]]] as const)("measures %s degree angles", (expected, a, b, c) => {
    const result = measureAngle([0, 1, 2], [a, b, c]);
    expect(result.ok && result.result.value).toBeCloseTo(expected, 8);
  });

  it("returns a signed dihedral in the fixed range", () => {
    const result = measureDihedral([0, 1, 2, 3], [[1, 0, 0], [0, 0, 0], [0, 1, 0], [0, 1, 1]]);
    expect(result.ok).toBe(true);
    if (result.ok) expect(result.result.value).toBeCloseTo(-90, 8);
  });

  it("rejects degenerate and non-finite measurements", () => {
    expect(measureAngle([0, 1, 2], [[0, 0, 0], [0, 0, 0], [1, 0, 0]])).toEqual({ ok: false, error: "DEGENERATE_MEASUREMENT" });
    expect(measureDistance([0, 1], [[0, 0, 0], [Number.NaN, 0, 0]])).toEqual({ ok: false, error: "INVALID_COORDINATE" });
  });

  it("formats bounded precision", () => expect(formatMeasurement(1.23456)).toBe("1.235"));
});
