import { expect, it } from "vitest";
import { reportFindingPresentation } from "./scientific-report-findings";

const limit = "数据为合成测试样本，不能据此断言真实材料预测能力或泛化性能。";
const assessment = { accepted: true, scope: "合成回归数据，4096 行", limitations: [limit] };
const findings = [
  { statement: `MAE 为 0.06367252119238281。${limit}`, reasoning_assessment: assessment },
  { statement: `RMSE 为 0.07072364590422509。${limit}`, reasoning_assessment: assessment },
];

it("groups an exact complete limitation without changing any saved finding or number", () => {
  const saved = JSON.stringify(findings);
  const view = reportFindingPresentation(findings);
  expect(view.sharedLimitations).toEqual([limit]);
  expect(view.statements).toEqual(["MAE 为 0.06367252119238281。", "RMSE 为 0.07072364590422509。"]);
  view.statements.forEach((statement, i) => expect(statement + view.sharedLimitations.join("")).toBe(findings[i].statement));
  expect(JSON.stringify(findings)).toBe(saved);
});

it.each([
  { scope: "另一批样本" }, { scope: "current ScientificResult scope" }, { accepted: false }, { limitations: [] },
])("keeps scope-specific or unverified qualifications attached: %o", change => {
  const source = findings.map((item, i) => i ? { ...item, reasoning_assessment: { ...assessment, ...change } } : item);
  expect(reportFindingPresentation(source)).toEqual({ statements: source.map(item => item.statement), sharedLimitations: [] });
});

it("keeps single, unassessed, partial-sentence and non-suffix limitations unchanged", () => {
  for (const source of [findings.slice(0, 1), findings.map(({ statement }) => ({ statement })),
    findings.map(item => ({ ...item, statement: `结果仅当${limit}` })),
    findings.map(item => ({ ...item, statement: `${item.statement}此外还受其他约束。` })),
    findings.map(item => ({ ...item, statement: limit })),
  ]) expect(reportFindingPresentation(source)).toEqual({ statements: source.map(item => item.statement), sharedLimitations: [] });
});

it("preserves the order of multiple common limitations and unique per-finding text", () => {
  const second = "数值未声明物理单位。";
  const source = findings.map((item, i) => ({ statement: `发现 ${i} 的完整限定。${item.statement}${second}`,
    reasoning_assessment: { ...assessment, limitations: [second, limit] } }));
  const view = reportFindingPresentation(source);
  expect(view.sharedLimitations).toEqual([limit, second]);
  view.statements.forEach((statement, i) => expect(statement + view.sharedLimitations.join("")).toBe(source[i].statement));
});
