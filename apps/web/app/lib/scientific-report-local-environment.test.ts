import { describe, expect, it } from "vitest";
import { localEnvironmentArtifactFixture } from "../../scientific-viewers/workspace/saved-local-environment.fixture";
import { renderScientificReportFigure } from "./scientific-report-figure";

describe("saved coordination polyhedron report", () => {
  it.each([360, 770, 920, 1200])("retains all exact vertices and faces in four fitted projections at %s", width => {
    const payload = localEnvironmentArtifactFixture().content;
    const before = JSON.stringify(payload);
    const rendered = renderScientificReportFigure(payload, "Si 位点 0", { width })!;
    expect(rendered).not.toBeNull();
    expect(rendered.pointCount).toBe(4);
    const svg = new DOMParser().parseFromString(rendered.svg, "image/svg+xml");
    expect(svg.querySelector("parsererror")).toBeNull();
    expect(svg.querySelectorAll("[data-polyhedron-view]")).toHaveLength(4);
    expect(svg.querySelectorAll("[data-face]")).toHaveLength(16);
    expect(svg.querySelectorAll("[data-vertex]")).toHaveLength(16);
    expect(svg.querySelector('[data-polyhedron-view="xy"] [data-vertex="vertex:0"]')?.getAttribute("data-xyz")).toBe("1,1,1");
    const x = svg.querySelector('[data-polyhedron-view="xy"] [data-vertex="vertex:0"]')!;
    const z = svg.querySelector('[data-polyhedron-view="xz"] [data-vertex="vertex:0"]')!;
    expect(x.getAttribute("cx")).toBe(z.getAttribute("cx"));
    expect(svg.documentElement.getAttribute("data-source-checksum")).toBe("a".repeat(64));
    expect(svg.documentElement.textContent).toContain("几何近邻不代表确定的化学键");
    expect(rendered.svg).not.toMatch(/(?:NaN|Infinity|<script)/u);
    expect(JSON.stringify(payload)).toBe(before);
  });

  it("retains unavailable surfaces and ambiguous classification without inventing geometry", () => {
    const payload = localEnvironmentArtifactFixture().content as any;
    payload.siteResults[0].polyhedron = { ...payload.siteResults[0].polyhedron, status: "UNAVAILABLE", faces: [], unavailableReason: "COPLANAR_POLYHEDRON" };
    payload.siteResults[0].classification.status = "AMBIGUOUS";
    const result = renderScientificReportFigure(payload, "分类不唯一")!;
    expect(result.svg).toContain("最近参考：四面体");
    expect(result.svg).toContain("未生成三维封闭多面体");
    expect(result.svg).not.toContain("data-face=");
  });

  it.each(["face", "duplicate", "nonfinite", "oversized"])("fails closed for %s", change => {
    const payload = localEnvironmentArtifactFixture().content as any;
    if (change === "face") payload.siteResults[0].polyhedron.faces[0].vertexIdentities[0] = "unknown";
    else if (change === "duplicate") payload.siteResults[0].polyhedron.vertices[1].vertexIdentity = "vertex:0";
    else if (change === "nonfinite") payload.siteResults[0].polyhedron.vertices[0].relativeCartesian[2] = Infinity;
    else payload.siteResults = Array.from({ length: 17 }, () => payload.siteResults[0]);
    // Malformed scientific payloads cannot fall back to an unrelated generic graph.
    payload.data = [{ x: [0, 1], y: [1, 2] }];
    expect(renderScientificReportFigure(payload, "Invalid")).toBeNull();
  });
});
