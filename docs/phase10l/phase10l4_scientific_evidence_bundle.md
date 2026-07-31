# ScientificEvidenceBundle 1.0

Bundles bind exact project, dataset/version, Profile, Intent, eligibility,
decision, Plan/graph, Job, execution outcome, ToolCall, Artifact checksum, and
lineage identities. Items carry a bounded semantic value, unit/reference,
subject, contract-aware field locator, producer identity, and warning or
limitation flags.

Limits are 16 approved projected source Artifacts, 128 unsupported Artifact
audit entries, 256 evidence items, 128 warnings, 64
limitations, JSON depth 14, and 262,144 serialized bytes. Cap failure is typed;
there is no order-dependent truncation. Only terminal source jobs can produce
a formal bundle.
