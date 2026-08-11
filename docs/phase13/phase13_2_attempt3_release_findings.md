# Phase 13-2 Attempt 3 Release Findings

## P13-R3-001

- Severity: P0
- Category: `RELEASE_CRITICAL_INTEGRATION_DEFECT`
- Status: `OPEN_REVIEWER_ACTION_REQUIRED`
- Affected path: all uploaded-resource jobs that execute in a fresh worker
- Observed first in: Demo 1 Dataset Intelligence + Composition Space
- Product consequence: real upload and planning succeed, but out-of-process
  Runtime cannot resolve the exact Profile and cannot create a ToolCall
- Scientific consequence: none; execution stops before scientific calculation
- Security consequence: none

### Root Cause

`/datasets/upload` stores normalized source exports in the process-local Phase2
runtime. Planner creates and persists the project, dataset and exact DataProfile,
but the SQL dataset does not carry those normalized exports. The durable worker
resolver therefore has no PostgreSQL/MinIO source-resource index from which to
rebuild the exact object store.

The Fix-Forward #2 Level-C2 service test manually persisted normalized exports.
It proved resolver behavior after registration but did not cover the real upload
endpoint followed by a new worker boundary.

### Required Reviewer Decision

The next remediation must connect already-supported upload ingestion to the
existing canonical source-resource persistence lifecycle. It must preserve exact
dataset/project/type/hash identity and must not use runtime reparse, latest,
filename, fuzzy, in-memory, or fixture-specific fallback.

