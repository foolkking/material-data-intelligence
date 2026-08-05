# Phase 10M-5 Composition Contracts

M5 adds four strict versioned DTOs across Python, checked-in JSON Schema, and
TypeScript:

* `ReportCompositionRequest 1.0`
* `ReportCompositionSnapshot 1.0`
* `RecipeReplayManifest 1.0`
* `ReportExportManifest 1.0`

Unknown fields, duplicate JSON keys, invalid enums/IDs/hashes, non-finite
numbers, depth above 14, request bytes above 524,288, and all count/string caps
are rejected. Canonical JSON uses sorted keys and stable ordering. Semantic
hashes include exact Workspace revision, Project/Job/Plan identities, selected
source IDs/hashes/contracts, order, captions, disclosures, and Recipe bindings;
record IDs, timestamps, traces, browser state, temporary URLs, and secrets are
excluded.

Snapshots are immutable. Editing and finalizing creates a new Report/Recipe
pair. Pair validation binds exact Workspace, Project, Job, Plan hash, and
composition semantic identity. Preview uses temporary deterministic IDs only
and performs no persistence.

Caps include 32 panels, 64 Artifacts, 32 figures, 32 tables, 32 claims, 256
Evidence items, 128 warnings, 64 limitations, 64 captions, 256 section items,
title length 256, caption length 2,048, and export size 2,097,152 bytes.
