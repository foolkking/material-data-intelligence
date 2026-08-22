# Capability Manifest 1.1

Agent 2.0 reasons about registered scientific capabilities, never directly
about executable Tools. A manifest has a stable capability ID/version,
requirement coverage, typed source/result input slots, typed outputs,
registered deterministic preconditions, limitations, and one or more bounded
Tool bindings.

`CapabilityPrecondition.predicate_id` resolves only through the
`CapabilityPreconditionRegistry`; strings are never evaluated. Active
manifests must reference registered requirements, known source/object or
produced-result types, registered projectors, and a Tool whose exact version
satisfies the declared constraint. Non-empty free-form Tool binding conditions
fail startup validation.

Phase 3 registers nine manifests across five families: Structure RDF, XRD
generation/comparison, ML regression evaluation, trajectory MSD/diffusion,
and phonon band/DOS/composition. This is not a mapping of all 62 Tools.
