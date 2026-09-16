# Research Control Semantics

Date: 2026-09-10

These controls project existing durable lifecycle behavior. UI state never
becomes execution authority.

| Control | Scientist-facing meaning | Durable behavior |
|---|---|---|
| Start analysis | Submit the current research question | Creates a validated ResearchTurn/plan path only after authorization and scientific scope validation |
| Bounded multi-step research | Permit additional scientifically justified analyses within fixed limits | Activates the existing bounded autonomy policy; it is not unrestricted autonomy |
| Stop autonomous research | Prevent another autonomous cycle | Preserves completed Results and current durable state |
| Cancel current analysis | Request cancellation of currently active work | Does not erase completed Artifacts, Results, or Interpretations |
| Continue current research | Continue from the existing question/evidence context | Reuses the current session/branch and existing exact Results where valid |
| Retry failed analysis | Retry from the latest safe durable boundary | Reuses completed upstream science; does not restart successful stages |
| Run analysis again | Intentionally create a new execution | May recompute even when an older Result exists |
| Reinterpret | Create a new grounded Interpretation of an existing Result | Performs no scientific recomputation |
| Edit question and create branch | Revise the premise without rewriting history | Creates an immutable research branch; original Results remain readable |
| Start new research | Begin an unrelated research context | Does not inherit unrelated memory or silently reuse stale evidence |

## Unsupported and clarification states

If scope or parameters are insufficient, no run is created. The timeline says
`未创建分析运行`, identifies the missing scientific requirement in plain
language, and keeps the original question visible.

Clarification asks only for an authoritative user choice such as a target
property, comparison source, exact version, algorithm, or fit interval. After
the answer, the same research context continues.

## Failure and partial success

A failure surface answers:

1. what failed;
2. why it failed in scientist-facing language;
3. which completed science remains;
4. which recovery action is valid.

Raw validation payloads, stack traces, Pydantic messages, worker state, and
provider prompts are not normal user copy.

