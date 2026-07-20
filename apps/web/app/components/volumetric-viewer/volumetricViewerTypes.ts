export type VolumeVector3 = readonly [number, number, number];
export type VolumeMatrix3 = readonly [VolumeVector3, VolumeVector3, VolumeVector3];

export type VolumetricArtifact = Readonly<{
  id?: string;
  artifactId?: string;
  jobId?: string;
  type?: string;
  name?: string;
  sizeBytes?: number;
  contentType?: string;
  sha256?: string | null;
  contentHash?: string;
  content?: unknown;
  payload?: unknown;
  metadata?: Record<string, unknown>;
}>;

export type ValidatedVolumetricGrid = Readonly<{
  schemaVersion: "phase10j.volumetric_grid.v1";
  gridId: string;
  contentHash: string;
  shape: readonly [number, number, number];
  origin: VolumeVector3;
  stepMatrix: VolumeMatrix3;
  sampleLocation: "node" | "cell_center";
  boundaryConditions: readonly ["periodic" | "non_periodic", "periodic" | "non_periodic", "periodic" | "non_periodic"];
  endpointPolicy: "excluded" | "included" | "not_applicable";
  periodic: boolean;
  structureBinding: Readonly<{
    structureSha256: string;
    latticeSha256: string;
    latticeMatrix: VolumeMatrix3;
  }> | null;
}>;

export type ValidatedVolumetricPayload = Readonly<{
  schemaVersion: "phase10j.volumetric_payload.v1";
  payloadId: string;
  encoding: "inline_json" | "raw_binary" | "gzip_binary" | "chunked_binary";
  dtype: "float32" | "float64";
  gridShape: readonly [number, number, number];
  valueCount: number;
  uncompressedBytes: number;
  compressedBytes: number;
  logicalSha256: string;
  storageSha256: string;
  artifactName: string | null;
  inlineValues: readonly number[] | null;
  chunks: readonly ValidatedVolumetricChunk[];
}>;

export type ValidatedVolumetricChunk = Readonly<{
  chunkId: string;
  iStart: number;
  iEnd: number;
  artifactName: string;
  encoding: "raw_binary" | "gzip_binary";
  mediaType: string;
  uncompressedBytes: number;
  compressedBytes: number;
  logicalSha256: string;
  storageSha256: string;
}>;

export type ValidatedVolumetricField = Readonly<{
  schemaVersion: "phase10j.volumetric_field.v1";
  fieldId: string;
  fieldName: string;
  gridId: string;
  payloadId: string;
  quantity: string;
  valueKind: "real" | "complex";
  fieldRank: "scalar" | "vector";
  storedComponentCount: number;
  unit: string;
  minimum: number;
  maximum: number;
  mean: number;
  integral: number;
  warnings: readonly string[];
  contentHash: string;
}>;

export type VolumetricFieldCompatibility = Readonly<{
  field: ValidatedVolumetricField;
  payload: ValidatedVolumetricPayload;
  supported: boolean;
  reasons: readonly string[];
}>;

export type ValidatedVolumetricBundle = Readonly<{
  datasetId: string;
  datasetContentHash: string;
  sourceFormat: string;
  grid: ValidatedVolumetricGrid;
  fields: readonly VolumetricFieldCompatibility[];
  warnings: readonly string[];
  manifestContentHash: string;
  artifactNames: readonly string[];
}>;

export type VolumetricOverlayAtom = Readonly<{
  siteIndex: number;
  species: string;
  position: VolumeVector3;
  radius: number;
  color: string;
}>;

export type VolumetricStructureOverlay = Readonly<{
  kind: "periodic_viewer_scene" | "non_periodic_atom_context";
  atoms: readonly VolumetricOverlayAtom[];
  bonds: readonly Readonly<{ start: VolumeVector3; end: VolumeVector3; id: string }>[];
  lattice: VolumeMatrix3 | null;
  unavailableReason: string | null;
}>;

export type VolumetricValidationResult =
  | Readonly<{ ok: true; bundle: ValidatedVolumetricBundle }>
  | Readonly<{ ok: false; code: VolumetricViewerErrorCode; errors: readonly string[] }>;

export const VOLUMETRIC_BROWSER_CAPS = Object.freeze({
  maximumPayloadBytes: 16_777_216,
  maximumVoxelsDesktop: 262_144,
  maximumVoxelsMobile: 131_072,
  maximumHaloValues: 274_625,
  maximumLayers: 4,
  maximumVerticesPerLayer: 400_000,
  maximumTrianglesPerLayer: 300_000,
  maximumTotalVertices: 800_000,
  maximumTotalTriangles: 600_000,
  maximumMeshBytes: 48_000_000,
  maximumGpuBytes: 64_000_000,
  maximumWorkerMessages: 64,
  maximumRequestsPerSecond: 8,
  maximumSupercellReplicas: 8,
  maximumExportDimension: 4096,
  maximumExportPixels: 16_777_216,
  maximumExtractionMs: 30_000,
} as const);

export type VolumetricViewerErrorCode =
  | "VOLUME_VIEWER_ARTIFACTS_MISSING"
  | "VOLUME_VIEWER_CONTRACT_INVALID"
  | "VOLUME_VIEWER_FIELD_UNSUPPORTED"
  | "VOLUME_VIEWER_BROWSER_CAP_EXCEEDED"
  | "VOLUME_VIEWER_PAYLOAD_LOAD_FAILED"
  | "VOLUME_VIEWER_PAYLOAD_BYTE_MISMATCH"
  | "VOLUME_VIEWER_PAYLOAD_HASH_MISMATCH"
  | "VOLUME_VIEWER_DECOMPRESSION_FAILED"
  | "VOLUME_VIEWER_WORKER_UNAVAILABLE"
  | "VOLUME_VIEWER_WORKER_FAILED"
  | "VOLUME_VIEWER_EXTRACTION_CANCELLED"
  | "VOLUME_VIEWER_EXTRACTION_STALE"
  | "VOLUME_VIEWER_MESH_CAP_EXCEEDED"
  | "VOLUME_VIEWER_WEBGL_UNSUPPORTED"
  | "VOLUME_VIEWER_RENDERER_FAILED"
  | "VOLUME_VIEWER_CONTEXT_LOST"
  | "VOLUME_VIEWER_EMPTY_SURFACE";

export class VolumetricViewerError extends Error {
  constructor(readonly code: VolumetricViewerErrorCode, message: string) {
    super(message);
    this.name = "VolumetricViewerError";
  }
}

export type IsosurfaceLayerRequest = Readonly<{
  layerId: string;
  isovalue: number;
  sign: "positive" | "negative" | "neutral";
}>;

export type IsosurfaceMesh = Readonly<{
  layerId: string;
  isovalue: number;
  positions: Float32Array;
  normals: Float32Array;
  indices: Uint32Array;
  vertexCount: number;
  triangleCount: number;
  boundingBox: Readonly<{ minimum: VolumeVector3; maximum: VolumeVector3 }>;
  meshHash: string;
  warnings: readonly string[];
}>;

export type IsosurfaceExtractionMetrics = Readonly<{
  requestId: number;
  voxelCount: number;
  logicalCubeCount: number;
  periodicBoundaryCubes: number;
  candidateTetrahedra: number;
  vertices: number;
  triangles: number;
  degenerateTrianglesRejected: number;
  extractionMs: number;
  normalMs: number;
  weldingMs: number;
  transferBytes: number;
  peakWorkingBytesEstimate: number;
}>;

export type IsosurfaceWorkerRequest = Readonly<{
  type: "extract";
  requestId: number;
  fieldId: string;
  fieldHash: string;
  grid: ValidatedVolumetricGrid;
  dtype: "float32" | "float64";
  fieldBuffer: ArrayBuffer;
  layers: readonly IsosurfaceLayerRequest[];
  caps: Readonly<{
    maximumVerticesPerLayer: number;
    maximumTrianglesPerLayer: number;
    maximumTotalVertices: number;
    maximumTotalTriangles: number;
    maximumExtractionMs: number;
  }>;
}>;

export type IsosurfaceWorkerResponse =
  | Readonly<{ type: "success"; requestId: number; meshes: readonly IsosurfaceMesh[]; metrics: IsosurfaceExtractionMetrics; warnings: readonly string[] }>
  | Readonly<{ type: "failure"; requestId: number; code: VolumetricViewerErrorCode; message: string }>;

export type DecodedVolumetricField = Readonly<{
  field: ValidatedVolumetricField;
  payload: ValidatedVolumetricPayload;
  buffer: ArrayBuffer;
  byteLength: number;
  fetchMs: number;
  decompressionMs: number;
  hashValidationMs: number;
}>;

export type VolumetricSurfacePick = Readonly<{
  fieldId: string;
  layerId: string;
  isovalue: number;
  triangleIndex: number;
  cartesianPosition: VolumeVector3;
  interpolatedFieldValue: number;
  meshHash: string;
}>;

export type VolumetricRendererSnapshot = Readonly<{
  state: "rendered" | "context_lost" | "disposed";
  canvasCount: number;
  contextCount: number;
  vertexCount: number;
  triangleCount: number;
  layerCount: number;
  drawCalls: number;
  geometries: number;
  materials: number;
  cameraProjection: "perspective" | "orthographic";
  clippingEnabled: boolean;
  surfaceVisible: boolean;
  structureVisible: boolean;
}>;

export type VolumetricRendererEngine = Readonly<{
  setSurfaceVisible: (visible: boolean) => void;
  setLayerVisible: (layerId: string, visible: boolean) => void;
  setStructureVisible: (visible: boolean) => void;
  setCellVisible: (visible: boolean) => void;
  setOpacity: (opacity: number) => void;
  setProjection: (projection: "perspective" | "orthographic") => void;
  setClipping: (enabled: boolean, axis: 0|1|2, offset: number) => void;
  resetCamera: () => void;
  fitSurface: () => void;
  fitStructure: () => void;
  setSelection: (pick: VolumetricSurfacePick | null) => void;
  snapshot: () => VolumetricRendererSnapshot;
  render: () => void;
  exportPng: (width: number, height: number, pixelRatio: number) => Promise<Blob>;
  dispose: () => void;
}>;
