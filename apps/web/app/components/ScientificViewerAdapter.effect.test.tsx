import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  getPlannerArtifactContent: vi.fn(),
}));

vi.mock("../lib/planner-api", () => ({
  getPlannerArtifactContent: mocks.getPlannerArtifactContent,
}));

vi.mock("./workspace/WorkspaceArtifactGallery", () => ({
  ScientificArtifactRenderer: ({ selected, artifacts }: { selected: { artifactId?: string; type?: string; content?: unknown }; artifacts: Array<{ content?: unknown }> }) => (
    <div data-testid="loaded-scientific-renderer" data-selected={selected.artifactId || selected.type}>{JSON.stringify(selected.content ?? artifacts[0]?.content)}</div>
  ),
}));

import { ScientificResultViewer, selectProductRendererArtifact, selectResultViewerBundle } from "./ScientificViewerAdapter";

beforeEach(() => mocks.getPlannerArtifactContent.mockReset());

it("keeps an in-flight artifact load across equivalent polling prop identities", async () => {
  let resolveContent: (value: ArrayBuffer) => void = () => undefined;
  mocks.getPlannerArtifactContent.mockReturnValue(new Promise<ArrayBuffer>((resolve) => {
    resolveContent = resolve;
  }));
  const artifact = () => ({
    artifactId: "artifact_1",
    jobId: "job_1",
    type: "table_json",
    version: "1",
    sha256: "a".repeat(64),
    sizeBytes: 28,
    contentType: "application/json",
  });
  const { rerender } = render(
    <ScientificResultViewer projectId="project_1" datasetId="dataset_1" jobId="job_1" selected={artifact()} artifacts={[artifact()]} />,
  );

  expect(screen.getByRole("status")).toHaveTextContent("正在加载科学结果");
  rerender(
    <ScientificResultViewer projectId="project_1" datasetId="dataset_1" jobId="job_1" selected={artifact()} artifacts={[artifact()]} />,
  );
  expect(mocks.getPlannerArtifactContent).toHaveBeenCalledTimes(1);

  resolveContent(new TextEncoder().encode(JSON.stringify({ rows: [{ formula: "BaTiO3" }] })).buffer);

  await waitFor(() => expect(screen.getByTestId("loaded-scientific-renderer")).toHaveTextContent("BaTiO3"));
  expect(mocks.getPlannerArtifactContent).toHaveBeenCalledTimes(1);
});

it("keeps volumetric binary and markdown auxiliary outputs out of JSON decoding", async () => {
  mocks.getPlannerArtifactContent.mockImplementation(async (_jobId: string, artifactId: string) => {
    if (artifactId === "dataset") return new TextEncoder().encode(JSON.stringify({ schema_version: "phase10j.volumetric_dataset.v1" })).buffer;
    if (artifactId === "recipe") return new TextEncoder().encode(JSON.stringify({ schemaVersion: "recipe/1" })).buffer;
    if (artifactId === "summary") return new TextEncoder().encode("# Volumetric summary").buffer;
    return new Uint8Array([0x1f, 0x8b, 0x08, 0x00]).buffer;
  });
  const artifacts = [
    { artifactId: "dataset", jobId: "job_volume", type: "volumetric_dataset_json", name: "volumetric_dataset.json", contentType: "application/json", sizeBytes: 1 },
    { artifactId: "binary", jobId: "job_volume", type: "volumetric_binary", name: "field.f64.gz", contentType: "application/json", sizeBytes: 4 },
    { artifactId: "summary", jobId: "job_volume", type: "summary_md", name: "summary.md", contentType: "application/json", sizeBytes: 1 },
    { artifactId: "recipe", jobId: "job_volume", type: "recipe_json", name: "recipe.json", contentType: "application/json", sizeBytes: 1 },
  ];

  render(
    <ScientificResultViewer projectId="project_1" datasetId="dataset_1" jobId="job_volume" selected={artifacts[0]} artifacts={artifacts} />,
  );

  await waitFor(() => expect(screen.getByTestId("loaded-scientific-renderer")).toHaveTextContent("phase10j.volumetric_dataset.v1"));
  expect(mocks.getPlannerArtifactContent).toHaveBeenCalledTimes(4);
});

it("keeps the selected result readable when an optional companion fails", async () => {
  mocks.getPlannerArtifactContent.mockImplementation(async (_jobId: string, artifactId: string) => {
    if (artifactId === "selected") return new TextEncoder().encode(JSON.stringify({ rows: [{ formula: "Si" }] })).buffer;
    return new TextEncoder().encode("{invalid-json").buffer;
  });
  const selected = { artifactId: "selected", jobId: "job_table", type: "table_json", name: "主表", contentType: "application/json", sizeBytes: 1 };
  const companion = { artifactId: "companion", jobId: "job_table", type: "table_json", name: "辅助表", contentType: "application/json", sizeBytes: 1 };
  render(<ScientificResultViewer projectId="project_1" datasetId="dataset_1" jobId="job_table" selected={selected} artifacts={[selected, companion]} />);
  await waitFor(() => expect(screen.getByTestId("loaded-scientific-renderer")).toHaveTextContent("Si"));
  expect(screen.queryByText("此结果暂时无法打开")).not.toBeInTheDocument();
});

it("bounds composite phonon loads to the selected result bundle", () => {
  const selected = { artifactId: "combined", type: "phonon_band_dos_json", name: "phonon_band_dos.json" };
  const bundle = selectResultViewerBundle(selected, [
    selected,
    { artifactId: "combined-plot", type: "plotly_json", name: "phonon_band_dos_plot.json" },
    { artifactId: "combined-table", type: "table_json", name: "phonon_band_dos_table.json" },
    { artifactId: "band-table", type: "table_json", name: "phonon_band_table.json" },
    { artifactId: "dos-table", type: "table_json", name: "phonon_dos_table.json" },
  ]);
  expect(bundle.map((item) => item.artifactId)).toEqual(["combined", "combined-plot", "combined-table"]);
});

it("loads only the exact ToolCall product pair for a selected scientific figure", () => {
  const selected = { artifactId: "comparison-plot", toolCallId: "call-comparison", type: "plotly_json", name: "experimental_xrd_comparison_plot.json" };
  const bundle = selectResultViewerBundle(selected, [
    { artifactId: "theory-table", toolCallId: "call-theory", type: "table_json", name: "xrd_pattern.json" },
    { artifactId: "theory-plot", toolCallId: "call-theory", type: "plotly_json", name: "xrd_plot.json" },
    { artifactId: "comparison-table", toolCallId: "call-comparison", type: "table_json", name: "experimental_xrd_comparison.json" },
    selected,
  ]);
  expect(bundle.map((item) => item.artifactId)).toEqual(["comparison-table", "comparison-plot"]);
});

it("promotes the validated product contract instead of flattening its figure to a generic plot", () => {
  const selected = {
    artifactId: "comparison-plot",
    toolCallId: "call-comparison",
    type: "plotly_json",
    content: { figure: { data: [] } },
  };
  const product = {
    artifactId: "comparison-table",
    toolCallId: "call-comparison",
    type: "table_json",
    content: {
      schema_version: "phase10n3.experimental_xrd_comparison.v1",
      artifactType: "structure.experimental_xrd_comparison",
    },
  };
  expect(selectProductRendererArtifact(selected, [selected, product])).toBe(product);
});

it("renders a selected XRD figure through its same-ToolCall professional product contract", async () => {
  const selected = { artifactId: "comparison-plot", jobId: "job_xrd", toolCallId: "call-comparison", type: "plotly_json", name: "experimental_xrd_comparison_plot.json", contentType: "application/json", sizeBytes: 1 };
  const product = { artifactId: "comparison-table", jobId: "job_xrd", toolCallId: "call-comparison", type: "table_json", name: "experimental_xrd_comparison.json", contentType: "application/json", sizeBytes: 1 };
  mocks.getPlannerArtifactContent.mockImplementation(async (_jobId: string, artifactId: string) => new TextEncoder().encode(JSON.stringify(
    artifactId === "comparison-table"
      ? { schema_version: "phase10n3.experimental_xrd_comparison.v1", artifactType: "structure.experimental_xrd_comparison" }
      : { figure: { data: [] } },
  )).buffer);
  render(<ScientificResultViewer projectId="project_1" datasetId="dataset_1" jobId="job_xrd" selected={selected} artifacts={[product, selected]} />);
  await waitFor(() => expect(screen.getByTestId("loaded-scientific-renderer")).toHaveAttribute("data-selected", "comparison-table"));
  expect(mocks.getPlannerArtifactContent).toHaveBeenCalledTimes(2);
});
