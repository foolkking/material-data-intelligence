# Materials Intelligence Platform — Exhaustive Pre/Post Capability Parity Audit

## Mode
READ_ONLY_CAPABILITY_CONSERVATION_AUDIT

## Baselines
- Pre-migration: `db75aa57136e4512b11b6fe69bb54840ad970323`
- Current audit head: `376436df67738bbf9901622edd5153e605ae7c3c`

## Purpose
Independently derive pre/current frontend routes, UI entrypoints, backend HTTP
operations, non-HTTP services, runtime/dynamic identities, migration-affected
symbols, reduced implementation files, code-volume anomalies, and test
coverage. Produce a machine-readable and human-readable capability ledger.

## Constraints
- Use Git plumbing/AST and safe runtime inspection; do not modify the forensic
  baseline, create a branch/worktree, push, mutate runtime/user data, or treat
  architecture/tests/build alone as parity proof.
- Complete the full inventory before any repair. If missing or unresolved
  capabilities exist, report them first rather than launching a broad refactor.
- A facade counts only when its canonical implementation target resolves.
- Runtime verification is reported independently; `NOT_RUNTIME_VERIFIED` is not
  silently converted to parity failure.

## Required gates
- Exact route/navigation/lazy/worker set differences.
- Frontend and backend meaningful-symbol accounting.
- Static HTTP method/path/contract comparison.
- Non-HTTP worker/service/repository/runtime/registry inventory.
- Dynamic handler, queue, Tool, Adapter, CLI, launcher and worker-path checks.
- Negative-space accounting for every migration-reduced implementation group.
- Per-group source-volume anomaly review.
- Test-reference mapping and explicit untested capability list.
- Full ledger with evidence and bounded missing/unresolved set.

## Prohibited actions
No source migration, capability repair before inventory completion, schema/auth/
identity/scientific/UI changes, evidence retirement, cleanup, branch/worktree
creation, push, or release.
