import { describe, expect, it } from "vitest";
import { layoutBrillouinZoneLabels, type BZLabelAnchor } from "./brillouinZoneLabelLayout";

const point = (id: string, x = 160, y = 180): BZLabelAnchor => ({ id, x, y, width: 44, height: 44 });

describe("Brillouin-zone point labels", () => {
  it("separates coincident and nearby points without moving their scientific anchors", () => {
    const points = [point("gamma"), point("r"), point("m", 160, 190), point("x", 180, 170)];
    const original = JSON.stringify(points);
    const layout = layoutBrillouinZoneLabels(points, 320, 400);
    expect(layout.overflow).toEqual([]);
    expect(layout.placed).toHaveLength(4);
    for (const a of layout.placed) for (const b of layout.placed) {
      if (a.id === b.id) continue;
      expect(a.left + a.width <= b.left || b.left + b.width <= a.left || a.top + a.height <= b.top || b.top + b.height <= a.top).toBe(true);
    }
    for (const placed of layout.placed) expect([placed.x, placed.y]).toEqual([points.find(item => item.id === placed.id)!.x, points.find(item => item.id === placed.id)!.y]);
    expect(JSON.stringify(points)).toBe(original);
    expect(layoutBrillouinZoneLabels(points, 320, 400)).toEqual(layout);
  });

  it("keeps edge labels fully within narrow canvases and reserves other point markers", () => {
    const points = [point("left", 0, 0), point("right", 180, 0), point("bottom", 180, 320)];
    const { placed, overflow } = layoutBrillouinZoneLabels(points, 180, 320);
    expect(overflow).toHaveLength(0);
    for (const item of placed) {
      expect(item.left).toBeGreaterThanOrEqual(0);
      expect(item.top).toBeGreaterThanOrEqual(0);
      expect(item.left + item.width).toBeLessThanOrEqual(180);
      expect(item.top + item.height).toBeLessThanOrEqual(320);
      for (const anchor of points) expect(anchor.x < item.left || anchor.x > item.left + item.width || anchor.y < item.top || anchor.y > item.top + item.height).toBe(true);
    }
  });

  it("returns crowded labels for the independent picker instead of forcing overlaps", () => {
    const points = Array.from({ length: 64 }, (_, i) => point(String(i), 80, 80));
    const layout = layoutBrillouinZoneLabels(points, 160, 160);
    expect(layout.overflow.length).toBeGreaterThan(0);
    expect(new Set([...layout.placed.map(item => item.id), ...layout.overflow]).size).toBe(64);
  });

  it("does not pin off-screen or non-finite coordinates to the image edge", () => {
    expect(layoutBrillouinZoneLabels([point("outside", -20, 0), point("bad", NaN, 40)], 320, 400)).toEqual({ placed: [], overflow: [] });
  });
});
