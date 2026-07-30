# Phase 10L-3 Artifact Port Metadata Audit

Status: implementation contract and Registry audit. Verification and exact-SHA
closure remain pending. This document records current Registry and Adapter
facts; it does not register a new scientific capability.

## Contract Versioning

Phase 10L-2 `ToolPlannerMetadata 1.0` remains valid for independent tools.
Phase 10L-3 adds a separate, additive `ToolArtifactPortMetadata 1.1` overlay.
Tools with no 1.1 input/output ports remain available for independent planning
but cannot participate as dependency producers or consumers.

Each output port declares a stable ID, artifact kind, contract family/version,
media type, `EXACTLY_ONE` cardinality, byte cap, determinism, required
provenance, exact identity policy, inert-content trust, and planner visibility.
Each input port declares accepted kinds/versions/media types, exact identity,
semantic role, materialization and base-resource policy, and the role/object
type supplied to the existing Adapter input contract. A tool may expose at
most 16 input plus output ports under the shared bounded contract.

## Scope And Sources

The audit covers the 38 tools whose Phase 10L-2 planner metadata reports `availability = AVAILABLE`. The machine-readable inventory is [artifact_contract_inventory.json](evidence/phase10l3_bounded_multi_tool/artifact_contract_inventory.json).

Authoritative inputs:

- `tool_registry/pymatviz_manifest.yaml`
- `tool_registry/platform_builtin_manifest.yaml`
- `tool_registry/matterviz_manifest.yaml`
- `packages/tool-registry/mdi_tool_registry/loader.py`
- `packages/tool-registry/mdi_tool_registry/planner_metadata.py`
- `packages/adapters/mdi_adapters/`
- `packages/artifact-core/mdi_artifact_core/phonon_contract.py`
- `packages/artifact-core/mdi_artifact_core/phonon_band_dos_contract.py`
- Phase 10L-2 actual Registry inventory

`artifact_types` in a manifest describes products emitted for storage or display. It does not by itself declare a planner-visible output port, a consumer input port, or producer/consumer compatibility. Generic `table_json`, `plotly_json`, HTML, PNG, Markdown, recipe, manifest, and summary artifacts therefore remain result artifacts unless an Adapter also enforces an exact scientific contract and role-bound input.

## Audit Result

| Classification | Count | Meaning |
|---|---:|---|
| Available registered tools | 38 | Current Phase 10L-2 `AVAILABLE` inventory. |
| Selected-chain producers | 2 | `phonon.band` and `phonon.dos`. |
| Selected-chain consumer | 1 | `phonon.band_dos`. It is also an artifact producer. |
| Input-capable but not dependency-ready | 2 | `dataset.composition_space` and `phonon.animation`; neither has a complete planner-visible producer/port closure for this phase. |
| Other tools without declared typed artifact input ports | 33 | Their artifacts are outputs for products, audit, export, or frontend consumption only. |

Exactly one real dependency-ready composition exists in the audited surface:

```text
phonon.band --canonical-band--> phonon.band_dos:band
phonon.dos  --canonical-dos ---> phonon.band_dos:dos
```

No other tool is identified as dependency-ready by this audit.

The deterministic compatibility matrix is built only over the exact Phase
10L-2 selected tool IDs and Registry snapshot. Every pair has a deterministic
pair ID and either an exact compatible kind/version/media tuple or bounded
typed rejection diagnostics. Registry insertion order has no authority.

## Selected Real Chain

### Band Producer

- Tool: `phonon.band` version `0.1.0`
- Stable output role: `canonical-band`
- Artifact type: `phonon_band_json`
- Contract: `phase10h.phonon_band.v1`
- Media type: `application/json`
- Properties: deterministic, inert JSON, structure identity and scientific provenance retained

### DOS Producer

- Tool: `phonon.dos` version `0.1.0`
- Stable output role: `canonical-dos`
- Artifact type: `phonon_dos_json`
- Contract: `phase10h.phonon_dos.v1`
- Media type: `application/json`
- Properties: deterministic, inert JSON, structure identity and scientific provenance retained

### Combined Consumer

- Tool: `phonon.band_dos` version `0.1.0`
- Required input role `band`: `refType=artifact`, `objectType=PhononBand`, contract `phase10h.phonon_band.v1`
- Required input role `dos`: `refType=artifact`, `objectType=PhononDos`, contract `phase10h.phonon_dos.v1`
- Cardinality: exactly one artifact per role
- Product contract: `phase10h.phonon_band_dos.v1`
- Media type: `application/json`

The existing Adapter validates independent contracts and then checks structure identity, atom ordering, cell/source lineage, force-constant provenance, frequency units, imaginary-mode encoding, zero tolerance, NAC metadata, DOS normalization, projection identity, display caps, and frequency domain. This is an existing scientific composition, not a new algorithm introduced by Phase 10L-3.

## Existing Input-Capable Paths Not Selected

### `dataset.composition_space`

The Adapter can consume bounded Phase 10K-3 regression or uncertainty content alongside the exact Profile 2.0 and table resources. The current Registry surface exposes those upstream products through generic `table_json` artifact types, not through stable planner-visible output roles and compatible input ports. Its required base Profile/table closure also needs explicit dependency semantics. It is therefore `INPUT_CAPABLE_NOT_DEPENDENCY_READY`, not a second approved chain.

### `phonon.animation`

The Adapter requires unique `structure`, `band`, and `eigenvectors` roles with exact object types. The current 38-tool `AVAILABLE` inventory has no registered planner-visible producer that emits the required phonon eigenvector-set artifact. The complete producer closure is absent, so it is `INPUT_CAPABLE_NOT_DEPENDENCY_READY`.

## Artifact Type Media Rules

The machine-readable inventory records each tool's current output artifact types and a shared media-type map. JSON artifact types use `application/json`; summaries use `text/markdown`; CSV uses `text/csv`; Plotly HTML uses `text/html`; preview PNG uses `image/png`. `volumetric_binary` is adapter-selected bounded binary content and has no single fixed media type in the current manifest, so the inventory records it as unknown rather than inventing one.

## Safety Boundary

- A manifest output type is not execution authority.
- HTML, PNG, Markdown, Plotly, recipe, report, summary, and frontend-view artifacts are not scientific Adapter inputs unless an exact port contract says otherwise.
- No artifact filename, display label, array index, local path, object-store key, URL, or arbitrary JSON shape establishes compatibility.
- No test-only or copy tool is treated as a production producer/consumer.
- Artifact payload remains inert and is not exposed to an LLM composer.
- Future metadata must preserve exact contract version, media type, cardinality, identity scope, byte cap, and provenance checks.
- `contentTrust=INERT_DATA` does not imply scientific compatibility; the exact
  producer and consumer contracts must still match.
- A provider receives only compatible pair IDs and their exact declared facts,
  never artifact payloads or the full Registry.
