# MDI V0 — Phase E Final Canonical Live-Agent Browser Qualification — attempt-01

This file records the user-authorized Phase E execution contract supplied in
this task. The complete user prompt in the task conversation is normative;
this repository file records the bounded execution entry and stop conditions
used before any Case execution.

## Scope

- Canonical positive cases: 16 frozen Cases, one exact committed repository SHA.
- Required chain: real Browser, product UI, persisted input, DataProfile,
  real provider, Intent, Eligibility, Planner, Redis queue, fresh Worker,
  registered Adapter, persisted Artifacts, Workspace/Renderer, grounded
  Interpretation, applicable Report Preview/Finalize, inert Recipe.
- No handcrafted intent/plan/job/tool/artifact/report, no replayed provider
  response, no authority mutation, no paraphrase/negative expansion, and no
  M4/future work.
- Failed discovery, remediation, candidate and Phase D evidence remain
  historical and must not be deleted or used as final exact-SHA evidence.

## Mandatory entry gate

Before Case 1, the active repository and the requested frozen authority must
prove all of the following:

- PHASE_D = PASS / LIVE_QUALIFICATION_ENVIRONMENT_SEALED
- READY_FOR_PHASE_E = YES
- frozen package is at the active repository authority path and matches the
  declared SHA-256
- FINAL_CANDIDATE_COMMITTED = YES
- FINAL_REPOSITORY_HEAD_SHA is the same SHA used by Phase D and all final Cases
- PRODUCTION_RUNTIME_AFFECTING_UNCOMMITTED_DIFFS = 0
- fresh DB/bootstrap, migration, PostgreSQL, Redis/RQ, MinIO, API, frontend,
  fresh Worker, Browser shell and provider configuration are healthy
- formal execution counters are zero before the campaign

## Stop rule

If the entry gate is not satisfied, do not upload qualification fixtures, do
not submit questions, do not create qualification Jobs/Artifacts, do not make
real provider calls, and do not repair the blocker by mutating frozen
authority, resetting the worktree, or using the historical source tree as an
active development checkout. Produce a truthful HARD_QUALIFICATION_BLOCKER
record and stop.

Created: 2026-09-16T02:51:36.1276626Z
