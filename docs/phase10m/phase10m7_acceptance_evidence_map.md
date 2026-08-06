# Phase 10M-7 Acceptance Evidence Map

| ID | Implementation/test | Browser/service evidence | Retained evidence |
| --- | --- | --- | --- |
| M7-A01 | M7 service aggregate plus L1-L5/M1/M5/M6 service suite | PostgreSQL/Redis/MinIO, zero-skip gate | `service_backed_summary.md` |
| M7-A02 | retained DeepSeek replay integration test | exact Profile through Report/Recipe continuity | `identity_continuity.md`, `scientific_integrity.md` |
| M7-A03 | Plan 0.1/0.2, partial, stale, missing regressions | M3-M6 browser/service cases | `scenario_matrix.md` |
| M7-A04 | focused/full backend and frontend, typecheck, build, lock, migration | exact-SHA CI | test and CI records |
| M7-A05 | M7 browser aggregate plus M3-M6 browser runners | Chromium/Firefox/WebKit/390x844 | `browser_matrix.md`, screenshots |
| M7-A06 | adversarial and secret scans | inert browser/network audit | `security_summary.md` |
| M7-A07 | deterministic evidence generator and manifest tests | DOM/network/console/mobile/performance | `manifest.json` |
| M7-A08 | three-commit lifecycle | three exact-SHA CI gates | completion/result/archive history |

The canonical source is `phase10m_acceptance_and_test_plan.md`; all four marked
registries contain exactly the same eight definitions.
