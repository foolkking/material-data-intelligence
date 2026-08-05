# Phase 10M-6 Security and Compatibility

Workspace, URL, Artifact, Report, Recipe, and recovery strings remain untrusted inert data. M6 adds no HTML/JavaScript/iframe/module/URL execution, shell/filesystem/network authority, scientific computation, identity inference, source rebinding, execution retry, or browser persistence authority. Typed API errors do not expose stack, path, storage key, secret, or Authorization data.

M1-M5 contracts, migration 0007, Report/Recipe persistence, renderer registry, scientific Adapters, Plan 0.1/0.2 behavior, Artifact hashes/lineage, and DeepSeek-only provider policy are unchanged.

```text
NEW_LLM_CALL_SITES = 0
M6_SAVE_RELOAD_RECOVERY_REQUIRES_LLM = NO
REAL_LLM_CALLS = 0
DEEPSEEK_POLICY_REGRESSION = PASS
WORKSPACE_COPIED_ARTIFACT_PAYLOADS = 0
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
FRONTEND_SCIENTIFIC_RECOMPUTATION = NONE
```

The complete marker list is retained in `evidence/phase10m6_workspace_recovery_closure/security_summary.md`.
