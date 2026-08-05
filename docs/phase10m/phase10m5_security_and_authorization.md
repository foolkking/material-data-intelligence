# Phase 10M-5 Security and Authorization

Every API resolves authorization through Project, Workspace, source Job,
Report/Recipe pair, panel, Artifact, Claim, and Evidence. Workspace ID alone is
not authorization. Exact checksum/version/hash checks reject cross-project,
cross-job, stale, tampered, missing, and URL-injected identities.

Artifact content and all user/source strings are inert. HTML, script, iframe,
SVG event handlers, JavaScript/data URLs, external URLs, module paths, path
traversal, duplicate keys, non-finite numbers, deep/oversize JSON, malicious
filenames, credential-shaped text, and Content-Disposition injection are
rejected or rendered as plain text.

Report has no Python, shell, filesystem, provider, scientific recomputation, or
claim-generation authority. Recipe has no Plan, Job, ToolCall, queue, Adapter,
or automatic replay authority. M5 adds no LLM call site:

```text
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0
REPORT_COMPOSITION_PROVIDER = NONE
RECIPE_COMPOSITION_PROVIDER = NONE
```

The permanent provider policy remains DeepSeek-only through `DEEPSEEK_KEY` for
future separately authorized real calls; M5 does not read that key.
