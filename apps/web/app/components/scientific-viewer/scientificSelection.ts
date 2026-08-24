import type { WorkspaceSelectionContext } from "../../lib/workspace-api";

export type ScientificObjectVersionRef = Readonly<{
  projectId: string;
  objectId: string;
  versionId: string;
  objectType: string;
  displayName: string;
}>;

export type ScientificSelection = Readonly<{
  contractVersion: "1.0";
  sourceRef: ScientificObjectVersionRef;
  viewerId: string;
  selectionType: string;
  semanticLocator: Readonly<Record<string, string | number>>;
  displayLabel: string;
  evidenceLocator: string | null;
}>;

const INTERNAL_ID_PATTERN = /^[0-9a-f]{8}-[0-9a-f-]{27,}$/i;

export function scientificSelectionFromWorkspace(
  selection: WorkspaceSelectionContext,
  sourceRef: ScientificObjectVersionRef,
  viewerId: string,
): ScientificSelection | null {
  const primary = selection.primary;
  if (!primary) return null;
  const entries = Object.entries(primary).filter(([key, value]) => value !== null && value !== undefined && semanticField(key));
  const semanticLocator = Object.fromEntries(entries.map(([key, value]) => [key, String(value)]));
  return Object.freeze({
    contractVersion: "1.0",
    sourceRef: Object.freeze({ ...sourceRef }),
    viewerId,
    selectionType: primary.kind,
    semanticLocator: Object.freeze(semanticLocator),
    displayLabel: selectionDisplayLabel(primary.kind, semanticLocator),
    evidenceLocator: typeof primary.fieldLocator === "string" ? primary.fieldLocator : null,
  });
}

export function selectionToResearchObjectRef(selection: ScientificSelection) {
  return {
    object_id: selection.sourceRef.objectId,
    version_id: selection.sourceRef.versionId,
    project_id: selection.sourceRef.projectId,
    object_type: selection.sourceRef.objectType,
    display_name: selection.sourceRef.displayName,
  };
}

export function opaqueSelectionEnvelope(selections: readonly ScientificSelection[]) {
  return selections.map((selection, index) => ({
    candidate_id: `selection_${index + 1}`,
    selection_type: selection.selectionType,
    display_label: selection.displayLabel,
    viewer: selection.viewerId,
    semantic_locator: selection.semanticLocator,
  }));
}

export function providerEnvelopeContainsInternalIdentity(envelope: unknown): boolean {
  return scan(envelope);
}

function scan(value: unknown): boolean {
  if (typeof value === "string") return INTERNAL_ID_PATTERN.test(value) || /artifact[_-]?[0-9a-f-]{12,}/i.test(value);
  if (Array.isArray(value)) return value.some(scan);
  if (value && typeof value === "object") return Object.entries(value).some(([key, item]) => /objectId|versionId|artifactId|jobId|toolCallId/i.test(key) || scan(item));
  return false;
}

function semanticField(key: string): boolean {
  return /siteId|sampleRef|peakId|matchId|atomId|frameId|speciesPairId|rdfBinId|kpointId|bandId|energyPointId|qPointId|branchId|reciprocalPointId|segmentId|fieldId|regionId|fieldLocator/i.test(key);
}

function selectionDisplayLabel(kind: string, locator: Record<string, string>): string {
  const value = locator.siteId || locator.sampleRef || locator.peakId || locator.matchId || locator.atomId || locator.frameId || locator.rdfBinId || locator.kpointId || locator.bandId || locator.energyPointId || locator.qPointId || locator.branchId || locator.reciprocalPointId || locator.fieldId;
  const label = ({ PERIODIC_SITE: "结构位点", DATASET_SAMPLE: "数据样本", EXPERIMENTAL_XRD_PEAK: "实验 XRD 峰", THEORETICAL_XRD_PEAK: "理论 XRD 峰", XRD_MATCH: "匹配峰", TRAJECTORY_ATOM: "轨迹原子", TRAJECTORY_FRAME: "轨迹帧", TRAJECTORY_RDF_BIN: "RDF 区间", ELECTRONIC_KPOINT: "k 点", PHONON_Q_POINT: "声子 q 点", VOLUMETRIC_FIELD: "体数据区域" } as Record<string, string>)[kind] || "科学选择";
  return value ? `${label} · ${value}` : label;
}
