# Phase 10L-5 Security Audit

- `REAL_LLM_CALLS = 0` applies to default CI and browser replay.
- `LIVE_GATE_REAL_LLM_CALLS = 16` applies only to the controlled DeepSeek suite.
- `OTHER_REAL_PROVIDER_CALLS = 0`.
- `DEEPSEEK_KEY` is the only credential source; the value is never persisted.
- No raw provider payload, Authorization header, artifact payload, private path, external artifact URL, or secret is retained.
- Provider output has no Tool, Plan, Job, Queue, shell, filesystem, or recommendation execution authority.
- `NO_SECRET_PATTERN_HITS`.
