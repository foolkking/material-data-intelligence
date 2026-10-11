import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { Artifact } from "../../lib/planner-api";
import { ElectronicStructurePanel } from "./ElectronicStructurePanel";
import { workspaceSnapshotFixture } from "./workspace-test-fixture";
import { validateWorkspaceSelectionContext } from "../../../shared/workspace/workspace-selection-contract";

const HASH = "a".repeat(64);

describe("ElectronicStructurePanel", () => {
  it("renders persisted Band and DOS facts with exact selection identities", () => {
    const band = bandArtifact(), dos = dosArtifact();
    const onSelection = vi.fn();
    render(<ElectronicStructurePanel artifacts={[band, dos]} selected={band} workspace={workspaceSnapshotFixture().workspace} onSelection={onSelection} />);
    expect(screen.getByTestId("electronic-band-plot")).toBeTruthy();
    expect(screen.getByTestId("electronic-dos-plot")).toBeTruthy();
    expect(screen.getByText(/数据源、能量参考、费米能级和自旋语义完全兼容/u)).toBeTruthy();
    expect(screen.getByText(/0\.6 eV/u)).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "选择带隙" }));
    expect(onSelection).toHaveBeenCalledWith(expect.objectContaining({ primary: expect.objectContaining({ kind: "ELECTRONIC_BAND_GAP", electronicResourceId: "band_1", artifactId: "artifact_band", artifactChecksum: HASH }) }));
    fireEvent.click(screen.getByText(/能带数值 ·/));
    fireEvent.click(screen.getAllByRole("button", { name: "选择" })[0]);
    expect(onSelection).toHaveBeenLastCalledWith(expect.objectContaining({ primary: expect.objectContaining({ kind: "ELECTRONIC_BAND_STATE", kpointId: "kp_g", bandId: "v1" }) }));
  });

  it("does not combine incompatible persisted sources", () => {
    const band = bandArtifact(), dos = dosArtifact();
    (dos.content as Record<string, any>).sourceResource.calculationIdentity = "calc_other";
    render(<ElectronicStructurePanel artifacts={[band, dos]} selected={dos} workspace={workspaceSnapshotFixture().workspace} onSelection={vi.fn()} />);
    expect(screen.getByText(/DO_NOT_COMBINE/u)).toBeTruthy();
  });

  it("rejects non-finite and executable-shaped untrusted payloads", () => {
    const band = bandArtifact();
    (band.content as Record<string, any>).bands[0].energiesEv[0] = Number.NaN;
    (band.content as Record<string, any>).sourceResource.javascript = "alert(1)";
    render(<ElectronicStructurePanel artifacts={[band]} selected={band} workspace={workspaceSnapshotFixture().workspace} onSelection={vi.fn()} />);
    expect(screen.getByRole("alert")).toHaveTextContent("N5_ELECTRONIC_CONTRACT_INVALID");
  });

  it("keeps large persisted curves bounded and avoids spread-based range failures", () => {
    const band = bandArtifact();
    const content = band.content as Record<string, any>;
    content.bands[0].energiesEv = Array.from({ length: 10_000 }, (_, index) => Math.sin(index / 20));
    content.bands = [content.bands[0]];
    content.kpoints = content.bands[0].energiesEv.map((_: number, index: number) => ({ kpointId: `k-${index}`, pathDistance: index / 50 }));
    render(<ElectronicStructurePanel artifacts={[band]} selected={band} workspace={workspaceSnapshotFixture().workspace} onSelection={vi.fn()} />);
    const points = screen.getByTestId("electronic-band-plot").querySelector("polyline")?.getAttribute("points") ?? "";
    expect(points.split(" ").filter(Boolean).length).toBeLessThanOrEqual(2_400);
    expect(points.split(" ").filter(Boolean).length).toBeGreaterThan(1_000);
    expect(screen.getByText(/有界预览/u)).toBeTruthy();
  });

  it("discloses presentation denominators without changing the persisted electronic result", () => {
    const band = bandArtifact();
    const content = band.content as Record<string, any>;
    content.bands = Array.from({ length: 49 }, (_, index) => ({
      bandIdentity: `band-${index}`,
      bandId: `b-${index}`,
      spinChannel: "none",
      energiesEv: [-index, index],
    }));
    content.states = Array.from({ length: 501 }, (_, index) => ({
      stateId: `state-${index}`,
      bandId: "b-0",
      spinChannel: "none",
      kpointId: "kp_g",
      energyEv: index,
    }));
    render(<ElectronicStructurePanel artifacts={[band]} selected={band} workspace={workspaceSnapshotFixture().workspace} onSelection={vi.fn()} />);
    expect(screen.getByText(/显示 48 \/ 49 条能带/u)).toBeTruthy();
    expect(screen.getByText("1–500 / 501 行")).toBeTruthy();
    expect(content.bands).toHaveLength(49);
    expect(content.states).toHaveLength(501);
  });

  it("pages to exact later band states and resets when the source checksum changes", () => {
    const band = bandArtifact(), onSelection = vi.fn();
    const content = band.content as Record<string, any>;
    content.states = Array.from({ length: 1040 }, (_, index) => ({ stateId: `state-${index}`, bandId: "b4", spinChannel: index < 520 ? "up" : "down", kpointId: `kp-${index}`, energyEv: index }));
    const props = { artifacts: [band], selected: band, workspace: workspaceSnapshotFixture().workspace, onSelection };
    const view = render(<ElectronicStructurePanel {...props} />);
    fireEvent.click(screen.getByText(/能带数值 ·/));
    expect(screen.getByRole("button", { name: "上一页" })).toBeDisabled();
    fireEvent.change(screen.getByLabelText("能带页码"), { target: { value: "3" } });
    expect(screen.getAllByRole("button", { name: "选择" })).toHaveLength(40);
    fireEvent.click(screen.getAllByRole("button", { name: "选择" })[0]);
    expect(onSelection).toHaveBeenLastCalledWith(expect.objectContaining({ primary: expect.objectContaining({ bandStateId: "state-1000", spinChannelId: "down", kpointId: "kp-1000", bandId: "b4" }) }));
    expect(screen.getByRole("button", { name: "下一页" })).toBeDisabled();
    const changed = { ...band, sha256: "b".repeat(64), contentHash: "b".repeat(64) };
    view.rerender(<ElectronicStructurePanel {...props} artifacts={[changed]} selected={changed} />);
    expect(screen.getByLabelText("能带页码")).toHaveValue(1);
    expect(content.states).toHaveLength(1040);
  });

  it("pages DOS by channel and energy without losing projection identity", () => {
    const dos = dosArtifact(), onSelection = vi.fn();
    const content = dos.content as Record<string, any>;
    content.energiesEv = Array.from({ length: 501 }, (_, index) => index / 100);
    content.energyPointIds = content.energiesEv.map((_: number, index: number) => `ep-${index}`);
    content.totalDos[0].values = content.energiesEv;
    content.projections[0].values = content.energiesEv;
    content.projections[0].spinChannel = "down";
    render(<ElectronicStructurePanel artifacts={[dos]} selected={dos} workspace={workspaceSnapshotFixture().workspace} onSelection={onSelection} />);
    fireEvent.click(screen.getByText(/态密度数值 ·/));
    fireEvent.click(screen.getByRole("button", { name: "下一页" }));
    fireEvent.click(screen.getAllByRole("button", { name: "选择" })[1]);
    expect(onSelection).toHaveBeenLastCalledWith(expect.objectContaining({ primary: expect.objectContaining({ energyPointId: "ep-0", dosChannelId: "si_s", projectionId: "si_s_identity", spinChannelId: "down" }) }));
    fireEvent.change(screen.getByLabelText("态密度页码"), { target: { value: "999" } });
    expect(screen.getByLabelText("态密度页码")).toHaveValue(3);
    expect(screen.getByText("1001–1002 / 1002 行")).toBeTruthy();
    expect(screen.getAllByRole("button", { name: "选择" })).toHaveLength(2);
    fireEvent.click(screen.getAllByRole("button", { name: "选择" })[1]);
    expect(onSelection).toHaveBeenLastCalledWith(expect.objectContaining({ primary: expect.objectContaining({ energyPointId: "ep-500", projectionId: "si_s_identity" }) }));
  });

  it("shows a truthful empty state when a valid contract has no finite curve values", () => {
    const band = bandArtifact();
    const content = band.content as Record<string, any>;
    content.bands = [];
    content.states = [];
    render(<ElectronicStructurePanel artifacts={[band]} selected={band} workspace={workspaceSnapshotFixture().workspace} onSelection={vi.fn()} />);
    expect(screen.queryByTestId("electronic-band-plot")).toBeNull();
    expect(screen.getByText(/没有可绘制的有限数值/u)).toBeTruthy();
  });

  it("keeps numerical tables and provenance collapsed while exposing plot axes", () => {
    render(<ElectronicStructurePanel artifacts={[bandArtifact(), dosArtifact()]} selected={bandArtifact()} workspace={workspaceSnapshotFixture().workspace} onSelection={vi.fn()} />);
    expect(screen.getByText(/能带数值 ·/).closest("details")).not.toHaveAttribute("open");
    expect(screen.getByText("数据与来源").closest("details")).not.toHaveAttribute("open");
    expect(screen.getByTestId("electronic-band-plot")).toHaveTextContent("倒易路径（源文件距离）");
    expect(screen.getByTestId("electronic-dos-plot")).toHaveTextContent("态密度（states/eV/cell）");
    for (const button of screen.getAllByRole("button", { name: "选择" })) expect(button).not.toBeVisible();
  });

  it("does not offer selection of an unavailable gap or replace the selected source with a sibling", () => {
    const first = bandArtifact(), selected = bandArtifact();
    selected.id = selected.artifactId = "selected_exact";
    (selected.content as Record<string, any>).gap.valueEv = null;
    render(<ElectronicStructurePanel artifacts={[first, selected]} selected={selected} workspace={workspaceSnapshotFixture().workspace} onSelection={vi.fn()} />);
    expect(screen.queryByRole("button", { name: "选择带隙" })).not.toBeInTheDocument();
    expect(screen.getByText("源数据未提供带隙结果。")).toBeInTheDocument();
  });

  it("preserves an exact DOS point identity when opening its numeric table", () => {
    const dos = dosArtifact(), onSelection = vi.fn();
    render(<ElectronicStructurePanel artifacts={[dos]} selected={dos} workspace={workspaceSnapshotFixture().workspace} onSelection={onSelection} />);
    fireEvent.click(screen.getByText(/态密度数值 ·/));
    fireEvent.click(screen.getAllByRole("button", { name: "选择" })[1]);
    expect(onSelection).toHaveBeenCalledWith(expect.objectContaining({ primary: expect.objectContaining({ kind: "ELECTRONIC_DOS_POINT", energyPointId: "ep_1", dosChannelId: "total", artifactId: "artifact_dos" }) }));
  });

  it("puts the selected DOS first when switching a combined source", () => {
    const band = bandArtifact(), dos = dosArtifact();
    render(<ElectronicStructurePanel artifacts={[band, dos]} selected={dos} workspace={workspaceSnapshotFixture().workspace} onSelection={vi.fn()} />);
    expect(screen.getByTestId("electronic-structure-panel").firstElementChild).toHaveAttribute("data-testid", "electronic-dos-view");
  });

  it.each(["dos-version", undefined])("binds a companion DOS selection to its own source and version: %s", (version) => {
    const band = bandArtifact(), dos = dosArtifact(), onSelection = vi.fn();
    const workspace = { ...workspaceSnapshotFixture().workspace, sourceJobId: "source-view" };
    dos.id = dos.artifactId = "source:dos-object";
    dos.jobId = "source-view";
    dos.sha256 = dos.contentHash = "b".repeat(64);
    dos.metadata = { sourceObjectId: "dos-object", sourceDatasetId: workspace.datasetId, sourceVersionId: version };
    render(<ElectronicStructurePanel artifacts={[band, dos]} selected={band} workspace={workspace} onSelection={onSelection} />);
    fireEvent.click(screen.getByText(/态密度数值 ·/));
    const table = screen.getByTestId("electronic-dos-view").querySelector("tbody button")!;
    fireEvent.click(table);
    const selection = validateWorkspaceSelectionContext(onSelection.mock.calls[0][0]);
    expect(selection.sourceScopeHash).toBe(dos.sha256);
    expect(selection.primary).toMatchObject({ sourceScopeHash: dos.sha256, datasetVersion: version ?? dos.sha256, electronicResourceId: "dos_1", artifactId: "source:dos-object", artifactChecksum: dos.sha256 });
  });

  it("retains the shared result scope for generated companion artifacts", () => {
    const band = bandArtifact(), dos = dosArtifact(), onSelection = vi.fn();
    dos.sha256 = "b".repeat(64);
    const workspace = workspaceSnapshotFixture().workspace;
    render(<ElectronicStructurePanel artifacts={[band, dos]} selected={band} workspace={workspace} onSelection={onSelection} />);
    fireEvent.click(screen.getByText(/态密度数值 ·/));
    fireEvent.click(screen.getByTestId("electronic-dos-view").querySelector("tbody button")!);
    expect(onSelection).toHaveBeenCalledWith(expect.objectContaining({ sourceScopeHash: workspace.sourceReferenceHash, primary: expect.objectContaining({ datasetVersion: workspace.datasetVersion, artifactChecksum: dos.sha256 }) }));
  });
});

function base(type: "electronic.band_structure" | "electronic.dos", id: string): Artifact {
  return { id, artifactId: id, jobId: "job_demo", toolCallId: `call_${id}`, type: "table_json", version: "1", contentHash: HASH, sha256: HASH, metadata: { projectId: "project_demo" }, content: {
    artifactType: type, schemaVersion: `phase10n5.${type.replace("electronic.", "electronic_")}.v1`, tool: { toolId: type, toolVersion: "0.1.0", adapterVersion: "0.1.0" }, sourceResource: { resourceId: type === "electronic.band_structure" ? "band_1" : "dos_1", resourceHash: HASH, calculationIdentity: "calc_1", structureIdentity: { structureId: "structure_1", structureHash: HASH } }, energy: { unit: "eV", reference: "source_absolute", fermiEnergyEv: 0 }, spin: { mode: "non_spin_polarized", channels: ["none"] }, warnings: [], limitations: ["Derived only from supplied electronic output."],
  } };
}

function bandArtifact(): Artifact {
  const artifact = base("electronic.band_structure", "artifact_band");
  Object.assign(artifact.content as Record<string, unknown>, { kpoints: [{ kpointId: "kp_g", fractionalCoordinates: [0, 0, 0], pathDistance: 0 }, { kpointId: "kp_x", fractionalCoordinates: [0.5, 0, 0], pathDistance: 1 }], bands: [{ bandIdentity: "band_identity_v1", bandId: "v1", spinChannel: "none", energiesEv: [-0.5, -0.2] }, { bandIdentity: "band_identity_c1", bandId: "c1", spinChannel: "none", energiesEv: [0.4, 0.8] }], states: [{ stateId: "state_1", bandId: "v1", spinChannel: "none", kpointId: "kp_g", energyEv: -0.5 }], gap: { valueEv: 0.6, directness: "INDIRECT", classification: "NONZERO_GAP_UNDER_POLICY" } });
  return artifact;
}

function dosArtifact(): Artifact {
  const artifact = base("electronic.dos", "artifact_dos");
  Object.assign(artifact.content as Record<string, unknown>, { dosUnitSemantic: "states_per_ev_cell", energiesEv: [-1, 0, 1], energyPointIds: ["ep_0", "ep_1", "ep_2"], totalDos: [{ channelIdentity: "total_identity", channelId: "total", spinChannel: "none", values: [1, 0.1, 2] }], projections: [{ channelIdentity: "si_s_identity", channelId: "si_s", spinChannel: "none", projectionKind: "orbital", label: "s", values: [0.4, 0.04, 0.8] }], projectionCompleteness: "PARTIAL" });
  return artifact;
}
