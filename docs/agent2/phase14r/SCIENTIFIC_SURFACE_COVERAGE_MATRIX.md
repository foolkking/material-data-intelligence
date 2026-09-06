# Scientific Surface / Viewer Coverage Matrix

Source of truth: `apps/api/mdi_api/research_agent/capabilities/defaults.py`,
`apps/api/mdi_api/research_agent/capabilities/packs.py`,
`apps/api/mdi_api/scientific_viewers/`, `apps/api/mdi_api/scientific_results/`,
and the corresponding `apps/web/app/components/` renderers.

`NOT_QUALIFIED` means the repository has a declared capability or renderer
but Phase 14-R has not yet produced a fresh real-data browser and
PostgreSQL/Redis/MinIO evidence package for that row.

| Capability ID | Pack | Input | Tool binding | Result projector | Presentation | Viewer/Figure/Table | Evidence/Report | Current status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `structure.rdf` | core.structure | `structure.crystal` | `structure.rdf` | `agent2.structure.rdf` | metric/figure | RDF viewer/figure | supported | PASS |
| `structure.coordination_hist` | core.structure | `structure.crystal` | `structure.coordination_hist` | `agent2.structure.coordination_hist` | finding/table | table | supported | PASS |
| `structure.coordination_crystalnn` | core.structure | `structure.crystal` | `structure.coordination_crystalnn` | `agent2.structure.coordination_crystalnn` | finding/table | Structure Viewer | supported | PASS |
| `structure.coordination_voronoinn` | core.structure | `structure.crystal` | `structure.coordination_voronoinn` | `agent2.structure.coordination_voronoinn` | finding/table | Structure Viewer | supported | PASS |
| `diffraction.theoretical_xrd` | core.other | `structure.crystal` | `structure.xrd` | `agent2.diffraction.theoretical_xrd` | figure | XRD figure | supported | PASS |
| `diffraction.experimental_theoretical_comparison` | core.other | experimental + theoretical XRD | `structure.experimental_xrd_comparison` | `agent2.diffraction.experimental_theoretical_comparison` | finding/figure/table | XRD comparison | supported | PASS |
| `trajectory.rdf` | core.trajectory | `trajectory.atomic` | `trajectory.rdf` | `agent2.trajectory.rdf` | figure/table | trajectory viewer | supported | PASS |
| `trajectory.msd` | core.trajectory | `trajectory.atomic` | `trajectory.msd` | `agent2.trajectory.msd` | metric/figure/table | trajectory viewer | supported | PASS |
| `trajectory.diffusion` | core.trajectory | trajectory + MSD | `trajectory.diffusion` | `agent2.trajectory.diffusion` | finding/metric/table | trajectory analytics + persisted diagnostic table | supported | PASS |
| `phonon.band` | core.other | `phonon.band_structure` | `phonon.band` | `agent2.phonon.band` | figure/table | Phonon Band Viewer | supported | PASS |
| `phonon.dos` | core.other | `phonon.dos` | `phonon.dos` | `agent2.phonon.dos` | figure/table | Phonon DOS Viewer | supported | PASS |
| `phonon.band_dos` | core.other | band + DOS | `phonon.band_dos` | `agent2.phonon.band_dos` | figure/table | combined viewer | supported | PASS |
| `electronic.band_structure` | core.electronic | `electronic.band_structure` | `electronic.band_structure` | `agent2.electronic.band_structure` | figure/finding | Band Viewer | supported | PASS |
| `electronic.dos` | core.electronic | `electronic.dos` | `electronic.dos` | `agent2.electronic.dos` | figure/finding | DOS Viewer | supported | PASS |
| `data.composition_space` | core.data | `materials.dataset`/`materials.table` | `dataset.composition_space` | `agent2.data.composition_space` | figure/table | Materials Explorer | supported | PASS |
| `data.materials_explorer` | core.data | `materials.dataset`/`materials.table` | `dataset.materials_explorer` | `agent2.data.materials_explorer` | table/finding | Scientific Table | supported | PASS |
| `ml.regression_evaluation` | core.other | `materials.dataset` | `ml.regression_evaluation` | `agent2.ml.regression_evaluation` | metric/table | N/A | supported | PASS |

### 2026-09-04 current-worktree object route recheck

An authenticated in-app browser tab on the isolated production build
`127.0.0.1:3022` opened every exact object/version link exposed by the active
qualification project:

| Scope | Count | Result |
| --- | ---: | --- |
| Exact ScientificObject/Version routes | 13 | `13/13` readable |
| Valid-route `role=alert` failures | 13 | `0` |
| Browser error-log entries | 13 | `0` |
| Desktop document-width overflow | 13 | `0 px` |
| Real canvas routes | 3 | trajectory/structure content mounted |

Table, electronic, phonon and ML families used bounded reviewed renderers;
trajectory and structure families mounted real canvas surfaces. This is a
current-worktree route qualification, not a claim that every declared
capability family has completed a separate human real-source campaign.

### 2026-08-31 trajectory diffusion real-source product path

Dataset `dataset_0001_441637edf69740aa` and persisted trajectory resource
`obj_trajectory_b0949ed50ff8` produced Plan
`plan_acb197e27b464ddca83157bd`, Job
`job_dc63f3f5d57742009c6be09e`, two completed ToolCalls
(`trajectory.msd`, `trajectory.diffusion`) and eight MinIO-backed Artifacts.
The accepted diffusion window is exactly `1–6 ps` with `11` fit points,
`R²=0.970301847945`, `α=0.924032310013`, and bounded
`D=0.038618084156 Å²/ps`.

Current-worktree re-interpretation
`interpretation_a115c2ced38a7586161370b7994fec88` over bundle
`bundle_d6ddf767fde0753fce41dd9ba943bf5d` projects ten grounded evidence
items, including exact fit start/end/count, without creating science:

```text
jobs/tool_calls/artifacts/scientific_result_snapshots/interpretations
before = 1/2/8/0/1
after  = 1/2/8/0/2
```

The evidence bundle is complete. `plotly_json`, `summary_md` and `recipe_json`
companions no longer falsely degrade a ToolCall when its authoritative
`table_json` is already projected; unknown, oversized or genuinely
unprojected scientific payloads remain fail-closed.

Authenticated desktop and `390x844` production-browser paths display the
persisted diagnostic table, exact `1–6 ps` narrative, ten evidence items and
the scientific limitation. Mobile measured `390/390` document width with no
global overflow. After authentication, console errors, page errors, critical
responses and failed API requests were all zero.

This establishes the real-source execution and grounded interpretation
authority used by the complete product qualification.

### 2026-08-31 archived trajectory communication qualification

The real product lifecycle archived ScientificObject
`f834e358-9944-4fe8-a3ab-f85d68041f54` while preserving exact version
`a22745f2-17b6-434f-ba4c-3fe6bd244841`. While archived, Report
`agent2_report_e54681009a0e49abe371247d9053ce61`, Result
`26127c48-d736-4983-b035-b68db238f6a7`, all four Evidence entries and the
24-frame trajectory Viewer remained usable. The Report now distinguishes
`当前版本` from `来源对象已归档`; the two facts are not conflated.

Report → Evidence → Viewer navigation and a real frame change preserved global
`Jobs / ToolCalls / Artifacts / ScientificResults` at
`285 / 377 / 1493 / 191`. The product Restore action returned the object to
`ACTIVE`; `current_version_id` stayed exact, version count stayed `1`, and
`archived_at` returned to null. Archived/historical behavior for this exact
diffusion path is therefore `PASS`. The diagnostic-table qualification was
completed in the subsequent Report projection entry below, so the top-level
`trajectory.diffusion` row is `PASS` for this exercised real-source path.

### 2026-08-31 trajectory diffusion communication closure

The current exact Agent2 path is fully exercised for
`trajectory.diffusion`:

```text
Turn = fb72c2ad-bed1-47d7-b557-f398f04a8ede
Result = 26127c48-d736-4983-b035-b68db238f6a7
Interpretation = 4d1f2f06-ac66-4878-9ee5-bf79c53b3229
Report = agent2_report_e54681009a0e49abe371247d9053ce61
Version = a22745f2-17b6-434f-ba4c-3fe6bd244841
```

Presentation displays all ten authoritative facts, Evidence traverses the
completed ToolCall and persisted Artifact, the Viewer renders 24 trajectory
frames, and the Report retains `D=0.038618084156 Å²/ps` plus the exact
`1–6 ps` fit interval. Mobile Report/Research/Evidence paths have zero global
overflow. Read-only navigation leaves scientific persistence unchanged.

The historical/archived campaign above and the persisted diagnostic-table
Report qualification below close the remaining exact diffusion surface.

### 2026-08-31 trajectory diagnostic Table and Report projection

The Report read model now derives bounded `table_sources` directly from the
immutable ScientificResult tables, alongside the existing Figure projection.
For Report `agent2_report_e54681009a0e49abe371247d9053ce61`, the authenticated
same-stack browser displays `轨迹扩散性质` and `轨迹均方位移` as persisted
`table_json` entries, each retaining its exact Artifact and source version
`a22745f2-17b6-434f-ba4c-3fe6bd244841`. Opening these links is explicitly
read-only and does not execute a Tool.

Backend Report coverage is `34 passed / 4 historical compatibility skips`;
frontend Report/Presentation coverage is `35 passed`; ContextManifest budget
coverage is `6 passed`. Browser error logs were empty. `trajectory.diffusion`
is now `PASS`.

### 2026-09-01 canonical Agent2 MSD surface closure

The later canonical Agent2 trajectory path supersedes the standalone legacy
planner path as the mature-product acceptance authority for `trajectory.msd`.
ResearchTurn `fb72c2ad-bed1-47d7-b557-f398f04a8ede` and ScientificResult
`26127c48-d736-4983-b035-b68db238f6a7` retain exact trajectory version
`a22745f2-17b6-434f-ba4c-3fe6bd244841`. The completed Job contains independent
`trajectory.msd` and `trajectory.diffusion` ToolCalls and eight persisted
MinIO Artifacts.

Authenticated product navigation from the Reports list reopened Report
`agent2_report_e54681009a0e49abe371247d9053ce61`. The report rendered the
independent `轨迹均方位移` Figure and persisted Table
`table.527203220b6850b18d5eef4295bd7181`, alongside the diffusion outputs,
four Evidence references, the 24-frame exact-version Viewer and the explicit
MSD limitations. The page had one `main` landmark, one labelled report-reader
region, no duplicate DOM IDs and no global overflow.

Read-only persistence counts before and after the normal report open were
identical:

```text
Jobs / ToolCalls / Artifacts / ScientificResultSnapshots
301 / 395 / 1565 / 203
```

The existing mobile and archived-source campaign for this same immutable
Turn/Result/Report/version already proves `390x844` usability, exact-version
historical access and zero recomputation. Therefore the top-level
`trajectory.msd` row is `PASS`; the standalone legacy planner run remains
retained only as compatibility history.

### 2026-08-31 composition-space and regression product qualification

The authenticated same-stack browser opened exact ResearchTurn
`fbbb0c51-4f39-4c97-ad7a-69ee089884a2`, Job
`job_agent2_fbbb0c514f394c97ad7a69ee089884a2`, ScientificResultSnapshot
`d984bb18-acc6-4d55-90e1-2097b0305a69` and ScientificResult
`f9f4fb16-edbe-53bc-9516-ebd3d7ba5b0a`. Interpretation
`432e6775-7590-4fc4-906e-e535c23809e8` and Report
`agent2_report_9b6943b7b3a9eaecd594ecf9bde7e806` are both grounded `VALID`.

The exact Dataset version
`cf2aeeea-53ad-452a-a4ef-7b61555004e5` rendered:

- the persisted composition-space Figure and Table with three stable samples,
  five element dimensions, PCA projection, clusters and descriptive-only
  limitations;
- the persisted regression diagnostic Table with `MAE=0.2`,
  `RMSE=0.21602468994692867`, `R²=0.9302325581395349`, explicit
  `prediction_minus_target` residual semantics, unknown-unit preservation and
  stable sample `sample-fe2o3`;
- Evidence traversal to completed ToolCall `dataset.composition_space`,
  Artifact
  `call_job_agent2_fbbb0c514f394c97ad7a69ee089884a2_step_1-table_json`,
  checksum
  `32adca799412da69b2fbf2204f635bdd4b52c801673a933ecec0fc9dacef5ea2`,
  and the exact source version;
- a professional Report with question, data/methods, discussion, limitations,
  conclusion, next steps, source Research link and bounded export controls.

At `390x844`, Report and Research measured `scrollWidth=390`, the mobile
Workbench exposed the real regression Table, and `sample-fe2o3` remained
visible. Browser warning/error logs were empty and duplicate DOM IDs were
zero. Before and after Figure/Table/Evidence/Report reads, PostgreSQL counts
remained `Jobs/ToolCalls/Artifacts/ScientificResults/Reports =
278/365/1450/184/36`, so no scientific recomputation occurred. Focused
frontend presentation/report/ML coverage passed `34/34`. These exact exercised
paths upgrade `data.composition_space` and `ml.regression_evaluation` to
`PASS`; unexercised capability families remain unchanged.

### 2026-08-31 coordination-histogram product qualification

The authenticated browser reopened ResearchTurn
`63d21ee3-6e18-49b3-ad6b-b3fb578563c5`, Job
`job_agent2_63d21ee36e1849b3ad6bb3fb578563c5`,
ScientificResultSnapshot `2382b0eb-b056-42b2-b6a7-d2e8a4ca398c` and
Interpretation `ee6b7667-d217-4a1e-82f9-b4be9152a93c` (`VALID`).

The product rendered the persisted coordination Figure and Table for exact
Structure version `8859cb49-0766-48cd-8a56-e44f5332e0c5`: one Si site,
coordination number 6, `3 Å` fixed-distance cutoff, a `100%` histogram row and
the explicit boundary that this is not CrystalNN, VoronoiNN or bond-order
authority. Evidence inspection resolved completed ToolCall
`structure.coordination_hist` and Plotly Artifact checksum
`0a595462eddb86b474ef9aba7ca17d78abc6d388c85fd67a8f55cf67aaeaeb0d`.

Using the normal product action generated Report
`agent2_report_19a0d0c261c28577101de81532464893`, snapshot
`c8cc6fcb-1f0b-50c6-b6db-049374f7de6e`, grounded `VALID`. The Report includes
the question, exact source, method, persisted Figure, findings, limitation,
conclusion and next steps. The only persisted delta was Reports `36→37`;
Jobs/ToolCalls/Artifacts/ScientificResults remained
`278/365/1450/184`. At `390x844` the Report measured `375/375` document/body
width, had zero duplicate IDs and no browser warnings/errors. Focused
coordination/presentation/report coverage passed `29/29`. This upgrades
`structure.coordination_hist` to `PASS`.
The legacy Planner Job has no Agent2 `ScientificResultSnapshot`; exact
ScientificObjectVersion, historical and archived Agent2 presentation campaigns
therefore remain open and prevent a `PASS` claim.

### 2026-08-30 source/viewer recovery and mobile evidence addendum

The authenticated same-stack browser rechecked the XRD/Data Platform surface after
restoring the repository-owned normalized scientific objects into the running MinIO
bucket. Dataset `dataset_0001_a3f92a7657f4493e` now resolves its persisted
`obj_structure_72a5ab29a949` and `obj_dataframe_4e34572e413c` resources through the
normal object-store authority. The desktop page rendered one validated XRD series
with 9 numeric values and the linked Structure Viewer rendered Si with one display
site; browser error/warning logs were empty.

At `390x844`, the same page measured `body.scrollWidth=388` and
`documentElement.scrollWidth=388` with no horizontal overflow. The data navigator
defaults to a compact, explicitly labelled `显示数据` control so the scientific
viewer remains primary; expanding it is user-controlled and does not change source
identity. Resource choices expose one strong resource label plus a current/switch
state rather than duplicate labels.

When a normalized source is genuinely unavailable, the secured API now returns the
typed `SOURCE_RESOURCE_UNAVAILABLE` `409` contract with retryable recovery guidance.
The Viewer surface presents `重试加载` and `查看来源与属性` actions without exposing
raw infrastructure errors or making the entire canvas an accidental button. These
checks validate source/viewer recovery and responsive presentation only; capability
families still marked `NOT_QUALIFIED` remain so until their real user paths are run.

### 2026-08-30 current-worktree same-stack capability batch

The current worktree was exercised against PostgreSQL
`127.0.0.1:55434/mdi`, Redis DB 13 and MinIO bucket `mdi-artifacts`, with
`MDI_RUN_INTEGRATION=1`. The selected service-backed files covered Agent2
planning/execution, interpretation, Report, coordination, XRD and professional
closure:

```text
selected = 12
passed = 12
failed = 0
errors = 0
skipped = 0
```

Two focused frontend runs passed `10/10` and `38/38`, covering exact ToolCall
pairing, XRD professional product projection, Dataset stable sample identity,
Coordination presentation, bounded malicious-label handling, registry
selection, Viewer read behavior and Evidence accessibility.

Current PostgreSQL contains persisted ScientificResult authority for
`data.materials_explorer`, `structure.coordination_crystalnn`,
`structure.coordination_voronoinn`, `diffraction.theoretical_xrd`,
`diffraction.experimental_theoretical_comparison` and `structure.rdf`.
Dataset, Coordination, XRD and RDF now also have authenticated browser
evidence, so those exercised rows are `PASS`. Renderer-only families remain
`NOT_QUALIFIED`.

### 2026-08-30 canonical RDF grounding and browser continuity

The real Data Platform handoff preserved exact Structure authority:

```text
ScientificObject = dc3c3eee-f254-4edf-a0fa-c955402b3069
ScientificObjectVersion = 8859cb49-0766-48cd-8a56-e44f5332e0c5
ResearchTurn = 54fdeada-af1e-4e65-8a8a-855fb52ae76c
AnalysisPlan = plan_a615abc9895649ab9b812912
Job = job_agent2_54fdeadaaf1e4e658a8a855fb52ae76c
ScientificResultSnapshot = a65dfde6-47f5-42fc-972c-66da77a27aa2
ScientificResult = 51baaff9-59ea-5a2e-8cad-931bbbd8586d
Interpretation = 87680594-fe78-46d6-8816-3e8a33993b09
grounding_status = VALID
Turn = COMPLETED
```

The canonical Result contains five deterministic facts with exact Artifact
locators: structure count, bin count, `r_max=8.0 angstrom`,
`bin_width=0.1 angstrom`, and
`number_density=0.037037 angstrom^-3`. The presentation renders those metrics,
the persisted RDF Figure and Table links, exact-version Viewer navigation,
Evidence disclosure, and the unchanged limitation that the projector does not
infer peaks or coordination shells.

The grounding boundary now accepts only equivalent inverse-cubic angstrom
spellings such as `angstrom^-3` and `Å⁻³`; an unsupported `nm^-3` unit and an
unsupported RDF peak claim remain rejected. Focused backend coverage is
`39 passed, 1 historical skip`. This closes the authenticated canonical RDF
scientific-content path without adding peak inference or another scientific
authority.

### 2026-08-30 canonical coordination continuity

The real authorized Structure Turn
`17b67e68-b7db-475b-bb4c-3b336cb2ba15` now has browser evidence for:

```text
CrystalNN + VoronoiNN ScientificResult
→ one Scientific Presentation
→ two Evidence references
→ exact Structure Viewer route
→ exact version disclosure
```

No scientific mutation request was emitted. The Viewer rendered the Structure
canvas and exact version `8859cb49-0766-48cd-8a56-e44f5332e0c5`; mobile
Research measured zero horizontal overflow. This upgrades the two coordination
rows from PARTIAL to PASS for the canonical authorized path, without changing
remaining NOT_QUALIFIED families.

For every row the intended authority chain is:

```text
exact ScientificObjectVersion
→ validated ToolCall
→ persisted Artifact
→ ScientificResult projector
→ bounded Presentation block
→ read-only Viewer/Table/Figure
→ Evidence and Report
```

No row permits frontend scientific computation, arbitrary renderer loading, or
silent current-version substitution. Desktop/mobile, historical, archived,
performance and security columns remain `NOT_QUALIFIED` until the
corresponding real-user evidence is recorded.

### 2026-08-31 electronic Report → Figure provenance repair

The authenticated same-stack Electronic report
`agent2_report_e7fa88beeb9a92cd8d46e44182ec46f9` now resolves its persisted
Figure descriptors to the matching exact source type instead of reusing the
first Result source for every figure. The Band figure resolves to
`electronic.band_structure` version
`7f7f1008-4d67-4592-a501-41d9a7d9a5cc`; the DOS figure resolves to
`electronic.dos` version
`087f93c4-2a5b-4c1e-b4e4-916c368801d0`. The report and presentation route
retain the same Result/Artifact authority, and the mobile browser measured
zero horizontal overflow. Backend Report coverage is `32 passed / 4 historical
compatibility skips`; the focused frontend Report/presentation/Shell batch is
`41 passed`.

### 2026-08-31 Phonon presentation/report/browser requalification

The same-stack authenticated browser requalified the persisted Phonon
Band + DOS result without creating a new scientific record:

```text
ScientificResultSnapshot = 405ee6b6-9cb8-4ebc-bc8a-7d7332feb46b
ScientificResult = 980afdc5-5f6b-5023-923a-974b9961bdd0
Interpretation = f6b8a955-4fc3-4139-903f-2f3f3362bcb3 (VALID)
Report = agent2_report_a015ca23c3a9bceee669c9725da408a1
```

The Report now reuses the same deterministic limitation-language mapping as
Research, so persisted English limitation strings are rendered in the
Chinese scientific workbench vocabulary. The Report exposed three persisted
Figures, two exact-version Viewer links, nine evidence references and two
exact source versions. The Phonon Band Viewer rendered six branches across
three q-points with a `0–5 THz` range; the mobile browser measured
`390/390` document/body width with no global overflow. Browser logs contained
zero errors or unhandled rejections.

Before and after Report → Research → Viewer navigation, PostgreSQL counts
remained `jobs/tool_calls/artifacts/scientific_result_snapshots/reports =
258/339/1359/181/33`; therefore read-only presentation, artifact, evidence
and Viewer navigation caused no scientific recomputation. These rows are
`PASS` for the exercised same-stack path; phonon animation remains outside the
current authority because no eigenvector Artifact is supplied.

The same browser batch also requalified the Electronic Band and DOS data
surfaces at exact versions
`7f7f1008-4d67-4592-a501-41d9a7d9a5cc` and
`087f93c4-2a5b-4c1e-b4e4-916c368801d0`. Both render real typed tables with
authoritative eV/state-density units, explicit unavailable/partial boundaries,
and zero mobile overflow. Full Electronic Research/Report browser coverage
remains `PARTIAL` until a complete multi-surface report/evidence path is
captured.

### 2026-08-31 trajectory RDF report and Viewer path

The authenticated same-stack browser opened the existing exact trajectory run
and generated a persisted Report without rerunning the scientific Job.
Report `agent2_report_55692c117165c20c3da272ef75e28118` retained exact
trajectory version `052d3a8e-8a35-48ac-9e65-b95a86b42c99`, rendered five
bounded findings (3 included frames, 2 atoms, 0.0–2.0 Å range, 200 bins and
3 pair samples), a persisted RDF Figure, two evidence references, and the
limitation that RDF peaks are not automatically chemical bonds or coordination
shells. The route measured zero horizontal overflow and exposed the exact
trajectory Viewer link. This upgrades `trajectory.rdf` to `PASS`. The later
standalone real-source MSD campaign below initially upgraded `trajectory.msd`
to `PARTIAL`; the canonical Agent2 MSD/diffusion path documented above
subsequently closes both rows as `PASS`.

### 2026-08-31 trajectory MSD real-source, Viewer and Report path

The normal authenticated upload-session path ingested the repository-owned
explicit-unwrapped EXTXYZ fixture into Dataset
`dataset_0001_b7f22cb1bb074f1a`, Profile
`profile_dataset_0001_b7f22cb1bb074f1a_v2`, and source object
`obj_trajectory_990aa1224948`. The stored source checksum is
`3424c71e0df3137e72529a868b8596769017f18dc3a6e5696e8a28855a138649`;
normal parsing preserved `positionWrapping=unwrapped` and trajectory
readiness is `READY`.

The exact Data-to-Research handoff produced Plan
`plan_72e81c4f236b4510b8d23450`, Job
`job_f2b56ba7d4a34c9288600852`, four persisted artifacts and Interpretation
`interpretation_fed32da21ee465e9e18d19048d559e93`
(`INTERPRETATION_READY_WITH_LIMITS`, grounding `VALID`). The product displayed
three authoritative lag rows and final MSD `0.0009 Å² @ 0.003 ps`; it
explicitly stated that no diffusion coefficient was estimated.

The Dataset object-store projection now unwraps only the normalized dataclass
wrapper at the API read boundary, so the existing worker authority remains
unchanged while the trajectory Viewer receives the canonical payload. The
authenticated Viewer rendered all four frames, wrapping metadata, time,
lattice, selection/measurement controls and the interactive renderer. The
MSD narrative no longer appends the unrelated RDF included-frame fact, so a
missing RDF fact cannot produce `NaN` text.

Opening Report → Research → Report was read-only: persisted counts for
Jobs/ToolCalls/Artifacts/Interpretations/Reports stayed
`261/341/1363/17/36`. This standalone legacy planner path did not create an
Agent2 ResearchTurn/ScientificResultSnapshot, so it remains compatibility
evidence only. The canonical Agent2 MSD/diffusion acceptance documented above
provides the missing snapshot, mobile, historical and archived evidence and is
the authority for the current `PASS` status.

### 2026-09-04 current-worktree route-level recheck

Against the current production frontend on `127.0.0.1:3020`, an authenticated
read-only sweep opened all `13/13` populated ScientificObject /
ScientificObjectVersion entries in the active project. Electronic DOS,
Phonon Band/DOS, Dataset and ML tables, Electronic Band, Structure, Trajectory
and Diffusion surfaces all reached their declared renderer or bounded fallback
after hydration. No route rendered `Internal Server Error`, `Application
error`, `SOURCE_MISSING`, or an alert failure; desktop overflow was `0 px`.
Structure and trajectory entries mounted real canvas renderers, and the
Structure detail showed a real `Si` site/cell payload plus exact-version
metadata. This recheck does not change the historical `PARTIAL` boundaries for
capability families not yet covered by an independent real-user campaign.

### 2026-09-04 explicit safe state for static/download-only artifacts

The workspace renderer registry already classifies `preview_png`,
`figure_pdf`, `matterviz_snapshot_png`, `plotly_html`, `figure_svg` and
other non-executable file contracts as `STATIC_METADATA` or `DOWNLOAD_ONLY`.
The renderer previously had no explicit branch for those classifications, so
they fell through to generic inert-fallback copy even though the registry had
intentionally made a safe disposition. The bounded renderer now presents an
explicit researcher-facing metadata/download state with artifact contract,
filename/size where available and checksum summary. It does not inline or
execute HTML, script, image payloads or arbitrary renderer code, and directs
users to the existing result-directory download action for the original bytes.

Deterministic frontend coverage is `8/8` for the workspace gallery and
renderer registry, including a metadata-only `preview_png` and a
download-only `plotly_html` containing a script token. The script token is
not rendered or executed. This closes the renderer-wiring gap for the
declared safe classifications without changing scientific authority,
provenance, or version resolution.
