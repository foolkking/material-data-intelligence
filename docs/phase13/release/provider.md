# Provider Policy

## Mode A: deterministic reproduction

Required release reproduction uses the deterministic/replay provider, requires no `DEEPSEEK_KEY`, and makes zero real LLM calls.

## Mode B: optional bounded DeepSeek verification

The only live provider is DeepSeek at `https://api.deepseek.com`, using `deepseek-v4-flash` or `deepseek-v4-pro` and the `DEEPSEEK_KEY` environment variable. Calls are bounded; retry-until-pass is forbidden. The provider produces structured planning/explanation output and cannot directly execute Tools or science.

A live-provider PASS is supplemental connectivity/planning evidence. It is not scientific validation or reference validation. Phase 13-3 performs zero real LLM calls.
