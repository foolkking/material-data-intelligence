import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { encodeWorkspaceSelectionUrl, decodeWorkspaceSelectionUrl, validateWorkspaceSelectionContext, clearedWorkspaceSelection } from "../../../shared/workspace/workspace-selection-contract";
import type { WorkspaceSelectionContext } from "../../lib/workspace-api";

const mocks = vi.hoisted(() => ({
  getScientificViewerProjection: vi.fn(),
  getScientificObjectSummary: vi.fn(),
  getProjectHistory: vi.fn(),
  listResearchSessions: vi.fn(),
  updateScientificObject: vi.fn(),
}));

vi.mock("../../lib/scientific-viewer-api", () => ({
  getScientificViewerProjection: mocks.getScientificViewerProjection,
  getScientificObjectSummary: mocks.getScientificObjectSummary,
  updateScientificObject: mocks.updateScientificObject,
}));
vi.mock("../../lib/planner-api", () => ({ getProjectHistory: mocks.getProjectHistory }));
vi.mock("../../lib/product-api", () => ({ listResearchSessions: mocks.listResearchSessions }));
vi.mock("../../../scientific-viewers/ScientificViewerAdapter", () => ({
  ScientificSourceViewer: ({ selection, onSelection }: { selection?: WorkspaceSelectionContext | null; onSelection: (value: WorkspaceSelectionContext) => void }) => <div data-testid="source-viewer">source viewer<span data-testid="restored-sample">{selection?.primary?.sampleRef}</span><button type="button" onClick={() => onSelection(sampleSelection())}>选择样本</button><button type="button" onClick={() => onSelection(clearedWorkspaceSelection("a".repeat(64)))}>从图内清除选择</button><button type="button" onClick={() => onSelection(clearedWorkspaceSelection("c".repeat(64)))}>清除外部来源</button></div>,
}));
vi.mock("../../../shared/layout/ProductNavigation", () => ({
  ProductLink: ({ children, href, ...props }: { children: React.ReactNode; href: string }) => <a href={href} {...props}>{children}</a>,
}));

import { ScientificObjectViewer } from "./ScientificObjectViewer";
import { useScientificObjectOperation } from "../../../shared/workspace/scientific-object-operations";

const baseProjection = (
  payloadStatus: "READY" | "METADATA_ONLY" | "SOURCE_MISSING" | "INVALIDATED",
) => ({
  contract_version: "1.0",
  project_id: "project-1",
  object_id: "object-1",
  version_id: "version-1",
  object_type: "structure.crystal",
  object_schema_version: "1",
  display_name: "Silicon",
  version_no: 1,
  is_current_version: true,
  availability_status: payloadStatus === "READY"
    ? "AVAILABLE"
    : payloadStatus === "INVALIDATED"
      ? "INVALID"
      : payloadStatus === "METADATA_ONLY"
        ? "PARTIALLY_AVAILABLE"
        : "SOURCE_MISSING",
  viewer: {
    viewer_id: "structure-viewer",
    viewer_version: "1.0",
    renderer_key: "structure",
    support: "PROFESSIONAL",
    interaction_capabilities: [],
    selection_capabilities: [],
    maximum_payload_bytes: 1024,
    fallback_policy: "metadata",
  },
  payload_status: payloadStatus,
  payload: payloadStatus === "READY" ? { lattice: {}, sites: [] } : null,
  canonical_metadata: {},
  source_resource_refs: [],
  content_hash: "a".repeat(64),
  semantic_hash: "b".repeat(64),
  payload_bytes: payloadStatus === "READY" ? 10 : null,
  omitted_item_count: 0,
  limitations: ["原始来源当前不可访问"],
});

beforeEach(() => {
  mocks.getScientificViewerProjection.mockReset().mockResolvedValue(baseProjection("SOURCE_MISSING"));
  mocks.getScientificObjectSummary.mockReset().mockResolvedValue({ id: "object-1", project_id: "project-1", kind: "scientific_object", object_type: "structure.crystal", display_name: "Silicon", lifecycle_status: "ACTIVE", current_version_id: "version-1" });
  mocks.updateScientificObject.mockReset();
  mocks.getProjectHistory.mockReset().mockResolvedValue({ items: [] });
  mocks.listResearchSessions.mockReset().mockResolvedValue({ items: [] });
});

afterEach(() => { vi.useRealTimers(); window.history.replaceState({}, "", "/"); });

function sampleSelection(overrides: Record<string, string> = {}) {
  return validateWorkspaceSelectionContext({ schemaVersion: "1.0", sourceScopeHash: "a".repeat(64), primary: { selectionSchemaVersion: "1.0", kind: "DATASET_SAMPLE", sourceScopeHash: "a".repeat(64), projectId: "project-1", datasetId: "object-1", datasetVersion: "version-1", objectId: "child-resource", sampleRef: "sample-1", ...overrides }, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false });
}

it("clears the exact embedded selection and URL while rejecting a foreign source's clear event", async () => {
  mocks.getScientificViewerProjection.mockResolvedValue(baseProjection("READY"));
  window.history.replaceState({}, "", "/projects/project-1/data?object=object-1&version=version-1&keep=1");
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" canResearch />);
  fireEvent.click(await screen.findByRole("button", {name: "选择样本"}));
  const token = new URLSearchParams(window.location.search).get("selection");
  expect(token).toBeTruthy();
  fireEvent.click(screen.getByRole("button", {name: "清除外部来源"}));
  expect(new URLSearchParams(window.location.search).get("selection")).toBe(token);
  fireEvent.click(screen.getByRole("button", {name: "从图内清除选择"}));
  expect(new URLSearchParams(window.location.search).has("selection")).toBe(false);
  expect(new URLSearchParams(window.location.search).get("keep")).toBe("1");
  expect(screen.getByTestId("restored-sample")).toBeEmptyDOMElement();
  expect(screen.getByRole("link", {name: "研究此数据"})).not.toHaveAttribute("href", expect.stringContaining("selection="));
});

it.each(["valid", "channel", "artifact", "checksum", "type"])("validates the exact volumetric source when restoring a %s selection", async variant => {
  mocks.getScientificViewerProjection.mockResolvedValue({...baseProjection("READY"), object_type: variant === "type" ? "structure.crystal" : "volumetric.field", payload: { channels: [{ name: "scalar", values: [1, 2] }] }});
  const context = validateWorkspaceSelectionContext({schemaVersion: "1.0", sourceScopeHash: "a".repeat(64), primary: {selectionSchemaVersion: "1.0", kind: "VOLUMETRIC_FIELD", sourceScopeHash: "a".repeat(64), projectId: "project-1", datasetId: "object-1", datasetVersion: "version-1", artifactId: variant === "artifact" ? "source:other:volumetric-dataset" : "source:object-1:volumetric-dataset", artifactChecksum: (variant === "checksum" ? "b" : "a").repeat(64), fieldId: variant === "channel" ? "channel:1" : "channel:0"}, secondary: [], compatibility: "EXACT", propagation: "EXACT_COMPATIBLE_ONLY", cleared: false});
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" initialSelectionToken={encodeWorkspaceSelectionUrl(context)} canResearch />);
  if (variant === "valid") {
    expect(await screen.findByText("体数据字段 1")).toBeVisible();
    expect(screen.getByRole("link", {name: "研究此数据"})).toHaveAttribute("href", expect.stringContaining("selection="));
  } else {
    expect(await screen.findByText("链接中的选择无法恢复，请在此版本中重新选择。科学内容仍可查看。")).toBeVisible();
    expect(screen.queryByRole("link", {name: "研究此数据"})).toBeNull();
  }
});

it.each(["frequency", "channel", "objectType"])("rejects nonexistent DOS %s in an otherwise exact-version link", async field => {
  const payload = JSON.parse(readFileSync(resolve(__dirname, "../../../../../tests/fixtures/phonon_contract/projected_dos.json"), "utf8"));
  mocks.getScientificViewerProjection.mockResolvedValue({...baseProjection("READY"), object_type: field === "objectType" ? "phonon.band_structure" : "phonon.dos", payload});
  const context = validateWorkspaceSelectionContext({schemaVersion: "1.0", sourceScopeHash: "a".repeat(64), primary: {selectionSchemaVersion: "1.0", kind: "PHONON_DOS_POINT", sourceScopeHash: "a".repeat(64), projectId: "project-1", datasetId: "object-1", datasetVersion: "version-1", phononArtifactId: "source:object-1", artifactChecksum: "a".repeat(64), frequencyPointId: field === "frequency" ? "frequency:999" : "frequency:0", dosChannelId: field === "channel" ? "projection:999" : "total"}, secondary: [], compatibility: "EXACT", propagation: "EXACT_COMPATIBLE_ONLY", cleared: false});
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" initialSelectionToken={encodeWorkspaceSelectionUrl(context)} canResearch />);
  expect(await screen.findByText("链接中的选择无法恢复，请在此版本中重新选择。科学内容仍可查看。")).toBeVisible();
  expect(screen.getByTestId("source-viewer")).toBeVisible();
  expect(screen.queryByRole("link", {name: "研究此数据"})).toBeNull();
});

it("rejects a nonexistent phonon mode in an otherwise exact-version link", async () => {
  const payload = JSON.parse(readFileSync(resolve(__dirname, "../../../../../tests/fixtures/phonon_contract/stable_band.json"), "utf8"));
  mocks.getScientificViewerProjection.mockResolvedValue({...baseProjection("READY"), object_type: "phonon.band_structure", payload});
  const context = validateWorkspaceSelectionContext({schemaVersion: "1.0", sourceScopeHash: "a".repeat(64), primary: {selectionSchemaVersion: "1.0", kind: "PHONON_Q_POINT", sourceScopeHash: "a".repeat(64), projectId: "project-1", datasetId: "object-1", datasetVersion: "version-1", phononArtifactId: "source:object-1", artifactChecksum: "a".repeat(64), qPointId: "q:999", branchId: "branch:2"}, secondary: [], compatibility: "EXACT", propagation: "EXACT_COMPATIBLE_ONLY", cleared: false});
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" initialSelectionToken={encodeWorkspaceSelectionUrl(context)} canResearch />);
  expect(await screen.findByText("链接中的选择无法恢复，请在此版本中重新选择。科学内容仍可查看。")).toBeVisible();
  expect(screen.getByTestId("source-viewer")).toBeVisible();
  expect(screen.queryByRole("link", {name: "研究此数据"})).toBeNull();
});

it("exposes a bounded retry and exact-source escape hatch when payload is unavailable", async () => {
  const user = userEvent.setup();
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" />);
  await waitFor(() => expect(screen.getByText("精确来源的原始科学数据当前不可用")).toBeInTheDocument());
  const sourceLink = screen.getByRole("link", { name: "返回项目数据" });
  expect(sourceLink).toHaveAttribute("href", "/projects/project-1/data");
  expect(sourceLink).toHaveClass("product-secondary-action");
  expect(screen.getByTestId("scientific-viewer-bounded-summary")).toHaveTextContent("version-1");
  const createObjectURL = vi.fn(() => "blob:viewer-metadata");
  const exportedParts: string[] = [];
  class MockBlob {
    constructor(parts: unknown[]) {
      exportedParts.push(parts.map(String).join(""));
    }
  }
  vi.stubGlobal("URL", { createObjectURL, revokeObjectURL: vi.fn() });
  vi.stubGlobal("Blob", MockBlob);
  const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
  await user.click(screen.getByText("查看数据详情"));
  await user.click(screen.getByRole("button", { name: "导出元数据摘要" }));
  expect(exportedParts[0]).not.toContain('"payload"');
  expect(click).toHaveBeenCalled();
  vi.unstubAllGlobals();
  click.mockRestore();

  mocks.getScientificViewerProjection.mockResolvedValue(baseProjection("READY"));
  await user.click(screen.getByRole("button", { name: "重新读取来源" }));
  await waitFor(() => expect(screen.getByTestId("source-viewer")).toBeInTheDocument());
  expect(mocks.getScientificViewerProjection).toHaveBeenCalledTimes(2);
});

it.each([
  ["METADATA_ONLY", "交互式预览已受限"],
  ["INVALIDATED", "此历史版本已失效"],
] as const)("does not offer a misleading source retry for %s", async (status, heading) => {
  mocks.getScientificViewerProjection.mockResolvedValue(baseProjection(status));
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" />);

  expect(await screen.findByText(heading)).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "返回项目数据" })).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "重新读取来源" })).not.toBeInTheDocument();
});

it("explains disabled lifecycle actions without hiding the exact viewer", async () => {
  mocks.getScientificObjectSummary.mockResolvedValue({ id: "object-1", project_id: "project-1", kind: "scientific_object", object_type: "structure.crystal", display_name: "Silicon", lifecycle_status: "INVALIDATED", current_version_id: "version-1" });
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" canManage />);
  const action = await screen.findByRole("button", { name: "归档科研对象" });
  expect(action).toBeDisabled();
  expect(action).toHaveAccessibleDescription("此科研对象已失效，生命周期操作已禁用；精确版本仍可只读查看。");
  expect(screen.getByTestId("scientific-viewer-bounded-summary")).toBeInTheDocument();
});

it("deduplicates rapid source retries behind a bounded backoff", async () => {
  const user = userEvent.setup();
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" />);
  await screen.findByText("精确来源的原始科学数据当前不可用");

  const retry = screen.getByRole("button", { name: "重新读取来源" });
  await user.click(retry);
  expect(screen.getByRole("button", { name: "稍后重试…" })).toBeDisabled();
  await waitFor(() => expect(mocks.getScientificViewerProjection).toHaveBeenCalledTimes(2), { timeout: 1500 });
  expect(mocks.getScientificViewerProjection).toHaveBeenCalledTimes(2);
});

it.each(["project_id", "object_id", "version_id"])("rejects a mismatched %s before exposing scientific content or Research", async (field) => {
  mocks.getScientificViewerProjection.mockResolvedValue({ ...baseProjection("READY"), [field]: "another-identity" });
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" canManage canResearch />);
  expect(await screen.findByRole("alert")).toHaveTextContent("暂时无法读取或确认此精确版本");
  expect(screen.queryByTestId("source-viewer")).not.toBeInTheDocument();
  expect(screen.queryByRole("link", { name: "研究此数据" })).not.toBeInTheDocument();
  expect(screen.getByRole("link", { name: "返回项目数据" })).toHaveAttribute("href", "/projects/project-1/data");
});

it("recovers object state independently while retaining the scientific body", async () => {
  mocks.getScientificViewerProjection.mockResolvedValue(baseProjection("READY"));
  mocks.getScientificObjectSummary.mockRejectedValueOnce(new Error("secret-provider-diagnostic"));
  const user = userEvent.setup();
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" canManage canResearch />);
  const body = await screen.findByTestId("source-viewer");
  expect(await screen.findByRole("alert")).toHaveTextContent("对象状态暂时无法读取");
  expect(screen.queryByText(/secret-provider-diagnostic/)).not.toBeInTheDocument();
  expect(screen.queryByRole("link", { name: "研究此数据" })).not.toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "重新读取对象状态" }));
  expect(await screen.findByRole("link", { name: "研究此数据" })).toHaveAttribute("href", expect.stringContaining("object=object-1&version=version-1"));
  expect(screen.getByTestId("source-viewer")).toBe(body);
  expect(mocks.getScientificViewerProjection).toHaveBeenCalledTimes(1);
  expect(mocks.getScientificObjectSummary).toHaveBeenCalledTimes(2);
});

it("retains the exact viewer and sample through a stalled lifecycle write and state reconciliation", async () => {
  vi.useFakeTimers();
  mocks.getScientificViewerProjection.mockResolvedValue(baseProjection("READY"));
  let finish!: (value: unknown) => void;
  mocks.updateScientificObject.mockImplementationOnce(() => new Promise((resolve) => { finish = resolve; }));
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" canManage canResearch />);
  await act(async () => {});
  const body = screen.getByTestId("source-viewer");
  fireEvent.click(screen.getByRole("button", { name: "选择样本" }));
  fireEvent.click(screen.getByRole("button", { name: "归档科研对象" }));
  await act(async () => { await vi.advanceTimersByTimeAsync(10001); });
  expect(screen.getByRole("alert")).toHaveTextContent("修改结果尚未确认");
  expect(screen.getByRole("button", { name: "归档科研对象" })).toBeDisabled();
  expect(screen.queryByRole("link", { name: "研究此数据" })).not.toBeInTheDocument();
  expect(screen.getByTestId("source-viewer")).toBe(body);
  mocks.getScientificObjectSummary.mockResolvedValueOnce({ id: "object-1", project_id: "project-1", kind: "scientific_object", object_type: "structure.crystal", display_name: "Silicon", lifecycle_status: "ARCHIVED", current_version_id: "version-1" });
  fireEvent.click(screen.getByRole("button", { name: "重新读取对象状态" }));
  await act(async () => {});
  expect(screen.getByRole("button", { name: "恢复科研对象" })).toHaveFocus();
  expect(screen.getByRole("link", { name: "研究此数据" })).toHaveAttribute("href", expect.stringContaining("selection="));
  await act(async () => finish({ id: "object-1", project_id: "project-1", lifecycle_status: "TRASHED" }));
  expect(screen.getByRole("button", { name: "恢复科研对象" })).toBeEnabled();
  expect(screen.getByTestId("source-viewer")).toBe(body); expect(mocks.getScientificViewerProjection).toHaveBeenCalledOnce();
});

it("shares confirmed lifecycle changes with its surrounding data directory", async () => {
  const user = userEvent.setup(); mocks.getScientificViewerProjection.mockResolvedValue(baseProjection("READY"));
  mocks.updateScientificObject.mockImplementation(async (id, changes) => ({ id, project_id: "project-1", kind: "scientific_object", object_type: "structure.crystal", display_name: "Silicon", lifecycle_status: changes.lifecycle, current_version_id: "version-1" }));
  function SharedViewer() {
    const management = useScientificObjectOperation("project-1");
    return <><output aria-label="目录状态">{management.known["object-1"]?.lifecycle_status || "ACTIVE"}</output><button onClick={() => void management.update(["object-1"], "ACTIVE", "directory")}>从目录恢复</button><ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" management={management} canManage canResearch /></>;
  }
  render(<SharedViewer />); const body = await screen.findByTestId("source-viewer");
  await user.click(screen.getByRole("button", { name: "归档科研对象" }));
  await screen.findByRole("button", { name: "恢复科研对象" }); expect(screen.getByLabelText("目录状态")).toHaveTextContent("ARCHIVED");
  await user.click(screen.getByRole("button", { name: "从目录恢复" }));
  await screen.findByRole("button", { name: "归档科研对象" }); expect(screen.getByLabelText("目录状态")).toHaveTextContent("ACTIVE");
  expect(screen.getByTestId("source-viewer")).toBe(body); expect(mocks.getScientificViewerProjection).toHaveBeenCalledOnce();
});

it("retains a bounded scientific summary through a failed payload retry", async () => {
  const user = userEvent.setup();
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" />);
  const summary = await screen.findByTestId("scientific-viewer-bounded-summary");
  mocks.getScientificViewerProjection.mockRejectedValueOnce(new Error("private storage path"));
  await user.click(screen.getByRole("button", { name: "重新读取来源" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("已读取的此版本信息仍保留");
  expect(screen.getByTestId("scientific-viewer-bounded-summary")).toBe(summary);
  expect(screen.queryByText(/private storage path/)).not.toBeInTheDocument();
  expect(mocks.getScientificObjectSummary).toHaveBeenCalledTimes(1);
  mocks.getScientificViewerProjection.mockResolvedValue(baseProjection("READY"));
  await user.click(screen.getByRole("button", { name: "重新读取" }));
  expect(await screen.findByTestId("source-viewer")).toBeInTheDocument();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
});

it.each(["source", "summary"])("bounds a stalled %s and ignores its late success after recovery", async (target) => {
  vi.useFakeTimers();
  let complete!: (value: unknown) => void;
  const request = target === "source" ? mocks.getScientificViewerProjection : mocks.getScientificObjectSummary;
  mocks.getScientificViewerProjection.mockResolvedValue(baseProjection("READY"));
  request.mockImplementationOnce(() => new Promise((resolve) => { complete = resolve; }));
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" canManage canResearch />);
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(screen.getByRole("alert")).toHaveTextContent("读取超时");
  if (target === "summary") expect(screen.getByTestId("source-viewer")).toBeInTheDocument();
  expect(request.mock.calls[0].at(-1).aborted).toBe(true);
  fireEvent.click(screen.getByRole("button", { name: target === "source" ? "重新读取" : "重新读取对象状态" }));
  await act(async () => { await vi.advanceTimersByTimeAsync(200); });
  expect(screen.getByRole("link", { name: "研究此数据" })).toBeInTheDocument();
  await act(async () => { complete(target === "source" ? { ...baseProjection("READY"), display_name: "obsolete response" } : { id: "object-1", project_id: "project-1", lifecycle_status: "TRASHED" }); });
  expect(screen.queryByText("obsolete response")).not.toBeInTheDocument();
  expect(screen.getByRole("link", { name: "研究此数据" })).toBeInTheDocument();
});

it("discards reads and scheduled retries when switching exact versions", async () => {
  vi.useFakeTimers();
  const { rerender } = render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" />);
  await act(async () => {});
  fireEvent.click(screen.getByRole("button", { name: "重新读取来源" }));
  mocks.getScientificViewerProjection.mockResolvedValue({ ...baseProjection("READY"), version_id: "version-2", display_name: "New exact version" });
  rerender(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-2" />);
  await act(async () => { await vi.advanceTimersByTimeAsync(1000); });
  expect(screen.getByRole("heading", { name: "New exact version" })).toBeInTheDocument();
  expect(mocks.getScientificViewerProjection).toHaveBeenCalledTimes(2);
  expect(mocks.getScientificViewerProjection.mock.calls[0][2].aborted).toBe(true);
});

it("keeps exact content visible when the linked selection is invalid", async () => {
  mocks.getScientificViewerProjection.mockResolvedValue(baseProjection("READY"));
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" initialSelectionToken="invalid-token" />);
  expect(await screen.findByRole("alert")).toHaveTextContent("链接中的选择无法恢复");
  expect(screen.getByTestId("source-viewer")).toBeInTheDocument();
});

it("defaults to read-only even with an active object summary", async () => {
  mocks.getScientificViewerProjection.mockResolvedValue(baseProjection("READY"));
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" />);
  expect(await screen.findByTestId("source-viewer")).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "归档科研对象" })).not.toBeInTheDocument();
  expect(screen.queryByRole("link", { name: "研究此数据" })).not.toBeInTheDocument();
});

it.each(["id", "project_id"])("rejects mismatched summary %s without hiding scientific content", async (field) => {
  mocks.getScientificViewerProjection.mockResolvedValue(baseProjection("READY"));
  mocks.getScientificObjectSummary.mockResolvedValue({ id: "object-1", project_id: "project-1", lifecycle_status: "ACTIVE", [field]: "wrong" });
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" canManage canResearch />);
  expect(await screen.findByTestId("source-viewer")).toBeInTheDocument();
  expect(await screen.findByRole("alert")).toHaveTextContent("对象状态暂时无法读取");
  expect(screen.queryByRole("link", { name: "研究此数据" })).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: "生命周期操作不可用" })).toBeDisabled();
});

it.each(["projectId", "datasetVersion"])("keeps content but blocks a foreign selection's %s until explicitly cleared", async (field) => {
  mocks.getScientificViewerProjection.mockResolvedValue(baseProjection("READY"));
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" initialSelectionToken={encodeWorkspaceSelectionUrl(sampleSelection({ [field]: "foreign" }))} canResearch />);
  expect(await screen.findByRole("alert")).toHaveTextContent("链接中的选择无法恢复");
  expect(screen.getByTestId("source-viewer")).toBeInTheDocument();
  expect(screen.queryByRole("link", { name: "研究此数据" })).not.toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "清除选择，查看完整版本" }));
  expect(await screen.findByRole("link", { name: "研究此数据" })).not.toHaveAttribute("href", expect.stringContaining("selection="));
});

it("persists exact selection in the URL, restores it, and clears it without losing other route state", async () => {
  mocks.getScientificViewerProjection.mockResolvedValue(baseProjection("READY"));
  window.history.replaceState({ routeState: "keep" }, "", "/projects/project-1/data?object=object-1&version=version-1&keep=1#source");
  const { unmount } = render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" canResearch />);
  await userEvent.click(await screen.findByRole("button", { name: "选择样本" }));
  const token = new URLSearchParams(window.location.search).get("selection")!;
  expect(decodeWorkspaceSelectionUrl(token).primary).toMatchObject({ datasetVersion: "version-1", sampleRef: "sample-1" });
  expect(window.history.state).toEqual({ routeState: "keep" });
  expect(window.location.hash).toBe("#source");
  unmount();
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" canResearch />);
  await waitFor(() => expect(screen.getByTestId("restored-sample")).toHaveTextContent("sample-1"));
  expect(screen.getByRole("link", { name: "研究此数据" })).toHaveAttribute("href", expect.stringContaining(`selection=${token}`));
  await userEvent.click(screen.getByRole("button", { name: "清除选择" }));
  expect(new URLSearchParams(window.location.search).has("selection")).toBe(false);
  expect(new URLSearchParams(window.location.search).get("keep")).toBe("1");
  expect(screen.getByTestId("restored-sample")).toBeEmptyDOMElement();
});
