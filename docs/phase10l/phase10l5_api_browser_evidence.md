# Phase 10L-5 API and Browser Evidence

The canonical API remains additive. Existing Planner and interpretation routes
are used; no browser route is allowed to call DeepSeek. Five current-product
browser cases validate exact goal/profile/plan/interpretation identity and
display the persisted findings/evidence surface. Three typed non-ready states
(clarification, unsupported, and capability mismatch) are replayed from exact
real-DeepSeek historical responses; they create no plan, job, queue message, or
tool call.

The browser runner is
`apps/web/test/natural-language-closure-browser-evidence.mjs`. It verifies:

* Chromium, Firefox, and WebKit desktop coverage;
* Chromium at 390x844 mobile;
* exact frozen input and persisted plan identity;
* claim-to-evidence links;
* keyboard focus, semantic status, and non-graph accessible representation;
* no horizontal overflow;
* no console/page errors or unapproved requests;
* no iframe, HTML, script, external URL, secret, or private path execution.

This is intentionally capture-backed browser replay. It proves the product UI
and API contract without pretending that a browser replay is a new DeepSeek
call. The source captures are real DeepSeek records, while browser replay
itself makes zero live API/provider calls. Full historical LLM replay coverage
is documented in `phase10l5_real_provider_verification.md` and the evidence
matrix.
