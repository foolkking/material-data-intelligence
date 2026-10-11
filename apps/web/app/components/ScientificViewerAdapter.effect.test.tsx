import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  getPlannerArtifactContent: vi.fn(),
}));

vi.mock("../lib/planner-api", () => ({
  getPlannerArtifactContent: mocks.getPlannerArtifactContent,
}));

vi.mock("next/link", () => ({
  default: ({ children, href, prefetch: _prefetch, ...props }: { children: React.ReactNode; href: string; prefetch?: boolean | null }) => (
    <a href={href} {...props}>{children}</a>
  ),
}));

vi.mock("../../scientific-viewers/workspace/WorkspaceArtifactGallery", () => ({
  ScientificArtifactRenderer: ({ selected, artifacts, delivery, workspace }: { selected: { artifactId?: string; type?: string; content?: unknown }; artifacts: Array<{ content?: unknown }>; delivery?: { context?: { primary?: { sampleRef?: string } } }; workspace: { datasetVersion?: string; sourceReferenceHash?: string } }) => (
    <div data-testid="loaded-scientific-renderer" data-selected={selected.artifactId || selected.type} data-sample={delivery?.context?.primary?.sampleRef}
      data-version={workspace.datasetVersion} data-scope={workspace.sourceReferenceHash}>{JSON.stringify(selected.content ?? artifacts[0]?.content)}</div>
  ),
}));

import { ScientificSourceViewer, ScientificResultViewer, selectProductRendererArtifact, selectResultViewerBundle, resultViewerLoadKey } from "./ScientificViewerAdapter";
import { validateWorkspaceSelectionContext } from "../../shared/workspace/workspace-selection-contract";

beforeEach(() => { mocks.getPlannerArtifactContent.mockReset(); });
afterEach(() => vi.useRealTimers());

it("puts the exact selected phonon resource first and retains only an unambiguous other-type companion", () => {
  const band = { objectId: "band_source", datasetId: "dataset", objectType: "PhononBand", payload: {} };
  const dos = { objectId: "dos_source", datasetId: "dataset", objectType: "PhononDos", payload: {} };
  const otherBand = { ...band, objectId: "second_band" };
  const view = render(<ScientificSourceViewer projectId="project" resource={otherBand} resources={[band, dos, otherBand]} />);
  expect(screen.getAllByTestId("loaded-scientific-renderer").map(item => item.dataset.selected)).toEqual(["source:second_band", "source:dos_source"]);
  view.rerender(<ScientificSourceViewer projectId="project" resource={dos} resources={[band, dos, otherBand]} />);
  expect(screen.getAllByTestId("loaded-scientific-renderer").map(item => item.dataset.selected)).toEqual(["source:dos_source"]);
});

it("keeps the explicitly selected electronic source primary when its companion is present", () => {
  const band = { objectId: "band_source", datasetId: "dataset", objectType: "ElectronicBand", payload: {} };
  const dos = { objectId: "dos_source", datasetId: "dataset", objectType: "ElectronicDos", payload: {} };
  const { rerender } = render(<ScientificSourceViewer projectId="project" resource={band} resources={[band, dos]} />);
  expect(screen.getByTestId("loaded-scientific-renderer")).toHaveAttribute("data-selected", "source:band_source");
  rerender(<ScientificSourceViewer projectId="project" resource={dos} resources={[band, dos]} />);
  expect(screen.getByTestId("loaded-scientific-renderer")).toHaveAttribute("data-selected", "source:dos_source");
});

it("renders the explicitly selected XRD or structure first and binds each view to its own version", () => {
  const xrd = { objectId: "xrd", datasetId: "d", versionId: "xrd-v1", objectHash: "a".repeat(64), objectType: "DataFrame", payload: { twoTheta: [20, 21], intensity: [1, 2] } };
  const laterXrd = { ...xrd, objectId: "xrd-second", versionId: "xrd-v2", objectHash: "b".repeat(64), payload: { twoTheta: [30, 31], intensity: [3, 4] } };
  const structure = { objectId: "structure", datasetId: "d", versionId: "structure-v1", objectHash: "c".repeat(64), objectType: "Structure", payload: {} };
  const { rerender } = render(<ScientificSourceViewer projectId="p" resource={laterXrd} resources={[xrd, structure, laterXrd]} />);
  let views = screen.getAllByTestId("loaded-scientific-renderer");
  expect(views.map(item => item.dataset.selected)).toEqual(["source:xrd-second", "source:structure"]);
  expect(views.map(item => [item.dataset.version, item.dataset.scope])).toEqual([["xrd-v2", laterXrd.objectHash], ["structure-v1", structure.objectHash]]);
  rerender(<ScientificSourceViewer projectId="p" resource={structure} resources={[laterXrd, structure]} />);
  views = screen.getAllByTestId("loaded-scientific-renderer");
  expect(views.map(item => item.dataset.selected)).toEqual(["source:structure", "source:xrd-second"]);
  expect(views.map(item => item.dataset.version)).toEqual(["structure-v1", "xrd-v2"]);
});

it("restores source selection only for its exact project, dataset, version and fingerprint", () => {
  const selection = validateWorkspaceSelectionContext({ schemaVersion: "1.0", sourceScopeHash: "a".repeat(64), primary: {
    selectionSchemaVersion: "1.0", kind: "DATASET_SAMPLE", sourceScopeHash: "a".repeat(64), projectId: "p", datasetId: "d", datasetVersion: "v1", objectId: "o", sampleRef: "sample-1",
  }, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false });
  const resource = { objectId: "o", datasetId: "d", versionId: "v1", objectHash: "a".repeat(64), objectType: "DataFrame", payload: [{ formula: "Fe" }] };
  const { rerender } = render(<ScientificSourceViewer projectId="p" resource={resource} selection={selection} />);
  expect(screen.getByTestId("loaded-scientific-renderer")).toHaveAttribute("data-sample", "sample-1");
  for (const changes of [{ datasetId: "foreign" }, { versionId: "v2" }, { objectHash: "b".repeat(64) }]) {
    rerender(<ScientificSourceViewer projectId="p" resource={{ ...resource, ...changes }} selection={selection} />);
    expect(screen.getByTestId("loaded-scientific-renderer")).not.toHaveAttribute("data-sample");
  }
  rerender(<ScientificSourceViewer projectId="other" resource={resource} selection={selection} />);
  expect(screen.getByTestId("loaded-scientific-renderer")).not.toHaveAttribute("data-sample");
});

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
    name: "主结果表",
    toolCallId: "tool_call_1",
    sha256: "a".repeat(64),
    sizeBytes: 28,
    contentType: "application/json",
  });
  const { rerender } = render(
    <ScientificResultViewer projectId="project_1" datasetId="dataset_1" jobId="job_1" selected={artifact()} artifacts={[artifact()]} />,
  );

  expect(screen.getByRole("status")).toHaveTextContent("正在加载科学结果");
  expect(screen.getByRole("status")).toHaveTextContent("科学结果已定位");
  expect(screen.getByText("artifact_1").closest("details")).not.toHaveAttribute("open");
  expect(screen.getByText("tool_call_1").closest("details")).not.toHaveAttribute("open");
  await userEvent.click(screen.getByText("技术来源与精确身份"));
  expect(screen.getByText("artifact_1")).toBeInTheDocument();
  expect(screen.getByText("tool_call_1")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "返回数据源" })).toHaveAttribute(
    "href",
    "/projects/project_1/data?dataset=dataset_1",
  );
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
  ].map(artifact => ({ ...artifact, toolCallId: "volume-call" }));

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
  const selected = { artifactId: "selected", jobId: "job_table", toolCallId: "table-call", type: "table_json", name: "主表", contentType: "application/json", sizeBytes: 1 };
  const companion = { artifactId: "companion", jobId: "job_table", toolCallId: "table-call", type: "table_json", name: "辅助表", contentType: "application/json", sizeBytes: 1 };
  render(<ScientificResultViewer projectId="project_1" datasetId="dataset_1" jobId="job_table" selected={selected} artifacts={[selected, companion]} />);
  await waitFor(() => expect(screen.getByTestId("loaded-scientific-renderer")).toHaveTextContent("Si"));
  expect(screen.queryByText("此结果暂时无法打开")).not.toBeInTheDocument();
  expect(screen.getByRole("status")).toHaveTextContent("辅助内容尚未完整读取");
  expect(screen.getByRole("status")).toHaveTextContent("辅助表");
  expect(screen.getByRole("status")).toHaveTextContent("内容格式校验失败");
});

it("distinguishes an unavailable exact Artifact from a transient Viewer failure", async () => {
  const user = userEvent.setup();
  const missing = Object.assign(new Error("The exact Artifact payload is currently unavailable."), {
    status: 404,
    details: {
      detail: {
        code: "ARTIFACT_CONTENT_NOT_FOUND",
        message: "The exact Artifact payload is currently unavailable.",
      },
    },
  });
  mocks.getPlannerArtifactContent
    .mockRejectedValueOnce(missing)
    .mockResolvedValueOnce(new TextEncoder().encode(JSON.stringify({ rows: [{ formula: "Si" }] })).buffer);
  const selected = {
    artifactId: "artifact_missing",
    jobId: "job_missing",
    type: "table_json",
    name: "missing table",
    contentType: "application/json",
    sizeBytes: 24,
    sha256: "b".repeat(64),
  };

  render(<ScientificResultViewer projectId="project_1" datasetId="dataset_1" jobId="job_missing" selected={selected} artifacts={[selected]} />);

  expect(
    await screen.findByRole("heading", { name: "原始结果内容当前不可用" }),
  ).toBeInTheDocument();
  expect(screen.getByRole("status")).toHaveTextContent("原始结果内容当前不可用");
  expect(screen.getByText("artifact_missing")).toBeInTheDocument();
  expect(screen.getByText("b".repeat(64))).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "返回数据源" })).toHaveAttribute(
    "href",
    "/projects/project_1/data?dataset=dataset_1",
  );
  expect(screen.queryByText("科学结果加载失败")).not.toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: "重新检查存储" }));
  await waitFor(() => expect(screen.getByTestId("loaded-scientific-renderer")).toHaveTextContent("Si"));
  expect(mocks.getPlannerArtifactContent).toHaveBeenCalledTimes(2);
});

it.each([
  {
    code: "ARTIFACT_CONTENT_GONE",
    status: 410,
    heading: "原始 Artifact 已永久不可用",
    detail: "不可通过重试恢复",
  },
  {
    code: "ARTIFACT_CONTENT_TOO_LARGE",
    status: 413,
    heading: "此 Artifact 超出安全浏览范围",
    detail: "系统未读取此大型 payload",
  },
])("shows a bounded non-retrying state for $status Artifact content", async ({
  code,
  status,
  heading,
  detail,
}) => {
  mocks.getPlannerArtifactContent.mockRejectedValueOnce(Object.assign(new Error(code), {
    status,
    details: { detail: { code } },
  }));
  const selected = {
    artifactId: `artifact_${status}`,
    jobId: `job_${status}`,
    type: "table_json",
    name: "bounded table",
    contentType: "application/json",
    sizeBytes: status === 413 ? 67_108_865 : 24,
    sha256: "c".repeat(64),
  };

  render(<ScientificResultViewer projectId="project_1" datasetId="dataset_1" jobId={`job_${status}`} selected={selected} artifacts={[selected]} />);

  expect(await screen.findByRole("heading", { name: heading })).toBeInTheDocument();
  expect(screen.getByRole("status")).toHaveTextContent(detail);
  expect(screen.queryByRole("button", { name: /重新/u })).not.toBeInTheDocument();
  expect(screen.getByText(`artifact_${status}`)).toBeInTheDocument();
  expect(screen.getByText("c".repeat(64))).toBeInTheDocument();
});

it("bounds composite phonon loads to the selected result bundle", () => {
  const selected = { artifactId: "combined", toolCallId: "combined-call", type: "phonon_band_dos_json", name: "phonon_band_dos.json" };
  const bundle = selectResultViewerBundle(selected, [
    selected,
    { artifactId: "combined-plot", type: "plotly_json", name: "phonon_band_dos_plot.json" },
    { artifactId: "combined-table", type: "table_json", name: "phonon_band_dos_table.json" },
    { artifactId: "band-table", type: "table_json", name: "phonon_band_table.json" },
    { artifactId: "dos-table", type: "table_json", name: "phonon_dos_table.json" },
  ].map(artifact => ({ ...artifact, toolCallId: "combined-call" })));
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

function deferredContent() {
  let resolve!: (value: ArrayBuffer) => void;
  const promise = new Promise<ArrayBuffer>((done) => { resolve = done; });
  return { promise, resolve };
}
const tableArtifact = (artifactId: string, sha256 = "a".repeat(64)) => ({
  artifactId, toolCallId: "table-call", type: "table_json", name: artifactId, sha256, contentType: "application/json", sizeBytes: 32,
});
const tableBytes = (formula: string) => new TextEncoder().encode(JSON.stringify({ rows: [{ formula }] })).buffer;

it("renders a selected table before a companion settles and preserves its DOM across failed retries", async () => {
  const stalled = deferredContent();
  let attempts = 0;
  mocks.getPlannerArtifactContent.mockImplementation((_job: string, id: string) => {
    if (id === "main") return Promise.resolve(tableBytes("Si"));
    attempts += 1;
    if (attempts === 1) return stalled.promise;
    if (attempts === 2) return Promise.reject(new Error("private-secret-provider-error"));
    return Promise.resolve(tableBytes("O"));
  });
  const main = tableArtifact("main");
  const auxiliary = tableArtifact("auxiliary");
  render(<ScientificResultViewer projectId="p" jobId="j" selected={main} artifacts={[main, auxiliary]} />);
  const body = await screen.findByTestId("loaded-scientific-renderer");
  expect(body).toHaveTextContent("Si");
  expect(screen.getByRole("status")).toHaveTextContent("auxiliary：正在读取");
  await act(async () => stalled.resolve(new TextEncoder().encode("invalid").buffer));
  fireEvent.click(screen.getByRole("button", { name: "重新加载缺失内容" }));
  await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("暂时无法读取"));
  expect(screen.getByTestId("loaded-scientific-renderer")).toBe(body);
  expect(document.body).not.toHaveTextContent("private-secret");
  fireEvent.click(screen.getByRole("button", { name: "重新加载缺失内容" }));
  await waitFor(() => expect(screen.queryByRole("status")).not.toBeInTheDocument());
  expect(screen.getByTestId("loaded-scientific-renderer")).toBe(body);
  expect(mocks.getPlannerArtifactContent.mock.calls.filter((call) => call[1] === "main")).toHaveLength(1);
});

it.each(["main", "auxiliary"])("times out %s independently and ignores its late response after retry", async (stalledId) => {
  vi.useFakeTimers();
  const stalled = deferredContent();
  let signal: AbortSignal | undefined;
  let attempts = 0;
  mocks.getPlannerArtifactContent.mockImplementation((_job: string, id: string, options: { signal: AbortSignal }) => {
    if (id !== stalledId) return Promise.resolve(tableBytes("retained"));
    if (++attempts === 1) { signal = options.signal; return stalled.promise; }
    return Promise.resolve(tableBytes("recovered"));
  });
  const main = tableArtifact("main");
  render(<ScientificResultViewer projectId="p" jobId="j" selected={main} artifacts={[main, tableArtifact("auxiliary")]} />);
  await act(async () => {});
  if (stalledId === "main") expect(screen.queryByTestId("loaded-scientific-renderer")).not.toBeInTheDocument();
  else expect(screen.getByTestId("loaded-scientific-renderer")).toHaveTextContent("retained");
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(signal?.aborted).toBe(true);
  expect(document.body).toHaveTextContent("读取超过 10 秒");
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: stalledId === "main" ? "重新加载" : "重新加载缺失内容" })); });
  const expected = stalledId === "main" ? "recovered" : "retained";
  expect(screen.getByTestId("loaded-scientific-renderer")).toHaveTextContent(expected);
  await act(async () => stalled.resolve(tableBytes("stale")));
  expect(screen.getByTestId("loaded-scientific-renderer")).toHaveTextContent(expected);
  expect(mocks.getPlannerArtifactContent.mock.calls.filter((call) => call[1] !== stalledId)).toHaveLength(1);
});

it("does not restart another pending companion when a failed companion is retried", async () => {
  const pending = deferredContent();
  mocks.getPlannerArtifactContent.mockImplementation((_job: string, id: string) => id === "main"
    ? Promise.resolve(tableBytes("Si")) : id === "pending" ? pending.promise : Promise.reject(new Error("offline")));
  const main = tableArtifact("main");
  const { unmount } = render(<ScientificResultViewer projectId="p" jobId="j" selected={main} artifacts={[main, tableArtifact("pending"), tableArtifact("failed")]} />);
  await screen.findByRole("button", { name: "重新加载缺失内容" });
  fireEvent.click(screen.getByRole("button", { name: "重新加载缺失内容" }));
  await screen.findByRole("button", { name: "重新加载缺失内容" });
  expect(mocks.getPlannerArtifactContent.mock.calls.filter((call) => call[1] === "pending")).toHaveLength(1);
  const signal = mocks.getPlannerArtifactContent.mock.calls.find((call) => call[1] === "pending")?.[2].signal;
  expect(signal.aborted).toBe(false);
  unmount();
  expect(signal.aborted).toBe(true);
  await act(async () => pending.resolve(tableBytes("late")));
});

it.each(["selected", "hash", "job", "project", "dataset", "producer"])("clears the previous scientific body immediately on a changed %s identity", async (change) => {
  const later = deferredContent();
  mocks.getPlannerArtifactContent.mockResolvedValue(tableBytes("old-result"));
  const main = tableArtifact("main");
  const other = tableArtifact("other");
  const props = { projectId: "p", datasetId: "d", jobId: "j", selected: main, artifacts: [main, other] };
  const { rerender } = render(<ScientificResultViewer {...props} />);
  await screen.findByTestId("loaded-scientific-renderer");
  mocks.getPlannerArtifactContent.mockReturnValue(later.promise);
  const next = { ...props };
  if (change === "selected") next.selected = other;
  if (change === "hash") { next.selected = tableArtifact("main", "b".repeat(64)); next.artifacts = [next.selected, other]; }
  if (change === "job") next.jobId = "next-job";
  if (change === "project") next.projectId = "next-project";
  if (change === "dataset") next.datasetId = "next-dataset";
  if (change === "producer") { next.selected = { ...main, toolCallId: "new-call" }; next.artifacts = [next.selected]; }
  rerender(<ScientificResultViewer {...next} />);
  expect(screen.queryByTestId("loaded-scientific-renderer")).not.toBeInTheDocument();
  await act(async () => later.resolve(tableBytes("new-result")));
  expect(screen.getByTestId("loaded-scientific-renderer")).toHaveTextContent("new-result");
});

it("prunes changed companion payloads without rereading the selected result", async () => {
  const old = deferredContent();
  const next = deferredContent();
  let calls = 0;
  mocks.getPlannerArtifactContent.mockImplementation((_job: string, id: string) => id === "main"
    ? Promise.resolve(tableBytes("Si")) : ++calls === 1 ? old.promise : next.promise);
  const main = tableArtifact("main");
  const { rerender } = render(<ScientificResultViewer projectId="p" jobId="j" selected={main} artifacts={[main, tableArtifact("aux")]} />);
  const body = await screen.findByTestId("loaded-scientific-renderer");
  const oldSignal = mocks.getPlannerArtifactContent.mock.calls[1][2].signal;
  rerender(<ScientificResultViewer projectId="p" jobId="j" selected={main} artifacts={[main, tableArtifact("aux", "b".repeat(64))]} />);
  expect(oldSignal.aborted).toBe(true);
  await act(async () => old.resolve(tableBytes("obsolete")));
  expect(screen.getByRole("status")).toHaveTextContent("正在读取");
  expect(screen.getByTestId("loaded-scientific-renderer")).toBe(body);
  await act(async () => next.resolve(tableBytes("current")));
  expect(screen.queryByRole("status")).not.toBeInTheDocument();
  expect(mocks.getPlannerArtifactContent.mock.calls.filter((call) => call[1] === "main")).toHaveLength(1);
});

it.each(["message", "detail"])("does not expose an arbitrary provider %s in failure details", async (source) => {
  const secret = "private-provider-token-or-local-path";
  mocks.getPlannerArtifactContent.mockRejectedValue(source === "message" ? new Error(secret)
    : { details: { detail: { code: secret } } });
  const main = tableArtifact("main");
  render(<ScientificResultViewer projectId="p" jobId="j" selected={main} artifacts={[main]} />);
  await screen.findByRole("alert");
  expect(document.body).not.toHaveTextContent(secret);
  expect(screen.getByRole("alert")).toHaveTextContent("ARTIFACT_CONTENT_LOAD_FAILED");
});

it("does not offer a retry for a permanently missing companion", async () => {
  mocks.getPlannerArtifactContent.mockImplementation((_job: string, id: string) => id === "main"
    ? Promise.resolve(tableBytes("Si")) : Promise.reject({ details: { detail: { code: "ARTIFACT_CONTENT_GONE" } } }));
  const main = tableArtifact("main");
  render(<ScientificResultViewer projectId="p" jobId="j" selected={main} artifacts={[main, tableArtifact("auxiliary")]} />);
  await screen.findByTestId("loaded-scientific-renderer");
  expect(screen.getByRole("status")).toHaveTextContent("auxiliary：原始内容已永久不可用");
  expect(screen.queryByRole("button", { name: /重新/u })).not.toBeInTheDocument();
});

it.each([
  ["phonon_band_dos_json", "phonon_band_dos.json", "table_json", "phonon_band_dos_table.json"],
  ["phonon_band_json", "phonon_band.json", "table_json", "phonon_band_table.json"],
  ["phonon_dos_json", "phonon_dos.json", "table_json", "phonon_dos_table.json"],
  ["electronic_band_json", "band.json", "electronic_dos_json", "dos.json"],
  ["volumetric_dataset_json", "volumetric_dataset.json", "volumetric_binary", "field.f64"],
  ["table_json", "coordination.json", "plotly_json", "coordination_plot.json"],
])("isolates %s companions across materials and jobs", (type, name, companionType, companionName) => {
  const selected = { artifactId: "selected", jobId: "job", toolCallId: "call-si", type, name };
  const companion = { artifactId: "own-companion", jobId: "job", toolCallId: "call-si", type: companionType, name: companionName };
  const foreign = { ...companion, artifactId: "other-material", toolCallId: "call-cu" };
  const foreignJob = { ...companion, artifactId: "other-job", jobId: "other-job" };
  expect(selectResultViewerBundle(selected, [foreign, foreignJob, companion, selected]).map(item => item.artifactId))
    .toEqual(["own-companion", "selected"]);
});

it("does not infer a historical result bundle from matching filenames or types", () => {
  const selected = { artifactId: "selected", type: "phonon_band_json", name: "phonon_band.json" };
  expect(selectResultViewerBundle(selected, [selected, { artifactId: "unknown", type: "table_json", name: "phonon_band_table.json" }]))
    .toEqual([selected]);
});

it("accepts consistent saved producer aliases without confusing call IDs with step IDs", () => {
  const selected = { artifactId: "selected", type: "table_json", metadata: { tool_call_id: "call-a" } };
  const own = { artifactId: "own", type: "table_json", provenance: { toolCallId: "call-a" } };
  const step = { artifactId: "step", type: "table_json", metadata: { stepId: "call-a" } };
  const conflicting = { artifactId: "conflicting", type: "table_json", toolCallId: "call-a", metadata: { tool_call_id: "call-b" } };
  expect(selectResultViewerBundle(selected, [own, step, conflicting, selected])).toEqual([own, selected]);
  expect(selectResultViewerBundle(conflicting, [conflicting, own])).toEqual([conflicting]);
});

it("never requests another material's auxiliary payload while the selected one is unavailable", async () => {
  const main = { ...tableArtifact("main"), jobId: "j", toolCallId: "si-call" };
  const own = { ...tableArtifact("own"), jobId: "j", toolCallId: "si-call" };
  const foreign = { ...tableArtifact("cu"), jobId: "j", toolCallId: "cu-call" };
  mocks.getPlannerArtifactContent.mockImplementation((_job: string, id: string) => id === "main"
    ? Promise.reject(new Error("ARTIFACT_CONTENT_NOT_FOUND")) : Promise.resolve(tableBytes(id)));
  render(<ScientificResultViewer projectId="p" jobId="j" selected={main} artifacts={[foreign, own, main]} />);
  await screen.findByRole("heading", { name: "原始结果内容当前不可用" });
  expect(mocks.getPlannerArtifactContent.mock.calls.map(call => call[1]).sort()).toEqual(["main", "own"]);
  expect(screen.queryByTestId("loaded-scientific-renderer")).not.toBeInTheDocument();
});

it("invalidates result reads when their saved producer identity changes", () => {
  const selected = { ...tableArtifact("main"), toolCallId: "si-call" };
  expect(resultViewerLoadKey("j", [selected])).not.toBe(resultViewerLoadKey("j", [{ ...selected, toolCallId: "cu-call" }]));
});

it("uses the enclosing job to exclude foreign companions when historical selected metadata omits it", () => {
  const selected = tableArtifact("main");
  const own = { ...tableArtifact("own"), jobId: "job" };
  const foreign = { ...tableArtifact("foreign"), jobId: "other-job" };
  expect(selectResultViewerBundle(selected, [selected, own, foreign], "job")).toEqual([selected, own]);
});

it.each([false, true])("rejects a selected artifact from another job before reading or rendering it (inline: %s)", async (inline) => {
  const selected = { ...tableArtifact("foreign"), jobId: "other-job", ...(inline ? { content: { rows: [{ formula: "Cu" }] } } : {}) };
  render(<ScientificResultViewer projectId="p" jobId="j" selected={selected} artifacts={[selected]} />);
  expect(await screen.findByRole("alert")).toHaveTextContent("结果与当前任务的来源不一致");
  expect(screen.queryByTestId("loaded-scientific-renderer")).not.toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "重新加载" })).not.toBeInTheDocument();
  expect(mocks.getPlannerArtifactContent).not.toHaveBeenCalled();
});

it("cancels a companion whose producer changes without rereading the selected artifact", async () => {
  const pending = deferredContent();
  mocks.getPlannerArtifactContent.mockImplementation((_job: string, id: string) => id === "main"
    ? Promise.resolve(tableBytes("Si")) : pending.promise);
  const main = tableArtifact("main");
  const auxiliary = tableArtifact("aux");
  const { rerender } = render(<ScientificResultViewer projectId="p" jobId="j" selected={main} artifacts={[main, auxiliary]} />);
  const body = await screen.findByTestId("loaded-scientific-renderer");
  const signal = mocks.getPlannerArtifactContent.mock.calls.find(call => call[1] === "aux")![2].signal;
  rerender(<ScientificResultViewer projectId="p" jobId="j" selected={main} artifacts={[main, { ...auxiliary, toolCallId: "other-material" }]} />);
  expect(signal.aborted).toBe(true);
  await act(async () => pending.resolve(tableBytes("Cu")));
  expect(screen.getByTestId("loaded-scientific-renderer")).toBe(body);
  expect(screen.queryByRole("status")).not.toBeInTheDocument();
  expect(mocks.getPlannerArtifactContent).toHaveBeenCalledTimes(2);
});
