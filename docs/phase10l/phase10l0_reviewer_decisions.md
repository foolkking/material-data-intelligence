# Phase 10L-0 Reviewer Decisions

Status: `REVIEWER_GATE`. No item below is an implementation authorization.

## Decisions Required Before Phase 10L-1

1. **Analysis Intent shape**: approve a standalone strict schema or a minimal
   extension around PlannerRequest. Audit recommendation is standalone intent
   because current intent is only a raw string.
2. **Ambiguity and clarification**: decide whether Initial Release includes a
   typed clarification outcome or only explicit safe rejection with guidance.
3. **Planner capability metadata ownership**: decide whether semantic
   eligibility is additive Registry metadata or a separate resolver keyed by
   Profile readiness capability.
4. **AnalysisPlan evolution**: decide whether intent identity, provider/prompt
   provenance, and plan caps require an additive AnalysisPlan version.
5. **Bounded multi-tool model**: choose ordered sequence with explicit artifact
   bindings or a restricted dependency graph. A generic DAG is not recommended.
6. **Failure/cancellation policy**: define whether independent completed
   artifacts yield partial success and how cancellation is checked between
   steps.
7. **Plan repair**: decide whether Initial Release permits one bounded
   validation-guided repair attempt, deterministic fallback only, or rejection
   without repair.
8. **Pre-execution user control**: decide whether plan approval/editing belongs
   in Phase 10L or is deferred to Phase 10M Workspace.
9. **Interpretation provider policy**: define structured context budget,
   untrusted-content labeling, no-invention contract, and default-CI mock path.

## Facts That Do Not Need Re-Decision

* Agent is the user-facing orchestration concept; Planner produces plans;
  Runtime executes them deterministically.
* LLM output is JSON only and has no direct execution authority.
* Tool Registry validation and registered Adapters are mandatory.
* PlanValidator runs before plan persistence and job creation.
* DataProfile is deterministic data truth.
* Scientific calculations are backend operations, not LLM operations.
* Existing Profile 2.0, Registry, persisted plan/hash, QueueWorkerRuntime,
  events, artifacts, summaries, and recipes are reusable foundations.

## Queue Barrier

After Phase 10L-0 archive:

```text
Phase 10L-0: ARCHIVED
Phase 10L-1: REVIEWER_GATE / AWAITING REVIEWER PROMPT
```

Do not add an executable Phase 10L-1 task until reviewer/user approval supplies
its complete prompt.
