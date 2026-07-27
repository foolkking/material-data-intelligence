# Phase 10J-7 Electronic Band / DOS Contract: Next Scope

> Status: HISTORICAL / SUPERSEDED BY GATE J6-R
> Electronic Band/DOS remains required for the initial release but is now
> planned under Phase 10N-5. Current authority: [../ROADMAP.md](../ROADMAP.md).
> This document is not an entry prompt.

## Status

Historical `NEXT / PENDING` record. This document was an entry contract, not an implementation.
No electronic schema, parser, adapter, tool, route, plot, or runtime behavior
is introduced by the post-J6 roadmap freeze.

## Historical Entry Criteria

At the time, Phase 10J-7 could start only after all of the following were true:

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

## Historical Contract Questions

The future Phase 10N-5 planning must resolve rather than assume:

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

## Historical Explicit Non-Scope

This historical J-7 scope did not implement parsers, adapters, Tool Registry entries, planner
routing, QueueWorkerRuntime behavior, charts, BZ linking, Fermi extraction,
renderers, DFT, external APIs, notebooks, scripts, or real LLM execution.
