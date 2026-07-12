export type RenderVector3 = readonly [number, number, number];
export type ImageOffset = readonly [number, number, number];

export type PeriodicSiteRef = {
  readonly siteIndex: number;
  readonly imageOffset: ImageOffset;
};

export type RenderAtom = {
  readonly id: string;
  readonly siteIndex: number;
  readonly ref: PeriodicSiteRef;
  readonly species: string;
  readonly label: string;
  readonly element: string;
  readonly occupancy: number;
  readonly position: RenderVector3;
  readonly canonicalPosition: RenderVector3;
  readonly fractionalPosition: RenderVector3 | null;
  readonly radius: number;
  readonly color: string;
};

export type RenderBond = {
  readonly id: string;
  readonly fromSiteIndex: number;
  readonly toSiteIndex: number;
  readonly fromRef: PeriodicSiteRef;
  readonly toRef: PeriodicSiteRef;
  readonly start: RenderVector3;
  readonly end: RenderVector3;
  readonly displacementCartesian: RenderVector3;
  readonly distanceAngstrom: number;
  readonly source: "distance_cutoff" | "explicit_input" | "legacy_same_cell";
  readonly authoritative: boolean;
};

export type RenderLattice = {
  readonly matrix: readonly [RenderVector3, RenderVector3, RenderVector3];
};

export type ValidatedRenderScene = {
  readonly contractVersion: "viewer_scene.v1" | "viewer_scene.v2";
  readonly schemaVersion: "phase10f8.viewer_scene.v1" | "phase10f18.viewer_scene.v2";
  readonly atoms: readonly RenderAtom[];
  readonly bonds: readonly RenderBond[];
  readonly lattice: RenderLattice;
  readonly displayLattice: RenderLattice;
  readonly supercellRepeat: ImageOffset;
  readonly source: Readonly<{
    readonly resourceId: string;
    readonly filename: string;
    readonly parser: string;
  }>;
  readonly formula: string;
  readonly warnings: readonly string[];
};

export type ViewerSceneValidation = {
  readonly valid: boolean;
  readonly errors: readonly string[];
  readonly warnings: readonly string[];
};

export type ViewerRendererState =
  | "idle"
  | "validating"
  | "ready"
  | "initializing_renderer"
  | "rendering"
  | "rendered"
  | "unsupported"
  | "validation_failed"
  | "renderer_failed"
  | "chunk_load_failed"
  | "scene_over_renderer_cap"
  | "context_lost"
  | "disposed";

export type ViewerRendererMetrics = {
  readonly performanceTier: "interactive" | "degraded";
  readonly atomCount: number;
  readonly bondCount: number;
  readonly speciesCount: number;
  readonly instancedMeshCount: number;
  readonly latticeEdgeCount: number;
  readonly drawCalls: number;
  readonly geometries: number;
  readonly materials: number;
  readonly triangles: number;
  readonly lines: number;
  readonly textures: number;
  readonly bufferAttributes: number;
  readonly sceneObjects: number;
  readonly initializationMs: number;
  readonly firstFrameMs: number;
};

export type ViewerRendererSnapshot = {
  readonly state: ViewerRendererState;
  readonly canvasCount: number;
  readonly atomCount: number;
  readonly bondCount: number;
  readonly latticeEdgeCount: number;
  readonly triangleCount: number;
  readonly lineCount: number;
  readonly cameraPosition: RenderVector3;
  readonly cameraTarget: RenderVector3;
  readonly drawingBuffer: readonly [number, number];
  readonly graphicsContext: "webgl2" | "webgl";
  readonly rendererVersion: string;
  readonly selectedSites: readonly PeriodicSiteRef[];
  readonly selectedSiteIndices: readonly number[];
  readonly siteScreenPositions: readonly Readonly<{ readonly ref: PeriodicSiteRef; readonly siteIndex: number; readonly x: number; readonly y: number }>[];
  readonly metrics: ViewerRendererMetrics;
};

export type ViewerRendererEngine = {
  readonly resetCamera: () => void;
  readonly setCellVisible: (visible: boolean) => void;
  readonly setBondsVisible: (visible: boolean) => void;
  readonly render: () => void;
  readonly keyboardCamera: (action: "rotate_left" | "rotate_right" | "rotate_up" | "rotate_down" | "pan_left" | "pan_right" | "pan_up" | "pan_down" | "zoom_in" | "zoom_out") => void;
  readonly setSelection: (sites: readonly PeriodicSiteRef[]) => void;
  readonly exportPng: () => Promise<Blob>;
  readonly snapshot: () => ViewerRendererSnapshot;
  readonly dispose: () => void;
};

export type ViewerRendererEngineFactory = (args: {
  readonly container: HTMLElement;
  readonly scene: ValidatedRenderScene;
  readonly onContextLost: () => void;
  readonly onSitePick?: (site: PeriodicSiteRef | null) => void;
  readonly pixelRatioCap: number;
  readonly antialias: boolean;
  readonly performanceTier: "interactive" | "degraded";
}) => Promise<ViewerRendererEngine>;
