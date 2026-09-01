# Chat / Research Control Contract

## Re-interpret existing scientific results

Modern ResearchTurn presentations may offer `重新解释（不重算科学结果）`
when the user is inside an authorized Research Session. The control creates a
new immutable ResearchTurn carrying the prior Result identity in its explicit
context and routes through the normal Agent2 action router. It never mutates
the historical Turn and cannot directly enqueue scientific work. If reuse is
not eligible, the existing router/planner semantics remain authoritative and
must fail closed or perform an explicitly new analysis.

Research controls are explicit actions over immutable execution history:

* Edit latest user message → new message revision and new ResearchTurn branch.
* Branch → preserves the old branch and exact source/result identities.
* Stop planning/orchestration → `CANCELED` with no Job where possible.
* Stop queued/running work → `CANCELING` then `CANCELED` or `PARTIAL`.
* Continue → reuses authorized session context and exact valid Results when
  eligible.
* Rerun → creates a new execution lineage and never overwrites old evidence.
* Re-interpret → changes only grounded narrative; Job/ToolCall/Artifact/Result
  deltas must all be zero.
* Retry → explicit new attempt or bounded failed-step retry, preserving the
  failed record.

The existing backend cancellation boundary is
`ResearchTurnService.cancel_turn` and
`/api/research/turns/{turn_id}/cancel`. The complete message-revision,
branch-switching and distinct Continue/Rerun/Re-interpret UI contract is
partially qualified.

Current-worktree browser evidence:

* completed parent Turn `8382c443-f9ca-4c90-9aa3-444fea683807`;
* edit child Turn `7a2f5367-3984-4fa3-9a10-05599079b68b` keeps the exact
  `parent_turn_id`, while the parent message and scientific descendants remain
  immutable;
* re-interpret child Turn `c94850bb-33cf-49d2-9d07-32b17ca319b6` completed
  with `grounding=VALID` and reused ScientificResult
  `15fc4d39-d2d7-5ac3-907a-cb06ed6b7a3f`;
* re-interpret persisted deltas are Job `0`, ToolCall `0`, Artifact `0`,
  ScientificResult `0`.

Queued/running cancellation, Continue and failure recovery are qualified below.
The broader Phase 14-R mature-product gate remains open for capability-wide,
retention/export, context-stress and release qualification.

## Exact failed-Turn recovery and bounded conversation history

Retry and Edit resolve the exact selected `ResearchTurn` through its persisted
user-message and context relation. They no longer read the last user message
from the mutable session tail. A failed/canceled Turn presents recovery actions
below the terminal state:

```text
修改问题
重新研究（新运行）
```

The active-state command is labeled `停止研究`; it remains beside truthful
execution progress rather than competing with the composer.

Authenticated evidence:

* failed parent Turn `8080a173-5e9f-4aef-89b7-78fed81316c8`;
* retry child Turn `f6441688-5404-4a0f-aa9f-31e7692ef8de`;
* exact Dataset object/version
  `8a425466-b697-4c85-9a43-199414a22865` /
  `be02266a-7d4f-4ebb-9f28-3132855167d0`;
* exact `DATASET_SAMPLE` locator `mat-2`;
* before/after counts:
  ResearchTurn `314 → 315`, Job `208 → 208`, ToolCall `269 → 269`,
  Artifact `1070 → 1070`, ScientificResult `140 → 140`.

The router classified the exact retry question as `ANSWER`, which is valid:
retry creates immutable conversational lineage but does not force unnecessary
scientific execution.

Long sessions now render a bounded message window around the selected
authoritative user message. The same browser session defaulted to `5` rendered
articles and hid `45` unrelated historical messages; `查看完整会话` expanded to
all `50`, and `收起到当前分支` restored the bounded window without changing
stored history. Mobile width remained `390/390`.

## Grounded historical message projection (2026-08-30)

Research session reads preserve immutable stored messages while deriving the
visible scientific answer from the exact persisted Interpretation and
ScientificResultSnapshot. The canonical re-interpret branch:

```text
parent Turn = 1c57db79-7a3b-4f20-bd9a-f883cf29d54b
child Turn = 7c65deb0-5791-4340-b6e6-ead5a8733445
Result = 14ce2fd1-e5bc-4798-906f-3333df2f7a91
Interpretation = 6005f096-19d9-4a35-9e22-0d79e47e8a63
```

reopened through the normal authenticated Research route. The child visible
answer retained independent CrystalNN/VoronoiNN findings, removed internal
fact ID echoes and normalized the redundant phrase to `成功识别出 1 个配位位点`.
The projection cannot repair an unsupported scientific Finding: the unchanged
grounding validator must accept the complete projected Interpretation or the
immutable original remains visible as audit evidence.

This is a communication/read-model repair only. It does not change the
cancellation or execution authority.

## Authenticated queued/running cancellation and Continue recovery (2026-08-30)

The current-worktree same-stack browser campaign exercised both durable
execution phases against PostgreSQL, Redis, MinIO and the real Redis workers.
The worker was suspended only long enough to make the target state observable;
it was resumed for the normal cancellation acknowledgement and was never
terminated.

Queued cancellation:

```text
ResearchTurn = 76e51edf-f798-4771-930a-2011027ade96
Job = job_agent2_76e51edff7984771930a2011027ade96
observed state = QUEUED / 等待执行资源
cancel transition = CANCELING → CANCELED
final Job state = cancelled
ToolCall delta = 0
Artifact delta = 0
ScientificResult delta = 0
```

Running cancellation:

```text
ResearchTurn = e2789fe7-9322-4e0d-b43b-23981408e70c
Job = job_agent2_e2789fe793224e0db43b23981408e70c
observed state = RUNNING / 正在执行分析
cancel transition = CANCELING → CANCELED
final Job state = cancelled
ToolCall delta = 0
Artifact delta = 0
ScientificResult delta = 0
```

A separate fast-race Turn
`77129519-3449-4ae8-887a-beb88a23459d` completed before cancellation could
win. The product correctly reconciled to `COMPLETED` rather than falsely
overwriting durable scientific success with a canceled label.

The terminal recovery group now distinguishes:

```text
继续研究
修改问题
重新研究（新运行）
```

`继续研究` is intentionally non-executing. In the authenticated browser it
focused the existing research composer and displayed:

```text
继续研究会保留当前会话与已授权的精确上下文；
只有提交新问题后才会开始新的处理。
```

Before and after the click, the canceled running case retained one immutable
ResearchTurn, the same canceled Job, and `ToolCall/Artifact/ScientificResult =
0/0/0`. Browser warnings and errors were zero. Focused frontend coverage is
`2 files / 61 tests passed`.
