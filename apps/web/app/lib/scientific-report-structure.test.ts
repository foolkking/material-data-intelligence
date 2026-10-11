import { describe, expect, it } from "vitest";
import bonded from "../../../../tests/fixtures/viewer_scene_v1/valid_optional_bonds.viewer_scene.v1.json";
import multi from "../../../../tests/fixtures/viewer_scene_v1/valid_multi_species_crystal.viewer_scene.v1.json";
import periodic from "../../../../tests/fixtures/viewer_scene_reference/periodic_viewer_scene.json";
import { renderScientificReportFigure } from "./scientific-report-figure";
import { idealCrystalScene } from "../components/viewer-scene/viewerScenePeriodicBondTestFixture";

const image = (payload: unknown, width = 920, compact = false) => {
  const rendered = renderScientificReportFigure(payload, "晶体结构", { width, compact });
  expect(rendered).not.toBeNull();
  expect(rendered!.svg).not.toMatch(/NaN|Infinity/);
  const document = new DOMParser().parseFromString(rendered!.svg, "image/svg+xml");
  expect(document.querySelector("parsererror")).toBeNull();
  return { rendered: rendered!, document };
};
const number = (e: Element, key: string) => Number(e.getAttribute(key));

describe("saved structure report images", () => {
  it("exports the same ideal-model colors, periodic geometry and model identity without altering originals", () => {
    const payload = idealCrystalScene(), before = JSON.stringify(payload);
    const { document } = image(payload, 360);
    expect(document.documentElement.textContent).toContain("理想晶格模型");
    for (const view of document.querySelectorAll("[data-structure-view]")) {
      expect(view.querySelectorAll('[data-image="false"]')).toHaveLength(2);
      for (const site of view.querySelectorAll('[data-image="false"]')) expect(site.getAttribute("fill")).toBe("#c88033");
      expect(view.querySelector("[data-bond]")?.getAttribute("data-distance")).toBe("0.4");
      expect(view.querySelector('[data-site="1:1:0:0"]')?.getAttribute("stroke")).toBe("#c88033");
    }
    expect(JSON.stringify(payload)).toBe(before);
  });

  it.each([360, 640, 920, 1200])("preserves every site, cell edge and saved relationship at width %s", width => {
    const before = JSON.stringify(bonded), { document, rendered } = image(bonded, width);
    expect(rendered.pointCount).toBe(2);
    expect(rendered.fit).toBe("width");
    const views = [...document.querySelectorAll("[data-structure-view]")];
    expect(views).toHaveLength(4);
    expect(new Set(views.map(view => view.getAttribute("data-scale"))).size).toBe(1);
    for (const view of views) {
      expect(view.querySelectorAll("[data-site]")).toHaveLength(2);
      expect(view.querySelectorAll("[data-cell-edge]")).toHaveLength(12);
      expect(view.querySelectorAll("[data-bond]")).toHaveLength(1);
      expect(view.querySelector('[data-site="1:0:0:0"]')?.getAttribute("data-xyz")).toBe("1.3575,1.3575,1.3575");
      expect(view.querySelector("[data-bond]")?.getAttribute("stroke-dasharray")).toBe("4 3");
    }
    for (const circle of document.querySelectorAll("circle[data-site]")) {
      expect(number(circle, "cx") - number(circle, "r")).toBeGreaterThan(19);
      expect(number(circle, "cx") + number(circle, "r")).toBeLessThan(width - 19);
    }
    expect(JSON.stringify(bonded)).toBe(before);
  });

  it("projects Cartesian coordinates with the same physical scale across axis views", () => {
    const payload = structuredClone(bonded);
    payload.scene.sites[1].xyz = [1, 2, 3];
    payload.scene.bonds = [];
    payload.scene.lattice.vectors = [[5, 1, 0], [0, 6, 2], [1, 0, 7]];
    const { document } = image(payload);
    for (const [viewId, dx, dy] of [["xy", 1, 2], ["xz", 1, 3], ["yz", 2, 3]] as const) {
      const view = document.querySelector(`[data-structure-view="${viewId}"]`)!;
      const a = view.querySelector('[data-site="0:0:0:0"]')!, b = view.querySelector('[data-site="1:0:0:0"]')!;
      const scale = number(view, "data-scale");
      expect((number(b, "cx") - number(a, "cx")) / scale).toBeCloseTo(dx, 10);
      expect((number(a, "cy") - number(b, "cy")) / scale).toBeCloseTo(dy, 10);
      expect(view.querySelector('[data-cell-edge="0"]')?.getAttribute("data-end")).toBe("5,1,0");
    }
  });

  it("adds only recorded periodic endpoint images, retaining the offset and source distance", () => {
    const before = JSON.stringify(periodic), { document, rendered } = image(periodic, 360);
    expect(rendered.pointCount).toBe(2);
    for (const view of document.querySelectorAll("[data-structure-view]")) {
      expect(view.querySelectorAll('[data-image="false"]')).toHaveLength(2);
      expect(view.querySelectorAll('[data-image="true"]')).toHaveLength(1);
      const ghost = view.querySelector('[data-site="1:1:0:0"]')!;
      expect(ghost.getAttribute("fill")).toBe("none");
      const line = view.querySelector("[data-bond]")!;
      expect(line.getAttribute("data-distance")).toBe("0.4");
      expect(line.getAttribute("data-to")).toBe("1:1:0:0");
      expect(line.getAttribute("data-end")).toBe(ghost.getAttribute("data-xyz"));
    }
    expect(document.documentElement.textContent).toContain("1 个周期映像，不计入晶胞位点数");
    expect(JSON.stringify(periodic)).toBe(before);
  });

  it("retains species, partial occupancy and scene truncation without claiming full coverage", () => {
    const payload = structuredClone(multi);
    payload.scene.sites[0].occupancy = 0.5;
    payload.validation.truncated = true;
    const { document } = image(payload, 360, true);
    expect(document.querySelectorAll("[data-species]")).toHaveLength(new Set(payload.scene.sites.map(site => site.element)).size);
    expect(document.querySelector("[data-occupancy]")?.getAttribute("data-occupancy")).toBeDefined();
    expect(document.documentElement.textContent).toContain("部分占位");
    expect(document.documentElement.textContent).toContain("= 0.5");
    expect(document.documentElement.textContent).toContain("场景经过截断");
  });

  it("preserves explicit relationship authority separately from candidate lines", () => {
    const payload = structuredClone(periodic);
    payload.scene.bonds[0].source = "explicit_input";
    payload.scene.bonds[0].authoritative = true;
    const { document } = image(payload);
    expect(document.querySelector("[data-bond]")?.getAttribute("stroke-dasharray")).toBeNull();
    expect(document.querySelector("[data-bond]")?.getAttribute("data-authoritative")).toBe("true");
  });

  it("keeps XML-sensitive site labels inert and intact", () => {
    const payload = structuredClone(bonded);
    payload.scene.sites[0].label = 'Fe & O <label> "a"';
    const { document } = image(payload);
    expect(document.querySelector("label, script, foreignObject")).toBeNull();
    expect(document.documentElement.textContent).toContain(payload.scene.sites[0].label);
  });

  it.each([
    (payload: typeof bonded) => { payload.scene.sites[0].xyz[0] = NaN; },
    (payload: typeof bonded) => { payload.scene.sites[0].occupancy = -0.1; },
    (payload: typeof bonded) => { payload.scene.sites[0].index = -1; },
    (payload: typeof bonded) => { payload.scene.bonds[0].distance = 123; },
    (payload: typeof bonded) => { payload.security.external_urls_allowed = true; },
    (payload: typeof bonded) => { payload.scene.sites[0].label = "<script>unsafe</script>"; },
  ])("declines invalid scientific geometry or unsafe input", mutate => {
    const payload = structuredClone(bonded); mutate(payload);
    expect(renderScientificReportFigure(payload, "图")).toBeNull();
  });
});
