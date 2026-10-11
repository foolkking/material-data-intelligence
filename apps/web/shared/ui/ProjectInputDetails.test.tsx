import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it } from "vitest";
import { ProjectInputDetails } from "./ProjectInputDetails";

const input = {
  tool_call_id: "table-call", tool_id: "viz.inline_xy", input_origin: "USER_TEXT_DATA",
  content_hash: "a".repeat(64), resolved_parameters: { data_text: "时间(s),位移(nm)\n0,0\n1,2", x_column: 0, y_columns: [1], style: "line" },
};
const provenance = { execution_scope: "PROJECT", input_origin: "USER_TEXT_DATA", parameter_inputs: [input] };

it("keeps exact input text and identity available on demand without mutating the saved record", async () => {
  const before = JSON.stringify(provenance), user = userEvent.setup();
  render(<ProjectInputDetails provenance={provenance} />);
  const summary = screen.getByText("输入参数与原始数据");
  expect(summary.closest("details")).not.toHaveAttribute("open");
  await user.click(summary);
  expect(screen.getByText("输入数据绘图 · 输入表格")).toBeVisible();
  const table = screen.getByLabelText("原始输入表格");
  expect(table.textContent).toBe(input.resolved_parameters.data_text);
  expect(table).toHaveAttribute("tabindex", "0");
  expect(screen.getByText("输入标识").closest("details")).not.toHaveAttribute("open");
  await user.click(screen.getByText("输入标识"));
  expect(screen.getByText(input.content_hash)).toBeVisible();
  expect(JSON.stringify(provenance)).toBe(before);
});

it("keeps separate function objects and multiple input origins readable", async () => {
  render(<ProjectInputDetails provenance={{ ...provenance, input_origin: "MIXED", parameter_inputs: [input, {
    tool_call_id: "curve-call", tool_id: "generation.function_curve", input_origin: "USER_PARAMETERS", content_hash: "b".repeat(64),
    resolved_parameters: { functions: [{ kind: "polynomial", coefficients: [-1, 0, 1] }, { kind: "sine", amplitude: 2 }], point_count: 101 },
  }] }} />);
  await userEvent.click(screen.getByText("输入参数与原始数据"));
  expect(screen.getByText("输入数据绘图 · 输入表格")).toBeVisible();
  expect(screen.getByText("函数曲线 · 输入参数")).toBeVisible();
  expect(screen.getByText("-1、0、1")).toBeVisible();
  expect(screen.getByText("正弦")).toBeVisible();
  expect(screen.queryByText("[object Object]")).not.toBeInTheDocument();
});

it.each([
  { ...provenance, execution_scope: "DATASET" },
  { ...provenance, parameter_inputs: [{ ...input, content_hash: "invalid" }] },
  { ...provenance, parameter_inputs: [{ ...input, input_origin: "IDEAL_MODEL" }] },
  { ...provenance, parameter_inputs: [{ ...input, tool_id: "unknown" }] },
  { ...provenance, parameter_inputs: [input, { ...input, content_hash: "b".repeat(64) }] },
])("does not turn unbound or ambiguous parameter data into a source", source => {
  render(<ProjectInputDetails provenance={source} />);
  expect(screen.queryByText("输入参数与原始数据")).not.toBeInTheDocument();
});
