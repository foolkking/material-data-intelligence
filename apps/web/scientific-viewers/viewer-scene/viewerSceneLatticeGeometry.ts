import type { RenderLattice, RenderVector3 } from "./viewerSceneRendererTypes";

// Shared by static report images and the interactive renderer; no camera runtime.
export function latticeCorners(matrix: RenderLattice["matrix"]): readonly RenderVector3[] {
  const [a, b, c] = matrix;
  return Object.freeze([
    vector(0, 0, 0), a, b, c,
    add(a, b), add(a, c), add(b, c), add(add(a, b), c),
  ]);
}

export function latticeEdges(matrix: RenderLattice["matrix"]): readonly (readonly [RenderVector3, RenderVector3])[] {
  const corners = latticeCorners(matrix);
  const pairs = [[0, 1], [0, 2], [0, 3], [1, 4], [1, 5], [2, 4], [2, 6], [3, 5], [3, 6], [4, 7], [5, 7], [6, 7]] as const;
  return Object.freeze(pairs.map(([from, to]) => Object.freeze([corners[from], corners[to]] as const)));
}

function add(left: RenderVector3, right: RenderVector3): RenderVector3 {
  return vector(left[0] + right[0], left[1] + right[1], left[2] + right[2]);
}

function vector(x: number, y: number, z: number): RenderVector3 {
  return Object.freeze([x, y, z]);
}
