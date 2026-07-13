# API and Runtime Evidence

Evidence under `evidence/phase10g1_trajectory_parser_adapter/` drives both valid EXTXYZ and canonical JSON through upload parser semantics, normalized object, fixed Plan, PlanValidator, Tool Registry, QueueWorkerRuntime, artifact storage/listing, and trajectory/summary/manifest validators. Invalid truncation and over-byte-cap cases create zero artifacts.

`structure.trajectory_import` is execution-stage registered because the current PlanValidator admits MVP-stage tools only, but it is explicitly planner-hidden and has no Mock Planner route. Formal user-facing trajectory registration is deferred to viewer product closure.
