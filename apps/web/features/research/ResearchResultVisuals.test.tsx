import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import type { ScientificPresentationBlock } from "../../app/lib/scientific-presentation";
import { ResearchResultVisuals } from "./ResearchResultVisuals";
import type { Agent2ResearchTurnResult } from "../../app/lib/agent2-research-api";
import { resolveResultVisualTarget } from "./result-navigation";

vi.mock("../../scientific-viewers/LazyScientificViewers", () => ({
  LazyScientificResultViewer: ({ jobId, selected }: { jobId: string; selected: { artifactId: string } }) =>
    <div data-testid="scientific-view">{jobId}:{selected.artifactId}</div>,
}));
const block = (id: string, type: "figure" | "table", jobId = "job-1") => ({
  id, type, title: id, artifactId: id, source: { resultId: "result-1", jobId, artifactId: id },
} as Extract<ScientificPresentationBlock, { type: "figure" | "table" }>);
const artifacts = ["table", "figure"].map((artifactId) => ({ artifactId, jobId: "job-1", type: "table_json" }));

it("opens the saved figure first, switches one exact output, and returns focus after closing", async () => {
  const user = userEvent.setup();
  const props = { blocks: [block("table", "table"), block("figure", "figure")], artifacts, projectId: "project-1", instanceId: "turn-1", facts: [] };
  const view = render(<ResearchResultVisuals {...props} />);
  expect(screen.getByTestId("scientific-view")).toHaveTextContent("job-1:figure");
  expect(screen.getByRole("button", { name: "figure" })).toHaveAttribute("aria-pressed", "true");
  await user.click(screen.getByRole("button", { name: "table" }));
  expect(screen.getAllByTestId("scientific-view")).toHaveLength(1);
  expect(screen.getByTestId("scientific-view")).toHaveTextContent("job-1:table");
  expect(screen.getByRole("link", { name: "查看源文件" })).toHaveAttribute("href", "/api/planner/jobs/job-1/artifacts/table/content");
  await user.click(screen.getByRole("button", { name: "收起视图" }));
  expect(screen.queryByTestId("scientific-view")).toBeNull();
  expect(screen.getByRole("button", { name: "table" })).toHaveFocus();
  view.rerender(<ResearchResultVisuals {...props} artifacts={[...artifacts]} />);
  expect(screen.queryByTestId("scientific-view")).toBeNull();
  await user.click(screen.getByRole("button", { name: "figure" }));
  expect(screen.getByTestId("scientific-view")).toHaveTextContent("job-1:figure");
});

it("does not bind a foreign or ambiguous artifact and resets selection when exact output identity changes", async () => {
  const user = userEvent.setup();
  const props = { blocks: [block("figure", "figure")], artifacts, projectId: "project-1", instanceId: "turn-1", facts: [] };
  const view = render(<ResearchResultVisuals {...props} artifacts={[{ artifactId: "figure", jobId: "foreign", type: "plotly_json" }]} />);
  expect(screen.queryByTestId("scientific-view")).toBeNull();
  view.rerender(<ResearchResultVisuals {...props} artifacts={[artifacts[1], artifacts[1]]} />);
  expect(screen.queryByTestId("scientific-view")).toBeNull();
  view.rerender(<ResearchResultVisuals {...props} />);
  await user.click(screen.getByRole("button", { name: "收起视图" }));
  view.rerender(<ResearchResultVisuals {...props} blocks={[block("figure", "figure", "job-2")]}
    artifacts={[{ artifactId: "figure", jobId: "job-2", type: "plotly_json" }]} />);
  expect(screen.getByTestId("scientific-view")).toHaveTextContent("job-2:figure");
});

it("keeps many outputs in one accessible selector with exact switching and close focus", async () => {
  const user = userEvent.setup();
  const names = ["Si.cif RDF", "Cu.cif RDF", "NaCl.cif RDF", "Si.cif data", "Cu.cif data", "NaCl.cif data"];
  render(<ResearchResultVisuals blocks={names.map((name, index) => block(name, index < 3 ? "figure" : "table"))}
    artifacts={names.map((artifactId) => ({ artifactId, jobId: "job-1", type: "plotly_json" }))}
    projectId="project-1" instanceId="turn-1" facts={[]} />);
  const selector = screen.getByRole("combobox", { name: "选择结果视图" });
  expect(selector).toHaveValue("Si.cif RDF");
  await user.selectOptions(selector, "Cu.cif RDF");
  expect(screen.getAllByTestId("scientific-view")).toHaveLength(1);
  expect(screen.getByTestId("scientific-view")).toHaveTextContent("job-1:Cu.cif RDF");
  await user.click(screen.getByRole("button", { name: "收起视图" }));
  expect(selector).toHaveFocus();
  expect(selector).toHaveValue("");
  await user.selectOptions(selector, "NaCl.cif data");
  expect(screen.getByTestId("scientific-view")).toHaveTextContent("job-1:NaCl.cif data");
});

const materialNames = ["NaCl.cif", "Si.cif", "Cu.cif"];
const savedResult = {
  result_snapshot_id: "saved-snapshot", result_items: materialNames.map(name => ({ id: name, artifact_ids: [`${name}-data`, name] })),
} as Agent2ResearchTurnResult;
const materialProps = {
  blocks: materialNames.flatMap(name => [block(`${name}-data`, "table"), block(name, "figure")]),
  artifacts: materialNames.flatMap(name => [name, `${name}-data`]).map(artifactId => ({ artifactId, jobId: "job-1", type: "plotly_json" })),
  projectId: "project-1", instanceId: "turn-1", facts: [],
};

it("opens a cited material instead of the first figure and restores it after manual selection, repeated opening, and refresh", async () => {
  const user = userEvent.setup();
  const citation = { snapshotId: "saved-snapshot", itemId: "Cu.cif" };
  const view = render(<ResearchResultVisuals {...materialProps} target={resolveResultVisualTarget(savedResult, citation)} />);
  const selector = screen.getByRole("combobox", { name: "选择结果视图" });
  expect(selector).toHaveValue("Cu.cif");
  expect(screen.getByTestId("scientific-view")).toHaveTextContent("job-1:Cu.cif");
  await user.selectOptions(selector, "Si.cif");
  view.rerender(<ResearchResultVisuals {...materialProps} target={resolveResultVisualTarget(savedResult, citation)} />);
  expect(selector).toHaveValue("Si.cif");
  view.rerender(<ResearchResultVisuals {...materialProps} target={resolveResultVisualTarget(savedResult, { ...citation, requestKey: 1 })} />);
  expect(selector).toHaveValue("Cu.cif");
  await user.click(screen.getByRole("button", { name: "收起视图" }));
  expect(screen.queryByTestId("scientific-view")).not.toBeInTheDocument();
  view.rerender(<ResearchResultVisuals {...materialProps} target={resolveResultVisualTarget(savedResult, { ...citation, itemId: "Si.cif" })} />);
  expect(selector).toHaveValue("Si.cif");
  view.unmount();
  render(<ResearchResultVisuals {...materialProps} target={resolveResultVisualTarget(savedResult, citation)} />);
  expect(screen.getByTestId("scientific-view")).toHaveTextContent("job-1:Cu.cif");
});

it.each(["wrong-snapshot", "unknown-item", "duplicate-item"])("never substitutes the first figure for a %s citation and permits explicit recovery", async issue => {
  const result = issue === "duplicate-item" ? { ...savedResult, result_items: [...savedResult.result_items, savedResult.result_items[2]] } : savedResult;
  const target = resolveResultVisualTarget(result, { snapshotId: issue === "wrong-snapshot" ? "other-snapshot" : "saved-snapshot", itemId: issue === "unknown-item" ? "missing" : "Cu.cif" });
  render(<ResearchResultVisuals {...materialProps} target={target} />);
  expect(screen.queryByTestId("scientific-view")).not.toBeInTheDocument();
  expect(screen.getByRole("status")).toHaveTextContent("这条引用的结果项当前无法定位");
  await userEvent.setup().selectOptions(screen.getByRole("combobox", { name: "选择结果视图" }), "Si.cif");
  expect(screen.getByTestId("scientific-view")).toHaveTextContent("job-1:Si.cif");
});

it("clears a manually recovered view when the saved snapshot changes even if the artifact identifiers are shared", async () => {
  const citation = { snapshotId: "saved-snapshot", itemId: "Cu.cif" };
  const other = { ...savedResult, result_snapshot_id: "other-snapshot" };
  const view = render(<ResearchResultVisuals {...materialProps} target={resolveResultVisualTarget(other, citation)} />);
  await userEvent.setup().selectOptions(screen.getByRole("combobox", { name: "选择结果视图" }), "Si.cif");
  view.rerender(<ResearchResultVisuals {...materialProps} target={resolveResultVisualTarget({ ...other, result_snapshot_id: "third-snapshot" }, citation)} />);
  expect(screen.queryByTestId("scientific-view")).not.toBeInTheDocument();
  view.rerender(<ResearchResultVisuals {...materialProps} target={resolveResultVisualTarget(savedResult, citation)} />);
  expect(screen.getByTestId("scientific-view")).toHaveTextContent("job-1:Cu.cif");
  view.rerender(<ResearchResultVisuals {...materialProps} />);
  expect(screen.getByTestId("scientific-view")).toHaveTextContent("job-1:NaCl.cif");
});
