# Continuous Integration

Status: CURRENT

The authoritative workflow is `.github/workflows/ci.yml`. It protects current
product behavior on pushes and pull requests while retaining an explicit manual
path for sealed historical browser evidence.

## Push And Pull Request Gates

| Job                               | Current contract                                                                                                                                               |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Unit Tests                        | Locked Python 3.11 environment, every current non-integration pytest (excluding explicitly marked historical `qualification` tests), and lock consistency.       |
| Scientific Replay (Linux/Windows) | The sealed Phase 11 numeric and identity invariants replay on both supported runner families and are compared.                                                 |
| Frontend                          | The complete Vitest suite, TypeScript check, production build, three-browser responsive/accessibility checks on the current Research workbench, and cross-product UX checks. |
| Service-backed Integration        | PostgreSQL, Redis, MinIO, migration/index verification, all integration tests, and a hard zero-skip assertion.                                                 |

Live provider calls and deployment are not CI gates. `DEEPSEEK_KEY` remains
empty in deterministic jobs.

## Historical Evidence Replay

Phase 10L/M/N and Phase 12-5 browser scripts are retained because they are
auditable reproduction tools for their sealed evidence. They are not run on
every push. Start the `CI` workflow manually with
`replay_historical_browser_evidence=true` when a reviewer explicitly needs to
revalidate those historical contracts. The workflow exposes them as one
`Replay sealed historical browser evidence (manual)` step; the orchestrator
still runs every retained script and fails on the first failed contract.

This distinction is evidence-based:

- `docs/ROADMAP.md` records Phase 10M, Phase 10N, Phase 12, and Phase 13 as
  complete and their exact-SHA CI evidence as sealed history.
- The 2026-08-17 release closure records all configured browser replays as
  passing and classifies historical evidence separately from current product
  defects.
- Remote run `32026543339` spent about 12 of its 15 frontend minutes installing
  browsers and replaying 17 phase-specific scripts. The current Vitest suite
  was not run; only one Phase 10 closure file was executed.
- Run `32441155365` failed frontend Vitest on a missing ignored Phase 10H
  fixture and one Research focus-timing assertion, and failed Python only when
  clean-checkout qualification tests attempted to read `_qualification/`.
- Run `32442770446` passed frontend Vitest, typecheck, and build, then isolated
  the remaining frontend failure to the stale Phase 13-4 Help selector
  (`.top-settings`) on the compatibility `/analysis` route; Python again
  failed only on clean-checkout qualification tests. Neither run is treated
  as proof of later gates it did not reach. The Help script remains available
  as historical evidence but is no longer a current product gate.
- Current product changes are guarded by the complete frontend test suite plus
  the retained three-browser Phase 12-6 and Phase 12-7 product checks.
- Phase 12-6 and Phase 12-7 open the current project-scoped Research route with
  deterministic auth/history/provider fixtures. They no longer target the
  retired `/analysis` compatibility route, while still checking keyboard skip
  navigation, the Research splitter, design tokens, touch targets, overflow,
  reduced motion, forced colors, and cross-browser error-free rendering.

## Qualification Package Tests

The historical qualification-package tests are marked `qualification`.
Several require the deliberately ignored local `_qualification/` workspace and
therefore cannot be a truthful clean-checkout push gate. They remain runnable
for an explicit local qualification audit:

```powershell
uv run python -m pytest -q -m qualification --tb=short
```

The default unit equivalent intentionally excludes them:

```powershell
uv run python -m pytest -q -m "not integration and not qualification" --tb=short
```

## Action Runtime Policy

The 2026-08-17 run warned that the previous `checkout@v4`, `setup-node@v4`,
`setup-uv@v5`, and Artifact v4 actions targeted deprecated Node 20 runtimes.
The 2026-08-21 audit moved them to the then-current official major releases:
`checkout@v7`, `setup-node@v7`, `setup-uv@v10.0.1`, `upload-artifact@v7`, and
`download-artifact@v8`. Project Node remains explicitly pinned to Node 20 for
the application build; the warning concerned the actions' own runtime.

## Local Equivalents

```powershell
uv sync --frozen --extra test
uv run python -m pytest -q -m "not integration and not qualification" --tb=short
uv lock --check

Set-Location apps/web
npm ci
npm test
npm run typecheck
npm run build
```

Service-backed and browser gates require the same services and pinned browser
runtime declared in the workflow. A task is not archived from `TASKS.md` until
its current HEAD has passed the required remote workflow.

The checked-in
`config/mandatory-service-qualification.json` is the single selection
authority for the mandatory PostgreSQL/Redis/MinIO campaign: test paths,
required test identities, minimum pass count, and zero-skip/failure policy.
After starting and configuring those services, local and CI qualification use
the same runner:

```powershell
uv run python scripts/mandatory_service_qualification.py run --junit integration.junit.xml --log integration.log
uv run python scripts/mandatory_service_qualification.py validate --junit integration.junit.xml
```
