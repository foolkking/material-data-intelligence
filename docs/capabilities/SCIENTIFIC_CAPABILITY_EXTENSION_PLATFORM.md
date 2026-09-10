# Scientific Capability Extension Platform

Status: active canonical contract (2026-09-10)

## 1. Ownership model

The platform extends scientific behavior through existing authorities:

```text
Scientific Requirement
  -> CapabilityManifest / trusted Capability Pack
  -> deterministic eligibility and preconditions
  -> Tool Registry contract
  -> Adapter Registry implementation
  -> typed Artifact ports where composition is supported
  -> ScientificResult projector
  -> generic, supported, required, or absent presentation surfaces
```

These layers are intentionally distinct:

- **Requirement** describes a scientific need.
- **Capability** describes the scientific operation that can satisfy it.
- **Capability Pack** is a trusted declarative family and fingerprint boundary.
- **Tool** is the stable executable contract.
- **Adapter** is the trusted concrete implementation.
- **Artifact ports** make selected multi-step outputs composable.
- **ScientificResult projector** converts execution output into normalized,
  source-grounded knowledge.
- **Viewer / interpretation / report support** describes presentation
  compatibility; it does not execute science.

Capability Packs never load arbitrary code. Execution remains
`registered Tool -> registered Adapter`; planner metadata contains no Python
paths, worker internals, shell commands, or untrusted imports.

## 2. CapabilityManifest 1.2

`CapabilityManifest` keeps the existing identity, scientific purpose,
requirements, input/output slots, deterministic preconditions and Tool
bindings. Version 1.2 adds explicit extension completeness metadata:

| Contract | Meaning |
|---|---|
| `result_support` | Whether a ScientificResult projector is required, supported, generic, or intentionally absent. |
| `artifact_port_support` | Whether typed dependency ports are required/supported or the Tool's ordinary Artifact contract is sufficient. |
| `interpretation_support` | `REQUIRED`, `SUPPORTED`, `GENERIC`, or `NONE`; explicit support requires an `interpretation_profile`. |
| `viewer_support` | Explicit presentation support; required/supported modes require trusted Viewer IDs. |
| `report_support` | Explicit report support; required/supported modes require a report projector binding. |
| `planner_visibility` | Whether an active capability may enter the bounded planner catalog. |
| `resource_profile` | Conservative hints; Tool Registry resource/cost metadata remains authoritative by default. |
| `execution_policy` | Retry, idempotency, partial-output and durable-boundary resumability metadata for Workstream A. |
| `qualification` | Structural/scientific qualification level and evidence pointers. Structural validity is not scientific-quality proof. |

Manifest 1.1 remains readable. New built-in manifests serialize as 1.2.

## 3. Eligibility and planning

Eligibility remains deterministic:

1. resolve authorized exact scientific object/result references;
2. match typed input slots;
3. evaluate registered hard preconditions;
4. verify a compatible Tool version exists;
5. return eligible, conditional, or ineligible candidates with reason codes.

The resolver now rejects any selected source outside the owning
`ResearchTurn.project_id` before planning.

`CapabilityExtensionRegistry.eligible_catalog()` is the planner projection.
It includes scientific purpose, requirements, typed inputs/outputs,
limitations, surface support, resource hints and a contract fingerprint. It
does not include Tool bindings or Adapter implementation names.

## 4. Artifact composition

Ordinary standalone capabilities may use the Tool Registry Artifact contract
without typed dependency ports. Capabilities declaring `SUPPORTED` or
`REQUIRED` typed ports must resolve valid port metadata.

`REQUIRED` is used where an execution step consumes a durable output from an
earlier step. Current reference paths include:

```text
trajectory.msd -> trajectory.diffusion
phonon.band + phonon.dos -> phonon.band_dos
structure.xrd -> structure.experimental_xrd_comparison
```

Port compatibility is checked by artifact kind, contract version, media type,
cardinality, maximum size, semantic role, provenance and inert-data trust.

## 5. Result and presentation

Every current Agent capability produces a typed `ScientificResult` through a
registered canonical projector. Projectors own facts, figures, tables,
evidence, methods, limitations and exact provenance; scientific algorithms
remain in their domain Adapter.

Presentation support is explicit:

- `GENERIC` means the platform's generic grounded interpretation/report or
  safe presentation fallback is intentional.
- `SUPPORTED` declares a registered specialized surface.
- `REQUIRED` fails completeness validation when its binding is missing.
- `NONE` is an intentional absence, not a forgotten integration.

Research UI should resolve semantic Result/Artifact descriptors rather than
make Tool IDs its scientific authority.

## 6. Completeness validator

Run:

```powershell
python scripts/capability_extension_report.py --check `
  --json-output docs/capabilities/generated/capability_inventory.json `
  --markdown-output docs/capabilities/generated/capability_inventory.md
```

The validator reads the canonical registries and checks:

- unique Capability and Pack ownership;
- known Requirements and scientific input/output types;
- deterministic preconditions;
- Tool existence and compatible versions;
- Adapter invocability;
- validated planner metadata;
- typed Artifact ports when declared;
- Result and progress projectors;
- explicit Viewer/interpretation/report support;
- deprecation/planner visibility consistency;
- dead Pack entries.

It also classifies non-Capability-reachable Tools, Adapters, projectors and
Viewer descriptors. Orphan classification is diagnostic and grants no cleanup
authority.

Current generated health:

```text
Capabilities = 17
Valid = 17
Incomplete = 0
Packs = 5
Tools = 62
Adapters = 50
Duplicate capability authorities = 0
```

The 45 registered Tools not currently Agent Capability-reachable are
classified as 33 public low-level Tools and 12 future/experimental Tools.
They are not deletion candidates. Five unbound Viewer descriptors are
classified as source-viewer or presentation-extension surfaces.

## 7. Versioning and deprecation

Capability, Tool, Adapter, Artifact schema and projector versions retain
separate meaning. Capability Pack contract and binding fingerprints preserve
the difference between scientific contract changes and implementation binding
changes. Historical Plans and Results retain the identities used at execution.

Deprecated capabilities remain readable but are excluded from the active
planner catalog. Existing historical Results are never rewritten.

## 8. Security boundary

- Manifests use strict typed models with unknown fields forbidden.
- Executable string conditions and executable Viewer bindings are rejected.
- Planner selection cannot create a Tool or Adapter identity.
- Project/source authorization occurs before capability planning.
- Artifact dependency ports accept inert data only.
- Capability metadata cannot bypass Tool/Adapter registries, lifecycle
  controls, Artifact validation or ScientificResult grounding.

## 9. Known hotspots

The extension path is now explicit and automatically validated, but built-in
registration is still concentrated in several authority files:

- Requirement registration;
- built-in Capability definitions;
- Tool YAML manifests;
- Adapter class registration;
- canonical Artifact-port declarations;
- canonical Result projector contracts;
- optional Viewer descriptors.

This is bounded central coupling, not duplicate authority. A later change may
make built-in scientific-family modules contribute these declarations without
altering identities. Do not introduce untrusted dynamic loading to remove a
few explicit registrations.
