# Phase 10F-1: Official Examples Direct Verification for Static Structure Physics

## Goal

Verify the completed static structure physics tools against direct-uploadable official-example-like local cases where possible:

```text
structure.coordination_hist
structure.xrd
structure.rdf
```

This phase adds direct verification evidence only. It does not implement a new adapter and does not change existing tool semantics.

## Current Baseline

```text
Phase 10E-8 commit: 39d3245 Add RDF browser API evidence
Phase 10E-8 HEAD: 39d3245f019f628f08e59c585210f2278b5f3ea8
Phase 10E-8 CI run: 28988090080 success
Static physics tools complete:
- structure.coordination_hist
- structure.xrd
- structure.rdf
```

## Execution Discipline

1. Only verify static physics tools.
2. Do not implement new adapters.
3. Do not modify `structure.coordination_hist`, `structure.xrd`, or `structure.rdf` core semantics.
4. Do not implement full interactive 3D viewer.
5. Do not implement WebGL renderer.
6. Do not introduce Three.js.
7. Do not implement `structure.viewer_3d`.
8. Do not implement `structure.brillouin_zone_3d`.
9. Do not implement phonon bands or DOS.
10. Do not implement advanced local environment classification.
11. Do not implement experimental fitting or Rietveld refinement.
12. Do not execute notebooks.
13. Do not execute external scripts.
14. Do not access the internet.
15. Do not install new dependencies.
16. Do not run a real LLM.
17. Do not execute artifact JavaScript.
18. Do not load external URLs from artifacts.
19. Do not modify QueueWorkerRuntime main semantics.
20. Do not modify AnalysisPlanRepository main semantics.
21. Do not modify `/planner/jobs` main semantics.
22. Do not relax PlanValidator security boundaries.
23. Do not mark mapping-only, notebook-only, script-heavy, external-API, missing-input, or screenshot-only cases as PASS.
24. Do not fabricate evidence.

## Preflight

Run:

```bash
cd "E:\1project\Material Data Intelligence"
git status --short
git log --oneline -40
git branch --show-current
git tag --points-at HEAD
```

Confirm:

- branch is `master`.
- git status is clean.
- HEAD is at or after `39d3245 Add RDF browser API evidence`.
- Phase 10E implementation and evidence docs exist.
- official-example benchmark pack exists locally if it will be used.

If the worktree is dirty, stop and report the changes.

## Direct-Uploadable Gate

A case may be treated as direct verification only if all are true:

- input file is local and directly uploadable through the platform.
- no notebook execution is required.
- no external script execution is required.
- no external API is required.
- expected static physics target maps clearly to one of:
  - `structure.coordination_hist`
  - `structure.xrd`
  - `structure.rdf`
- artifact comparison policy is deterministic.
- evidence can be captured through local API/job flow and browser/static preview.

Otherwise record the case as mapping reference, unsupported, or future scope; do not mark it PASS.

## Artifact Comparison Policy

For direct verification cases:

- coordination histogram:
  - verify artifact filenames, schema versions, `tool_id`, histogram bins, warnings/limits, security flags.
  - compare stable JSON contract and deterministic ordering, not unsupported advanced chemistry labels.
- XRD:
  - verify artifact filenames, schema versions, `tool_id`, CuKa-only policy, sorted peaks, limits/warnings, security flags.
  - compare tolerance-pinned peak positions/intensities only if local expected values are available.
  - do not claim experimental fitting or official screenshot reproduction.
- RDF:
  - verify artifact filenames, schema versions, `tool_id`, periodic-only policy, bins, counts, number-density normalization, partial-pair ordering, limits/warnings, security flags.
  - compare deterministic JSON fields only; do not claim experimental PDF fitting.

## Evidence Capture Policy

For each PASS case, capture:

- sanitized API request/response transcript.
- selected `tool_id`.
- job id and plan id if present.
- artifact names and metadata.
- copied artifacts.
- browser/static preview screenshots where feasible.
- security audit: no artifact JS, no external URLs, no WebGL, no Three.js, no real LLM, no secrets.
- negative-routing sanity check for adjacent prompts when relevant.

## Docs

Add or update:

```text
docs/phase10f/phase10f1_static_physics_official_direct_verification.md
docs/phase10f/browser_api_evidence/phase10f1_static_physics_direct_verification/
```

The main doc must include:

- scope.
- baseline.
- official/direct-uploadable gate.
- case inventory.
- PASS / mapping-only / unsupported / future-scope decisions.
- API evidence.
- artifact comparison evidence.
- browser/static preview evidence.
- security evidence.
- tests/checks.
- deferred scope.
- conclusion.

## Persistent Updates

Update:

```text
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/TOOL_REGISTRY_NOTES.md
persistent/ARCHITECTURE_DECISIONS.md
```

Record:

- Phase 10F-1 started/completed.
- which static physics cases were directly verified.
- which cases remain mapping-only or future scope.
- no new adapter.
- no full viewer/WebGL/Three.js/phonon.
- no notebook/script execution.
- no official PASS without direct verification.

## Checks

Run:

```bash
git status --short
git diff --stat
git diff --check
uv lock --check
npm --prefix apps/web run typecheck
uv run python -m pytest -q
```

If full pytest is too heavy, run relevant static physics, registry, planner, service-backed, and no-skipped tests and record the gap honestly.

## Redaction / Secret Scan

Scan at least:

```text
docs/phase10f
persistent
```

Final evidence must record:

```text
NO_SECRET_PATTERN_HITS
```

## Commit / CI

After checks pass:

```bash
git status --short
git diff --stat
git add docs/phase10f persistent
git commit -m "Verify static physics official examples"
git push origin master
```

Wait for current HEAD CI:

- unit job success.
- frontend job success.
- service-backed integration success.
- no-skipped assertion passed.
- default CI does not call a real LLM.
- git status clean.

## Final Output

Return:

```markdown
# Phase 10F-1 Official Static Physics Direct Verification Result

## 1. Conclusion
PASS / PARTIAL_PASS / FAIL

## 2. Baseline
- Phase 10E-8 HEAD:
- current HEAD before:
- branch:
- git status before:

## 3. Direct Verification
- coordination_hist:
- XRD:
- RDF:

## 4. Mapping / Unsupported Cases
- mapping-only:
- notebook-only:
- script-heavy:
- external API:
- missing input:

## 5. Evidence
- API:
- artifacts:
- browser/static preview:
- security:

## 6. Not Implemented
- new adapters:
- full viewer:
- WebGL / Three.js:
- phonon:
- notebook/script workflows:

## 7. Checks / CI
- git diff --check:
- uv lock --check:
- npm typecheck:
- pytest:
- CI:

## 8. Next Recommendation
...
```

## PASS / PARTIAL_PASS / FAIL

PASS requires:

- direct-uploadable gate applied.
- no unsupported case marked PASS.
- evidence captured for every PASS case.
- docs/persistent updated.
- checks and CI passed.
- no new adapter/viewer/WebGL/phonon implementation.

PARTIAL_PASS allows:

- official pack missing but recorded.
- no direct-uploadable official cases found, with mapping inventory completed.
- CI unavailable after local checks pass, recorded honestly.

FAIL if:

- evidence is fabricated.
- unsupported cases are marked PASS.
- notebooks/scripts/external APIs are executed.
- new adapter/viewer/WebGL/phonon implementation is added.
- runtime authority boundaries are changed.
