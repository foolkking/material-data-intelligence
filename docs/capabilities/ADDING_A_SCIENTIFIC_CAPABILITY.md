# Adding a Scientific Capability

This guide uses the canonical repository at
`E:\1project\mdi-b0-5a1`. The old repository is comparison-only.

## 1. Choose the scientific contract

Define the operation in scientific language:

- required exact `ScientificObjectVersion` or prior Result types;
- hard deterministic preconditions;
- parameters and units;
- output semantic/result types;
- known limitations;
- whether execution is retry-safe or resumable only from a durable boundary.

Do not begin with a Python function name or Tool ID.

## 2. Register or reuse a Requirement

Use:

`apps/api/mdi_api/research_agent/requirements/registry.py`

Requirements describe needs such as `trajectory.compute_msd`; they do not
reference Adapter classes. Keep constraint JSON Schema bounded and reject
unknown fields.

## 3. Declare the Capability

Use the built-in manifests in:

`apps/api/mdi_api/research_agent/capabilities/defaults.py`

Declare:

- stable `capability_id` and version;
- Requirement IDs;
- exact accepted scientific input types;
- output result/object types;
- registered deterministic preconditions;
- Tool binding/version constraint;
- explicit Result, Artifact-port, interpretation, Viewer and report support;
- planner visibility, resource source, execution policy, qualification and
  limitations.

The default builder groups declarations into trusted Capability Packs.

## 4. Define the Tool contract

Add or reuse a manifest in `tool_registry/*.yaml`. A Tool contract owns:

- stable Tool ID/version;
- typed input options and parameter schema;
- declared Artifact types;
- Adapter name;
- timeout/cost/cache/resource limits;
- stage and planner availability.

Do not put arbitrary imports, shell commands or executable code in capability
or Tool metadata.

## 5. Implement and register the Adapter

Implement domain science under `packages/adapters/mdi_adapters/` and register
the class in `packages/adapters/mdi_adapters/registry.py`.

Adapters validate typed inputs and produce declared Artifacts. They do not
become Requirement, planning, lifecycle, Report or Viewer authorities.

## 6. Add typed Artifact ports only when composable

If another planned step consumes the output, add port metadata in:

`packages/tool-registry/mdi_tool_registry/dependency_ports.py`

Declare artifact kind, contract/schema version, media type, cardinality,
maximum bytes, semantic role and required provenance. Mark the Capability
`artifact_port_support=REQUIRED` when a durable upstream Artifact is a required
input.

Reference example:

```text
trajectory.msd
  output port: trajectory-msd
  contract: phase10n4.trajectory_msd.v1

trajectory.diffusion
  input port: msd
  accepts the same inert Artifact contract
```

## 7. Produce ScientificResult

Add the bounded Artifact payload schema and projector contract under:

`apps/api/mdi_api/application/scientific_results/projectors/`

The projector normalizes grounded facts/evidence/methods/limitations and exact
source provenance. It must not recompute the scientific method.

## 8. Declare presentation support

- Use `GENERIC` when generic grounded interpretation/report/table fallback is
  a deliberate supported path.
- Use `SUPPORTED`/`REQUIRED` with registered Viewer IDs or profiles for a
  specialized surface.
- Use `NONE` when the surface is intentionally unavailable.

Specialized Viewer descriptors live under
`apps/api/mdi_api/scientific_viewers/`. Frontend rendering belongs under
`apps/web/scientific-viewers/` or the relevant migrated feature owner—not in
the Capability manifest.

## 9. Validate before execution

Run:

```powershell
python scripts/capability_extension_report.py --check
python -m pytest tests/test_capability_extension_platform.py -q
```

Then run the relevant Requirement/resolution/binder, Adapter, Artifact,
projector and Viewer/Report tests. A composable capability also needs a
dependency-port compatibility test.

The validator must show the new Capability as `VALID`. Do not treat structural
validation as scientific quality. Add capability-specific scientific fixtures,
reference cases and limitations before declaring scientific qualification.

## 10. Expected change surface

A conventional producing capability usually changes these explicit
authorities:

1. Requirement registry (only for a new scientific need);
2. Capability declaration/Pack contribution;
3. Tool manifest;
4. Adapter implementation and registration;
5. Artifact payload/projector;
6. optional Artifact port and Viewer descriptor;
7. domain-focused tests.

No Agent state-machine, worker queue identity, generic Result service,
Research page dispatcher, or Report engine change should be necessary for a
conventional capability. If one is, document why the existing contract cannot
represent the new science before adding central special cases.

