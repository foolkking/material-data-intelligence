export type BZVector3 = readonly [number, number, number];

export type BZVertex = Readonly<{
  id: string;
  orderIndex: number;
  cartesian: BZVector3;
  fractional: BZVector3;
  incidentFaceIds: readonly string[];
}>;

export type BZEdge = Readonly<{
  id: string;
  orderIndex: number;
  vertexIds: readonly [string, string];
  length: number;
  incidentFaceIds: readonly string[];
}>;

export type BZFace = Readonly<{
  id: string;
  orderIndex: number;
  vertexIds: readonly string[];
  edgeIds: readonly string[];
  area: number;
  centroid: BZVector3;
  outwardNormal: BZVector3;
  generatorHkl: readonly [number, number, number];
  generatorCartesian: BZVector3;
  planeOffset: number;
  triangleVertexIndices: readonly number[];
}>;

export type BZPoint = Readonly<{
  id: string;
  labelKey: string;
  displayLabel: string;
  aliases: readonly string[];
  fractional: BZVector3;
  cartesian: BZVector3;
  incidentSegmentIds: readonly string[];
}>;

export type BZSegment = Readonly<{
  id: string;
  variantId: string;
  orderIndex: number;
  startPointId: string;
  endPointId: string;
  startLabelKey: string;
  endLabelKey: string;
  start: BZVector3;
  end: BZVector3;
  length: number;
  discontinuityBefore: boolean;
  discontinuityAfter: boolean;
}>;

export type BZPathVariant = Readonly<{
  id: string;
  description: string;
  selected: boolean;
  segmentIds: readonly string[];
}>;

export type BZScene = Readonly<{
  structureIdentity: string;
  packageId: string;
  reciprocalHash: string;
  zoneHash: string;
  kpathHash: string | null;
  convention: "physics_2pi";
  units: "angstrom^-1";
  reciprocalMatrix: readonly [BZVector3, BZVector3, BZVector3];
  visualScale: number;
  vertices: readonly BZVertex[];
  edges: readonly BZEdge[];
  faces: readonly BZFace[];
  points: readonly BZPoint[];
  segments: readonly BZSegment[];
  variants: readonly BZPathVariant[];
  selectedVariantId: string | null;
  discontinuityIds: readonly string[];
  volume: number;
  surfaceArea: number;
  provider: Readonly<{ name: string; version: string; pathConvention: string; timeReversal: boolean }>;
  warnings: readonly string[];
}>;

export type BZSelection =
  | Readonly<{ kind: "point"; id: string }>
  | Readonly<{ kind: "face"; id: string }>
  | Readonly<{ kind: "vertex"; id: string }>
  | Readonly<{ kind: "segment"; id: string; variantId: string }>;

export type BZProjection = "perspective" | "orthographic";
export type BZCameraPreset = "isometric" | "b1" | "b2" | "b3";
export type BZRendererState = "ready" | "initializing" | "rendered" | "unsupported" | "invalid" | "over_cap" | "context_lost" | "renderer_failed" | "disposed";

export type BZVisibility = Readonly<{
  faces: boolean;
  edges: boolean;
  vertices: boolean;
  axes: boolean;
  points: boolean;
  labels: boolean;
  path: boolean;
}>;

export type BZRendererMetrics = Readonly<{
  artifactBytes: number;
  vertexCount: number;
  edgeCount: number;
  faceCount: number;
  triangleCount: number;
  pointCount: number;
  pathSegmentCount: number;
  visibleLabelCount: number;
  drawCalls: number;
  geometries: number;
  materials: number;
  textures: number;
  canvasCount: number;
  contextCount: number;
  mappingMs: number;
  initializationMs: number;
  firstFrameMs: number;
}>;

export type BZRendererSnapshot = Readonly<{
  state: BZRendererState;
  graphicsContext: "webgl2" | "webgl";
  rendererVersion: string;
  projection: BZProjection;
  cameraPosition: BZVector3;
  cameraTarget: BZVector3;
  cameraUp: BZVector3;
  selection: BZSelection | null;
  pointScreenPositions: readonly Readonly<{ id: string; x: number; y: number }>[];
  faceScreenPositions: readonly Readonly<{ id: string; x: number; y: number }>[];
  metrics: BZRendererMetrics;
}>;

export type BZExportRequest = Readonly<{
  width: number;
  height: number;
  pixelRatio: 1 | 2;
  background: "light" | "dark" | "transparent";
}>;

export type BZRendererEngine = Readonly<{
  resetCamera: () => void;
  fit: () => void;
  setCameraPreset: (preset: BZCameraPreset) => void;
  setProjection: (projection: BZProjection) => void;
  setVisibility: (visibility: BZVisibility) => void;
  setOpacity: (opacity: number) => void;
  setVariant: (variantId: string | null) => void;
  setSelection: (selection: BZSelection | null) => void;
  keyboardCamera: (action: "rotate_left" | "rotate_right" | "rotate_up" | "rotate_down" | "pan_left" | "pan_right" | "zoom_in" | "zoom_out") => void;
  exportPng: (request: BZExportRequest) => Promise<Blob>;
  snapshot: () => BZRendererSnapshot;
  dispose: () => void;
}>;

export type BZRendererEngineFactory = (args: Readonly<{
  container: HTMLElement;
  scene: BZScene;
  visibility: BZVisibility;
  opacity: number;
  projection: BZProjection;
  variantId: string | null;
  mappingMs: number;
  artifactBytes: number;
  onSelection: (selection: BZSelection | null) => void;
  onContextLost: () => void;
  onViewChange: () => void;
}>) => Promise<BZRendererEngine>;
