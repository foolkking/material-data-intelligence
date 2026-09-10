# Workstream C — Scientific Capability Extension Platform

状态：已完成
授权日期：2026-09-10
完成日期：2026-09-10
Canonical repository：`E:\1project\mdi-b0-5a1`

## Mission

Strengthen the existing scientific extension architecture:

```text
Requirement
→ Capability
→ Capability Pack
→ Tool
→ Adapter
→ Plan Step
→ Artifact
→ ScientificResult
→ Interpretation
→ Viewer
→ Report
```

Do not replace this architecture. Turn its implicit integration requirements
into explicit, deterministic, inspectable contracts so a scientific developer
can add a conventional capability through bounded domain-local changes.

Workstreams A and B are closed. Preserve ResearchTurn lifecycle,
ContextSnapshot provenance, exact ScientificObject/Version identity,
ScientificResult authority, public APIs, authorization, queue/worker identity,
Tool IDs and Adapter IDs. Do not develop or run services from
`E:\1project\Material Data Intelligence`.

## Required reconnaissance

Inspect only capability-extension owners:

- requirements, capability manifests/packs, resolution and eligibility;
- Tool Registry, Tool manifests and input/output ports;
- Adapter Registry and implementations;
- AnalysisPlan binding and artifact contracts;
- ScientificResult projector registry and schemas;
- interpretation, viewer and report compatibility;
- scientific object type compatibility;
- planner-visible capability metadata;
- capability qualification/tests.

Trace representative Structure/local-environment, XRD, trajectory/MSD,
electronic, Dataset/analytics, ML and phonon/volumetric capabilities. Retain
existing mechanisms when they already solve the requirement.

## Extension contract

A complete capability must explicitly declare, using existing contracts where
possible:

```text
identity/version/status
scientific purpose/domain
requirements satisfied
accepted scientific input types
deterministic preconditions
Tool binding
Adapter binding
input/output Artifact ports
Result projector mode
Result semantics
interpretation support
viewer support
report support
planner visibility
resource/cost class
retry/idempotency characteristics where relevant
qualification status/limitations
Capability Pack ownership
```

Optional surfaces must be explicit (`REQUIRED`, `SUPPORTED`, `GENERIC`,
`NONE`, or compatible existing vocabulary). Absence must not be accidental.
Structural completeness does not establish scientific-quality PASS.

Keep distinctions:

- Capability = scientific operation.
- Tool = stable executable contract.
- Adapter = trusted concrete scientific implementation.
- Capability Pack = declarative scientific-family extension unit.
- Executable behavior remains behind Tool Registry and Adapter Registry.

Never allow manifests to introduce arbitrary imports, `eval`, `exec`, shell,
filesystem or network execution.

## Eligibility and planner projection

Requirements describe scientific needs, not implementation names.
Eligibility and hard preconditions are deterministic and expose structured:

```text
ELIGIBLE
INELIGIBLE
UNSUPPORTED
MISSING_INPUT
AMBIGUOUS
```

Eligibility determines what is allowed; planning selects among eligible
options. Planner-visible projections remain compact, scientific and traceable
through Workstream B ContextSnapshot metadata. They must not expose Python
paths, worker internals or arbitrary Adapter implementation details.

## Ports, execution and recovery

Artifact ports must describe semantic type/schema/cardinality, units where
relevant, source relationships and downstream compatibility. Validate
multi-step Plan compatibility before execution where practical. Avoid
tool-specific central conditionals when existing registries/descriptors can
own the mapping.

Capability execution must continue through the Workstream A authority:

```text
Plan → Job → ToolCall → Artifact → ScientificResult
```

Preserve stage ownership, duplicate-delivery safety, recovery, cancellation
and provenance. Capability metadata may conservatively expose retryability,
idempotency, partial-output and non-resumable characteristics without becoming
a second lifecycle authority.

## Result, interpretation and presentation

Every producing capability explicitly declares whether it uses a generic
projector, typed projector, or intentionally produces no ScientificResult.
Projectors normalize facts, figures, tables, evidence, methods, limitations
and exact provenance while domain algorithms stay domain-local.

Interpretation, Viewer and Report compatibility must be explicit. The platform
must support generic or no-viewer/no-report cases without treating them as
missing integration. Central Research UI and report code must not dispatch on
Tool IDs when semantic Result/Artifact descriptors can resolve presentation.

## Completeness validator and generated inventory

Implement a validator over canonical registries—not a shadow registry—that
checks:

```text
unique capability identity
valid Capability Pack
known scientific input/result types
valid deterministic preconditions
referenced Tool exists and validates
referenced Adapter exists
valid Artifact ports and step compatibility
required Result projector exists
viewer/interpretation/report declarations are valid
planner metadata is valid and bounded
deprecation/status semantics are coherent
no conflicting identities
```

Generate machine-readable and human-readable inventory from live canonical
registry state. Report actual counts, extension coverage, experimental/
deprecated status and incomplete capabilities.

Classify—not mass-delete—orphans:

```text
Tool with no reachable capability
Adapter with no Tool
projector with no producer
viewer descriptor with no source/result
Capability with missing Tool
Pack with dead entry
```

Classifications may include public low-level Tool, internal Tool, compatibility
Tool, experimental/future component, or defect.

## Reference extension and authoring experience

Normalize one bounded existing capability as a reference if needed. Do not add
a fake user-visible scientific capability. Demonstrate the actual extension
path:

```text
manifest
→ Tool
→ Adapter
→ Artifact
→ Result
→ optional interpretation/viewer/report
→ validation
```

Create:

- `docs/capabilities/SCIENTIFIC_CAPABILITY_EXTENSION_PLATFORM.md`
- `docs/capabilities/ADDING_A_SCIENTIFIC_CAPABILITY.md`

The guide must use real repository examples and state exact authoring,
registration, validation and testing steps.

## Tests and runtime verification

Focused tests must cover:

- manifest/Pack validation and duplicate identity;
- missing Tool/Adapter;
- invalid input type, precondition, Artifact port and projector;
- optional Viewer/Interpretation/Report semantics;
- deprecation behavior;
- eligibility and structured reasons;
- bounded planner projection;
- multi-step port compatibility;
- authorization preservation;
- projector binding;
- inventory generation and orphan classification.

Run representative regression for Structure, XRD, Trajectory, Electronic,
Dataset and ML through real canonical registry/Adapter paths.

Run at least one canonical real-service Agent path:

```text
request → requirement → resolution → plan → Tool → Adapter
→ Artifact → ScientificResult
```

and one multi-step or presentation path where practical. Use only
qualification-owned data. Confirm API/workers load canonical code.

## Boundaries

Do not:

- reopen Workstream A/B or repository migration;
- change frozen Tool/Adapter/queue/handler identities;
- build a plugin marketplace or untrusted dynamic loader;
- introduce a workflow engine, scheduler or new distributed architecture;
- centralize domain scientific algorithms;
- create a giant central capability module;
- redesign Research UI;
- push or perform remote release qualification;
- delete user/runtime/history/qualification data.

Keep `transport → application → domain → infrastructure` directionality and
avoid duplicate capability authorities.

## Documentation and task closure

Update `docs/index.md`, `PROJECT_STATE.md`, `persistent/DESIGN_PROGRESS.md`,
`persistent/TASK_BOARD.md`, `persistent/CHANGELOG.md`, `results.md`, and close
the corresponding `TASKS.md` block only after tests and required canonical
runtime evidence pass.

## Completion gates

```text
CAPABILITY_EXTENSION_MODEL = COHERENT
REQUIREMENT_TO_CAPABILITY = PASS
CAPABILITY_ELIGIBILITY = DETERMINISTIC
CAPABILITY_PRECONDITIONS = EXPLICIT
CAPABILITY_TO_TOOL_BINDING = PASS
TOOL_TO_ADAPTER_BINDING = PASS
ARTIFACT_PORT_VALIDATION = PASS
CAPABILITY_TO_RESULT_PROJECTOR = PASS
OPTIONAL_VIEWER_SUPPORT = EXPLICIT
OPTIONAL_INTERPRETATION_SUPPORT = EXPLICIT
OPTIONAL_REPORT_SUPPORT = EXPLICIT
CAPABILITY_PACK_VALIDATION = PASS
CAPABILITY_COMPLETENESS_VALIDATOR = PASS
CAPABILITY_INVENTORY = GENERATED_FROM_CANONICAL_REGISTRIES
ORPHAN_COMPONENT_CLASSIFICATION = COMPLETE
PLANNER_CAPABILITY_CONTEXT = BOUNDED_AND_TRACEABLE
EXISTING_CAPABILITY_REGRESSION = PASS
REAL_SERVICE_CAPABILITY_PATH = PASS
DUPLICATE_CAPABILITY_AUTHORITY = 0
```

Final report must also state:

```text
SCIENTIFIC_CAPABILITY_EXTENSION_FOUNDATION = READY | PARTIAL
CENTRAL_FILES_REQUIRED_FOR_CONVENTIONAL_NEW_CAPABILITY = <count/summary>
KNOWN_EXTENSION_HOTSPOTS = <summary>
UNRESOLVED_CAPABILITY_PLATFORM_BLOCKERS = <count>
```

Directly answer whether a competent scientific developer can add a
conventional capability without deep knowledge of every Agent, worker, Result,
Viewer and Report implementation. Recommend the next workstream based on
actual findings: Agent autonomy/multi-step research or scientific quality/
evaluation.
