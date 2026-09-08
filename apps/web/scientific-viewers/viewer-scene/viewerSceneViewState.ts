import type { RenderVector3, ValidatedRenderScene, ViewerRendererSnapshot } from "./viewerSceneRendererTypes";

export const VIEWER_CLIP_AXES = ["x", "y", "z"] as const;
export type ViewerClipAxis = (typeof VIEWER_CLIP_AXES)[number];
export type CameraPreset = "default" | "top" | "front" | "side" | "isometric";
export type ViewerClipPlane = Readonly<{ axis: ViewerClipAxis; position: number; enabled: boolean }>;
export type ViewerClipState = Readonly<{ enabled: boolean; planes: readonly ViewerClipPlane[] }>;
export type ViewerCellDisplayState = Readonly<{ unitCell: boolean; supercellBoundary: boolean; latticeAxes: boolean }>;

export const DEFAULT_CLIP_STATE: ViewerClipState = Object.freeze({
  enabled: false,
  planes: Object.freeze(VIEWER_CLIP_AXES.map((axis) => Object.freeze({ axis, position: 0, enabled: false }))),
});

export function sceneClipBounds(scene: ValidatedRenderScene): Readonly<Record<ViewerClipAxis, readonly [number, number]>> {
  const positions = scene.atoms.map((atom) => atom.position);
  const extent = (axis: number): readonly [number, number] => {
    const values = positions.map((position) => position[axis]).filter(Number.isFinite);
    const min = values.length ? Math.min(...values) : 0;
    const max = values.length ? Math.max(...values) : 1;
    return Object.freeze(min === max ? [min - 1, max + 1] : [min, max]);
  };
  return Object.freeze({ x: extent(0), y: extent(1), z: extent(2) });
}

export function initialViewerClipState(scene: ValidatedRenderScene): ViewerClipState {
  const bounds = sceneClipBounds(scene);
  return Object.freeze({
    enabled: false,
    planes: Object.freeze(VIEWER_CLIP_AXES.map((axis) => Object.freeze({ axis, position: midpoint(bounds[axis]), enabled: false }))),
  });
}

export function validateViewerClipState(value: unknown, scene: ValidatedRenderScene): ViewerClipState {
  if (!isRecord(value) || typeof value.enabled !== "boolean" || !Array.isArray(value.planes) || value.planes.length !== 3) throw new Error("VIEWER_CLIP_STATE_INVALID");
  const sourcePlanes = value.planes;
  const bounds = sceneClipBounds(scene);
  const planes = VIEWER_CLIP_AXES.map((axis, index) => {
    const plane = sourcePlanes[index];
    if (!isRecord(plane) || plane.axis !== axis || typeof plane.enabled !== "boolean" || typeof plane.position !== "number" || !Number.isFinite(plane.position)) throw new Error("VIEWER_CLIP_STATE_INVALID");
    const [min, max] = bounds[axis];
    if (plane.position < min || plane.position > max) throw new Error("VIEWER_CLIP_POSITION_OUT_OF_RANGE");
    return Object.freeze({ axis, position: plane.position, enabled: plane.enabled });
  });
  if (planes.filter((plane) => plane.enabled).length > 3) throw new Error("VIEWER_CLIP_PLANE_LIMIT_EXCEEDED");
  return Object.freeze({ enabled: value.enabled, planes: Object.freeze(planes) });
}

export function buildViewerViewState(
  scene: ValidatedRenderScene,
  clip: ViewerClipState,
  display: ViewerCellDisplayState,
  preset: CameraPreset,
  snapshot: ViewerRendererSnapshot,
) {
  const safeClip = validateViewerClipState(clip, scene);
  const camera = validateCameraState({ preset, position: snapshot.cameraPosition, target: snapshot.cameraTarget, up: snapshot.cameraUp, zoom: snapshot.cameraZoom });
  return Object.freeze({
    schema_version: "phase10f25.viewer_view_state.v1" as const,
    scene: Object.freeze({ schema_version: scene.schemaVersion, resource_id: scene.source.resourceId }),
    camera,
    clipping: safeClip,
    display: Object.freeze({ unit_cell: display.unitCell, supercell_boundary: display.supercellBoundary, lattice_axes: display.latticeAxes }),
    policy: Object.freeze({ renderer_local: true, structure_mutated: false, canonical_topology_mutated: false, max_active_clip_planes: 3 }),
    security: Object.freeze({ inert_json: true, contains_javascript: false, external_urls: Object.freeze([]) }),
  });
}

export function replayViewerViewState(scene: ValidatedRenderScene, value: unknown) {
  if (!isRecord(value) || value.schema_version !== "phase10f25.viewer_view_state.v1") throw new Error("VIEWER_VIEW_STATE_INVALID");
  const source = isRecord(value.scene) ? value.scene : null;
  const display = isRecord(value.display) ? value.display : null;
  if (source?.schema_version !== scene.schemaVersion || source.resource_id !== scene.source.resourceId || !display || typeof display.unit_cell !== "boolean" || typeof display.supercell_boundary !== "boolean" || typeof display.lattice_axes !== "boolean") throw new Error("VIEWER_VIEW_STATE_INVALID");
  return Object.freeze({
    camera: validateCameraState(value.camera),
    clipping: validateViewerClipState(value.clipping, scene),
    display: Object.freeze({ unitCell: display.unit_cell, supercellBoundary: display.supercell_boundary, latticeAxes: display.lattice_axes }),
  });
}

function validateCameraState(value: unknown) {
  if (!isRecord(value) || !["default", "top", "front", "side", "isometric"].includes(String(value.preset)) || !vector(value.position) || !vector(value.target) || !vector(value.up) || typeof value.zoom !== "number" || !Number.isFinite(value.zoom) || value.zoom <= 0 || value.zoom > 100) throw new Error("VIEWER_CAMERA_STATE_INVALID");
  const bounded = [...value.position, ...value.target, ...value.up].every((item) => Math.abs(item) <= 1_000_000);
  if (!bounded) throw new Error("VIEWER_CAMERA_STATE_INVALID");
  return Object.freeze({ preset: value.preset as CameraPreset, position: freezeVector(value.position), target: freezeVector(value.target), up: freezeVector(value.up), zoom: value.zoom });
}

function vector(value: unknown): value is [number, number, number] { return Array.isArray(value) && value.length === 3 && value.every((item) => typeof item === "number" && Number.isFinite(item)); }
function freezeVector(value: [number, number, number]): RenderVector3 { return Object.freeze([...value]) as RenderVector3; }
function midpoint(value: readonly [number, number]) { return (value[0] + value[1]) / 2; }
function isRecord(value: unknown): value is Record<string, unknown> { return Boolean(value) && typeof value === "object" && !Array.isArray(value); }
