export type RenderVector3 = readonly [number, number, number];

export type RenderAtom = {
  readonly id: string;
  readonly siteIndex: number;
  readonly species: string;
  readonly label: string;
  readonly position: RenderVector3;
  readonly radius: number;
  readonly color: string;
};

export type RenderBond = {
  readonly id: string;
  readonly fromSiteIndex: number;
  readonly toSiteIndex: number;
  readonly start: RenderVector3;
  readonly end: RenderVector3;
};

export type RenderLattice = {
  readonly matrix: readonly [RenderVector3, RenderVector3, RenderVector3];
};

export type ValidatedRenderScene = {
  readonly contractVersion: "viewer_scene.v1";
  readonly schemaVersion: "phase10f8.viewer_scene.v1";
  readonly atoms: readonly RenderAtom[];
  readonly bonds: readonly RenderBond[];
  readonly lattice: RenderLattice;
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
  readonly metrics: ViewerRendererMetrics;
};

export type ViewerRendererEngine = {
  readonly resetCamera: () => void;
  readonly setCellVisible: (visible: boolean) => void;
  readonly setBondsVisible: (visible: boolean) => void;
  readonly render: () => void;
  readonly snapshot: () => ViewerRendererSnapshot;
  readonly dispose: () => void;
};

export type ViewerRendererEngineFactory = (args: {
  readonly container: HTMLElement;
  readonly scene: ValidatedRenderScene;
  readonly onContextLost: () => void;
  readonly pixelRatioCap: number;
}) => Promise<ViewerRendererEngine>;
