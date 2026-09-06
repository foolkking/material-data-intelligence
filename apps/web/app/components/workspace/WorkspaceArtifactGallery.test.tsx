import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";

import type { Artifact } from "../../lib/planner-api";
import {
  ScientificArtifactRenderer,
  WorkspaceArtifactGallery,
} from "./WorkspaceArtifactGallery";
import { workspaceSnapshotFixture } from "./workspace-test-fixture";

const mocks = vi.hoisted(() => ({
  getPlannerJobArtifacts: vi.fn(),
}));

vi.mock("../../lib/planner-api", async () => ({
  ...(await vi.importActual("../../lib/planner-api")),
  getPlannerJobArtifacts: mocks.getPlannerJobArtifacts,
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

  expect(
    screen.getByText("左右滑动查看完整属性；样本身份与选择操作固定在左侧。"),
  ).toBeInTheDocument();
  const tableRegion = screen.getByRole("region", {
    name: "已验证的数据表，可横向滚动查看完整列",
  });
  expect(tableRegion).toHaveAttribute("tabindex", "0");
  const descriptionId = tableRegion.getAttribute("aria-describedby");
  expect(descriptionId).toBeTruthy();
  expect(document.getElementById(descriptionId ?? "")).toHaveTextContent(
    "样本身份与选择操作固定在左侧",
  );
  expect(screen.getByRole("columnheader", { name: "样本 / 选择" })).toHaveClass(
    "workspace-table-identity-column",
  );
  expect(screen.getAllByText("mat-2")).not.toHaveLength(0);
  expect(screen.getByRole("columnheader", { name: "sampleRef" })).toBeInTheDocument();

  await userEvent.click(
    screen.getByRole("button", { name: "选择样本 mat-2" }),
  );
  expect(onSelection).toHaveBeenCalledWith(
    expect.objectContaining({
      primary: expect.objectContaining({
        kind: "DATASET_SAMPLE",
        objectId: "object_table",
        sampleRef: "mat-2",
      }),
    }),
  );
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
  const region = screen.getByRole("region", { name: "已验证的数据表，可横向滚动查看完整列" });
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
    "当前显示 1-100 / 205 行。",
  );
  const previous = screen.getByRole("button", { name: "数据表上一页" });
  const next = screen.getByRole("button", { name: "数据表下一页" });
  expect(previous).toBeDisabled();
  expect(next).toBeEnabled();
  expect(screen.getByRole("button", { name: "选择样本 mat-1" })).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "选择样本 mat-101" })).not.toBeInTheDocument();

  await user.click(next);
  expect(screen.getByTestId("workspace-table-count")).toHaveTextContent(
    "当前显示 101-200 / 205 行。",
  );
  expect(previous).toBeEnabled();
  expect(next).toBeEnabled();

  await user.click(next);
  expect(screen.getByTestId("workspace-table-count")).toHaveTextContent(
    "当前显示 201-205 / 205 行。",
  );
  expect(next).toBeDisabled();
  expect(screen.getByRole("button", { name: "选择样本 mat-205" })).toBeInTheDocument();
  expect(consoleError).not.toHaveBeenCalledWith(expect.stringContaining("same key"));
  consoleError.mockRestore();
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
