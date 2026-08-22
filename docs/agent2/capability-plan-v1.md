# Capability Plan 1.0

A `CapabilityPlan` contains at most eight typed steps. Each step selects a
supplied `cap_N`, records requirement coverage, preserves explicit parameters,
declares outputs from its manifest, and binds inputs as `SOURCE_OBJECT`,
`PREVIOUS_RESULT`, or `PLANNED_OUTPUT`. Dependencies are derived only from
planned-output bindings; there is no second dependency authority.

The validator rejects unknown/ineligible capabilities, unknown sources,
missing required requirements, cycles, forward/self dependencies, incompatible
producer/consumer ports and limit overflow. Optional requirements must be
listed when omitted.

Unique strategies use a deterministic fast path with no LLM. Alternative
strategies use `scientific-capability-planner/1.0`, opaque refs, Pydantic's
generated schema, typed capability input/output port views and at most one
bounded repair. The provider never sees Tool IDs or runs inside a database
transaction. A historical Result may bind as `PREVIOUS_RESULT` only when its
persisted bundle exposes an authorized exact-version ScientificObject output;
artifact-only runtime identities are not accepted as Plan 0.2 source inputs.
Provider-facing candidate views include only opaque bound source/result keys,
missing slots and compatible producer `cap_N` keys. Multiple producer or
reusable-result alternatives disable the deterministic fast path.
