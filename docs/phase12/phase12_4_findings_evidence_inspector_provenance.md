# Phase 12-4 Findings, Evidence, Inspector and Provenance

Phase 12-4 implements a presentation-only trust path over persisted
`GroundedScientificInterpretation 1.0` and `ScientificEvidenceBundle 1.0`:

```text
Finding -> exact Evidence membership -> source Artifact -> Tool/version
        -> Plan/Job -> dataset/source scope -> provenance
```

Findings are ordered only by persisted `displayOrder` with `claimId` as a stable
tie-break. Evidence links come only from supporting, limiting and contradicting
ID arrays. The UI neither generates claims nor infers relationships from text.
Warnings and scientific limitations remain visible near affected claims.

The Workspace Inspector exposes Summary, Scientific details and Provenance;
Developer details remain collapsed and subordinate. Registry 62, DataProfile
2.4, Workspace/Artifact/Selection authority and migration 0007 are unchanged.
