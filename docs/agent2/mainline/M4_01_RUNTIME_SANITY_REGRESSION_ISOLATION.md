# MDI V0 — M4-01 Runtime Sanity / Regression Isolation

## Authority

- Base HEAD: `c4e74f922947be96833d0e276ad20f23241d6707`
- Preserve the current uncommitted M4-01 worktree.
- Do not commit, rollback, start M4-02, run Phase D, or run Phase E.
- During this task M4-01 is `NEEDS_FIX_PENDING_RUNTIME_SANITY`.

## Objective

Determine from raw runtime evidence whether the operator-observed service
problem is:

1. expected task-owned service shutdown;
2. browser proxy/auth evidence artifact;
3. normal-runtime startup/configuration failure;
4. frontend polling/reconnect regression;
5. API/admission regression introduced by M4-01; or
6. unrelated pre-existing environment failure.

Do not guess and do not edit product code before a regression is proven.

## Required execution

1. Record HEAD, status, unstaged diff names, and staged diff names without
   changing the worktree.
2. Verify the previous M4-01 task-owned API, frontend, and browser-proxy
   shutdown and compare expected test ports with current listeners/processes.
3. Start the current worktree through normal product service paths with
   isolated PostgreSQL, Redis, MinIO, API, frontend, and all six workers.
   Do not use the M4 fault harness. The prior `/backend` reverse proxy is
   browser tooling only and may be used only if the built-in browser requires
   it.
4. Before fault injection, prove API/health, frontend application shell,
   PostgreSQL, Redis, MinIO, six workers, and provider readiness. Preserve
   stdout/stderr and reject crash loops, unexplained 5xx loops, or uncaught
   exceptions.
5. Diagnose `/auth/me` 401 behavior under normal authenticated operation,
   including cookie/session, origins, and proxy involvement. Normal runtime
   must not continuously produce 401 requests.
6. Observe a bounded healthy-page request window and count `/auth/me`,
   progress, context-manifest, research-session, and provider-status requests.
   Detect tight loops, duplicate timers, zero-delay retries, stale reconnect
   loops, polling after unmount/terminal state, and polling during invalid
   authentication.
7. Determine whether context-manifest 409 responses are expected and bounded
   while unavailable or defective/unbounded after readiness.
8. Execute one no-fault normal workflow:
   browser → Project → Research session → durable Turn → Plan → Job → ToolCall
   → ScientificResult → Interpretation → truthful browser terminal state.
   Capture all durable IDs and prove duplicate Turn/Job/Result and orphan
   counts are zero.
9. Only if the no-fault workflow passes, execute one full-stack F11 scenario
   while a real Job is active: keep workers running, terminate only the
   task-owned API, observe truthful browser disconnect, restart the API,
   recover the same Turn/Plan/Job, publish one Result and Interpretation, and
   reach truthful browser terminal state without duplicate effects.
10. If the current worktree fails normal mode, create a temporary worktree at
    `c4e74f922947be96833d0e276ad20f23241d6707` on separate ports/namespaces and
    run the same startup and no-fault workflow. Do not alter the main worktree.
11. Only after `BASE PASS + M4 CURRENT FAIL` may the nine M4 production owners
    be investigated as a confirmed regression. Do not broadly revert them.
12. Reconcile all evidence, stop only task-owned processes after identity
    verification, preserve shared PostgreSQL/Redis/MinIO, and return the exact
    M4-01 runtime-sanity report requested by the operator.

## Hard gates

- No migration unless a blocker is first reported.
- No product fix unless an M4 regression is proven.
- No request storm.
- Normal authenticated `/auth/me` passes without continuous 401s.
- No-fault full product workflow passes before fault injection.
- F11 full-stack test preserves Turn, Plan, Job, Result, and Interpretation
  authority with zero duplicate admission, Job, Tool effect, or Result.
- `COMMIT_EXECUTED=NO`, `M4-02 started=NO`.
