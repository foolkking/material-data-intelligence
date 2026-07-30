# Phase 10L-3 API and PlannerWorkbench Surface

Status: additive implementation surface; browser and service-backed evidence
remain pending.

## Canonical Planning API

The existing Planner create path keeps the Phase 10L-1 and 10L-2 gates. For a
valid dependency composition it additionally returns:

- `plan_schema_version = 0.2`;
- `graph_hash`;
- exact `dependency_bindings`;
- deterministic `topological_order`;
- the existing Intent, eligibility, decision, plan, job, and enqueue fields.

The plan and queryable binding audit rows are persisted before the job is
attached and enqueued. Dependency validation runs before the unchanged
PlanValidator. A non-`PLAN_READY` result continues to create no plan, job, or
queue message. An invalid 0.2 plan is never retried as 0.1.

## Read API

`GET /planner/jobs/{job_id}` adds a bounded `dependencyExecutionSummary`.

`GET /planner/jobs/{job_id}/dependencies` returns the job-scoped audit view:

- plan ID/hash/schema and graph hash;
- dependency bindings and planned binding rows;
- final topological order and execution record;
- runtime binding resolutions;
- artifact lineage records.

For a 0.1 job, the same route returns the plan identity with empty dependency
collections. Read routes do not execute, repair, or replan.

## PlannerWorkbench

The additive dependency panel is rendered only for AnalysisPlan 0.2. It shows:

- schema and graph identity;
- deterministic topological order;
- producer/output-port to consumer/input-port cards;
- exact artifact kind and contract version;
- binding resolution state;
- per-step runtime state and blocked reason;
- retained artifact lineage;
- inert developer/audit JSON when Developer mode is enabled.

The semantic ordered list and stacked dependency cards provide a non-graph
representation. Cards are keyboard focusable, the panel uses `aria-live`, and
mobile CSS stacks fields to avoid requiring a graph library. The UI does not
author edges, edit plans, invoke Adapters, or render artifact HTML/JavaScript.

The Run gate remains tied to the validated canonical planning outcome. The
frontend does not infer dependency success from step order or display state.
