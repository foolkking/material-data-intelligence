# UI Layout System V2 Requirements

**Previous freeze:** `FROZEN_BASELINE_V1`
**Current:** `FROZEN_BASELINE_V2`
**Amendment date:** 2026-09-06
**Freeze status:** `ARCHITECTURE_FREEZE_AMENDED_PENDING_BASELINE_COMMIT`
**Scope:** requirements only; no CSS/component implementation.

V2 preserves UX and scientific semantics, not the present pixel geometry. Current 36%, 420px, 320–640px, 7px, 264px, 344px, breakpoint and shell values are `CURRENT_BASELINE` evidence only.

## Required Archetypes

| Archetype | Required ownership model |
|---|---|
| `DOCUMENT` | readable content measure; document scroll; local overflow only for declared wide artifacts |
| `DIRECTORY/LIST` | list/table main region; explicit loading/empty/error; predictable pagination/filter state |
| `DATA_WORKBENCH` | dataset/object/version context; main scientific surface; optional inspector |
| `RESEARCH_WORKBENCH` | Conversation and Workbench contexts with state-dependent priority |
| `SCIENTIFIC_VIEWER` | minimum usable scientific surface, viewer controls and specialized loading/error |
| `ADMIN/SETTINGS` | settings navigation, form/document content and recovery semantics |

A route chooses an archetype explicitly. Shared shell/layout must not absorb feature behavior.

## Global Requirements

- Global context and project/context navigation remain semantically distinct.
- Each archetype declares root, document, rail, main, inspector and viewer scroll owners.
- Sticky elements declare their containing scroll context.
- No accidental nested page scrolling or zoom-created third scroll owner.
- Responsive behavior accounts for viewport, content minimums and product state.
- `NO_HORIZONTAL_OVERFLOW` and `GOOD_READABILITY` are separate acceptance results.
- Fixed pixels are acceptable for controls/icons/separators where justified; layout-coupled constants require ownership/tokens.
- Narrow/compact modes preserve route, selection, focus and recovery context.

## Research State Responsiveness

Research must allow different space priorities without freezing ratios:

| State family | Priority requirement |
|---|---|
| `ASKING/HISTORY` | readable conversation/history and composer access |
| `PLANNING/RUNNING` | conversation intent plus visible structured progress/workbench state |
| `RESULT/VIEWER` | usable scientific result surface while Conversation remains reachable |
| `EMPTY/LOADING/FAILURE` | clear next action, ownership and recovery without fake workspace content |

Requirements:

- Conversation and Scientific Workbench remain complete, accessible contexts on desktop and narrow modes.
- Bounded DOM history and earlier/newer/location capabilities remain; unbounded timeline rendering is forbidden.
- Pane switching preserves needed reading position, focus and session/turn/result identity.
- Splitter, if retained, remains keyboard/focus accessible, but exact width/range/default is not frozen.
- Independent pane scrolling may remain or be replaced; either model must explicitly define root/document policy and sticky composer/header behavior.
- Transport payload boundedness is evaluated separately from DOM boundedness.

## Data Content-State Responsiveness

Data may allocate space differently for:

- `EMPTY`
- `IMPORTING`
- `IMPORT_FAILURE`
- `OBJECT_SELECTION`
- `VERSION_SELECTION`
- `VIEWER_ACTIVE`
- `VIEWER_LOADING/FAILURE`

Requirements:

- Navigator context remains accessible but need not be permanently visible or retain 264px.
- Inspector remains an optional capability and need not permanently occupy 344px.
- Empty/importing states use available space appropriately and do not imply a loaded viewer.
- Exact immutable version selection and fail-closed behavior are preserved through collapse/drawer/compact transitions.
- Table, structure, trajectory, phonon, electronic and volumetric viewers may define different internal overflow and minimum-width policies.
- Small/medium desktop behavior considers scientific content minimums, not viewport width alone.

## Scientific Viewer Surface

- Each viewer family declares minimum usable width/height and a narrower-container fallback.
- Viewer engines, dynamic imports and web-worker source relationships remain functional.
- Controls and scientific content remain keyboard reachable and are not obscured at zoom.
- A layout change cannot alter scientific data authority or silently substitute a different object/version/result.

## Reports, Lists and Settings

- Reports use a readable document measure; explicitly wide tables/figures own local overflow.
- Lists do not inherit workbench splitters without feature evidence.
- Settings/admin layouts preserve validation, permission and recovery states.
- Artifact presentation remains feature/report-owned unless proven generic.

## Responsive and Zoom Verification

Future approved implementation must verify at least 390×844, approximately 768, approximately 1024, 1280×720, 1440×900, 1920×1080 and 125%/150%/200% zoom. Verification covers:

- horizontal overflow and readability separately;
- focus order and visible focus;
- scroll owner count and sticky containment;
- route/query/selection restoration;
- empty/loading/error/running/result states;
- scientific minimum usable surface;
- bounded history DOM.

Historical screenshots are context, not current PASS. This freeze launches no screenshot campaign.

## CSS Reality Baseline

The current `globals.css` is a large coupled stylesheet (statically observed: 98 variables, 53 media-query occurrences, extensive fixed-pixel/grid/flex rules). V2 implementation must first assign feature/layout ownership. It must not mechanically replace all pixel values or extract code merely because it is duplicated.

## Non-Goals

No final CSS, ratio, breakpoint, token value, component implementation, container-query mandate, or universal page template is defined here.
