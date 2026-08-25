# Agent-2.0 Phase 11 — Extensible Capability Platform 1.0

## Current implementation record

### Base

- Phase 10 sealed base: `fd23073009f92120d32efc710d57e457ed4c92ea`
- Alembic head remains `0025_agent2_scientific_selection`.
- No migration is required for the trusted declarative registry.

### Contract

`mdi_api.research_agent.capabilities.packs` adds a repository-trusted,
declarative `CapabilityPackManifest`, `CapabilityPackCapability`,
`PackValidationResult`, deterministic contract/binding fingerprints, and an
atomic `CapabilityExtensionRegistry`.

Packs contain existing `CapabilityManifest` contracts and references to
reviewed Tool/Result/Progress bindings. They cannot contain imports, executable
code, shell commands, arbitrary prompts, or remote installation instructions.
Validation is all-or-nothing and checks duplicate pack/capability identities,
requirements, object types, Tool Registry versions, projector bindings, and
preconditions.

### Agent boundary

The default Phase 10 capabilities are normalized through repository-owned
packs (`core.structure`, `core.electronic`, `core.data`, `core.trajectory`,
`core.other`) before being exposed to the existing resolver registry.
`eligible_catalog()` exposes semantic capability summaries only; raw Tool IDs,
adapter paths, and implementation internals are excluded.

### Regression evidence

- Existing Phase 10 manifests remain unchanged scientifically and continue to
  bind through AnalysisPlan 0.2, QueueWorkerRuntime, Tool Registry,
  ScientificResult projectors, and Phase 9 Viewers.
- Phase 10 regression plus Pack validation: `38 passed`.
- Invalid packs fail closed without partial registration.
- Contract fingerprints are stable for identical contracts and change for
  semantic contract changes.
- Unknown Tool, unknown Result projector, duplicate identities, disabled
  capabilities, prompt-injection fields, and raw Tool catalog exposure are
  covered by deterministic tests.

### Authenticated extension proof

Using the real Chromium executable supplied for acceptance and the same
PostgreSQL/Redis/MinIO stack, a natural-language Structure request completed
after the Pack boundary was active:

- Turn `dda9c25a-d198-459e-af2c-cddb8ecf860b`
- exact source object/version
  `773089f9-3ce8-4645-92dd-2f62c64cba89` /
  `65f56d10-008d-445d-ab2f-228aebf1835b`
- CrystalNN + VoronoiNN selected, normal Job/ToolCall/Artifact/Result path
- grounded interpretation `VALID`; Structure coordination Viewer available
- fatal errors `0`, unhandled rejections `0`, failed critical requests `0`

The browser catalog contained semantic capability data only; no raw Tool IDs
were sent as provider-facing catalog fields. The optional report lookup 404s
were the existing absence-of-report state and were not treated as failures.

Current worktree verification: backend `1798 passed / 83 skipped`, frontend
`582 passed`, typecheck PASS, production build PASS, touched Ruff PASS,
compileall PASS, `uv lock --check` PASS, and `git diff --check` PASS.
PostgreSQL/Redis/MinIO service-backed professional closure passed `1/1` when
run with the repository container credentials.

### Scope

This is a repository-trusted v1 extension boundary, not a marketplace or
dynamic code loader. Phase 11 does not add scientific algorithms, migrations,
arbitrary Python, or Tool Registry exposure to the Agent.

## Release status

P11-A/P11-B and exact-head CI remain to be completed. This file intentionally
does not embed its own future commit SHA.
