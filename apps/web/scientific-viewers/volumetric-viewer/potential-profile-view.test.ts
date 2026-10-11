import { expect, it } from "vitest";
import { profileChart, profilePointAt } from "./potential-profile-view";
import type { PotentialProfilePoint } from "./electrostaticPotentialProduct";

const points: PotentialProfilePoint[] = Array.from({ length: 32 }, (_, index) => ({ index, fractional: index / 32, pathLengthAngstrom: index / 4, sourceValue: index / 32, displayedValue: index / 32, planeSampleCount: 1024 }));

it("maps the zoomed curve endpoints to the original grid planes at different rendered widths", () => {
  const chart = profileChart(points, [.25, .75], 1000);
  for (const width of [320, 1000, 1440]) {
    const bounds = { left: 120, width };
    expect(profilePointAt(chart, bounds.left + chart.left / chart.width * width, bounds)?.index).toBe(8);
    expect(profilePointAt(chart, bounds.left + chart.right / chart.width * width, bounds)?.index).toBe(24);
  }
  const panned = profileChart(points, [.375, .875], 640);
  expect(profilePointAt(panned, panned.left, { left: 0, width: 640 })?.index).toBe(12);
  expect(profilePointAt(panned, panned.right, { left: 0, width: 640 })?.index).toBe(28);
});

it("plots source coordinates rather than evenly distributing filtered array indices", () => {
  const uneven = [0, .2, .8, 1].map((fractional, index) => ({ ...points[index], fractional, pathLengthAngstrom: fractional * 10 }));
  const chart = profileChart(uneven, [0, 1], 640);
  expect(chart.plotted[1].x).toBeCloseTo(chart.left + .2 * (chart.right - chart.left));
  expect(chart.xTicks.at(-1)?.value).toBe(10);
  expect(profilePointAt(chart, chart.left + .8 * (chart.right - chart.left), { left: 0, width: 640 })?.index).toBe(2);
});

it("retains finite constant-field axes and never invents points in an empty window", () => {
  const constant = profileChart(points.map(point => ({ ...point, displayedValue: 0 })), [0, 1], 320);
  expect(constant.plotted.every(point => Number.isFinite(point.x) && Number.isFinite(point.y))).toBe(true);
  expect(constant.yTicks[0].value).toBeLessThan(0);
  expect(constant.yTicks.at(-1)!.value).toBeGreaterThan(0);
  expect(profilePointAt(profileChart(points, [.99, 1], 320), 200, { left: 0, width: 320 })).toBeNull();
  expect(profilePointAt(constant, 20, { left: 0, width: 0 })).toBeNull();
});
