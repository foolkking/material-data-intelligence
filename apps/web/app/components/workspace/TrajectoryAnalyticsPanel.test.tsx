import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TrajectoryAnalyticsPanel } from "./TrajectoryAnalyticsPanel";

const common = { trajectory: { trajectoryHash: `sha256:${"1".repeat(64)}` }, warnings: [], limitations: ["Bounded persisted result."] };
function artifact(content: Record<string, unknown>) { return { id: "a", artifactId: "a", sha256: "a".repeat(64), type: "table_json", name: "n4.json", content } as never; }
const workspace = { sourceReferenceHash: "b".repeat(64), projectId: "project", datasetId: "dataset", datasetVersion: "v1", sourceJobId: "job" } as never;
const onSelection = () => undefined;

describe("TrajectoryAnalyticsPanel", () => {
  it("renders RDF and MSD table alternatives", () => {
    const rdf = artifact({ ...common, artifactType: "trajectory.rdf", schema_version: "phase10n4.trajectory_rdf.v1", speciesPair: { pairId: "pair", speciesA: "Li", speciesB: "O" }, window: { mode: "whole" }, binIds: ["bin1", "bin2"], binCentersAngstrom: [1, 2], gR: [0.2, 1.1] });
    const view = render(<TrajectoryAnalyticsPanel artifacts={[rdf]} selected={rdf} workspace={workspace} onSelection={onSelection} />);
    expect(screen.getByText("径向分布函数数值表")).toBeInTheDocument();
    view.unmount();
    const msd = artifact({ ...common, artifactType: "trajectory.msd", schema_version: "phase10n4.trajectory_msd.v1", species: "Li", seriesId: "series", lagIds: ["lag1"], lagTimesPs: [1], totalMsdAngstrom2: [0.6], directionalMsdAngstrom2: { x: [0.2], y: [0.2], z: [0.2] }, originCounts: [10] });
    render(<TrajectoryAnalyticsPanel artifacts={[msd]} selected={msd} workspace={workspace} onSelection={onSelection} />);
    expect(screen.getByText("均方位移数值表")).toBeInTheDocument();
  });

  it("renders qualified and unavailable diffusion status without fitting", () => {
    const value = artifact({ ...common, artifactType: "trajectory.diffusion", schema_version: "phase10n4.trajectory_diffusion.v1", fitWindow: { windowId: "window", startPs: 2, endPs: 8 }, fit: { slopeAngstrom2PerPs: 0.6, rSquared: 0.99 }, regimeDiagnostic: { diagnosticId: "diagnostic", status: "DIFFUSIVE_WINDOW_ACCEPTED", alpha: 1.01 }, diffusionEstimate: { available: true, value: 0.1 } });
    render(<TrajectoryAnalyticsPanel artifacts={[value]} selected={value} workspace={workspace} onSelection={onSelection} />);
    expect(screen.getByText("拟合区间满足扩散判据")).toBeInTheDocument();
    expect(screen.getByText("扩散拟合诊断")).toBeInTheDocument();
    expect(screen.queryByText(/Frontend recomputation/u)).not.toBeInTheDocument();
    expect(screen.getByText("0.6")).toBeInTheDocument();
    expect(screen.getByText("0.99")).toBeInTheDocument();
  });
});
