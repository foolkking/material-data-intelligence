# Phase 10K-2 Evidence

This directory contains sanitized, bounded, locally generated Dataset Materials
Explorer evidence. `api/` records the real persisted plan/job/runtime/API path;
`artifacts/` contains the exact inert products; `fixtures/` captures required
scientific cases; `performance/` contains 4/5,000/100,000-row timings; and
`browser/` contains Chromium/Firefox/WebKit/mobile product evidence.

Regenerate backend evidence with:

```text
uv run python scripts/generate_phase10k2_dataset_explorer_evidence.py
```

Regenerate browser evidence with:

```text
node apps/web/test/dataset-materials-explorer-browser-evidence.mjs
```

The evidence contains no private absolute path, secret, real LLM call,
external request, external asset, artifact JavaScript, or dependency payload.
