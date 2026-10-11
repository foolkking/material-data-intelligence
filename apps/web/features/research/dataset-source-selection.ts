import type { DatasetSourceResource, PromotedDatasetTable } from "../../app/lib/planner-api";
import type { Agent2ScientificSelection } from "../../app/lib/agent2-research-api";
import type { WorkspaceSelectionContext } from "../../app/lib/workspace-api";
import { decodeWorkspaceSelectionUrl } from "../../shared/workspace/workspace-selection-contract";
import { electronicSpinLabel } from "../../scientific-viewers/workspace/electronic-plot";
import { phononBandPoint, phononDosPoint } from "../../scientific-viewers/phonon-shared/phonon-selection";
import { parseTrajectoryPoint, trajectoryPointLabel, trajectorySemanticLocator } from "../../scientific-viewers/trajectory-viewer/trajectory-selection";
import { sourceVolumetricChannel } from "../../scientific-viewers/volumetric-viewer/volumetric-selection";
import { densityFieldName } from "../../scientific-viewers/volumetric-viewer/density-display";

export class DatasetSourceSelectionError extends Error {
  constructor(message = "所选原子与当前结构来源不一致。请返回数据重新选择；问题已保留，尚未提交分析。") { super(message); }
}

export type DatasetStructureSelection = Readonly<{
  family: "structure";
  context: WorkspaceSelectionContext;
  siteId: string;
  siteIndex: number;
  species: string;
  imageOffset: readonly number[];
  label: string;
}>;

// A sample's optional return token is legacy navigation context. A structure
// token is the requested research subject and must never silently disappear.
export function datasetStructureSelection(projectId: string, datasetId?: string, token?: string, sampleRef?: string): DatasetStructureSelection | null {
  if (!token) return null;
  let context: WorkspaceSelectionContext;
  try { context = decodeWorkspaceSelectionUrl(token); }
  catch { if (sampleRef) return null; throw new DatasetSourceSelectionError(); }
  const primary = context.primary;
  if (sampleRef && primary?.kind !== "PERIODIC_SITE") return null;
  if (!datasetId || sampleRef || context.cleared || context.compatibility !== "EXACT" || context.secondary.length ||
      primary?.kind !== "PERIODIC_SITE" || primary.projectId !== projectId || primary.datasetId !== datasetId) throw new DatasetSourceSelectionError();
  const match = /^([A-Z][a-z]?)-(0|[1-9]\d*):(-?\d+)\.(-?\d+)\.(-?\d+)$/.exec(primary.siteId || "");
  const siteIndex = Number(match?.[2]);
  const imageOffset = match?.slice(3).map(Number) || [];
  if (!match || !Number.isSafeInteger(siteIndex) || imageOffset.some(value => !Number.isSafeInteger(value) || Math.abs(value) > 3)) throw new DatasetSourceSelectionError();
  return { family: "structure", context, siteId: primary.siteId!, siteIndex, species: match[1], imageOffset,
    label: `${match[1]} · 位点 ${siteIndex}${imageOffset.some(value => value !== 0) ? ` · 周期位置 [${imageOffset.join(", ")}]` : ""}` };
}

export type DatasetElectronicSelection = Readonly<{
  family: "electronic";
  context: WorkspaceSelectionContext;
  resourceId: string;
  label: string;
}>;
export type DatasetPhononSelection = Readonly<{ family: "phonon"; context: WorkspaceSelectionContext; resourceId: string; label: string }>;
export type DatasetTrajectorySelection = Readonly<{ family: "trajectory"; context: WorkspaceSelectionContext; resourceId: string; label: string }>;
export type DatasetVolumetricSelection = Readonly<{ family: "volumetric"; context: WorkspaceSelectionContext; resourceId: string; label: string }>;
export type DatasetSourceSelection = DatasetStructureSelection | DatasetElectronicSelection | DatasetPhononSelection | DatasetTrajectorySelection | DatasetVolumetricSelection;

export function datasetSourceSelection(projectId: string, datasetId?: string, token?: string, sampleRef?: string): DatasetSourceSelection | null {
  if (!token) return null;
  let context: WorkspaceSelectionContext;
  try { context = decodeWorkspaceSelectionUrl(token); }
  catch { return datasetStructureSelection(projectId, datasetId, token, sampleRef); }
  const primary = context.primary;
  if (primary?.kind === "VOLUMETRIC_FIELD") {
    const artifact = /^source:(.+):volumetric-dataset$/.exec(primary.artifactId || "");
    const channel = /^channel:(0|[1-9]\d*)$/.exec(primary.fieldId || "");
    if (!datasetId || sampleRef || !artifact || !channel || !Number.isSafeInteger(Number(channel[1])) ||
        context.cleared || context.compatibility !== "EXACT" || context.secondary.length ||
        primary.projectId !== projectId || primary.datasetId !== datasetId || primary.artifactChecksum !== context.sourceScopeHash) throw volumetricSelectionError();
    return {family:"volumetric",context,resourceId:artifact[1],label:`体数据字段 ${Number(channel[1]) + 1}`};
  }
  if (primary?.kind === "TRAJECTORY_FRAME" || primary?.kind === "TRAJECTORY_ATOM") {
    const point = parseTrajectoryPoint(primary.frameId, primary.atomId);
    if (!point || !datasetId || sampleRef || context.cleared || context.compatibility !== "EXACT" || context.secondary.length ||
        primary.projectId !== projectId || primary.datasetId !== datasetId || !primary.artifactId?.startsWith("source:") ||
        !primary.trajectoryId || primary.artifactChecksum !== context.sourceScopeHash || (primary.kind === "TRAJECTORY_ATOM") !== Boolean(point.atom)) throw trajectorySelectionError();
    return {family:"trajectory",context,resourceId:primary.artifactId.slice("source:".length),label:trajectoryPointLabel(point)};
  }
  if (primary?.kind === "PHONON_Q_POINT" || primary?.kind === "PHONON_DOS_POINT") {
    if (!datasetId || sampleRef || context.cleared || context.compatibility !== "EXACT" || context.secondary.length ||
        primary.projectId !== projectId || primary.datasetId !== datasetId || !primary.phononArtifactId?.startsWith("source:") ||
        primary.artifactChecksum !== context.sourceScopeHash) throw phononSelectionError();
    if (primary.kind === "PHONON_DOS_POINT") {
      if (!/^frequency:(0|[1-9]\d*)$/.test(primary.frequencyPointId || "") || !/^(total|projection:(0|[1-9]\d*))$/.test(primary.dosChannelId || "")) throw phononSelectionError();
      return { family: "phonon", context, resourceId: primary.phononArtifactId.slice("source:".length),
        label: `${primary.dosChannelId === "total" ? "总态密度" : `投影 ${primary.dosChannelId!.slice(11)}`} · 频率点 ${primary.frequencyPointId!.slice(10)}` };
    }
    if (!/^q:(0|[1-9]\d*)$/.test(primary.qPointId || "") || !/^branch:(0|[1-9]\d*)$/.test(primary.branchId || "")) throw phononSelectionError();
    return { family: "phonon", context, resourceId: primary.phononArtifactId.slice("source:".length),
      label: `声子 q 点 ${primary.qPointId!.slice(2)} · 分支 ${primary.branchId!.slice(7)}` };
  }
  if (!primary?.kind.startsWith("ELECTRONIC_")) return datasetStructureSelection(projectId, datasetId, token, sampleRef);
  if (!datasetId || sampleRef || context.cleared || context.compatibility !== "EXACT" || context.secondary.length ||
      !["ELECTRONIC_BAND_STATE", "ELECTRONIC_DOS_POINT"].includes(primary.kind) || primary.projectId !== projectId || primary.datasetId !== datasetId ||
      primary.jobId !== "source-view" || !primary.artifactId?.startsWith("source:") || primary.artifactChecksum !== context.sourceScopeHash) throw electronicSelectionError();
  const resourceId = primary.artifactId.slice("source:".length);
  const spin = electronicSpinLabel(primary.spinChannelId || "none");
  const label = primary.kind === "ELECTRONIC_BAND_STATE" ? `能带 ${primary.bandId} · k 点 ${primary.kpointId} · ${spin}`
    : `通道 ${primary.dosChannelId} · 能量点 ${energyPointIndex(primary.energyPointId, resourceId) + 1} · ${spin}`;
  return { family: "electronic", context, resourceId, label };
}

export function selectedDatasetSourceResource(selection: DatasetSourceSelection, resources: readonly DatasetSourceResource[]): DatasetSourceResource {
  if (selection.family === "structure") return selectedStructureResource(selection, resources);
  const primary = selection.context.primary!;
  const matches = resources.filter(resource => resource.objectId === selection.resourceId);
  const resource = matches[0];
  if (matches.length !== 1 || resource.datasetId !== primary.datasetId || !resource.objectHash ||
      resource.objectHash !== selection.context.sourceScopeHash || (resource.versionId || resource.objectHash) !== primary.datasetVersion) throw selection.family === "volumetric" ? volumetricSelectionError() : selection.family === "trajectory" ? trajectorySelectionError() : selection.family === "phonon" ? phononSelectionError() : electronicSelectionError();
  if (selection.family === "volumetric") volumetricLocator(selection, resource); else if (selection.family === "trajectory") trajectoryLocator(selection, resource); else if (selection.family === "phonon") phononLocator(selection, resource); else electronicLocator(selection, resource);
  return resource;
}

export function bindDatasetSourceSelection(selection: DatasetSourceSelection, resource: DatasetSourceResource, promoted: PromotedDatasetTable): Agent2ScientificSelection {
  if (selection.family === "structure") return bindStructureSelection(selection, resource, promoted);
  selectedDatasetSourceResource(selection, [resource]);
  const projectId = selection.context.primary!.projectId;
  const { object, version } = promoted;
  const objectType = selection.family === "volumetric" ? "volumetric.field" : selection.family === "trajectory" ? "trajectory.atomic" : selection.family === "phonon" ? (selection.context.primary!.kind === "PHONON_DOS_POINT" ? "phonon.dos" : "phonon.band_structure") : resource.objectType === "ElectronicBand" ? "electronic.band_structure" : "electronic.dos";
  let refs = version?.source_resource_refs_json;
  if (typeof refs === "string") { try { refs = JSON.parse(refs); } catch { refs = null; } }
  if (!object?.id || !version?.id || object.project_id !== projectId || object.object_type !== objectType ||
      version.scientific_object_id !== object.id || version.semantic_hash !== resource.objectHash ||
      !Array.isArray(refs) || !refs.some(value => { const ref = record(value); return ref?.project_id === projectId && ref.dataset_id === resource.datasetId && ref.resource_id === resource.objectId; })) {
    throw new DatasetSourceSelectionError("暂时无法确认所选科学数据的正式版本。请重新读取来源后再试；问题已保留，尚未提交分析。");
  }
  const locator = selection.family === "volumetric" ? volumetricLocator(selection, resource) : selection.family === "trajectory" ? trajectoryLocator(selection, resource) : selection.family === "phonon" ? phononLocator(selection, resource) : electronicLocator(selection, resource);
  return { contract_version: "1.0", object_ref: { project_id: projectId, object_id: object.id, version_id: version.id, object_type: objectType, display_name: object.display_name },
    viewer_id: selection.family === "volumetric" ? "scientific.volumetric" : selection.family === "trajectory" ? "scientific.trajectory" : selection.family === "phonon" ? (objectType === "phonon.dos" ? "scientific.phonon-dos" : "scientific.phonon-band") : resource.objectType === "ElectronicBand" ? "scientific.band-structure" : "scientific.density-of-states", selection_type: selection.context.primary!.kind,
    semantic_locator: locator, display_label: selection.family === "volumetric" ? volumetricLabel(selection, resource) : selection.label, evidence_locator: locator };
}

function volumetricLocator(selection: DatasetVolumetricSelection, resource: DatasetSourceResource) {
  const fieldId = selection.context.primary!.fieldId || "";
  const source = resource.objectType === "VolumetricData" ? sourceVolumetricChannel(resource.payload, fieldId) : null;
  if (!source) throw volumetricSelectionError();
  return {field_id:fieldId,source_channel_index:source.index,field_locator:`/channels/${source.index}`};
}
function volumetricLabel(selection: DatasetVolumetricSelection, resource: DatasetSourceResource) {
  const {channel} = sourceVolumetricChannel(resource.payload, selection.context.primary!.fieldId || "")!;
  return `${densityFieldName({fieldName:String(channel.name || selection.label),quantity:String(channel.quantity || "generic_scalar"),spin:null})} · ${selection.label}`;
}
function volumetricSelectionError() { return new DatasetSourceSelectionError("所选体数据字段与当前来源不一致。请返回数据重新选择；问题已保留，尚未提交分析。"); }

function trajectoryLocator(selection: DatasetTrajectorySelection, resource: DatasetSourceResource) {
  const primary = selection.context.primary!;
  const locator = resource.objectType === "Trajectory" ? trajectorySemanticLocator(resource.payload, primary.frameId, primary.atomId, primary.trajectoryId) : null;
  if (!locator) throw trajectorySelectionError();
  return locator;
}
function trajectorySelectionError() { return new DatasetSourceSelectionError("所选轨迹帧或原子与当前来源不一致。请返回数据重新选择；问题已保留，尚未提交分析。"); }

function phononLocator(selection: DatasetPhononSelection, resource: DatasetSourceResource): Record<string, string | number> {
  const primary = selection.context.primary!;
  if (primary.kind === "PHONON_DOS_POINT") {
    const point = resource.objectType === "PhononDos" ? phononDosPoint(resource.payload, primary.frequencyPointId, primary.dosChannelId) : null;
    if (!point) throw phononSelectionError();
    const projection = point.projection;
    return { frequency_point_id: primary.frequencyPointId!, dos_channel_id: primary.dosChannelId!, frequency_point_index: point.frequencyIndex,
      frequency_thz: point.frequency, dos_value: point.density, density_unit: "modes_per_terahertz", channel_kind: projection ? "projection" : "total",
      ...(projection ? { projection_index: projection.projection_index, projection_type: projection.projection_type, species: projection.species,
        ...(projection.atom_index !== null ? { atom_index: projection.atom_index } : {}) } : {}) };
  }
  const point = resource.objectType === "PhononBand" ? phononBandPoint(resource.payload, primary.qPointId, primary.branchId) : null;
  if (!point) throw phononSelectionError();
  return { q_point_id: primary.qPointId!, branch_id: primary.branchId!, qpoint_index: point.qpointIndex, branch_index: point.branchIndex,
    frequency_thz: point.frequency, path_distance: point.distance, q_a: point.coordinates[0], q_b: point.coordinates[1], q_c: point.coordinates[2] };
}
function phononSelectionError() { return new DatasetSourceSelectionError("所选声子数据与当前来源不一致。请返回数据重新选择；问题已保留，尚未提交分析。"); }

function electronicLocator(selection: DatasetElectronicSelection, resource: DatasetSourceResource): Record<string, string | number> {
  const primary = selection.context.primary!, source = record(resource.payload);
  const isBand = primary.kind === "ELECTRONIC_BAND_STATE";
  if (resource.objectType !== (isBand ? "ElectronicBand" : "ElectronicDos") || source?.schemaVersion !== (isBand ? "phase10n5.electronic_band_resource.v1" : "phase10n5.electronic_dos_resource.v1") ||
      source.resourceId !== primary.electronicResourceId || source.energyUnit !== "eV") throw electronicSelectionError();
  const common = { spin_channel_id: primary.spinChannelId!, energy_unit: "eV", energy_reference: String(source.energyReference || "unknown") };
  if (isBand) {
    const points = Array.isArray(source.kpoints) ? source.kpoints.map(record) : [];
    const indices = points.flatMap((point, index) => point?.kpointId === primary.kpointId ? [index] : []);
    const bands = Array.isArray(source.bands) ? source.bands.map(record).filter(band => band?.bandId === primary.bandId && band?.spinChannel === primary.spinChannelId) : [];
    const index = indices[0], energies = bands[0]?.energiesEv;
    if (indices.length !== 1 || bands.length !== 1 || !Array.isArray(energies) || energies.length !== points.length || !finite(energies[index]) ||
        primary.bandStateId !== `source-state:${resource.objectId}:${primary.bandId}:${index}`) throw electronicSelectionError();
    return { ...common, band_id: primary.bandId!, kpoint_id: primary.kpointId!, kpoint_index: index, energy_ev: energies[index] };
  }
  const index = energyPointIndex(primary.energyPointId, resource.objectId);
  const energies = source.energiesEv;
  const projections = Boolean(primary.projectionId);
  const sourceChannels = projections ? source.projections : source.totalDos;
  const channels = Array.isArray(sourceChannels) ? sourceChannels.map(record).filter(channel => channel?.channelId === primary.dosChannelId && channel?.spinChannel === primary.spinChannelId) : [];
  const values = channels[0]?.values;
  if (!Array.isArray(energies) || channels.length !== 1 || !Array.isArray(values) || values.length !== energies.length || !finite(energies[index]) || !finite(values[index]) ||
      (projections && primary.projectionId !== `source-dos:${resource.objectId}:projection:${primary.spinChannelId}:${primary.dosChannelId}`)) throw electronicSelectionError();
  return { ...common, dos_channel_id: primary.dosChannelId!, channel_kind: projections ? "projection" : "total", energy_point_index: index, energy_ev: energies[index], dos_value: values[index],
    ...(typeof source.dosUnitSemantic === "string" ? { dos_unit_semantic: source.dosUnitSemantic } : {}),
    ...(projections && typeof channels[0]?.projectionKind === "string" ? { projection_kind: channels[0].projectionKind } : {}) };
}
function energyPointIndex(id: string | null, resourceId: string): number {
  const prefix = `source-dos-point:${resourceId}:`;
  const suffix = id?.startsWith(prefix) ? id.slice(prefix.length) : "";
  const index = Number(suffix);
  if (!/^(0|[1-9]\d*)$/.test(suffix) || !Number.isSafeInteger(index)) throw electronicSelectionError();
  return index;
}
function finite(value: unknown): value is number { return typeof value === "number" && Number.isFinite(value); }
function electronicSelectionError(message = "所选电子数据与当前来源不一致。请返回数据重新选择；问题已保留，尚未提交分析。") { return new DatasetSourceSelectionError(message); }

export function selectedStructureResource(selection: DatasetStructureSelection, resources: readonly DatasetSourceResource[]): DatasetSourceResource {
  const primary = selection.context.primary!;
  const matches = resources.filter(resource => resource.objectId === primary.objectId);
  const resource = matches[0];
  if (matches.length !== 1 || resource.objectType !== "Structure" || resource.datasetId !== primary.datasetId ||
      !resource.objectHash || resource.objectHash !== selection.context.sourceScopeHash || resource.objectHash !== primary.structureId ||
      (resource.versionId || resource.objectHash) !== primary.datasetVersion) throw new DatasetSourceSelectionError();
  const source = record(resource.payload);
  const site = record(Array.isArray(source?.sites) ? source.sites[selection.siteIndex] : null);
  const species = Array.isArray(site?.species) ? site.species.map(record).find(value => value !== null) : null;
  const element = typeof species?.element === "string" ? species.element : typeof site?.label === "string" ? site.label.replace(/\d+$/u, "") : "";
  const lattice = record(source?.lattice)?.matrix;
  if (element !== selection.species || !finiteTriplet(site?.xyz) || !Array.isArray(lattice) || lattice.length !== 3 || !lattice.every(finiteTriplet)) throw new DatasetSourceSelectionError();
  return resource;
}

export function bindStructureSelection(selection: DatasetStructureSelection, resource: DatasetSourceResource, promoted: PromotedDatasetTable): Agent2ScientificSelection {
  const projectId = selection.context.primary!.projectId;
  const { object, version } = promoted;
  let refs = version?.source_resource_refs_json;
  if (typeof refs === "string") { try { refs = JSON.parse(refs); } catch { refs = null; } }
  if (!object?.id || !version?.id || object.project_id !== projectId || object.object_type !== "structure.crystal" ||
      version.scientific_object_id !== object.id || version.semantic_hash !== resource.objectHash ||
      !Array.isArray(refs) || !refs.some(value => { const ref = record(value); return ref?.project_id === projectId && ref.dataset_id === resource.datasetId && ref.resource_id === resource.objectId; })) {
    throw new DatasetSourceSelectionError("暂时无法确认所选结构的正式版本。请重新读取来源后再试；问题已保留，尚未提交分析。");
  }
  const locator = { site_id: selection.siteId, site_index: selection.siteIndex, species: selection.species,
    image_offset_a: selection.imageOffset[0], image_offset_b: selection.imageOffset[1], image_offset_c: selection.imageOffset[2] };
  return { contract_version: "1.0", object_ref: { project_id: projectId, object_id: object.id, version_id: version.id, object_type: object.object_type, display_name: object.display_name },
    viewer_id: "scientific.structure-3d", selection_type: "PERIODIC_SITE", semantic_locator: locator, display_label: selection.label, evidence_locator: locator };
}

function record(value: unknown): Record<string, unknown> | null { return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null; }
function finiteTriplet(value: unknown): value is number[] { return Array.isArray(value) && value.length === 3 && value.every(item => typeof item === "number" && Number.isFinite(item)); }
