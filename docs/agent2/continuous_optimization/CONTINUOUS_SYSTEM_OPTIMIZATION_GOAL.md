# Continuous Autonomous System Optimization Goal

Authorized: 2026-09-05

## Objective

Continuously and autonomously improve the complete Materials Intelligence
Platform across functionality, performance, stability, maintainability, user
experience, security, automation, code quality, architecture, test coverage,
observability, cost efficiency and developer efficiency.

This goal extends the active Product Maturity Closure. It does not reopen
sealed scientific authority and does not create a new product Phase.

## Persistent loop

```text
discover
→ select one independent improvement
→ investigate root cause
→ define the smallest complete change
→ implement only that improvement
→ test
→ repair regressions caused by it
→ verify in the real product where relevant
→ record result and new discoveries
→ select the next improvement
```

Do not stop because the system is already good, because an arbitrary number of
items has been completed, or because only lower-priority work remains. Continue
while a real, valuable, risk-controlled improvement can be made.

## Initial inventory requirement

Maintain a dynamic candidate pool with at least 100 concrete, non-duplicated
improvements. Every candidate must:

- describe an evidenced defect, risk or opportunity;
- be independently implementable;
- have a concrete verification method;
- identify affected files, modules or runtime surfaces;
- include Impact, Urgency, Confidence, Effort and Risk;
- avoid empty, speculative or quantity-padding statements.

The inventory covers at minimum:

- frontend, backend, API and database;
- authentication, authorization and data integrity;
- scientific identity, versions, Results, provenance and exact source binding;
- Data Platform, Research, Viewers, Evidence, Reports, History and lifecycle;
- configuration and environment handling;
- build, CI/CD, dependencies, tests and automation;
- logs, errors, observability, recovery and resource governance;
- performance, caching, payload sizes and request behavior;
- UI, UX, routing, responsive behavior and accessibility;
- maintainability, type safety, duplication and developer experience;
- documentation, internationalization and supported-product discovery.

New findings are appended continuously. Completion of the initial inventory
does not close this goal.

## Prioritization

Prefer high-impact, urgent, high-confidence, low-risk work with reasonable
effort, while maintaining balance across:

```text
Bug
UX
Performance
Stability
Architecture
Security
Testing
Engineering quality
Product value
Developer efficiency
Maintainability
```

## One-improvement rule

Only one clear, independent improvement may be implemented in a loop. Audit
work may run in parallel, but production changes for unrelated improvements
must not be bundled into the same loop.

Each selected item must record:

1. problem and current evidence;
2. reason for current priority;
3. expected benefit;
4. affected files/modules;
5. investigated root cause and existing related implementation;
6. minimal complete solution;
7. tests and runtime/browser verification;
8. actual outcome;
9. new candidates discovered.

Do not perform unrelated refactors, broad formatting, speculative rewrites,
meaningless renames or complexity-only changes.

## Verification

Run the strongest proportionate checks supported by the affected layer:

```text
unit tests
integration/service-backed tests
browser/E2E
lint and Ruff
typecheck
production build
compileall
uv lock --check
git diff --check
API/data verification
performance/resource checks
```

Code inspection alone is not completion evidence.

## Safety and frozen boundaries

- Preserve `ScientificObject` logical identity and immutable
  `ScientificObjectVersion`.
- Preserve `ScientificResult` as scientific fact authority.
- Preserve fail-closed grounding, exact-version provenance and
  `SILENT_LATEST_SUBSTITUTION = NO`.
- Agent output remains a structured Analysis Plan; validated Tool Registry and
  worker runtime retain execution authority.
- Never move arbitrary Python, shell, filesystem or network execution into the
  LLM or browser.
- Never expose chain of thought, secrets, BYOK, credentials or infrastructure
  internals.
- Preserve unrelated worktree changes and user-owned evidence.
- Do not delete user/scientific data, change production infrastructure, publish,
  push or perform irreversible actions without the required authority.
- Keep current services and browser tabs running unless a selected improvement
  specifically requires a bounded restart.

## Blocked items

An item blocked by credentials, external infrastructure, permissions or a
genuine product decision is recorded as `BLOCKED` with evidence and minimum
external input. It does not stop the whole goal while another safe improvement
is available.

## Status

Maintain:

```text
DISCOVERED
COMPLETED
BLOCKED
REMAINING
CURRENT
```

The dynamic ledger is:

`docs/agent2/continuous_optimization/OPTIMIZATION_BACKLOG.md`

Every completed loop is appended to:

`docs/agent2/continuous_optimization/OPTIMIZATION_LOG.md`

Meaningful architectural/product state is also reconciled with the existing
`persistent/` documents and root `results.md`.

## Stop condition

Continue until the active agent is stopped by the platform, exhausts available
execution resources, loses all required tools, or every remaining improvement
requires unavailable external input and no safe local work remains.

Before any forced stop, leave a compact continuation checkpoint containing the
latest counts, current item, top remaining priorities, tests, runtime state and
exact next action.
