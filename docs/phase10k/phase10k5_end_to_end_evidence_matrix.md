# Phase 10K-5 End-to-End Evidence Matrix

Evidence root:
`docs/phase10k/evidence/phase10k5_material_intelligence_integration/`.

Each runtime case follows Mock Planner -> `/planner/jobs` -> persisted validated
AnalysisPlan -> QueueWorkerRuntime -> Registry -> Adapter -> persisted artifact
-> API retrieval. Browser replay hydrates those captures; component fixtures
are not used as product evidence.

| Case | Profile | Dataset | ML | Composition Space | API | Browser |
| --- | --- | --- | --- | --- | --- | --- |
| A materials table | PASS | PASS | N/A | PASS | PASS | PASS |
| B structure enriched | PASS | PASS | N/A | N/A | PASS | PASS |
| C regression | PASS | PASS | PASS | PASS, ML error color | PASS | PASS |
| D uncertainty | PASS | PASS | PASS | PASS, uncertainty color | PASS | PASS |
| E classification | PASS | PASS | PASS | N/A by current product contract | PASS | PASS |
| F explicit comparison | PASS | PASS | N/A | PASS, shared fit | PASS | PASS |
| G partial capability | PASS | PASS | unavailable, not failed | PASS | PASS | PASS |
| H ambiguous ML | PASS | PASS | safely blocked | conditional | PASS | PASS |

`N/A` is retained as N/A and is never reported as PASS.

Browser coverage includes Chromium, Firefox, WebKit, and Chromium mobile
viewports for Dataset Explorer, Materials ML, and Composition Space. Captures
include product screenshots, console/network audits, keyboard/touch probes,
numeric tables, and horizontal-overflow checks.

`integration/report_recipe_compatibility.json` proves that the existing Report
flow can reference persisted product artifact IDs/content hashes and that K2,
K3, and K4 Recipes retain the same exact binding, selected tool, and parameters.
It does not introduce a new Report implementation.

Machine-readable markers:

```text
MATERIAL_INTELLIGENCE_RUNTIME_INTEGRATION_PASS
MATERIAL_INTELLIGENCE_API_INTEGRATION_PASS
MATERIAL_INTELLIGENCE_BROWSER_INTEGRATION_PASS
MATERIAL_INTELLIGENCE_PROFILE_AUTHORITY_EVIDENCE_PASS
MATERIAL_INTELLIGENCE_SAMPLE_IDENTITY_EVIDENCE_PASS
MATERIAL_INTELLIGENCE_VERSION_BINDING_EVIDENCE_PASS
MATERIAL_INTELLIGENCE_PARTIAL_FAILURE_ISOLATION_PASS
MATERIAL_INTELLIGENCE_REPRODUCIBILITY_PASS
MATERIAL_INTELLIGENCE_REPORT_RECIPE_COMPATIBILITY_PASS
MATERIAL_INTELLIGENCE_PERFORMANCE_EVIDENCE_PASS
MATERIAL_INTELLIGENCE_ACCESSIBILITY_EVIDENCE_PASS
NO_MATERIAL_INTELLIGENCE_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```
