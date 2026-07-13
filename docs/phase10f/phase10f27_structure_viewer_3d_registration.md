# Phase 10F-27 Formal structure.viewer_3d Registration

## Decision

`structure.viewer_3d` is the one formal product identity for opening the
production interactive periodic structure viewer. The repository already had
the adapter, planner route, runtime semantics, and frontend consumer. This
phase corrects registry ownership by moving the unique entry from the
MatterViz manifest to `platform_builtin_manifest.yaml`; it does not create a
second tool or change QueueWorkerRuntime semantics.

The formal execution path remains:

```text
natural viewer intent -> validated AnalysisPlan -> structure.viewer_3d
-> StructureViewer3DAdapter -> inert viewer_scene.v2 artifacts
-> independent frontend validation -> lazy local renderer or JSON fallback
```

Explicit scene-data requests remain routed to `structure.viewer_scene`.
Historical Phase 10D tools remain direct compatibility paths only.

## Product boundary

The registered product covers atoms, lattice, bounded periodic bonds,
inspection, distance/angle/dihedral measurement, renderer-local supercells,
clipping, camera controls, scientific export, accessibility, mobile use, and
JSON fallback. It does not claim trajectories, phonons, Brillouin zones,
volumetric data, editing, or authoritative chemical topology.
