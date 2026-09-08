import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  getScientificViewerProjection: vi.fn(),
  listScientificObjects: vi.fn(),
  getProjectHistory: vi.fn(),
  listResearchSessions: vi.fn(),
  updateScientificObject: vi.fn(),
}));

vi.mock("../../lib/scientific-viewer-api", () => ({
  getScientificViewerProjection: mocks.getScientificViewerProjection,
  listScientificObjects: mocks.listScientificObjects,
  updateScientificObject: mocks.updateScientificObject,
}));
vi.mock("../../lib/planner-api", () => ({ getProjectHistory: mocks.getProjectHistory }));
vi.mock("../../lib/product-api", () => ({ listResearchSessions: mocks.listResearchSessions }));
vi.mock("../../../scientific-viewers/ScientificViewerAdapter", () => ({
  ScientificSourceViewer: () => <div data-testid="source-viewer">source viewer</div>,
}));
vi.mock("../../shared/layout/ProductNavigation", () => ({
  ProductLink: ({ children, href, ...props }: { children: React.ReactNode; href: string }) => <a href={href} {...props}>{children}</a>,
}));

import { ScientificObjectViewer } from "./ScientificObjectViewer";

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
  mocks.listScientificObjects.mockReset().mockResolvedValue({
    items: [{ id: "object-1", project_id: "project-1", kind: "scientific_object", object_type: "structure.crystal", display_name: "Silicon", lifecycle_status: "ACTIVE", current_version_id: "version-1" }],
    next_cursor: null,
  });
  mocks.getProjectHistory.mockReset().mockResolvedValue({ items: [] });
  mocks.listResearchSessions.mockReset().mockResolvedValue({ items: [] });
});

it("exposes a bounded retry and exact-source escape hatch when payload is unavailable", async () => {
  const user = userEvent.setup();
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" />);
  await waitFor(() => expect(screen.getByText("精确来源的原始科学数据当前不可用")).toBeInTheDocument());
  const sourceLink = screen.getByRole("link", { name: "查看来源与属性" });
  expect(sourceLink).toHaveAttribute("href", "/projects/project-1/data?object=object-1&version=version-1");
  expect(sourceLink).toHaveClass("product-primary-action");
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
  expect(screen.getByRole("link", { name: "查看来源与属性" })).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "重新读取来源" })).not.toBeInTheDocument();
});

it("explains disabled lifecycle actions without hiding the exact viewer", async () => {
  mocks.listScientificObjects.mockResolvedValue({
    items: [{ id: "object-1", project_id: "project-1", kind: "scientific_object", object_type: "structure.crystal", display_name: "Silicon", lifecycle_status: "INVALIDATED", current_version_id: "version-1" }],
    next_cursor: null,
  });
  render(<ScientificObjectViewer projectId="project-1" objectId="object-1" versionId="version-1" />);
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
