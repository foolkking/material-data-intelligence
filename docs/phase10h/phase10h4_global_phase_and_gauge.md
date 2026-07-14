# Phase 10H-4 Global Phase and Gauge

Scientific equivalence ignores one common complex phase. Canonical serialization
traverses atom-major xyz, finds the first component above `1e-12`, and rotates
the whole mode so that component is real and positive. Per-atom or per-component
canonicalization is forbidden because it destroys relative phase. The raw
source phase is not duplicated in the canonical artifact.
