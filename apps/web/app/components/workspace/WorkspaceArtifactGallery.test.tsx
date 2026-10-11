import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";

import type { Artifact } from "../../lib/planner-api";
import {
  ScientificArtifactRenderer,
  WorkspaceArtifactGallery,
} from "./WorkspaceArtifactGallery";
import { workspaceSnapshotFixture } from "./workspace-test-fixture";
import { datasetSampleSelection, type WorkspaceSelectionDelivery } from "../../../shared/workspace/workspace-selection-runtime";

const mocks = vi.hoisted(() => ({
  getPlannerJobArtifacts: vi.fn(),
}));

vi.mock("../../lib/planner-api", async () => ({
  ...(await vi.importActual("../../lib/planner-api")),
  getPlannerJobArtifacts: mocks.getPlannerJobArtifacts,
}));

// Plot rendering has its own component and browser coverage. Keep these
// gallery/table interactions independent of Plotly's canvas/WebGL runtime.
vi.mock("../../../scientific-viewers/workspace/WorkspaceGenericPlot", () => ({
  WorkspaceGenericPlot: () => <div data-testid="plot-preview" />,
}));

it("keeps gallery ARIA identities unique when multiple workspaces share a page", async () => {
  mocks.getPlannerJobArtifacts.mockResolvedValue([]);
  const snapshot = workspaceSnapshotFixture();
  const panel = snapshot.panels.find((item) => item.panelKind === "SCIENTIFIC_RESULT");
  expect(panel).toBeDefined();

  const { container } = render(
    <>
      <WorkspaceArtifactGallery
        workspace={snapshot.workspace}
        panel={panel!}
        delivery={null}
        onSelection={() => undefined}
        onNavigateReference={() => undefined}
      />
      <WorkspaceArtifactGallery
        workspace={snapshot.workspace}
        panel={panel!}
        delivery={null}
        onSelection={() => undefined}
        onNavigateReference={() => undefined}
      />
    </>,
  );

  await waitFor(() => expect(mocks.getPlannerJobArtifacts).toHaveBeenCalledTimes(2));
  const galleries = [
    ...container.querySelectorAll<HTMLElement>("section.workspace-artifact-gallery"),
  ];
  expect(galleries).toHaveLength(2);
  const labelledBy = galleries.map((gallery) => gallery.getAttribute("aria-labelledby"));
  expect(labelledBy.every(Boolean)).toBe(true);
  expect(new Set(labelledBy).size).toBe(2);
  labelledBy.forEach((id, index) => {
    expect(galleries[index].querySelector(`#${id}`)).toHaveTextContent("Result gallery");
  });
  const allIds = [...container.querySelectorAll<HTMLElement>("[id]")].map((node) => node.id);
  expect(new Set(allIds).size).toBe(allIds.length);
});

it("shows and searches scientific unit symbols only in controlled conversion tables", async () => {
  const content = { schemaVersion: "mdi.project.parameter-table/1.0", artifactType: "reference.convert_units", sampleAnalysis: false,
    rows: [{ "原单位": "nm", "原数值": 0.5, "换算结果": 5, "目标单位": "angstrom" }] };
  const original = JSON.stringify(content);
  const artifact: Artifact = { id: "conversion", type: "table_json", version: "1", content };
  render(<ScientificArtifactRenderer selected={artifact} workspace={workspaceSnapshotFixture().workspace} />);
  expect(screen.getByRole("cell", { name: "Å" })).toBeInTheDocument();
  expect(screen.queryByRole("cell", { name: "angstrom" })).not.toBeInTheDocument();
  expect(screen.getAllByRole("columnheader").map(cell => cell.textContent)).toEqual(["原数值", "原单位", "换算结果", "目标单位"]);
  await userEvent.type(screen.getByRole("searchbox"), "Å");
  expect(screen.getByRole("cell", { name: "5" })).toBeInTheDocument();
  expect(screen.queryByRole("columnheader", { name: "选择" })).not.toBeInTheDocument();
  expect(JSON.stringify(content)).toBe(original);
});

it("renders saved scalar metrics without inventing selectable samples or units", async () => {
  const artifact = { id: "metrics", artifactId: "metrics", jobId: "job_demo", toolCallId: "tool_call_demo", type: "metrics_json", version: "1", name: "metrics.json", content: { metrics: { n: 4, mae: 0.125, rmse: 0.1322875655532295, r2: null }, targetColumn: "y_true", predictionColumn: "y_pred" } } as Artifact;
  render(<ScientificArtifactRenderer selected={artifact} artifacts={[artifact]} workspace={workspaceSnapshotFixture().workspace} />);
  expect(screen.getByRole("rowheader", { name: "平均绝对误差（MAE）" })).toBeInTheDocument();
  expect(screen.getByRole("cell", { name: "≈ 0.1322876" })).toHaveAttribute("title", "完整数值：0.1322875655532295");
  expect(screen.getByRole("cell", { name: "0.125" })).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "完整数值" }));
  expect(screen.getByRole("button", { name: "完整数值" })).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByRole("cell", { name: "0.1322875655532295" })).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "完整数值" }));
  expect(screen.getByRole("cell", { name: "≈ 0.1322876" })).toBeInTheDocument();
  expect(screen.getByRole("cell", { name: "未提供" })).toBeInTheDocument();
  expect(screen.getByText("目标列：y_true")).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /选择样本/u })).not.toBeInTheDocument();
  expect(screen.getByLabelText("结构化数据 JSON")).not.toBeVisible();
  await userEvent.click(screen.getByText("数据与来源"));
  expect(screen.getByLabelText("结构化数据 JSON")).toBeVisible();
  expect(screen.getByLabelText("结构化数据 JSON")).toHaveTextContent('"rmse": 0.1322875655532295');
  expect(screen.getByText("job_demo")).toBeVisible();
  expect(screen.getByText("tool_call_demo")).toBeVisible();
});

it("shows exact plot coordinates with axis labels without inventing empty fields or sample identities", async () => {
  const artifact: Artifact = { id: "xrd-numeric", type: "plotly_json", content: { figure: {
    data: [{ type: "scatter", name: "实验 XRD", x: [30, 31, 32], y: [1, null, 3] }],
    layout: { xaxis: { title: { text: "2θ (°)" } }, yaxis: { title: { text: "强度 (a.u.)" } } },
  } } };
  render(<ScientificArtifactRenderer selected={artifact} artifacts={[artifact]} workspace={workspaceSnapshotFixture().workspace} />);
  await userEvent.click(screen.getByText("查看数值数据 · 3 行"));
  expect(screen.getAllByRole("columnheader").map(cell => cell.textContent)).toEqual(["序号", "2θ (°)", "强度 (a.u.)"]);
  expect(screen.getByRole("cell", { name: "31" })).toBeInTheDocument();
  expect(screen.getByRole("cell", { name: "缺失" })).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /选择样本/u })).not.toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "2θ (°)" }));
  expect(screen.getByRole("columnheader", { name: "2θ (°) ↑" })).toHaveAttribute("aria-sort", "ascending");
  await userEvent.type(screen.getByRole("searchbox"), "32");
  expect(screen.getAllByRole("row")).toHaveLength(2);
  await userEvent.clear(screen.getByRole("searchbox"));
  await userEvent.type(screen.getByRole("searchbox"), "缺失");
  expect(screen.getAllByRole("row")).toHaveLength(2);
  expect(screen.getByRole("cell", { name: "31" })).toBeInTheDocument();
});

it("discloses the full numerical point count while bounding plot table search and rendering", async () => {
  const artifact: Artifact = { id: "large-plot", type: "plotly_json", content: { data: [{ type: "scatter", x: Array.from({ length: 1005 }, (_, i) => i), y: Array(1005).fill(0) }] } };
  render(<ScientificArtifactRenderer selected={artifact} artifacts={[artifact]} workspace={workspaceSnapshotFixture().workspace} />);
  await userEvent.click(screen.getByText("查看数值数据 · 1000 行"));
  expect(screen.getByRole("note")).toHaveTextContent("仅预览前 1,000 行（全表 1,005 行），搜索与排序仅限预览。");
  expect(screen.getByRole("searchbox")).toHaveAttribute("placeholder", "搜索预览内容");
  expect(screen.getAllByRole("row")).toHaveLength(101);
  await userEvent.type(screen.getByRole("searchbox"), "1004");
  expect(screen.getByText("预览范围内没有匹配项。")).toBeInTheDocument();
});

it("does not call a bounded trace inventory the full table", async () => {
  const artifact: Artifact = { id: "many-series", type: "plotly_json", content: { data: Array.from({ length: 130 }, () => ({ x: [1], y: [2] })) } };
  render(<ScientificArtifactRenderer selected={artifact} artifacts={[artifact]} workspace={workspaceSnapshotFixture().workspace} />);
  await userEvent.click(screen.getByText("查看数值数据 · 128 行"));
  expect(screen.getByText(/已读取系列共 128 行/)).toBeVisible();
  expect(screen.queryByText(/全表/)).not.toBeInTheDocument();
  expect(screen.getByRole("searchbox")).toHaveAttribute("placeholder", "搜索预览内容");
  expect(screen.getByText(/另有 2 个数据系列未展开/)).toBeVisible();
});

it("shows saved undefined R² once, without treating it as missing", () => {
  const artifact = { id: "metrics", artifactId: "metrics", jobId: "job_demo", toolCallId: "tool_call_demo", type: "metrics_json", version: "1", name: "metrics.json", content: { metrics: { n: 3, mae: 0, r2: null, r2Status: "undefined_constant_target" }, targetColumn: "y_true", predictionColumn: "y_pred" } } as Artifact;
  render(<ScientificArtifactRenderer selected={artifact} artifacts={[artifact]} workspace={workspaceSnapshotFixture().workspace} />);
  expect(screen.getByRole("cell", { name: "未定义（目标值为常量）" })).toBeInTheDocument();
  expect(screen.queryByRole("rowheader", { name: "r2Status" })).not.toBeInTheDocument();
  expect(screen.queryByRole("cell", { name: "未提供" })).not.toBeInTheDocument();
});

it("keeps stable sample identity visible while exposing deliberate horizontal scrolling", async () => {
  const artifact: Artifact = {
    id: "artifact_table",
    artifactId: "artifact_table",
    jobId: "job_demo",
    toolCallId: "tool_call_demo",
    type: "table_json",
    version: "1",
    name: "材料属性表",
    content: {
      rows: [
        {
          objectId: "object_table",
          sampleRef: "mat-2",
          formula: "BaTiO3",
          band_gap: 3.2,
          formation_energy: -2.45,
          density: 6.02,
        },
      ],
    },
  };
  const onSelection = vi.fn();

  render(
    <ScientificArtifactRenderer
      selected={artifact}
      artifacts={[artifact]}
      workspace={workspaceSnapshotFixture().workspace}
      onSelection={onSelection}
    />,
  );

  const tableRegion = screen.getByRole("region", {
    name: "数据表，可横向滚动查看完整列",
  });
  expect(screen.queryByText("左右滑动查看完整属性；选择操作固定在左侧。")).not.toBeInTheDocument();
  Object.defineProperties(tableRegion, { scrollWidth: { configurable: true, value: 800 }, clientWidth: { configurable: true, value: 320 } });
  fireEvent(window, new Event("resize"));
  expect(screen.getByText("左右滑动查看完整属性；选择操作固定在左侧。")).toBeInTheDocument();
  expect(tableRegion).toHaveAttribute("tabindex", "0");
  const descriptionId = tableRegion.getAttribute("aria-describedby");
  expect(descriptionId).toBeTruthy();
  expect(document.getElementById(descriptionId ?? "")).toHaveTextContent(
    "选择操作固定在左侧",
  );
  expect(screen.getByRole("columnheader", { name: "选择" })).toHaveClass(
    "workspace-table-identity-column",
  );
  expect(screen.getByRole("button", { name: "选择样本 mat-2" })).toHaveAttribute("title", "mat-2");
  expect(screen.queryByRole("columnheader", { name: "sampleRef" })).not.toBeInTheDocument();
  expect(screen.queryByRole("columnheader", { name: "objectId" })).not.toBeInTheDocument();
  await userEvent.click(screen.getByText("列显示"));
  await userEvent.click(screen.getByRole("checkbox", { name: "sampleRef" }));
  expect(screen.getByRole("columnheader", { name: "sampleRef" })).toBeInTheDocument();
  expect(screen.getAllByText("mat-2")).not.toHaveLength(0);
  fireEvent.keyDown(screen.getByRole("checkbox", { name: "sampleRef" }), { key: "Escape" });
  expect(screen.getByRole("button", { name: "列显示" })).toHaveFocus();
  expect(screen.getByRole("button", { name: "列显示" })).toHaveAttribute("aria-expanded", "false");

  await userEvent.click(
    screen.getByRole("button", { name: "选择样本 mat-2" }),
  );
  expect(screen.getByRole("button", { name: "选择样本 mat-2" })).toHaveAttribute("aria-pressed", "true");
  expect(onSelection).toHaveBeenCalledWith(
    expect.objectContaining({
      primary: expect.objectContaining({
        kind: "DATASET_SAMPLE",
        objectId: "object_table",
        sampleRef: "mat-2",
      }),
    }),
  );
  await userEvent.type(screen.getByRole("searchbox", { name: "搜索" }), "no-match");
  expect(screen.getByText("没有匹配的样本。")).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "清除搜索" }));
  expect(screen.getByRole("button", { name: "选择样本 mat-2" })).toBeInTheDocument();
  Object.defineProperty(tableRegion, "clientWidth", { configurable: true, value: 900 });
  fireEvent(window, new Event("resize"));
  expect(tableRegion).not.toHaveAttribute("aria-describedby");
});

it("omits sample controls from numeric tables without inventing identity while retaining search and sort", async () => {
  const artifact: Artifact = { id: "plain-table", type: "table_json", version: "1", content: { rows: [{ formula: "Fe", value: 3 }, { formula: "Si", value: 1 }] } };
  const onSelection = vi.fn();
  render(<ScientificArtifactRenderer selected={artifact} workspace={workspaceSnapshotFixture().workspace} onSelection={onSelection} />);
  expect(screen.queryByRole("columnheader", { name: "选择" })).not.toBeInTheDocument();
  expect(screen.queryByText("不可选择")).not.toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "value" }));
  expect(screen.getAllByRole("row")[1]).toHaveTextContent("Si");
  await userEvent.type(screen.getByRole("searchbox"), "no-match");
  expect(screen.getByText("没有匹配的数据。")).toHaveAttribute("colspan", "2");
  await userEvent.click(screen.getByRole("button", { name: "清除搜索" }));
  expect(screen.getAllByRole("row")).toHaveLength(3);
  expect(onSelection).not.toHaveBeenCalled();
});

it("keeps valid rows selectable in mixed tables and requires a dataset version", async () => {
  const artifact: Artifact = { id: "mixed-table", type: "table_json", version: "1", content: { rows: [{ sampleRef: "sample-1", formula: "Fe" }, { formula: "Si" }] } };
  const workspace = workspaceSnapshotFixture().workspace;
  const onSelection = vi.fn();
  const view = render(<ScientificArtifactRenderer selected={artifact} workspace={workspace} onSelection={onSelection} />);
  expect(screen.getByText("无样本标识")).toBeInTheDocument();
  expect(screen.getAllByRole("button", { name: /选择样本/ })).toHaveLength(1);
  await userEvent.click(screen.getByRole("button", { name: "选择样本 sample-1" }));
  expect(onSelection).toHaveBeenCalledWith(expect.objectContaining({ primary: expect.objectContaining({ datasetId: workspace.datasetId, datasetVersion: workspace.datasetVersion, sampleRef: "sample-1" }) }));
  view.rerender(<ScientificArtifactRenderer selected={artifact} workspace={{ ...workspace, datasetVersion: null }} onSelection={onSelection} />);
  expect(screen.queryByRole("columnheader", { name: "选择" })).not.toBeInTheDocument();
  view.rerender(<ScientificArtifactRenderer selected={{ ...artifact, content: { rows: [{ objectId: "source-1", sampleRef: "sample-1", formula: "Fe" }] } }} workspace={{ ...workspace, datasetVersion: null }} onSelection={onSelection} />);
  expect(screen.getByRole("columnheader", { name: "sampleRef" })).toBeInTheDocument();
  expect(screen.getByRole("cell", { name: "source-1" })).toBeInTheDocument();
});

it("restores and clears a generic table's canonical sample highlight without emitting another selection", async () => {
  const workspace = workspaceSnapshotFixture().workspace;
  const artifact: Artifact = { id: "artifact-table", type: "table_json", version: "1", content: { rows: [{ objectId: "child-object", sampleRef: "sample-1", formula: "Fe" }] } };
  const onSelection = vi.fn();
  const delivery: WorkspaceSelectionDelivery = { panelId: "source", originPanelId: null, compatibility: "EXACT", reason: "restored", transaction: 0, context: datasetSampleSelection(workspace, { objectId: "child-object", sampleRef: "sample-1", sampleKey: "child-object:sample-1" }) };
  const { rerender } = render(<ScientificArtifactRenderer selected={artifact} artifacts={[artifact]} workspace={workspace} delivery={delivery} onSelection={onSelection} />);
  expect(await screen.findByRole("button", { name: "选择样本 sample-1" })).toHaveAttribute("aria-pressed", "true");
  expect(onSelection).not.toHaveBeenCalled();
  rerender(<ScientificArtifactRenderer selected={artifact} artifacts={[artifact]} workspace={workspace} delivery={null} onSelection={onSelection} />);
  expect(screen.getByRole("button", { name: "选择样本 sample-1" })).toHaveAttribute("aria-pressed", "false");
});

it("keeps large table controls reachable through a focused horizontal scroll region", () => {
  const artifact: Artifact = {
    id: "artifact_wide",
    artifactId: "artifact_wide",
    jobId: "job_demo",
    toolCallId: "tool_call_demo",
    type: "table_json",
    version: "1",
    name: "宽科学表",
    content: { rows: [{ sample_id: "sample-1", formula: "BaTiO3", very_long_authoritative_column_name: "value" }] },
  };
  render(
    <ScientificArtifactRenderer
      selected={artifact}
      artifacts={[artifact]}
      workspace={workspaceSnapshotFixture().workspace}
    />,
  );
  const region = screen.getByRole("region", { name: "数据表，可横向滚动查看完整列" });
  expect(region).toHaveAttribute("tabindex", "0");
  expect(region.querySelector("table")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "选择样本 sample-1" })).toBeInTheDocument();
});

it("reports the visible range and total rows while paging a bounded scientific table", async () => {
  const user = userEvent.setup();
  const consoleError = vi.spyOn(console, "error").mockImplementation(() => undefined);
  const rows = Array.from({ length: 205 }, (_, index) => ({
    objectId: "object_table",
    sample_id: `mat-${index + 1}`,
    formula: index % 2 ? "SiO2" : "Si",
    band_gap: index / 100,
  }));
  const artifact: Artifact = {
    id: "artifact_large_table",
    artifactId: "artifact_large_table",
    jobId: "job_demo",
    toolCallId: "tool_call_demo",
    type: "table_json",
    version: "1",
    name: "大数据集结果",
    content: { rows },
  };

  render(
    <ScientificArtifactRenderer
      selected={artifact}
      artifacts={[artifact]}
      workspace={workspaceSnapshotFixture().workspace}
    />,
  );

  expect(screen.getByTestId("workspace-table-count")).toHaveTextContent(
    "1-100 / 205 行",
  );
  const previous = screen.getByRole("button", { name: "数据表上一页" });
  const next = screen.getByRole("button", { name: "数据表下一页" });
  expect(previous).toBeDisabled();
  expect(next).toBeEnabled();
  expect(screen.getByRole("button", { name: "选择样本 mat-1" })).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "选择样本 mat-101" })).not.toBeInTheDocument();

  await user.click(next);
  expect(screen.getByTestId("workspace-table-count")).toHaveTextContent(
    "101-200 / 205 行",
  );
  expect(previous).toBeEnabled();
  expect(next).toBeEnabled();

  await user.click(next);
  expect(screen.getByTestId("workspace-table-count")).toHaveTextContent(
    "201-205 / 205 行",
  );
  expect(next).toBeDisabled();
  expect(screen.getByRole("button", { name: "选择样本 mat-205" })).toBeInTheDocument();
  expect(consoleError).not.toHaveBeenCalledWith(expect.stringContaining("same key"));
  consoleError.mockRestore();
});

it("keeps columns beyond the former 32-column cutoff searchable, sortable and individually visible", async () => {
  const row = Object.fromEntries(Array.from({ length: 64 }, (_, index) => [`property_${index + 1}`, index]));
  const artifact: Artifact = { id: "many-columns", type: "table_json", version: "1", content: { rows: [{ ...row, property_64: 999 }, { ...row, property_64: 1 }] } };
  render(<ScientificArtifactRenderer selected={artifact} workspace={workspaceSnapshotFixture().workspace} />);
  expect(screen.getAllByRole("columnheader")).toHaveLength(64);
  await userEvent.click(screen.getByRole("button", { name: "property_64" }));
  expect(screen.getAllByRole("row")[1].lastElementChild).toHaveTextContent("1");
  await userEvent.click(screen.getByRole("button", { name: "列显示" }));
  await userEvent.click(screen.getByRole("checkbox", { name: "property_64" }));
  expect(screen.queryByRole("columnheader", { name: /property_64/ })).not.toBeInTheDocument();
  await userEvent.click(screen.getByRole("checkbox", { name: "property_64" }));
  expect(screen.getByRole("columnheader", { name: /property_64/ })).toHaveAttribute("aria-sort", "ascending");
  await userEvent.type(screen.getByRole("searchbox"), "999");
  expect(screen.getByRole("cell", { name: "999" })).toBeInTheDocument();
  expect(screen.getAllByRole("row")).toHaveLength(2);
});

it("includes fields first encountered on a later preview page", async () => {
  const rows: Record<string, unknown>[] = Array.from({ length: 260 }, (_, index) => ({ measurement: index }));
  rows[259].late_property = "late measurement";
  const artifact: Artifact = { id: "sparse-columns", type: "table_json", version: "1", content: { rows } };
  render(<ScientificArtifactRenderer selected={artifact} workspace={workspaceSnapshotFixture().workspace} />);
  expect(screen.getByRole("columnheader", { name: "late_property" })).toBeInTheDocument();
  await userEvent.type(screen.getByRole("searchbox"), "late measurement");
  expect(screen.getByRole("cell", { name: "late measurement" })).toBeInTheDocument();
  expect(screen.getAllByRole("row")).toHaveLength(2);
});

it("makes bounded search explicit and keeps repeated-formula samples distinct through filtering", async () => {
  const rows = Array.from({ length: 1005 }, (_, index) => ({ sample_id: `ml-${index}`, formula: "LiFePO4", value: index }));
  const artifact: Artifact = { id: "bounded-table", type: "table_json", version: "1", content: { rows } };
  const onSelection = vi.fn();
  render(<ScientificArtifactRenderer selected={artifact} workspace={workspaceSnapshotFixture().workspace} onSelection={onSelection} />);
  const search = screen.getByRole("searchbox");
  const note = screen.getByText("仅预览前 1,000 行（全表 1,005 行），搜索与排序仅限预览。");
  expect(search).toHaveAttribute("aria-describedby", note.id);
  expect(search).toHaveAttribute("placeholder", "搜索预览内容");
  expect(screen.getByTestId("workspace-table-count")).toHaveTextContent("显示 1-100 行 · 3 列");
  await userEvent.click(screen.getByRole("button", { name: "选择样本 ml-8" }));
  expect(onSelection).toHaveBeenLastCalledWith(expect.objectContaining({ primary: expect.objectContaining({ sampleRef: "ml-8" }) }));
  fireEvent.change(search, { target: { value: "ml-1004" } });
  expect(screen.getByText("预览范围内没有匹配项。")).toBeInTheDocument();
  expect(screen.getByTestId("workspace-table-count")).toHaveTextContent("匹配 0 行 · 3 列");
  expect(screen.queryByRole("button", { name: "选择样本 ml-1004" })).not.toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "清除搜索" }));
  expect(screen.getByRole("button", { name: "选择样本 ml-8" })).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByRole("button", { name: "选择样本 ml-0" })).toHaveAttribute("aria-pressed", "false");
  expect(rows).toHaveLength(1005);
});

it("fails closed with researcher-facing copy when the exact payload is missing", () => {
  const artifact: Artifact = {
    id: "artifact_missing",
    artifactId: "artifact_missing",
    jobId: "job_demo",
    toolCallId: "tool_call_demo",
    type: "unknown_payload",
    version: "1",
    name: "缺失资源",
    content: undefined,
    contentHash: "d".repeat(64),
  };

  render(
    <ScientificArtifactRenderer
      selected={artifact}
      artifacts={[artifact]}
      workspace={workspaceSnapshotFixture().workspace}
    />,
  );

  expect(screen.getByRole("heading", { name: "当前资源没有可用的专业查看器" })).toBeInTheDocument();
  expect(screen.getByText(/不会执行未知组件/)).toBeInTheDocument();
  expect(screen.getByText("查看技术详情")).toBeInTheDocument();
  expect(screen.getByText("unknown_payload@1")).toBeInTheDocument();
});

it("renders metadata-only scientific files as an explicit safe state", () => {
  const artifact: Artifact = {
    id: "artifact-preview",
    artifactId: "artifact-preview",
    jobId: "job_demo",
    type: "preview_png",
    version: "1",
    name: "structure-preview.png",
    content: undefined,
    sizeBytes: 4096,
    sha256: "a".repeat(64),
  };

  render(
    <ScientificArtifactRenderer
      selected={artifact}
      artifacts={[artifact]}
      workspace={workspaceSnapshotFixture().workspace}
    />,
  );

  expect(screen.getByRole("status", { name: "科学资源元数据" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "原始文件保留，可查看元数据" })).toBeInTheDocument();
  expect(screen.getByText("preview_png@1")).toBeInTheDocument();
  expect(screen.getByText("4.0 KiB")).toBeInTheDocument();
  expect(screen.getByText(/没有被替换、重算或伪装成图片预览/)).toBeInTheDocument();
});

it("keeps download-only scientific files inert and researcher-readable", () => {
  const artifact: Artifact = {
    id: "artifact-html",
    artifactId: "artifact-html",
    jobId: "job_demo",
    type: "plotly_html",
    version: "1",
    name: "plot.html",
    content: "<script>alert(1)</script>",
    sizeBytes: 120,
    contentType: "text/html",
  };

  render(
    <ScientificArtifactRenderer
      selected={artifact}
      artifacts={[artifact]}
      workspace={workspaceSnapshotFixture().workspace}
    />,
  );

  expect(screen.getByRole("status", { name: "科学资源下载" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "该资源通过安全下载访问" })).toBeInTheDocument();
  expect(screen.queryByText(/alert/)).not.toBeInTheDocument();
});
