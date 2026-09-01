import { describe, expect, it } from "vitest";

import { researchRunTitle } from "./research-display";

describe("researchRunTitle", () => {
  it("names legacy static RDF runs from their persisted tool identity", () => {
    expect(researchRunTitle({ toolIds: ["structure.rdf"] }))
      .toBe("静态结构径向分布函数（RDF）");
  });

  it("distinguishes MSD-only, diffusion-only, and combined trajectory runs", () => {
    expect(researchRunTitle({ toolIds: ["trajectory.msd"] }))
      .toBe("均方位移（MSD）");
    expect(researchRunTitle({ toolIds: ["trajectory.diffusion"] }))
      .toBe("轨迹扩散分析");
    expect(researchRunTitle({ toolIds: ["trajectory.msd", "trajectory.diffusion"] }))
      .toBe("均方位移（MSD）与轨迹扩散");
  });

  it("uses the persisted user question when no scientific capability is more specific", () => {
    expect(researchRunTitle({ userQuestion: "比较两个结构的稳定性" }))
      .toBe("比较两个结构的稳定性");
  });

  it("keeps a bounded fallback for runs without historical display evidence", () => {
    expect(researchRunTitle({})).toBe("已完成的材料数据分析");
  });
});
