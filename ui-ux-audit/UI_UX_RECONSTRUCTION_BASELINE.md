# UI/UX Reconstruction Baseline

## 1. Executive Summary

### Product
Material Data Intelligence is a **scientific materials analysis platform** that allows researchers to:
- Upload material datasets (CSV, CIF, POSCAR, XYZ, ZIP)
- Submit natural-language analysis requests
- Generate validated JSON AnalysisPlans via LLM
- Execute bounded scientific tool adapters (pymatviz, Plotly, pymatgen, ASE, phonopy)
- View structured execution timelines, interactive visualizations, and grounded scientific interpretations
- Persist results in Scientific Workspaces with report composition

### Architecture
- **Frontend**: Next.js 15 / React 19 / TypeScript / Zustand / Three.js / Plotly.js
- **Backend**: FastAPI (Python) with SQLite/Redis, LLM providers (DeepSeek, Mock), QueueWorkerRuntime
- **Monorepo**: `apps/web`, `apps/api`, `services/llm`, `services/workers`, `packages/`, `tool_registry/`
- **Design System**: Custom CSS (4083 lines in `globals.css`) with "Design System 2.0" primitive and semantic tokens. No external component library.

### Major Workflows
1. Dataset selection/upload → Profile generation → Prompt submission → Intent analysis → Plan validation → Job execution → Results → Interpretation → Workspace
2. Scientific Workspace: persistent view of job results with artifact gallery, report composer, selection contract, and inspector

### Overall UI/UX Maturity
**Capable engineering prototype with professional-quality CSS foundations but insufficient visual hierarchy, excessive density, and monolithic component architecture.**

The platform is functionally rich, has a coherent design token system, supports i18n (zh-CN/en-US), and has accessibility foundations (skip links, ARIA, focus-visible). The primary UX weakness is information overload: all panels render with equal visual weight, developer-oriented information leaks into user mode, and the results tab presents 10+ panels without progressive disclosure.

### Highest-Risk UX Issues
1. Global Context Bar occupies excessive horizontal space at all viewports, competing with the primary task
2. Results tab has unbounded vertical scrolling with 10+ panels
3. Developer/audit information visible in non-developer mode for several panels
4. Monolithic component (2970 lines, ~50 useState hooks) prevents incremental improvement
5. Mobile experience below 768px lacks explicit planner shell adaptation

### Highest-Risk Technical/UI Coupling
- PlannerWorkbench.tsx (2970 lines) manages all state, tabs, dialogs, and viewers in one component
- Scientific viewers (Three.js) are conditionally rendered inside tab panels — tab switching destroys/recreates them
- No React Suspense boundaries, no dynamic imports, no code splitting for heavy viewers

### Major Unknowns
- Runtime behavior could not be browser-verified (requires backend services running)
- Actual perceived latency for LLM plan generation and job execution
- Real mobile touch interaction with 3D viewers
- Actual bundle size after tree-shaking

---

## 2. Investigation Scope

### Files/Documents Reviewed
| Category | Files |
|----------|-------|
| Product docs | README.md, docs/03_FRONTEND_WORKSPACE_DESIGN.md, docs/03A_FRONTEND_COMPONENT_SPEC.md, docs/03B_FRONTEND_STATE_AND_INTERACTION.md |
| Frontend source | apps/web/package.json, app/page.tsx, app/layout.tsx, app/globals.css (4083 lines), app/components/PlannerWorkbench.tsx (2970 lines, full read), app/components/workspace/ScientificWorkspaceShell.tsx (200 lines), app/lib/i18n.ts, app/lib/planner-api.ts, app/lib/workspace-api.ts, app/lib/messages/zh-CN.ts |
| Backend source | apps/api/mdi_api/routers/planner.py (function inventory, route structure) |
| Workspace route | app/workspaces/[workspaceId]/page.tsx, error.tsx, loading.tsx |
| Config | next.config.mjs, pnpm-workspace.yaml |

### Viewports Analyzed (from CSS @media queries)
- 1180px — Global context bar collapse
- 900px — Workspace layout shift
- 820px — Planner secondary collapse
- 760px — Multiple component breakpoints
- 640px — Mobile primary breakpoint
- 600px — Workspace report breakpoint
- 560px — Workspace artifact breakpoint

### What Was Excluded
- Full backend execution testing (requires running services)
- Browser automation / Playwright screenshots
- Performance profiling (requires running app)
- Automated accessibility scanning
- Full workspace shell review (first 200 lines only)

---

## 3. Current Product Model

### Purpose
An AI-powered materials science analysis workbench that bridges natural language requests to bounded, validated scientific computations with full provenance tracking.

### Main Entities
| Entity | Role |
|--------|------|
| Project | Container for datasets and jobs |
| Dataset | Uploaded material data (CSV, CIF, POSCAR, etc.) |
| DataProfile | Deterministic analysis of dataset capabilities and readiness |
| AnalysisIntent | Structured interpretation of user's natural language goal |
| AnalysisPlan | LLM-generated, validator-approved multi-step execution plan |
| Job | Queued execution unit bound to a persisted plan |
| ToolCall | Individual adapter execution within a job |
| Artifact | Output file/data from a tool call (charts, JSON, 3D scenes) |
| Interpretation | Grounded scientific conclusions with evidence lineage |
| Workspace | Persistent organized view of job+artifacts+interpretation |
| Report | Composed scientific document from workspace artifacts |
| Recipe | Reproducibility specification |

### User-Visible Concepts
- 数据集 (Dataset), Profile, 分析意图 (Analysis Intent), 分析计划 (Analysis Plan), 任务 (Job), 工具调用 (Tool Call), 产物 (Artifact), 科学解释 (Interpretation), 工作区 (Workspace), 报告 (Report), 配方 (Recipe)
- Developer concepts (hidden by default): planId, planHash, intentId, graphHash, provenance bindings

---

## 4. Repository & Frontend Architecture

### Directory Map
```
apps/
├── web/                    Next.js 15 frontend
│   ├── app/
│   │   ├── page.tsx        Root → PlannerWorkbench
│   │   ├── layout.tsx      Minimal root layout
│   │   ├── globals.css     4083-line design system + all component styles
│   │   ├── components/
│   │   │   ├── PlannerWorkbench.tsx          (2970 lines, monolithic)
│   │   │   ├── viewer-scene/                3D structure viewer (Three.js)
│   │   │   ├── trajectory-viewer/           MD trajectory viewer
│   │   │   ├── phonon-band/                 Phonon band structure
│   │   │   ├── phonon-dos/                  Phonon DOS
│   │   │   ├── phonon-band-dos/             Combined phonon
│   │   │   ├── phonon-animation/            Phonon mode animation
│   │   │   ├── brillouin-zone/              BZ visualization
│   │   │   ├── band-bz-link/                Linked band+BZ view
│   │   │   ├── volumetric-viewer/           Volumetric field viewer
│   │   │   ├── composition-space/           Composition explorer
│   │   │   ├── dataset-explorer/            Dataset materials explorer
│   │   │   ├── materials-ml/                ML evaluation panel
│   │   │   ├── material-intelligence/       Intelligence integration
│   │   │   ├── workspace/                   Scientific Workspace (shell + 15+ files)
│   │   │   └── design-system/               StatusLabel component
│   │   ├── workspaces/[workspaceId]/        Dynamic workspace route
│   │   └── lib/
│   │       ├── planner-api.ts               API client + all types (~150+ exports)
│   │       ├── workspace-api.ts             Workspace API client + types
│   │       ├── i18n.ts                      Translation system
│   │       ├── messages/{zh-CN,en-US}.ts    ~150+ message keys each
│   │       └── *Contract.ts                 Data contracts for scientific viewers
│   └── test/                               Vitest + browser evidence scripts
├── api/                    FastAPI backend
│   └── mdi_api/routers/    planner, datasets, health, tools, workspaces, secrets, etc.
services/
├── llm/                    LLM provider abstractions (DeepSeek, Mock, OpenAI-compatible)
└── workers/                Queue worker runtime
tool_registry/              Scientific tool manifests
```

### Routing
| Route | Component | Purpose |
|-------|-----------|----------|
| `/` | PlannerWorkbench | Main analysis workspace (single-page experience) |
| `/workspaces/[workspaceId]` | ScientificWorkspaceShell | Persistent scientific workspace |

### Shell Structure
- Root layout: Minimal `<html><body>` wrapper with globals.css import
- **No shared layout between routes** — each is self-contained
- No global navigation shell, no shared header/sidebar

### State Management
- **PlannerWorkbench**: ~50 `useState` hooks in one component (no external store)
- **ScientificWorkspaceShell**: Similar pattern (~30 useState + useCallback/useEffect)
- **Scientific viewers**: Zustand stores (listed in package.json) for viewer-specific state
- **React Query**: Listed as dependency (`@tanstack/react-query ^5.80.0`) but not observed in main planner flow
- **No global state provider** wrapping the app

### Styling System
- **No component library** (no shadcn, Radix, MUI, Chakra, Tailwind)
- Pure CSS in single `globals.css` (4083 lines)
- Design System 2.0 tokens via CSS custom properties
- Token layers: Primitive (`--ds-color-graphite-*`) → Semantic (`--color-background`) → Legacy aliases (`--bg`, `--panel`)

---

## 5. Documentation / Code / Runtime Contradictions

| ID | Documentation Says | Code Says | Runtime Says | Current Conclusion |
|----|-------------------|-----------|--------------|--------------------|
| C1 | Component spec (03A) defines `DeveloperAuditDrawer` as separate overlay | PlannerWorkbench uses inline `<details>` blocks with `developerMode` conditionals | Not verified | Drawer concept never implemented; developer info scattered inline |
| C2 | Spec requires `FullscreenResultModal`, `ArtifactPreviewModal` | No modal implementation found | Not verified | Overlays not implemented |
| C3 | Spec defines `ThemeToggle` as functional | Code renders `◐` icon button with no theme switching logic | Not verified | Theme toggle is non-functional placeholder |
| C4 | Doc: "小屏幕下左侧进入 Drawer" (left panel becomes drawer on small screens) | No drawer component exists in PlannerWorkbench; CSS stacks vertically | Not verified | Responsive drawer NOT implemented |
| C5 | Doc: "Tab 切换不能导致数据丢失" (tab switch must not lose data) | Tabs use conditional render (`activeTab === X ? content : null`) which unmounts | Not verified | State preserved in parent hooks but heavy components (viewers) are destroyed/recreated |
| C6 | Spec defines separate `ConversationChunkList`, `UserRequestChunk`, `PlanPreviewChunk` | All inline in PlannerWorkbench as `buildConversationChunks` + single button render | Not verified | Conceptual model exists but no component extraction |

---

## 6. Route & Page Inventory

| Route | Purpose | Entry Points | Major Actions | Major Components | Data Source | Auth | Responsive |
|-------|---------|-------------|---------------|-----------------|-------------|------|------------|
| `/` | Main analysis planner | Direct URL, app launch | Dataset select, prompt submit, plan review, job execution, interpretation, workspace open | PlannerWorkbench (GlobalContextBar, DataContextShell, MainWorkspaceTabs, 3 Dialogs) | REST API + SSE | None | Partial (no mobile planner rules) |
| `/workspaces/[id]` | Scientific workspace | "Open Workspace" button | View artifacts, compose reports, inspect selections, navigate panels | ScientificWorkspaceShell (Header, SaveBar, Layout, Inspector, MobileDrawer) | REST API + optimistic local | None | Yes (900/640/560px) |

---

## 7. Current Information Architecture

```
Application
├── / (Planner Workbench)
│   ├── Global Context Bar
│   │   ├── Brand block ("Material Data Intelligence")
│   │   ├── Primary Navigation (Home, Data, Analyses, Workspaces, Reports, Settings)
│   │   ├── Dataset Context Button → DatasetCommandDialog
│   │   ├── Model Context Button → ModelProviderDialog
│   │   ├── Job Status Pill (read-only)
│   │   └── Settings area (Workspace History btn, Language, Theme, Settings, Help, Dev Toggle)
│   ├── Data Context Panel (Left, resizable 240-520px, collapsible)
│   │   └── Format-adaptive profile (table/structure/archive/unsupported/intelligence)
│   └── Main Workspace Tabs (mutually exclusive)
│       ├── Agent Process Tab
│       │   ├── Timeline event list
│       │   ├── Provenance panel
│       │   └── System health panel
│       ├── Conversation & Plan Tab
│       │   ├── Stage rail (Data→Intent→Plan→Execution→Results)
│       │   ├── Prompt composer (textarea + examples + submit)
│       │   ├── Error explainer (conditional)
│       │   ├── Validation failure (conditional)
│       │   ├── Analysis intent panel (conditional)
│       │   ├── Capability planning panel (conditional)
│       │   ├── Conversation chunk list
│       │   ├── Plan preview panel
│       │   ├── Dependency execution panel (conditional, plan v0.2)
│       │   └── Run controls
│       └── Results & Export Tab
│           ├── Snapshot partial failure (conditional)
│           ├── Selected result context + Workspace entry
│           ├── Report/Recipe summary
│           ├── Grounded interpretation
│           ├── Material intelligence integration
│           ├── Dataset materials explorer
│           ├── Composition space explorer
│           ├── Materials ML evaluation
│           ├── Material result renderer
│           ├── Metrics result renderer
│           ├── Table summary renderer
│           ├── Viewer static preview (3D structure)
│           ├── BZ / Band-BZ linked view
│           ├── Trajectory preview
│           ├── Volumetric preview
│           ├── Phonon animation
│           ├── Phonon Band+DOS / Band / DOS
│           ├── Artifact gallery (grouped by type)
│           ├── Tool call list
│           └── Export controls
├── /workspaces/[id] (Scientific Workspace)
│   ├── Header (title, status, back link, actions)
│   ├── Save bar (title input, save/conflict actions)
│   ├── Guide (collapsible)
│   ├── Recovery alerts (conditional)
│   ├── Selection banner (conditional)
│   ├── Layout (3-column: data rail | navigation | main panel)
│   ├── Inspector drawer (right, overlay)
│   └── Mobile context drawer (left, overlay)
└── Dialogs (modal overlays)
    ├── DatasetCommandDialog (dataset list, upload, demo, profile preview)
    ├── ModelProviderDialog (provider mode, model select, test connection)
    └── WorkspaceHistoryDialog (project workspace list)
```

### IA Issues
- Primary nav mixes page links (`<a href="/">`), dialog openers (buttons), and tab switchers — inconsistent affordances
- "Home" link points to `/` which IS the current page
- "Settings" nav item opens ModelProviderDialog rather than actual settings
- Workspace History accessible from both nav button and top-settings button (duplicated entry)
- No breadcrumbs between Planner and Workspace routes
- Workspace route has its own back link but no shared navigation context

---

## 8. Component Inventory

### Primitives (all custom, no library)
| Component | Implementation | Notes |
|-----------|---------------|-------|
| Button | Native `<button>` + CSS variants | primary, secondary, compact, icon-button, file-button |
| Input/Select/Textarea | Native elements + global CSS | No custom wrappers |
| Dialog | `.dialog-backdrop` + `.dialog-panel` pattern | No focus trap, no Escape |
| Segmented control | `.segmented` div with buttons | Language toggle, interpretation mode |
| Badge/Pill | `.section-heading span` | Status badges in panel headings |
| Skip link | `.skip-link` | Accessibility skip to content |
| Resize handle | `<button role="separator">` | With keyboard support |

### Composites (inline functions in PlannerWorkbench)
| Component | Purpose | Reuse Count |
|-----------|---------|-------------|
| PanelHeading | Title + badge for panels | ~30+ |
| Field/TestField | dt/dd pair in mini-grid | ~100+ |
| CompactTable | Small data tables for viewers | ~5 |
| SecurityBadge | Boolean security indicators | ~4 per viewer |
| ErrorExplainer | Structured error display | 1 |
| FormatAdaptiveProfile | Dataset profile display | 2 (left panel + dialog) |
| MaterialProfileIntelligence | Capability/readiness display | 1 |

### Scientific Viewer Components (separate files)
| Component | File | Purpose |
|-----------|------|---------|
| ViewerSceneRendererSurface | viewer-scene/ | 3D crystal structure viewer (Three.js) |
| TrajectoryViewerSurface | trajectory-viewer/ | MD trajectory replay |
| PhononBandPreviewPanel | phonon-band/ | Phonon band structure |
| PhononDosPreviewPanel | phonon-dos/ | Phonon DOS |
| PhononBandDosPreviewPanel | phonon-band-dos/ | Combined phonon band+DOS |
| PhononAnimationSurface | phonon-animation/ | Phonon mode animation (Three.js) |
| BrillouinZonePreviewPanel | brillouin-zone/ | Brillouin zone (Three.js) |
| BandBZLinkedView | band-bz-link/ | Linked band+BZ coordination |
| VolumetricPreviewPanel | volumetric-viewer/ | Volumetric field slicing/isosurface |
| DatasetMaterialsExplorerPanel | dataset-explorer/ | Dataset-wide material navigation |
| CompositionSpaceExplorerPanel | composition-space/ | Composition space visualization |
| MaterialsMlEvaluationPanel | materials-ml/ | ML model evaluation |

### Workspace Components (separate files in workspace/)
| Component | Purpose |
|-----------|---------|
| ScientificWorkspaceShell | Main workspace shell with load/save/conflict |
| WorkspaceArtifactGallery | Artifact browsing with active artifact display |
| WorkspaceReportComposer | Report composition from artifacts |
| WorkspaceGenericPlot | Plotly-based generic plot renderer |
| CoordinationResultPanel | Coordination analysis display |
| LocalEnvironmentPolyhedraPanel | Local environment visualization |
| ExperimentalXrdComparisonPanel | XRD comparison display |
| TrajectoryAnalyticsPanel | Trajectory analysis (RDF, MSD) |
| ElectronicStructurePanel | Electronic band/DOS display |
| StatusLabel | Design system status badge |

### Duplicated/Inconsistent Implementations
- Dialog close: `×` character in Dataset/Model dialogs vs `X` text in WorkspaceHistory
- Panel heading: `PanelHeading` function in planner vs `.workspace-panel-header` CSS in workspace
- Metadata grid: `.mini-grid` in planner vs `.workspace-metadata-grid` in workspace
- Empty states: `<p className="empty-state">` vs custom notice divs vs role="status" patterns
- Active/selected states: `.active` (accent bg) vs `.selected` (accent border)

---

## 9. API & UI Contract Map

### Major UI → API Operations
| UI Action | API Call | Response Shape | UI Update |
|-----------|----------|---------------|----------|
| Initial load | `GET /health` + `GET /datasets` + `GET /planner/providers` + `GET /planner/provider-status` | Health, DatasetOption[], ProviderOption[], ProviderStatus | Populate context bar silently |
| Select dataset | `GET /datasets/{id}/profile` | DataProfileSummary | Left panel + data message |
| Load demo | `POST /datasets/demo` | Dataset + DataProfileSummary | Auto-select, switch to mock mode |
| Upload file | `POST /datasets` | Dataset + optional profile | Add to list, auto-select |
| Generate profile | `POST /datasets/{id}/profile` | DataProfileSummary | Update left panel |
| Submit analysis | `POST /planner/jobs` | PlannerJobCreateResult (plan, job_id, validation_errors, capability) | Plan preview, start SSE |
| Clarify intent | `POST /planner/intents/{id}/clarify` | Revised AnalysisIntent | Re-submit if READY |
| Monitor execution | SSE `/planner/jobs/{id}/events/stream` | Server-Sent Events | Real-time timeline |
| Refresh snapshot | 6× parallel `GET` (job, events, tool_calls, artifacts, result, dependencies) | WorkspaceSnapshot | Full state update |
| Test provider | `POST /planner/providers/test` | ProviderTestResult | Result card |
| Resolve provider | `POST /planner/providers/resolve` | ProviderResolveResult | Provider label |
| Generate interpretation | `POST /planner/jobs/{id}/interpretation` | InterpretationResponse | Interpretation panel |
| Get interpretation evidence | `GET /planner/interpretations/{id}/evidence` | InterpretationEvidenceResponse | Evidence items |
| Create workspace | `POST /workspaces` | WorkspaceId | Navigate to workspace route |
| List workspaces | `GET /projects/{id}/workspaces` | WorkspaceSummary[] | History dialog |

### SSE Event Protocol
```
EventSource connects to /planner/jobs/{id}/events/stream?after_seq=N
Event types (in execution order):
  plan.generated → plan.persisted → job.queued → plan.loaded → data.loaded
  → tool.started → tool.completed (per tool)
  → artifact.ready (per artifact)
  → job.completed | job.failed

On EventSource error → close + switch to 2.5s polling fallback
On terminal event → full snapshot refresh
```

---

## 10. Entity & State Model

### Job Lifecycle
```
created → queued → running → completed | failed | partial_success
```

### AnalysisIntent Outcomes
```
READY → proceed to plan generation
NEEDS_CLARIFICATION → show clarification form, re-submit on answer
UNSUPPORTED → show unsupported reasons, block execution
```

### Capability Planning Outcomes
```
PLAN_READY | VALIDATION_FAILED | NO_ELIGIBLE_TOOLS | PARTIAL_COVERAGE
```

### Workspace Status
```
INITIALIZING | RUNNING | PARTIAL_RESULTS | COMPLETE | FAILED | READY | STALE | LEGACY_READ_ONLY | UNSUPPORTED | SOURCE_MISSING
```

### Workspace Panel States (per panel)
```
NOT_APPLICABLE | READY_NOT_RUN | LOADING | PRODUCED | PARTIAL | UNAVAILABLE | FAILED | BLOCKED_BY_DEPENDENCY | STALE | CAP_EXCEEDED | CONTRACT_UNSUPPORTED | SOURCE_DELETED | PROFILE_AUTHORITY_UNAVAILABLE
```

---

## 11. State Matrix

| Surface | State | Trigger | Visible UI | Available Actions | Verified? |
|---------|-------|---------|-----------|-------------------|----------|
| App shell | Initial load | Page open | Empty panels, no spinner | Wait | Inferred |
| Dataset context | Empty | No dataset | "请选择数据集" | Open dialog | Verified |
| Dataset context | Loading | Dataset selected | "正在读取数据上下文" | Wait | Verified |
| Dataset context | Ready | Profile loaded | Format-adaptive display | Collapse, resize | Verified |
| Dataset context | Collapsed | User collapses | 44px narrow column with expand button | Expand | Verified |
| Provider | Not configured | No secret | Status text in model button | Open model dialog | Verified |
| Provider | Ready | Resolution successful | Provider label with model name | Submit | Verified |
| Prompt | Idle | Page load (with example pre-filled) | Textarea with text | Edit, submit | Verified |
| Submission | Submitting | Submit clicked | Button disabled, "提交中..." | Wait | Verified |
| Submission | Validation failed | Plan invalid | Red validation-failure panel | Fix and retry | Verified |
| Submission | Error | API error | ErrorExplainer with 4-part recovery | Retry, modify | Verified |
| Intent | NEEDS_CLARIFICATION | Ambiguous request | Clarification form with select options | Answer, submit | Verified |
| Intent | UNSUPPORTED | Out of scope | Red alert with boundary reasons | Modify request | Verified |
| Job | Queued | Plan validated + enqueued | Timeline shows job.queued event | Watch | Verified |
| Job | Running | SSE events arriving | Timeline items accumulate | Switch tabs | Verified |
| Job | Completed | Terminal event | All snapshot data available | View results, interpret | Verified |
| Job | Failed | job.failed event | Error in timeline + snapshot | Review error | Verified |
| Interpretation | Not generated | Job terminal, no interp | "NOT GENERATED" badge, mode selector | Generate | Verified |
| Interpretation | Busy | Generate clicked | "Interpreting..." disabled button | Wait | Verified |
| Interpretation | Ready | Success response | Claims + evidence + recommendations | Browse, audit | Verified |
| Workspace | Loading | Route entered | Loading.tsx: "Loading Workspace" | Wait | Verified |
| Workspace | Ready | Data loaded | Full 3-column layout | Navigate, inspect, save | Inferred |
| Workspace | Error | Route error | Error.tsx with retry + back link | Retry, navigate back | Verified |
| Workspace | Dirty | Title/state edited | Save state label changes | Save | Inferred |
| Workspace | Conflict | Server revision diverged | Conflict banner with resolution actions | Resolve | Inferred |

---

## 12. Critical User Journeys

### Journey A — First Analysis (Happy Path)
| # | User Action | System Response | Feedback | Friction |
|---|-------------|----------------|----------|----------|
| 1 | Open app | Context bar + empty panels render | No loading indicator | Silent API calls |
| 2 | Click dataset button in context bar | DatasetCommandDialog opens | Dialog appears | Project ID field visible (technical) |
| 3 | Click "加载演示数据" | Demo loads, dialog closes, profile appears | "Demo 数据已加载" | Good |
| 4 | Review profile in left panel | Format-adaptive display | Immediate | Good |
| 5 | Review/edit prompt in Conversation tab | Pre-filled example prompt visible | - | Good |
| 6 | Click "创建并运行" | Button disabled, plan generates | "提交中..." | Good |
| 7 | Intent panel appears | Shows READY / NEEDS_CLARIFICATION | Panel renders | May require clarification answers |
| 8 | Plan preview appears | Human-readable steps | Success | Good |
| 9 | Job starts executing (auto-enqueued) | SSE events stream to Agent tab | Timeline grows | Must switch tab to see |
| 10 | Job completes | Terminal event, snapshot refreshes | No auto-tab-switch | User must manually go to Results |
| 11 | View results | 10+ panels in results tab | Extensive scrolling | Information overload |
| 12 | Generate interpretation | Click button, wait | "Interpreting..." | Good |
| 13 | Open workspace | Click "Open Workspace", page navigates | Full navigation | Context lost |

**Meaningful actions**: 8-10 clicks minimum
**Context switches**: 3 tab switches (Conversation→Agent→Results)
**Risk points**: No auto-navigation on job complete; tab switch destroys viewer state

### Journey B — Custom Dataset Upload
| # | User Action | Friction |
|---|-------------|----------|
| 1 | Open dataset dialog | Must see/set Project ID |
| 2 | Click file upload label | Hidden `<input type="file">` behind label |
| 3 | Select file | `file.text()` reads as string — binary files may fail |
| 4 | Wait for upload + profile | Single status text, button disabled |
| 5 | Dialog auto-closes on success | Good |
| 6 | Left panel updates with profile | Good |

---

## 13. Interaction Feedback Audit

| Operation | Immediate Ack | Progress | Completion | Failure | Recovery |
|-----------|--------------|----------|-----------|---------|----------|
| Submit analysis | Button disabled + text change | "提交中..." | Tab content updates | ErrorExplainer | Structured suggestions |
| Upload file | dataBusy disables buttons | Status text | Dialog closes | Error in submitError | Try again |
| Load demo | dataBusy disables buttons | Status text | Dialog closes + profile shows | Error | Manual retry |
| SSE events | Timeline item appears instantly | Progressive list growth | Terminal event | Fallback to polling | Transparent |
| Generate interpretation | Button text "Interpreting..." | Same | Panel populates | Diagnostics list | Clear |
| Open workspace | Button "Opening Workspace" | Same | Page navigates | Error alert inline | Error text |
| Provider test | None immediate | None | Result card (success/error) | Error card | Retry button |

### Silent Operations (No User Feedback)
- Initial health/dataset/provider/status loading on page open
- Provider resolution on mode/model change
- Snapshot refresh (6 API calls) after job terminal event
- Tab switching (no transition animation)

---

## 14. Visual System Audit

### Typography
| Level | Size | Weight | Line-height | Use |
|-------|------|--------|-------------|-----|
| h1 | 20px | 700 (inherited) | 1.15 | Brand title |
| h2 | 16px | 700 | 1.25 | Panel headings |
| h3 | 14px | 700 | 1.3 | Section headings |
| Eyebrow | 11px | 850, uppercase | - | Category labels |
| Body | ~14px (inherited) | 400 | 1.45 | Content |
| Labels (dt) | 11px | 900, uppercase | - | Field labels |
| Values (dd) | 13px | 700 | - | Field values |
| Small/muted | 12-13px | 700-800 | - | Metadata |
| Code/pre | 12px | monospace | - | JSON, code blocks |

**Font stack**: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif
**Feature settings**: `"tnum" 1, "liga" 1`
**Issue**: dt at 11px/900/uppercase is very dense and hard to scan; h1/h2/h3 are close in size (20/16/14), creating weak hierarchy.

### Spacing (DS2.0 Tokens)
| Token | Value | Actual Usage |
|-------|-------|-------------|
| --ds-space-1 | 4px | Minimal |
| --ds-space-2 | 8px | Grid gaps, small padding |
| --ds-space-3 | 12px | Panel gaps, section spacing |
| --ds-space-4 | 16px | Workspace panels |
| --ds-space-5 | 24px | Sparse usage |
| --ds-space-6 | 32px | Sparse usage |

**Inconsistency**: Many hardcoded values (7px, 9px, 10px, 14px, 18px) don't map to any token. Panel padding is 14px (not a token value).

### Color System
| Semantic Token | Value | Use |
|----------------|-------|-----|
| --color-background | #f4f6f5 (graphite-50) | Page bg |
| --color-surface | #ffffff | Panels |
| --color-surface-sunken | #eef2f0 | Nested areas, inputs |
| --color-border | #d6ded9 | Default borders |
| --color-border-strong | #aebbb4 | Emphasized borders |
| --color-text-primary | #17211e (graphite-950) | Main text |
| --color-text-secondary | #44514b (graphite-700) | Supporting text |
| --color-text-muted | #66736d (graphite-500) | Labels, metadata |
| --color-accent | #08756c (accent-600) | All interactive elements |
| --color-accent-hover | #075a53 (accent-700) | Hover state |
| --color-focus-ring | #0a8277 | Focus outline |
| --color-status-success | #16663e | Completed states |
| --color-status-warning | #865711 | Warning/partial |
| --color-status-danger | #ae2c23 | Errors, failures |

**Issue**: Single accent (#08756c) for buttons, links, nav active, badges, progress, selection — "teal soup" effect where nothing stands out.

### Borders / Radius / Elevation
| Token | Value |
|-------|-------|
| --ds-radius-sm | 4px |
| --ds-radius-md | 6px |
| --ds-radius-lg | 8px |
| --ds-radius-pill | 999px |
| --ds-shadow-subtle | 0 1px 2px rgba(23,33,30,0.06) |
| --ds-shadow-overlay | 0 12px 28px rgba(23,33,30,0.16) |

**Issue**: Every panel has `border: 1px solid var(--border); border-radius: 8px; background: var(--panel); box-shadow: var(--shadow)` — no elevation hierarchy between primary content and secondary metadata.

### Icons
- **No icon library**: Unicode characters only (◐, ⚙, ?, ×, ›, X)
- No SVG icon system
- Stage markers: text strings (`OK`, `NOW`, `-`)
- **Issue**: Inconsistent visual weight, alignment, and semantics

---

## 15. Visual Attention & Hierarchy Audit

| Page | Intended Primary Task | Actual Strongest Visual Element | Match? | Competing Elements |
|------|----------------------|-------------------------------|--------|-------------------|
| Planner (Conversation tab) | Write/submit analysis prompt | Global Context Bar (6-column, multiple buttons) | No | Stage rail, intent panel, capability panel, chunk list all compete |
| Planner (Results tab) | View scientific results | Selected Result Context header | Partial | 10+ panels rendered simultaneously with identical visual weight |
| Planner (Agent tab) | Monitor execution | Timeline list with left-border indicators | Yes | Provenance + health panels compete |
| Workspace | Navigate/review results | Header with title | Yes | Well-structured 3-column layout |

---

## 16. Density Audit

| Surface | Current Density | Task Match | Issue |
|---------|----------------|------------|-------|
| Global Context Bar | Very Dense | No | 6-column grid with IDs, provider info, job status — all reference-only |
| Data Context (left) | Comfortable | Yes | Appropriate for reference data |
| Conversation tab | Dense | Partial | Stage rail + prompt are good; intent/capability/dependency panels add noise |
| Results tab | Very Dense | No | 10+ panels in single scroll; no progressive disclosure |
| Agent Process tab | Comfortable | Yes | Timeline + provenance appropriate |
| Workspace | Comfortable | Yes | 3-column layout well-organized |
| Dialogs | Comfortable | Yes | 2-panel grid clear |

---

## 17. Responsive Audit

| Surface | Desktop (≥1180) | Narrow (820-1180) | Tablet (640-820) | Mobile (≤640) | Problem |
|---------|----------------|-------------------|-----------------|--------------|----------|
| Global Context Bar | 6-column grid, all items visible | Likely overflows/wraps (no explicit breakpoint) | No explicit rule | No explicit rule | **No mobile adaptation for planner context bar** |
| Data Context (left) | Resizable 240-520px | Collapsible via button | Stacks vertically | Stacks vertically | Doc specifies drawer; not implemented |
| Main Tabs | Full render | Full render | Full render | Full render | No mobile-specific tab behavior |
| Workspace header | 3-column | 2-column at ≤900 | 1-column at ≤640 | 1-column | Good |
| Workspace layout | 3-column (data+nav+main) | 2-column at ≤900 (nav+main) | Block at ≤640 + mobile drawer | Block + drawer | Good |
| Workspace buttons | 36px min-height | Same | 44px at ≤640 | 44px | Good (touch target increase) |
| Viewer canvases | aspect-ratio: 16/10, min-height: 420px | Scales | Scales | Scales | `touch-action: pan-y` set |
| Dialogs | Fixed width panels | Scales | `max-width: calc(100vw - 24px)` | Same | Reasonable |

**Critical gap**: The entire planner shell (context bar, left panel behavior, tab navigation) has NO mobile-specific breakpoints. Only the workspace route has proper mobile adaptation.

---

## 18. Accessibility Baseline

### Strengths
- Skip link to `#planner-primary-content` (and `#workspace-primary-content`)
- `aria-label` on main landmarks, navigation, resize handle, dialogs, viewer tabs
- `role="dialog"` + `aria-modal="true"` on all dialogs
- `aria-live="polite"` on dynamic panels (intent, capability, interpretation)
- Resize handle with `role="separator"`, `aria-orientation="vertical"`, `aria-valuenow/min/max`, full keyboard support
- `focus-visible` outline: 3px solid var(--color-focus-ring), offset: 2px
- `prefers-reduced-motion` media query present (reduces transitions)
- `forced-colors` media query present (high contrast mode support)
- `::selection` styled for readability
- Workspace: focus management refs exist (`inspectorCloseRef`, `contextCloseRef`, etc.)

### Severe Issues
| Issue | Location | Severity | Impact |
|-------|----------|----------|--------|
| No focus trap in dialogs | All 3 dialogs | S1 | Users can tab behind open modal |
| No Escape key handling | All 3 dialogs | S1 | Cannot keyboard-dismiss |
| No focus restoration on close | All 3 dialogs | S1 | Focus lost after dialog close |
| Backdrop click-to-close inconsistent | Dataset=`role="presentation"`, History=`onMouseDown` on target | S2 | Different interaction models |
| Timeline items not keyboard-navigable | Agent Process tab | S2 | Cannot focus individual events |
| No `aria-pressed`/`aria-selected` on chunk buttons | Conversation tab | S2 | Selection not communicated |
| 3D canvas inaccessible | All Three.js viewers | S2 | Inherent WebGL limitation |
| Planner buttons 36px (not 44px touch target) | Planner mobile | S2 | Touch targets too small |
| No `aria-invalid`/`aria-describedby` for errors | Form inputs | S3 | Error state not communicated |

---

## 19. Performance & Perceived Performance

| Issue | Type | Evidence |
|-------|------|----------|
| No loading state during initial 4 API calls | Missing feedback | `loadInitialState()` fires with no spinner/skeleton |
| PlannerWorkbench.tsx (2970 lines) as single bundle | Bundle size | No code splitting, no dynamic imports |
| Three.js + Plotly + all viewers imported at top level | Bundle size | Static imports in PlannerWorkbench lines 7-19 |
| Tab switching unmounts/remounts viewers | Heavy re-initialization | `activeTab === X ? content : null` destroys WebGL context |
| 6 parallel API calls on every poll cycle (2.5s) | Network | `refreshSnapshot` calls 6 endpoints simultaneously |
| Large JSON.stringify in render path (developer mode) | Render cost | Multiple `<pre>{JSON.stringify(x, null, 2)}</pre>` |
| No Suspense boundaries | Layout instability | All content renders synchronously |
| SSE immediately closes on any error | Premature fallback | Single `onerror` handler closes + switches to polling |

### Positive Patterns
- SSE for real-time updates (low latency when working)
- Polling fallback is transparent to user
- Snapshot refresh uses `Promise.allSettled` (partial failure tolerance)

---

## 20. Error Prevention & Recovery

| Operation | Confirmation | Undo | Retry | Preserved State |
|-----------|-------------|------|-------|----------------|
| Submit analysis | None (immediate) | No | Yes (modify + resubmit) | Prompt, dataset, provider preserved |
| Upload file | File picker | No | Yes (re-upload) | Other state unchanged |
| Load demo | None | No | Yes (retry) | Errors don't corrupt state |
| Open workspace | None | Back link only | No | Planner state lost (full navigation) |
| Generate interpretation | None | No | Yes (regenerate) | Previous interpretation replaced |
| Save workspace | None | Conflict resolution | Yes | Local draft preserved |

### Positive Patterns
- ErrorExplainer: 4-part structured error (what/why/do/preserved)
- Validation failure: explicit "no plan saved, no job created, nothing enqueued"
- Partial snapshot failure: shows which slices failed, preserves successful data
- No destructive operations exposed in the planner

### Missing Patterns
- No `beforeunload` warning for unsaved workspace changes
- No confirmation before re-submitting analysis (overwrites previous results in state)
- No undo for workspace save operations

---

## 21. Consistency Matrix

| Concept | Implementation A | Implementation B | User Impact |
|---------|-----------------|-----------------|-------------|
| Dialog close button | `×` secondary button (Dataset/Model) | `X` text icon-button (WorkspaceHistory) | Minor visual inconsistency |
| Panel heading | `PanelHeading` inline function (planner) | `.workspace-panel-header` CSS pattern (workspace) | Different visual treatment |
| Metadata display | `.mini-grid` 2-col dl/dt/dd | `.workspace-metadata-grid` auto-fit grid | Same data, different layouts |
| Empty state | `<p className="empty-state">` | Custom notice divs | Inconsistent messaging style |
| Loading indication | `dataBusy` disables buttons (no spinner) | `busy` flag shows "Loading..." text | No unified pattern |
| Status display | Inline text ("completed", "queued") | `.workspace-status` pill component | Different visual weight |
| Active/selected | `.active` class (accent background) | `.selected` class (accent border) | Different visual models |
| Button min-height | 36px (planner default) | 44px (workspace mobile) | Touch target inconsistency |
| Navigation | `<a>` for Home, `<button>` for others | All `<button>` in workspace nav | Mixed affordances |
| Accent color usage | Buttons + links + badges + nav + progress | Same everywhere | Cannot distinguish action types |

---

## 22. UX Issue Register

| ID | Surface | Issue | Category | Severity | Evidence | User Impact | Confidence |
|----|---------|-------|----------|----------|----------|-------------|------------|
| U01 | Global Context Bar | 6-column dense grid with reference data competes with primary task; no mobile breakpoint | Visual Hierarchy, Density | S1 | CSS:1785 grid definition | Users parse complex header before reaching their task | Verified |
| U02 | Results tab | 10+ panels rendered without progressive disclosure in single vertical scroll | Density, Cognitive Load | S1 | ResultsExportTab lines 1626-1681 | Cannot identify primary result without extensive scrolling | Verified |
| U03 | All dialogs | No focus trap, no Escape key, no focus restoration | Accessibility | S1 | No keydown handler, no useEffect focus management | Keyboard users cannot navigate dialogs | Verified |
| U04 | Conversation tab | Developer concepts (Intent, CapabilityGate, planId/hash) visible in non-developer mode | Cognitive Load | S1 | AnalysisIntentPanel/CapabilityPlanningPanel render unconditionally when data exists | Non-technical users face unexplained jargon | Verified |
| U05 | Initial load | No visible loading state during initial API calls | Feedback | S2 | `loadInitialState()` with no corresponding UI state | Page appears incomplete briefly | Strong evidence |
| U06 | Mobile | Planner shell has no mobile breakpoint; left panel drawer not implemented | Responsive | S2 | No @media for planner below 760px; no drawer code | Mobile users get squeezed desktop layout | Verified |
| U07 | Tab switching | Conditional render unmounts viewers, destroying 3D state | Interaction, Performance | S2 | `activeTab === X ? content : null` pattern | Camera/zoom/selection lost on switch | Verified |
| U08 | Dataset dialog | Project ID field exposed to all users | Cognitive Load | S2 | DatasetCommandDialog always shows project ID input | Non-developers see technical field | Verified |
| U09 | Conversation tab | Submit button far below prompt (after stage rail, intent, capability, chunks, plan, dependencies) | Efficiency, Discoverability | S2 | RunControls rendered last in ConversationPlanTab | Scrolling required to reach primary action | Verified |
| U10 | Navigation | Primary nav mixes page links, dialog openers, and tab switchers | IA, Consistency | S2 | GlobalPrimaryNavigation: `<a>` + dialog buttons + tab buttons | Users cannot predict click outcomes | Verified |
| U11 | Visual system | Single accent color (#08756c) for all interactive semantics | Color, Hierarchy | S2 | --color-accent used everywhere | Cannot distinguish actions from info from navigation | Verified |
| U12 | Bundle/performance | Three.js + Plotly + all viewers imported statically, no code splitting | Performance | S2 | Package.json deps + static imports | Large initial bundle | Verified |
| U13 | All panels | Identical visual weight (same border/bg/padding/shadow) for all content | Visual Hierarchy | S2 | CSS:1823-1840 shared panel styles | Important content indistinguishable from metadata | Verified |
| U14 | Typography | dt elements at 11px/900/uppercase create dense visual noise | Typography, Density | S2 | CSS:2241-2244 | Labels harder to scan than values | Verified |
| U15 | Icons | Unicode characters (◐⚙?×›) without tooltips, inconsistent weight | Discoverability | S3 | GlobalContextBar icon buttons | Sighted users must guess meanings | Verified |

---

## 23. Top 10 Highest-Impact Findings

### 1. Monolithic Component Architecture
**Current**: PlannerWorkbench.tsx is 2970 lines with ~50 useState hooks and 20+ inline sub-components. No code splitting.
**Evidence**: Full file read confirms single-file architecture.
**Why it matters**: Every state change re-evaluates entire tree; impossible to lazy-load viewers; blocks incremental redesign.
**Affected**: All planner interactions + future maintenance.
**Risk**: Any visual change risks breaking complex orchestration logic.

### 2. Results Tab Information Overload
**Current**: 10+ scientific panels render simultaneously (intelligence, explorer, composition, ML, metrics, tables, 3D, trajectory, volumetric, phonon, artifacts, tool calls, export).
**Evidence**: ResultsExportTab renders all unconditionally when artifacts exist.
**Why it matters**: Critical results buried below fold among secondary panels.
**Affected**: The core value-delivery moment — viewing analysis results.
**Risk**: Users miss important findings; perceived product quality low.

### 3. Dialog Accessibility Failures
**Current**: No focus trap, no Escape handling, no focus restoration for any dialog.
**Evidence**: No `onKeyDown` or focus management logic in dialog components.
**Why it matters**: WCAG 2.1 Level A failure; blocks keyboard-only users.
**Affected**: Dataset selection, model configuration — prerequisite steps.
**Risk**: Accessibility compliance failure; excludes users.

### 4. Global Context Bar Density & Competition
**Current**: 6-column grid showing reference data (dataset ID, model status, job ID, provider label) in the most prominent viewport position.
**Evidence**: CSS grid with 6 explicit column tracks occupying full width.
**Why it matters**: Competes with primary task area; pushes work content below fold.
**Affected**: Every interaction — always visible, always competing.
**Risk**: New users overwhelmed; attention budget wasted on reference info.

### 5. Tab Switching Destroys Viewer State
**Current**: `{activeTab === "x" ? content : null}` pattern unmounts entire tab content.
**Evidence**: MainWorkspaceTabs conditional rendering logic.
**Why it matters**: Three.js WebGL context, camera position, zoom, selection all lost.
**Affected**: Switching between execution monitoring and result viewing.
**Risk**: Users must re-orient in 3D space after every tab switch.

### 6. Missing Mobile Planner Adaptation
**Current**: No @media queries target planner shell below 760px. Doc specifies drawer for left panel at <768px — not implemented.
**Evidence**: CSS audit, no drawer code in PlannerWorkbench.
**Why it matters**: Mobile users get squeezed desktop layout; unusable on phones.
**Affected**: Entire planner on mobile/tablet.
**Risk**: Significant user segment excluded.

### 7. Developer Information Leakage
**Current**: AnalysisIntentPanel, CapabilityPlanningPanel, RunControls show planId/planHash/intentId/jobId regardless of developer mode. DatasetCommandDialog shows Project ID.
**Evidence**: Components render technical fields unconditionally when data exists.
**Why it matters**: Cognitive overhead for non-technical users; false sense of required interaction.
**Affected**: Every step of the analysis workflow.
**Risk**: Confusion; users may attempt to edit technical IDs.

### 8. No Initial Loading State
**Current**: Page renders empty panels while 4 API calls complete with no spinner/skeleton.
**Evidence**: `loadInitialState()` in useEffect with no loading gate.
**Why it matters**: App appears broken for seconds on slow connections.
**Affected**: First impression, every session start.
**Risk**: Perceived quality; users may reload.

### 9. Navigation Model Confusion
**Current**: Primary nav mixes `<a href="/">` (page link), buttons that open dialogs, and buttons that switch tabs.
**Evidence**: GlobalPrimaryNavigation renders 6 items with 3 different behavior types.
**Why it matters**: Users cannot predict what clicking a nav item does.
**Affected**: All navigation.
**Risk**: Disorientation; mental model mismatch.

### 10. Single Accent Color for All Semantics
**Current**: #08756c used for primary buttons, secondary buttons, links, active nav, badges, progress indicators, selection, and informational elements.
**Evidence**: `--color-accent` applied to all interactive + informational elements.
**Why it matters**: Cannot visually distinguish primary actions from navigation from status from info.
**Affected**: All interactions — slows task identification.
**Risk**: Reduced efficiency; users must read text to determine interactivity.

---

## 24. Must Preserve / Must Understand Before Changing

1. **SSE → polling fallback**: Resilient real-time update mechanism for job events
2. **Plan validation → execution isolation**: Security boundary (validate → persist → queue → execute). UI must never bypass.
3. **Secret/key redaction**: `redactPayload()` + backend-side filtering ensures no API keys in frontend
4. **Chunk-based result navigation**: Selecting a conversation chunk drives which results display
5. **Format-adaptive data context**: Left panel adapts to table/structure/composition/archive types
6. **Bilingual i18n (zh-CN / en-US)**: Full translation with runtime locale switching
7. **Developer mode toggle**: Controls visibility of audit JSON, raw payloads, technical IDs
8. **Keyboard-accessible resize handle**: ArrowLeft/Right/Home/End with aria-value attributes
9. **Design System 2.0 token architecture**: Primitive → semantic → component token layers
10. **Workspace persistence + conflict detection**: ETag-based optimistic concurrency with conflict UI
11. **Workspace selection contract**: URL-encodable selections for cross-panel coordination
12. **Viewer scene compatibility system**: Version-aware rendering with migration policy
13. **Stage rail progress indicator**: 5-stage pipeline visualization (effective UX pattern)
14. **Grounded interpretation with evidence lineage**: Claims linked to specific artifact field locators
15. **ErrorExplainer pattern**: Structured 4-part error recovery (what/why/do/preserved)
16. **Validation failure semantics**: Clear "nothing saved/created/enqueued" messaging
17. **Workspace panel kind/state model**: Rich state machine per workspace view

---

## 25. Unknowns & Verification Gaps

| Question | Why Unresolved | Evidence Checked | Risk if Wrong | Recommended Verification |
|----------|---------------|-----------------|---------------|-------------------------|
| Actual initial load time? | Backend not running | Source only | May not need skeleton if <500ms | Run full stack, measure with DevTools |
| Does mobile layout actually break? | No runtime test | CSS analysis only | May have CSS overflow issues | Test at 390×844 in real browser |
| Dialog focus behavior in practice? | Code inspection only | Source | Browsers may partially compensate | Keyboard test in Chrome/Firefox |
| SSE reconnection reliability? | Single onerror handler | Source | May lose events during transition | Network throttle test |
| 3D viewer performance on tab switch? | Conditional render confirmed | Source | WebGL context loss severity unknown | Runtime with actual scene data |
| Workspace conflict resolution UX? | Complex code present | First 200 lines only | May be confusing | Simulate concurrent edits |
| Actual JS bundle size? | No build artifacts | Package.json only | Tree-shaking may reduce significantly | `npm run build` + bundle analysis |
| Touch interaction with 3D viewers? | `touch-action: pan-y` found | CSS only | May not work on mobile | Test on touch device |
| Large dataset performance? | No pagination visible in profile display | Source | Left panel overflow possible | Test with 1000+ structures |

---

## 26. Reconstruction Constraints Discovered

1. **API contract stability**: Frontend depends on ~15+ REST endpoints with specific response shapes. UI changes must not require API changes.
2. **SSE event protocol**: Real-time updates depend on named server-sent event types. Must maintain SSE consumption.
3. **Workspace URL contract**: `?panel=X&selection=Y` parameters drive workspace state. Must preserve for shareability.
4. **i18n key structure**: ~150+ translation keys. Must maintain or extend (not replace) the key set.
5. **Developer mode = simple boolean**: Show/hide audit info. Not a separate app or route.
6. **Security boundary**: Frontend never stores API keys. Provider config routes through backend `/planner/providers/test`.
7. **Plan validation semantics**: UI must communicate "nothing saved/created/enqueued" on failure.
8. **Artifact type dispatch**: Renderers are selected by `artifact.type` and `artifact.name` pattern matching.
9. **Workspace ETag concurrency**: Save uses If-Match; UI must handle 409 Conflict.
10. **Scientific viewer isolation**: Three.js viewers manage own WebGL contexts; cannot share across panels.
11. **No authentication**: No auth guards exist. Future redesign should not assume auth.
12. **Route split is intentional**: Planner (/) and Workspace (/workspaces/[id]) are separate experiences with different layouts.
13. **Monolithic decomposition required first**: Any visual redesign of PlannerWorkbench requires extracting sub-components to avoid breaking 50 state hooks.
14. **Single CSS file**: All 4083 lines must be refactored alongside component extraction.

---

## 27. Phase 2 Input Package

### A. Confirmed Product Facts
- Two-route application: PlannerWorkbench (single-page analysis) + ScientificWorkspace (persistent result organization)
- Pipeline: NL prompt → intent analysis → capability planning → plan validation → execution → results → interpretation
- Bilingual (zh-CN primary, en-US secondary) with runtime switching
- Developer/User mode toggle controls audit visibility
- ~20 scientific visualization components (3D, 2D, tables, interactive)
- Design System 2.0 with well-structured CSS tokens
- No authentication in current implementation

### B. Confirmed User Journeys
1. Select/upload dataset → Profile → Prompt → Intent → Plan → Execute → Results → Interpret → Workspace
2. Open workspace → Navigate panels → Browse artifacts → Compose report → Save

### C. Confirmed State Model
- Tab-based main workspace (3 mutually exclusive tabs, conditional render)
- Chunk-selection drives results display
- SSE + polling fallback for real-time job monitoring
- Dataset + Profile + Provider as global context (in component state)
- Workspace with ETag-based persistence + conflict detection

### D. Confirmed Technical Constraints
- Next.js 15 App Router, React 19, single globals.css (4083 lines)
- No external UI component library
- Fixed backend API contract (~15 endpoints)
- Security: no secrets in frontend, no plan bypass
- Bilingual i18n with ~150+ keys per locale
- Three.js + Plotly in main bundle (no dynamic import)

### E. Highest-Impact UX Problems
1. No visual hierarchy — every panel has equal weight
2. Results tab information overload (10+ panels, no progressive disclosure)
3. Dialog accessibility failures (focus trap, Escape, restoration)
4. Global context bar density competing with primary task
5. Primary action (submit) buried below informational panels
6. No mobile planner adaptation
7. Developer information leaking into user mode

### F. Highest-Impact Visual Problems
1. Single accent color for all interactive semantics
2. 11px/900/uppercase labels creating visual noise
3. Every panel identical visual weight (border/bg/padding)
4. No icon system (Unicode characters)
5. No elevation hierarchy
6. Inconsistent spacing (tokens exist but often bypassed)

### G. Preservation Requirements
1. SSE + polling resilience pattern
2. Security boundaries (plan validation, secret redaction)
3. Format-adaptive data context display
4. Bilingual i18n support
5. Developer mode separation
6. Design System 2.0 token architecture
7. Scientific viewer data contracts
8. Workspace save/conflict model
9. Chunk-to-result linking
10. Stage rail progress indicator
11. ErrorExplainer structured error pattern
12. Grounded interpretation with evidence lineage

### H. Unresolved Questions
1. Actual runtime performance (load time, bundle size)
2. Mobile layout behavior in practice
3. Scientific viewer accessibility with screen readers
4. Full workspace route behavior (only 200 lines reviewed)
5. Large dataset performance in left panel
6. Touch interaction quality on 3D viewers
7. SSE reconnection reliability under poor network
