# Research Orchestrator Contract v1

The Phase 2 Orchestrator classifies a ResearchTurn. It does not select Tools,
create an AnalysisPlan or Job, execute code, interpret scientific evidence, or
compose a Report.

## Provider boundary

`StructuredLLMClient.generate_structured()` is the only orchestration provider
interface. `DeepSeekStructuredLLMClient` adapts the existing server-managed
DeepSeek transport and resolves `DEEPSEEK_KEY` only inside that transport. The
key, provider configuration, cookies, storage paths, and complete provider
request are never persisted in Turn context or decisions.

The versioned prompt is `research-orchestrator/1.0`. Its output schema comes
only from `ResearchTurnDecision.model_json_schema()`. The provider receives
authorized compact context and registered Scientific Requirement IDs, never
Tool Registry manifests or adapter implementations.

## Transaction sequence

```text
TX A: CAS claim -> assemble/authorize -> persist snapshot -> ORCHESTRATING
COMMIT
DeepSeek structured request (no open UnitOfWork transaction)
TX B: validate -> reauthorize -> persist immutable decision/message/events
COMMIT
```

Schema or semantic failure permits one repair. Repair input is bounded to the
validation error, legal opaque keys, registered requirement IDs, and the same
Pydantic schema. A second failure marks the Turn with a typed safe error.

## Wakeup and idempotency

Post Turn remains a short `202 Accepted` transaction. When
`MDI_AGENT2_ORCHESTRATION_ENABLED=1` and `MDI_QUEUE_BACKEND=redis`, it submits
an RQ wakeup whose sole function argument is `turn_id`. Database state is
canonical. Duplicate queue delivery loses the RECEIVED CAS and performs no
provider call. The default local/CI configuration leaves orchestration wakeup
disabled, so ordinary tests never consume a live provider.
