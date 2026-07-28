# Phase 10K-3 Materials ML Evaluation Evidence

Evidence is stored at
`docs/phase10k/evidence/phase10k3_materials_ml_evaluation/`.

- `api/`: sanitized Profile 2.0 and Planner/job/events/tool-call/result captures.
- `artifacts/`: persisted regression, uncertainty, classification, summary,
  and recipe outputs retrieved through API artifact content routes.
- `fixtures/required_cases.json`: scientific product snapshots.
- `performance/performance_metrics.json`: 4/5,000/100,000-row bounded runs.
- `browser/`: Chromium, Firefox, WebKit, mobile, accessibility, console/network,
  and PNG captures.
- `security_audit.json`, `network_audit.json`, and `evidence_manifest.json`:
  inert-content, no-network, secret, and SHA-256 integrity records.

`tests/integration/test_phase10_product_closure.py` also binds all three
products through persisted Planner jobs, PostgreSQL repositories, Redis queue
metadata, MinIO artifact storage, and QueueWorkerRuntime when the repository's
service-backed CI environment is enabled. Local runs without that environment
remain explicitly skipped rather than being represented as service evidence.

Required runtime, browser, chemistry, uncertainty, classification,
performance, network, and secret markers are enforced by
`tests/test_phase10k3_materials_ml_evidence.py`.
