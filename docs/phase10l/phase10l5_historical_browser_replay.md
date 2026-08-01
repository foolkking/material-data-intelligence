# Phase 10L-5 Historical Browser and Mock-LLM Replay Matrix

## Scope

The Phase 10L-5 live gate was expanded after audit because earlier browser
evidence often used real browser rendering with MockLLMProvider planning. The
five current-product cases alone were insufficient to claim repository-wide
LLM coverage. The historical runner therefore replays the useful semantic
planner cases through the current canonical path using real DeepSeek and exact
current Profile/Registry facts.

## Verified totals

| Set | Cases | Real calls | Models | Result |
|---|---:|---:|---|---|
| Current-product L5 suite | 5 | 16 | deepseek-v4-flash | PASS |
| Supplemental historical replay | 40 | 92 | flash/pro | PASS |
| Combined semantic coverage | 45 | 108 | flash/pro | PASS |

The two JSON records are `deepseek_verification_suite.json` and
`historical_deepseek_replay_suite.json`. The evidence manifest contains 166
entries and records the five current live run IDs, browser hashes, provider
audits, and sanitized failure provenance.

## Phase coverage

The supplemental records cover the useful retained planner semantics from
Phase 9, 10A, 10B, 10C, 10E, 10F, 10G, 10H, 10I, 10J, 10K, 10L-1, and 10L-2.
They exercise current registered tools or explicitly documented canonical
replacements, exact target and resource binding, clarification, unsupported
requests, capability mismatch, and no-plan/no-job/no-enqueue behavior.

The L5 current suite also includes the Phase 10L-3 phonon dependency chain and
L4 grounded interpretation. Real DeepSeek calls are made only in the bounded
server-side runners; browser evidence replays the sanitized persisted capture
and makes zero live API/provider calls.

## Exclusions and reasons

The following are not mislabeled as real LLM coverage:

* Pure browser interaction, renderer, accessibility, performance, and security
  fixtures. These are deterministic UI/runtime checks, not LLM decisions.
* Provider parser negative cases, prompt-injection cases, and deterministic
  failure injection. They must stay deterministic to prove rejection and are
  covered by focused tests and security evidence.
* Historical tools that have no current registered executable capability. They
  are recorded as superseded or unsupported rather than made selectable by
  adding a compatibility tool.
* Phase 1-8 infrastructure-only flows, which have no natural-language planner
  semantic to replay.
* Phase 10D static-preview-only flows, where the current planner semantic is
  represented by the 10F viewer/current replacement coverage.
* Damaged or missing historical prompt text. These entries use a documented
  semantic reconstruction from the retained case/tool contract and are never
  claimed as byte-for-byte prompt replay.

No excluded item is counted in the 45-case PASS total. The runner retains
sanitized diagnostics and source evidence paths for auditability.
