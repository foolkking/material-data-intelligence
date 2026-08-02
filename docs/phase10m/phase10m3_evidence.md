# Phase 10M-3 Evidence

Sanitized evidence is retained at
`docs/phase10m/evidence/phase10m3_canonical_selection/`.

It contains entry/M2 archive facts, the seven acceptance mappings, identity and
subscription matrices, codec/store/compatibility/security cases, database
write audit, DeepSeek policy regression, Chromium/Firefox/WebKit and Chromium
390x844 captures, console/network audits, screenshots, and a SHA-256 manifest.

The browser runner uses bounded metadata fixtures and is explicitly not a fake
natural-language or fake-provider claim. It validates only selection behavior.
Text evidence is LF-normalized before hashing; PNG bytes are hashed raw.
PostgreSQL/Redis/MinIO closure is owned by exact-SHA CI when local services are
unavailable.
