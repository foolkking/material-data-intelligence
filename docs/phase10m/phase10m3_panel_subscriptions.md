# Phase 10M-3 Panel Subscriptions

The checked-in selection declaration table is keyed by formal renderer
contract. It is separate from the Phase 10M-4 scientific renderer registry.

- Overview and provenance consume all 13 exact kinds.
- Data consumes dataset/material/structure/site/trajectory identities.
- Execution consumes whole Artifact identity.
- Scientific-result metadata consumes Artifact-derived identities and emits a
  whole Artifact only when exactly one matching source ref supplies ID, hash,
  contract, version, Project, and Job.
- Findings, evidence, and report consume bounded Artifact/evidence/claim kinds.
- Plan and inert fallback neither consume nor emit.

Findings and evidence do not declare emission in M3 because their formal
payload mappers are Phase 10M-4 scope. This prevents metadata from advertising
an identity producer that the current shell cannot truthfully construct.

Subscriptions are capped at 32. They are removed on unmount; semantic replay
does not republish; each delivery records origin panel, transaction, typed
compatibility, and navigation reason.
