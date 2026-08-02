import { describe, expect, it } from "vitest";

import { sanitizePlotSpec } from "./WorkspaceGenericPlot";

describe("Phase 10M-4 generic Plotly renderer", () => {
  it("renders only bounded backend data through a stripped application layout", () => {
    const result = sanitizePlotSpec({
      figure: {
        data: [{ type: "scatter", x: [1, 2], y: [3, 4], name: "<img src=x>", hovertemplate: "javascript:alert(1)" }],
        layout: { title: { text: "<script>bad</script> Valid" }, images: [{ source: "https://example.invalid/image.png" }], annotations: [{ text: "<iframe>" }] },
      },
    }, 10);
    expect(result).toMatchObject({ ok: true, pointCount: 2 });
    if (!result.ok) return;
    expect(result.layout).not.toHaveProperty("images");
    expect(result.layout).not.toHaveProperty("annotations");
    expect(result.data[0]).not.toHaveProperty("hovertemplate");
    expect((result.data[0] as Record<string, unknown>).name).toBe(" img src=x ");
  });

  it("refuses browser histogram binning, non-finite values, and point caps", () => {
    expect(sanitizePlotSpec({ figure: { data: [{ type: "histogram", x: [1, 2] }] } }, 10)).toMatchObject({ ok: false, code: "PLOTLY_TRACE_TYPE_UNSUPPORTED" });
    expect(sanitizePlotSpec({ figure: { data: [{ type: "scatter", x: [1], y: [Number.NaN] }] } }, 10)).toMatchObject({ ok: false, code: "PLOTLY_TRACE_INVALID" });
    expect(sanitizePlotSpec({ figure: { data: [{ type: "scatter", x: [1, 2, 3], y: [1, 2, 3] }] } }, 2)).toMatchObject({ ok: false, code: "PLOTLY_POINT_CAP_EXCEEDED" });
  });
});
