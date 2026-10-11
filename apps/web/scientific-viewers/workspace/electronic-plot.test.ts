import { describe, expect, it } from "vitest";
import { electronicPlotData } from "./electronic-plot";

describe("electronic plot coordinates", () => {
  it("uses nonuniform source path distances and breaks instead of joining disconnected segments", () => {
    const payload = { kpoints: [0, 0.1, 8, 10].map((pathDistance, index) => ({ kpointId: `k-${index}`, pathDistance, label: index === 0 ? "Γ" : undefined })), bands: [{ bandId: "v", energiesEv: [-1, -0.5, -0.2, -1] }], pathSegments: [{ endKpointId: "k-1", breakAfter: true }] };
    const before = JSON.stringify(payload);
    const plot = electronicPlotData(payload, "band");
    expect(plot.curves[0].segments).toEqual([[[0, -1], [0.1, -0.5]], [[8, -0.2], [10, -1]]]);
    expect(plot.xDomain).toEqual([0, 10]);
    expect(plot.ticks).toEqual([{ value: 0, label: "Γ" }]);
    expect(JSON.stringify(payload)).toBe(before);
  });

  it("keeps nonuniform DOS energies paired with their values and includes a zero baseline", () => {
    const plot = electronicPlotData({ energiesEv: [-5, -4.9, 2], totalDos: [{ values: [2, 8, 3] }] }, "dos");
    expect(plot.curves[0].segments).toEqual([[[-5, 2], [-4.9, 8], [2, 3]]]);
    expect(plot.yDomain).toEqual([0, 8]);
  });

  it.each([{ values: [1, 2] }, { values: [1, "bad", 3] }, { values: [1, Infinity, 3] }])("does not filter out invalid values and shift their coordinates: $values", ({ values }) => {
    const plot = electronicPlotData({ energiesEv: [0, 1, 8], totalDos: [{ values }] }, "dos");
    expect(plot.curves).toHaveLength(0);
    expect(plot.invalidSeries).toBe(1);
  });

  it("preserves sharp extrema and break endpoints when bounding a long series", () => {
    const values = Array(10_000).fill(0); values[451] = 17; values[8131] = -8;
    const payload = { kpoints: values.map((_, i) => ({ pathDistance: i ** 2, kpointId: `k-${i}` })), bands: [{ energiesEv: values }], pathSegments: [{ endKpointId: "k-5000", breakAfter: true }] };
    const plot = electronicPlotData(payload, "band"), segments = plot.curves[0].segments, points = segments.flat();
    expect(points.length).toBeLessThanOrEqual(2_400);
    expect(points).toContainEqual([451 ** 2, 17]);
    expect(points).toContainEqual([8131 ** 2, -8]);
    expect(segments[0].at(-1)).toEqual([5000 ** 2, 0]);
    expect(segments[1][0]).toEqual([5001 ** 2, 0]);
    expect(points.at(-1)).toEqual([9999 ** 2, 0]);
    expect(plot.curves[0].sampled).toBe(true);
  });

  it("retains both boundary labels when disconnected segments share a distance", () => {
    const plot = electronicPlotData({ kpoints: [{ kpointId: "a", pathDistance: 1, label: "X" }, { kpointId: "b", pathDistance: 1, label: "L" }], bands: [{ energiesEv: [1, 2] }], pathSegments: [{ endKpointId: "a", breakAfter: true }] }, "band");
    expect(plot.ticks).toEqual([{ value: 1, label: "X | L" }]);
    expect(plot.curves[0].segments).toHaveLength(2);
    expect(plot.xDomain[1]).toBeGreaterThan(plot.xDomain[0]);
  });
});
