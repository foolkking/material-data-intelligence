# Phase 10H-4 Phonon Eigenvector Contract

Phase 10H-4 defines inert contracts for phonon mode references, one complex
eigenvector, bounded eigenvector sets, summaries, and manifests. It binds every
mode to a canonical band artifact hash, structure/calculation identity,
q-point, source-stable branch, frequency, and optional Gamma NAC direction.

Canonical vectors are Cartesian, dimensionless, mass-weighted eigenvectors with
global Euclidean unit norm. A single global phase is canonicalized by making the
first nonzero atom-major xyz component real and positive. Real-space display
directions use `u_i=e_i/sqrt(m_i)` and a separate display-only maximum-atom
amplitude policy.

This phase adds validators, deterministic helpers, small fixtures, independent
Python/NumPy and TypeScript checks, evidence, and security policy. It adds no
parser, adapter, Tool Registry entry, planner route, UI, animation, solver,
notebook/script, external resource, or real LLM path.
