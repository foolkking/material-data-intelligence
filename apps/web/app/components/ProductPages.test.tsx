import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  listProjects: vi.fn(),
  createProject: vi.fn(),
  updateProject: vi.fn(),
  bulkProjectAction: vi.fn(),
  deleteEmptyProject: vi.fn(),
  updateDataset: vi.fn(),
  bulkDatasetAction: vi.fn(),
  deleteEmptyDataset: vi.fn(),
  getProjectHistory: vi.fn(),
  getDatasetSourceResources: vi.fn(),
  uploadDatasetFiles: vi.fn(),
  listScientificObjects: vi.fn(),
}));

vi.mock("next/link", () => ({ default: ({ children, href, ...props }: { children: React.ReactNode; href: string }) => <a href={href} {...props}>{children}</a> }));
vi.mock("../lib/planner-api", () => ({
  listProjects: mocks.listProjects,
  createProject: mocks.createProject,
  updateProject: mocks.updateProject,
  bulkProjectAction: mocks.bulkProjectAction,
  deleteEmptyProject: mocks.deleteEmptyProject,
  updateDataset: mocks.updateDataset,
  bulkDatasetAction: mocks.bulkDatasetAction,
  deleteEmptyDataset: mocks.deleteEmptyDataset,
  getProjectHistory: mocks.getProjectHistory,
  getDatasetSourceResources: mocks.getDatasetSourceResources,
  uploadDatasetFiles: mocks.uploadDatasetFiles,
}));
vi.mock("./ProductShell", () => ({
  ProductShell: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  RequireProductAuth: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));
vi.mock("../lib/scientific-viewer-api", () => ({
  listScientificObjects: mocks.listScientificObjects,
}));
vi.mock("./ScientificViewerAdapter", () => ({
  ScientificSourceViewer: ({ resource, onSelection }: { resource: { objectType: string }; onSelection?: (selection: unknown) => void }) => <div data-testid="quick-preview-scientific-viewer">{resource.objectType}{onSelection ? <button type="button" aria-label="选择第一条科学数据" onClick={() => onSelection({ schemaVersion: "1.0", sourceScopeHash: "scope", primary: { kind: "DATASET_SAMPLE", sampleRef: "BaTiO3" }, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false })}>选择</button> : null}</div>,
}));
vi.mock("./scientific-viewer/ScientificObjectViewer", () => ({
  ScientificObjectViewer: () => <div data-testid="scientific-object-viewer" />,
}));

import { ConsolePage, DatasetUploadPage, ProjectDataPage, ProjectsPage, TableScientificView } from "./ProductPages";

beforeEach(() => {
  vi.clearAllMocks();
  mocks.listProjects.mockResolvedValue([{ id: "project_1", projectId: "project_1", name: "Perovskite stability study", description: "材料稳定性研究" }]);
  mocks.createProject.mockResolvedValue({ id: "project_2", projectId: "project_2", name: "新项目", status: "active", role: "owner" });
  mocks.updateProject.mockImplementation(async (_projectId: string, changes: Record<string, unknown>) => ({ id: "project_2", projectId: "project_2", name: "新项目", status: "active", role: "owner", ...changes }));
  mocks.bulkProjectAction.mockResolvedValue({ action: "archive", projectIds: ["project_1"], count: 1 });
  mocks.deleteEmptyProject.mockResolvedValue({ projectId: "project_1", deleted: true });
  mocks.updateDataset.mockResolvedValue({ id: "dataset_1", datasetId: "dataset_1", projectId: "project_1", name: "materials-table", status: "profile_ready" });
  mocks.bulkDatasetAction.mockResolvedValue({ action: "archive", datasetIds: ["dataset_1"], count: 1 });
  mocks.deleteEmptyDataset.mockResolvedValue({ datasetId: "dataset_1", deleted: true });
  mocks.getProjectHistory.mockResolvedValue({ project: { id: "project_1", name: "研究项目", role: "owner" }, datasets: [{ datasetId: "dataset_1", name: "materials-table", import: { fileCount: 1, resources: [] }, profile: { rowCount: 3, semanticRoles: {} }, status: "profile_ready" }], analyses: [] });
  mocks.getDatasetSourceResources.mockResolvedValue([{ objectId: "object_1", objectType: "DataFrame", datasetId: "dataset_1", payload: [{ formula: "BaTiO3" }] }]);
  mocks.uploadDatasetFiles.mockResolvedValue({ datasetId: "dataset_2" });
  mocks.listScientificObjects.mockResolvedValue({ items: [], next_cursor: null });
});

it("opens a real source-resource viewer in Console quick preview", async () => {
  const user = userEvent.setup();
  render(<ConsolePage />);

  await user.click(await screen.findByRole("button", { name: "快速查看" }));
  expect(await screen.findByRole("complementary", { name: "数据快速查看" })).toBeInTheDocument();
  expect(await screen.findByTestId("quick-preview-scientific-viewer")).toHaveTextContent("DataFrame");
  expect(mocks.getDatasetSourceResources).toHaveBeenCalledWith("dataset_1", expect.anything());
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

  await user.click(screen.getByRole("button", { name: "选择多个数据集" }));
  await user.click(screen.getByRole("checkbox", { name: "选择 materials-table" }));
  await user.click(screen.getByRole("button", { name: "归档" }));
  await waitFor(() => expect(mocks.bulkDatasetAction).toHaveBeenCalledWith(["dataset_1"], "archive"));
  await user.click(screen.getByRole("button", { name: "已归档" }));
  await waitFor(() => expect(mocks.listScientificObjects).toHaveBeenLastCalledWith("project_1", expect.anything(), "ARCHIVED"));
});

it("does not expose dataset mutation controls to a viewer project member", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { id: "project_1", name: "共享研究项目", role: "viewer" },
    datasets: [{ datasetId: "dataset_1", name: "shared-materials", status: "profile_ready", import: { fileCount: 1, resources: [] }, profile: { rowCount: 3, semanticRoles: {} } }],
    analyses: [],
  });
  render(<ProjectDataPage projectId="project_1" />);

  expect((await screen.findAllByText("shared-materials")).length).toBeGreaterThan(0);
  expect(screen.queryByRole("button", { name: "选择多个数据集" })).not.toBeInTheDocument();
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
