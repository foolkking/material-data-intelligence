# Agent and Report Quality Evaluation

Evaluation combines deterministic correctness, structured rubric review and
real-user inspection. LLM-as-judge is supplemental only.

The versioned evaluation set must include simple, ambiguous, multi-step,
continuation, reuse, historical comparison, partial failure, unsupported
request, wrong-assumption, large Dataset, synthesis, stop/edit/rerun and
re-interpret cases across every currently declared capability family.

Score:

```text
intent understanding
context selection
clarification quality
capability/tool-plan correctness
over-analysis / under-analysis
grounding and limitations
scientific usefulness and relevance
conversation naturalness
latency
Report structure, coherence, evidence and conclusion quality
```

Each case stores exact source/version, Turn/Job/Result/Report identities and
whether science was recomputed. A quality failure must not be hidden by
changing deterministic acceptance criteria.

