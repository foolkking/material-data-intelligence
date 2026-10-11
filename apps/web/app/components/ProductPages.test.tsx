import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  searchQuery: "",
  sourceSelection: null as unknown,
  listProjects: vi.fn(),
  createProject: vi.fn(),
  getAuthUser: vi.fn(),
  updateProject: vi.fn(),
  bulkProjectAction: vi.fn(),
  deleteEmptyProject: vi.fn(),
  getProjectDependencyImpact: vi.fn(),
  getProjectExportManifest: vi.fn(),
  updateDataset: vi.fn(),
  bulkDatasetAction: vi.fn(),
  deleteEmptyDataset: vi.fn(),
  getDatasetDependencyImpact: vi.fn(),
  getProjectHistory: vi.fn(),
  getCachedProjectHistory: vi.fn(),
  getDatasetSourceResources: vi.fn(),
  uploadDatasetFiles: vi.fn(),
  listScientificObjects: vi.fn(),
  bulkUpdateScientificObjects: vi.fn(),
  getScientificObjectDependencyImpact: vi.fn(),
  updateScientificObject: vi.fn(),
  routerPush: vi.fn(),
  routerReplace: vi.fn(),
  routerPrefetch: vi.fn(),
}));

vi.mock("next/link", () => ({ default: ({ children, href, prefetch: _prefetch, ...props }: { children: React.ReactNode; href: string; prefetch?: boolean | null }) => <a href={href} {...props}>{children}</a> }));
vi.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams(mocks.searchQuery),
  useRouter: () => ({
    back: vi.fn(),
    forward: vi.fn(),
    prefetch: mocks.routerPrefetch,
    push: mocks.routerPush,
    refresh: vi.fn(),
    replace: mocks.routerReplace,
  }),
}));
vi.mock("../lib/product-api", async (original) => ({ ...await original<typeof import("../lib/product-api")>(), getAuthUser: mocks.getAuthUser }));
vi.mock("../lib/planner-api", () => ({
  listProjects: mocks.listProjects,
  createProject: mocks.createProject,
  updateProject: mocks.updateProject,
  bulkProjectAction: mocks.bulkProjectAction,
  deleteEmptyProject: mocks.deleteEmptyProject,
  getProjectDependencyImpact: mocks.getProjectDependencyImpact,
  getProjectExportManifest: mocks.getProjectExportManifest,
  updateDataset: mocks.updateDataset,
  bulkDatasetAction: mocks.bulkDatasetAction,
  deleteEmptyDataset: mocks.deleteEmptyDataset,
  getDatasetDependencyImpact: mocks.getDatasetDependencyImpact,
  getProjectHistory: mocks.getProjectHistory,
  getCachedProjectHistory: mocks.getCachedProjectHistory,
  getDatasetSourceResources: mocks.getDatasetSourceResources,
  uploadDatasetFiles: mocks.uploadDatasetFiles,
}));
vi.mock("../../shared/layout/ProductShell", () => ({
  ProductShell: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  RequireProductAuth: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));
vi.mock("../lib/scientific-viewer-api", () => ({
  listScientificObjects: mocks.listScientificObjects,
  bulkUpdateScientificObjects: mocks.bulkUpdateScientificObjects,
  getScientificObjectDependencyImpact: mocks.getScientificObjectDependencyImpact,
  updateScientificObject: mocks.updateScientificObject,
}));
vi.mock("../../scientific-viewers/ScientificViewerAdapter", () => ({
  ScientificSourceViewer: ({ resource, selection, onSelection }: { resource: { objectType: string; objectId?: string }; selection?: { primary?: { sampleRef?: string } }; onSelection?: (selection: unknown) => void }) => <div data-testid="quick-preview-scientific-viewer" data-object={resource.objectId} data-sample={selection?.primary?.sampleRef}>{resource.objectType}{onSelection ? <button type="button" aria-label="选择第一条科学数据" onClick={() => onSelection(mocks.sourceSelection || { schemaVersion: "1.0", sourceScopeHash: "scope", primary: { kind: "DATASET_SAMPLE", sampleRef: "BaTiO3" }, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false })}>选择</button> : null}</div>,
}));
vi.mock("../../scientific-viewers/scientific-viewer/ScientificObjectViewer", () => ({
  ScientificObjectViewer: ({ objectId, versionId, canManage, canResearch }: { objectId: string; versionId: string; canManage: boolean; canResearch: boolean }) => <div data-testid="scientific-object-viewer" data-object={objectId} data-version={versionId} data-can-manage={String(canManage)} data-can-research={String(canResearch)} />,
}));

import {
  ConsolePage,
  DatasetUploadPage,
  ProjectDataPage,
  ProjectsPage,
  ProjectOverviewPage,
  TableScientificView,
  dataTableViewHref,
  resolveDataPageSelection,
  resolveDatasetSelection,
} from "./ProductPages";
import {
  encodeWorkspaceSelectionUrl,
  validateWorkspaceSelectionContext,
} from "./workspace/workspace-selection-contract";

afterEach(() => vi.unstubAllGlobals());

beforeEach(() => {
  vi.clearAllMocks();
  window.sessionStorage.clear();
  mocks.getAuthUser.mockResolvedValue({ id: "creation-user", displayName: "研究员", roles: [] });
  mocks.searchQuery = "";
  mocks.sourceSelection = null;
  mocks.listProjects.mockResolvedValue([{ id: "project_1", projectId: "project_1", name: "Perovskite stability study", description: "材料稳定性研究", status: "active", role: "owner" }]);
  mocks.createProject.mockResolvedValue({ id: "project_2", projectId: "project_2", name: "新项目", status: "active", role: "owner" });
  mocks.updateProject.mockImplementation(async (projectId: string, changes: Record<string, unknown>) => ({
    id: projectId,
    projectId,
    name: typeof changes.name === "string" ? changes.name : "新项目",
    description: typeof changes.description === "string" ? changes.description : undefined,
    status: changes.lifecycle === "TRASHED" ? "trashed" : changes.archived ? "archived" : "active",
    role: "owner",
    ...(changes.pinned === undefined ? {} : { pinned: changes.pinned }),
    ...(changes.tags === undefined ? {} : { tags: changes.tags }),
    ...changes,
  }));
  mocks.bulkProjectAction.mockImplementation(async (ids: string[], action: string) => ({ action, projectIds: ids, count: ids.length }));
  mocks.deleteEmptyProject.mockResolvedValue({ projectId: "project_1", deleted: true });
  mocks.getProjectDependencyImpact.mockResolvedValue({ entity: "project", entityId: "project_1", displayName: "项目", canDelete: true, dependencyCount: 0, dependencies: [], impact: { removedFromActiveDiscovery: false, historicalProvenanceProtected: false, historicalResearchRemainsAccessible: false } });
  mocks.getProjectExportManifest.mockResolvedValue({
    schemaVersion: "mdi.project-reproducibility-manifest/1.0",
    exportKind: "authorized_project_provenance",
    executable: false,
    generatedAt: "2026-09-01T00:00:00Z",
    project: { id: "project_1", name: "Perovskite stability study", description: "材料稳定性研究", status: "active", pinned: false, tags: [], role: "owner" },
    datasets: [], scientificObjects: [], scientificObjectVersions: [], researchSessions: [], researchTurns: [], scientificResults: [], reports: [],
    bounds: { truncated: {} }, excluded: ["credentials and secrets"],
  });
  mocks.updateDataset.mockResolvedValue({ id: "dataset_1", datasetId: "dataset_1", projectId: "project_1", name: "materials-table", status: "profile_ready" });
  mocks.bulkDatasetAction.mockImplementation(async (datasetIds: string[], action: string) => ({ action, datasetIds, count: datasetIds.length }));
  mocks.deleteEmptyDataset.mockResolvedValue({ datasetId: "dataset_1", deleted: true });
  mocks.getDatasetDependencyImpact.mockResolvedValue({ entity: "dataset", entityId: "dataset_1", displayName: "数据集", canDelete: true, dependencyCount: 0, dependencies: [], impact: { removedFromActiveDiscovery: false, historicalProvenanceProtected: false, historicalResearchRemainsAccessible: false } });
  mocks.getProjectHistory.mockResolvedValue({ project: { id: "project_1", name: "研究项目", role: "owner" }, datasets: [{ datasetId: "dataset_1", name: "materials-table", import: { fileCount: 1, resources: [] }, profile: { rowCount: 3, semanticRoles: {} }, status: "profile_ready" }], analyses: [] });
  mocks.getCachedProjectHistory.mockReturnValue(null);
  mocks.getDatasetSourceResources.mockResolvedValue([{ objectId: "object_1", objectType: "DataFrame", datasetId: "dataset_1", payload: [{ formula: "BaTiO3" }] }]);
  mocks.uploadDatasetFiles.mockResolvedValue({ datasetId: "dataset_2" });
  mocks.listScientificObjects.mockResolvedValue({ items: [], next_cursor: null });
  mocks.bulkUpdateScientificObjects.mockImplementation(async (projectId: string, ids: string[], lifecycle: string) => ({
    project_id: projectId, lifecycle, count: ids.length,
    items: ids.map((id) => ({ id, project_id: projectId, lifecycle_status: lifecycle, display_name: id, kind: "STRUCTURE", object_type: "structure.crystal", current_version_id: "version_1" })),
  }));
  mocks.getScientificObjectDependencyImpact.mockResolvedValue({
    entity: "scientific_object",
    entityId: "object_1",
    displayName: "Silicon",
    canDelete: false,
    dependencyCount: 2,
    dependencies: [
      { kind: "scientific_object_versions", label: "科学对象版本", count: 1 },
      { kind: "scientific_result_snapshots", label: "ScientificResult", count: 1 },
    ],
    impact: {
      removedFromActiveDiscovery: true,
      historicalProvenanceProtected: true,
      historicalResearchRemainsAccessible: true,
      scientificSnapshotMutated: false,
    },
  });
  mocks.updateScientificObject.mockImplementation(async (objectId: string, changes: { archived?: boolean; lifecycle?: string }) => ({
    id: objectId,
    project_id: "project_1",
    kind: "STRUCTURE",
    object_type: "structure.crystal",
    display_name: "Silicon",
    lifecycle_status: changes.lifecycle || (changes.archived ? "ARCHIVED" : "ACTIVE"),
    current_version_id: "version_1",
  }));
});

it("prioritizes an explicit dataset route selection over a still-valid prior selection", () => {
  expect(resolveDatasetSelection("dataset_xrd", "dataset_band", ["dataset_band", "dataset_xrd"])).toBe("dataset_xrd");
  expect(resolveDatasetSelection("", "dataset_band", ["dataset_band", "dataset_xrd"])).toBe("dataset_band");
  expect(resolveDatasetSelection("", "missing", ["dataset_band", "dataset_xrd"])).toBe("dataset_band");
});

it("opens a real source-resource viewer in Console quick preview", async () => {
  const user = userEvent.setup();
  render(<ConsolePage />);

  await user.click(await screen.findByRole("button", { name: "快速查看" }));
  expect(await screen.findByRole("complementary", { name: "数据快速查看" })).toBeInTheDocument();
  expect(await screen.findByTestId("quick-preview-scientific-viewer")).toHaveTextContent("DataFrame");
  expect(mocks.getDatasetSourceResources).toHaveBeenCalledWith("dataset_1", expect.anything());
});

it("retries a failed Console quick preview in place without leaving the project", async () => {
  const user = userEvent.setup();
  mocks.getDatasetSourceResources
    .mockRejectedValueOnce(new Error("SOURCE_RESOURCE_LOAD_FAILED"))
    .mockResolvedValueOnce([{ objectId: "object_1", objectType: "DataFrame", datasetId: "dataset_1", payload: [{ formula: "BaTiO3" }] }]);

  render(<ConsolePage />);

  await user.click(await screen.findByRole("button", { name: "快速查看" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("暂时无法加载数据");
  await user.click(screen.getByRole("button", { name: "重新加载数据" }));

  expect(await screen.findByTestId("quick-preview-scientific-viewer")).toHaveTextContent("DataFrame");
  expect(mocks.getDatasetSourceResources).toHaveBeenCalledTimes(2);
});

it("restores focus after closing quick preview", async () => {
  const user = userEvent.setup();
  render(<ConsolePage />);
  const trigger = await screen.findByRole("button", { name: "快速查看" });
  await user.click(trigger);
  await screen.findByRole("complementary", { name: "数据快速查看" });
  await user.click(screen.getByRole("button", { name: "关闭快速查看" }));
  await waitFor(() => expect(document.activeElement).toBe(trigger));
});

it("binds the three phonon roles and offers the exact uploaded dataset for Research", async () => {
  const user = userEvent.setup();
  render(<DatasetUploadPage projectId="project_1" />);
  await user.type(await screen.findByLabelText("数据集名称"), "phonon bundle");
  await user.click(screen.getByRole("button", { name: "声子组合" }));
  await user.upload(
    await screen.findByLabelText("结构文件"),
    new File(["structure"], "UPLOAD_structure.vasp", {
      type: "application/octet-stream",
    }),
  );
  await user.upload(
    await screen.findByLabelText("声子能带文件"),
    new File(["band"], "UPLOAD_phonon_band.json", {
      type: "application/json",
    }),
  );
  await user.upload(
    await screen.findByLabelText("声子态密度文件"),
    new File(["dos"], "UPLOAD_phonon_dos.json", {
      type: "application/json",
    }),
  );
  await user.click(
    screen.getByRole("button", { name: "上传并解析" }),
  );
  await waitFor(() => expect(mocks.uploadDatasetFiles).toHaveBeenCalled());
  const files = mocks.uploadDatasetFiles.mock.calls[0][2];
  expect(files).toEqual([
    expect.objectContaining({
      file: expect.objectContaining({ name: "UPLOAD_structure.vasp" }),
      companionGroupId: "phonon_bundle",
    }),
    expect.objectContaining({
      file: expect.objectContaining({ name: "UPLOAD_phonon_band.json" }),
      importKind: "phonon_band",
      contractVersion: "phase10h.phonon_band.v1",
      companionGroupId: "phonon_bundle",
    }),
    expect.objectContaining({
      file: expect.objectContaining({ name: "UPLOAD_phonon_dos.json" }),
      importKind: "phonon_dos",
      contractVersion: "phase10h.phonon_dos.v1",
      companionGroupId: "phonon_bundle",
    }),
  ]);
  expect(await screen.findByRole("link", { name: "开始研究" })).toHaveAttribute("href", "/projects/project_1/research?dataset=dataset_2");
  expect(screen.getByRole("link", { name: "查看数据" })).toHaveAttribute("href", "/projects/project_1/data?dataset=dataset_2");
  expect(screen.getByRole("heading", { name: "文件已上传" })).toHaveFocus();
  expect(mocks.routerPush).not.toHaveBeenCalled();
});

it("keeps the typed phonon action disabled until all three roles are selected", async () => {
  const user = userEvent.setup();
  render(<DatasetUploadPage projectId="project_1" />);
  await user.type(await screen.findByLabelText("数据集名称"), "phonon bundle");
  await user.click(screen.getByRole("button", { name: "声子组合" }));
  const action = screen.getByRole("button", {
    name: "上传并解析",
  });
  expect(action).toBeDisabled();
  await user.upload(
    screen.getByLabelText("结构文件"),
    new File(["structure"], "UPLOAD_structure.vasp"),
  );
  await user.upload(
    screen.getByLabelText("声子能带文件"),
    new File(["band"], "UPLOAD_phonon_band.json"),
  );
  expect(action).toBeDisabled();
  await user.upload(
    screen.getByLabelText("声子态密度文件"),
    new File(["dos"], "UPLOAD_phonon_dos.json"),
  );
  expect(action).toBeEnabled();
});

it("keeps the direct upload route read-only for viewer members", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "共享研究项目", role: "viewer" },
    datasets: [],
    analyses: [],
  });
  render(<DatasetUploadPage projectId="project_1" />);
  expect(await screen.findByRole("heading", { name: "此项目为只读" })).toBeInTheDocument();
  expect(screen.queryByLabelText("数据集名称")).not.toBeInTheDocument();
  expect(screen.getByRole("link", { name: "查看项目数据" })).toHaveAttribute("href", "/projects/project_1/data");
});

it("recovers a failed project history read from the current overview route", async () => {
  const user = userEvent.setup();
  const history = {
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [],
    analyses: [],
  };
  mocks.getProjectHistory
    .mockRejectedValueOnce(new Error("PROJECT_HISTORY_TEMPORARY_FAILURE"))
    .mockResolvedValueOnce(history);

  render(<ProjectOverviewPage projectId="project_1" />);

  expect(await screen.findByRole("alert")).toHaveTextContent("暂时无法读取项目数据，请重试。");
  await user.click(screen.getByRole("button", { name: "重新加载项目数据" }));
  expect(await screen.findByRole("region", { name: "研究项目的项目概览" })).toBeInTheDocument();
  expect(mocks.getProjectHistory).toHaveBeenCalledTimes(2);
  expect(mocks.getProjectHistory).toHaveBeenLastCalledWith("project_1", { forceRefresh: true });
});

it("preserves each upload mode's files and submits only the selected mode", async () => {
  const user = userEvent.setup();
  render(<DatasetUploadPage projectId="project_1" />);
  await user.type(await screen.findByLabelText("数据集名称"), "材料表");
  expect(screen.getByRole("group", { name: "普通文件" })).toBeVisible();
  expect(screen.queryByRole("group", { name: "声子组合文件" })).not.toBeInTheDocument();
  await user.upload(screen.getByLabelText("源文件"), new File(["material,value\nFe,1"], "materials.csv"));
  await user.click(screen.getByRole("button", { name: "声子组合" }));
  expect(screen.getByRole("button", { name: "上传并解析" })).toBeDisabled();
  await user.upload(screen.getByLabelText("结构文件"), new File(["structure"], "POSCAR"));
  await user.click(screen.getByRole("button", { name: "普通文件" }));
  expect(screen.getByRole("list", { name: "源文件已选择文件" })).toHaveTextContent("materials.csv");
  expect(screen.getByLabelText("数据集名称")).toHaveValue("材料表");
  await user.click(screen.getByRole("button", { name: "上传并解析" }));
  await screen.findByRole("heading", { name: "文件已上传" });
  expect(mocks.uploadDatasetFiles).toHaveBeenCalledWith("project_1", "材料表", [expect.objectContaining({ file: expect.objectContaining({ name: "materials.csv" }) })]);
  expect(mocks.uploadDatasetFiles).toHaveBeenCalledTimes(1);
});

it("removes selected files, permits choosing the same file again, and starts another clean upload", async () => {
  const user = userEvent.setup();
  render(<DatasetUploadPage projectId="project_1" />);
  await user.type(await screen.findByLabelText("数据集名称"), "再次上传");
  const file = new File(["Fe"], "材料.csv");
  await user.upload(screen.getByLabelText("源文件"), file);
  await user.click(screen.getByRole("button", { name: "移除 源文件 材料.csv" }));
  await waitFor(() => expect(screen.getByLabelText("源文件")).toHaveFocus());
  expect(screen.queryByRole("list", { name: "源文件已选择文件" })).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: "上传并解析" })).toBeDisabled();
  await user.upload(screen.getByLabelText("源文件"), file);
  await user.click(screen.getByRole("button", { name: "上传并解析" }));
  await user.click(await screen.findByRole("button", { name: "继续上传" }));
  expect(screen.getByLabelText("数据集名称")).toHaveValue("");
  await waitFor(() => expect(screen.getByLabelText("数据集名称")).toHaveFocus());
  expect(screen.queryByRole("list", { name: "源文件已选择文件" })).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: "上传并解析" })).toBeDisabled();
});

it("blocks duplicate uploads and edits while pending, then keeps the draft after failure", async () => {
  const user = userEvent.setup();
  let rejectUpload!: (reason: Error) => void;
  mocks.uploadDatasetFiles.mockImplementationOnce(() => new Promise((_resolve, reject) => { rejectUpload = reject; }));
  render(<DatasetUploadPage projectId="project_1" />);
  await user.type(await screen.findByLabelText("数据集名称"), "保留草稿");
  await user.upload(screen.getByLabelText("源文件"), new File(["Fe"], "table.csv"));
  const form = screen.getByRole("form", { name: "上传数据" });
  act(() => { fireEvent.submit(form); fireEvent.submit(form); });
  expect(mocks.uploadDatasetFiles).toHaveBeenCalledTimes(1);
  expect(screen.getByLabelText("数据集名称")).toBeDisabled();
  expect(screen.getByLabelText("源文件")).toBeDisabled();
  expect(screen.getByRole("button", { name: "声子组合" })).toBeDisabled();
  expect(screen.getByRole("button", { name: "移除 源文件 table.csv" })).toBeDisabled();
  await act(async () => { rejectUpload(new Error("UPLOAD_RECEIPT_INTERNAL_DETAIL")); });
  expect(screen.getByRole("alert")).toHaveTextContent("名称和文件已保留");
  expect(screen.queryByText("UPLOAD_RECEIPT_INTERNAL_DETAIL")).not.toBeInTheDocument();
  expect(screen.getByLabelText("数据集名称")).toHaveValue("保留草稿");
  expect(screen.getByRole("list", { name: "源文件已选择文件" })).toHaveTextContent("table.csv");
  await user.click(screen.getByRole("button", { name: "重试上传" }));
  await screen.findByRole("heading", { name: "文件已上传" });
  expect(mocks.uploadDatasetFiles).toHaveBeenCalledTimes(2);
});

it("keeps a completed upload visible when its response lacks a dataset link", async () => {
  mocks.uploadDatasetFiles.mockResolvedValueOnce({});
  const user = userEvent.setup();
  render(<DatasetUploadPage projectId="project_1" />);
  await user.type(await screen.findByLabelText("数据集名称"), "已接收文件");
  await user.upload(screen.getByLabelText("源文件"), new File(["Fe"], "table.csv"));
  await user.click(screen.getByRole("button", { name: "上传并解析" }));
  await screen.findByRole("heading", { name: "文件已上传" });
  expect(screen.getByRole("link", { name: "查看项目数据" })).toHaveAttribute("href", "/projects/project_1/data");
  expect(screen.queryByRole("link", { name: "开始研究" })).not.toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "重试上传" })).not.toBeInTheDocument();
  expect(mocks.uploadDatasetFiles).toHaveBeenCalledTimes(1);
});

it("does not carry an upload draft or late completion into another project", async () => {
  const user = userEvent.setup();
  let finishUpload!: (result: unknown) => void;
  mocks.uploadDatasetFiles.mockImplementationOnce(() => new Promise((resolve) => { finishUpload = resolve; }));
  const { rerender } = render(<DatasetUploadPage projectId="project_1" />);
  await user.type(await screen.findByLabelText("数据集名称"), "第一个项目的文件");
  await user.upload(screen.getByLabelText("源文件"), new File(["Fe"], "first.csv"));
  await user.click(screen.getByRole("button", { name: "上传并解析" }));
  mocks.getProjectHistory.mockResolvedValueOnce({ project: { projectId: "project_2", name: "第二个项目", role: "owner" }, datasets: [], analyses: [] });
  rerender(<DatasetUploadPage projectId="project_2" />);
  expect(await screen.findByLabelText("数据集名称")).toHaveValue("");
  expect(screen.queryByRole("list", { name: "源文件已选择文件" })).not.toBeInTheDocument();
  await act(async () => { finishUpload({ datasetId: "old_dataset", projectId: "project_1" }); });
  expect(screen.queryByRole("heading", { name: "文件已上传" })).not.toBeInTheDocument();
  expect(screen.queryByRole("link", { name: "开始研究" })).not.toBeInTheDocument();
});

it("paints a warmed project overview without showing a second loading state", async () => {
  const warmedHistory = {
    project: { id: "project_1", name: "已预热项目", role: "owner" },
    datasets: [],
    analyses: [],
  };
  mocks.getCachedProjectHistory.mockReturnValue(warmedHistory);

  render(<ProjectOverviewPage projectId="project_1" />);

  expect(screen.getByRole("region", { name: "已预热项目的项目概览" })).toBeInTheDocument();
  expect(screen.queryByText("正在加载研究内容…")).not.toBeInTheDocument();
  expect(mocks.getProjectHistory).not.toHaveBeenCalled();
});

it("never substitutes another dataset for a missing explicit link", async () => {
  expect(resolveDatasetSelection("missing", "dataset_1", ["dataset_1"])).toBe("");
  render(<ProjectDataPage projectId="project_1" initialDatasetId="missing" />);
  expect(await screen.findByRole("alert")).toHaveTextContent("暂时无法打开这份数据");
  expect(screen.queryByRole("heading", { name: "materials-table" })).not.toBeInTheDocument();
  expect(screen.queryByRole("link", { name: "研究此数据" })).not.toBeInTheDocument();
  expect(mocks.getDatasetSourceResources).not.toHaveBeenCalled();
  expect(screen.getByRole("link", { name: "浏览项目数据" })).toHaveAttribute("href", "/projects/project_1/data");
});

it.each([true, false])("accepts the canonical API projectId in project history (cached: %s)", async (cached) => {
  const history = { schemaVersion: "ProjectHistoryView/1.0", project: { projectId: "project_1", name: "接口中的项目", role: "owner" }, datasets: [], analyses: [] };
  if (cached) mocks.getCachedProjectHistory.mockReturnValue(history);
  else mocks.getProjectHistory.mockResolvedValueOnce(history);
  render(<ProjectOverviewPage projectId="project_1" />);
  expect(await screen.findByRole("region", { name: "接口中的项目的项目概览" })).toBeInTheDocument();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
});

it("keeps the explicit dataset open when the directory lifecycle filter changes", async () => {
  const user = userEvent.setup();
  render(<ProjectDataPage projectId="project_1" initialDatasetId="dataset_1" />);
  await screen.findByTestId("quick-preview-scientific-viewer");
  for (const label of ["已归档", "回收站", "当前"]) {
    await user.click(screen.getByRole("button", { name: label }));
    expect(screen.getByRole("heading", { name: "materials-table" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "研究此数据" })).toHaveAttribute("href", "/projects/project_1/research?dataset=dataset_1");
  }
  expect(mocks.getDatasetSourceResources).toHaveBeenCalledTimes(1);
});

it("removes the old source immediately when the live query addresses a missing dataset", async () => {
  mocks.searchQuery = "dataset=dataset_1";
  const { rerender } = render(<ProjectDataPage projectId="project_1" initialDatasetId="dataset_1" />);
  await screen.findByTestId("quick-preview-scientific-viewer");
  mocks.searchQuery = "dataset=missing";
  rerender(<ProjectDataPage projectId="project_1" initialDatasetId="dataset_1" />);
  expect(screen.getByRole("alert")).toHaveTextContent("暂时无法打开这份数据");
  expect(screen.queryByTestId("quick-preview-scientific-viewer")).not.toBeInTheDocument();
  expect(screen.queryByRole("link", { name: "研究此数据" })).not.toBeInTheDocument();
  expect(mocks.getDatasetSourceResources).toHaveBeenCalledTimes(1);
});

it("refreshes a warm incomplete directory and recovers only the dataset in the link", async () => {
  mocks.getDatasetSourceResources.mockResolvedValue([{ objectId: "recovered-resource", datasetId: "dataset_2", objectType: "DataFrame", payload: [] }]);
  const history = await mocks.getProjectHistory();
  const target = { ...history.datasets[0], datasetId: "dataset_2", name: "Recovered source" };
  mocks.getCachedProjectHistory.mockReturnValue(history);
  mocks.getProjectHistory.mockClear().mockResolvedValue({ ...history, datasets: [...history.datasets, target] });
  render(<ProjectDataPage projectId="project_1" initialDatasetId="dataset_2" />);
  expect(screen.getByRole("alert")).toHaveTextContent("暂时无法打开这份数据");
  expect(mocks.getDatasetSourceResources).not.toHaveBeenCalled();
  await userEvent.setup().click(screen.getByRole("button", { name: "重新检查" }));
  expect(await screen.findByRole("heading", { name: "Recovered source" })).toBeInTheDocument();
  await screen.findByTestId("quick-preview-scientific-viewer");
  expect(mocks.getProjectHistory).toHaveBeenCalledTimes(1);
  expect(mocks.getProjectHistory).toHaveBeenLastCalledWith("project_1", { forceRefresh: true });
  expect(mocks.getDatasetSourceResources).toHaveBeenCalledTimes(1);
  expect(mocks.getDatasetSourceResources).toHaveBeenLastCalledWith("dataset_2", expect.any(AbortSignal));
  expect(screen.getByRole("link", { name: "研究此数据" })).toHaveAttribute("href", "/projects/project_1/research?dataset=dataset_2");
});

it("retains the directory after a failed link recheck without duplicate errors", async () => {
  const history = await mocks.getProjectHistory();
  mocks.getCachedProjectHistory.mockReturnValue(history);
  mocks.getProjectHistory.mockRejectedValueOnce(new Error("RAW_STORAGE_ERROR"));
  render(<ProjectDataPage projectId="project_1" initialDatasetId="missing" />);
  await userEvent.setup().click(screen.getByRole("button", { name: "重新检查" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("暂时无法读取项目数据");
  expect(screen.queryByText("RAW_STORAGE_ERROR")).not.toBeInTheDocument();
  expect(within(screen.getByRole("complementary", { name: "项目数据目录" })).getByRole("link", { name: /materials-table/ })).toBeInTheDocument();
  expect(mocks.getDatasetSourceResources).not.toHaveBeenCalled();
});

it("bounds a stalled project read, retries once and ignores the late response", async () => {
  let resolveStalled!: (item: unknown) => void;
  mocks.getProjectHistory.mockImplementationOnce(() => new Promise((resolve) => { resolveStalled = resolve; }));
  vi.useFakeTimers();
  try {
    await act(async () => { render(<ProjectOverviewPage projectId="project_1" />); });
    await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
    expect(screen.getByRole("alert")).toHaveTextContent("项目数据读取超时");
  } finally {
    vi.useRealTimers();
  }
  const retryButton = screen.getByRole("button", { name: "重新加载项目数据" });
  act(() => { fireEvent.click(retryButton); fireEvent.click(retryButton); });
  await screen.findByRole("region", { name: "研究项目的项目概览" });
  expect(mocks.getProjectHistory).toHaveBeenCalledTimes(2);
  expect(mocks.getProjectHistory).toHaveBeenLastCalledWith("project_1", { forceRefresh: true });
  await act(async () => { resolveStalled({ project: { id: "project_1", name: "过期的项目内容" }, datasets: [], analyses: [] }); });
  expect(screen.queryByRole("region", { name: "过期的项目内容的项目概览" })).not.toBeInTheDocument();
});

it("rejects foreign project cache and responses and can recover the correct project", async () => {
  const foreign = { project: { id: "foreign", name: "其他项目" }, datasets: [], analyses: [] };
  mocks.getCachedProjectHistory.mockReturnValue(foreign);
  mocks.getProjectHistory.mockResolvedValueOnce(foreign);
  render(<ProjectOverviewPage projectId="project_1" />);
  expect(screen.queryByRole("region", { name: "其他项目的项目概览" })).not.toBeInTheDocument();
  expect(await screen.findByRole("alert")).toHaveTextContent("暂时无法读取项目数据");
  expect(mocks.getProjectHistory).toHaveBeenCalledTimes(1);
  expect(mocks.getProjectHistory).toHaveBeenLastCalledWith("project_1", { forceRefresh: true });
  await userEvent.setup().click(screen.getByRole("button", { name: "重新加载项目数据" }));
  expect(await screen.findByRole("region", { name: "研究项目的项目概览" })).toBeInTheDocument();
  expect(screen.queryByRole("region", { name: "其他项目的项目概览" })).not.toBeInTheDocument();
});

it("opens and focuses the available views when upload records are empty", async () => {
  mocks.getProjectHistory.mockResolvedValue({ project: { id: "project_1", name: "研究项目", role: "owner" }, datasets: [], analyses: [] });
  mocks.listScientificObjects.mockResolvedValue({ items: [{ id: "object_1", project_id: "project_1", display_name: "材料表", object_type: "DataFrame", current_version_id: "version_1", lifecycle_status: "ACTIVE" }], next_cursor: null });
  render(<ProjectDataPage projectId="project_1" />);
  await screen.findByRole("heading", { name: "选择一份数据开始查看" });
  expect(screen.queryByRole("heading", { name: "尚无项目数据" })).not.toBeInTheDocument();
  expect(screen.getByText("还没有上传记录。")).toBeInTheDocument();
  await userEvent.setup().click(screen.getByRole("button", { name: "浏览数据视图" }));
  const link = screen.getByRole("link", { name: /材料表/ });
  expect(link).toHaveAttribute("href", "/projects/project_1/data?object=object_1&version=version_1");
  expect(screen.getByRole("button", { name: "数据视图" })).toHaveAttribute("aria-pressed", "true");
  await waitFor(() => expect(link).toHaveFocus());
  expect(document.getElementById("data-navigator-content")).toHaveAttribute("data-mobile-collapsed", "false");
});

it("explains unavailable versions without hiding their names or offering invalid links", async () => {
  mocks.getProjectHistory.mockResolvedValue({ project: { id: "project_1", name: "研究项目", role: "owner" }, datasets: [], analyses: [] });
  mocks.listScientificObjects.mockResolvedValue({ items: [{ id: "object_pending", project_id: "project_1", lifecycle_status: "ACTIVE", display_name: "待处理的材料表", object_type: "DataFrame", current_version_id: null }], next_cursor: null });
  render(<ProjectDataPage projectId="project_1" />);
  await screen.findByRole("heading", { name: "这些数据暂时无法查看" });
  await userEvent.setup().click(screen.getByRole("button", { name: "查看数据视图" }));
  const directory = screen.getByRole("region", { name: "数据视图" });
  expect(within(directory).getByText("待处理的材料表")).toBeInTheDocument();
  expect(within(directory).getByText("1 项数据")).toBeInTheDocument();
  expect(within(directory).queryByRole("link")).not.toBeInTheDocument();
  await userEvent.setup().click(screen.getByRole("button", { name: "选择多个数据或科研对象" }));
  expect(screen.queryByRole("button", { name: "全选对象" })).not.toBeInTheDocument();
  expect(within(directory).queryByRole("checkbox")).not.toBeInTheDocument();
  mocks.listScientificObjects.mockRejectedValueOnce(new Error("Directory unavailable"));
  await userEvent.setup().click(screen.getByRole("button", { name: "重新加载数据视图" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("目录暂时无法更新，请重新加载。");
  expect(within(directory).queryByRole("alert")).not.toBeInTheDocument();
  expect(within(directory).getByText("待处理的材料表")).toBeInTheDocument();
});

it("shows read failure rather than an empty project and recovers the available views", async () => {
  mocks.getProjectHistory.mockResolvedValue({ project: { id: "project_1", name: "研究项目", role: "owner" }, datasets: [], analyses: [] });
  mocks.listScientificObjects.mockRejectedValueOnce(new Error("Directory unavailable")).mockResolvedValueOnce({ items: [{ id: "object_1", project_id: "project_1", lifecycle_status: "ACTIVE", display_name: "材料表", object_type: "DataFrame", current_version_id: "version_1" }], next_cursor: null });
  render(<ProjectDataPage projectId="project_1" />);
  await screen.findByRole("heading", { name: "暂时无法读取数据目录" });
  expect(screen.queryByText("尚无项目数据")).not.toBeInTheDocument();
  await userEvent.setup().click(screen.getByRole("button", { name: "重新加载目录" }));
  expect(await screen.findByRole("heading", { name: "选择一份数据开始查看" })).toBeInTheDocument();
  expect(mocks.listScientificObjects).toHaveBeenCalledTimes(2);
});

it("gives the scientific property table an accessible name and caption", () => {
  render(<TableScientificView dataset={{ name: "materials-table", profile: { semanticRoles: { band_gap: 3, density: 3 } } } as never} onInspect={vi.fn()} />);

  const table = screen.getByRole("table", { name: "materials-table科学属性" });
  expect(table).toHaveAccessibleName("materials-table科学属性");
  expect(table.querySelector("caption")).toHaveTextContent("科学属性、语义角色、记录数量和单位");
  expect(screen.getAllByRole("row").some((row) => row.getAttribute("aria-selected") === "false")).toBe(true);
  expect(screen.getAllByText("未声明")).toHaveLength(2);
  expect(screen.queryByText("eV")).not.toBeInTheDocument();
  expect(screen.queryByText("g/cm³")).not.toBeInTheDocument();
});

it("keeps Data table query, sort and row state in a bounded shareable route", async () => {
  const user = userEvent.setup();
  const onRouteStateChange = vi.fn();
  const dataset = {
    name: "materials-table",
    profile: { semanticRoles: { band_gap: 3, density: 3 } },
  } as never;
  const { rerender } = render(
    <TableScientificView
      dataset={dataset}
      onInspect={vi.fn()}
      initialQuery="den"
      initialSort="desc"
      initialSelectedRow="density"
      onRouteStateChange={onRouteStateChange}
    />,
  );

  expect(screen.getByRole("searchbox", { name: "搜索表格" })).toHaveValue("den");
  expect(screen.getByRole("button", { name: "切换排序" })).toHaveTextContent("↓");
  expect(screen.getByRole("row", { selected: true })).toHaveTextContent("density");
  expect(screen.getByRole("status")).toHaveTextContent("复制地址可恢复同一数据视图");

  await user.clear(screen.getByRole("searchbox", { name: "搜索表格" }));
  await user.type(screen.getByRole("searchbox", { name: "搜索表格" }), "band");
  expect(onRouteStateChange).toHaveBeenLastCalledWith(
    { query: "band" },
    "replace",
  );
  await user.click(screen.getByRole("button", { name: "切换排序" }));
  expect(onRouteStateChange).toHaveBeenCalledWith({ sort: "asc" }, "push");
  await user.click(screen.getByRole("row", { name: /band_gap/ }));
  expect(onRouteStateChange).toHaveBeenCalledWith({ row: "band_gap" }, "push");

  rerender(
    <TableScientificView
      dataset={dataset}
      onInspect={vi.fn()}
      initialQuery="band"
      initialSort="asc"
      initialSelectedRow="band_gap"
      onRouteStateChange={onRouteStateChange}
    />,
  );
  await waitFor(() =>
    expect(screen.getByRole("row", { selected: true })).toHaveTextContent(
      "band_gap",
    ),
  );
  rerender(
    <TableScientificView
      dataset={dataset}
      onInspect={vi.fn()}
      initialQuery="density"
      initialSort="asc"
      initialSelectedRow="density"
      onRouteStateChange={onRouteStateChange}
    />,
  );
  expect(screen.getByRole("searchbox", { name: "搜索表格" })).toHaveValue(
    "density",
  );
  await waitFor(() =>
    expect(screen.getByRole("row", { selected: true })).toHaveTextContent(
      "density",
    ),
  );
});

it("preserves exact Data authority while restoring only authorized canonical selection URLs", () => {
  const current =
    "http://127.0.0.1:3023/projects/project_1/data?dataset=dataset_1&object=object_1&version=version_1&tableQuery=old&tableSort=desc&tableRow=density";
  const next = new URL(
    dataTableViewHref(current, {
      query: "band gap",
      sort: "asc",
      row: "band_gap",
      selection: "opaque-token",
    }),
    "http://127.0.0.1:3023",
  );
  expect(next.searchParams.get("dataset")).toBe("dataset_1");
  expect(next.searchParams.get("object")).toBe("object_1");
  expect(next.searchParams.get("version")).toBe("version_1");
  expect(next.searchParams.get("tableQuery")).toBe("band gap");
  expect(next.searchParams.has("tableSort")).toBe(false);
  expect(next.searchParams.get("tableRow")).toBe("band_gap");
  expect(next.searchParams.get("selection")).toBe("opaque-token");

  const selection = validateWorkspaceSelectionContext({
    schemaVersion: "1.0",
    sourceScopeHash: "a".repeat(64),
    primary: {
      selectionSchemaVersion: "1.0",
      kind: "DATASET_SAMPLE",
      sourceScopeHash: "a".repeat(64),
      projectId: "project_1",
      datasetId: "dataset_1",
      datasetVersion: "v2",
      objectId: "object_1",
      sampleRef: "mat-2",
    },
    secondary: [],
    propagation: "EXACT_COMPATIBLE_ONLY",
    compatibility: "EXACT",
    cleared: false,
  });
  const token = encodeWorkspaceSelectionUrl(selection);
  expect(resolveDataPageSelection(token, "project_1", "dataset_1")).toEqual(
    selection,
  );
  expect(resolveDataPageSelection(token, "project_2", "dataset_1")).toBeNull();
  expect(resolveDataPageSelection(token, "project_1", "dataset_2")).toBeNull();
  expect(resolveDataPageSelection("not-canonical!", "project_1")).toBeNull();
});

it("keeps selection in the viewer and opens source details only on request with focus return", async () => {
  const user = userEvent.setup();
  render(<ProjectDataPage projectId="project_1" />);

  const trigger = await screen.findByRole("button", { name: "选择第一条科学数据" });
  await user.click(trigger);
  expect(screen.queryByRole("button", { name: "关闭详情" })).toBeNull();
  expect(trigger).toHaveFocus();
  const details = screen.getByRole("button", { name: "查看来源与属性" });
  await user.click(details);
  expect(screen.getByRole("heading", { name: "已选数据样本" })).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "关闭详情" }));
  await waitFor(() => expect(document.activeElement).toBe(details));
});

it("opens exact shared research from a participating dataset without assigning the routing dataset's outputs to it", async () => {
  const user = userEvent.setup();
  const history = await mocks.getProjectHistory();
  history.project.role = "viewer";
  history.datasets[0].import.files = [{ name: "NaCl_synthetic.cif" }];
  history.datasets[0].resultSummary = { artifactCount: 4 };
  const shared = { datasetId: "routing-dataset", sourceDatasetIds: ["routing-dataset", "dataset_1"], toolIds: ["structure.rdf"], artifactCount: 12, researchSessionId: "joint-session" };
  history.analyses = [
    { ...shared, jobId: "completed-job", researchTurnId: "completed-turn", status: "succeeded", researchTurnStatus: "COMPLETED", userQuestion: "比较两份材料的 RDF", createdAt: "2026-10-03T08:00:00Z" },
    { ...shared, jobId: "failed-job", researchTurnId: "failed-turn", status: "failed", userQuestion: "比较两份材料的 RDF", createdAt: "2026-10-02T08:00:00Z" },
    { jobId: "legacy-job", datasetId: "dataset_1", status: "succeeded", userQuestion: "原有的单材料分析", createdAt: "2026-10-01T08:00:00Z" },
    { ...shared, jobId: "foreign", datasetId: "dataset_1", sourceDatasetIds: ["another-dataset"], userQuestion: "路由字段不能代表来源" },
    { ...shared, jobId: "unverified", datasetId: "dataset_1", sourceDatasetIds: [], userQuestion: "未验证的历史来源" },
  ];
  render(<ProjectDataPage projectId="project_1" />);
  expect(screen.queryByRole("region", { name: "相关研究" })).toBeNull();
  await user.click(await screen.findByRole("button", { name: "查看来源与属性" }));
  expect(screen.getByRole("region", { name: "源文件" })).toHaveTextContent("NaCl_synthetic.cif");
  const studies = screen.getByRole("region", { name: "相关研究" });
  const links = within(studies).getAllByRole("link");
  expect(links.map(link => link.getAttribute("href"))).toEqual([
    "/projects/project_1/research/joint-session?turn=completed-turn",
    "/projects/project_1/research/joint-session?turn=failed-turn",
    "/projects/project_1/research?run=legacy-job",
  ]);
  expect(links[0]).toHaveTextContent("分析完成");
  expect(links[0]).toHaveTextContent("静态结构径向分布函数（RDF）");
  expect(links[0]).toHaveAttribute("title", "比较两份材料的 RDF");
  expect(links[0]).toHaveTextContent("2 份数据");
  expect(links[1]).toHaveTextContent("分析失败");
  expect(studies).toHaveTextContent("3 次分析");
  expect(studies).toHaveTextContent("4 个输出文件");
  expect(studies).not.toHaveTextContent("12 个输出文件");
  expect(studies).not.toHaveTextContent("路由字段不能代表来源");
  expect(studies).not.toHaveTextContent("未验证的历史来源");
  expect(screen.queryByRole("link", { name: "研究此数据" })).toBeNull();
  expect(history.analyses.map((run: { jobId: string }) => run.jobId)).toEqual(["completed-job", "failed-job", "legacy-job", "foreign", "unverified"]);
});

it("keeps older related research reachable and resets its disclosure when changing datasets", async () => {
  const user = userEvent.setup();
  const history = await mocks.getProjectHistory();
  history.datasets[0].import.files = [{ name: "first.cif" }];
  history.datasets.push({ ...history.datasets[0], datasetId: "dataset_2", name: "第二份材料", import: { fileCount: 1, files: [{ name: "second.cif" }], resources: [] } });
  history.analyses = [
    { jobId: "other", datasetId: "elsewhere", userQuestion: "其他数据的分析", createdAt: "2026-10-09T08:00:00Z" },
    ...Array.from({ length: 7 }, (_, index) => ({ jobId: `related-${index}`, sourceDatasetIds: ["dataset_1"], status: "succeeded", userQuestion: `第 ${index + 1} 次研究`, createdAt: `2026-10-0${index + 1}T08:00:00Z` })),
  ];
  mocks.searchQuery = "dataset=dataset_1";
  mocks.getDatasetSourceResources.mockImplementation(async (datasetId: string) => [{ objectId: `object-${datasetId}`, datasetId, objectType: "DataFrame", payload: [{ formula: "Si" }] }]);
  const view = render(<ProjectDataPage projectId="project_1" />);
  await user.click(await screen.findByRole("button", { name: "查看来源与属性" }));
  const studies = screen.getByRole("region", { name: "相关研究" });
  expect(within(studies).getAllByRole("link")).toHaveLength(5);
  expect(within(studies).getAllByRole("link")[0]).toHaveTextContent("第 7 次研究");
  await user.click(within(studies).getByRole("button", { name: "显示全部 7 次分析" }));
  expect(within(studies).getAllByRole("link")).toHaveLength(7);
  expect(studies).not.toHaveTextContent("其他数据的分析");
  mocks.searchQuery = "dataset=dataset_2";
  view.rerender(<ProjectDataPage projectId="project_1" />);
  expect(screen.getByRole("region", { name: "源文件" })).toHaveTextContent("second.cif");
  expect(screen.getByRole("region", { name: "相关研究" })).toHaveTextContent("暂无相关研究");
  expect(screen.queryByRole("link", { name: /第 7 次研究/ })).toBeNull();
  mocks.searchQuery = "dataset=dataset_1";
  view.rerender(<ProjectDataPage projectId="project_1" />);
  expect(within(screen.getByRole("region", { name: "相关研究" })).getAllByRole("link")).toHaveLength(5);
  expect(screen.getByRole("button", { name: "显示全部 7 次分析" })).toHaveAttribute("aria-expanded", "false");
});

it("does not invent source filenames or infer membership from an invalid explicit source list", async () => {
  const history = await mocks.getProjectHistory();
  history.analyses = [{ jobId: "invalid-source", datasetId: "dataset_1", sourceDatasetIds: null, userQuestion: "不应推断的来源" }];
  render(<ProjectDataPage projectId="project_1" />);
  await userEvent.setup().click(await screen.findByRole("button", { name: "查看来源与属性" }));
  expect(screen.getByRole("region", { name: "源文件" })).toHaveTextContent("源文件名称未记录");
  expect(screen.getByRole("region", { name: "相关研究" })).toHaveTextContent("暂无相关研究");
  expect(screen.queryByRole("link", { name: /不应推断的来源/ })).toBeNull();
  expect(screen.queryByText("内容类型与可用属性来自已生成的数据语义档案。")).toBeNull();
});

it("lists all projects without inferring product categories from test naming conventions", async () => {
  const user = userEvent.setup();
  mocks.listProjects.mockResolvedValue([
    { id: "case_1", name: "Case 13 · Q-PHONON-001 · Run 01", description: "声子色散、声子态密度与布里渊区联动（Phase 10H / 10I）" },
    { id: "phase_1", name: "Phase 10 · Viewer validation · Run 01", description: "结构查看器阶段记录" },
    { id: "other_1", name: "其他 · Legacy Session · Run 01", description: "历史研究会话" },
  ]);

  render(<ProjectsPage />);

  expect(await screen.findByRole("region", { name: "项目列表" })).toBeInTheDocument();
  expect(screen.queryByRole("heading", { name: "16-case 项目" })).not.toBeInTheDocument();
  expect(screen.queryByRole("heading", { name: "Phase 项目" })).not.toBeInTheDocument();
  expect(screen.queryByRole("heading", { name: "其他项目与历史记录" })).not.toBeInTheDocument();
  expect(screen.getByText(/声子色散、声子态密度/)).toBeInTheDocument();

  await user.type(screen.getByRole("searchbox", { name: "搜索项目、描述或标签" }), "Phase 10H");
  expect(screen.getByText("Case 13 · Q-PHONON-001 · Run 01")).toBeInTheDocument();
  expect(screen.queryByText("其他 · Legacy Session · Run 01")).not.toBeInTheDocument();
});

it("pins a project from its management menu and keeps the action state visible", async () => {
  const user = userEvent.setup();
  mocks.listProjects.mockResolvedValue([
    { id: "project_a", name: "Alpha project", role: "owner", status: "active", pinned: false },
    { id: "project_b", name: "Beta project", role: "owner", status: "active", pinned: true },
  ]);
  mocks.updateProject.mockResolvedValueOnce({
    id: "project_a",
    projectId: "project_a",
    name: "Alpha project",
    role: "owner",
    status: "active",
    pinned: true,
  });

  render(<ProjectsPage />);
  expect(await screen.findByText("Beta project")).toBeInTheDocument();
  const alpha = screen.getByText("Alpha project");
  fireEvent.contextMenu(alpha.closest(".managed-object-row")!);
  await user.click(screen.getByRole("menuitem", { name: "列表置顶" }));
  await waitFor(() =>
    expect(mocks.updateProject).toHaveBeenCalledWith("project_a", { pinned: true }, expect.any(AbortSignal)),
  );
  expect(
    within(screen.getByText("Alpha project").closest(".managed-object-row")!)
      .getByText("列表置顶 · 打开项目 →"),
  ).toBeInTheDocument();
});

it("exports an authorized non-executable project provenance manifest from the actions menu", async () => {
  const user = userEvent.setup();
  const createObjectURL = vi.fn(() => "blob:project-manifest");
  const revokeObjectURL = vi.fn();
  vi.stubGlobal("URL", { createObjectURL, revokeObjectURL });
  const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
  render(<ProjectsPage />);

  const row = (await screen.findByText("Perovskite stability study")).closest(".managed-object-row")!;
  fireEvent.contextMenu(row);
  await user.click(screen.getByRole("menuitem", { name: "导出项目清单" }));

  await waitFor(() => expect(mocks.getProjectExportManifest).toHaveBeenCalledWith("project_1", expect.any(AbortSignal)));
  expect(click).toHaveBeenCalled();
  expect(screen.getByText(/已导出“Perovskite stability study”/)).toBeInTheDocument();
  vi.unstubAllGlobals();
  click.mockRestore();
});

it("creates a project from the Console and offers the upload continuation", async () => {
  const user = userEvent.setup();
  render(<ConsolePage />);

  await user.click(await screen.findByRole("button", { name: "新建项目" }));
  expect(screen.getByRole("dialog", { name: "新建研究项目" })).toBeInTheDocument();
  await user.type(screen.getByLabelText("项目名称"), "新项目");
  await user.type(screen.getByLabelText(/研究说明/), "结构与电子性质研究");
  await user.click(screen.getByRole("button", { name: "创建项目" }));

  await waitFor(() => expect(mocks.createProject).toHaveBeenCalledWith("新项目", expect.any(AbortSignal)));
  expect(await screen.findByRole("link", { name: "上传数据" })).toHaveAttribute("href", "/projects/project_2/datasets/new");
});

it("restores focus to the Console trigger after closing project creation", async () => {
  const user = userEvent.setup();
  render(<ConsolePage />);

  const trigger = await screen.findByRole("button", { name: "新建项目" });
  await user.click(trigger);
  await user.click(screen.getByRole("button", { name: "关闭" }));
  await waitFor(() => expect(document.activeElement).toBe(trigger));
});

it("does not encourage duplicate creation when optional project description fails", async () => {
  const user = userEvent.setup();
  mocks.updateProject.mockRejectedValueOnce(new Error("temporary write failure"));
  render(<ConsolePage />);

  await user.click(await screen.findByRole("button", { name: "新建项目" }));
  await user.type(screen.getByLabelText("项目名称"), "新项目");
  await user.type(screen.getByLabelText(/研究说明/), "待保存说明");
  await user.click(screen.getByRole("button", { name: "创建项目" }));

  expect(await screen.findByRole("dialog", { name: "项目已创建" })).toBeInTheDocument();
  expect(await screen.findByRole("alert")).toHaveTextContent("项目已创建，研究说明的保存结果尚未确认");
  expect(mocks.createProject).toHaveBeenCalledTimes(1);
});

it.each([
  { name: "Projects", Page: ProjectsPage },
  { name: "Console", Page: ConsolePage },
])("recovers the project directory without remounting ($name)", async ({ Page }) => {
  const user = userEvent.setup();
  mocks.listProjects.mockRejectedValueOnce(new Error("目录连接失败"));
  render(<Page />);
  expect(await screen.findByRole("alert")).toHaveTextContent("暂时无法读取项目列表");
  await user.click(screen.getByRole("button", { name: "重新加载项目数据" }));
  expect((await screen.findAllByText("Perovskite stability study")).length).toBeGreaterThan(0);
  expect(mocks.listProjects).toHaveBeenLastCalledWith({ forceRefresh: true, signal: expect.any(AbortSignal) });
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
});

it("preserves project filters across a failed post-mutation refresh and retries only the read", async () => {
  const user = userEvent.setup();
  const projects = [{ id: "project_1", name: "Alpha", role: "owner", status: "archived", tags: ["材料"] }];
  mocks.listProjects.mockResolvedValue(projects).mockResolvedValueOnce(projects).mockRejectedValueOnce(new Error("列表刷新失败"));
  render(<ProjectsPage />);
  await user.click(await screen.findByRole("button", { name: "已归档" }));
  await user.type(screen.getByRole("searchbox"), "Alpha");
  await user.selectOptions(screen.getByLabelText("标签"), "材料");
  await user.click(screen.getByRole("button", { name: "选择" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 Alpha" }));
  await user.click(screen.getByRole("button", { name: "列表置顶" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("暂时无法读取项目列表");
  expect(screen.getByText("已列表置顶 1 个项目。")).toHaveAttribute("role", "status");
  await user.click(screen.getByRole("button", { name: "重新加载项目数据" }));
  await screen.findByText("Alpha");
  expect(screen.getByRole("searchbox")).toHaveValue("Alpha");
  expect(screen.getByLabelText("标签")).toHaveValue("材料");
  expect(screen.getByRole("button", { name: "已归档" })).toHaveAttribute("aria-pressed", "true");
  expect(mocks.bulkProjectAction).toHaveBeenCalledTimes(1);
  expect(screen.queryByRole("region", { name: "批量项目操作" })).not.toBeInTheDocument();
});

it("keeps the selection after a failed batch and announces successful retry", async () => {
  const user = userEvent.setup();
  mocks.bulkProjectAction.mockRejectedValueOnce(new Error("批量服务不可用"));
  render(<ProjectsPage />);
  await user.click(await screen.findByRole("button", { name: "选择" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 Perovskite stability study" }));
  await user.click(screen.getByRole("button", { name: "归档" }));
  expect(await screen.findByText(/批量更新项目的结果尚未确认/)).toBeInTheDocument();
  expect(screen.getByRole("checkbox", { name: "选择 Perovskite stability study" })).toBeChecked();
  expect(mocks.listProjects).toHaveBeenCalledTimes(1);
  await user.click(screen.getByRole("button", { name: "重新读取项目列表" }));
  await waitFor(() => expect(screen.queryByText(/批量更新项目的结果尚未确认/)).not.toBeInTheDocument());
  expect(screen.getByRole("checkbox", { name: "选择 Perovskite stability study" })).toBeChecked();
  await user.click(screen.getByRole("button", { name: "归档" }));
  expect(await screen.findByText("已归档 1 个项目。")).toHaveAttribute("role", "status");
  await screen.findByRole("button", { name: "选择" });
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
});

it("opens the same project actions from right click and supports explicit batch selection", async () => {
  const user = userEvent.setup();
  mocks.listProjects.mockResolvedValue([
    { id: "case_1", name: "Case 01 · Q-TABLE-001 · Run 01", role: "owner", status: "active", description: "材料属性表" },
    { id: "case_2", name: "Case 02 · Q-STRUCTURE-001 · Run 01", role: "owner", status: "active", description: "晶体结构" },
  ]);
  render(<ProjectsPage />);

  const title = await screen.findByText("Case 01 · Q-TABLE-001 · Run 01");
  fireEvent.contextMenu(title.closest(".managed-object-row")!);
  expect(screen.getByRole("menu", { name: /Case 01/ })).toBeInTheDocument();
  expect(screen.getByRole("menuitem", { name: "上传数据" })).toBeInTheDocument();
  expect(screen.getByRole("menuitem", { name: "编辑项目信息" })).toBeInTheDocument();
  await user.keyboard("{Escape}");
  await waitFor(() => expect(document.activeElement).toBe(screen.getByRole("button", { name: /管理 Case 01/ })));

  await user.click(screen.getByRole("button", { name: "选择" }));
  await user.click(screen.getByRole("checkbox", { name: /选择 Case 01/ }));
  expect(screen.getByText("1 个已选择")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "归档" }));
  await waitFor(() => expect(mocks.bulkProjectAction).toHaveBeenCalledWith(["case_1"], "archive", expect.any(AbortSignal)));
});

it("supports bounded bulk pinning from the project selection toolbar", async () => {
  const user = userEvent.setup();
  mocks.listProjects.mockResolvedValue([
    { id: "project_a", name: "Alpha project", role: "owner", status: "active", description: "结构研究" },
    { id: "project_b", name: "Beta project", role: "owner", status: "active", description: "电子研究" },
  ]);
  render(<ProjectsPage />);

  await user.click(await screen.findByRole("button", { name: "选择" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 Alpha project" }));
  await user.click(screen.getByRole("button", { name: "列表置顶" }));
  await waitFor(() =>
    expect(mocks.bulkProjectAction).toHaveBeenCalledWith(["project_a"], "pin", expect.any(AbortSignal)),
  );
});

it("previews project dependencies before bulk-moving projects to Trash", async () => {
  const user = userEvent.setup();
  mocks.listProjects.mockResolvedValue([
    {
      id: "project_a",
      name: "Alpha project",
      role: "owner",
      status: "active",
      description: "结构研究",
    },
    {
      id: "project_b",
      name: "Beta project",
      role: "owner",
      status: "active",
      description: "电子研究",
    },
  ]);
  mocks.getProjectDependencyImpact
    .mockResolvedValueOnce({
      entity: "project",
      entityId: "project_a",
      displayName: "Alpha project",
      canDelete: false,
      dependencyCount: 2,
      dependencies: [
        { kind: "scientific_results", label: "ScientificResult", count: 2 },
      ],
      impact: {
        removedFromActiveDiscovery: true,
        historicalProvenanceProtected: true,
        historicalResearchRemainsAccessible: true,
      },
    })
    .mockResolvedValueOnce({
      entity: "project",
      entityId: "project_b",
      displayName: "Beta project",
      canDelete: true,
      dependencyCount: 0,
      dependencies: [],
      impact: {
        removedFromActiveDiscovery: true,
        historicalProvenanceProtected: true,
        historicalResearchRemainsAccessible: true,
      },
    });

  render(<ProjectsPage />);
  await user.click(await screen.findByRole("button", { name: "选择" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 Alpha project" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 Beta project" }));
  await user.click(screen.getByRole("button", { name: "移入回收站" }));

  const dialog = await screen.findByRole("dialog", {
    name: "将 2 个项目移入回收站",
  });
  expect(dialog).toHaveTextContent("ScientificResult：2");
  expect(mocks.bulkProjectAction).not.toHaveBeenCalled();

  await user.click(
    within(dialog).getByRole("button", { name: "确认移入回收站" }),
  );
  await waitFor(() =>
    expect(mocks.bulkProjectAction).toHaveBeenCalledWith(
      ["project_a", "project_b"],
      "trash", expect.any(AbortSignal)),
  );
});

it("keeps missing normalized scientific resources recoverable in the Viewer context", async () => {
  const user = userEvent.setup();
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [{
      datasetId: "dataset_xrd",
      name: "实验 XRD",
      status: "profile_ready",
      import: { fileCount: 2, resources: [] },
      profile: { objectCount: 2, semanticRoles: {} },
    }],
    analyses: [],
  });
  mocks.getDatasetSourceResources
    .mockRejectedValueOnce(new Error("此数据的解析资源暂时无法读取。源文件与数据记录仍然保留，可重试加载或重新导入源文件。"))
    .mockResolvedValueOnce([{
      objectId: "xrd_1",
      objectType: "DataFrame",
      datasetId: "dataset_xrd",
      payload: [{ two_theta: 20, intensity: 100 }],
    }]);

  render(<ProjectDataPage projectId="project_1" />);

  expect(await screen.findByRole("alert")).toHaveTextContent("数据档案、精确来源与解析记录仍然保留");
  expect(screen.getByRole("button", { name: "重新加载数据" })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "查看来源与属性" })).toBeInTheDocument();
  expect(screen.queryByRole("link", { name: "研究此数据" })).toBeNull();
  expect(screen.queryByText("Failed to fetch")).not.toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: "重新加载数据" }));
  expect(await screen.findByTestId("quick-preview-scientific-viewer")).toHaveTextContent("DataFrame");
  expect(mocks.getDatasetSourceResources).toHaveBeenCalledTimes(2);
});

it("explains a failed table read, retains the loaded profile and retries the actual source", async () => {
  const user = userEvent.setup();
  const history = await mocks.getProjectHistory();
  history.datasets[0].profile.semanticRoles = { band_gap: 3 };
  mocks.getDatasetSourceResources.mockRejectedValueOnce(new Error("private upstream traceback"));

  render(<ProjectDataPage projectId="project_1" />);

  expect(await screen.findByRole("alert")).toHaveTextContent("表格数据尚未加载");
  expect(screen.getByRole("heading", { name: "materials-table" })).toBeInTheDocument();
  expect(screen.queryByRole("link", { name: "研究此数据" })).toBeNull();
  expect(screen.queryByText(/private upstream traceback/)).toBeNull();
  await user.click(screen.getByText("查看已读取的列描述"));
  expect(screen.getByRole("table", { name: "materials-table科学属性" })).toHaveTextContent("band_gap");
  await user.click(screen.getByRole("button", { name: "查看来源与属性" }));
  const inspector = screen.getByRole("region", { name: "materials-table" });
  expect(inspector).toHaveTextContent("3");
  await user.keyboard("{Escape}");
  await user.click(screen.getByRole("button", { name: "重新加载数据" }));

  expect(await screen.findByTestId("quick-preview-scientific-viewer")).toHaveTextContent("DataFrame");
  expect(screen.getByRole("link", { name: "研究此数据" })).toHaveAttribute("href", "/projects/project_1/research?dataset=dataset_1");
  expect(screen.queryByRole("alert")).toBeNull();
  expect(mocks.getDatasetSourceResources).toHaveBeenCalledTimes(2);
});

it.each(["search", "tag", "status"] as const)("limits project batch actions to the visible writable selection after changing %s", async (filter) => {
  const user = userEvent.setup();
  mocks.listProjects.mockResolvedValue([
    { id: "project_a", name: "Alpha", role: "owner", status: "active", tags: ["材料"] },
    { id: "project_b", name: "Beta", role: "owner", status: "active", tags: ["电子"] },
    { id: "project_c", name: "Gamma", role: "owner", status: "archived", tags: ["材料"] },
  ]);
  render(<ProjectsPage />);
  await user.click(await screen.findByRole("button", { name: "选择" }));
  await user.click(screen.getByRole("button", { name: "选择当前结果" }));
  const batch = screen.getByRole("region", { name: "批量项目操作" });
  expect(batch).toHaveTextContent("2 个已选择");
  if (filter === "search") await user.type(screen.getByRole("searchbox"), "Alpha");
  else if (filter === "tag") await user.selectOptions(screen.getByLabelText("标签"), "材料");
  else await user.click(screen.getByRole("button", { name: "已归档" }));
  if (filter === "status") {
    expect(batch).toHaveTextContent("0 个已选择");
    expect(within(batch).getByRole("button", { name: "移入回收站" })).toBeDisabled();
    await user.click(screen.getByRole("checkbox", { name: "选择 Gamma" }));
  }
  expect(batch).toHaveTextContent("1 个已选择");
  await user.click(within(batch).getByRole("button", { name: "移入回收站" }));
  const dialog = await screen.findByRole("dialog", { name: "将 1 个项目移入回收站" });
  const expectedId = filter === "status" ? "project_c" : "project_a";
  await waitFor(() => expect(mocks.getProjectDependencyImpact).toHaveBeenCalledWith(expectedId, expect.any(AbortSignal)));
  expect(mocks.getProjectDependencyImpact).toHaveBeenCalledTimes(1);
  await user.click(within(dialog).getByRole("button", { name: "确认移入回收站" }));
  await waitFor(() => expect(mocks.bulkProjectAction).toHaveBeenCalledWith([expectedId], "trash", expect.any(AbortSignal)));
});

it("searches organization tags even when the name and description do not contain the query", async () => {
  const user = userEvent.setup();
  mocks.listProjects.mockResolvedValue([
    { id: "tagged", name: "Alpha", role: "owner", status: "active", tags: ["待复核"] },
    { id: "untagged", name: "Beta", role: "owner", status: "active", tags: [] },
  ]);
  render(<ProjectsPage />);
  await user.type(await screen.findByRole("searchbox"), "待复核");
  expect(screen.getByText("Alpha")).toBeInTheDocument();
  expect(screen.queryByText("Beta")).toBeNull();
  expect(screen.getByRole("status")).toHaveTextContent("1 个项目");
});

it("distinguishes filtered-out projects from empty trash and clears the filters in place", async () => {
  const user = userEvent.setup();
  mocks.listProjects.mockResolvedValue([
    { id: "active", name: "Alpha", role: "owner", status: "active" },
    { id: "trashed", name: "Beta", role: "owner", status: "trashed" },
  ]);
  render(<ProjectsPage />);
  await user.click(await screen.findByRole("button", { name: "回收站" }));
  await user.type(screen.getByRole("searchbox"), "unmatched");
  expect(screen.getByText(/当前搜索与筛选条件下没有项目/)).toBeInTheDocument();
  expect(screen.queryByText("回收站为空。")).toBeNull();
  await user.click(screen.getByRole("button", { name: "清除搜索与筛选" }));
  expect(screen.getByText("Alpha")).toBeInTheDocument();
  expect(screen.getByRole("searchbox")).toHaveValue("");
  expect(screen.getByRole("button", { name: "当前" })).toHaveAttribute("aria-pressed", "true");
});

it("bounds a stalled source read and ignores its late response after recovery", async () => {
  let resolveStalled!: (items: unknown[]) => void;
  let stalledSignal!: AbortSignal;
  mocks.getDatasetSourceResources.mockImplementationOnce((_id: string, signal: AbortSignal) => {
    stalledSignal = signal;
    return new Promise((resolve) => { resolveStalled = resolve; });
  });
  vi.useFakeTimers();
  try {
    await act(async () => { render(<ProjectDataPage projectId="project_1" />); });
    expect(screen.getByText("正在加载科学数据…")).toBeInTheDocument();
    await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
    expect(screen.getByRole("alert")).toHaveTextContent("读取科学数据超时");
    expect(stalledSignal.aborted).toBe(true);
  } finally {
    vi.useRealTimers();
  }
  await userEvent.setup().click(screen.getByRole("button", { name: "重新加载数据" }));
  expect(await screen.findByTestId("quick-preview-scientific-viewer")).toHaveTextContent("DataFrame");
  await act(async () => { resolveStalled([{ objectId: "late", objectType: "CrystalStructure" }]); });
  expect(screen.getByTestId("quick-preview-scientific-viewer")).toHaveTextContent("DataFrame");
});

it("does not let a previous dataset response replace the current source", async () => {
  const history = await mocks.getProjectHistory();
  history.datasets.push({ ...history.datasets[0], datasetId: "dataset_2", name: "Second dataset" });
  let resolvePrevious!: (items: unknown[]) => void;
  let previousSignal!: AbortSignal;
  mocks.getDatasetSourceResources.mockImplementationOnce((_id: string, signal: AbortSignal) => {
    previousSignal = signal;
    return new Promise((resolve) => { resolvePrevious = resolve; });
  }).mockResolvedValueOnce([{ objectId: "second", objectType: "Second table", datasetId: "dataset_2" }]);
  const { rerender } = render(<ProjectDataPage projectId="project_1" initialDatasetId="dataset_1" />);
  await screen.findByText("正在加载科学数据…");
  rerender(<ProjectDataPage projectId="project_1" initialDatasetId="dataset_2" />);
  expect(await screen.findByTestId("quick-preview-scientific-viewer")).toHaveTextContent("Second table");
  expect(previousSignal.aborted).toBe(true);
  await act(async () => { resolvePrevious([{ objectId: "old", objectType: "Previous table", datasetId: "dataset_1" }]); });
  expect(screen.getByTestId("quick-preview-scientific-viewer")).toHaveTextContent("Second table");
  expect(screen.getByRole("link", { name: "研究此数据" })).toHaveAttribute("href", "/projects/project_1/research?dataset=dataset_2");
});

it("does not describe an unclassified 404 as confirmed source deletion", async () => {
  mocks.getDatasetSourceResources.mockRejectedValueOnce(Object.assign(new Error("Unknown route"), { status: 404 }));
  render(<ProjectDataPage projectId="project_1" />);
  expect(await screen.findByRole("alert")).toHaveTextContent("暂时无法读取");
  expect(screen.queryByText("已确认缺失")).toBeNull();
  expect(screen.getByRole("button", { name: "重新加载数据" })).toBeInTheDocument();
});

it("distinguishes confirmed missing source bytes from a transient storage failure", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [{
      datasetId: "dataset_missing",
      name: "历史轨迹",
      status: "profile_ready",
      import: { fileCount: 1, resources: [] },
      profile: { objectCount: 1, semanticRoles: {} },
    }],
    analyses: [],
  });
  const missing = Object.assign(
    new Error("SOURCE_MISSING"),
    { status: 404, errorType: "SOURCE_MISSING" },
  );
  mocks.getDatasetSourceResources.mockRejectedValueOnce(missing);

  render(<ProjectDataPage projectId="project_1" />);

  expect(await screen.findByRole("alert")).toHaveTextContent(
    "原始科学数据当前不可用",
  );
  expect(screen.getByRole("status")).toHaveTextContent("已确认缺失");
  expect(screen.getByRole("button", { name: "再次确认来源" })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "重新导入源文件" })).toHaveAttribute(
    "href",
    "/projects/project_1/datasets/new",
  );
  const fallback = screen.getByRole("alert");
  const fallbackTitle = fallback.querySelector("strong[id]");
  expect(fallbackTitle?.id).toMatch(/^science-fallback-title-/u);
  expect(fallback).toHaveAttribute("aria-labelledby", fallbackTitle?.id);
  expect(screen.getByText(/不会用其他版本替代/)).toBeInTheDocument();
});

it("presents a never-populated Dataset as an import empty state instead of a storage failure", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [{
      datasetId: "dataset_empty",
      name: "待导入数据",
      status: "created",
      import: { fileCount: 0, resources: [] },
      profile: { objectCount: 0, semanticRoles: {} },
    }],
    analyses: [],
  });
  mocks.getDatasetSourceResources.mockResolvedValue([]);

  render(<ProjectDataPage projectId="project_1" />);

  expect(await screen.findByText("这个数据集还没有科学对象")).toBeInTheDocument();
  expect(screen.getByText(/可继续接收材料数据/)).toBeInTheDocument();
  expect(screen.queryByText(/解析资源暂时无法读取/)).toBeNull();
  expect(screen.queryByRole("button", { name: "重新加载数据" })).toBeNull();
  expect(screen.queryByRole("link", { name: "研究此数据" })).toBeNull();
});

it("shows one directory at a time while preserving exact source and version links", async () => {
  const user = userEvent.setup();
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [{
      datasetId: "dataset_1",
      name: "高熵合金来源数据",
      status: "profile_ready",
      import: { fileCount: 2, resources: [] },
      profile: { objectCount: 2, rowCount: 2, semanticRoles: {} },
    }],
    analyses: [],
  });
  mocks.listScientificObjects.mockResolvedValue({
    items: [
      {
        id: "object_1",
        project_id: "project_1",
        kind: "STRUCTURE",
        object_type: "structure.crystal",
        display_name: "合金结构 A",
        lifecycle_status: "ACTIVE",
        current_version_id: "version_1",
      },
      {
        id: "object_2",
        project_id: "project_1",
        kind: "TABLE",
        object_type: "materials.table",
        display_name: "材料表 B",
        lifecycle_status: "ACTIVE",
        current_version_id: "version_2",
      },
    ],
    next_cursor: null,
  });
  mocks.getDatasetSourceResources.mockResolvedValue([
    {
      objectId: "resource_1",
      objectType: "DataFrame",
      datasetId: "dataset_1",
      payload: [{ formula: "FeNiCoCr" }],
    },
  ]);

  render(<ProjectDataPage projectId="project_1" />);

  expect(await screen.findByRole("link", { name: /高熵合金来源数据/ })).toBeInTheDocument();
  expect(screen.queryByRole("link", { name: /合金结构 A/ })).not.toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "数据视图" }));
  expect(screen.getByRole("link", { name: /合金结构 A/ })).toHaveAttribute("href", "/projects/project_1/data?object=object_1&version=version_1");
  expect(screen.getByRole("link", { name: /材料表 B/ })).toHaveAttribute("href", "/projects/project_1/data?object=object_2&version=version_2");
  expect(screen.queryByRole("link", { name: /高熵合金来源数据/ })).not.toBeInTheDocument();
  expect(screen.queryByText("数据层级与来源说明")).not.toBeInTheDocument();
  expect(screen.queryByText("解析后的科学身份")).not.toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "上传记录" }));
  expect(screen.getByRole("link", { name: /高熵合金来源数据/ })).toHaveAttribute("href", "/projects/project_1/data?dataset=dataset_1");
  await user.click(screen.getByRole("button", { name: "选择多个数据或科研对象" }));
  await user.click(screen.getByRole("button", { name: "全选数据" }));
  expect(screen.queryByRole("button", { name: "全选对象" })).not.toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "数据视图" }));
  expect(screen.queryByRole("region", { name: "批量数据操作" })).not.toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "选择多个数据或科研对象" }));
  expect(screen.getByRole("region", { name: "批量数据操作" })).toHaveTextContent("0 个已选择");
  expect(screen.queryByRole("button", { name: "全选数据" })).not.toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "全选对象" }));
  expect(screen.getByRole("region", { name: "批量数据操作" })).toHaveTextContent("2 个已选择");
  expect(mocks.bulkDatasetAction).not.toHaveBeenCalled();
  expect(mocks.bulkUpdateScientificObjects).not.toHaveBeenCalled();
});
it("lets mobile users collapse the data context without losing its explicit location", async () => {
  const user = userEvent.setup();
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [{
      datasetId: "dataset_xrd",
      name: "实验 XRD",
      status: "profile_ready",
      import: { fileCount: 1, resources: [] },
      profile: { objectCount: 1, semanticRoles: {} },
    }],
    analyses: [],
  });
  render(<ProjectDataPage projectId="project_1" />);
  const toggle = await screen.findByRole("button", { name: "收起目录" });
  expect(toggle).toHaveAttribute("aria-expanded", "true");
  await user.click(toggle);
  expect(screen.getByRole("button", { name: "展开目录" })).toHaveAttribute("aria-expanded", "false");
  expect(screen.getByRole("heading", { name: "项目数据" })).toBeInTheDocument();
  expect(screen.queryByRole("heading", { name: "研究项目" })).not.toBeInTheDocument();
  expect(document.getElementById("data-navigator-content")).toHaveAttribute("data-mobile-collapsed", "true");
  expect(document.getElementById("data-navigator-content")).toContainElement(screen.getByRole("group", { name: "数据集状态" }));
  await user.click(screen.getByRole("button", { name: "展开目录" }));
  expect(document.getElementById("data-navigator-content")).toHaveAttribute("data-mobile-collapsed", "false");
});

it("moves a project to the recoverable trash with a dependency preview", async () => {
  const user = userEvent.setup();
  mocks.listProjects.mockResolvedValue([
    { id: "case_1", projectId: "case_1", name: "可恢复项目", role: "owner", status: "active", description: "保留历史 provenance" },
  ]);
  mocks.getProjectDependencyImpact.mockResolvedValue({
    entity: "project",
    entityId: "case_1",
    displayName: "可恢复项目",
    canDelete: false,
    dependencyCount: 2,
    dependencies: [{
      kind: "scientific_results",
      label: "科学结果",
      count: 2,
      href: "/projects/case_1/research",
    }],
    impact: { removedFromActiveDiscovery: true, historicalProvenanceProtected: true, historicalResearchRemainsAccessible: true },
  });
  mocks.updateProject.mockResolvedValueOnce({
    id: "case_1",
    projectId: "case_1",
    name: "可恢复项目",
    role: "owner",
    status: "trashed",
  });
  render(<ProjectsPage />);

  await user.click(await screen.findByRole("button", { name: "管理 可恢复项目" }));
  await user.click(screen.getByRole("menuitem", { name: "移入回收站" }));
  expect(await screen.findByRole("dialog", { name: "将项目移入回收站" })).toHaveTextContent("科学结果：2");
  expect(screen.getByRole("link", { name: "科学结果" })).toHaveAttribute(
    "href",
    "/projects/case_1/research",
  );
  await user.click(screen.getByRole("button", { name: "移入回收站" }));
  await waitFor(() =>
    expect(mocks.updateProject).toHaveBeenCalledWith("case_1", {
      lifecycle: "TRASHED",
    }, expect.any(AbortSignal)),
  );

  await user.click(screen.getByRole("button", { name: "回收站" }));
  expect(await screen.findByText("可恢复项目")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "管理 可恢复项目" }));
  expect(screen.queryByRole("menuitem", { name: "上传数据" })).not.toBeInTheDocument();
  expect(screen.getByRole("menuitem", { name: "从回收站恢复" })).toBeInTheDocument();
});

it("restores focus to the originating project row after editing from its menu", async () => {
  const user = userEvent.setup();
  mocks.listProjects.mockResolvedValue([
    { id: "case_1", name: "Case 01 · Q-TABLE-001 · Run 01", role: "owner", status: "active", description: "材料属性表" },
  ]);
  render(<ProjectsPage />);

  const trigger = await screen.findByRole("button", { name: /管理 Case 01/ });
  await user.click(trigger);
  await user.click(screen.getByRole("menuitem", { name: "编辑项目信息" }));
  expect(screen.getByRole("dialog", { name: "编辑项目信息" })).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "关闭" }));
  await waitFor(() => expect(document.activeElement).toBe(trigger));
});

it.each(["escape", "cancel", "close", "save"] as const)("dismisses a project management deep link after %s without reopening it", async (action) => {
  const user = userEvent.setup();
  window.history.replaceState({}, "", "/projects?manage=project_1&view=all#row");
  try {
    const { rerender } = render(<ProjectsPage manageProjectId="project_1" />);
    const dialog = await screen.findByRole("dialog", { name: "编辑项目信息" });
    if (action === "escape") await user.keyboard("{Escape}");
    else await user.click(within(dialog).getByRole("button", { name: { cancel: "取消", close: "关闭", save: "保存更改" }[action] }));
    await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
    expect(mocks.routerReplace).toHaveBeenCalledWith("/projects?view=all#row", { scroll: false });
    await waitFor(() => expect(screen.getByRole("heading", { name: "项目" })).toHaveFocus());
    rerender(<ProjectsPage manageProjectId="project_1" />);
    expect(screen.queryByRole("dialog")).toBeNull();
    rerender(<ProjectsPage manageProjectId="" />);
    rerender(<ProjectsPage manageProjectId="project_1" />);
    expect(await screen.findByRole("dialog", { name: "编辑项目信息" })).toBeInTheDocument();
  } finally {
    window.history.replaceState({}, "", "/");
  }
});

it.each(["missing", "viewer"] as const)("explains a %s management link without opening a writable editor", async (kind) => {
  const user = userEvent.setup();
  if (kind === "viewer") mocks.listProjects.mockResolvedValue([{ id: "project_1", name: "Shared project", role: "viewer", status: "active" }]);
  const manageId = kind === "missing" ? "missing" : "project_1";
  window.history.replaceState({}, "", `/projects?manage=${manageId}`);
  try {
    render(<ProjectsPage manageProjectId={manageId} />);
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(kind === "missing" ? "无法打开项目管理" : "当前为只读");
    expect(screen.queryByRole("dialog")).toBeNull();
    await user.click(within(alert).getByRole("button", { name: "返回项目列表" }));
    expect(mocks.routerReplace).toHaveBeenCalledWith("/projects", { scroll: false });
    expect(screen.queryByRole("alert")).toBeNull();
    expect(mocks.updateProject).not.toHaveBeenCalled();
  } finally {
    window.history.replaceState({}, "", "/");
  }
});

it("retains an edited project draft until an uncertain save is reconciled by a successful read", async () => {
  const user = userEvent.setup();
  mocks.updateProject.mockRejectedValueOnce(new Error("offline"));
  render(<ProjectsPage />);
  await user.click(await screen.findByRole("button", { name: "管理 Perovskite stability study" }));
  await user.click(screen.getByRole("menuitem", { name: "编辑项目信息" }));
  const name = screen.getByLabelText("项目名称");
  await user.clear(name); await user.type(name, "保留编辑内容");
  await user.click(screen.getByRole("button", { name: "保存更改" }));
  expect(await screen.findByText(/保存项目的结果尚未确认/)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "保存更改" })).toBeDisabled();
  mocks.listProjects.mockRejectedValueOnce(new Error("still offline"));
  await user.click(screen.getByRole("button", { name: "重新读取项目列表" }));
  expect(await screen.findByText(/当前编辑内容已保留/)).toBeInTheDocument();
  expect(name).toHaveValue("保留编辑内容");
  await user.click(screen.getByRole("button", { name: "重新读取项目列表" }));
  await waitFor(() => expect(screen.getByRole("button", { name: "保存更改" })).toBeEnabled());
  await waitFor(() => expect(name).toHaveFocus());
  expect(name).toHaveValue("保留编辑内容"); expect(mocks.updateProject).toHaveBeenCalledOnce();
  await user.click(screen.getByRole("button", { name: "保存更改" }));
  await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
  expect(screen.getByText("保留编辑内容")).toBeInTheDocument();
});

it("does not let a canceled save close a newly opened project editor", async () => {
  const user = userEvent.setup(); let resolve!: (value: unknown) => void;
  mocks.updateProject.mockImplementationOnce(() => new Promise((done) => { resolve = done; }));
  render(<ProjectsPage />);
  const open = async () => { await user.click(await screen.findByRole("button", { name: "管理 Perovskite stability study" })); await user.click(screen.getByRole("menuitem", { name: "编辑项目信息" })); };
  await open();
  await user.clear(screen.getByLabelText("项目名称")); await user.type(screen.getByLabelText("项目名称"), "旧编辑");
  await user.click(screen.getByRole("button", { name: "保存更改" }));
  await user.click(screen.getByRole("button", { name: "取消" }));
  await user.click(screen.getByRole("button", { name: "重新读取项目列表" }));
  await waitFor(() => expect(screen.queryByText(/保存项目的结果尚未确认/)).not.toBeInTheDocument());
  await open(); await user.clear(screen.getByLabelText("项目名称")); await user.type(screen.getByLabelText("项目名称"), "新的草稿");
  await act(async () => resolve({ id: "project_1", projectId: "project_1", name: "旧编辑", description: "材料稳定性研究", status: "active", role: "owner" }));
  expect(screen.getByRole("dialog", { name: "编辑项目信息" })).toBeInTheDocument();
  expect(screen.getByLabelText("项目名称")).toHaveValue("新的草稿");
});

it("edits bounded project organization tags without changing scientific scope", async () => {
  const user = userEvent.setup();
  mocks.listProjects.mockResolvedValue([
    {
      id: "tagged_project",
      name: "Tagged project",
      role: "owner",
      status: "active",
      description: "结构研究",
      tags: ["结构"],
    },
  ]);
  render(<ProjectsPage />);

  await user.click(await screen.findByRole("button", { name: "管理 Tagged project" }));
  await user.click(screen.getByRole("menuitem", { name: "编辑项目信息" }));
  const tags = screen.getByLabelText(/组织标签/);
  await user.clear(tags);
  await user.type(tags, "结构, XRD, 待复核");
  await user.click(screen.getByRole("button", { name: "保存更改" }));
  await waitFor(() =>
    expect(mocks.updateProject).toHaveBeenCalledWith("tagged_project", {
      name: "Tagged project",
      description: "结构研究",
      tags: ["结构", "XRD", "待复核"],
    }, expect.any(AbortSignal)),
  );
  expect(
    within(screen.getByText("Tagged project").closest(".managed-object-row")!)
      .getByText(/结构 · XRD · 待复核/),
  ).toBeInTheDocument();
});

it("filters the project catalog by non-scientific organization tag", async () => {
  const user = userEvent.setup();
  mocks.listProjects.mockResolvedValue([
    {
      id: "tagged_structure",
      name: "Structure review",
      role: "owner",
      status: "active",
      description: "结构研究",
      tags: ["结构", "待复核"],
    },
    {
      id: "tagged_xrd",
      name: "XRD review",
      role: "owner",
      status: "active",
      description: "衍射研究",
      tags: ["XRD"],
    },
  ]);
  render(<ProjectsPage />);

  const selector = await screen.findByLabelText("标签");
  await user.selectOptions(selector, "XRD");
  expect(screen.getByText("XRD review")).toBeInTheDocument();
  expect(screen.queryByText("Structure review")).not.toBeInTheDocument();
  expect(screen.getByRole("status")).toHaveTextContent("1 个项目");
});

it("keeps shared viewer projects navigable without project mutation affordances", async () => {
  mocks.listProjects.mockResolvedValue([
    { id: "shared_1", name: "共享结构研究", role: "viewer", status: "active", description: "只读项目" },
  ]);
  render(<ProjectsPage />);

  const trigger = await screen.findByRole("button", { name: "管理 共享结构研究" });
  fireEvent.click(trigger);
  expect(screen.getByRole("menuitem", { name: "查看数据" })).toBeInTheDocument();
  expect(screen.getByRole("menuitem", { name: "研究记录" })).toBeInTheDocument();
  expect(screen.queryByRole("menuitem", { name: "上传数据" })).not.toBeInTheDocument();
  expect(screen.queryByRole("menuitem", { name: "编辑项目信息" })).not.toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "选择" })).not.toBeInTheDocument();
});

it.each(["admin", "researcher"] as const)(
  "keeps %s project actions write-capable without owner-only purge authority",
  async (role) => {
    mocks.listProjects.mockResolvedValue([
      {
        id: `shared_${role}`,
        name: `${role} 协作项目`,
        role,
        status: "active",
      },
    ]);
    render(<ProjectsPage />);

    await userEvent.click(
      await screen.findByRole("button", {
        name: `管理 ${role} 协作项目`,
      }),
    );
    expect(screen.getByRole("menuitem", { name: "上传数据" })).toBeInTheDocument();
    expect(screen.getByRole("menuitem", { name: "编辑项目信息" })).toBeInTheDocument();
    expect(screen.getByRole("menuitem", { name: "归档项目" })).toBeInTheDocument();
    expect(screen.getByRole("menuitem", { name: "导出项目清单" })).toBeInTheDocument();
    expect(screen.queryByRole("menuitem", { name: "移入回收站" })).not.toBeInTheDocument();
    expect(screen.queryByRole("menuitem", { name: "永久删除空项目" })).not.toBeInTheDocument();
  },
);

it("exposes the read-only provenance export to shared viewer members", async () => {
  const user = userEvent.setup();
  const createObjectURL = vi.fn(() => "blob:viewer-project-manifest");
  const revokeObjectURL = vi.fn();
  vi.stubGlobal("URL", { createObjectURL, revokeObjectURL });
  const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
  mocks.listProjects.mockResolvedValue([
    { id: "shared_viewer", name: "共享只读项目", role: "viewer", status: "active" },
  ]);
  const exportFixture = await mocks.getProjectExportManifest();
  mocks.getProjectExportManifest.mockResolvedValue({ ...exportFixture, project: { ...exportFixture.project, id: "shared_viewer" } });
  mocks.getProjectExportManifest.mockClear();
  render(<ProjectsPage />);

  const row = (await screen.findByText("共享只读项目")).closest(".managed-object-row")!;
  fireEvent.contextMenu(row);
  expect(screen.getByRole("menuitem", { name: "导出项目清单" })).toBeInTheDocument();
  expect(screen.queryByRole("menuitem", { name: "编辑项目信息" })).not.toBeInTheDocument();
  await user.click(screen.getByRole("menuitem", { name: "导出项目清单" }));

  await waitFor(() => expect(mocks.getProjectExportManifest).toHaveBeenCalledWith("shared_viewer", expect.any(AbortSignal)));
  expect(click).toHaveBeenCalled();
  expect(screen.getByText(/已导出“共享只读项目”/)).toBeInTheDocument();
  vi.unstubAllGlobals();
  click.mockRestore();
});

it("manages datasets from the Data Navigator without permanent per-row buttons", async () => {
  const user = userEvent.setup();
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [{ datasetId: "dataset_1", name: "materials-table", status: "profile_ready", import: { fileCount: 1, resources: [] }, profile: { rowCount: 3, semanticRoles: {} } }],
    analyses: [],
  });
  render(<ProjectDataPage projectId="project_1" />);

  const datasetTitle = await screen.findByText("materials-table");
  expect(mocks.listScientificObjects).toHaveBeenCalledWith("project_1", expect.anything(), "ACTIVE", undefined);
  fireEvent.contextMenu(datasetTitle.closest(".managed-object-row")!);
  expect(screen.getByRole("menuitem", { name: "重命名数据集" })).toBeInTheDocument();
  await user.keyboard("{Escape}");

  await user.click(screen.getByRole("button", { name: "选择多个数据或科研对象" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 materials-table" }));
  await user.click(screen.getByRole("button", { name: "归档" }));
  await waitFor(() => expect(mocks.bulkDatasetAction).toHaveBeenCalledWith(["dataset_1"], "archive", expect.any(AbortSignal)));
  await user.click(screen.getByRole("button", { name: "已归档" }));
  await waitFor(() => expect(mocks.listScientificObjects).toHaveBeenLastCalledWith("project_1", expect.anything(), "ARCHIVED", undefined));
});

it("moves a dataset to trash and restores it without exposing new research actions", async () => {
  const user = userEvent.setup();
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [{ datasetId: "dataset_1", name: "recoverable-data", status: "profile_ready", import: { fileCount: 1, resources: [] }, profile: { rowCount: 3, semanticRoles: {} } }],
    analyses: [],
  });
  mocks.getDatasetDependencyImpact.mockResolvedValue({
    entity: "dataset",
    entityId: "dataset_1",
    displayName: "recoverable-data",
    canDelete: false,
    dependencyCount: 1,
    dependencies: [{ kind: "scientific_results", label: "科学结果", count: 1 }],
    impact: { removedFromActiveDiscovery: true, historicalProvenanceProtected: true, historicalResearchRemainsAccessible: true },
  });
  mocks.updateDataset
    .mockResolvedValueOnce({ id: "dataset_1", datasetId: "dataset_1", projectId: "project_1", name: "recoverable-data", status: "trashed" })
    .mockResolvedValueOnce({ id: "dataset_1", datasetId: "dataset_1", projectId: "project_1", name: "recoverable-data", status: "profile_ready" });
  render(<ProjectDataPage projectId="project_1" />);

  await user.click(await screen.findByRole("button", { name: "管理 recoverable-data" }));
  await user.click(screen.getByRole("menuitem", { name: "移入回收站" }));
  expect(await screen.findByRole("dialog", { name: "将数据集移入回收站" })).toHaveTextContent("科学结果：1");
  await user.click(screen.getByRole("button", { name: "移入回收站" }));
  await waitFor(() =>
    expect(mocks.updateDataset).toHaveBeenCalledWith("dataset_1", {
      lifecycle: "TRASHED",
    }, expect.any(AbortSignal)),
  );

  await user.click(screen.getByRole("button", { name: "回收站" }));
  expect((await screen.findAllByText("recoverable-data")).length).toBeGreaterThan(0);
  expect(screen.queryByRole("link", { name: "研究此数据" })).not.toBeInTheDocument();
  expect(screen.queryByRole("link", { name: "上传数据" })).not.toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "管理 recoverable-data" }));
  await user.click(screen.getByRole("menuitem", { name: "从回收站恢复" }));
  await waitFor(() =>
    expect(mocks.updateDataset).toHaveBeenLastCalledWith("dataset_1", {
      archived: false,
    }, expect.any(AbortSignal)),
  );
});

it("resumes project history with the authoritative ResearchTurn identity", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [],
    analyses: [{
      jobId: "job_nonstandard_history",
      researchSessionId: "session_1",
      researchTurnId: "turn-123",
      status: "succeeded",
      userQuestion: "比较两个结构",
      toolIds: [],
      stepCount: 2,
      artifactCount: 1,
      artifactTypes: ["table_json"],
      interpretationCount: 1,
      reportCount: 1,
      recipeCount: 0,
    }],
  });
  render(<ProjectOverviewPage projectId="project_1" />);
  const link = await screen.findByRole("link", { name: /比较两个结构/ });
  expect(link).toHaveAttribute("href", "/projects/project_1/research/session_1?run=job_nonstandard_history&turn=turn-123");
});

it("shows the authoritative ResearchTurn terminal status instead of a stale Job status", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [],
    analyses: [{
      jobId: "job_stale_running",
      researchSessionId: "session_1",
      researchTurnId: "turn-failed",
      researchTurnStatus: "FAILED",
      status: "running",
      userQuestion: "比较两个结构",
      toolIds: [],
      stepCount: 2,
      artifactCount: 0,
      artifactTypes: [],
      interpretationCount: 0,
      reportCount: 0,
      recipeCount: 0,
    }],
  });

  render(<ProjectOverviewPage projectId="project_1" />);

  expect(await screen.findByText("分析失败")).toBeInTheDocument();
  expect(screen.queryByText("分析进行中")).not.toBeInTheDocument();
});

it("keeps only current datasets in overview while retaining historical research sources", async () => {
  const history = await mocks.getProjectHistory();
  const source = history.datasets[0];
  mocks.getProjectHistory.mockResolvedValue({ ...history, datasets: [
    { ...source, datasetId: "archived", name: "已归档的实验数据", status: "archived" },
    { ...source, datasetId: "trashed", name: "回收站数据", status: "trashed" },
    { ...source, name: "当前实验数据", profile: { rowCount: 0 } },
  ], analyses: [{ jobId: "old-job", datasetId: "archived", status: "succeeded", toolIds: [], userQuestion: "原来的实验结果" }] });
  render(<ProjectOverviewPage projectId="project_1" />);
  await screen.findByRole("heading", { name: "项目概览" });
  const current = screen.getByRole("heading", { name: "当前数据" }).closest("section")!;
  expect(within(current).getByRole("link", { name: /当前实验数据.*0 行/ })).toHaveAttribute("href", "/projects/project_1/data?dataset=dataset_1");
  expect(within(current).queryByText("已归档的实验数据")).not.toBeInTheDocument();
  expect(screen.queryByText("回收站数据")).not.toBeInTheDocument();
  expect(screen.getByRole("link", { name: /原来的实验结果.*已归档的实验数据/ })).toHaveAttribute("href", "/projects/project_1/research?run=old-job");
});

it("distinguishes and orders overview runs by their saved question, source and creation time", async () => {
  const history = await mocks.getProjectHistory();
  const run = { datasetId: "dataset_1", status: "succeeded", toolIds: ["table.histogram"] };
  mocks.getProjectHistory.mockResolvedValue({ ...history, analyses: [
    { ...run, jobId: "older", userQuestion: "比较高温样品", createdAt: "2026-09-01T08:00:00Z" },
    { ...run, jobId: "newer", userQuestion: "比较低温样品", createdAt: "2026-09-02T08:00:00Z" },
    { ...run, jobId: "missing-date", createdAt: "not-a-date" },
  ] });
  render(<ProjectOverviewPage projectId="project_1" />);
  const section = (await screen.findByRole("heading", { name: "最近研究" })).closest("section")!;
  const rows = [...section.querySelectorAll(".overview-row")];
  expect(rows.map((row) => row.getAttribute("href"))).toEqual(["/projects/project_1/research?run=newer", "/projects/project_1/research?run=older", "/projects/project_1/research?run=missing-date"]);
  expect(rows[0]).toHaveTextContent("比较低温样品");
  expect(rows[0]).toHaveTextContent("materials-table");
  expect(rows[0].querySelector("time")).toHaveAttribute("datetime", "2026-09-02T08:00:00.000Z");
  expect(rows[2]).toHaveTextContent("材料属性分布");
  expect(rows[2].querySelector("time")).toBeNull();
});

it("shows all sources of a joint overview run and does not turn an unverified source into the routing dataset", async () => {
  const history = await mocks.getProjectHistory();
  const sources = ["Si", "Cu", "NaCl"].map((name, index) => ({ ...history.datasets[0], datasetId: `material-${index}`, name: `${name} 晶体` }));
  const run = { datasetId: sources[0].datasetId, status: "succeeded", toolIds: ["structure.rdf"] };
  mocks.getProjectHistory.mockResolvedValue({ ...history, datasets: sources, analyses: [
    { ...run, jobId: "joint", userQuestion: "比较三个材料", sourceDatasetIds: sources.map((source) => source.datasetId) },
    { ...run, jobId: "unverified", userQuestion: "历史研究", sourceDatasetIds: [] },
  ] });
  render(<ProjectOverviewPage projectId="project_1" />);
  const section = (await screen.findByRole("heading", { name: "最近研究" })).closest("section")!;
  const joint = within(section).getByRole("link", { name: /比较三个材料/ });
  expect(within(joint).getAllByRole("listitem").map((item) => item.textContent)).toEqual(["Si 晶体", "Cu 晶体", "NaCl 晶体"]);
  const unverified = within(section).getByRole("link", { name: /历史研究/ });
  expect(unverified).toHaveTextContent("来源待核实");
  expect(unverified).not.toHaveTextContent("Si 晶体");
});

it("discloses long project descriptions and keeps the overview read-only for viewers", async () => {
  const history = await mocks.getProjectHistory();
  const description = "比较不同温度下材料的稳定性，保留原始实验条件。".repeat(12);
  mocks.getProjectHistory.mockResolvedValue({ ...history, project: { ...history.project, description, role: "viewer" }, datasets: [] });
  render(<ProjectOverviewPage projectId="project_1" />);
  await screen.findByRole("heading", { name: "项目概览" });
  expect(screen.queryByRole("heading", { name: "研究项目" })).not.toBeInTheDocument();
  expect(screen.getByText(description)).not.toBeVisible();
  await userEvent.setup().click(screen.getByText("项目说明"));
  expect(screen.getByText(description)).toBeVisible();
  expect(screen.queryByRole("link", { name: "上传数据 →" })).not.toBeInTheDocument();
  expect(screen.getByRole("link", { name: "查看研究记录" })).toHaveAttribute("href", "/projects/project_1/research");
});

it("does not expose dataset mutation controls to a viewer project member", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "共享研究项目", role: "viewer" },
    datasets: [{ datasetId: "dataset_1", name: "shared-materials", status: "profile_ready", import: { fileCount: 1, resources: [] }, profile: { rowCount: 3, semanticRoles: {} } }],
    analyses: [],
  });
  render(<ProjectDataPage projectId="project_1" />);

  expect((await screen.findAllByText("shared-materials")).length).toBeGreaterThan(0);
  expect(screen.queryByRole("button", { name: "选择多个数据或科研对象" })).not.toBeInTheDocument();
  fireEvent.contextMenu(screen.getAllByText("shared-materials")[0].closest(".managed-object-row")!);
  expect(screen.getByRole("menuitem", { name: "查看研究记录" })).toBeInTheDocument();
  expect(screen.queryByRole("menuitem", { name: "重命名数据集" })).not.toBeInTheDocument();
  expect(screen.queryByRole("menuitem", { name: "归档数据集" })).not.toBeInTheDocument();
  expect(screen.queryByRole("menuitem", { name: "删除空数据集" })).not.toBeInTheDocument();
  expect(screen.queryByRole("link", { name: "上传数据" })).not.toBeInTheDocument();
});

it("resolves an explicitly addressed historical version even when absent from the active directory", async () => {
  mocks.listScientificObjects.mockResolvedValue({ items: [], next_cursor: null });
  render(<ProjectDataPage projectId="project_1" initialObjectId="object_1" initialObjectVersionId="version_1" />);

  expect(await screen.findByTestId("scientific-object-viewer")).toBeInTheDocument();
  expect(mocks.listScientificObjects).toHaveBeenCalledWith("project_1", expect.anything(), "ACTIVE", undefined);
  expect(screen.getByTestId("scientific-object-viewer")).toHaveAttribute("data-version", "version_1");
});

it("retains the explicitly addressed object during directory failure and retry", async () => {
  const user = userEvent.setup();
  mocks.listScientificObjects.mockRejectedValueOnce(new Error("directory internal detail"));
  render(<ProjectDataPage projectId="project_1" initialObjectId="object_1" initialObjectVersionId="version_1" />);
  const viewer = await screen.findByTestId("scientific-object-viewer");
  expect(viewer).toHaveAttribute("data-object", "object_1");
  expect(viewer).toHaveAttribute("data-version", "version_1");
  expect(viewer).toHaveAttribute("data-can-manage", "true");
  expect(viewer).toHaveAttribute("data-can-research", "true");
  expect(screen.queryByTestId("quick-preview-scientific-viewer")).not.toBeInTheDocument();
  expect(await screen.findByRole("alert")).toHaveTextContent("科研对象目录暂时无法读取");
  await user.click(screen.getByRole("button", { name: "重新加载科研对象" }));
  await waitFor(() => expect(screen.queryByRole("alert")).not.toBeInTheDocument());
  expect(screen.getByTestId("scientific-object-viewer")).toBe(viewer);
});

it("fails closed when an object route omits the immutable version", async () => {
  mocks.listScientificObjects.mockResolvedValue({
    items: [{
      id: "object_1",
      project_id: "project_1",
      kind: "STRUCTURE",
      object_type: "structure.crystal",
      display_name: "Silicon",
      lifecycle_status: "ACTIVE",
      current_version_id: "version_1",
    }],
    next_cursor: null,
  });

  render(<ProjectDataPage projectId="project_1" initialObjectId="object_1" />);

  const state = await screen.findByRole("alert");
  expect(state).toHaveTextContent("这个链接缺少数据版本");
  expect(screen.queryByTestId("scientific-object-viewer")).not.toBeInTheDocument();
  await userEvent.setup().click(screen.getByRole("button", { name: "选择数据版本" }));
  const versionLink = screen.getByRole("link", { name: /Silicon/ });
  expect(versionLink).toHaveAttribute("href", "/projects/project_1/data?object=object_1&version=version_1");
  await waitFor(() => expect(versionLink).toHaveFocus());
  expect(screen.queryByTestId("scientific-object-viewer")).not.toBeInTheDocument();
});

it("exposes archive and restore actions for scientific objects through the existing lifecycle API", async () => {
  const user = userEvent.setup();
  mocks.listScientificObjects
    .mockResolvedValueOnce({
      items: [{ id: "object_1", project_id: "project_1", kind: "STRUCTURE", object_type: "structure.crystal", display_name: "Silicon", lifecycle_status: "ACTIVE", current_version_id: "version_1" }],
      next_cursor: null,
    })
    .mockResolvedValue({ items: [], next_cursor: null });
  render(<ProjectDataPage projectId="project_1" />);

  await user.click(await screen.findByRole("button", { name: "数据视图" }));
  const title = await screen.findByText("Silicon");
  await user.click(screen.getByRole("button", { name: "管理 Silicon" }));
  await user.click(screen.getByRole("menuitem", { name: "归档科研对象" }));
  await waitFor(() => expect(mocks.updateScientificObject).toHaveBeenCalledWith("object_1", { lifecycle: "ARCHIVED" }, expect.any(AbortSignal)));
  expect(screen.queryByText("Silicon")).not.toBeInTheDocument();
});

it("bulk archives selected scientific objects without mutating their versions", async () => {
  const user = userEvent.setup();
  mocks.listScientificObjects.mockResolvedValue({
    items: [
      { id: "object_1", project_id: "project_1", kind: "STRUCTURE", object_type: "structure.crystal", display_name: "Silicon", lifecycle_status: "ACTIVE", current_version_id: "version_1" },
      { id: "object_2", project_id: "project_1", kind: "TABLE", object_type: "materials.table", display_name: "Materials", lifecycle_status: "ACTIVE", current_version_id: "version_2" },
    ],
    next_cursor: null,
  });
  render(<ProjectDataPage projectId="project_1" />);

  await user.click(await screen.findByRole("button", { name: "数据视图" }));
  await screen.findByText("Silicon");
  await user.click(screen.getByRole("button", { name: "选择多个数据或科研对象" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 Silicon" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 Materials" }));
  await user.click(screen.getByRole("button", { name: "归档科研对象" }));

  await waitFor(() =>
    expect(mocks.bulkUpdateScientificObjects).toHaveBeenCalledWith(
      "project_1",
      ["object_1", "object_2"],
      "ARCHIVED",
      expect.any(AbortSignal),
    ),
  );
  expect(screen.queryByText("Silicon")).not.toBeInTheDocument();
  expect(screen.queryByText("Materials")).not.toBeInTheDocument();
});

it("previews dependencies before bulk-moving scientific objects to Trash", async () => {
  const user = userEvent.setup();
  mocks.listScientificObjects.mockResolvedValue({
    items: [
      { id: "object_1", project_id: "project_1", kind: "STRUCTURE", object_type: "structure.crystal", display_name: "Silicon", lifecycle_status: "ACTIVE", current_version_id: "version_1" },
      { id: "object_2", project_id: "project_1", kind: "TABLE", object_type: "materials.table", display_name: "Materials", lifecycle_status: "ACTIVE", current_version_id: "version_2" },
    ],
    next_cursor: null,
  });
  mocks.getScientificObjectDependencyImpact
    .mockResolvedValueOnce({
      entity: "scientific_object",
      entityId: "object_1",
      displayName: "Silicon",
      canDelete: false,
      dependencyCount: 2,
      dependencies: [
        { kind: "scientific_result_snapshots", label: "ScientificResult", count: 1 },
      ],
      impact: { removedFromActiveDiscovery: true, historicalProvenanceProtected: true, historicalResearchRemainsAccessible: true, scientificSnapshotMutated: false },
    })
    .mockResolvedValueOnce({
      entity: "scientific_object",
      entityId: "object_2",
      displayName: "Materials",
      canDelete: false,
      dependencyCount: 1,
      dependencies: [
        { kind: "artifacts", label: "Artifact", count: 1 },
      ],
      impact: { removedFromActiveDiscovery: true, historicalProvenanceProtected: true, historicalResearchRemainsAccessible: true, scientificSnapshotMutated: false },
    });
  render(<ProjectDataPage projectId="project_1" />);

  await user.click(await screen.findByRole("button", { name: "数据视图" }));
  await screen.findByText("Silicon");
  await user.click(screen.getByRole("button", { name: "选择多个数据或科研对象" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 Silicon" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 Materials" }));
  const objectBatchActions = within(
    screen.getByRole("region", { name: "批量科研对象操作" }),
  );
  await user.click(objectBatchActions.getByRole("button", { name: "移入回收站" }));

  const dialog = await screen.findByRole("dialog", { name: "将 2 个科研对象移入回收站" });
  expect(await within(dialog).findByText("依赖影响汇总")).toBeInTheDocument();
  expect(within(dialog).getByText("ScientificResult：1")).toBeInTheDocument();
  expect(within(dialog).getByText("Artifact：1")).toBeInTheDocument();
  expect(mocks.bulkUpdateScientificObjects).not.toHaveBeenCalled();

  await user.click(within(dialog).getByRole("button", { name: "确认移入回收站" }));
  await waitFor(() =>
    expect(mocks.bulkUpdateScientificObjects).toHaveBeenCalledWith(
      "project_1",
      ["object_1", "object_2"],
      "TRASHED",
      expect.any(AbortSignal),
    ),
  );
});

it("previews dependencies before bulk-moving datasets to Trash", async () => {
  const user = userEvent.setup();
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [
      { datasetId: "dataset_1", name: "materials-table", import: { fileCount: 1, resources: [] }, profile: { rowCount: 3, semanticRoles: {} }, status: "profile_ready" },
      { datasetId: "dataset_2", name: "structure-table", import: { fileCount: 1, resources: [] }, profile: { rowCount: 2, semanticRoles: {} }, status: "profile_ready" },
    ],
    analyses: [],
  });
  mocks.getDatasetDependencyImpact
    .mockResolvedValueOnce({
      entity: "dataset",
      entityId: "dataset_1",
      displayName: "materials-table",
      canDelete: false,
      dependencyCount: 2,
      dependencies: [{ kind: "scientific_objects", label: "科研对象", count: 1 }],
      impact: { removedFromActiveDiscovery: true, historicalProvenanceProtected: true, historicalResearchRemainsAccessible: true, scientificSnapshotMutated: false },
    })
    .mockResolvedValueOnce({
      entity: "dataset",
      entityId: "dataset_2",
      displayName: "structure-table",
      canDelete: false,
      dependencyCount: 1,
      dependencies: [{ kind: "scientific_result_snapshots", label: "ScientificResult", count: 1 }],
      impact: { removedFromActiveDiscovery: true, historicalProvenanceProtected: true, historicalResearchRemainsAccessible: true, scientificSnapshotMutated: false },
    });
  render(<ProjectDataPage projectId="project_1" />);

  await screen.findByText("materials-table");
  await user.click(screen.getByRole("button", { name: "选择多个数据或科研对象" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 materials-table" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 structure-table" }));
  const datasetBatchActions = within(
    screen.getByRole("region", { name: "批量数据操作" }),
  );
  await user.click(datasetBatchActions.getByRole("button", { name: "移入回收站" }));

  const dialog = await screen.findByRole("dialog", { name: "将 2 个数据集移入回收站" });
  expect(await within(dialog).findByText("依赖影响汇总")).toBeInTheDocument();
  expect(within(dialog).getByText("科研对象：1")).toBeInTheDocument();
  expect(within(dialog).getByText("ScientificResult：1")).toBeInTheDocument();
  expect(mocks.bulkDatasetAction).not.toHaveBeenCalled();

  await user.click(within(dialog).getByRole("button", { name: "确认移入回收站" }));
  await waitFor(() =>
    expect(mocks.bulkDatasetAction).toHaveBeenCalledWith(
      ["dataset_1", "dataset_2"],
      "trash",
      expect.any(AbortSignal),
    ),
  );
});

it("keeps the Dataset Trash preview open when the batch mutation fails", async () => {
  const user = userEvent.setup();
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "研究项目", role: "owner" },
    datasets: [
      { datasetId: "dataset_1", name: "materials-table", import: { fileCount: 1, resources: [] }, profile: { rowCount: 3, semanticRoles: {} }, status: "profile_ready" },
    ],
    analyses: [],
  });
  mocks.getDatasetDependencyImpact.mockResolvedValue({
    entity: "dataset",
    entityId: "dataset_1",
    displayName: "materials-table",
    canDelete: false,
    dependencyCount: 1,
    dependencies: [{ kind: "scientific_result_snapshots", label: "ScientificResult", count: 1 }],
    impact: { removedFromActiveDiscovery: true, historicalProvenanceProtected: true, historicalResearchRemainsAccessible: true, scientificSnapshotMutated: false },
  });
  mocks.bulkDatasetAction.mockRejectedValueOnce(new Error("批量操作服务暂时不可用"));
  render(<ProjectDataPage projectId="project_1" />);

  await screen.findByText("materials-table");
  await user.click(screen.getByRole("button", { name: "选择多个数据或科研对象" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 materials-table" }));
  await user.click(
    within(screen.getByRole("region", { name: "批量数据操作" })).getByRole(
      "button",
      { name: "移入回收站" },
    ),
  );
  const dialog = await screen.findByRole("dialog", { name: "将 1 个数据集移入回收站" });
  await user.click(within(dialog).getByRole("button", { name: "确认移入回收站" }));

  expect(await within(dialog).findByText("批量更新数据集的结果尚未确认，请重新读取数据列表后再操作。")).toBeInTheDocument();
  expect(screen.getByRole("dialog", { name: "将 1 个数据集移入回收站" })).toBeInTheDocument();
});

it("retains a dataset rename draft through failed reconciliation and uses the exact refreshed dataset", async () => {
  const user = userEvent.setup();
  mocks.updateDataset.mockRejectedValueOnce(new Error("response lost"));
  render(<ProjectDataPage projectId="project_1" />);
  await user.click(await screen.findByRole("button", { name: "管理 materials-table" }));
  await user.click(screen.getByRole("menuitem", { name: "重命名数据集" }));
  const field = screen.getByRole("textbox", { name: "数据集名称" });
  await user.clear(field); await user.type(field, "保留的重命名草稿");
  await user.click(screen.getByRole("button", { name: "保存更改" }));
  const reread = await screen.findByRole("button", { name: "重新读取数据列表" });
  expect(screen.getByRole("button", { name: "保存更改" })).toBeDisabled();
  mocks.getProjectHistory.mockRejectedValueOnce(new Error("offline"));
  await user.click(reread); await screen.findByText("暂时无法读取数据列表，当前内容已保留。请重试。");
  expect(field).toHaveValue("保留的重命名草稿");
  await user.click(reread); await waitFor(() => expect(screen.getByRole("button", { name: "保存更改" })).toBeEnabled());
  expect(field).toHaveValue("保留的重命名草稿");
  mocks.updateDataset.mockResolvedValueOnce({ id: "dataset_1", datasetId: "dataset_1", projectId: "project_1", name: "保留的重命名草稿", status: "profile_ready" });
  await user.click(screen.getByRole("button", { name: "保存更改" }));
  await waitFor(() => expect(screen.queryByRole("dialog", { name: "重命名数据集" })).not.toBeInTheDocument());
  expect(mocks.updateDataset).toHaveBeenCalledTimes(2);
});

it("keeps a newly opened dataset editor intact when the previous canceled save resolves", async () => {
  const user = userEvent.setup(); let resolve!: (value: unknown) => void;
  mocks.updateDataset.mockImplementationOnce(() => new Promise((done) => { resolve = done; }));
  render(<ProjectDataPage projectId="project_1" />);
  const open = async () => { await user.click(await screen.findByRole("button", { name: "管理 materials-table" })); await user.click(screen.getByRole("menuitem", { name: "重命名数据集" })); };
  await open(); await user.click(screen.getByRole("button", { name: "保存更改" }));
  await waitFor(() => expect(mocks.updateDataset).toHaveBeenCalledOnce());
  await user.click(screen.getByRole("button", { name: "取消" })); await open();
  const field = screen.getByRole("textbox", { name: "数据集名称" }); await user.clear(field); await user.type(field, "新的编辑");
  await act(async () => resolve({ id: "dataset_1", datasetId: "dataset_1", projectId: "project_1", name: "materials-table", status: "profile_ready" }));
  expect(screen.getByRole("dialog", { name: "重命名数据集" })).toBeInTheDocument(); expect(field).toHaveValue("新的编辑");
  expect(screen.getByRole("button", { name: "保存更改" })).toBeDisabled();
});

it("removes restored scientific objects from the archived filtered view", async () => {
  const user = userEvent.setup();
  mocks.listScientificObjects.mockResolvedValue({
    items: [{ id: "object_1", project_id: "project_1", kind: "STRUCTURE", object_type: "structure.crystal", display_name: "Archived silicon", lifecycle_status: "ARCHIVED", current_version_id: "version_1" }],
    next_cursor: null,
  });
  render(<ProjectDataPage projectId="project_1" />);
  await user.click(await screen.findByRole("button", { name: "已归档" }));
  await user.click(await screen.findByRole("button", { name: "数据视图" }));
  await screen.findByText("Archived silicon");
  await user.click(screen.getByRole("button", { name: "管理 Archived silicon" }));
  await user.click(screen.getByRole("menuitem", { name: "恢复科研对象" }));
  await waitFor(() => expect(mocks.updateScientificObject).toHaveBeenCalledWith("object_1", { lifecycle: "ACTIVE" }, expect.any(AbortSignal)));
  expect(screen.queryByText("Archived silicon")).not.toBeInTheDocument();
});

it("lists scientific objects in the Trash filter and exposes a reversible restore action", async () => {
  const user = userEvent.setup();
  mocks.listScientificObjects.mockImplementation(async (_projectId: string, _signal: AbortSignal, lifecycle?: string) => ({
    items: lifecycle === "TRASHED"
      ? [{ id: "object_1", project_id: "project_1", kind: "STRUCTURE", object_type: "structure.crystal", display_name: "Trashed silicon", lifecycle_status: "TRASHED", current_version_id: "version_1" }]
      : [],
    next_cursor: null,
  }));
  render(<ProjectDataPage projectId="project_1" />);
  await user.click(await screen.findByRole("button", { name: "回收站" }));
  await user.click(await screen.findByRole("button", { name: "数据视图" }));
  await screen.findByText("Trashed silicon");
  expect(mocks.listScientificObjects).toHaveBeenLastCalledWith("project_1", expect.anything(), "TRASHED", undefined);
  await user.click(screen.getByRole("button", { name: "管理 Trashed silicon" }));
  await user.click(screen.getByRole("menuitem", { name: "恢复科研对象" }));
  await waitFor(() => expect(mocks.updateScientificObject).toHaveBeenCalledWith("object_1", { lifecycle: "ACTIVE" }, expect.any(AbortSignal)));
});

it("previews scientific object dependencies before moving it to Trash", async () => {
  const user = userEvent.setup();
  mocks.listScientificObjects.mockResolvedValue({
    items: [{ id: "object_1", project_id: "project_1", kind: "STRUCTURE", object_type: "structure.crystal", display_name: "Silicon", lifecycle_status: "ACTIVE", current_version_id: "version_1" }],
    next_cursor: null,
  });
  render(<ProjectDataPage projectId="project_1" />);
  await user.click(await screen.findByRole("button", { name: "数据视图" }));
  await screen.findByText("Silicon");
  await user.click(screen.getByRole("button", { name: "管理 Silicon" }));
  await user.click(screen.getByRole("menuitem", { name: "移入回收站" }));
  expect(await screen.findByText("依赖影响")).toBeInTheDocument();
  expect(mocks.getScientificObjectDependencyImpact).toHaveBeenCalledWith("object_1", expect.any(AbortSignal));
  expect(screen.getByText("ScientificResult：1")).toBeInTheDocument();
  expect(mocks.updateScientificObject).not.toHaveBeenCalled();
  await user.click(screen.getByRole("button", { name: "移入回收站" }));
  await waitFor(() => expect(mocks.updateScientificObject).toHaveBeenCalledWith("object_1", { lifecycle: "TRASHED" }, expect.any(AbortSignal)));
});

it.each(["project", "dataset", "object"] as const)("recovers a failed %s dependency preview before enabling its action", async (kind) => {
  const user = userEvent.setup();
  const read = kind === "project" ? mocks.getProjectDependencyImpact : kind === "dataset" ? mocks.getDatasetDependencyImpact : mocks.getScientificObjectDependencyImpact;
  read.mockRejectedValueOnce(new Error("private dependency failure"));
  if (kind === "object") mocks.listScientificObjects.mockResolvedValue({
    items: [{ id: "object_1", project_id: "project_1", kind: "STRUCTURE", object_type: "structure.crystal", display_name: "Silicon", lifecycle_status: "ACTIVE", current_version_id: "version_1" }],
    next_cursor: null,
  });
  render(kind === "project" ? <ProjectsPage /> : <ProjectDataPage projectId="project_1" />);
  const name = kind === "project" ? "Perovskite stability study" : kind === "dataset" ? "materials-table" : "Silicon";
  if (kind === "object") await user.click(await screen.findByRole("button", { name: "数据视图" }));
  await user.click(await screen.findByRole("button", { name: `管理 ${name}` }));
  await user.click(screen.getByRole("menuitem", { name: "移入回收站" }));
  const dialog = screen.getByRole("dialog");
  expect(await within(dialog).findByRole("alert")).toHaveTextContent("暂时无法读取");
  expect(within(dialog).getByRole("button", { name: "移入回收站" })).toBeDisabled();
  expect(dialog).not.toHaveTextContent("private dependency failure");
  await user.click(within(dialog).getByRole("button", { name: "重新检查依赖" }));
  await waitFor(() => expect(within(dialog).getByRole("button", { name: "移入回收站" })).toBeEnabled());
  expect(read).toHaveBeenCalledTimes(2);
  expect(mocks.updateProject).not.toHaveBeenCalled();
  expect(mocks.updateDataset).not.toHaveBeenCalled();
  expect(mocks.updateScientificObject).not.toHaveBeenCalled();
});

it("retains successful project dependency checks while retrying a failed sibling", async () => {
  const user = userEvent.setup();
  mocks.listProjects.mockResolvedValue([
    { id: "a", name: "Alpha", role: "owner", status: "active" },
    { id: "b", name: "Beta", role: "owner", status: "active" },
  ]);
  const saved = await mocks.getProjectDependencyImpact();
  mocks.getProjectDependencyImpact.mockClear().mockImplementation(async (id: string) => {
    if (id === "b") throw new Error("source unavailable");
    return { ...saved, dependencyCount: 7, dependencies: [{ kind: "results", label: "科学结果", count: 7 }] };
  });
  render(<ProjectsPage />);
  await user.click(await screen.findByRole("button", { name: "选择" }));
  await user.click(screen.getByRole("button", { name: "选择当前结果" }));
  await user.click(screen.getByRole("button", { name: "移入回收站" }));
  const dialog = screen.getByRole("dialog");
  await within(dialog).findByRole("alert");
  expect(dialog).toHaveTextContent("科学结果：7");
  expect(within(dialog).getByRole("button", { name: "确认移入回收站" })).toBeDisabled();
  mocks.getProjectDependencyImpact.mockResolvedValue(saved);
  await user.click(within(dialog).getByRole("button", { name: "重新检查依赖" }));
  await waitFor(() => expect(within(dialog).getByRole("button", { name: "确认移入回收站" })).toBeEnabled());
  expect(dialog).toHaveTextContent("科学结果：7");
  expect(mocks.getProjectDependencyImpact.mock.calls.map(([id]) => id)).toEqual(["a", "b", "b"]);
});

it.each(["project", "dataset"] as const)("blocks permanent %s deletion on a failed or server-denied dependency preview, including Enter", async (kind) => {
  const user = userEvent.setup();
  const read = kind === "project" ? mocks.getProjectDependencyImpact : mocks.getDatasetDependencyImpact;
  const saved = await read();
  read.mockClear().mockRejectedValueOnce(new Error("failed preview")).mockResolvedValue({ ...saved, canDelete: false });
  if (kind === "project") mocks.listProjects.mockResolvedValue([{ id: "project_1", name: "Protected", role: "owner", status: "trashed" }]);
  else {
    const history = await mocks.getProjectHistory();
    history.datasets[0].status = "trashed";
    history.datasets[0].name = "Protected";
  }
  render(kind === "project" ? <ProjectsPage /> : <ProjectDataPage projectId="project_1" />);
  await user.click(await screen.findByRole("button", { name: "回收站" }));
  await user.click(await screen.findByRole("button", { name: "管理 Protected" }));
  await user.click(screen.getByRole("menuitem", { name: kind === "project" ? "永久删除空项目" : "永久删除空数据集" }));
  const dialog = screen.getByRole("dialog");
  await within(dialog).findByRole("alert");
  await user.type(within(dialog).getByRole("textbox"), "Protected{Enter}");
  expect(within(dialog).getByRole("button", { name: "永久删除" })).toBeDisabled();
  await user.click(within(dialog).getByRole("button", { name: "重新检查依赖" }));
  await waitFor(() => expect(within(dialog).queryByRole("alert")).toBeNull());
  expect(within(dialog).getByRole("button", { name: "永久删除" })).toBeDisabled();
  await user.click(within(dialog).getByRole("textbox"));
  await user.keyboard("{Enter}");
  expect(mocks.deleteEmptyProject).not.toHaveBeenCalled();
  expect(mocks.deleteEmptyDataset).not.toHaveBeenCalled();
});

it("keeps scientific object lifecycle mutation unavailable to read-only members", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "共享研究项目", role: "viewer" },
    datasets: [],
    analyses: [],
  });
  mocks.listScientificObjects.mockResolvedValue({
    items: [{ id: "object_1", project_id: "project_1", kind: "STRUCTURE", object_type: "structure.crystal", display_name: "Shared silicon", lifecycle_status: "ACTIVE", current_version_id: "version_1" }],
    next_cursor: null,
  });
  render(<ProjectDataPage projectId="project_1" />);
  await userEvent.click(await screen.findByRole("button", { name: "数据视图" }));
  await screen.findByText("Shared silicon");
  await userEvent.click(screen.getByRole("button", { name: "管理 Shared silicon" }));
  expect(screen.getByRole("menuitem", { name: "查看研究记录" })).toBeInTheDocument();
  expect(screen.queryByRole("menuitem", { name: "归档科研对象" })).not.toBeInTheDocument();
  expect(mocks.updateScientificObject).not.toHaveBeenCalled();
});

it.each([{ name: "Console", Page: ConsolePage }, { name: "Projects", Page: ProjectsPage }])("bounds a stalled $name directory and rejects its late result", async ({ Page }) => {
  let resolveOld!: (items: unknown) => void;
  mocks.listProjects.mockReturnValueOnce(new Promise((resolve) => { resolveOld = resolve; }));
  vi.useFakeTimers();
  try {
    render(<Page />);
    await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
    expect(screen.getByRole("alert")).toHaveTextContent("项目列表读取超时");
    expect(mocks.listProjects.mock.calls[0][0].signal.aborted).toBe(true);
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新加载项目数据" })); });
    expect(screen.getAllByText("Perovskite stability study").length).toBeGreaterThan(0);
    await act(async () => { resolveOld([{ id: "wrong", name: "迟到的旧项目" }]); });
    expect(screen.queryByText("迟到的旧项目")).not.toBeInTheDocument();
  } finally { vi.useRealTimers(); }
});

it("bounds quick-preview source reads, preserves the project link and ignores late sources", async () => {
  const user = userEvent.setup();
  let resolveOld!: (items: unknown) => void;
  mocks.getDatasetSourceResources.mockReturnValueOnce(new Promise((resolve) => { resolveOld = resolve; }));
  render(<ConsolePage />); const trigger = await screen.findByRole("button", { name: "快速查看" });
  vi.useFakeTimers();
  try {
    await act(async () => { fireEvent.click(trigger); });
    expect(screen.getByRole("button", { name: "关闭快速查看" })).toHaveFocus();
    await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
    expect(screen.getByRole("alert")).toHaveTextContent("暂时无法加载数据");
    expect(screen.getByRole("link", { name: "打开项目数据" })).toHaveAttribute("href", "/projects/project_1/data?dataset=dataset_1");
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重新加载数据" })); });
    expect(screen.getByTestId("quick-preview-scientific-viewer")).toHaveTextContent("DataFrame");
    await act(async () => resolveOld([{ objectId: "late", datasetId: "dataset_1", objectType: "LateSource", payload: [] }]));
    expect(screen.getByTestId("quick-preview-scientific-viewer")).not.toHaveTextContent("LateSource");
  } finally { vi.useRealTimers(); }
  await user.keyboard("{Escape}"); await waitFor(() => expect(trigger).toHaveFocus());
});

it("rejects quick-preview history from a different project before reading sources", async () => {
  const user = userEvent.setup();
  mocks.getProjectHistory.mockResolvedValue({ project: { id: "foreign" }, datasets: [{ datasetId: "foreign-dataset" }], analyses: [] });
  render(<ConsolePage />); await user.click(await screen.findByRole("button", { name: "快速查看" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("暂时无法加载数据");
  expect(mocks.getDatasetSourceResources).not.toHaveBeenCalled();
  expect(screen.queryByTestId("quick-preview-scientific-viewer")).not.toBeInTheDocument();
});

it("rejects quick-preview resources from a different dataset", async () => {
  const user = userEvent.setup();
  mocks.getDatasetSourceResources.mockResolvedValueOnce([{ objectId: "foreign", datasetId: "wrong-dataset", objectType: "DataFrame", payload: [] }]);
  render(<ConsolePage />); await user.click(await screen.findByRole("button", { name: "快速查看" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("暂时无法加载数据");
  expect(screen.queryByTestId("quick-preview-scientific-viewer")).not.toBeInTheDocument();
});

it("keeps the preview dataset and validated sample in its data-page handoff", async () => {
  const user = userEvent.setup();
  const selection = validateWorkspaceSelectionContext({
    schemaVersion: "1.0", sourceScopeHash: "a".repeat(64),
    primary: { selectionSchemaVersion: "1.0", kind: "DATASET_SAMPLE", sourceScopeHash: "a".repeat(64), projectId: "project_1", datasetId: "dataset_1", datasetVersion: "v2", objectId: "object_1", sampleRef: "mat-2" },
    secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false,
  });
  mocks.sourceSelection = selection;
  render(<ConsolePage />); await user.click(await screen.findByRole("button", { name: "快速查看" }));
  await user.click(await screen.findByRole("button", { name: "选择第一条科学数据" }));
  const href = new URL(screen.getByRole("link", { name: "查看所选数据" }).getAttribute("href")!, "http://localhost");
  expect(href.searchParams.get("dataset")).toBe("dataset_1");
  expect(resolveDataPageSelection(href.searchParams.get("selection")!, "project_1", "dataset_1")).toEqual(selection);
  await user.click(screen.getByRole("button", { name: "取消选择" }));
  expect(screen.getByRole("link", { name: "打开项目数据" })).toHaveAttribute("href", "/projects/project_1/data?dataset=dataset_1");
  mocks.sourceSelection = { ...selection, primary: { ...selection.primary, projectId: "foreign" } };
  await user.click(screen.getByRole("button", { name: "选择第一条科学数据" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("当前选择无法带到数据页");
  expect(screen.queryByRole("link", { name: "查看所选数据" })).not.toBeInTheDocument();
});

it("restores a raw-data selection into its matching resource rather than the first file", async () => {
  const selection = validateWorkspaceSelectionContext({ schemaVersion: "1.0", sourceScopeHash: "b".repeat(64), primary: {
    selectionSchemaVersion: "1.0", kind: "DATASET_SAMPLE", sourceScopeHash: "b".repeat(64), projectId: "project_1", datasetId: "dataset_1", datasetVersion: "v1", objectId: "second", sampleRef: "sample-2",
  }, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false });
  mocks.searchQuery = new URLSearchParams({ dataset: "dataset_1", selection: encodeWorkspaceSelectionUrl(selection) }).toString();
  mocks.getDatasetSourceResources.mockResolvedValueOnce([
    { objectId: "first", datasetId: "dataset_1", versionId: "v1", objectHash: "a".repeat(64), objectType: "DataFrame", payload: [] },
    { objectId: "second", datasetId: "dataset_1", versionId: "v1", objectHash: "b".repeat(64), objectType: "DataFrame", payload: [] },
  ]);
  render(<ProjectDataPage projectId="project_1" />);
  await waitFor(() => expect(screen.getByTestId("quick-preview-scientific-viewer")).toHaveAttribute("data-object", "second"));
  expect(screen.getByTestId("quick-preview-scientific-viewer")).toHaveAttribute("data-sample", "sample-2");
  const research = new URL(screen.getByRole("link", { name: "研究此数据" }).getAttribute("href")!, "http://localhost");
  expect(research.searchParams.get("sample")).toBe("sample-2");
  expect(research.searchParams.get("sourceSelection")).toBe(encodeWorkspaceSelectionUrl(selection));
});

const routeResources = () => [
  { objectId: "first", datasetId: "dataset_1", versionId: "v1", objectHash: "a".repeat(64), objectType: "PhononBand", payload: {} },
  { objectId: "second", datasetId: "dataset_1", versionId: "v1", objectHash: "b".repeat(64), objectType: "PhononDos", payload: {} },
];

it("restores the exact resource from the URL and follows history without rereading its dataset", async () => {
  mocks.getDatasetSourceResources.mockResolvedValue(routeResources());
  mocks.searchQuery = "dataset=dataset_1&resource=second";
  const view = render(<ProjectDataPage projectId="project_1" />);
  await waitFor(() => expect(screen.getByTestId("quick-preview-scientific-viewer")).toHaveAttribute("data-object", "second"));
  expect(screen.getByRole("button", { name: "声子态密度" })).toHaveAttribute("aria-pressed", "true");
  mocks.searchQuery = "dataset=dataset_1&resource=first";
  view.rerender(<ProjectDataPage projectId="project_1" />);
  await waitFor(() => expect(screen.getByTestId("quick-preview-scientific-viewer")).toHaveAttribute("data-object", "first"));
  mocks.searchQuery = "dataset=dataset_1&resource=second";
  view.rerender(<ProjectDataPage projectId="project_1" />);
  await waitFor(() => expect(screen.getByTestId("quick-preview-scientific-viewer")).toHaveAttribute("data-object", "second"));
  expect(mocks.getDatasetSourceResources).toHaveBeenCalledTimes(1);
});

it("records explicit resource switching while clearing the previous selection and retaining unrelated URL state", async () => {
  const selection = validateWorkspaceSelectionContext({ schemaVersion: "1.0", sourceScopeHash: "a".repeat(64), primary: {
    selectionSchemaVersion: "1.0", kind: "DATASET_SAMPLE", sourceScopeHash: "a".repeat(64), projectId: "project_1", datasetId: "dataset_1", datasetVersion: "v1", objectId: "first", sampleRef: "row-1",
  }, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false });
  mocks.searchQuery = new URLSearchParams({dataset:"dataset_1",resource:"first",selection:encodeWorkspaceSelectionUrl(selection),tableQuery:"old",tableSort:"desc",tableRow:"row-1",keep:"value"}).toString();
  window.history.replaceState({ __NA: true, __PRIVATE_NEXTJS_INTERNALS_TREE: {}, retained: "yes" }, "", `/projects/project_1/data?${mocks.searchQuery}#plot`);
  try {
    mocks.getDatasetSourceResources.mockResolvedValue(routeResources());
    const view=render(<ProjectDataPage projectId="project_1" />);
    await screen.findByTestId("quick-preview-scientific-viewer");
    await userEvent.setup().click(screen.getByRole("button", { name:"声子态密度" }));
    const current=new URL(window.location.href);
    expect(current.searchParams.get("resource")).toBe("second");
    expect(current.searchParams.get("dataset")).toBe("dataset_1");
    for(const name of ["selection","tableQuery","tableSort","tableRow"])expect(current.searchParams.has(name)).toBe(false);
    expect(current.searchParams.get("keep")).toBe("value");expect(current.hash).toBe("#plot");
    expect(window.history.state).toEqual({retained:"yes",dataResourceView:true});
    mocks.searchQuery=current.search.slice(1);view.rerender(<ProjectDataPage projectId="project_1" />);
    await waitFor(() => expect(screen.getByTestId("quick-preview-scientific-viewer")).toHaveAttribute("data-object","second"));
    expect(screen.getByTestId("quick-preview-scientific-viewer")).not.toHaveAttribute("data-sample");
    expect(screen.getByRole("link",{name:"研究此数据"}).getAttribute("href")).not.toContain("sample=");
  } finally {window.history.replaceState({},"","/");}
});

it.each(["missing", ""])("never substitutes the first resource for a missing explicit target: %s", async resource => {
  mocks.getDatasetSourceResources.mockResolvedValue(routeResources());
  mocks.searchQuery=`dataset=dataset_1&resource=${resource}`;
  const view=render(<ProjectDataPage projectId="project_1" />);
  expect(await screen.findByRole("alert")).toHaveTextContent("暂时无法找到这项数据内容");
  expect(screen.queryByTestId("quick-preview-scientific-viewer")).not.toBeInTheDocument();
  expect(screen.queryByRole("link",{name:"研究此数据"})).not.toBeInTheDocument();
  if (!resource) { view.unmount(); return; }
  mocks.getDatasetSourceResources.mockResolvedValueOnce([...routeResources(),{...routeResources()[0],objectId:resource}]);
  await userEvent.setup().click(screen.getByRole("button",{name:"重新读取数据内容"}));
  await waitFor(()=>expect(screen.getByTestId("quick-preview-scientific-viewer")).toHaveAttribute("data-object",resource));
  await waitFor(() => expect(within(screen.getByRole("navigation", { name: "数据内容" })).getAllByRole("button").find(button => button.getAttribute("aria-pressed") === "true")).toHaveFocus());
  expect(mocks.getDatasetSourceResources).toHaveBeenCalledTimes(2);
  view.unmount();
});

it("does not show a scientific selection from a different explicitly requested resource", async () => {
  const selection=validateWorkspaceSelectionContext({schemaVersion:"1.0",sourceScopeHash:"a".repeat(64),primary:{selectionSchemaVersion:"1.0",kind:"DATASET_SAMPLE",sourceScopeHash:"a".repeat(64),projectId:"project_1",datasetId:"dataset_1",datasetVersion:"v1",objectId:"first",sampleRef:"sample-1"},secondary:[],propagation:"EXACT_COMPATIBLE_ONLY",compatibility:"EXACT",cleared:false});
  mocks.searchQuery=new URLSearchParams({dataset:"dataset_1",resource:"second",selection:encodeWorkspaceSelectionUrl(selection)}).toString();
  mocks.getDatasetSourceResources.mockResolvedValue(routeResources());
  render(<ProjectDataPage projectId="project_1" />);
  expect(await screen.findByRole("alert")).toHaveTextContent("链接中的数据内容与选择不一致");
  expect(screen.queryByTestId("quick-preview-scientific-viewer")).not.toBeInTheDocument();
  expect(screen.queryByRole("link",{name:"研究此数据"})).not.toBeInTheDocument();
});

it.each(["foreign dataset", "duplicate identity"])("rejects ambiguous resource reads: %s",async reason=>{
  const resources=routeResources();
  if(reason==="foreign dataset")resources[1].datasetId="foreign";
  else resources[1].objectId="first";
  mocks.searchQuery="dataset=dataset_1&resource=first";mocks.getDatasetSourceResources.mockResolvedValue(resources);
  render(<ProjectDataPage projectId="project_1" />);
  expect(await screen.findByRole("alert")).toHaveTextContent("当前科学资源暂时无法读取");
  expect(screen.queryByTestId("quick-preview-scientific-viewer")).not.toBeInTheDocument();
  expect(screen.queryByRole("link",{name:"研究此数据"})).not.toBeInTheDocument();
});

it("keeps the requested resource when a stalled read is retried and ignores its late completion",async()=>{
  let resolveOld!:(items:unknown[])=>void;
  mocks.searchQuery="dataset=dataset_1&resource=second";
  mocks.getDatasetSourceResources.mockImplementationOnce(()=>new Promise(resolve=>{resolveOld=resolve;})).mockResolvedValueOnce(routeResources());
  vi.useFakeTimers();
  try{
    await act(async()=>{render(<ProjectDataPage projectId="project_1" />);});
    await act(async()=>{await vi.advanceTimersByTimeAsync(10_000);});
    expect(screen.getByRole("alert")).toHaveTextContent("读取科学数据超时");
    await act(async()=>{fireEvent.click(screen.getByRole("button",{name:"重新加载数据"}));});
    expect(screen.getByTestId("quick-preview-scientific-viewer")).toHaveAttribute("data-object","second");
    await act(async()=>resolveOld([routeResources()[0]]));
    expect(screen.getByTestId("quick-preview-scientific-viewer")).toHaveAttribute("data-object","second");
  }finally{vi.useRealTimers();}
});

it("keeps the raw volumetric resource identity through field selection and URL restoration", async () => {
  const hash = "b".repeat(64), resourceId = "dataset_1:volume";
  const selection = validateWorkspaceSelectionContext({ schemaVersion: "1.0", sourceScopeHash: hash, primary: {
    selectionSchemaVersion: "1.0", kind: "VOLUMETRIC_FIELD", sourceScopeHash: hash, projectId: "project_1", datasetId: "dataset_1", datasetVersion: hash,
    artifactId: `source:${resourceId}:volumetric-dataset`, artifactChecksum: hash, fieldId: "channel:0",
  }, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false });
  const token = encodeWorkspaceSelectionUrl(selection);
  mocks.sourceSelection = selection;
  mocks.searchQuery = "dataset=dataset_1";
  const resource = { objectId: resourceId, datasetId: "dataset_1", objectHash: hash, objectType: "VolumetricData", payload: {} };
  mocks.getDatasetSourceResources.mockResolvedValue([resource]);
  const view = render(<ProjectDataPage projectId="project_1" />);
  await userEvent.setup().click(await screen.findByRole("button", {name: "选择第一条科学数据"}));
  expect(new URL(window.location.href).searchParams.get("resource")).toBe(resourceId);
  mocks.getDatasetSourceResources.mockResolvedValue([{...resource, objectId: "same-content"}, resource]);
  mocks.searchQuery = new URLSearchParams({dataset: "dataset_1", selection: token}).toString();
  view.unmount();
  render(<ProjectDataPage projectId="project_1" />);
  await waitFor(() => expect(screen.getByTestId("quick-preview-scientific-viewer")).toHaveAttribute("data-object", resourceId));
  const research = new URL(screen.getByRole("link", {name: "研究此数据"}).getAttribute("href")!, "http://localhost");
  expect(research.searchParams.get("sourceSelection")).toBe(token);
});

it("restores an electronic companion by exact artifact identity even when source hashes are duplicated", async () => {
  const hash = "b".repeat(64);
  const selection = validateWorkspaceSelectionContext({ schemaVersion: "1.0", sourceScopeHash: hash, primary: {
    selectionSchemaVersion: "1.0", kind: "ELECTRONIC_DOS_POINT", sourceScopeHash: hash, projectId: "project_1", datasetId: "dataset_1", datasetVersion: "v1", jobId: "source-view", artifactId: "source:second-dos", artifactChecksum: hash, electronicResourceId: "payload-resource", energyPointId: "point-2", dosChannelId: "total", spinChannelId: "none",
  }, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false });
  mocks.searchQuery = new URLSearchParams({ dataset: "dataset_1", selection: encodeWorkspaceSelectionUrl(selection) }).toString();
  const resource = { objectId: "second-dos", datasetId: "dataset_1", versionId: "v1", objectHash: hash, objectType: "ElectronicDos", payload: {} };
  mocks.getDatasetSourceResources.mockResolvedValueOnce([{ ...resource, objectId: "first-dos" }, resource]);
  render(<ProjectDataPage projectId="project_1" />);
  await waitFor(() => expect(screen.getByTestId("quick-preview-scientific-viewer")).toHaveAttribute("data-object", "second-dos"));
  const research = new URL(screen.getByRole("link", { name: "研究此数据" }).getAttribute("href")!, "http://localhost");
  expect(research.searchParams.get("sourceSelection")).toBe(encodeWorkspaceSelectionUrl(selection));
});

it.each([false, true])("carries the selected periodic atom from an upload record into Research with duplicate content: %s", async (duplicate) => {
  const hash = "b".repeat(64);
  const selection = validateWorkspaceSelectionContext({ schemaVersion: "1.0", sourceScopeHash: hash, primary: {
    selectionSchemaVersion: "1.0", kind: "PERIODIC_SITE", sourceScopeHash: hash, projectId: "project_1", datasetId: "dataset_1", datasetVersion: hash, objectId: "structure", structureId: hash, siteId: "Li-0:1.0.0",
  }, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false });
  const token = encodeWorkspaceSelectionUrl(selection);
  mocks.searchQuery = new URLSearchParams({ dataset: "dataset_1", selection: token }).toString();
  const resource = { objectId: "structure", datasetId: "dataset_1", objectHash: hash, objectType: "Structure", payload: {} };
  mocks.getDatasetSourceResources.mockResolvedValueOnce(duplicate ? [{ ...resource, objectId: "other_structure" }, resource] : [resource]);
  render(<ProjectDataPage projectId="project_1" />);
  await waitFor(() => expect(screen.getByTestId("quick-preview-scientific-viewer")).toHaveAttribute("data-object", "structure"));
  const link = await screen.findByRole("link", { name: "研究此数据" });
  const research = new URL(link.getAttribute("href")!, "http://localhost");
  expect(research.searchParams.get("sourceSelection")).toBe(token);
  expect(research.searchParams.has("sample")).toBe(false);
});
