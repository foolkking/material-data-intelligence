# Pre-M1 → Pre-M2 → Pre-M3 Chained Execution

状态：用户已授权执行。

日期：2026-09-12

## Authority

- Program pack: `E:\MDI_V0_Completion_Pack_Final`
- Canonical repository: `E:\1project\mdi-b0-5a1`
- Review output root: `E:\mdi-v0-review`
- Accepted prerequisite: `Pre-M0 attempt-02 = ACCEPTED`
- Pre-M0 ZIP SHA-256:
  `449a4897e79f5bd714e166bcff4cf833a18ff35710a77ff8630eb9b8b10db92a`
- Pre-M0 `phase_return.json` SHA-256:
  `8a91bbcbde4f8b412bb4836f8c48623118f16cdf88f7770cfc8f29bcce983507`

Execute exactly, in order:

1. `phases/PM1.md`
2. `phases/PM2.md`
3. `phases/PM3.md`

Also obey `MASTER_PROMPT.md`,
`governance/EXECUTION_CONTRACT.md`,
`governance/CONFLICTS_AND_CLARIFICATIONS.md`,
`review/RETURN_PROTOCOL.md`, and every spec/case referenced by each phase.

## Chained scheduling override

For these three phases only, complete, self-verify, autonomously repair,
seal an independent review bundle, checkpoint, and continue to the next phase
without waiting for inter-phase external review. This is scheduling authority
only: never self-assign external acceptance or weaken evidence requirements.

Each phase must use the next unused attempt directory and preserve its own:

- `phase_return.json`
- raw evidence
- focused tests
- browser/screenshots where required
- sealed review ZIP and SHA-256

Stop the chain only for a genuine external/scientific/safety blocker that
cannot be resolved from the repository and authorized environment.

## Required phase outcomes

### Pre-M1

Implement and verify all PM1 requirements: context roles and support
eligibility, fact/common-ancestry lineage, Report/Interpretation/Memory
dereference, purpose-specific actual model context, recoverable serialized
representation accounting, pins/exclusions/scope, original prompt versus
interpreted objective, non-recursive durable Memory, existing-model-role
instrumentation, same-authority UI projection, and the 20-turn no-evidence
inflation replay.

### Pre-M2

Implement and verify all PM2 requirements: parameter authority/origin/effect,
resolved values and provenance, recomputation/source-version behavior,
retry/rerun/reinterpret/continue/branch separation, preference boundaries,
archive/trash/invalidation/missing semantics, partial ingestion and retry
identity, Found/Added/Used transitions, permissions, and source privacy.

### Pre-M3

Implement and verify all PM3 requirements and directly address the accepted
PM0 findings `PM0-DATA-EMPTY`, `PM0-RESEARCH-SPLIT`, and
`PM0-NOTIFICATIONS-LOADING`. Use the real canonical browser and persisted
scientific state. Capture actual viewport, browser zoom, usable container,
scroll-owner, network/console and before/after evidence. Preserve G semantics
and do not redesign Pre-M4 presentation surfaces.

## Protected state and stop boundary

- Preserve the dirty H/I/J/Pre-M baseline and historical J frozen evidence.
- Do not reset, clean, checkout an older tree, commit, push, tag, release, use
  remote CI, fabricate reviews, regenerate J responses, expose secrets, stop
  unrelated services, delete user objects, or flush shared Redis.
- Do not add a secondary critic/judge/expert Agent.
- Keep services running unless an affected controlled project component must
  be restarted after a production modification.
- Run focused regression after every material fix and a final cross-phase
  regression before sealing Pre-M3.
- After sealing Pre-M3, stop. Do not start Pre-M4, Pre-M5, Pre-M6, M, FINAL0,
  J0, or K0.

Final response must be concise and report each phase status, attempt, review
ZIP, ZIP SHA-256, tests, important fixes, nonblocking handoffs, plus:

`Pre-M4 started = NO`, `M started = NO`,
`J frozen evidence modified = NO`.
