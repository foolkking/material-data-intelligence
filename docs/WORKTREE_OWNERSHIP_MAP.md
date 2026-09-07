# Worktree Ownership Map

**Status:** `FROZEN_BASELINE_V2`
**Current observation:** 2026-09-06
**Branch:** `master`
**HEAD:** `268106e7634472cc8a815e27a8bf3d3eda16be1d`
**origin/master:** `9864e79c433536cc90b24c6a4c68c5bebd940daa`
**Ahead/behind:** `3 / 0`
**Staged:** `0`
**Status entries:** `169` = `51` tracked modified + `118` untracked.
**Policy:** current tree is forensic/reference only; no migration executes here.

## Tracked Modified Ownership

Exact diffs were inspected. None of the following are created by the current amendment except `docs/index.md` and `persistent/ARCHITECTURE_DECISIONS.md`; the ten new/rewritten freeze artifacts are current-task documentation changes. No business Python/React/CSS source modification was observed in the tracked modified set.

| Path/family | Count | Classification | Basis and handling |
|---|---:|---|---|
| `docs/index.md` | 1 | `FREEZE_DOCUMENT_CHANGE` | current amendment allowlist; retain |
| `persistent/ARCHITECTURE_DECISIONS.md` | 1 | `FREEZE_DOCUMENT_CHANGE` | current amendment allowlist; preserve prior ADRs and append V2 ADR |
| `AGENTS.md` | 1 | `PREEXISTING_SOURCE_CHANGE` | repository instruction diff predates this amendment; do not overwrite |
| `apps/web/next-env.d.ts` | 1 | `BUILD_GENERATED` | generated Next type declaration; not business source; exclude from migration baseline |
| `AGENT2_PHASE6_RESULTS.md` | 1 | `HISTORICAL_ARTIFACT` | prior result/ledger change; outside allowlist |
| `docs/phase10k/evidence/phase10k3_*` | 15 | `EVIDENCE_GENERATED` | tracked evidence/manifest family with phase references; retain and do not normalize here |
| `docs/phase10k/evidence/phase10k4_*` | 28 | `EVIDENCE_GENERATED` | tracked evidence/manifest family with phase references; retain and do not normalize here |
| `docs/phase12/evidence/phase12_1_*` | 2 | `EVIDENCE_GENERATED` | design-system audit evidence and manifest; retain |
| `docs/phase13/release/quick-start.md` | 1 | `HISTORICAL_ARTIFACT` | release documentation change outside allowlist; retain |
| **Total** | **51** |  | No tracked business implementation change identified. |

## Untracked Ownership Families

| Path/family | Count/shape | Classification | Evidence / handling |
|---|---:|---|---|
| `.phase13-*` data directories and `.phase12_upload_result.json` | 6 families/files | `RUNTIME_GENERATED` | upload/database/object-store run residue; do not copy or delete |
| `.phase14r-*` JSON, recovery dirs, Redis config, cookies/provenance | 39 families/files | `RUNTIME_GENERATED` / `USER_OWNED_OR_UNKNOWN` for session-bearing files | runtime snapshots and possible credentials/session material; never expose or copy; no deletion |
| `.pytest-*` | 14 dirs | `CACHE_GENERATED` | isolated test/cache residue; no migration input |
| `.vite/` | 1 dir | `CACHE_GENERATED` | frontend cache; no migration input |
| `CODEX_HANDOFF.md` | 1 | `USER_OWNED_CONFIRMED` | user-provided continuation context; retain |
| root and `apps/web/` PNGs | 37 | `EVIDENCE_GENERATED` / `UNKNOWN` individually | screenshots require reverse-reference gate; none deleted |
| `artifacts_phase13_preflight.png` | 1 | `EVIDENCE_GENERATED` | release/preflight-looking artifact; retain pending authority check |
| `docs/agent2.zip` | 1 | `UNKNOWN` | archive content/owner not resolved; human review required |
| `docs/agent2/phase12_data_platform/` | 1 family | `UNKNOWN` | untracked documentation/evidence family; ownership not established |
| thirteen V2 freeze docs | 13 | `FREEZE_DOCUMENT_CHANGE` | current amendment allowlist; retain and review |

Untracked counts are grouped by provable family, not assigned wholesale to a user. Timestamps are auxiliary only. Cookie/provenance files are treated as potentially sensitive and are excluded from any future clean worktree copy.

## Clean Migration Policy

`MIGRATION_EXECUTION_REQUIRES_CLEAN_EXACT_SHA_WORKTREE`.

Future Batch 0 or physical migration must:

1. start from an approved exact committed SHA, not this dirty tree;
2. use an isolated worktree and repository-owned cache paths;
3. exclude unknown runtime/evidence residue and session-bearing files;
4. record the source SHA and pre/post public/dynamic contract surfaces;
5. leave this tree unchanged as forensic reference.

This policy closes `DIRTY_WORKTREE_DIRECT_EXECUTION` as an execution blocker. It does not authorize cleanup or imply that every residue has an identified historical owner.
