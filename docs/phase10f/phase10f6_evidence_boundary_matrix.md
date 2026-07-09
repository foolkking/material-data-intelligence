# Phase 10F-6 Evidence Boundary Matrix

| Evidence Type | Applies To | Current Status | PASS Claim Allowed | Official PASS Eligible | Notes |
|---|---|---|---:|---:|---|
| Implementation tests | `structure.coordination_hist`, `structure.xrd`, `structure.rdf` | complete | true | false | Supports implementation PASS, not official-example PASS. |
| Browser/API evidence | completed static physics tools | complete | true | false | Supports product evidence and artifact-preview evidence. |
| Fixture-pack replay | Phase 10F-4 fixture pack | PASS | true | false | Supports fixture-pack replay PASS only. |
| `internal_regression` fixture | current three Phase 10F cases | replay PASS | true | false | Internal regression fixtures cannot become official PASS by themselves. |
| `official_like_curated` fixture | future curated cases | not used in replay | true | false | Useful for regression, not official PASS. |
| `official_direct` case | future official direct-uploadable cases | absent | true after replay | true after replay | Can become official PASS only after direct platform replay and expected-contract comparison. |
| Approved `official_derived_manual` case | future reviewer-approved derived cases | absent | true after approval and replay | true after approval and replay | Requires source traceability, reviewer approval, and direct replay. |
| `mapping_only` case | official benchmark mappings | classified non-PASS | false | false | Mapping references are not execution evidence. |
| Notebook-only case | official examples requiring notebooks | excluded | false | false | No notebook execution in this evidence chain. |
| Script-heavy case | official examples requiring scripts | excluded | false | false | No external script execution in this evidence chain. |
| Future-scope viewer/phonon case | viewer, WebGL, Brillouin-zone, phonon examples | deferred | false | false | Requires separate planning and approval before any implementation or evidence claim. |

## Rules

- `internal_regression` fixture-pack PASS is not official PASS.
- `official_like_curated` is not official PASS.
- `mapping_only` is not PASS.
- `official_direct` can become official PASS only after direct replay.
- Approved `official_derived_manual` can become official PASS only after reviewer approval and direct replay.
