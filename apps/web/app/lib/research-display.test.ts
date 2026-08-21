import { describe, expect, it } from "vitest";

import { researchRunTitle } from "./research-display";

describe("researchRunTitle", () => {
  it("names legacy static RDF runs from their persisted tool identity", () => {
    expect(researchRunTitle({ toolIds: ["structure.rdf"] }))
      .toBe("静态结构径向分布函数（RDF）");
  });

  it("uses the persisted user question when no scientific capability is more specific", () => {
    expect(researchRunTitle({ userQuestion: "比较两个结构的稳定性" }))
      .toBe("比较两个结构的稳定性");
  });

  it("keeps a bounded fallback for runs without historical display evidence", () => {
    expect(researchRunTitle({})).toBe("已完成的材料数据分析");
  });
});
