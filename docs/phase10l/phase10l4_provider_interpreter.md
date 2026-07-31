# Strict Provider Interpreter

The optional OpenAI-compatible mode receives only the provider-safe projection
of the exact evidence bundle, allowlisted claim vocabulary, partial state, and
strict output contract. It never receives raw Artifacts, arrays, paths, URLs,
secrets, full Registry data, source code, or execution authority.

Exactly one JSON object is accepted. Prose, fences, duplicate keys, unknown
fields, invented IDs/numbers/units/entities, HTML/code/path/URL content, and
over-cap output fail. One validation-guided repair may shrink or correct the
same evidence domain; a second repair and deterministic fallback are forbidden.
Default tests and evidence use `REAL_LLM_CALLS = 0`.
