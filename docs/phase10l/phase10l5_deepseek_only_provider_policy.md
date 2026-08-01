# Phase 10L-5 DeepSeek-Only Provider Policy

New real LLM calls are authorized only through `DeepSeekProvider`.

```text
provider = DeepSeekProvider
base URL = https://api.deepseek.com
key source = DEEPSEEK_KEY only
allowed models = deepseek-v4-flash, deepseek-v4-pro
```

`OpenAICompatibleProvider` remains a historical/fake-transport compatibility
path. It cannot make a new network call. OpenAI, Anthropic, custom endpoints,
alternate environment keys, frontend keys, and per-request credentials are
rejected. Provider call audit stores purpose, model, prompt/response hashes,
sizes, token usage, elapsed time, and sanitized outcome only.

The DeepSeek provider is used for intent extraction, capability selection,
bounded composition, and strict grounded interpretation. Provider output is
always strict JSON and is validated by platform-owned schemas and validators.
There is no silent fallback from a DeepSeek failure to Mock or deterministic
output.
