# Phase 10M-0 Workspace Fact Audit Evidence

Audit baseline: `8f304fa08ddab1cefd69848f621f8438fc2038d5`. This directory is
sanitized retained evidence for the direct reviewer-authorized Phase 10M-0
audit. It does not claim that the proposed Workspace is implemented.

## Evidence sources

- `baseline.txt`, `git_history.txt`, `l5_archive_verification.txt`, and
  `task_state.txt` prove entry state and no queue admission.
- Route/component/API/persistence/renderer/identity files are implementation-
  grounded inventories using repository-relative source paths.
- `browser_current/` is the current L5 persisted-capture replay: five ready
  cases, clarification, unsupported, capability mismatch, Chromium/Firefox/
  WebKit desktop, and Chromium 390x844 mobile.
- `browser_interpretation_current/` is the current L4 persisted-capture replay:
  deterministic and strict-provider findings, partial results, no supported
  evidence, validation failure, source-integrity failure, evidence drill-down,
  three desktop browsers, and Chromium mobile.
- `screenshots/` contains the 41 raw PNG captures copied from those two runs.

## Browser truth

Both runners used local route-fulfilled persisted captures. `DEEPSEEK_KEY`,
`OPENAI_API_KEY`, and `MDI_LLM_API_KEY` were empty. They made no live API or
provider calls. The runner reported zero console/page errors and zero external
requests; the L5 matrix reported no document-level horizontal overflow at
desktop and 390x844. Firefox and WebKit mobile were not run by the existing
runner and are recorded as `UNAVAILABLE` rather than inferred.

The first L5 attempt hit a stale generated Next HMR chunk after local cache
removal. The repository-local `.next` cache and incomplete output were removed
only after path verification, then the same run passed from regenerated assets.
This infrastructure event is retained in `browser_audit_method.md` and is not
counted as a product failure.

## Current missing surfaces

The evidence confirms absence, not failure, for Workspace route/entity/history,
aggregate Workspace API, layout persistence, deep-link identity, and global
selection. Historical Job reload is an explicit current limitation because no
history route exists.

## Integrity

Text evidence is normalized to LF before final hashing; PNG hashes use raw
bytes. No secrets, authorization headers, provider raw payloads, private user
paths, object-store keys, or unsanitized database rows are retained.
