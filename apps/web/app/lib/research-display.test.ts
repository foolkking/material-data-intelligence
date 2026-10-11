import { describe, expect, it } from "vitest";

import { researchRunFailureMessage, researchRunSourceDatasets, researchRunTitle } from "./research-display";

describe("researchRunSourceDatasets", () => {
  const datasets = [
    { datasetId: "si", name: "Si 晶体" },
    { datasetId: "cu", name: "Cu 晶体" },
    { datasetId: "nacl", name: "NaCl 晶体" },
  ];
  it("keeps every exact source in saved order without duplicating a dataset", () => {
    expect(researchRunSourceDatasets({ datasetId: "si", sourceDatasetIds: ["cu", "si", "nacl", "cu"] }, datasets))
      .toEqual([datasets[1], datasets[0], datasets[2]]);
  });
  it("uses the routing dataset only for older records without a source inventory", () => {
    expect(researchRunSourceDatasets({ datasetId: "si" }, datasets)).toEqual([datasets[0]]);
    expect(researchRunSourceDatasets({ datasetId: "si", sourceDatasetIds: [] }, datasets)).toEqual([]);
    expect(researchRunSourceDatasets({ datasetId: "si", sourceDatasetIds: ["missing"] }, datasets))
      .toEqual([{ datasetId: "missing", name: "来源数据不可用" }]);
  });
});

describe("researchRunFailureMessage", () => {
  it.each([
    ["TOOL_INPUT_INVALID: Requested target column does not exist.", "目标列不存在"],
    ["TOOL_INPUT_INVALID: private input details", "输入未通过工具校验"],
    ["Requested DataProfile is unavailable for this dataset.", "数据描述无法读取"],
  ])("explains the persisted failure %s", (message, expected) => {
    expect(researchRunFailureMessage([{ eventType: "job.failed", message }])).toContain(expected);
  });

  it("does not expose raw worker exceptions or infer failure from a running event", () => {
    expect(researchRunFailureMessage([{ eventType: "job.failed", message: "Traceback secret=private-value" }])).not.toMatch(/Traceback|private-value/);
    expect(researchRunFailureMessage([{ eventType: "tool.started", message: "TOOL_INPUT_INVALID: private value" }])).toContain("没有可展示的具体原因");
  });
});

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
    expect(researchRunTitle({})).toBe("材料数据分析");
  });

  it("does not infer scientific columns or completion from a generic tool identity", () => {
    expect(researchRunTitle({ toolIds: ["data.correlation"] })).toBe("材料属性相关性分析");
    expect(researchRunTitle({ toolIds: ["data.correlation"], userQuestion: "比较温度与电导率" })).toBe("比较温度与电导率");
    expect(researchRunTitle({})).not.toContain("完成");
  });
});
