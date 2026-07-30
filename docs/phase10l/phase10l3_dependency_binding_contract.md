# Phase 10L-3 Dependency Binding Contract

## One Authoritative Edge Model

Every dependency is a typed artifact binding:

```json
{
  "bindingId": "binding_<deterministic-id>",
  "producerStepId": "step-band",
  "producerOutputPort": "canonical-band",
  "consumerStepId": "step-band-dos",
  "consumerInputPort": "band",
  "artifactKind": "phonon_band_json",
  "artifactContractVersion": "phase10h.phonon_band.v1",
  "mediaType": "application/json",
  "cardinality": "EXACTLY_ONE"
}
```

The binding simultaneously names the producer step and output port, exact
artifact contract, and consumer step and input port. The graph edge is derived
from this record. There is no separate `dependsOn` list and no order-only edge.

## Deterministic Identity and Order

`bindingId` is derived from the canonical semantic fields. Graph hashing sorts
bindings by producer step, producer output port, consumer step, consumer input
port, and binding ID. Topological execution uses lexicographically stable step
IDs whenever multiple steps are ready.

## Cardinality and Uniqueness

- Phase 10L-3 supports only `EXACTLY_ONE`.
- A consumer input port may be bound once.
- Duplicate bindings, self-cycles, ordinary cycles, and transitive cycles are
  rejected.
- Producer and consumer steps must both exist in the exact selected tool set.
- Ports and artifact fields must equal one compatible Registry matrix pair.

## Forbidden Bindings

Bindings cannot contain wildcards, regular expressions, arbitrary JSON
pointers, parameter paths, display labels, filenames, array positions,
filesystem paths, object-store keys, URLs, external artifact IDs, previous-job
artifacts, cross-project artifacts, stale resource identities, dynamic
conditions, callbacks, or executable content.

Missing runtime artifacts do not trigger a fallback to raw dataset input. A
failed binding is recorded before the consumer Adapter can run.
