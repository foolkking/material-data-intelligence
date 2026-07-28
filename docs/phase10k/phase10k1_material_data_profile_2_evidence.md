# Phase 10K-1 Material Data Profile 2.0 Evidence

## Captures

- API: real in-process FastAPI upload, persisted profile fetch, and regenerate
  calls for materials properties, regression/uncertainty, ambiguity,
  classification, and periodic Structure.
- Browser: actual PlannerWorkbench in Chromium, Firefox, WebKit, and Chromium
  mobile, with screenshots and console/network audits.
- Performance: tiny, medium, and near-cap cases with duration, peak Python
  allocation proxy, output bytes, and coverage counts.
- Security: inert JSON-only profile metadata, no artifact JavaScript, no real
  LLM, no external URL, and no secret-pattern hit.

## Current Evidence Metrics

The recorded run inspected 5x4, 1000x32, and a requested 4112x516 table. The
near-cap case inspected exactly 4096 rows and 512 columns, produced explicit row
and column cap warnings, and serialized to less than 200 KiB. These values are
environment evidence, not a cross-machine latency SLA.

## Markers

```text
MATERIAL_DATA_PROFILE_API_EVIDENCE_PASS
MATERIAL_DATA_PROFILE_PERFORMANCE_EVIDENCE_PASS
MATERIAL_PROFILE_BROWSER_EVIDENCE_PASS
MATERIAL_PROFILE_MOBILE_EVIDENCE_PASS
NO_MATERIAL_PROFILE_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

The browser evidence is limited to the compact Profile 2.0 surface. Phase 10K-5
still owns full Material Intelligence integration closure.
