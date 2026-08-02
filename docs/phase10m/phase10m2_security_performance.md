# Phase 10M-2 Security and Performance

Initial loading performs one cancellable `GET /workspaces/{workspaceId}` and
uses a request generation guard to discard stale responses. The aggregate is
metadata-only and panel switching does not request Artifact content. Browser
evidence covers 1, 8, and 32 panels plus 20 repeated switches. Measurements
are development/browser acceptance evidence, not a production capacity claim.

Workspace text and audit JSON are inert React text. The shell contains no
artifact script, HTML execution, iframe, dynamic module, external Artifact
URL, tool/Job/enqueue authority, provider authority, scientific calculation,
or recommendation execution. Cross-project and source authorization remain
owned by the M1 API. `REAL_LLM_CALLS = 0` and `M2_NEW_LLM_CALL_SITES = 0`.
