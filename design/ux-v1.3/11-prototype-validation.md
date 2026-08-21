# Prototype Validation

## Environment

- Prototype: `design/ux-v1.3/prototype/`, local static server at `http://127.0.0.1:4173/`.
- Browser: real Chrome controlled through the Codex Chrome capability; no Playwright Interactive.
- Fixture scope: `Perovskite stability study`, `materials-table`, BaTiO3/SrTiO3/CaTiO3, 516-atom AIMD trajectory, XRD, electronic and volumetric resources.
- Production API/database/queue requirement: none.

## Baseline pass

Current production UI was opened in Chrome at 1440x900 and 1920x1080 before prototype work. Baseline evidence is in `evidence/baseline/`.

| Baseline observation | Product consequence |
| --- | --- |
| Primary analysis exposed Data/Profile, provider, job/plan/queue process and a tabbed object workflow together. | Move machine details behind progressive disclosure; use Project/Data/Research/Result concepts. |
| Project error/empty state was sparse and technical. | Project Overview needs a research-context empty/recovery design. |
| Scientific data, process and result did not have a stable shared spatial hierarchy. | Use Navigator + large Viewer + contextual Inspector and Conversation + Workbench. |

## Chrome pass 2: high-fidelity desktop

| Page/state | Viewport | Observation | Change / final disposition |
| --- | --- | --- |
| Landing | 1440x900 | First capture exposed an orphaned Chinese title line. | Increased copy column and reduced headline scale; rechecked. Two balanced lines and next workflow band visible. PASS. |
| Console | 1440x900 | Continue-research action is visible before recent Projects; no dashboard-card field. | PASS. |
| Project Overview | 1440x900 | Research activity and data context have separate hairline-column ownership; Quick Preview opens from data. | PASS. |
| Data/Table | 1440x900 | Table owns `1176px` after a 264px Navigator; units, sticky columns/headers, selected row visible. | Fixed Navigator height to fill workbench after initial wrapper defect. PASS. |
| Data/Structure | 1440x900 | Large canvas, minimal overlay, site selection, 344px Inspector. | PASS. |
| Research Complete | 1440x900 | Conversation `518px` (36%), Activity `224px`, Figure-led result visible concurrently. | PASS. |
| Research Running incremental | 1440x900 | Completed correlation Figure appears while statistical summary remains a named active step. | PASS; no percentage or fake stream. |
| Unsupported | 1440x900 | Scientific missing-field explanation and alternatives visible. | Removed even explanatory default mention of internal Plan/Job/Queue terms. PASS. |
| Reports / Reader | 1440x900 | Run report rows and `~860px` scientific reading column verified. | PASS. |

## Chrome pass 3: responsive/stress

| Viewport | Pages / stress | Measured / observed result | Status |
| --- | --- | --- | --- |
| 1920x1080 | Research Complete | Conversation `691px`, Activity `224px`, document result `~915px`, no horizontal overflow. | PASS |
| 1440x900 | long project name, material names, full table columns, long research headline, partial/failed/unsupported states | Labels wrap or truncate within ownership regions; no viewport overflow. | PASS_WITH_NOTES |
| 1280x800 | Research Complete, Data, Quick Preview | Conversation `461px`; Activity `204px`; Data Navigator `236px`; Quick Preview `870px` exactly 68vw; no horizontal overflow. | PASS |
| 390x844 CSS viewport (Chrome reported 391x844) | Data and Research | Research linearizes Conversation then Workbench; Navigator becomes a horizontal context list; native document width does not exceed CSS layout width. | PASS_WITH_NOTES |

Chrome screenshot capture for mobile produced duplicated tiled pixels in the browser tool despite correct Chrome DOM metrics. This is a tooling limitation, not treated as visual proof. Mobile source, dimensions, scroll behavior and Inspector geometry were verified through Chrome; a production device pass remains required.

## Chrome pass 4: interaction and accessibility

| Check | Evidence/result | Status |
| --- | --- | --- |
| Visible focus implementation | global `:focus-visible` 2px Mineral Green outline with offset; skip link present. | PASS |
| Icon button accessible name | initial title-only icon control was found by Chrome locator to lack an accessible name. Added `aria-label` for titled icon controls; rechecked `打开 Inspector`. | PASS |
| Escape close | Quick Preview closed with Escape. | PASS |
| Focus restoration | after Escape, focus returned to the `预览` trigger with `data-action=preview:table`. | PASS |
| Research splitter keyboard | implemented ArrowLeft/ArrowRight between 30-45%; functional source behavior requires final production component test. | PARTIALLY_VERIFIED |
| Reduced motion | `prefers-reduced-motion` rule suppresses animation/transition. | PASS_BY_SOURCE |
| 200% browser zoom | not executed through Chrome capability. | NOT_VERIFIED |
| Screen reader announcements | not available in this pass. | NOT_VERIFIED |

## Prototype defects found and fixed

1. A template syntax error initially prevented rendering. Fixed before visual review.
2. Data Navigator was wrapped in a non-stretching grid child. Removed wrapper; rechecked full-height ownership.
3. Landing Chinese title had an orphaned line at 1440. Adjusted grid/headline geometry and rechecked.
4. Quick Preview persisted during cross-route navigation. Route changes now clear preview state and page overflow.
5. Unsupported copy named forbidden internal terms even while denying them. Removed from default copy.
6. Icon buttons had a tooltip but no accessible name. Added `aria-label` whenever a tooltip title is supplied.
7. Mobile Inspector used `100vw` and produced an offset under Chrome viewport scaling. Changed to left/right anchored width and rechecked geometry.

## Design review and design-deslop

The review used the interface-design system and senior-designer web checklist as the review rubric.

| Review area | Finding | Resolution |
| --- | --- | --- |
| Focal point | Data/Table and Structure must dominate, not Navigator metadata. | Main Viewer given residual workbench width; Inspector only opens contextually. |
| Hierarchy | Current baseline mixed backend process with research content. | Prototype uses Project/Data/Research/Result language and progressive detail. |
| Typography | Initial landing title had poor CJK line balance. | Fixed and Chrome rechecked; IBM Plex Sans loaded in Chrome. |
| Surfaces | Risk of dashboard/card accumulation. | Used bands, hairlines, workbench regions and document structure; no section-card grid. |
| Density | Activity could become a log. | Limited it to named scientific stages plus one factual detail. |
| Color | Accent could become a green dashboard. | Green reserved for selection/action/active research; neutral surfaces dominate. |
| State honesty | Risk of fake streaming/progress. | Only named states and persisted artifact target are represented. |
| Deslop | Generic AI gradients, glass, purple palette, decorative molecule imagery, bento layout, badge clutter, and raw ID leakage. | None used. Data gradients are solely scalar/plot encodings, not brand decoration. |

## DESIGN_REALITY_MATRIX

| UX feature | Prototype | Current backend | Production implication |
| --- | ---: | --- | --- |
| Persistent Conversation | Yes | missing as business model | backend required |
| Single Dataset analysis | Yes | exists | reuse |
| Project auto scope | target shown | missing cross-Dataset resolver | backend required |
| Running steps | Yes | partial real events | adapt only to trusted facts |
| Incremental Artifact | Yes | artifact readable before terminal | frontend composition |
| Workspace hidden | Yes | internal Workspace exists | shell decoupling |
| Inspector | Yes | partial reusable selection/evidence | decouple/recompose |
| Run Report | Yes | exists | reuse |
| Project aggregate Report | No | missing | future capability |

## Review matrix

| Screen | 1920 | 1440 | 1280 | 390 |
| --- | --- | --- | --- | --- |
| Landing | PASS_WITH_NOTES | PASS | PASS_BY_LAYOUT | PASS_BY_LAYOUT |
| Console | PASS_BY_LAYOUT | PASS | PASS_BY_LAYOUT | PASS_BY_LAYOUT |
| Project Overview | PASS_BY_LAYOUT | PASS | PASS_BY_LAYOUT | PASS_BY_LAYOUT |
| Data/Table | PASS_BY_LAYOUT | PASS | PASS | PASS_WITH_NOTES |
| Data/Structure | PASS_BY_LAYOUT | PASS | PASS_BY_LAYOUT | PASS_WITH_NOTES |
| Research Idle | PASS_BY_LAYOUT | PASS | PASS_BY_LAYOUT | PASS_BY_LAYOUT |
| Research Running | PASS_BY_LAYOUT | PASS | PASS | PASS_BY_LAYOUT |
| Research Result | PASS | PASS | PASS | PASS_WITH_NOTES |
| Unsupported | PASS_BY_LAYOUT | PASS | PASS_BY_LAYOUT | PASS_BY_LAYOUT |
| Inspector | PASS_BY_LAYOUT | PASS | PASS_BY_LAYOUT | PASS_WITH_NOTES |
| Reports / Reader | PASS_BY_LAYOUT | PASS | PASS_BY_LAYOUT | PASS_BY_LAYOUT |

`PASS_BY_LAYOUT` means the Chrome viewport and layout/overflow contract was checked after responsive CSS review, but no separately retained screenshot was inspected for that exact page/viewport. It is not a production browser acceptance result.

## UX-V1.3.1 closure validation

**Closure revision:** `UX-V1.3.1-final-2026-08-18`.

**Final prototype source observed:** `prototype/index.html` 2026-08-18 00:20:34; `prototype/prototype.js` 2026-08-18 02:03:33; `prototype/styles.css` 2026-08-18 01:59:06. Final DOM included the revision marker in the review-only control surface.

| Closure check | Chrome result | Disposition |
| --- | --- | --- |
| Language policy | Landing, Console, Data, Research, Inspector and Report chrome loaded with Chinese labels. Canonical formulas, filenames, units, `DOS` and source properties remained canonical. | PASS |
| Complete hierarchy | Initial final check found that the compact summary still occupied the `224px` Activity column. CSS was corrected to a one-column `44.7px` full-width summary; the result surface grew to `1222.8px` and Figure to `1080.0px`. | PASS after fix |
| Running hierarchy | `RUNNING_WITH_INCREMENTAL_RESULT` retained a `224.0px` Activity rail and a `998.8px` live result at Chrome's actual desktop viewport. | PASS |
| Data toolbar | Toolbar rendered `materials-table.csv`, `8 个样本 · 4 个属性`, `研究此数据`, and overflow only. It had zero nested preview actions and zero permanent Inspector actions. | PASS |
| Table density | Actual CSS geometry was `39.98px`; unit text was `12px`. Row selection opened the `344px` Inspector while retaining a `1312px` Viewer. | PASS |
| Quick Preview | Console action opened a dialog at `1239.98px`, exactly `68vw` of the actual 1920px Chrome viewport. Escape closed it and restored the triggering action. | PASS |
| Login Modal | Login opened a modal, focus entered `#login-email`, Shift+Tab wrapped to close, Tab wrapped back to email, Escape closed it and restored the Login trigger. | PASS |
| Selection keyboard | Enter on a structure-site button opened the contextual Inspector. Table rows expose keyboard-reachable button semantics. | PASS |
| Reviewer annotation scan | Research state DOM contained no `原型`, `生产实现`, `backend`, or `current contract` reviewer wording. Review-only annotation remains confined to the review control. | PASS |
| Reduced motion | CSS retains `prefers-reduced-motion` suppression; OS preference could not be toggled in Chrome. | PASS_WITH_NOTES |
| 200% zoom | Chrome Ctrl-plus attempt did not change `innerWidth`, `innerHeight`, or DPR. | NOT_VERIFIED |
| Viewport/screenshot evidence | Chrome rendered the final revision at actual `1920x1200` and saved/visually reviewed final Landing logged-out and Login Modal screenshots. Capture became intermittent afterward; viewport override did not apply. | PARTIAL |

### UX_V1_3_1_FINAL_MATRIX

This is a final-evidence matrix. `NOT_VERIFIED` is deliberate: no final screenshot was captured for that viewport, and geometry-only inspection is not labelled visual PASS.

| Surface | 1920 | 1440 | 1280 | 390 | 200% | Keyboard |
| --- | --- | --- | --- | --- | --- | --- |
| Landing Logged-out | PASS | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | PASS |
| Login Modal | PASS | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | PASS |
| Console / Quick Preview | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | PASS |
| Data Table | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | PASS |
| Data Structure / Inspector | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | PASS |
| Research Running | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | PASS |
| Research Complete | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | PASS |
| Unsupported / Clarification | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | PASS |
| Reports / Reader | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | PASS |

`evidence/closure/` is reserved for a recapture from this revision. It intentionally contains this disposition only, not stale UX-V1.3 images relabelled as UX-V1.3.1 evidence.
