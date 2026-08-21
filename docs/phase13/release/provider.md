# Provider Policy

## Mode A: deterministic reproduction

Required release reproduction uses the deterministic/replay provider, requires no `DEEPSEEK_KEY`, and makes zero real LLM calls.

## Mode B: optional bounded live-provider verification

The built-in server environment profile remains available for bounded DeepSeek
verification. In addition, the product can store a user-entered
OpenAI-compatible connection (`provider`, `baseUrl`, encrypted API key). Calls
are bounded; retry-until-pass is forbidden. A provider produces structured
planning/explanation output and cannot directly execute Tools or science.

## Server-hosted Provider API contract

The provider API is intentionally provider-agnostic at the metadata boundary.
`GET /planner/providers` returns server-owned profiles with at least:

```text
provider, kind, baseUrl, defaultModel, allowedModels,
configurationSource, secretSource, execution
```

`GET /planner/providers/status` and the `resolve`/`test` routes return the same
redacted contract fields plus status and typed diagnostics. A connection is
created with `POST /planner/providers/configure`, model ids are discovered with
`GET /planner/providers/{provider}/models`, the selected model group is saved with
`PATCH /planner/providers/{provider}/models`, and removed with
`DELETE /planner/providers/{provider}`. The API key is encrypted server-side,
never returned, and never enters prompts, artifacts, reports or exports.

The live custom connection adapter currently implements the OpenAI-compatible
protocol. Anthropic-native or other non-compatible protocols still require an
explicit server adapter; the UI does not claim universal vendor support.

A live-provider PASS is supplemental connectivity/planning evidence. It is not scientific validation or reference validation. Thinking depth is a bounded provider-neutral preference (`quick`, `standard`, `deep`), not hidden chain of thought. Phase 13-3 performs zero real LLM calls.
