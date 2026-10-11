import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { sourceResourceArtifact } from "../../scientific-viewers/ScientificViewerAdapter";
import { selectPhononBandPoint, restoredPhononBandPoint, selectPhononDosPoint, restoredPhononDosPoint, phononDosPoint } from "../../scientific-viewers/phonon-shared/phonon-selection";
import type { ScientificWorkspace } from "../../app/lib/workspace-api";
import { encodeWorkspaceSelectionUrl, validateWorkspaceSelectionContext } from "../../shared/workspace/workspace-selection-contract";
import { bindStructureSelection, datasetStructureSelection, selectedStructureResource, datasetSourceSelection, selectedDatasetSourceResource, bindDatasetSourceSelection } from "./dataset-source-selection";

const hash = "a".repeat(64);
const context = validateWorkspaceSelectionContext({ schemaVersion: "1.0", sourceScopeHash: hash, primary: {
  selectionSchemaVersion: "1.0", kind: "PERIODIC_SITE", sourceScopeHash: hash, projectId: "project_1", datasetId: "dataset_selected", datasetVersion: hash,
  objectId: "resource_structure", structureId: hash, siteId: "Li-0:-1.0.1",
}, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false });
const token = encodeWorkspaceSelectionUrl(context);
const selection = datasetStructureSelection("project_1", "dataset_selected", token)!;
const resource = { objectId: "resource_structure", objectType: "Structure", datasetId: "dataset_selected", objectHash: hash,
  payload: { lattice: { matrix: [[5, 0, 0], [1, 6, 0], [0, 1, 7]] }, sites: [{ species: [{ element: "Li", occu: 1 }], xyz: [1, 2, 3] }] } };
const promoted = { object: { id: "scientific_structure", project_id: "project_1", object_type: "structure.crystal", current_version_id: "newer_version" },
  version: { id: "exact_version", scientific_object_id: "scientific_structure", semantic_hash: hash,
    source_resource_refs_json: [{ project_id: "project_1", dataset_id: "dataset_selected", resource_id: "resource_structure" }] } };

describe("dataset structure Research selection", () => {
  it("binds the selected resource and periodic position to the returned immutable version", () => {
    expect(selectedStructureResource(selection, [{ ...resource, objectId: "first" }, resource])).toBe(resource);
    const bound = bindStructureSelection(selection, resource, promoted);
    expect(bound.object_ref.version_id).toBe("exact_version");
    expect(bound.semantic_locator).toEqual({ site_id: "Li-0:-1.0.1", site_index: 0, species: "Li", image_offset_a: -1, image_offset_b: 0, image_offset_c: 1 });
    expect(bound.display_label).toContain("周期位置 [-1, 0, 1]");
  });
  it.each(["projectId", "datasetId", "sample", "malformed", "site"])("rejects ambiguous or invalid %s route context", (field) => {
    const invalid = field === "malformed" ? "invalid" : field === "site" ? encodeWorkspaceSelectionUrl({ ...context, primary: { ...context.primary!, siteId: "Li-999999999999999999999:0.0.0" } }) : token;
    expect(() => datasetStructureSelection(field === "projectId" ? "foreign" : "project_1", field === "datasetId" ? "foreign" : "dataset_selected", invalid, field === "sample" ? "row_1" : undefined)).toThrow();
  });
  it.each(["objectId", "datasetId", "objectHash", "versionId", "objectType"])("rejects a changed resource %s", (field) => {
    expect(() => selectedStructureResource(selection, [{ ...resource, [field]: "foreign" }])).toThrow();
  });
  it("rejects missing, duplicate and nonexistent atom identities", () => {
    expect(() => selectedStructureResource(selection, [])).toThrow();
    expect(() => selectedStructureResource(selection, [resource, resource])).toThrow();
    expect(() => selectedStructureResource({ ...selection, siteIndex: 1 }, [resource])).toThrow();
    expect(() => selectedStructureResource({ ...selection, species: "Na" }, [resource])).toThrow();
  });
  it.each(["semantic_hash", "scientific_object_id", "source_resource_refs_json", "id"])("rejects unverified promoted version %s", (field) => {
    expect(() => bindStructureSelection(selection, resource, { ...promoted, version: { ...promoted.version, [field]: field === "id" ? "" : "foreign" } })).toThrow();
  });
  it("rejects a promoted object in another project", () => {
    expect(() => bindStructureSelection(selection, resource, { ...promoted, object: { ...promoted.object, project_id: "foreign" } })).toThrow();
  });
});

function electronicFixture(kind: "band" | "dos", projection = false) {
  const resourceId = "dataset:electronic", payloadId = "source-calculation";
  const primary = { selectionSchemaVersion: "1.0", sourceScopeHash: hash, projectId: "project_1", datasetId: "dataset_selected", datasetVersion: "v1", jobId: "source-view", artifactId: `source:${resourceId}`, artifactChecksum: hash, electronicResourceId: payloadId, spinChannelId: "down",
    ...(kind === "band" ? { kind: "ELECTRONIC_BAND_STATE", bandId: "b1", kpointId: "k1", bandStateId: `source-state:${resourceId}:b1:1` }
      : { kind: "ELECTRONIC_DOS_POINT", dosChannelId: "total", energyPointId: `source-dos-point:${resourceId}:1`, ...(projection ? { projectionId: `source-dos:${resourceId}:projection:down:total` } : {}) }) };
  const context = validateWorkspaceSelectionContext({ schemaVersion: "1.0", sourceScopeHash: hash, primary, secondary: [], propagation: "EXACT_COMPATIBLE_ONLY", compatibility: "EXACT", cleared: false });
  const token = encodeWorkspaceSelectionUrl(context);
  const selection = datasetSourceSelection("project_1", "dataset_selected", token)!;
  const source = { schemaVersion: kind === "band" ? "phase10n5.electronic_band_resource.v1" : "phase10n5.electronic_dos_resource.v1", resourceId: payloadId, energyUnit: "eV", energyReference: "source_absolute",
    kpoints: [{ kpointId: "k0" }, { kpointId: "k1" }], bands: [{ bandId: "b1", spinChannel: "up", energiesEv: [3, 4] }, { bandId: "b1", spinChannel: "down", energiesEv: [1, 2] }],
    energiesEv: [-3, -0.25, 4], totalDos: [{ channelId: "total", spinChannel: "up", values: [4, 5, 6] }, { channelId: "total", spinChannel: "down", values: [1, 2, 3] }], projections: [{ channelId: "total", spinChannel: "down", values: [0.1, 0.2, 0.3], projectionKind: "orbital" }] };
  const resource = { objectId: resourceId, datasetId: "dataset_selected", objectHash: hash, versionId: "v1", objectType: kind === "band" ? "ElectronicBand" : "ElectronicDos", payload: source };
  const promoted = { object: { id: "object_electronic", project_id: "project_1", object_type: kind === "band" ? "electronic.band_structure" : "electronic.dos", current_version_id: "newer" },
    version: { id: "exact_version", scientific_object_id: "object_electronic", semantic_hash: hash, source_resource_refs_json: [{ project_id: "project_1", dataset_id: resource.datasetId, resource_id: resourceId }] } };
  return { context, token, selection, resource, source, promoted };
}

function phononFixture() {
  const payload = JSON.parse(readFileSync(resolve(__dirname, "../../../../tests/fixtures/phonon_contract/stable_band.json"), "utf8"));
  const resource = {objectId: "phonon_resource", objectType: "PhononBand", datasetId: "dataset_selected", objectHash: hash, versionId: "phonon_v1", payload};
  const artifact = sourceResourceArtifact(resource);
  const workspace = {projectId: "project_1", datasetId: "dataset_selected", datasetVersion: "companion_version", sourceReferenceHash: "b".repeat(64), sourceJobId: "source-view"} as ScientificWorkspace;
  const context = selectPhononBandPoint(workspace, artifact, {qpointIndex: 1, branchIndex: 2})!;
  const token = encodeWorkspaceSelectionUrl(context);
  const selection = datasetSourceSelection("project_1", resource.datasetId, token)!;
  const promoted = {object: {id: "phonon_object", project_id: "project_1", object_type: "phonon.band_structure"}, version: {id: "admitted_phonon_version", scientific_object_id: "phonon_object", semantic_hash: hash, source_resource_refs_json: [{project_id: "project_1", dataset_id: resource.datasetId, resource_id: resource.objectId}]}};
  return {payload, resource, artifact, workspace, context, token, selection, promoted};
}

function phononDosFixture(projectionIndex: number | null = null) {
  const payload = JSON.parse(readFileSync(resolve(__dirname, "../../../../tests/fixtures/phonon_contract/projected_dos.json"), "utf8"));
  const resource = {...phononFixture().resource, objectType: "PhononDos", payload};
  const artifact = sourceResourceArtifact(resource), workspace = phononFixture().workspace;
  const context = selectPhononDosPoint(workspace, artifact, {frequencyIndex: 0, projectionIndex})!;
  const token = encodeWorkspaceSelectionUrl(context), selection = datasetSourceSelection("project_1", resource.datasetId, token)!;
  const previous = phononFixture().promoted;
  const promoted = {...previous, object: {...previous.object, object_type: "phonon.dos"}};
  return {payload, resource, artifact, workspace, context, token, selection, promoted};
}

describe("phonon DOS Research handoff", () => {
  it.each([null, 0, 1])("keeps exact negative frequency and original density for channel %s", projectionIndex => {
    const {payload, resource, artifact, context, token, selection, promoted} = phononDosFixture(projectionIndex);
    expect(token.length).toBeLessThanOrEqual(2048);
    expect(context.sourceScopeHash).toBe(hash);
    expect(restoredPhononDosPoint(context, artifact)).toMatchObject({frequencyIndex: 0, projectionIndex});
    expect(selectedDatasetSourceResource(selection, [{...resource, objectId: "sibling"}, resource])).toBe(resource);
    const bound = bindDatasetSourceSelection(selection, resource, promoted);
    expect(bound.viewer_id).toBe("scientific.phonon-dos");
    expect(bound.object_ref.object_type).toBe("phonon.dos");
    expect(bound.semantic_locator).toMatchObject({frequency_point_index: 0, frequency_thz: -1, dos_value: projectionIndex === null ? payload.total_dos[0] : payload.projected_dos[projectionIndex].values[0], channel_kind: projectionIndex === null ? "total" : "projection"});
    if (projectionIndex !== null) expect(bound.semantic_locator).toMatchObject({projection_index: projectionIndex, atom_index: projectionIndex, species: "Si"});
    expect(bound.evidence_locator).toEqual(bound.semantic_locator);
  });
  it.each([["frequency:999", "total"], ["frequency:0", "projection:999"], ["frequency:-1", "total"], ["frequency:01", "total"], ["energy:1", "total"], ["frequency:0", "up"], ["frequency:9007199254740992", "total"]])("rejects invalid sample %s / %s", (frequency, channel) => {
    expect(phononDosPoint(phononDosFixture().payload, frequency, channel)).toBeNull();
  });
  it.each(["objectId", "objectHash", "versionId", "datasetId", "objectType"])("rejects changed DOS resource %s", field => {
    const {selection, resource} = phononDosFixture();
    expect(() => selectedDatasetSourceResource(selection, [{...resource, [field]: "foreign"}])).toThrow();
  });
  it("rejects cross-artifact restoration, missing data and unverified admission", () => {
    const {selection, resource, artifact, context, promoted} = phononDosFixture(1);
    expect(restoredPhononDosPoint(context, {...artifact, id: "source:foreign", artifactId: "source:foreign"})).toBeNull();
    expect(() => bindDatasetSourceSelection(selection, resource, {...promoted, version: {...promoted.version, source_resource_refs_json: []}})).toThrow();
    resource.payload.projected_dos[1].values.pop();
    expect(() => selectedDatasetSourceResource(selection, [resource])).toThrow();
  });
});

describe("phonon mode Research handoff", () => {
  it("selects a companion's exact scope and retains original mode values through URL and admission", () => {
    const {payload, artifact, context, token, selection, resource, promoted} = phononFixture();
    expect(context.sourceScopeHash).toBe(hash);
    expect(context.primary).toMatchObject({datasetVersion: "phonon_v1", phononArtifactId: "source:phonon_resource", qPointId: "q:1", branchId: "branch:2"});
    expect(token.length).toBeLessThanOrEqual(2048);
    expect(restoredPhononBandPoint(context, artifact)).toMatchObject({qpointIndex: 1, branchIndex: 2});
    expect(restoredPhononBandPoint(context, {...artifact, id: "source:duplicate", artifactId: "source:duplicate"})).toBeNull();
    expect(selectedDatasetSourceResource(selection, [{...resource, objectId: "same_content"}, resource])).toBe(resource);
    const bound = bindDatasetSourceSelection(selection, resource, promoted);
    expect(bound.object_ref.version_id).toBe("admitted_phonon_version");
    expect(bound.viewer_id).toBe("scientific.phonon-band");
    expect(bound.semantic_locator).toMatchObject({qpoint_index: 1, branch_index: 2, frequency_thz: payload.branches[2].frequencies[1], path_distance: payload.qpoints[1].distance, q_a: payload.qpoints[1].coordinates[0]});
    expect(bound.evidence_locator).toEqual(bound.semantic_locator);
  });
  it.each(["project", "dataset", "sample", "qpoint", "branch", "checksum"])("rejects mismatched %s route identity", field => {
    const {context, token} = phononFixture();
    const primary = {...context.primary!, ...(field === "qpoint" ? {qPointId: "q:-1"} : field === "branch" ? {branchId: null} : field === "checksum" ? {artifactChecksum: "c".repeat(64)} : {})};
    const next = ["qpoint", "branch", "checksum"].includes(field) ? encodeWorkspaceSelectionUrl({...context, primary}) : token;
    expect(() => datasetSourceSelection(field === "project" ? "foreign" : "project_1", field === "dataset" ? "foreign" : "dataset_selected", next, field === "sample" ? "row_1" : undefined)).toThrow();
  });
  it.each(["objectId", "objectHash", "versionId", "objectType"])("rejects changed resource %s", field => {
    const {selection, resource} = phononFixture();
    expect(() => selectedDatasetSourceResource(selection, [{...resource, [field]: "foreign"}])).toThrow();
    expect(() => selectedDatasetSourceResource(selection, [resource, resource])).toThrow();
  });
  it("rejects nonexistent mode values and unverified admission provenance", () => {
    const {selection, resource, payload, workspace, artifact, promoted} = phononFixture();
    expect(selectPhononBandPoint(workspace, artifact, {qpointIndex: 999, branchIndex: 2})).toBeNull();
    payload.branches[2].frequencies.pop();
    expect(() => selectedDatasetSourceResource(selection, [resource])).toThrow();
    const valid = phononFixture();
    expect(() => bindDatasetSourceSelection(valid.selection, valid.resource, {...promoted, version: {...promoted.version, source_resource_refs_json: []}})).toThrow();
  });
});

describe("electronic source Research handoff", () => {
  it.each(["band", "dos"] as const)("binds %s to its exact resource, spin and admitted version", kind => {
    const { selection, resource, promoted } = electronicFixture(kind);
    expect(selectedDatasetSourceResource(selection, [{ ...resource, objectId: "first" }, resource])).toBe(resource);
    const bound = bindDatasetSourceSelection(selection, resource, promoted);
    expect(bound.object_ref.version_id).toBe("exact_version");
    expect(bound.semantic_locator).toMatchObject({ spin_channel_id: "down", energy_reference: "source_absolute", energy_ev: kind === "band" ? 2 : -0.25 });
    expect(bound.semantic_locator).toMatchObject(kind === "band" ? { band_id: "b1", kpoint_id: "k1", kpoint_index: 1 } : { dos_channel_id: "total", channel_kind: "total", energy_point_index: 1, dos_value: 2 });
  });
  it("distinguishes a projection from a total channel with the same name and spin", () => {
    const { selection, resource, promoted } = electronicFixture("dos", true);
    expect(bindDatasetSourceSelection(selection, resource, promoted).semantic_locator).toMatchObject({ channel_kind: "projection", projection_kind: "orbital", dos_value: 0.2 });
  });
  it.each(["project", "dataset", "sample", "job", "checksum", "point"])("rejects mismatched route %s", field => {
    const { context, token } = electronicFixture("dos");
    const changed = field === "job" ? { jobId: "job_foreign" } : field === "checksum" ? { artifactChecksum: "b".repeat(64) } : field === "point" ? { energyPointId: "source-dos-point:foreign:1" } : {};
    const next = Object.keys(changed).length ? encodeWorkspaceSelectionUrl({ ...context, primary: { ...context.primary!, ...changed } }) : token;
    expect(() => datasetSourceSelection(field === "project" ? "foreign" : "project_1", field === "dataset" ? "foreign" : "dataset_selected", next, field === "sample" ? "row-1" : undefined)).toThrow();
  });
  it.each(["objectId", "datasetId", "objectHash", "versionId", "objectType"])("rejects changed source %s", field => {
    const { selection, resource } = electronicFixture("band");
    expect(() => selectedDatasetSourceResource(selection, [{ ...resource, [field]: "foreign" }])).toThrow();
  });
  it.each(["band", "dos"] as const)("rejects missing, duplicated or truncated %s source values", kind => {
    const { selection, resource, source } = electronicFixture(kind);
    expect(() => selectedDatasetSourceResource(selection, [])).toThrow();
    expect(() => selectedDatasetSourceResource(selection, [resource, resource])).toThrow();
    if (kind === "band") { source.bands[1].energiesEv = [1]; } else { source.totalDos[1].values = [1]; }
    expect(() => selectedDatasetSourceResource(selection, [resource])).toThrow();
  });
  it.each(["id", "semantic_hash", "scientific_object_id", "source_resource_refs_json"])("rejects a mismatched admitted %s", field => {
    const { selection, resource, promoted } = electronicFixture("dos");
    expect(() => bindDatasetSourceSelection(selection, resource, { ...promoted, version: { ...promoted.version, [field]: field === "id" ? "" : "foreign" } })).toThrow();
  });
});
