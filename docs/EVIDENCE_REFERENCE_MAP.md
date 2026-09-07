# Evidence Reference Map

**Status:** `FROZEN_BASELINE_V2`
**Observation date:** 2026-09-06
**Purpose:** reverse-reference and retention map for future source migration and later cleanup review.
**Deletion performed:** `NO`

A file is not disposable because it is untracked, old, a screenshot, or large. `REDUNDANT_CANDIDATE` is a review classification only, never delete authorization.

## Reverse-Reference Families

| PATH / FAMILY | TRACKED | REFERENCED_BY | HASHED | REGENERATABLE | CURRENT_AUTHORITY | RETENTION_CLASS | FUTURE_DELETE_ELIGIBLE | REASON |
|---|---|---|---|---|---|---|---|---|
| `docs/phase13/final/initial_release_manifest.json` and referenced phase13 evidence roots | yes | release manifest, release validators, phase13 docs | yes/manifest-linked | generally yes, but not without rerun | release/qualification authority | `RELEASE_AUTHORITY` | no automatic eligibility | release claims and source/evidence identity depend on it |
| `docs/phase13/final/presentation/presentation_manifest.json` and five hashed screenshots | mixed | presentation manifest and phase13 final docs | yes | yes only by reproducing campaign | `RELEASE_AUTHORITY` | `HASH_REFERENCED` + `RELEASE_AUTHORITY` | no | byte/hash references are explicit |
| `docs/phase13/final/phase13_forensic_timeline.json` | yes | release timeline/docs | yes or manifest-linked | yes with historical inputs | historical release authority | `HISTORICAL_CONTRACT` | no while referenced | establishes chronology and provenance |
| `docs/qualification/**` and `config/mandatory-service-qualification.json` | yes | qualification config, CI, validators, phase tests | manifests where specified | campaign-dependent | `QUALIFICATION_AUTHORITY` | `QUALIFICATION_AUTHORITY` | no automatic eligibility | future source path changes must update disposition, not erase records |
| `_qualification/**` | generally untracked/ignored | qualification runners, retention scripts, manifests | per run | yes by rerun | current qualification runtime/evidence | `QUALIFICATION_AUTHORITY` | only after retention policy + no references | run outputs may be required for audit/reproduction |
| `.qualification_runs/**` | runtime-managed | qualification/retention/runtime scripts | per run metadata | yes by controlled rerun | qualification runtime | `QUALIFICATION_AUTHORITY` | governed only by retention script | protected runtime authority |
| `docs/phase10k/evidence/phase10k3_*`, `phase10k4_*` | tracked modified/preexisting | phase manifests, docs, tests/generators | evidence manifests | yes by phase campaign | historical/current evidence depending manifest | `NORMALIZED_BUT_REFERENCED` | no while manifest/release/test references exist | current dirty modifications are preserved |
| `docs/phase12/evidence/phase12_1_design_system_2_0/*` | tracked modified/preexisting | phase12 docs/manifest | manifest | yes by audit rerun | historical contract evidence | `HISTORICAL_CONTRACT` | no while manifest referenced | visual audit and design-system claims |
| `design/**/evidence`, `docs/**/evidence` | mixed | phase docs, manifests, scripts, tests | family-dependent | usually yes | historical evidence or qualification authority | `HISTORICAL_CONTRACT` or `UNKNOWN` by family | only after reverse-reference proof | directory name alone does not establish ownership |
| root `phase13*.png`, `phase14r*.png`, `apps/web/*viewer*.png` | untracked | some are referenced by release/presentation manifests; many not resolved individually | some explicit, many unknown | yes by browser campaign | mixed | `MUST_RETAIN` where referenced; otherwise `UNKNOWN` / candidate | only when all screenshot gates pass | unique bug/behavior evidence cannot be inferred away |
| `.runtime_services/**` | runtime-managed | launchers, cleanup, operations, manifests | runtime identity fields | no as historical identity | active/stale runtime authority | `RELEASE_OR_QUALIFICATION_AUTHORITY` / `RUNTIME_PROTECTED` | no automatic eligibility | manifests and observation records must not be deleted here |
| service logs under runtime/cache families | mostly untracked | launchers, diagnostics, forensic records | sometimes referenced by manifests | yes | ephemeral runtime or historical evidence | `EPHEMERAL_LOG` unless referenced | later only after active/reference gate | no deletion in amendment |
| `.phase*`, `.pytest-*`, `.vite`, `.cache`, `apps/web/.cache` | mostly ignored/untracked | run scripts, build/cleanup scripts | build IDs/manifests may reference selected paths | generally yes | runtime/cache authority varies by family | `EPHEMERAL_TMP`, `REGENERATABLE_CACHE`, or `UNKNOWN` | only via existing bounded cleanup/retention rules | protected when active or tracked/referenced |
| `Data/.minio.sys` and object-store data | runtime-managed | MinIO/object-store authority | object metadata | not safely by source rerun | data authority | `RUNTIME_PROTECTED` | no | scientific/artifact data is not documentation residue |
| `results.md`, `AGENT*_RESULTS.md`, persistent ledgers | tracked | tests/scripts/docs/AGENTS | no | no simple regeneration | historical/current ledger authority | `HISTORICAL_CONTRACT` / `CURRENT_LEDGER` | no until reader migration | reader compatibility is documented separately |

## Screenshot Rule

A screenshot may become `REDUNDANT_SCREENSHOT_CANDIDATE` only when all are proven:

- not release or qualification authority;
- no manifest or hash reference;
- no CI/test/script reader;
- not the unique evidence of a bug, behavior, accessibility, or regression claim;
- normalized conclusion is recorded in formal docs or the future `PROJECT_STATE.md` ledger.

No screenshot in this amendment is `DELETE_AUTHORIZED`. Release/presentation screenshots and any manifest/hash-referenced family are `MUST_RETAIN`.

## Source-Migration Reference Rule

For future path changes, preserve historical evidence bytes and paths. Update only explicitly non-persisted CI/test/qualification readers in the same approved batch. Do not rewrite release manifests to conceal the old source path. Every source-path reader must receive a `DYNAMIC_CONTRACT_MANIFEST` disposition and a post-change reference scan.

## Cleanup Authority

Existing bounded cleanup/retention scripts remain the only future cleanup authorities. This amendment creates no new runtime or evidence authority and performs no deletion, archive, cache purge, log rotation, or screenshot removal.
