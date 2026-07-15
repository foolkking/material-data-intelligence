# Phase 10I-2 Brillouin Renderer

## Scope and product identity

`structure.brillouin_zone` remains the only public Brillouin-zone tool. The
adapter produces inert Phase 10I artifacts through the persisted plan and
QueueWorkerRuntime path. The frontend recognizes the artifact family, validates
it independently, and lazy-loads one application-owned Three.js renderer. No
renderer, shader, module, texture, URL, or callback is stored in an artifact.

The standalone product renders the first Brillouin-zone polyhedron, primitive
reciprocal axes, canonical high-symmetry points, and the selected canonical
k-path. Electronic bands, phonons, meshes, magnetic/surface zones, custom paths,
and Band-BZ synchronization are not part of this phase.

## Validation and scene mapping

WebGL initialization is gated by all four contract identities, inert security
declarations, manifest content-hash references, source-structure identity,
primitive-lattice identity, reciprocal-lattice binding, `physics_2pi`, and
`angstrom^-1`. Canonical IDs and topology references are checked before mapping.
Invalid, non-finite, over-cap, or executable-looking fields produce a typed
fallback and no canvas.

The mapper consumes canonical reciprocal Cartesian coordinates directly. It
does not multiply or divide by `2*pi`. One deterministic uniform visual scalar
fits the scene; original reciprocal coordinates remain in the inspector and
tables. Per-axis normalization is forbidden.

Renderer budgets are at most 256 vertices, 512 edges, 256 faces, 512 triangles,
128 points, 256 path segments, 64 visible labels, DPR 2, and 16,777,216 export
pixels. A physical three-dimensional lattice Voronoi cell does not approach the
defensive contract maxima: the captured triclinic case is the highest-complexity
scientific case at 24 vertices, 36 edges, 14 faces, and 44 triangles. Synthetic
over-cap input is tested only as a refusal case and is not represented as a
scientific Brillouin zone.

## Geometry and rendering

Each ordered face loop is projected onto an orthonormal basis derived from its
canonical outward normal. The mapper verifies coplanarity, outside-CCW winding,
finite nonzero triangles, and triangle-area agreement with the canonical face
area. Convex loops are fan-triangulated under a fixed work cap. Triangulation
diagonals are never emitted as scientific edges.

Faces use one transparent application-owned material with depth testing,
disabled depth writes, conservative opacity 0.08-0.65, and opaque canonical
edges above them. Browser transparency sorting can differ slightly for
overlapping coplanar fragments; topology, coordinates, opaque edges, picking,
and the textual alternative remain authoritative. Edges, reciprocal axes, and
k-paths each use a shared `LineSegments` geometry. Vertices and high-symmetry
points use shared `Points` geometry. No per-object material is created.

K-path geometry contains only emitted canonical segments. Discontinuity records
do not create connector lines. Variant selection uses stable variant and segment
IDs and disposes the replaced path buffer. Labels are bounded React text nodes;
artifact HTML, CSS, fonts, and MathJax are not interpreted.

## Interaction and lifecycle

Point, face, vertex, and path raycasts map to canonical IDs. Selection is
independent of triangle indices and is cleared when its layer, artifact, or path
variant becomes unavailable. The inspector reports original reciprocal
coordinates, face generators, normals, topology, provider, convention, and path
identity. Point and segment tables provide a complete non-canvas alternative.

OrbitControls supplies rotate, zoom, and pan. Perspective and orthographic
cameras share deterministic fit and reciprocal-basis `+b1`, `+b2`, `+b3`, and
isometric presets. Keyboard arrows rotate, `+`/`-` zoom, and `R` resets. Touch
uses the same local controls. Auto-rotation and continuous idle RAF are absent.
Clipping is deferred because the structure-viewer plane contract is real-space
specific; no nonfunctional BZ clipping control is exposed.

One surface owns at most one canvas, WebGL context, OrbitControls instance, and
ResizeObserver. Context loss prevents default browser behavior, disposes stale
GPU resources, and offers controlled reinitialization. Unmount and artifact
replacement remove listeners, disconnect resize observation, dispose all
geometries/materials/path replacements, dispose the renderer, force context
loss, and remove the canvas. PNG export is local, fixed-camera, dimension/DPR
bounded, filename-sanitized, and revokes its Blob URL.

## Product boundary and handoff

The Results workspace provides `3D Renderer`, `Scientific data`, and `Manifest`
tabs plus summary/recipe/artifact downloads. Renderer failure never changes the
backend job result. Phase 10I-3 may consume the stable point, segment, variant,
reciprocal, and structure identities. This phase does not create cross-panel
selection or recompute a band path.
