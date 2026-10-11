import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TrajectoryAnalyticsPanel } from "./TrajectoryAnalyticsPanel";
import type { Artifact } from "../../lib/planner-api";

const common = { trajectory: { trajectoryHash: `sha256:${"1".repeat(64)}` }, warnings: [], limitations: ["Bounded persisted result."] };
function artifact(content: Record<string, unknown>) { return { id: "a", artifactId: "a", sha256: "a".repeat(64), type: "table_json", name: "n4.json", content } as Artifact; }
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
    expect(screen.getByLabelText("扩散拟合诊断")).toBeInTheDocument();
    expect(screen.queryByText(/Frontend recomputation/u)).not.toBeInTheDocument();
    expect(screen.getByText("0.6")).toBeInTheDocument();
    expect(screen.getByText("0.99")).toBeInTheDocument();
  });

  const msdPayload = { ...common, artifactType: "trajectory.msd", schema_version: "phase10n4.trajectory_msd.v1", species: "Li", seriesId: "series", lagIds: ["lag1", "lag2"], lagTimesPs: [0.1, 0.2], totalMsdAngstrom2: [0.6, 1.2], directionalMsdAngstrom2: { x: [0.1, 0.2], y: [0.2, 0.4], z: [0.3, 0.6] }, originCounts: [10, 9] };

  it("shows all saved MSD directions before the collapsed table and retains exact lag selection", () => {
    const value = artifact(msdPayload), select = vi.fn();
    render(<TrajectoryAnalyticsPanel artifacts={[value]} selected={value} workspace={workspace} onSelection={select} />);
    const plot = screen.getByRole("img", { name: /均方位移曲线/ });
    expect(plot.querySelectorAll('polyline[data-point-count="2"]')).toHaveLength(4);
    expect(screen.getByText("数值数据 · 2 行").closest("details")).not.toHaveAttribute("open");
    fireEvent.click(screen.getByText("数值数据 · 2 行"));
    fireEvent.click(screen.getByRole("button", { name: "选择滞后时间 0.2 ps" }));
    expect(select).toHaveBeenCalledWith(expect.objectContaining({ primary: expect.objectContaining({
      kind: "TRAJECTORY_MSD_LAG", msdSeriesId: "series", msdLagId: "lag2", artifactId: "a", artifactChecksum: "a".repeat(64), jobId: "job", datasetVersion: "v1",
    }) }));
  });

  it.each([
    { lagTimesPs: [0.1, NaN] }, { totalMsdAngstrom2: [0.6] },
    { directionalMsdAngstrom2: { x: [0.1, Infinity], y: [0.2, 0.4], z: [0.3, 0.6] } },
    { lagIds: ["lag1", "lag1"] }, { originCounts: [10, -1] }, { lagTimesPs: [0.2, 0.1] },
  ])("rejects malformed arrays without dropping points or shifting identity: %j", change => {
    const value = artifact({ ...msdPayload, ...change });
    render(<TrajectoryAnalyticsPanel artifacts={[value]} selected={value} workspace={workspace} onSelection={onSelection} />);
    expect(screen.getByRole("alert")).toHaveTextContent("轨迹分析结果不可用");
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("omits inactive selection controls in a read-only result preview", () => {
    const value = artifact(msdPayload);
    render(<TrajectoryAnalyticsPanel artifacts={[value]} selected={value} workspace={workspace} />);
    expect(screen.getByRole("img", { name: /均方位移曲线/ })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /选择/ })).not.toBeInTheDocument();
    fireEvent.click(screen.getByText("数值数据 · 2 行"));
    expect(screen.queryByRole("button", { name: /选择/ })).not.toBeInTheDocument();
  });

  it("preserves an insufficient-duration diagnostic, rejects coefficient promotion and binds the saved fit to its producer", () => {
    const value = artifact({ ...common, artifactType: "trajectory.diffusion", schema_version: "phase10n4.trajectory_diffusion.v1",
      scope: { toolCallId: "call", jobId: "job" }, fitWindow: { windowId: "window", startPs: 0.02, endPs: 0.1, durationPs: 0.08, pointCount: 41 },
      resolvedParameters: { minimum_fit_duration_ps: 1 }, fit: { rSquared: 0.9998 }, regimeDiagnostic: { diagnosticId: "diagnostic", status: "INSUFFICIENT_DURATION" }, diffusionEstimate: { available: true, value: 0.0514 } });
    const plot = { ...artifact({}), type: "plotly_json", jobId: "job", toolCallId: "call", content: {
      schema_version: "phase10n4.trajectory_plot.v1", artifactType: "diffusion_fit_plot", data: [
        { name: "MSD", x: [0.02, 0.1], y: [0.006, 0.03] }, { name: "persisted fit", x: [0.02, 0.1], y: [0.0061, 0.0301] },
      ],
    } } as Artifact;
    const view = render(<TrajectoryAnalyticsPanel artifacts={[value, plot]} selected={value} workspace={workspace} onSelection={onSelection} />);
    expect(screen.getByRole("status")).toHaveTextContent("拟合窗口时长不足");
    expect(screen.getByText("最短要求（ps）")).toBeInTheDocument();
    expect(screen.queryByText(/0.0514/)).not.toBeInTheDocument();
    expect(screen.getByRole("img", { name: /所选窗口/ }).querySelectorAll("polyline")).toHaveLength(2);
    view.rerender(<TrajectoryAnalyticsPanel artifacts={[value, { ...plot, toolCallId: "other" }]} selected={value} workspace={workspace} onSelection={onSelection} />);
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });
});
