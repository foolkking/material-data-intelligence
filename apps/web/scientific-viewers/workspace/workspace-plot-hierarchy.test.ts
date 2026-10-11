import { describe, expect, it } from "vitest";
import { sanitizePlotSpec } from "./WorkspaceGenericPlot";

describe("saved hierarchy rendering", () => {
  const hierarchy = {
    ids: ["unary/Cu/Cu", "unary/Cu", "unary"], labels: ["Cu", "Cu", "unary"],
    parents: ["unary/Cu", "unary", ""], values: [2, 2, 2], branchvalues: "total",
  };
  it.each(["treemap", "sunburst"])("keeps distinct repeated labels and parent identity for %s", type => {
    const content = { data: [{ type, ...hierarchy }] }, before = JSON.stringify(content);
    const spec = sanitizePlotSpec(content, 3);
    expect(spec.ok).toBe(true);
    if (!spec.ok) return;
    const trace = spec.data[0] as typeof hierarchy;
    expect(trace.labels).toEqual(["Cu", "Cu", "unary"]);
    expect(trace.ids).toHaveLength(3);
    expect(new Set(trace.ids).size).toBe(3);
    expect(trace.parents).toEqual([trace.ids[1], trace.ids[2], ""]);
    expect(trace.values).toEqual([2, 2, 2]);
    expect(trace.branchvalues).toBe("total");
    expect(JSON.stringify(content)).toBe(before);
  });

  it("keeps remainder semantics instead of silently treating parent remainder as total", () => {
    for (const branchvalues of [undefined, "remainder"]) {
      const spec = sanitizePlotSpec({ data: [{ type: "sunburst", ...hierarchy, values: [2, 1, 0], branchvalues }] }, 3);
      expect(spec).toMatchObject({ ok: true, data: [{ values: [2, 1, 0], branchvalues: "remainder" }] });
    }
  });

  it.each([1, 1e-12, 1e-100, 1e-300])("validates parent totals independently of the value scale %s", scale => {
    const trace = { type: "sunburst", ids: ["root", "a", "b"], labels: ["root", "a", "b"],
      parents: ["", "root", "root"], values: [0.3 * scale, 0.1 * scale, 0.2 * scale], branchvalues: "total" };
    expect(sanitizePlotSpec({ data: [trace] }, 3)).toMatchObject({ ok: true });
    expect(sanitizePlotSpec({ data: [{ ...trace, values: [scale, 25 * scale, 25 * scale] }] }, 3)).toMatchObject({ ok: false });
    expect(sanitizePlotSpec({ data: [{ ...trace, values: [0, scale, 0] }] }, 3)).toMatchObject({ ok: false });
    expect(sanitizePlotSpec({ data: [{ ...trace, values: [scale, 25 * scale, 25 * scale], branchvalues: "remainder" }] }, 3)).toMatchObject({ ok: true });
  });

  it("rejects overflowed child totals even when each saved value is finite", () => {
    const trace = { type: "treemap", ids: ["root", "a", "b"], labels: ["root", "a", "b"],
      parents: ["", "root", "root"], values: [Number.MAX_VALUE, Number.MAX_VALUE, Number.MAX_VALUE], branchvalues: "total" };
    expect(sanitizePlotSpec({ data: [trace] }, 3)).toMatchObject({ ok: false });
  });

  it("resolves ID-free saved figures by unique labels and retains requested depth and root", () => {
    expect(sanitizePlotSpec({ data: [{ type: "treemap", labels: ["root", "child"], parents: ["", "root"], values: [2, 2], branchvalues: "total", level: "root", maxdepth: 2, sort: false }] }, 2))
      .toMatchObject({ ok: true, data: [{ ids: ["node-0", "node-1"], parents: ["", "node-0"], level: "node-0", maxdepth: 2, sort: false }] });
  });

  it("does not merge identities that have the same escaped or shortened display text", () => {
    const spec = sanitizePlotSpec({ data: [{ type: "treemap", ids: ["<a>", "<b>"], labels: ["Cu", "Cu"], parents: ["", "<a>"], values: [1, 1], branchvalues: "total" }] }, 2);
    expect(spec).toMatchObject({ ok: true, data: [{ ids: ["node-0", "node-1"], parents: ["", "node-0"] }] });
  });

  it.each([
    { ids: ["duplicate", "duplicate", "root"] }, { ids: ["", "b", "c"] },
    { parents: ["missing", "unary", ""] }, { parents: ["unary/Cu/Cu", "unary", ""] },
    { parents: ["unary/Cu", "unary/Cu/Cu", ""] },
    { values: [-1, 2, 2] }, { values: [3, 2, 2] }, { values: [2, 2] },
    { branchvalues: "invalid" }, { level: "missing" }, { maxdepth: 0 }, { maxdepth: 1.5 },
    { sort: "false" }, { labels: ["Cu"] },
  ])("rejects invalid or misleading hierarchy %j", patch => {
    expect(sanitizePlotSpec({ data: [{ type: "sunburst", ...hierarchy, ...patch }] }, 3)).toMatchObject({ ok: false });
  });

  it("rejects ambiguous labels without IDs and empty all-zero charts", () => {
    expect(sanitizePlotSpec({ data: [{ type: "treemap", labels: ["Cu", "Cu"], parents: ["", ""], values: [1, 1] }] }, 2)).toMatchObject({ ok: false });
    expect(sanitizePlotSpec({ data: [{ type: "treemap", ...hierarchy, values: [0, 0, 0] }] }, 3)).toMatchObject({ ok: false, code: "PLOTLY_NO_FINITE_POINTS" });
  });

  it("validates deep graphs iteratively without dropping nodes or overflowing the stack", () => {
    const n = 12_000;
    const trace = { type: "sunburst", ids: Array.from({ length: n }, (_, i) => `id-${i}`), labels: Array(n).fill("layer"), parents: Array.from({ length: n }, (_, i) => i ? `id-${i - 1}` : ""), values: Array(n).fill(1), branchvalues: "total" };
    expect(sanitizePlotSpec({ data: [trace] }, n)).toMatchObject({ ok: true, pointCount: n });
    expect(sanitizePlotSpec({ data: [trace] }, n - 1)).toMatchObject({ ok: false });
  });

  it("preserves bounded panel domains and count labels and discloses saved truncation", () => {
    const spec = sanitizePlotSpec({ artifactType: "composition.chem_sys_sunburst", warnings: ["too_many_leaf_nodes_warning"], plotlyFigure: { data: [{ type: "sunburst", ...hierarchy, domain: { x: [0.2, 0.8] }, textinfo: "label+value" }] } }, 3);
    expect(spec).toMatchObject({ ok: true, data: [{ domain: { x: [0.2, 0.8] }, textinfo: "label+value" }], notes: [expect.stringContaining("未显示分组")] });
    expect(sanitizePlotSpec({ data: [{ type: "treemap", ...hierarchy, domain: { x: [2, 3] } }] }, 3)).toMatchObject({ ok: false });
  });
});
