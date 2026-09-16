# MDI V0 — M0 attempt-02

## EVIDENCE-ONLY POINTER FIX — STOP BEFORE M1

External decision: M0 attempt-01 is `NEEDS_FIX (EVIDENCE_ONLY)`.
All substantive M0-001…M0-008 evidence is sufficient. No product, runtime,
scientific, workload, backup/restore, fault-ownership, cleanup, or service
qualification execution may be rerun. Attempt-01 is sealed and immutable.

Create only:

```text
M0 attempt-02
E:\mdi-v0-review\M0_attempt-02.zip
```

### Failure/recovery pointer

Verify from the sealed Pre-M5 attempt-04 ZIP and use:

```text
sealed member = research_state_trace_46095_final.json
SHA256 = 9933d5b5f7fc3490339c5f9eb56515c3551f480d847b9e176a0541cb593d25ba
turn = 46095d1c-1f97-412f-9f79-58001793e264
```

The incorrect `research_state_trace_final.json` filename must occur zero times
as a current provenance pointer.

### `/tasks` pointer

Verify from sealed Pre-M3 attempt-03 and use:

```text
sealed artifact = authenticated_route_evidence.json
SHA256 = 3c8893707fd84d1702a59a4719e70b38193829d850e158789c07583a8e2a22e8
locator label = tasks
route = /tasks
embedded screenshot_reference = after_tasks_1440x900.png
raw screenshot bundled = NO
```

Do not present the standalone PNG or its SHA256 as the sealed artifact.

Update only `pre_m6_pointer_errata.json`, `M0_input_provenance.json`, the new
attempt-02 `phase_return.json`, and files whose references must change.
Carry all other attempt-01 evidence forward by exact hash. Preserve:

```text
M0-001 ... M0-008 = IMPLEMENTED_AND_VERIFIED
production behavior changed = NO
runtime M0 evidence rerun = NO
M1 started = NO
```

Scan all current attempt-02 aggregates and require:

```text
research_state_trace_final.json current pointer count = 0
after_tasks_1440x900.png sealed-artifact claims = 0
after_tasks_1440x900.png may occur only as embedded screenshot_reference
```

Run the official validator with `--seal`, build
`E:\mdi-v0-review\M0_attempt-02.zip`, verify ZIP CRC/integrity, compute ZIP and
phase-return SHA256, then stop for external review without starting M1.

