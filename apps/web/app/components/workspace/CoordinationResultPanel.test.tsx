import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { Artifact } from "../../lib/planner-api";
import { CoordinationResultPanel } from "./CoordinationResultPanel";
import { workspaceSnapshotFixture } from "./workspace-test-fixture";

const HASH = "a".repeat(64);
const STRUCTURE_HASH = "b".repeat(64);

describe("CoordinationResultPanel", () => {
  it("compares algorithm-specific Artifacts and emits an exact site selection", () => {
    const crystal = coordinationArtifact("crystalnn", 4);
    const voronoi = coordinationArtifact("voronoinn", 6);
    const onSelection = vi.fn();

    render(
      <CoordinationResultPanel
        artifacts={[crystal, voronoi]}
        selected={crystal}
        workspace={workspaceSnapshotFixture().workspace}
        onSelection={onSelection}
      />,
    );

    expect(screen.getByRole("heading", { name: "Algorithm comparison" })).toBeTruthy();
    expect(screen.getByText(/not definitive chemical bonding/u)).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "0" }));

    expect(onSelection).toHaveBeenCalledWith(expect.objectContaining({
      compatibility: "EXACT",
      primary: expect.objectContaining({
        kind: "PERIODIC_SITE",
        objectId: "structure_resource",
        structureId: STRUCTURE_HASH,
        siteId: `site:${STRUCTURE_HASH}:0`,
        artifactId: "artifact_crystalnn",
        artifactChecksum: HASH,
      }),
    }));
  });

  it("rejects a malformed periodic-image identity before presentation", () => {
    const artifact = coordinationArtifact("crystalnn", 4);
    const content = structuredClone(artifact.content) as Record<string, any>;
    content.siteResults[0].neighbors[0].periodicImage = [0, 0, 0.5];
    const malformed = { ...artifact, content };

    render(
      <CoordinationResultPanel
        artifacts={[malformed]}
        selected={malformed}
        workspace={workspaceSnapshotFixture().workspace}
        onSelection={vi.fn()}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent("COORDINATION_CONTRACT_INVALID");
  });
});

function coordinationArtifact(algorithm: "crystalnn" | "voronoinn", coordinationValue: number): Artifact {
  const algorithmName = algorithm === "crystalnn" ? "CrystalNN" : "VoronoiNN";
  const artifactType = `structure.coordination_${algorithm}`;
  return {
    id: `artifact_${algorithm}`,
    artifactId: `artifact_${algorithm}`,
    jobId: "job_demo",
    toolCallId: `call_${algorithm}`,
    type: "table_json",
    version: "1",
    contentHash: HASH,
    sha256: HASH,
    metadata: { projectId: "project_demo" },
    content: {
      schema_version: `phase10n1.${algorithm}_coordination.v1`,
      artifactType,
      algorithm: { algorithmId: `pymatgen.${algorithmName}`, algorithmVersion: "2026.5.4" },
      library: { name: "pymatgen", version: "2026.5.4", license: "MIT" },
      resolvedParameters: {},
      parameterHash: HASH,
      scope: { sourceResourceId: "structure_resource", sourceResourceHash: HASH },
      coverage: { status: "COMPLETE", totalSites: 1, successfulSites: 1, unsupportedSites: 0, failedSites: 0, ratio: 1 },
      siteResults: [{
        siteId: `site:${STRUCTURE_HASH}:0`,
        siteIndex: 0,
        structureHash: STRUCTURE_HASH,
        species: "Si",
        coordinationSemantics: `${algorithmName}-derived coordination`,
        coordinationValue,
        neighborCount: 1,
        neighbors: [{
          neighborIdentity: `neighbor:${STRUCTURE_HASH}:0:1:0,0,0:${algorithm}`,
          neighborSiteId: `site:${STRUCTURE_HASH}:1`,
          neighborSiteIndex: 1,
          periodicImage: [0, 0, 0],
          distance: 2.35,
          distanceUnit: "angstrom",
          weight: 1,
        }],
      }],
      warnings: [],
    },
  };
}
