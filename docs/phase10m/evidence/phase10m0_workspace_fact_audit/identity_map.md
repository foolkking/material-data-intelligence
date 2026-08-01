# Canonical Identity Audit Evidence

The complete map is `docs/phase10m/phase10m0_identity_and_lineage_map.md`.

Current durable identity chain:

```text
Project -> Dataset/version -> DataProfile -> AnalysisIntent
        -> EligibilityResolution/Selection -> AnalysisPlan -> Job
        -> ToolCall -> Artifact/lineage -> Evidence -> Claim/Interpretation
        -> Report/Recipe
```

Exact local renderer identities exist for stable sample/object refs, periodic sites, trajectory atoms/frames, q-points/branches, reciprocal points, artifacts/checksums, evidence locators, claims, and dependency producer/consumer ports. They are not unified in one cross-artifact frontend contract.

Array position, display label, row order, fuzzy identity, implicit unit conversion, and current-version substitution are rejected as future Workspace identity authority.
