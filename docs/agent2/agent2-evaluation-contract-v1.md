# Agent 2.0 Phase 2 Evaluation Contract

`evaluation/fixtures/phase2_p0.json` is a strict Pydantic-validated set of C01
through C15. Every case has one canonical message and at least three Chinese or
English paraphrases. It covers routing, object/result reference resolution,
clarification, parameter preservation, report/data/open classification, stale
Result reuse, cross-Project rejection, unknown-key/Requirement injection, and
prompt injection inside scientific metadata.

The deterministic suite validates all 60 case/message combinations with a
controlled provider decision. It proves schema, reference, Requirement,
constraint, action and safety enforcement; it is not reported as live model
accuracy.

Live tests require both `MDI_RUN_AGENT2_LIVE=1` and `DEEPSEEK_KEY`. The
canonical qualification covers C01, C02, C03, C05 and C07. The paraphrase gate
runs every provider-routable valid case and requires at least 95%. C05 remains
a provider-free deterministic clarification. C11-C13 remain deterministic
security/invalid-output cases rather than asking a provider to attack itself.

Ordinary CI sets no live gate and runs all deterministic evaluation tests. Live
qualification never replaces fake-provider tests.
