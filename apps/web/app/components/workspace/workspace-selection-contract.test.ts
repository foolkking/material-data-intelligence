import { describe, expect, it } from "vitest";

import type { WorkspaceSelectionContext, WorkspaceSelectionKind, WorkspaceSelectionRef } from "../../lib/workspace-api";
import {
  canonicalSelectionJson,
  clearedWorkspaceSelection,
  decodeWorkspaceSelectionUrl,
  encodeWorkspaceSelectionUrl,
  selectionRefIdentity,
  validateWorkspaceSelectionContext,
  validateWorkspaceSelectionRef,
  WorkspaceSelectionError,
  WORKSPACE_SELECTION_KINDS,
} from "./workspace-selection-contract";

const HASH = "a".repeat(64);

describe("Phase 10M-3 canonical Workspace selection contract", () => {
  it.each(WORKSPACE_SELECTION_KINDS)("validates exact %s identities", (kind) => {
    const ref = validateWorkspaceSelectionRef(selection(kind));
    expect(ref.kind).toBe(kind);
    expect(selectionRefIdentity(ref)).toBe(canonicalSelectionJson(ref));
  });

  it("round-trips canonical URL state and rejects non-canonical, duplicate-key, and over-cap tokens", () => {
    const context = contextFor("DATASET_SAMPLE");
    const token = encodeWorkspaceSelectionUrl(context);
    expect(token.length).toBeLessThanOrEqual(2_048);
    expect(decodeWorkspaceSelectionUrl(token)).toEqual(context);

    const duplicate = canonicalSelectionJson(context).replace('"schemaVersion":"1.0"', '"schemaVersion":"1.0","schemaVersion":"1.0"');
    expect(() => decodeWorkspaceSelectionUrl(base64url(duplicate))).toThrowError(/invalid or non-canonical/u);
    expect(() => decodeWorkspaceSelectionUrl("not+base64")).toThrowError(/base64url/u);
    expect(() => decodeWorkspaceSelectionUrl("a".repeat(2_049))).toThrowError(/2048/u);
  });

  it("restores canonical 1.0 URL tokens created before the additive N2 identity fields", () => {
    const context = contextFor("DATASET_SAMPLE");
    const legacy = JSON.parse(canonicalSelectionJson(context)) as Record<string, unknown>;
    const primary = legacy.primary as Record<string, unknown>;
    for (const field of ["environmentId", "polyhedronId", "vertexId", "faceId", "geometryReferenceId"]) delete primary[field];
    const raw = canonicalSelectionJson(legacy as unknown as WorkspaceSelectionContext);
    expect(decodeWorkspaceSelectionUrl(base64url(raw))).toEqual(context);
  });

  it("rejects index, display-label, fuzzy, path, URL, and executable authority fields", () => {
    for (const injected of [
      { rowIndex: 0 }, { displayLabel: "sample one" }, { fuzzyTarget: "band gap-ish" },
      { path: "C:\\private\\artifact.json" }, { url: "https://example.invalid" },
      { script: "alert(1)" },
    ]) {
      expect(() => validateWorkspaceSelectionRef({ ...selection("DATASET_SAMPLE"), ...injected })).toThrow();
    }
    const prototypeKey = JSON.parse('{"__proto__":{"polluted":true}}') as Record<string, unknown>;
    expect(() => validateWorkspaceSelectionRef({ ...selection("DATASET_SAMPLE"), ...prototypeKey })).toThrow();
  });

  it("rejects stale, foreign, mixed-kind, and duplicate multi-selection", () => {
    const primary = selection("DATASET_SAMPLE");
    expect(() => validateWorkspaceSelectionContext({ ...contextFor("DATASET_SAMPLE"), sourceScopeHash: "b".repeat(64) })).toThrowError(/scope/u);
    expect(() => validateWorkspaceSelectionContext({ ...contextFor("DATASET_SAMPLE"), secondary: [{ ...primary, projectId: "project_foreign", sampleRef: "sample_2" }] })).toThrowError(/project/u);
    expect(() => validateWorkspaceSelectionContext({ ...contextFor("DATASET_SAMPLE"), secondary: [selection("ARTIFACT")] })).toThrowError(/kind/u);
    expect(() => validateWorkspaceSelectionContext({ ...contextFor("DATASET_SAMPLE"), secondary: [primary] })).toThrow(WorkspaceSelectionError);
  });

  it("accepts 16 exact secondary identities and rejects the seventeenth without truncation", () => {
    const primary = selection("DATASET_SAMPLE");
    const secondary = Array.from({ length: 16 }, (_, index) => ({
      ...primary,
      objectId: `object_${index + 2}`,
      sampleRef: `sample_${index + 2}`,
    }));
    expect(validateWorkspaceSelectionContext({ ...contextFor("DATASET_SAMPLE"), secondary }).secondary).toHaveLength(16);
    expect(() => validateWorkspaceSelectionContext({
      ...contextFor("DATASET_SAMPLE"),
      secondary: [...secondary, { ...primary, objectId: "object_18", sampleRef: "sample_18" }],
    })).toThrowError("Selection context bounds are invalid.");
  });

  it("uses an explicit inert cleared context", () => {
    expect(clearedWorkspaceSelection(HASH)).toEqual(expect.objectContaining({ cleared: true, primary: null, secondary: [], compatibility: "NOT_APPLICABLE" }));
  });
});

function contextFor(kind: WorkspaceSelectionKind) {
  return validateWorkspaceSelectionContext({
    schemaVersion: "1.0",
    sourceScopeHash: HASH,
    primary: selection(kind),
    secondary: [],
    propagation: "EXACT_COMPATIBLE_ONLY",
    compatibility: "EXACT",
    cleared: false,
  });
}

function selection(kind: WorkspaceSelectionKind): WorkspaceSelectionRef {
  const values: Record<string, string | null> = Object.fromEntries([
    "datasetId", "datasetVersion", "jobId", "objectId", "sampleRef", "structureId", "siteId",
    "trajectoryId", "atomId", "frameId", "phononArtifactId", "qPointId", "branchId",
    "reciprocalArtifactId", "reciprocalPointId", "segmentId", "fieldId", "regionId",
    "artifactId", "artifactChecksum", "artifactContract", "artifactVersion", "toolCallId",
    "bundleId", "bundleHash", "evidenceItemId", "sourceArtifactId", "sourceArtifactChecksum",
    "fieldLocator", "interpretationId", "interpretationHash", "claimId",
    "environmentId", "polyhedronId", "vertexId", "faceId", "geometryReferenceId",
  ].map((field) => [field, null]));
  Object.assign(values, {
    DATASET_SAMPLE: { datasetId: "dataset_1", datasetVersion: "v1", objectId: "object_1", sampleRef: "sample_1" },
    MATERIAL_OBJECT: { datasetId: "dataset_1", datasetVersion: "v1", objectId: "object_1" },
    STRUCTURE: { datasetId: "dataset_1", datasetVersion: "v1", objectId: "object_1", structureId: "structure_1" },
    PERIODIC_SITE: { datasetId: "dataset_1", datasetVersion: "v1", objectId: "object_1", structureId: "structure_1", siteId: "site_1" },
    LOCAL_ENVIRONMENT: { datasetId: "dataset_1", datasetVersion: "v1", jobId: "job_1", objectId: "object_1", structureId: "structure_1", siteId: "site_1", artifactId: "artifact_n2", artifactChecksum: HASH, sourceArtifactId: "artifact_n1", sourceArtifactChecksum: HASH, environmentId: "environment_1", geometryReferenceId: "tetrahedral" },
    COORDINATION_POLYHEDRON: { datasetId: "dataset_1", datasetVersion: "v1", jobId: "job_1", objectId: "object_1", structureId: "structure_1", siteId: "site_1", artifactId: "artifact_n2", artifactChecksum: HASH, sourceArtifactId: "artifact_n1", sourceArtifactChecksum: HASH, environmentId: "environment_1", polyhedronId: "polyhedron_1", geometryReferenceId: "tetrahedral" },
    POLYHEDRON_VERTEX: { datasetId: "dataset_1", datasetVersion: "v1", jobId: "job_1", objectId: "object_1", structureId: "structure_1", siteId: "site_1", artifactId: "artifact_n2", artifactChecksum: HASH, sourceArtifactId: "artifact_n1", sourceArtifactChecksum: HASH, polyhedronId: "polyhedron_1", vertexId: "vertex:neighbor:0,0,0" },
    POLYHEDRON_FACE: { datasetId: "dataset_1", datasetVersion: "v1", jobId: "job_1", objectId: "object_1", structureId: "structure_1", siteId: "site_1", artifactId: "artifact_n2", artifactChecksum: HASH, sourceArtifactId: "artifact_n1", sourceArtifactChecksum: HASH, polyhedronId: "polyhedron_1", faceId: "face:vertex:0|vertex:1|vertex:2" },
    TRAJECTORY_ATOM: { datasetId: "dataset_1", datasetVersion: "v1", trajectoryId: "trajectory_1", atomId: "atom_1" },
    TRAJECTORY_FRAME: { datasetId: "dataset_1", datasetVersion: "v1", trajectoryId: "trajectory_1", frameId: "frame_1" },
    PHONON_Q_POINT: { datasetId: "dataset_1", datasetVersion: "v1", phononArtifactId: "artifact_phonon", artifactChecksum: HASH, qPointId: "qpoint_1" },
    PHONON_BRANCH: { datasetId: "dataset_1", datasetVersion: "v1", phononArtifactId: "artifact_phonon", artifactChecksum: HASH, branchId: "branch_1" },
    RECIPROCAL_POINT: { datasetId: "dataset_1", datasetVersion: "v1", reciprocalArtifactId: "artifact_bz", artifactChecksum: HASH, reciprocalPointId: "point_gamma" },
    VOLUMETRIC_FIELD: { datasetId: "dataset_1", datasetVersion: "v1", fieldId: "field_charge", artifactId: "artifact_volume", artifactChecksum: HASH },
    ARTIFACT: { jobId: "job_1", artifactId: "artifact_1", artifactChecksum: HASH, artifactContract: "platform.dataset.summary", artifactVersion: "1.0" },
    EVIDENCE_ITEM: { jobId: "job_1", bundleId: "bundle_1", bundleHash: HASH, evidenceItemId: "evidence_1", sourceArtifactId: "artifact_1", sourceArtifactChecksum: HASH, fieldLocator: "metrics.rmse" },
    CLAIM: { jobId: "job_1", interpretationId: "interpretation_1", interpretationHash: HASH, claimId: "claim_1" },
  }[kind]);
  return { selectionSchemaVersion: "1.0", kind, sourceScopeHash: HASH, projectId: "project_1", ...values } as WorkspaceSelectionRef;
}

function base64url(raw: string): string {
  return btoa(raw).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/u, "");
}
