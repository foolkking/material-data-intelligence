# Phase 10K-2 Dataset Materials Explorer Evidence

Evidence root:
[`evidence/phase10k2_dataset_materials_explorer/`](evidence/phase10k2_dataset_materials_explorer/)

The capture runs a real Profile 2.0 fixture through Mock Planner, persisted
AnalysisPlan, PlanValidator, QueueWorkerRuntime, `dataset.materials_explorer`,
ToolCall persistence, four artifacts, and the bounded API content route. Mock
Planner is deterministic test infrastructure; no real LLM is called.

The product fixture simultaneously covers composition, three canonical
structures, two material properties, missing/invalid/non-finite values, exact
formula and structure duplicates, duplicate explicit sample ID, stable fallback
sample references, and explicit train/test comparison. Performance captures
small, medium, and the 100,000-row hard cap.

Chromium, Firefox, and WebKit consume the runtime-generated product artifact in
the actual PlannerWorkbench Results surface. Chromium additionally covers a
390x844 touch viewport. Screenshots, console/network audit, accessibility
snapshot, browser timing, and SHA-256 evidence manifest are committed.

Markers:

```text
DATASET_MATERIALS_EXPLORER_RUNTIME_EVIDENCE_PASS
DATASET_COMPOSITION_EXPLORER_EVIDENCE_PASS
DATASET_STRUCTURE_STATISTICS_EVIDENCE_PASS
DATASET_PROPERTY_EXPLORER_EVIDENCE_PASS
DATASET_QUALITY_EVIDENCE_PASS
DATASET_COMPARISON_EVIDENCE_PASS
DATASET_MATERIALS_EXPLORER_BROWSER_EVIDENCE_PASS
DATASET_MATERIALS_EXPLORER_PERFORMANCE_EVIDENCE_PASS
NO_DATASET_EXPLORER_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```
