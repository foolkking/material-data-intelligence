# Phase 10M-5 Acceptance Evidence Map

| ID | Requirement | Implementation | Tests/evidence |
| --- | --- | --- | --- |
| M5-A01 | `REPORT_RECIPE_AUTHORITY_AND_CONTRACTS` | Strict DTOs/schemas/hash and existing repositories | `test_phase10m5_report_contracts.py`, `authority_audit.json` |
| M5-A02 | `SCIENTIFIC_REPORT_COMPOSITION` | Eligibility projector and deterministic 12-section composer | `test_phase10m5_report_composition.py`, complete/partial cases |
| M5-A03 | `EXACT_RECIPE_REPLAY_MANIFEST` | Exact 0.1/0.2 Plan/step/binding manifest | recipe 0.1/0.2/determinism captures |
| M5-A04 | `WORKSPACE_COMPOSITION_UI_AND_HISTORY` | Workspace Report panel and immutable history | component tests and four-browser evidence |
| M5-A05 | `DETERMINISTIC_PREVIEW_AND_SAFE_EXPORT` | No-write preview and JSON/Markdown export | preview/export captures and hashes |
| M5-A06 | `PARTIAL_COMPATIBILITY_ACCESSIBILITY_PERFORMANCE_SECURITY` | Typed states, caps, mobile/a11y/security | edge, performance, security, mobile evidence |
| M5-A07 | `END_TO_END_EVIDENCE_AND_VERIFIED_LIFECYCLE` | Service-backed pair plus exact-SHA lifecycle | integration test, manifest, CI history |

```text
expected = 7
implemented = 7
missing = 0
extra = 0
duplicate = 0
```
