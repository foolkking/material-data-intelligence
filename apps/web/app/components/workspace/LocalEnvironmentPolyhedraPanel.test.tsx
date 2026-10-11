import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { localEnvironmentArtifactFixture as environmentArtifact } from "../../../scientific-viewers/workspace/saved-local-environment.fixture";
import { LocalEnvironmentPolyhedraPanel } from "./LocalEnvironmentPolyhedraPanel";
import { workspaceSnapshotFixture } from "./workspace-test-fixture";

const HASH = "a".repeat(64);
const STRUCTURE_HASH = "b".repeat(64);

describe("LocalEnvironmentPolyhedraPanel", () => {
  it("highlights saved vertices in a result preview without fabricating a workspace selection", () => {
    const artifact = environmentArtifact();
    const workspace = { ...workspaceSnapshotFixture().workspace, datasetId: null };
    const { container } = render(<LocalEnvironmentPolyhedraPanel artifacts={[artifact]} selected={artifact} workspace={workspace} />);
    expect(screen.queryByRole("button", { name: "选中配位环境" })).toBeNull();
    fireEvent.click(screen.getByText("顶点与周期近邻（4）"));
    fireEvent.click(screen.getByRole("button", { name: "顶点 1" }));
    expect(container.querySelector('[data-vertex-id="vertex:0"]')).toHaveAttribute("data-selected", "true");
    fireEvent.click(screen.getByText("多面体的面（4）"));
    fireEvent.click(screen.getByRole("button", { name: "面 1" }));
    expect(container.querySelector('polygon[data-selected="true"]')).toBeTruthy();
  });

  it("renders persisted geometry and emits exact source-bound site selection", () => {
    const artifact = environmentArtifact();
    const onSelection = vi.fn();
    render(<LocalEnvironmentPolyhedraPanel artifacts={[artifact]} selected={artifact} workspace={workspaceSnapshotFixture().workspace} onSelection={onSelection} />);
    expect(screen.getByRole("heading", { name: "配位多面体" })).toBeTruthy();
    expect(screen.getByRole("heading", { name: "位点 0 · 四面体" })).toBeTruthy();
    expect(screen.getByRole("img", { name: /配位多面体，4 个近邻顶点/u })).toBeTruthy();
    expect(screen.getByText(/不代表确定的化学键/u)).toBeTruthy();
    expect(screen.getByText("来源与参数").closest("details")).not.toHaveAttribute("open");
    fireEvent.click(screen.getByText("位点列表（1）"));
    fireEvent.click(screen.getByRole("button", { name: "选择位点 0" }));
    expect(onSelection).toHaveBeenCalledWith(expect.objectContaining({
      compatibility: "EXACT",
      primary: expect.objectContaining({
        kind: "PERIODIC_SITE",
        objectId: "structure_resource",
        structureId: STRUCTURE_HASH,
        siteId: `site:${STRUCTURE_HASH}:0`,
        artifactId: "artifact_n2",
        artifactChecksum: HASH,
      }),
    }));
    fireEvent.click(screen.getByRole("button", { name: "选中配位环境" }));
    expect(onSelection).toHaveBeenLastCalledWith(expect.objectContaining({ primary: expect.objectContaining({ kind: "LOCAL_ENVIRONMENT", environmentId: "environment:demo", sourceArtifactId: "artifact_n1", sourceArtifactChecksum: HASH }) }));
    fireEvent.click(screen.getByRole("button", { name: "选中多面体" }));
    expect(onSelection).toHaveBeenLastCalledWith(expect.objectContaining({ primary: expect.objectContaining({ kind: "COORDINATION_POLYHEDRON", polyhedronId: "polyhedron:demo" }) }));
    fireEvent.click(screen.getByText("顶点与周期近邻（4）"));
    fireEvent.click(screen.getByRole("button", { name: "顶点 1" }));
    expect(onSelection).toHaveBeenLastCalledWith(expect.objectContaining({ primary: expect.objectContaining({ kind: "POLYHEDRON_VERTEX", vertexId: "vertex:0" }) }));
    fireEvent.click(screen.getByText("多面体的面（4）"));
    fireEvent.click(screen.getByRole("button", { name: "面 1" }));
    expect(onSelection).toHaveBeenLastCalledWith(expect.objectContaining({ primary: expect.objectContaining({ kind: "POLYHEDRON_FACE", faceId: "face:0" }) }));
  });

  it("rejects malformed or untrusted payloads before presentation", () => {
    const artifact = environmentArtifact();
    const malformed = { ...artifact, content: { ...(artifact.content as Record<string, unknown>), parameterHash: "../private" } };
    render(<LocalEnvironmentPolyhedraPanel artifacts={[malformed]} selected={malformed} workspace={workspaceSnapshotFixture().workspace} onSelection={vi.fn()} />);
    expect(screen.getByRole("alert")).toHaveTextContent("N2_LOCAL_ENVIRONMENT_CONTRACT_INVALID");
  });

  it.each([
    ["non-finite nested coordinate", (payload: Record<string, any>) => { payload.siteResults[0].polyhedron.vertices[0].relativeCartesian[0] = Number.NaN; }],
    ["dangling face identity", (payload: Record<string, any>) => { payload.siteResults[0].polyhedron.faces[0].vertexIdentities[0] = "vertex:missing"; }],
    ["oversized vertices", (payload: Record<string, any>) => { payload.siteResults[0].polyhedron.vertices = Array.from({ length: 65 }, () => payload.siteResults[0].polyhedron.vertices[0]); }],
    ["unsafe object key", (payload: Record<string, any>) => { Object.defineProperty(payload.resolvedParameters, "constructor", { value: "alert(1)", enumerable: true }); }],
    ["duplicate vertex identity", (payload: Record<string, any>) => { payload.siteResults[0].polyhedron.vertices[1].vertexIdentity = "vertex:0"; }],
    ["degenerate face identity", (payload: Record<string, any>) => { payload.siteResults[0].polyhedron.faces[0].vertexIdentities = ["vertex:0", "vertex:0", "vertex:1"]; }],
  ])("rejects %s", (_name, mutate) => {
    const artifact = environmentArtifact();
    mutate(artifact.content as Record<string, any>);
    render(<LocalEnvironmentPolyhedraPanel artifacts={[artifact]} selected={artifact} workspace={workspaceSnapshotFixture().workspace} onSelection={vi.fn()} />);
    expect(screen.getByRole("alert")).toHaveTextContent("N2_LOCAL_ENVIRONMENT_CONTRACT_INVALID");
  });

  it("does not substitute another artifact when the selected result is invalid", () => {
    const artifact = environmentArtifact();
    render(<LocalEnvironmentPolyhedraPanel artifacts={[artifact]} selected={{ ...artifact, id: "invalid", artifactId: "invalid", content: {} }} workspace={workspaceSnapshotFixture().workspace} onSelection={vi.fn()} />);
    expect(screen.getByRole("alert")).toBeTruthy();
    expect(screen.queryByRole("img")).toBeNull();
  });

  it("rotates with the keyboard and restores the fitted view without changing scientific selection", () => {
    const artifact = environmentArtifact();
    const before = JSON.stringify(artifact.content);
    const onSelection = vi.fn();
    const { container } = render(<LocalEnvironmentPolyhedraPanel artifacts={[artifact]} selected={artifact} workspace={workspaceSnapshotFixture().workspace} onSelection={onSelection} />);
    const point = container.querySelector('[data-vertex-id="vertex:0"]')!;
    const initial = [point.getAttribute("cx"), point.getAttribute("cy")];
    const view = screen.getByRole("group", { name: "多面体视图，方向键旋转，Home 适配" });
    fireEvent.keyDown(view, { key: "ArrowRight" });
    expect([point.getAttribute("cx"), point.getAttribute("cy")]).not.toEqual(initial);
    fireEvent.keyDown(view, { key: "Home" });
    expect([point.getAttribute("cx"), point.getAttribute("cy")]).toEqual(initial);
    expect(onSelection).not.toHaveBeenCalled();
    expect(JSON.stringify(artifact.content)).toEqual(before);
  });

  it("keeps an unavailable surface and ambiguous classification explicit", () => {
    const artifact = environmentArtifact();
    const site = (artifact.content as Record<string, any>).siteResults[0];
    site.polyhedron = { ...site.polyhedron, status: "UNAVAILABLE", faces: [], unavailableReason: "COPLANAR_POLYHEDRON" };
    site.classification.status = "AMBIGUOUS";
    render(<LocalEnvironmentPolyhedraPanel artifacts={[artifact]} selected={artifact} workspace={workspaceSnapshotFixture().workspace} onSelection={vi.fn()} />);
    expect(screen.getByRole("heading", { name: "位点 0 · 分类不唯一" })).toBeTruthy();
    expect(screen.getByText("近邻共面，未生成三维封闭多面体。")).toBeTruthy();
    expect(screen.queryByText("多面体的面（4）")).toBeNull();
  });

  it("shows the saved scientific number without stripping zeros from its exponent", () => {
    const artifact = environmentArtifact();
    (artifact.content as Record<string, any>).siteResults[0].distortionMetrics.polyhedronVolume = 1e-10;
    render(<LocalEnvironmentPolyhedraPanel artifacts={[artifact]} selected={artifact} workspace={workspaceSnapshotFixture().workspace} onSelection={vi.fn()} />);
    fireEvent.click(screen.getByText("几何指标"));
    expect(screen.getByText("1e-10 Å³")).toBeVisible();
  });

  it("makes sites beyond the old 250-row limit reachable with exact selection", () => {
    const artifact = environmentArtifact();
    const payload = artifact.content as Record<string, any>;
    payload.siteResults = Array.from({ length: 251 }, (_, index) => ({ ...payload.siteResults[0], siteId: "site:" + STRUCTURE_HASH + ":" + index, siteIndex: index, environmentIdentity: "environment:" + index }));
    const onSelection = vi.fn();
    render(<LocalEnvironmentPolyhedraPanel artifacts={[artifact]} selected={artifact} workspace={workspaceSnapshotFixture().workspace} onSelection={onSelection} />);
    fireEvent.click(screen.getByText("位点列表（251）"));
    for (let page = 0; page < 5; page++) fireEvent.click(screen.getByRole("button", { name: "下一页位点" }));
    fireEvent.click(screen.getByRole("button", { name: "选择位点 250" }));
    expect(onSelection).toHaveBeenLastCalledWith(expect.objectContaining({ primary: expect.objectContaining({ siteId: "site:" + STRUCTURE_HASH + ":250", kind: "PERIODIC_SITE" }) }));
    expect(screen.getByRole("heading", { name: "位点 250 · 四面体" })).toBeTruthy();
    expect(within(screen.getByRole("region", { name: "位点配位列表" })).getAllByRole("row")).toHaveLength(2);
  });
});
