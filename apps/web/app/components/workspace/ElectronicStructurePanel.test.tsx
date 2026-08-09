import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { Artifact } from "../../lib/planner-api";
import { ElectronicStructurePanel } from "./ElectronicStructurePanel";
import { workspaceSnapshotFixture } from "./workspace-test-fixture";

const HASH = "a".repeat(64);

describe("ElectronicStructurePanel", () => {
  it("renders persisted Band and DOS facts with exact selection identities", () => {
    const band = bandArtifact(), dos = dosArtifact();
    const onSelection = vi.fn();
    render(<ElectronicStructurePanel artifacts={[band, dos]} selected={band} workspace={workspaceSnapshotFixture().workspace} onSelection={onSelection} />);
    expect(screen.getByTestId("electronic-band-plot")).toBeTruthy();
    expect(screen.getByTestId("electronic-dos-plot")).toBeTruthy();
    expect(screen.getByText(/Exact compatible source/u)).toBeTruthy();
    expect(screen.getByText(/0\.6 eV/u)).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Select gap" }));
    expect(onSelection).toHaveBeenCalledWith(expect.objectContaining({ primary: expect.objectContaining({ kind: "ELECTRONIC_BAND_GAP", electronicResourceId: "band_1", artifactId: "artifact_band", artifactChecksum: HASH }) }));
    fireEvent.click(screen.getAllByRole("button", { name: "Select" })[0]);
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
