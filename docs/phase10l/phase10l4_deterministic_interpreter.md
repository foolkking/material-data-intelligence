# Deterministic Interpreter

`phase10l4.deterministic.v1` converts validated evidence into stable direct
observations, warnings, limitations, non-executable follow-up suggestions, and
`NO_SUPPORTED_CONCLUSION` where appropriate. Ordering, IDs, rendering, and
hashes are deterministic; duplicate claims are suppressed.

It does not call an LLM, re-run science, dump raw evidence, or infer causal,
stability, validation, or deployment conclusions.
