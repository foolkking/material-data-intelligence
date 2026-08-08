import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { Artifact } from "../../lib/planner-api";
import { ExperimentalXrdComparisonPanel } from "./ExperimentalXrdComparisonPanel";
import { workspaceSnapshotFixture } from "./workspace-test-fixture";

const HASH = "a".repeat(64);

describe("ExperimentalXrdComparisonPanel", () => {
  it("renders persisted correspondence with table alternatives and exact selections", () => {
    const artifact = xrdArtifact();
    const onSelection = vi.fn();
    render(<ExperimentalXrdComparisonPanel artifacts={[artifact]} selected={artifact} workspace={workspaceSnapshotFixture().workspace} onSelection={onSelection} />);
    expect(screen.getByRole("heading", { name: "Experimental XRD comparison" })).toBeTruthy();
    expect(screen.getByRole("img", { name: /detected experimental peaks/u })).toBeTruthy();
    expect(screen.getByText(/not Rietveld refinement or definitive phase identification/u)).toBeTruthy();
    fireEvent.click(screen.getAllByRole("button", { name: "Select" })[0]);
    expect(onSelection).toHaveBeenCalledWith(expect.objectContaining({ primary: expect.objectContaining({ kind: "XRD_MATCH", matchId: "xrd-match:1", experimentalResourceId: "experimental_xrd_1", theoreticalArtifactId: "artifact_theory" }) }));
    fireEvent.click(screen.getAllByRole("button", { name: "Select" })[1]);
    expect(onSelection).toHaveBeenLastCalledWith(expect.objectContaining({ primary: expect.objectContaining({ kind: "EXPERIMENTAL_XRD_PEAK", peakId: "experimental-peak:2" }) }));
  });

  it("rejects malformed and executable-shaped payloads before presentation", () => {
    const artifact = xrdArtifact();
    artifact.content = { ...(artifact.content as Record<string, unknown>), limitations: ["javascript:alert(1)"] };
    render(<ExperimentalXrdComparisonPanel artifacts={[artifact]} selected={artifact} workspace={workspaceSnapshotFixture().workspace} onSelection={vi.fn()} />);
    expect(screen.getByRole("alert")).toHaveTextContent("N3_XRD_CONTRACT_INVALID");
  });
});

function xrdArtifact(): Artifact {
  return {
    id: "artifact_n3", artifactId: "artifact_n3", jobId: "job_demo", type: "table_json", version: "1", contentHash: HASH, sha256: HASH,
    metadata: { projectId: "project_demo" }, content: {
      schema_version: "phase10n3.experimental_xrd_comparison.v1", artifactType: "structure.experimental_xrd_comparison",
      tool: { toolId: "structure.experimental_xrd_comparison", toolVersion: "0.1.0", adapterVersion: "0.1.0" },
      experimentalResource: { resourceId: "experimental_xrd_1", resourceHash: HASH, pointCount: 5, wavelength: 1.5406, wavelengthUnit: "angstrom" },
      theoreticalArtifact: { artifactId: "artifact_theory", artifactChecksum: HASH, toolId: "structure.xrd", structureIdentities: ["structure_1"], wavelength: 1.5406, wavelengthUnit: "angstrom" },
      experimentalSeries: { twoTheta: [19.8, 20, 20.2, 40, 40.2], normalizedIntensity: [0, 1, 0, 0.8, 0] },
      experimentalPeaks: [{ peakId: "experimental-peak:1", twoTheta: 20, normalizedIntensity: 1 }, { peakId: "experimental-peak:2", twoTheta: 40, normalizedIntensity: 0.8 }],
      theoreticalPeaks: [{ peakId: "theoretical-peak:1", twoTheta: 20.02, relativeIntensity: 100, hkls: [{ hkl: [1, 0, 0] }] }, { peakId: "theoretical-peak:2", twoTheta: 60, relativeIntensity: 80, hkls: [] }],
      matches: [{ matchId: "xrd-match:1", experimentalPeakId: "experimental-peak:1", theoreticalPeakId: "theoretical-peak:1", experimentalTwoTheta: 20, theoreticalTwoTheta: 20.02, signedDeltaTwoTheta: -0.02, absoluteDeltaTwoTheta: 0.02, theoreticalHkls: [{ hkl: [1, 0, 0] }] }],
      unmatchedExperimentalPeaks: [{ peakId: "experimental-peak:2", twoTheta: 40, normalizedIntensity: 0.8 }],
      unmatchedTheoreticalPeaks: [{ peakId: "theoretical-peak:2", twoTheta: 60, relativeIntensity: 80, hkls: [] }],
      residualSummary: { matchedCount: 1, maeDeltaTwoTheta: 0.02, unit: "degree" },
      coverage: { matchedPairs: 1, unmatchedExperimentalPeaks: 1, unmatchedTheoreticalPeaks: 1 },
      matcher: { algorithmId: "mdi.xrd_ordered_position_match@1.0.0", parameters: { matching_tolerance_deg: 0.15 }, parameterHash: HASH },
      peakDetector: { algorithmId: "mdi.experimental_xrd_peak_detection@1.0.0", libraryVersion: "1.17.1", parameterHash: HASH, independentOfTheoreticalMatching: true },
      parameterHash: HASH, warnings: [], limitations: ["This is not Rietveld refinement or definitive phase identification."],
    },
  };
}
