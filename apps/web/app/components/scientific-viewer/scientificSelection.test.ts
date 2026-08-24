import { describe, expect, it } from "vitest";

import type { WorkspaceSelectionContext } from "../../lib/workspace-api";
import { opaqueSelectionEnvelope, providerEnvelopeContainsInternalIdentity, scientificSelectionFromWorkspace, selectionToResearchObjectRef } from "./scientificSelection";
import { resolveScientificSelectionLink } from "./selectionLinkResolver";

describe("Agent2 Phase 9 ScientificSelection", () => {
  it("preserves exact object/version while exposing a human scientific locator", () => {
    const selection = scientificSelectionFromWorkspace(workspace("PERIODIC_SITE", { siteId: "O-12", structureId: "LiFePO4" }), source(), "scientific.structure-3d");
    expect(selection).toMatchObject({ selectionType: "PERIODIC_SITE", displayLabel: "结构位点 · O-12", semanticLocator: { siteId: "O-12" } });
    expect(selectionToResearchObjectRef(selection!)).toEqual({ object_id: source().objectId, version_id: source().versionId, project_id: "project", object_type: "structure.crystal", display_name: "LiFePO4" });
  });

  it("projects only opaque provider candidates and deterministic linked-selection outcomes", () => {
    const selection = scientificSelectionFromWorkspace(workspace("EXPERIMENTAL_XRD_PEAK", { peakId: "peak-17" }), source(), "scientific.xrd")!;
    const envelope = opaqueSelectionEnvelope([selection]);
    expect(envelope[0].candidate_id).toBe("selection_1");
    expect(providerEnvelopeContainsInternalIdentity(envelope)).toBe(false);
    expect(resolveScientificSelectionLink(selection, "xrd").status).toBe("LINKED");
    expect(resolveScientificSelectionLink(selection, "volumetric").status).toBe("UNSUPPORTED");
  });
});

function source() {
  return { projectId: "project", objectId: "11111111-1111-4111-8111-111111111111", versionId: "22222222-2222-4222-8222-222222222222", objectType: "structure.crystal", displayName: "LiFePO4" };
}

function workspace(kind: string, values: Record<string, string>): WorkspaceSelectionContext {
  return { schemaVersion: "1.0", sourceScopeHash: "a".repeat(64), primary: { selectionSchemaVersion: "1.0", kind, sourceScopeHash: "a".repeat(64), projectId: "project", datasetId: "dataset", datasetVersion: "version", objectId: "11111111-1111-4111-8111-111111111111", fieldLocator: null, ...values }, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false } as unknown as WorkspaceSelectionContext;
}
