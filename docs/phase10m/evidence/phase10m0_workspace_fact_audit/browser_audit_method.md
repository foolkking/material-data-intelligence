# Browser Fact Audit Method

The current browser audit uses the existing `natural-language-closure-browser-evidence.mjs` runner with:

- current repository source at the Phase 10M-0 audit commit;
- Chromium, Firefox, WebKit, and Chromium 390x844;
- locally served Next UI;
- route-fulfilled, persisted, sanitized Phase 10L captures;
- no live API forwarding;
- no live provider call;
- `DEEPSEEK_KEY` and `OPENAI_API_KEY` empty in the runner process;
- external network requests blocked and counted.

This proves current rendering and interaction against retained contract captures. It is not service-backed browser E2E and does not prove proposed Workspace behavior. The first audit attempt encountered a stale generated Next HMR chunk after local temporary/cache removal; the verified repository-local `.next` cache and incomplete audit output were deleted, then the audit was rerun from regenerated assets. No production source was changed.
