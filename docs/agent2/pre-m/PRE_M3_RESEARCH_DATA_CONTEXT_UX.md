# Pre-M3 Research, Data & Context Product UX

Status: `PASS_WITH_EVALUATED_ENVELOPE`  
Date: 2026-09-11

## Current defect corrected

The asking/history Research state used a fixed narrow conversation column while
an empty Workbench consumed most desktop width. The default now follows state:

```text
asking / history        → conversation-first width
scientific result open  → workbench-oriented width
manual resize           → user layout wins
```

The split remains keyboard accessible and bounded. Mobile retains one primary
pane with tab switching. Conversation and Workbench remain the two intended
desktop scroll owners; no third body/root workbench scroll is introduced.

## Context experience

Research now presents meaningful Context roles and direct-support eligibility.
Exact IDs, hashes and source references remain under advanced disclosure.
This preserves the scientist-facing path:

```text
source exists
→ selected/candidate
→ actually used
→ evidence or continuity role
→ exact provenance when requested
```

## Data and unsupported states

The existing Data product retains Dataset → Scientific Data → Analysis Results,
typed overview/empty/partial/failure states, scientific-type grouping and exact
historical source navigation. No filename dump or browser-side scientific
computation was added.

## Evidence

- Current Chromium desktop and 390×844 replay: PASS.
- Desktop: skip navigation, keyboard splitter, forced colors, reduced motion,
  no page overflow, no browser errors.
- Mobile: tab navigation, one visible pane, 44 px controls, no global
  horizontal overflow, no browser errors.
- Full frontend: `119 files / 961 tests`.

The current replay uses bounded API fixtures to isolate current layout behavior.
G's five persisted service-backed browser journeys remain the lifecycle/product
continuity evidence. Neither is presented as a formal human usability study.
