# Research Context Contract v1

Phase 2 separates product conversation, immutable database context, and the
bounded provider transcript. Provider input is never a conversation authority.

## Candidate assembly

`ResearchContextCandidateBundle` is assembled from already-authorized state:
current UI selection and scope, exact refs retained by up to six recent
terminal Turns, up to six persisted Result snapshots, and bounded user-visible
messages from those Turns. Message content is capped at 4,000 characters with
a deterministic truncation marker. A Turn accepts at most 64 active refs and
16 selected refs; assembly retains at most 80 authorized object candidates,
six Result candidates, 12 compact Messages, and six recent Turn IDs. Artifact
payloads, storage URLs, cookies, credentials, and provider configuration are
not read.

Object candidates are reloaded by object/version ID and verified against the
current Project and exact `object_type`. Historical versions are retained; no
candidate is silently upgraded to `current_version_id`. Result candidates
retain their persisted CURRENT/STALE projection.

## Opaque references and priority

The provider sees `obj_N`, `result_N`, and `finding_N` keys. It cannot nominate
a database UUID. Returned keys must be members of the supplied set and have the
right ref type. Unknown or mistyped keys fail validation; there is no fuzzy
correction.

Priority is server-owned:

```text
EXPLICIT_REFERENCE > UI_SELECTION > CURRENT_SCOPE > PREVIOUS_TURN_RESULT
> PINNED_CONTEXT > RECENT_CONTEXT
```

The action validator rejects selection of a lower-priority object. Equal
highest-priority object candidates produce deterministic clarification before
the provider is called.

## Compilation and fingerprint

`CompactResearchContext` contains bounded object/result summaries, explicit
constraints, unresolved questions, and recent visible conversation. Its
fingerprint hashes Project/Turn identity, exact object/version refs, Result
identity and relevance, constraints, retained Turn IDs, and compiler version.
It excludes timestamps and random ordering.

Compilation enforces the supplied budget against serialized UTF-8 bytes using
the conservative `token_budget * 4` boundary. When needed it deterministically
removes the oldest conversation, then unresolved questions, then the
lowest-priority object/Result summaries while retaining the highest-priority
reference. It fails closed when required context cannot fit; it never sends an
oversized provider envelope.

The processor commits one `ResearchContextSnapshot` before any DeepSeek call.
The snapshot is unique and immutable per Turn. Provider failure or duplicate
delivery cannot replace it.
