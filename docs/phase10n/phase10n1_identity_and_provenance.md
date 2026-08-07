# Phase 10N-1 Identity And Provenance

Every result binds Project, Job, Plan/version, ToolCall, source resource/hash and
immutable structure/hash. A site identity is `site:<structureHash>:<index>` and is
valid only inside that exact structure hash. A neighbor relation includes the central
site, neighbor site, exact periodic image triplet, distance, algorithm/version and
parameter hash.

Ordering is canonical by structure identity, central site identity, neighbor site
identity, periodic image and distance. Artifact payloads contain bounded derived rows;
they do not copy the complete source structure. Checksum validation and scope checks
are performed by the existing artifact and runtime authorities.

The current selection contract supports exact structure-site selection. A periodic
neighbor relation remains algorithm-specific in the coordination panel unless the
existing selection contract has an exact relation kind; no cross-algorithm or
nearest-point mapping is performed.
