export type CartesianPoint = readonly [number, number, number];
export type PolyhedronVertex = Readonly<{ vertexIdentity: string; relativeCartesian: CartesianPoint }>;
export type PolyhedronFace = Readonly<{ faceIdentity: string; vertexIdentities: readonly string[] }>;
export type PolyhedronView = Readonly<{ yaw: number; pitch: number }>;

export const POLYHEDRON_VIEWS = {
  spatial: { yaw: -Math.PI / 5, pitch: Math.PI / 7 },
  xy: { yaw: 0, pitch: 0 },
  xz: { yaw: 0, pitch: Math.PI / 2 },
  yz: { yaw: -Math.PI / 2, pitch: 0 },
} satisfies Record<string, PolyhedronView>;

/** A rigid camera rotation only; all three saved coordinates keep one scale. */
export function rotatePolyhedronPoint([x, y, z]: CartesianPoint, view: PolyhedronView): CartesianPoint {
  const horizontal = x * Math.cos(view.yaw) + z * Math.sin(view.yaw);
  const depth = -x * Math.sin(view.yaw) + z * Math.cos(view.yaw);
  return [horizontal, y * Math.cos(view.pitch) - depth * Math.sin(view.pitch), y * Math.sin(view.pitch) + depth * Math.cos(view.pitch)];
}

export function projectSavedPolyhedron(
  vertices: readonly PolyhedronVertex[], faces: readonly PolyhedronFace[],
  width: number, height: number, view: PolyhedronView, zoom = 1,
) {
  // Normalize before taking norms so even bounded but extreme finite input
  // cannot overflow. A fixed bounding sphere keeps rotation fitted and steady.
  const coordinateScale = Math.max(0, ...vertices.flatMap((vertex) => vertex.relativeCartesian.map(Math.abs))) || 1;
  const normalized = vertices.map((vertex) => vertex.relativeCartesian.map((value) => value / coordinateScale) as unknown as CartesianPoint);
  const radius = Math.max(0, ...normalized.map((point) => Math.hypot(...point))) || 1;
  const scale = Math.max(1, Math.min(width, height) - 80) / (2 * radius) * zoom;
  const center = { x: width / 2, y: height / 2 };
  const points = vertices.map((vertex, index) => {
    const [x, y, depth] = rotatePolyhedronPoint(normalized[index], view);
    return { vertexIdentity: vertex.vertexIdentity, index, x: center.x + x * scale, y: center.y - y * scale, depth };
  });
  const byId = new Map(points.map((point) => [point.vertexIdentity, point]));
  const polygons = faces.map((face) => {
    const projected = face.vertexIdentities.map((id) => byId.get(id));
    if (projected.some((point) => !point)) throw new Error("Polyhedron face references an unavailable saved vertex");
    const facePoints = projected as typeof points;
    return { faceIdentity: face.faceIdentity, points: facePoints, depth: facePoints.reduce((sum, point) => sum + point.depth, 0) / facePoints.length };
  }).sort((left, right) => left.depth - right.depth);
  const axes = ([[1, 0, 0], [0, 1, 0], [0, 0, 1]] as const).map((point, index) => {
    const [x, y] = rotatePolyhedronPoint(point, view);
    return { label: ["X", "Y", "Z"][index], x: x * 24, y: -y * 24 };
  });
  return { center, points, polygons, axes };
}
