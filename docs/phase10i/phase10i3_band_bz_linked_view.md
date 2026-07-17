# Phase 10I-3 Band-BZ Linked View

## Scope and boundary

Phase 10I-3 composes existing `phonon.band` and
`structure.brillouin_zone` artifacts in the frontend. It does not add a public
tool, recompute either scientific product, or persist a new scientific
artifact. The application-owned internal contract is
`phase10i3.reciprocal_band_bz_link.v1`.

The supported product is phonon band to Brillouin-zone linking. The type and
state boundaries are neutral enough for a future electronic-band consumer, but
this phase contains no electronic-band artifact, calculation, route, or claim.

## Compatibility gate

Linked mode starts only after both source products validate independently and
the link builder verifies:

- exact band artifact SHA-256 binding;
- source structure identity;
- standardized primitive real-lattice matrix and hash;
- reciprocal convention `physics_2pi`, coordinate system, and units;
- one selected BZ path variant;
- ordered segment count, direction, endpoints, and discontinuities;
- every band sample's segment identity, normalized `t`, and Cartesian residual;
- source-stable branch index and frequency-array shape; and
- bounded sample, segment, branch, mapping, and numeric-value counts.

The Phase 10H band schema does not carry provider or time-reversal fields.
Compatibility is therefore accepted only when the complete ordered path
geometry equals the selected provider-bound BZ variant. Stable warnings record
the undeclared source metadata. Labels are never scientific identity or a
fallback mapping.

Primitive-lattice, convention, unit, path, sample, branch, and discontinuity
mismatches block linked mode before a BZ engine is allocated. Ordinary artifact
previews remain available.

## Link model and identity

The immutable model binds the band hash, reciprocal/BZ/k-path hashes,
structure and primitive-lattice identities, selected path variant, provider,
and conventions. It derives three bounded maps:

1. Point occurrences distinguish one geometric BZ point from each concrete
   start/end occurrence on the band path.
2. Segment mappings preserve source order, direction, discontinuity state,
   distance range, and canonical BZ segment ID.
3. Sample mappings preserve q-point index, segment index, reciprocal
   fractional/Cartesian coordinate, normalized `t`, residual, and optional
   endpoint occurrence.

Branches are separate from reciprocal selection. A BZ q-point does not imply a
phonon branch, frequency, or mode. Branch identity is retained only when the
selection originated from a band sample or an exact existing mode reference.
No nearest-frequency matching is permitted.

## Shared selection and interaction

One component-local reducer owns hover and pinned selections. Each event has a
monotonic transaction ID and source panel. Hover leave restores the pinned
selection; stale leave events are ignored; controlled BZ updates do not feed
back into the reducer. Artifact hash changes reset both states.

Band-to-BZ supports endpoint, interior sample, segment, branch,
imaginary-frequency, hover, pin, table, and keyboard selection. The BZ engine
uses an application-owned reciprocal-sample marker or canonical segment
highlight without reconstructing base geometry.

BZ-to-band supports canonical path point and whole-segment selection. Point
selection resolves exact path occurrences and exposes occurrence context while
leaving the branch unset. Discontinuities are never interpolated. Arbitrary
interior-segment BZ raycast is deferred.

The shared inspector reports source, variant, point/segment/sample identities,
q-point coordinates, normalized `t`, residual, path distance, branch,
frequency, imaginary classification, warnings, and compatibility state.

## Animation handoff

Animation is enabled only when an existing validated package binds the same
band hash and exact q-point, branch, frequency, mode ID, structure, and NAC
semantics. Missing, stale, or mismatched eigenvector data produces a disabled
typed state. The link never searches by frequency or nearest coordinate.

## UI, accessibility, and lifecycle

Desktop uses a Band/BZ workspace with a shared inspector. Mobile uses Band, BZ,
and Inspector tabs. Only the visible BZ tab owns a canvas/context, so tab changes
release and recreate bounded GPU resources instead of retaining hidden work.

The linked region has an accessible name, polite status, named controls,
keyboard-operable samples and segments, visible focus, Escape-to-clear, and a
bounded semantic sample table. Text exposes scientific identity so color is not
the only carrier. There is no continuous linked-view motion.

## Resource and security policy

Caps are 4,096 samples, 256 segments, 256 branches, 8,192 mappings, and 262,144
band numeric values. Mapping is iterative and bounded. The BZ engine retains
Phase 10I-2 geometry, DPR, context, and lifecycle caps.

All source strings render through React text nodes. Artifacts cannot supply
HTML, CSS, URLs, shaders, modules, callbacks, DOM IDs, or renderer types. The
link performs no fetch, XHR, worker, websocket, image, texture, or remote module
load. Selection is ephemeral session state and never mutates canonical
artifacts.

## Known limitations

- Band v1 provider/time-reversal metadata is undeclared; exact ordered geometry
  and visible warnings are required.
- Only the selected canonical path variant is linked.
- BZ point and whole-segment reverse linking are implemented; arbitrary
  interior-segment raycast is deferred.
- State is session-local and not encoded in the URL.
- Mobile uses tabs rather than simultaneous panels.
- Electronic bands, custom paths, reciprocal meshes, magnetic/surface BZ,
  unfolding, interpolation, and collaborative cursors remain unimplemented.
