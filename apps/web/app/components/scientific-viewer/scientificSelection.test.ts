import { describe, expect, it } from "vitest";

import type { WorkspaceSelectionContext } from "../../lib/workspace-api";
import { apiSemanticLocator, opaqueSelectionEnvelope, providerEnvelopeContainsInternalIdentity, scientificSelectionFromWorkspace, selectionToResearchObjectRef } from "./scientificSelection";
import { resolveScientificSelectionLink } from "./selectionLinkResolver";

describe("Agent2 Phase 9 ScientificSelection", () => {
  it("preserves exact object/version while exposing a human scientific locator", () => {
    const selection = scientificSelectionFromWorkspace(workspace("PERIODIC_SITE", { siteId: "O-12", structureId: "LiFePO4" }), source(), "scientific.structure-3d");
    expect(selection).toMatchObject({ selectionType: "PERIODIC_SITE", displayLabel: "结构位点 · O-12", semanticLocator: { siteId: "O-12" } });
    expect(apiSemanticLocator(selection!)).toEqual({ site_id: "O-12" });
    expect(selectionToResearchObjectRef(selection!)).toEqual({ object_id: source().objectId, version_id: source().versionId, project_id: "project", object_type: "structure.crystal", display_name: "LiFePO4" });
  });

  it("projects only opaque provider candidates and deterministic linked-selection outcomes", () => {
    const selection = scientificSelectionFromWorkspace(workspace("EXPERIMENTAL_XRD_PEAK", { peakId: "peak-17", jobId: "source-view", artifactId: "artifact-1", artifactChecksum: "a".repeat(64), experimentalResourceId: "resource-1" }), source(), "scientific.xrd")!;
    const envelope = opaqueSelectionEnvelope([selection]);
    expect(envelope[0].candidate_id).toBe("selection_1");
    expect(providerEnvelopeContainsInternalIdentity(envelope)).toBe(false);
    expect(resolveScientificSelectionLink(selection, "xrd").status).toBe("LINKED");
    expect(resolveScientificSelectionLink(selection, "volumetric").status).toBe("UNSUPPORTED");
  });

  it.each(["projectId", "datasetVersion"])("rejects a selection from a different %s instead of rebinding it", (field) => {
    const value = workspace("PERIODIC_SITE", { siteId: "O-12", structureId: "LiFePO4", [field]: "foreign" });
    expect(scientificSelectionFromWorkspace(value, source(), "scientific.structure-3d")).toBeNull();
  });

  it("checks a known source fingerprint and refuses partial multi-selection", () => {
    const value = workspace("PERIODIC_SITE", { siteId: "O-12", structureId: "LiFePO4" });
    expect(scientificSelectionFromWorkspace(value, source(), "scientific.structure-3d", "b".repeat(64))).toBeNull();
    expect(scientificSelectionFromWorkspace({ ...value, secondary: [{ ...value.primary!, siteId: "O-13" }] }, source(), "scientific.structure-3d")).toBeNull();
  });

  it("preserves child sample identities while binding the immutable parent version", () => {
    const value = workspace("DATASET_SAMPLE", { objectId: "child-resource", sampleRef: "sample-1" });
    expect(scientificSelectionFromWorkspace(value, source(), "scientific.scientific-table")).toMatchObject({ sourceRef: source(), semanticLocator: { sampleRef: "sample-1" } });
    expect(value.primary?.objectId).toBe("child-resource");
  });

  it.each(["ELECTRONIC_BAND_STATE", "ELECTRONIC_DOS_POINT"])("preserves the spin and channel identity of %s through the exact-version viewer", kind => {
    const value = workspace(kind, { jobId: "source-view", artifactId: "source:resource", artifactChecksum: "a".repeat(64), electronicResourceId: "resource", spinChannelId: "down",
      ...(kind === "ELECTRONIC_BAND_STATE" ? { bandId: "b1", kpointId: "k1", bandStateId: "state1" } : { dosChannelId: "p-orbital", energyPointId: "point1", projectionId: "projection1" }) });
    const selected = scientificSelectionFromWorkspace(value, source(), "scientific.electronic")!;
    expect(apiSemanticLocator(selected)).toMatchObject({ spin_channel_id: "down", ...(kind === "ELECTRONIC_BAND_STATE" ? { band_id: "b1", kpoint_id: "k1", band_state_id: "state1" } : { dos_channel_id: "p-orbital", energy_point_id: "point1", projection_id: "projection1" }) });
  });
});

function source() {
  return { projectId: "project", objectId: "11111111-1111-4111-8111-111111111111", versionId: "22222222-2222-4222-8222-222222222222", objectType: "structure.crystal", displayName: "LiFePO4" };
}

function workspace(kind: string, values: Record<string, string>): WorkspaceSelectionContext {
  return { schemaVersion: "1.0", sourceScopeHash: "a".repeat(64), primary: { selectionSchemaVersion: "1.0", kind, sourceScopeHash: "a".repeat(64), projectId: "project", datasetId: "dataset", datasetVersion: source().versionId, ...(kind === "EXPERIMENTAL_XRD_PEAK" || kind.startsWith("ELECTRONIC_") ? {} : { objectId: source().objectId }), fieldLocator: null, ...values }, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false } as unknown as WorkspaceSelectionContext;
}
