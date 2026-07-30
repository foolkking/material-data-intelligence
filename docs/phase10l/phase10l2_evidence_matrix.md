# Phase 10L-2 Evidence Matrix

Canonical sanitized evidence is stored at
`docs/phase10l/evidence/phase10l2_capability_aware_planner/`.

| Requirement | Evidence |
|---|---|
| Baseline and queue gate | `entry/baseline_audit.json` |
| Metadata contract and all registered tools | `registry/planner_metadata_contract.json`, `registry/actual_capability_inventory.json` |
| Deterministic Registry identity | `registry/snapshot.json` |
| Eligibility and typed rejection | `eligibility/ready_trace.json`, `eligibility/rejection_matrix.json` |
| Eligible-only provider context | `provider/candidate_isolation.json` |
| Stable ranking and collision handling | `selection/deterministic_ranking.json`, `regressions/independent_composition_collision.json` |
| Exact parameter provenance | `binding/exact_parameter_provenance.json` |
| Audit regressions | `regressions/*.json` |
| Strict fake provider and one repair | `llm/strict_parse_and_one_repair.json` |
| PLAN_READY API | `api/plan_ready.json` |
| Non-ready no side effects | `api/non_ready_no_job.json` |
| Immutable persistence | `persistence/immutable_associations.json` |
| Caps and timings | `performance/near_cap.json` |
| Security markers | `security/security_audit.json` |
| Browser/mobile/console/network | `browser/*.json`, `screenshots/*.png` |
| Test capture | `test_captures.json` |
| Integrity | `evidence_manifest.json` |

Text evidence is normalized before SHA-256 hashing; PNG hashes cover raw bytes.
The browser runner verifies Chromium, Firefox, WebKit, and Chromium 390x844
READY/non-ready states, inert audit JSON, no horizontal overflow, empty console
errors, and no external network requests.
