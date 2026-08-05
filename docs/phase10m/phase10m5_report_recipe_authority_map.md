# Phase 10M-5 Report/Recipe Authority Map

Report composition is a deterministic projection over persisted authorities:

```text
Workspace revision + Job/Plan + Artifact lineage + Grounded claims/evidence
  -> validated source inventory
  -> immutable Report snapshot + immutable Recipe manifest
```

The Adapter/Runtime owns scientific values; Artifact and checksum own persisted
results; Evidence owns grounding; Interpretation owns validated claims;
Workspace owns source references. Report selects and presents those facts.
Recipe records exact declarative rerun inputs with all execution flags false.

The composition service may read exact Project, Dataset version, Profile hash,
Intent, Eligibility, Planner decision, Plan, Job, ToolCall, dependency record,
Artifact, lineage, Interpretation, Claim, Evidence, Report, and Recipe records.
It cannot create a Plan, Job, ToolCall, queue message, Artifact, interpretation,
claim, or scientific value. Browser selection, camera state, canvas pixels,
filenames, display labels, MIME guesses, and latest-version lookup are not
authorities.

Legacy Report/Recipe records remain readable and unchanged. Records without M5
contracts are returned as typed read-only history; no bulk rewrite occurs.
