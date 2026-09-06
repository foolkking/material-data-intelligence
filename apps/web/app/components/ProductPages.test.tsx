import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  listProjects: vi.fn(),
  createProject: vi.fn(),
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
}));

vi.mock("next/link", () => ({ default: ({ children, href, prefetch: _prefetch, ...props }: { children: React.ReactNode; href: string; prefetch?: boolean | null }) => <a href={href} {...props}>{children}</a> }));
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
vi.mock("./ProductShell", () => ({
  ProductShell: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  RequireProductAuth: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));
vi.mock("../lib/scientific-viewer-api", () => ({
  listScientificObjects: mocks.listScientificObjects,
  bulkUpdateScientificObjects: mocks.bulkUpdateScientificObjects,
  getScientificObjectDependencyImpact: mocks.getScientificObjectDependencyImpact,
  updateScientificObject: mocks.updateScientificObject,
}));
vi.mock("./ScientificViewerAdapter", () => ({
  ScientificSourceViewer: ({ resource, onSelection }: { resource: { objectType: string }; onSelection?: (selection: unknown) => void }) => <div data-testid="quick-preview-scientific-viewer">{resource.objectType}{onSelection ? <button type="button" aria-label="选择第一条科学数据" onClick={() => onSelection({ schemaVersion: "1.0", sourceScopeHash: "scope", primary: { kind: "DATASET_SAMPLE", sampleRef: "BaTiO3" }, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false })}>选择</button> : null}</div>,
}));
vi.mock("./scientific-viewer/ScientificObjectViewer", () => ({
  ScientificObjectViewer: () => <div data-testid="scientific-object-viewer" />,
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

beforeEach(() => {
  vi.clearAllMocks();
  mocks.listProjects.mockResolvedValue([{ id: "project_1", projectId: "project_1", name: "Perovskite stability study", description: "材料稳定性研究", status: "active", role: "owner" }]);
  mocks.createProject.mockResolvedValue({ id: "project_2", projectId: "project_2", name: "新项目", status: "active", role: "owner" });
  mocks.updateProject.mockImplementation(async (projectId: string, changes: Record<string, unknown>) => ({
    id: projectId,
    projectId,
    name: typeof changes.name === "string" ? changes.name : "新项目",
    description: typeof changes.description === "string" ? changes.description : undefined,
    status: changes.lifecycle === "TRASHED" ? "trashed" : "active",
    role: "owner",
    ...(changes.pinned === undefined ? {} : { pinned: changes.pinned }),
    ...(changes.tags === undefined ? {} : { tags: changes.tags }),
    ...changes,
  }));
  mocks.bulkProjectAction.mockResolvedValue({ action: "archive", projectIds: ["project_1"], count: 1 });
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
  mocks.bulkDatasetAction.mockResolvedValue({ action: "archive", datasetIds: ["dataset_1"], count: 1 });
  mocks.deleteEmptyDataset.mockResolvedValue({ datasetId: "dataset_1", deleted: true });
  mocks.getDatasetDependencyImpact.mockResolvedValue({ entity: "dataset", entityId: "dataset_1", displayName: "数据集", canDelete: true, dependencyCount: 0, dependencies: [], impact: { removedFromActiveDiscovery: false, historicalProvenanceProtected: false, historicalResearchRemainsAccessible: false } });
  mocks.getProjectHistory.mockResolvedValue({ project: { id: "project_1", name: "研究项目", role: "owner" }, datasets: [{ datasetId: "dataset_1", name: "materials-table", import: { fileCount: 1, resources: [] }, profile: { rowCount: 3, semanticRoles: {} }, status: "profile_ready" }], analyses: [] });
  mocks.getCachedProjectHistory.mockReturnValue(null);
  mocks.getDatasetSourceResources.mockResolvedValue([{ objectId: "object_1", objectType: "DataFrame", datasetId: "dataset_1", payload: [{ formula: "BaTiO3" }] }]);
  mocks.uploadDatasetFiles.mockResolvedValue({ datasetId: "dataset_2" });
  mocks.listScientificObjects.mockResolvedValue({ items: [], next_cursor: null });
  mocks.bulkUpdateScientificObjects.mockResolvedValue({
    project_id: "project_1",
    lifecycle: "ARCHIVED",
    count: 1,
    items: [],
  });
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

it("declares phonon band and DOS files as a typed companion upload", async () => {
  const user = userEvent.setup();
  render(<DatasetUploadPage projectId="project_1" />);
  await user.type(await screen.findByLabelText("数据集名称"), "phonon bundle");
  await user.upload(await screen.findByLabelText("源文件"), [
    new File(["band"], "UPLOAD_phonon_band.json", { type: "application/json" }),
    new File(["dos"], "UPLOAD_phonon_dos.json", { type: "application/json" }),
    new File(["structure"], "UPLOAD_structure.vasp", { type: "application/octet-stream" }),
  ]);
  fireEvent.submit(screen.getByRole("button", { name: "上传并解析" }).closest("form")!);
  await waitFor(() => expect(mocks.uploadDatasetFiles).toHaveBeenCalled());
  const files = mocks.uploadDatasetFiles.mock.calls[0][2];
  expect(files).toEqual(expect.arrayContaining([
    expect.objectContaining({ file: expect.objectContaining({ name: "UPLOAD_phonon_band.json" }), importKind: "phonon_band", contractVersion: "phase10h.phonon_band.v1", companionGroupId: "phonon_bundle" }),
    expect.objectContaining({ file: expect.objectContaining({ name: "UPLOAD_phonon_dos.json" }), importKind: "phonon_dos", contractVersion: "phase10h.phonon_dos.v1", companionGroupId: "phonon_bundle" }),
  ]));
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

  expect(await screen.findByRole("alert")).toHaveTextContent("PROJECT_HISTORY_TEMPORARY_FAILURE");
  await user.click(screen.getByRole("button", { name: "重新加载项目数据" }));
  expect(await screen.findByRole("heading", { name: "研究项目" })).toBeInTheDocument();
  expect(mocks.getProjectHistory).toHaveBeenCalledTimes(2);
});

it("paints a warmed project overview without showing a second loading state", async () => {
  const warmedHistory = {
    project: { id: "project_1", name: "已预热项目", role: "owner" },
    datasets: [],
    analyses: [],
  };
  mocks.getCachedProjectHistory.mockReturnValue(warmedHistory);

  render(<ProjectOverviewPage projectId="project_1" />);

  expect(screen.getByRole("heading", { name: "已预热项目" })).toBeInTheDocument();
  expect(screen.queryByText("正在加载研究内容…")).not.toBeInTheDocument();
  expect(mocks.getProjectHistory).not.toHaveBeenCalled();
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

it("restores focus to the exact scientific selection after closing the Inspector", async () => {
  const user = userEvent.setup();
  render(<ProjectDataPage projectId="project_1" />);

  const trigger = await screen.findByRole("button", { name: "选择第一条科学数据" });
  await user.click(trigger);
  await user.click(screen.getByRole("button", { name: "关闭详情" }));
  await waitFor(() => expect(document.activeElement).toBe(trigger));
});

it("groups case, phase and other projects while searching scientific capabilities", async () => {
  const user = userEvent.setup();
  mocks.listProjects.mockResolvedValue([
    { id: "case_1", name: "Case 13 · Q-PHONON-001 · Run 01", description: "声子色散、声子态密度与布里渊区联动（Phase 10H / 10I）" },
    { id: "phase_1", name: "Phase 10 · Viewer validation · Run 01", description: "结构查看器阶段记录" },
    { id: "other_1", name: "其他 · Legacy Session · Run 01", description: "历史研究会话" },
  ]);

  render(<ProjectsPage />);

  expect(await screen.findByRole("heading", { name: "16-case 项目" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Phase 项目" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "其他项目与历史记录" })).toBeInTheDocument();
  expect(screen.getByText(/声子色散、声子态密度/)).toBeInTheDocument();

  await user.type(screen.getByRole("searchbox", { name: "搜索项目、Case 或科学能力" }), "Phase 10H");
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
    expect(mocks.updateProject).toHaveBeenCalledWith("project_a", { pinned: true }),
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

  await waitFor(() => expect(mocks.getProjectExportManifest).toHaveBeenCalledWith("project_1"));
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

  await waitFor(() => expect(mocks.createProject).toHaveBeenCalledWith("新项目"));
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
  expect(screen.getByRole("status")).toHaveTextContent("项目已创建，但研究说明暂未保存");
  expect(mocks.createProject).toHaveBeenCalledTimes(1);
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
  await waitFor(() => expect(mocks.bulkProjectAction).toHaveBeenCalledWith(["case_1"], "archive"));
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
    expect(mocks.bulkProjectAction).toHaveBeenCalledWith(["project_a"], "pin"),
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
      "trash",
    ),
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
  expect(screen.getByRole("button", { name: "重新检查存储" })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "查看来源与属性" })).toBeInTheDocument();
  expect(screen.queryByRole("link", { name: "研究此数据" })).toBeNull();
  expect(screen.queryByText("Failed to fetch")).not.toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: "重新检查存储" }));
  expect(await screen.findByTestId("quick-preview-scientific-viewer")).toHaveTextContent("DataFrame");
  expect(mocks.getDatasetSourceResources).toHaveBeenCalledTimes(2);
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
    "原始解析 payload 当前不可用",
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

  expect(await screen.findByText("尚未导入科学对象")).toBeInTheDocument();
  expect(screen.getByText(/尚未接收源文件/)).toBeInTheDocument();
  expect(screen.queryByText(/解析资源暂时无法读取/)).toBeNull();
  expect(screen.queryByRole("button", { name: "重新检查存储" })).toBeNull();
  expect(screen.queryByRole("link", { name: "研究此数据" })).toBeNull();
});

it("explains the Dataset-to-immutable-scientific-version authority bridge without guessing identity", async () => {
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

  const authority = await screen.findByRole("region", {
    name: "来源 Dataset → 科研对象 → 不可变版本",
  });
  expect(authority).toHaveTextContent("高熵合金来源数据");
  expect(authority).toHaveTextContent("2 个源文件");
  expect(authority).toHaveTextContent("2 个已绑定");
  expect(authority).toHaveTextContent(
    "重命名或归档 Dataset 不会改写不可变科学版本",
  );
  expect(authority).toHaveTextContent("本页不会按名称猜测或替换版本");
  expect(screen.getAllByText("来源范围")).toHaveLength(2);
  expect(screen.getByText("解析后的科学身份")).toBeInTheDocument();
  expect(screen.getByText("选择对象后查看其精确不可变版本；它不是 Dataset 的替代入口。")).toBeInTheDocument();
  const authorityLegend = screen.getByRole("region", {
    name: "来源数据与科学身份",
  });
  expect(authorityLegend).toHaveTextContent("Dataset");
  expect(authorityLegend).toHaveTextContent("Scientific Object");
  expect(authorityLegend).toHaveTextContent("管理导入文件、记录与查询");
  expect(authorityLegend).toHaveTextContent("保存解析后的科学身份");
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
  const toggle = await screen.findByRole("button", { name: "收起数据" });
  expect(toggle).toHaveAttribute("aria-expanded", "true");
  await user.click(toggle);
  expect(screen.getByRole("button", { name: "显示数据" })).toHaveAttribute("aria-expanded", "false");
  expect(screen.getByRole("heading", { name: "研究项目" })).toBeInTheDocument();
  expect(document.getElementById("data-navigator-content")).toHaveAttribute("data-mobile-collapsed", "true");
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
    }),
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
    }),
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
  render(<ProjectsPage />);

  const row = (await screen.findByText("共享只读项目")).closest(".managed-object-row")!;
  fireEvent.contextMenu(row);
  expect(screen.getByRole("menuitem", { name: "导出项目清单" })).toBeInTheDocument();
  expect(screen.queryByRole("menuitem", { name: "编辑项目信息" })).not.toBeInTheDocument();
  await user.click(screen.getByRole("menuitem", { name: "导出项目清单" }));

  await waitFor(() => expect(mocks.getProjectExportManifest).toHaveBeenCalledWith("shared_viewer"));
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
  expect(mocks.listScientificObjects).toHaveBeenCalledWith("project_1", expect.anything(), "ACTIVE");
  fireEvent.contextMenu(datasetTitle.closest(".managed-object-row")!);
  expect(screen.getByRole("menuitem", { name: "重命名数据集" })).toBeInTheDocument();
  await user.keyboard("{Escape}");

  await user.click(screen.getByRole("button", { name: "选择多个数据或科研对象" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 materials-table" }));
  await user.click(screen.getByRole("button", { name: "归档" }));
  await waitFor(() => expect(mocks.bulkDatasetAction).toHaveBeenCalledWith(["dataset_1"], "archive"));
  await user.click(screen.getByRole("button", { name: "已归档" }));
  await waitFor(() => expect(mocks.listScientificObjects).toHaveBeenLastCalledWith("project_1", expect.anything(), "ARCHIVED"));
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
    }),
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
    }),
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
  const link = (await screen.findByText("打开 →")).closest("a");
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

it("keeps an explicitly addressed archived scientific object resolvable outside default discovery filtering", async () => {
  mocks.listScientificObjects.mockResolvedValue({
    items: [{ id: "object_1", project_id: "project_1", kind: "STRUCTURE", object_type: "structure.crystal", display_name: "archived structure", lifecycle_status: "ARCHIVED", current_version_id: "version_1" }],
    next_cursor: null,
  });
  render(<ProjectDataPage projectId="project_1" initialObjectId="object_1" initialObjectVersionId="version_1" />);

  expect(await screen.findByTestId("scientific-object-viewer")).toBeInTheDocument();
  expect(mocks.listScientificObjects).toHaveBeenCalledWith("project_1", expect.anything(), undefined);
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
  expect(state).toHaveTextContent("需要指定科研对象版本");
  expect(state).toHaveTextContent("避免静默替换为最新版本");
  expect(screen.getByRole("link", { name: "返回项目数据" })).toHaveAttribute(
    "href",
    "/projects/project_1/data",
  );
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

  const title = await screen.findByText("Silicon");
  await user.click(screen.getByRole("button", { name: "管理 Silicon" }));
  await user.click(screen.getByRole("menuitem", { name: "归档科研对象" }));
  await waitFor(() => expect(mocks.updateScientificObject).toHaveBeenCalledWith("object_1", { archived: true }));
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

  expect(await within(dialog).findByRole("alert")).toHaveTextContent(
    "批量操作服务暂时不可用",
  );
  expect(screen.getByRole("dialog", { name: "将 1 个数据集移入回收站" })).toBeInTheDocument();
});

it("removes restored scientific objects from the archived filtered view", async () => {
  const user = userEvent.setup();
  mocks.listScientificObjects.mockResolvedValue({
    items: [{ id: "object_1", project_id: "project_1", kind: "STRUCTURE", object_type: "structure.crystal", display_name: "Archived silicon", lifecycle_status: "ARCHIVED", current_version_id: "version_1" }],
    next_cursor: null,
  });
  render(<ProjectDataPage projectId="project_1" />);
  await user.click(await screen.findByRole("button", { name: "已归档" }));
  await screen.findByText("Archived silicon");
  await user.click(screen.getByRole("button", { name: "管理 Archived silicon" }));
  await user.click(screen.getByRole("menuitem", { name: "恢复科研对象" }));
  await waitFor(() => expect(mocks.updateScientificObject).toHaveBeenCalledWith("object_1", { archived: false }));
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
  await screen.findByText("Trashed silicon");
  expect(mocks.listScientificObjects).toHaveBeenLastCalledWith("project_1", expect.anything(), "TRASHED");
  await user.click(screen.getByRole("button", { name: "管理 Trashed silicon" }));
  await user.click(screen.getByRole("menuitem", { name: "恢复科研对象" }));
  await waitFor(() => expect(mocks.updateScientificObject).toHaveBeenCalledWith("object_1", { archived: false }));
});

it("previews scientific object dependencies before moving it to Trash", async () => {
  const user = userEvent.setup();
  mocks.listScientificObjects.mockResolvedValue({
    items: [{ id: "object_1", project_id: "project_1", kind: "STRUCTURE", object_type: "structure.crystal", display_name: "Silicon", lifecycle_status: "ACTIVE", current_version_id: "version_1" }],
    next_cursor: null,
  });
  render(<ProjectDataPage projectId="project_1" />);
  await screen.findByText("Silicon");
  await user.click(screen.getByRole("button", { name: "管理 Silicon" }));
  await user.click(screen.getByRole("menuitem", { name: "移入回收站" }));
  expect(await screen.findByText("依赖影响")).toBeInTheDocument();
  expect(mocks.getScientificObjectDependencyImpact).toHaveBeenCalledWith("object_1");
  expect(screen.getByText("ScientificResult：1")).toBeInTheDocument();
  expect(mocks.updateScientificObject).not.toHaveBeenCalled();
  await user.click(screen.getByRole("button", { name: "移入回收站" }));
  await waitFor(() => expect(mocks.updateScientificObject).toHaveBeenCalledWith("object_1", { lifecycle: "TRASHED" }));
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
  await screen.findByText("Shared silicon");
  await userEvent.click(screen.getByRole("button", { name: "管理 Shared silicon" }));
  expect(screen.getByRole("menuitem", { name: "查看研究记录" })).toBeInTheDocument();
  expect(screen.queryByRole("menuitem", { name: "归档科研对象" })).not.toBeInTheDocument();
  expect(mocks.updateScientificObject).not.toHaveBeenCalled();
});
