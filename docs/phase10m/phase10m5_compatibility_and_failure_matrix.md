# Phase 10M-5 Compatibility and Failure Matrix

| Source state | Report behavior | Recipe behavior |
| --- | --- | --- |
| Complete 0.2 | `REPORT_READY` or limits from explicit disclosures | Exact typed dependencies and bindings |
| Historical 0.1 | Methods/results retained | No invented graph; independent/sequential model |
| Partial results | Successful branches plus mandatory failed/blocked scope | Original partial outcome and descendants |
| All failed | `REPORT_NO_SCIENTIFIC_RESULTS`; no positive finding | Exact attempted methods and failures |
| No interpretation | Findings unavailable; Artifact/method/provenance retained | Exact Plan and execution facts |
| Stale | No latest rebinding; mandatory stale disclosure | Exact stale source retained |
| Missing selected Artifact | Finalize rejects until optional selection removed | No same-name/type substitution |
| Legacy Report/Recipe | Read-only history and typed unavailable fields | Original JSON/hash unchanged |
| Contract mismatch | `REPORT_SOURCE_INTEGRITY_FAILED` or unsupported | No inferred upgrade |

M1-M4 contracts, M4 renderer registry, AnalysisPlan 0.1/0.2, Runtime, Tool
Registry, Adapters, Artifact values, L4 Evidence/Interpretation, and existing
Report/Recipe APIs remain unchanged. M5 APIs are additive.
