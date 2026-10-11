import { expect, it } from "vitest";
import { reportLimitationPresentation } from "./scientific-limitation-text";

it("coalesces reviewed translations and aliases without losing references or changing saved limitations", () => {
  const items = [
    { statement: "No center-of-mass drift correction is applied.", source_refs: ["source.a"] },
    { statement: "未应用质心漂移校正。", source_refs: ["source.b", "source.a"] },
    { statement: " 本次结果未应用质心漂移校正。 ", source_refs: [] },
    { statement: "MSD uses Cartesian x/y/z axes and is not automatically crystallographic a/b/c diffusion.", source_refs: ["axes"] },
    { statement: "MSD使用笛卡尔x/y/z轴，非自动晶格a/b/c扩散。", source_refs: [] },
  ];
  const original = structuredClone(items);
  expect(reportLimitationPresentation(items)).toEqual([
    { statement: "本次结果未应用质心漂移校正。", source_refs: ["source.a", "source.b"] },
    { statement: "MSD 使用笛卡尔 x/y/z 轴，不会自动解释为晶体学 a/b/c 方向扩散。", source_refs: ["axes"] },
  ]);
  expect(items).toEqual(original);
});

it.each([
  ["仅适用于 1 m 的范围。", "仅适用于 1 M 的范围。"],
  ["拟合窗口为 0.08 ps。", "拟合窗口为 1.0 ps。"],
  ["未应用质心漂移校正。", "已应用质心漂移校正。"],
  ["未应用质心漂移校正。", "材料 A 未应用质心漂移校正。"],
  ["MSD使用笛卡尔x/y/z轴，非自动晶格a/b/c扩散。", "MSD使用笛卡尔z/y/x轴，非自动晶格a/b/c扩散。"],
])("retains distinct scientific statements: %s / %s", (first, second) => {
  const result = reportLimitationPresentation([first, second].map(statement => ({ statement, source_refs: [] })));
  expect(result).toHaveLength(2);
  expect(result[1].statement).toBe(second);
});

it("keeps unrecognized text verbatim, including object-property names", () => {
  const items = ["constructor", "__proto__", "toString", "未应用质心漂移校正。仅适用于本次拟合。"].map(statement => ({ statement, source_refs: [] }));
  expect(reportLimitationPresentation(items)).toEqual(items);
});
