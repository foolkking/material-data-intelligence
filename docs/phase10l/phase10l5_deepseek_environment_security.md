# Phase 10L-5 DeepSeek Environment Security

The API key is loaded from the process environment variable `DEEPSEEK_KEY`.
It is never accepted in Planner request JSON, frontend state, prompt fields,
logs, artifacts, recipes, reports, browser captures, or evidence manifests.
The frontend only selects the server-side DeepSeek provider and never calls
DeepSeek directly.

The endpoint is fixed by code. The model is an allowlisted value. The provider
transport sends the key only in the transient Authorization header needed for
the HTTPS request; call audit and persistence receive hashes and sanitized
metadata, never the header.

Artifact payloads, paths, URLs, object-store keys, Registry implementation
details, and secrets are excluded from provider projections. Prompt injection
text remains inert untrusted text. Interpretation recommendations are display
only and carry `executionAuthorized=false`, `planCreated=false`, and
`jobCreated=false`.
