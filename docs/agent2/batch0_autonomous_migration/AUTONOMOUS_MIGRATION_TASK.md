# Batch 0 Autonomous Architecture Migration

Status: ACTIVE

## Scope

Continue the approved canonical architecture normalization from baseline
`6fb7dc87700da11b38cb4ae093629a47b1c80e85` through the remaining B0-5
ownership preparation, B0-6 architecture guards, and B0-7 deterministic
read-only checker. Reuse `E:/1project/mdi-b0-5a1`; do not create branches or
worktrees, push, perform physical file moves, or alter API/schema/queue,
scientific, authorization, transaction, persisted-identity, or UI behavior.

Routine shared infrastructure seams and internally cohesive sub-batches are
authorized without additional approval. Stop only for a real semantic or
safety blocker, or after the pre-physical-migration milestone is reached.

## Required invariants

- Legacy public and dynamic paths remain resolvable during preparation.
- Canonical modules never import compatibility facades.
- Domain/application layers do not import transport or concrete infrastructure
  except for explicitly bounded composition edges.
- Database/Alembic, persisted IDs, queue names/handler paths, scientific
  authority, and UI behavior remain unchanged.
- Every cohesive change receives one local commit; nothing is pushed.

## Verification

Run focused syntax, import-boundary, public-surface, and behavior tests for each
slice. Run broader checks only at useful milestones. Do not perform hash checks
or mutate user runtime data/evidence; restore test-generated unrelated files
before commits. At completion report the commit ledger, architecture guard and
checker results, remaining legacy modules, hard invariants, and exact physical
migration candidate groups.
