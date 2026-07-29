# Phase 10L-1 Security and Caps

## Caps

| Resource | Limit |
|---|---:|
| Raw goal | 16,384 characters |
| Resource refs | 32 |
| Scientific intents | 16 |
| Target semantics | 32 |
| Desired outputs | 32 |
| Ambiguities | 32 |
| Clarification questions | 3 |
| Clarification rounds | 1 |
| Diagnostics per array | 32 |
| JSON depth | 12 |
| Serialized intent | 262,144 bytes |

All identities, labels, prompts, values, and provider metadata also have field
length bounds. Profile facts and LLM prompt context are capped before use.

## Trust Boundary

Intent JSON is inert data. It gains no shell, filesystem, network, notebook,
script, artifact JavaScript, HTML, callback, or Tool Registry authority.
Credential-shaped values are redacted before persistence/provider context;
instruction-like text is recorded as inert warning text. The frontend renders
contract JSON in a `pre` element and uses no raw HTML.

The strict LLM path rejects Markdown fences, extra prose, duplicate JSON keys,
unknown fields, invented dataset/Profile/resource/target/question identity,
over-cap arrays, and inconsistent READY/ambiguity states. Default tests and
evidence make zero real LLM calls and no external requests.
