# Phase 10M-0 Compatibility Strategy

Status: REVIEWER-SEALED RECOMMENDATION

| Source | Decision | Workspace behavior |
| --- | --- | --- |
| AnalysisPlan 0.1 | Preserve | Project as independent ordered steps; never infer dependency |
| AnalysisPlan 0.2 | Preserve | Project exact dependency bindings and execution graph |
| Historical plans/jobs | Project | Idempotent lazy Workspace creation from exact records |
| Old Job without modern identity | Read-only | `LEGACY_READ_ONLY`; no identity inference |
| Job without dependency graph | Preserve | Execution panel shows independent work only |
| Partial execution | Preserve | Workspace and affected panels disclose partial/blocked branches |
| Missing Profile | Read-only | No sample/site cross-selection; show authority unavailable |
| Stale dataset version | Preserve historical binding | `STALE`; no remap to current version |
| Legacy Artifact | Inert fallback | Metadata/download or strict JSON/text fallback, not scientific renderer |
| Unsupported Artifact contract | Read-only | `CONTRACT_UNSUPPORTED` and exact provenance |
| Missing interpretation | Preserve | Findings is not requested/unavailable; no synthetic findings |
| Existing PlannerWorkbench `/` | Preserve | Remains canonical new-analysis entry |
| Existing API clients | Preserve | Current endpoints unchanged; Workspace API additive |
| Existing reports | Preserve | Readable; Workspace composition absent until explicitly created |
| Existing recipes | Preserve | Readable; unsupported replay is blocked, never upgraded silently |
| Existing browser evidence | Historical only | Retains original SHA; not claimed as current Workspace proof |

Workspace introduction does not mutate AnalysisIntent 1.0, EligibilityResolution 1.0, AnalysisPlan 0.1/0.2, plan hashes, Runtime semantics, Artifact lineage, interpretation, report, or recipe records. Existing URLs continue to render PlannerWorkbench. New deep links require a persisted Workspace identity.

Compatibility failures are typed and local to a panel or read-only projection. They never cause scientific data coercion, fallback execution, current-version rebinding, or hidden historical migration.
