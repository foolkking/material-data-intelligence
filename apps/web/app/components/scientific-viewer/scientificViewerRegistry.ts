export type ScientificViewerSupport = "PROFESSIONAL" | "SUPPORTED" | "FALLBACK" | "NOT_CURRENTLY_SUPPORTED";

export type ScientificViewerDescriptor = Readonly<{
  viewerId: string;
  viewerVersion: "1.0";
  scientificType: string;
  rendererKey: string;
  support: ScientificViewerSupport;
  interactionCapabilities: readonly string[];
  selectionCapabilities: readonly string[];
  maximumPayloadBytes: number;
  fallbackPolicy: "SCIENTIFIC_METADATA" | "SAFE_FILE_PREVIEW" | "AUTHORIZED_DOWNLOAD";
}>;

type ResolveInput = Readonly<{
  objectType: string;
  semanticRole?: string | null;
  schemaVersion?: string | null;
}>;

const MIB = 1024 * 1024;

const VIEWERS: readonly ScientificViewerDescriptor[] = Object.freeze([
  descriptor("materials.dataset", "scientific-table", ["sort", "filter", "inspect_units"], ["TABLE_ROW", "TABLE_COLUMN"], 8 * MIB),
  descriptor("structure.crystal", "structure-3d", ["rotate", "zoom", "reset", "inspect_cell"], ["STRUCTURE_SITE"], 8 * MIB),
  descriptor("trajectory.atomic", "trajectory", ["frame_navigation", "playback", "inspect_time"], ["TRAJECTORY_FRAME", "TRAJECTORY_ATOM"], 32 * MIB),
  descriptor("diffraction.xrd.experimental", "xrd", ["zoom", "inspect_series", "inspect_peaks"], ["XRD_PEAK"], 8 * MIB),
  descriptor("diffraction.xrd.theoretical", "xrd", ["zoom", "inspect_series", "inspect_peaks"], ["XRD_PEAK"], 8 * MIB),
  descriptor("analysis.rdf", "rdf", ["zoom", "inspect_curve", "inspect_validated_peaks"], ["RDF_RANGE", "RDF_PEAK"], 8 * MIB),
  descriptor("electronic.band_structure", "band-structure", ["zoom", "inspect_k_path", "inspect_energy"], ["BAND_POINT", "BAND_SEGMENT"], 16 * MIB),
  descriptor("electronic.dos", "density-of-states", ["zoom", "inspect_series", "inspect_energy"], ["DOS_SERIES", "ENERGY_INTERVAL"], 16 * MIB),
  descriptor("phonon.band_structure", "phonon-band", ["zoom", "inspect_q_path"], ["PHONON_Q_POINT", "PHONON_BRANCH"], 16 * MIB),
  descriptor("phonon.dos", "phonon-dos", ["zoom", "inspect_series"], ["PHONON_BRANCH", "ENERGY_INTERVAL"], 16 * MIB),
  descriptor("reciprocal.brillouin_zone", "brillouin-zone", ["rotate", "zoom", "inspect_path"], ["RECIPROCAL_POINT", "PATH_SEGMENT"], 8 * MIB),
  descriptor("volumetric.charge_density", "volumetric", ["isosurface", "slice", "inspect_field"], ["VOLUMETRIC_REGION"], 16 * MIB),
]);

const BY_TYPE = new Map(VIEWERS.map((item) => [item.scientificType, item]));

const LEGACY_TYPES: Record<string, string> = {
  DataFrame: "materials.dataset",
  Structure: "structure.crystal",
  Atoms: "structure.crystal",
  Trajectory: "trajectory.atomic",
  ElectronicBand: "electronic.band_structure",
  ElectronicDos: "electronic.dos",
  PhononBand: "phonon.band_structure",
  PhononDos: "phonon.dos",
  BrillouinZone: "reciprocal.brillouin_zone",
  PhononEigenvector: "phonon.band_structure",
  VolumetricData: "volumetric.charge_density",
};

export function resolveScientificViewer(input: ResolveInput): ScientificViewerDescriptor {
  const semantic = String(input.semanticRole || "").toLowerCase();
  const schema = String(input.schemaVersion || "").toLowerCase();
  if (semantic.includes("rdf") || schema.includes("rdf")) return BY_TYPE.get("analysis.rdf")!;
  if (semantic.includes("xrd") || schema.includes("xrd")) return BY_TYPE.get(semantic.includes("experimental") ? "diffraction.xrd.experimental" : "diffraction.xrd.theoretical")!;
  const scientificType = LEGACY_TYPES[input.objectType] || input.objectType;
  return BY_TYPE.get(scientificType) || Object.freeze({
    viewerId: "scientific.generic-safe-fallback",
    viewerVersion: "1.0",
    scientificType,
    rendererKey: "generic-safe-fallback",
    support: "FALLBACK",
    interactionCapabilities: ["inspect_metadata", "download"],
    selectionCapabilities: [],
    maximumPayloadBytes: 2 * MIB,
    fallbackPolicy: "SAFE_FILE_PREVIEW",
  });
}

export function listScientificViewerCapabilities(): readonly ScientificViewerDescriptor[] {
  return VIEWERS;
}

function descriptor(scientificType: string, rendererKey: string, interactions: string[], selections: string[], maximumPayloadBytes: number): ScientificViewerDescriptor {
  return Object.freeze({
    viewerId: `scientific.${rendererKey}`,
    viewerVersion: "1.0",
    scientificType,
    rendererKey,
    support: "PROFESSIONAL",
    interactionCapabilities: Object.freeze(interactions),
    selectionCapabilities: Object.freeze(selections),
    maximumPayloadBytes,
    fallbackPolicy: "SCIENTIFIC_METADATA",
  });
}
