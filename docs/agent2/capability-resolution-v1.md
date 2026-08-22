# Capability Resolution 1.0

`CapabilityResolutionService` deterministically maps validated Phase 2
requirements and exact context-snapshot refs to registered manifests. It
reauthorizes logical object, immutable version, Project, type and availability
before resolution.

- `ELIGIBLE`: every direct required input is bound and an executable Tool
  version is available.
- `CONDITIONAL`: a required input is absent now but a registered candidate
  output has an exact compatible result/object type.
- `INELIGIBLE`: type, availability, precondition, producer path or executable
  Tool version fails.

Resolution order and the registry fingerprint are canonical. The fingerprint
covers manifest versions, requirements, ports, preconditions, Tool bindings
and relevant Tool versions. One immutable resolution row is stored per Turn
before any optional capability-planner provider call.
