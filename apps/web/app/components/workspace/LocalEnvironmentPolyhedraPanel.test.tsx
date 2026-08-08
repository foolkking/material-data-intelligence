import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { Artifact } from "../../lib/planner-api";
import { LocalEnvironmentPolyhedraPanel } from "./LocalEnvironmentPolyhedraPanel";
import { workspaceSnapshotFixture } from "./workspace-test-fixture";

const HASH = "a".repeat(64);
const STRUCTURE_HASH = "b".repeat(64);

describe("LocalEnvironmentPolyhedraPanel", () => {
  it("renders persisted geometry and emits exact source-bound site selection", () => {
    const artifact = environmentArtifact();
    const onSelection = vi.fn();
    render(<LocalEnvironmentPolyhedraPanel artifacts={[artifact]} selected={artifact} workspace={workspaceSnapshotFixture().workspace} onSelection={onSelection} />);
    expect(screen.getByRole("heading", { name: "Geometry-derived local environment" })).toBeTruthy();
    expect(screen.getByText("tetrahedral")).toBeTruthy();
    expect(screen.getByRole("img", { name: /Persisted polyhedron/u })).toBeTruthy();
    expect(screen.getByText(/not definitive bonding chemistry/u)).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "0" }));
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
    fireEvent.click(screen.getByRole("button", { name: "Select environment" }));
    expect(onSelection).toHaveBeenLastCalledWith(expect.objectContaining({ primary: expect.objectContaining({ kind: "LOCAL_ENVIRONMENT", environmentId: "environment:demo", sourceArtifactId: "artifact_n1", sourceArtifactChecksum: HASH }) }));
    fireEvent.click(screen.getByRole("button", { name: "Select polyhedron" }));
    expect(onSelection).toHaveBeenLastCalledWith(expect.objectContaining({ primary: expect.objectContaining({ kind: "COORDINATION_POLYHEDRON", polyhedronId: "polyhedron:demo" }) }));
    fireEvent.click(screen.getByRole("button", { name: "Select vertex 1" }));
    expect(onSelection).toHaveBeenLastCalledWith(expect.objectContaining({ primary: expect.objectContaining({ kind: "POLYHEDRON_VERTEX", vertexId: "vertex:0" }) }));
    fireEvent.click(screen.getByRole("button", { name: "Select face 1" }));
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
  ])("rejects %s", (_name, mutate) => {
    const artifact = environmentArtifact();
    mutate(artifact.content as Record<string, any>);
    render(<LocalEnvironmentPolyhedraPanel artifacts={[artifact]} selected={artifact} workspace={workspaceSnapshotFixture().workspace} onSelection={vi.fn()} />);
    expect(screen.getByRole("alert")).toHaveTextContent("N2_LOCAL_ENVIRONMENT_CONTRACT_INVALID");
  });
});

function environmentArtifact(): Artifact {
  return {
    id: "artifact_n2", artifactId: "artifact_n2", jobId: "job_demo", toolCallId: "call_n2", type: "table_json", version: "1", contentHash: HASH, sha256: HASH,
    metadata: { projectId: "project_demo" }, content: {
      schema_version: "phase10n2.local_environment_polyhedra.v1", artifactType: "structure.local_environment_polyhedra",
      tool: { toolId: "structure.local_environment_polyhedra", toolVersion: "0.1.0", adapterVersion: "0.1.0" },
      algorithm: { classification: "mdi.angular_spectrum_reference_match@1.0.0", faceConstruction: "scipy.spatial.ConvexHull@1.17.1" },
      referenceCatalog: { catalogId: "mdi.local_geometry_reference_catalog", catalogVersion: "1.0.0", geometryIds: ["tetrahedral"] },
      resolvedParameters: {}, parameterHash: HASH, scope: { sourceResourceId: "structure_resource", sourceResourceHash: HASH, structureHash: STRUCTURE_HASH },
      sourceCoordination: { artifactId: "artifact_n1", artifactChecksum: HASH, toolId: "structure.coordination_crystalnn", toolVersion: "0.1.0", algorithmId: "pymatgen.crystalnn", algorithmVersion: "2026.5.4", parameterHash: HASH, contractVersion: "phase10n1.crystalnn_coordination.v1" },
      coverage: { status: "COMPLETE", requestedSites: 1, evaluatedSites: 1, unavailableSites: 0, classifiedSites: 1, ambiguousSites: 0, unclassifiedSites: 0, ratio: 1 }, warnings: [],
      siteResults: [{ environmentIdentity: "environment:demo", polyhedronIdentity: "polyhedron:demo", siteId: `site:${STRUCTURE_HASH}:0`, siteIndex: 0, structureHash: STRUCTURE_HASH,
        classification: { status: "CLASSIFIED", referenceGeometryId: "tetrahedral", referenceGeometryVersion: "1.0.0", geometryDistanceRms: 0, geometryScore: 1, alternatives: [] },
        sourceCoordinationValue: 4, sourceCoordinationSemantics: "crystalnn_weight_sum", neighborRelationIdentities: ["neighbor:0", "neighbor:1", "neighbor:2", "neighbor:3"],
        polyhedron: { status: "AVAILABLE", unavailableReason: null, vertices: [0, 1, 2, 3].map((index) => ({ vertexIdentity: `vertex:${index}`, neighborIdentity: `neighbor:${index}`, neighborSiteId: `site:${STRUCTURE_HASH}:${index + 1}`, periodicImage: [0, 0, 0], relativeCartesian: [index, index % 2, 0] as [number, number, number], distance: index + 1, distanceUnit: "angstrom" })), faces: [{ faceIdentity: "face:0", vertexIdentities: ["vertex:0", "vertex:1", "vertex:2"] }] },
        distortionMetrics: { geometryDistanceRms: 0, radialDistanceMean: 2.3 }, warnings: [],
      }],
      runtimeDiagnostics: {}, provenance: {}, limits: {}, security: {},
    },
  };
}
