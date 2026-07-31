# Phase 10L-4 Evidence

Sanitized evidence is retained under
`evidence/phase10l4_grounded_interpretation/`. It includes contract schemas,
five supported families, the L3 phonon dependent chain, partial/no-evidence/
integrity outcomes, provider isolation and adversarial grounding, API and
persistence audits, performance/security markers, Chromium/Firefox/WebKit and
390x844 captures, DOM/network/console audits, raw PNG hashes, and an
LF-normalized SHA-256 manifest.

Local evidence does not substitute for verified queue closure. Corrected
implementation exact-SHA CI run `30606774006` passed PostgreSQL/Redis/MinIO,
Alembic, all 31 selected service-backed tests, and the zero-skip assertion.

Browser captures are real Chromium/Firefox/WebKit UI runs over route-fulfilled
fixtures generated from persisted API/runtime cases. They prove rendering,
interaction, accessibility, inert content, network isolation, and semantic
replay. They do not substitute for service-backed backend E2E, which remains an
exact-SHA CI gate.
