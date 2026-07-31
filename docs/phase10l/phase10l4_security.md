# Phase 10L-4 Security Boundary

Artifact text is inert and raw payloads are not provider context. Prompt
injection, HTML/script, credential-shaped strings, paths, URLs, duplicate JSON
keys, invented identities, stale/cross-scope lineage, and checksum mismatches
are rejected or excluded before claims.

Interpretation has no Python, shell, filesystem, network, Tool Registry,
ToolCall, Plan, Job, queue, iframe, HTML, or JavaScript execution authority.
Evidence captures are sanitized and secret-scanned.
