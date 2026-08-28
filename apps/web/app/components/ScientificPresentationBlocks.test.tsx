import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ScientificPresentationBlocks } from "./ScientificPresentationBlocks";

const mocks = vi.hoisted(() => ({
  getPlannerInterpretationEvidence: vi.fn(),
}));

vi.mock("../lib/planner-api", () => ({
  getPlannerInterpretationEvidence: mocks.getPlannerInterpretationEvidence,
}));

const presentation = {
  schemaVersion: "1.0" as const,
  exactSourceRefs: [{ objectId: "object-1", versionId: "version-2", objectType: "structure.crystal", displayName: "Silicon" }],
  blocks: [{
    id: "evidence-1",
    type: "evidence_reference" as const,
    title: "证据",
    label: "band_gap = 2.5",
    source: {
      resultId: "result-1",
      interpretationId: "interpretation-1",
      evidenceId: "evidence-1",
      artifactId: "artifact-1",
      jobId: "job-1",
      toolCallId: "call-1",
      objectId: "object-1",
      versionId: "version-2",
    },
  }],
};

describe("ScientificPresentationBlocks evidence inspector", () => {
  it("opens a bounded exact source chain without exposing raw infrastructure details", async () => {
    mocks.getPlannerInterpretationEvidence.mockResolvedValue({
      interpretationId: "interpretation-1",
      bundleId: "bundle-1",
      bundleHash: "a".repeat(64),
      jobId: "job-1",
      planId: "plan-1",
      evidenceItems: [{
        schemaVersion: "1.0",
        evidenceItemId: "evidence-1",
        semanticRole: "band_gap",
        evidenceKind: "SCALAR",
        subjectId: "mat-2",
        displayValue: "2.5",
        unit: "eV",
        sourceArtifactId: "artifact-1",
        sourceArtifactChecksum: "b".repeat(64),
        artifactContract: "dataset.table",
        artifactContractVersion: "1.0",
        sourceToolId: "data.materials_explorer",
        sourceToolVersion: "1.0",
        fieldLocator: { fieldId: "band_gap", entityId: "mat-2" },
        warnings: [],
        limitations: [],
      }],
      sourceArtifactIds: ["artifact-1"],
      sourceObjectRefs: [{ objectId: "object-1", versionId: "version-2", objectType: "dataset", displayName: "Dataset" }],
      artifacts: [{ artifactId: "artifact-1", jobId: "job-1", contentHash: "c".repeat(64) }],
      toolCalls: [{ id: "call-1", toolId: "data.materials_explorer", status: "completed" }],
      bundleWarnings: [],
      bundleLimitations: [],
    });

    const user = userEvent.setup();
    render(<ScientificPresentationBlocks presentation={presentation} projectId="project-1" instanceId="turn-1" />);
    await user.click(screen.getByRole("button", { name: "检查证据链" }));

    expect(await screen.findByRole("region", { name: "证据链 evidence-1" })).toHaveTextContent("version-2");
    expect(screen.getByRole("region", { name: "证据链 evidence-1" })).toHaveTextContent("data.materials_explorer");
    expect(screen.getByRole("region", { name: "证据链 evidence-1" })).toHaveTextContent("band_gap · 2.5 eV");
    expect(screen.getByRole("region", { name: "证据链 evidence-1" })).not.toHaveTextContent("redis://");
    expect(screen.getByRole("link", { name: "打开权威 Artifact" })).toHaveAttribute("href", "/api/planner/jobs/job-1/artifacts/artifact-1/content");
    await waitFor(() => expect(mocks.getPlannerInterpretationEvidence).toHaveBeenCalledWith("interpretation-1"));
  });
});
