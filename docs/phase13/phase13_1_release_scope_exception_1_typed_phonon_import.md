# Phase 13-1 Release Scope Exception #1

Status: **FAILED / REVIEWER_ACTION_REQUIRED**

The reviewer-authorized candidate adds explicit typed imports for the existing
`PhononBand` and `PhononDos` contracts through the existing Dataset upload and
durable source pipeline. Generic phonon JSON remains mapping-only and is not
auto-detected or promoted.

The fresh canonical Demo 5 run passed typed import, DataProfile 2.4, Intent
1.0, Eligibility 1.0, AnalysisPlan validation, PostgreSQL Job persistence,
Redis enqueue, fresh-worker durable reconstruction, four registered ToolCalls,
and 27 persisted Artifacts. Workspace creation then failed with
`PANEL_CAP_EXCEEDED` because deterministic projection requires more than the
fixed 32-panel contract. This is tracked as `P13-RSE1-001`, a new P0 product
integration defect.

The stop rule was applied immediately. Demo 4 reached a fresh current Workspace
but did not proceed to Chromium Report Finalize. Neither R5-001 nor R5-002 is
closed. The candidate is not release-verified; Phase 11 input support, Fact
Model, and Scope Baseline current authorities are unchanged.
