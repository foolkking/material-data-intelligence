# Phase 10L-3 Evidence Contract

Canonical evidence path:

```text
docs/phase10l/evidence/phase10l3_bounded_multi_tool/
```

## Required Evidence Groups

| Group | Required facts |
|---|---|
| Entry | baseline, L2 archive, queue admission, source map |
| Registry | 38-tool inventory, 1.0/1.1 metadata, exact port matrix |
| Planning | 0.2 schema, deterministic IDs/hashes, Mock and strict fake-provider composition |
| Real chain | phonon band and DOS producers into `phonon.band_dos` |
| Runtime | persisted exact plan, topological execution, binding resolution, replay |
| Failure | producer/consumer failure, blocked descendants, independent branch continuation |
| Validation | cycles, caps, unknown steps, duplicate ports, contract/scope/checksum/size failures |
| Persistence | migration, SQLite/PostgreSQL, immutable records, 0.1/0.2 round-trip |
| API | PLAN_READY, graph/read routes, non-ready no-side-effect cases |
| Browser | Chromium, Firefox, WebKit, 390x844 mobile, accessibility, overflow |
| Security | provider isolation, inert payloads, paths/URLs/code rejection, secret scan |
| Performance | legal near-cap graph, bytes, time, memory, row counts, replay growth |
| Compatibility | historical 0.1 hashes/jobs/artifacts and L1/L2 regressions |

The checked-in inventory currently records the actual 38 available tools and
selected phonon chain. It is audit input, not sufficient runtime evidence.

## Integrity

Text captures must be sanitized, deterministically ordered where applicable,
normalized to LF before SHA-256, and free of local-user paths and credentials.
PNG hashes cover raw bytes. `evidence_manifest.json` must cover every retained
evidence file without including itself.

## Current State

Current local state after deterministic generation and browser replay:

```text
artifact inventory = PRESENT
runtime/API/browser/performance/security captures = PASS
Chromium/Firefox/WebKit/390x844 = PASS
evidence manifest = PASS
service-backed local = UNAVAILABLE (services not configured)
service-backed exact-SHA CI = PENDING
exact-SHA CI = PENDING
```

The browser replay consumes the real generator's persisted plan/runtime/API
captures; it does not invent dependency IDs or execution states. These values
are updated only from real commands and captures.
