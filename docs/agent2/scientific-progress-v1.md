# Scientific Progress v1

`ResearchProgressView 1.0` is a bounded product projection of real execution
facts. It is available from:

```http
GET /api/research/turns/{turn_id}/progress
```

The endpoint re-authorizes Turn Project access. The DTO contains Turn status,
the scientific plan title, capability-level steps, active/completed counts,
declared incremental outputs, warnings, terminal execution outcome, and the
`result_projection_pending` flag. It intentionally excludes Job IDs, Tool IDs,
ToolCall IDs, worker IDs, queues, provider metadata, storage keys, and secrets.

Progress labels come from registered Capability metadata through the
`ScientificProgressProjectorRegistry`. They are deterministic descriptions such
as “正在生成理论 XRD 图谱”; no LLM participates during execution. An output is
visible only after its Artifact row is committed and its step/type matches an
AnalysisPlan expected output.

Turn events project to product SSE names including `analysis.queued`,
`analysis.started`, `analysis.step.*`, `analysis.output.available`,
`analysis.canceling`, terminal execution status, and `result.pending`.
`Last-Event-ID` resumes from the next monotonic TurnEvent sequence.

The Research conversation renders this as a compact activity block under the
assistant pre-run message. Status is conveyed by text and symbols as well as
color; cancellation remains keyboard accessible and the activity never steals
focus from the composer.
