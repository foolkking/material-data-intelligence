import { describe, expect, it } from "vitest";
import { POLYHEDRON_VIEWS, projectSavedPolyhedron, rotatePolyhedronPoint, type CartesianPoint } from "./localEnvironmentProjection";

const vertex = (id: string, relativeCartesian: CartesianPoint) => ({ vertexIdentity: id, relativeCartesian });

describe("saved polyhedron projection", () => {
  it("keeps distances under camera rotation in all three dimensions", () => {
    const left: CartesianPoint = [2, -1, 4], right: CartesianPoint = [-3, 2, .5];
    const distance = (a: CartesianPoint, b: CartesianPoint) => Math.hypot(...a.map((value, index) => value - b[index]));
    for (const view of Object.values(POLYHEDRON_VIEWS)) {
      expect(distance(rotatePolyhedronPoint(left, view), rotatePolyhedronPoint(right, view))).toBeCloseTo(distance(left, right), 12);
    }
  });

  it("uses one scale for unequal axes in a wide viewport", () => {
    const points = [vertex("left", [-4, 0, 0]), vertex("right", [4, 0, 0]), vertex("top", [0, 1, 0]), vertex("bottom", [0, -1, 0])];
    const projection = projectSavedPolyhedron(points, [], 640, 240, POLYHEDRON_VIEWS.xy);
    const [left, right, top, bottom] = projection.points;
    expect((right.x - left.x) / (bottom.y - top.y)).toBeCloseTo(4, 12);
  });

  it("retains the depth axis and only the faces that were actually saved", () => {
    const vertices = [vertex("a", [0, 0, -2]), vertex("b", [0, 0, 2]), vertex("c", [1, 0, 0])];
    const faces = [{ faceIdentity: "saved-face", vertexIdentities: ["c", "a", "b"] }];
    const before = JSON.stringify({ vertices, faces });
    const projection = projectSavedPolyhedron(vertices, faces, 300, 260, POLYHEDRON_VIEWS.spatial);
    expect(projection.points[0].x).not.toBe(projection.points[1].x);
    expect(projection.points[0].y).not.toBe(projection.points[1].y);
    expect(projection.polygons[0].points.map((point) => point.vertexIdentity)).toEqual(["c", "a", "b"]);
    expect(projectSavedPolyhedron(vertices, [], 300, 260, POLYHEDRON_VIEWS.spatial).polygons).toEqual([]);
    expect(JSON.stringify({ vertices, faces })).toEqual(before);
  });

  it.each([[280, 256], [640, 400], [1600, 480]])("fits all saved vertices initially at %s × %s", (width, height) => {
    const vertices = [vertex("a", [14, -3, 2]), vertex("b", [-3, 1, -4]), vertex("c", [2, 8, 3])];
    for (const view of Object.values(POLYHEDRON_VIEWS)) {
      const projection = projectSavedPolyhedron(vertices, [], width, height, view);
      for (const point of projection.points) {
        expect(point.x).toBeGreaterThanOrEqual(40);
        expect(point.x).toBeLessThanOrEqual(width - 40);
        expect(point.y).toBeGreaterThanOrEqual(40);
        expect(point.y).toBeLessThanOrEqual(height - 40);
      }
    }
  });

  it("keeps finite display coordinates for extreme finite saved vectors", () => {
    const projection = projectSavedPolyhedron([vertex("a", [Number.MAX_VALUE, Number.MAX_VALUE, Number.MAX_VALUE])], [], 640, 400, POLYHEDRON_VIEWS.spatial);
    expect(Number.isFinite(projection.points[0].x)).toBe(true);
    expect(Number.isFinite(projection.points[0].y)).toBe(true);
  });
});
