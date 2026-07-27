# Phase 10J-7 Electronic Band / DOS Contract: Next Scope

## Status

`NEXT / PENDING`. This document is an entry contract, not an implementation.
No electronic schema, parser, adapter, tool, route, plot, or runtime behavior
is introduced by the post-J6 roadmap freeze.

## Entry Criteria

Phase 10J-7 may start only after all of the following are true:

* Phase 10J-6 implementation, result, evidence, completion-record CI, and queue
  archive are complete.
* The post-J6 J-7 through J-12 roadmap is committed and its exact current-HEAD
  CI succeeds.
* Branch is `master`, `origin/master` equals HEAD, and the worktree is clean.
* No unfinished J-6 task remains in `TASKS.md`.
* Electronic band/DOS and Fermi repository audits confirm no existing product
  is being duplicated.
* There is no overlapping public electronic tool identity.
* The reviewer explicitly directs entry into Phase 10J-7.

## Contract Questions

J-7 must resolve rather than assume:

* bounded first-batch source formats and authoritative source metadata;
* structure, calculation, reciprocal-lattice, k-point, path, and BZ identity;
* reciprocal units and physics-`2*pi` policy;
* energy units, energy zero, and Fermi-energy semantics;
* band index, spin, occupation, degeneracy, crossing, discontinuity, and gap
  authority;
* DOS grid, density unit, normalization, integrated-state checks, smearing,
  projections, and projection completeness;
* deterministic caps, validation order, error codes, provenance, and inert
  security declarations.

## Explicit Non-Scope

J-7 does not implement parsers, adapters, Tool Registry entries, planner
routing, QueueWorkerRuntime behavior, charts, BZ linking, Fermi extraction,
renderers, DFT, external APIs, notebooks, scripts, or real LLM execution.
