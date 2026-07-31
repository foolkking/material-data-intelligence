# Phase 10L-4 API and Frontend

Additive routes create/list interpretations per planner Job and retrieve one
interpretation or its evidence. Create accepts only mode, expected Plan hash,
bounded provider configuration, and optional idempotency key; it accepts no raw
Artifact IDs, custom prompt/schema, or tool list.

PlannerWorkbench shows mode, outcome, findings, warnings, limitations,
non-executable recommendations, evidence drill-down, provenance, partial state,
and inert audit JSON. Run/execution controls are unchanged. The surface is
keyboard operable, uses semantic status, and stacks without horizontal overflow
at 390x844.
