# Global Shell and Navigation

## Hierarchy

```text
Public: Landing -> Login
Private: Console -> Projects -> Project
                                 |- Overview
                                 |- Data
                                 |- Research
                                 `- Reports
```

`Workspace` is absent from primary navigation. Internally it remains the existing single-run projection/layout/selection/report context; future production UI maps it to Run, Result, Inspector, and Report.

## Global bar

- 56px high, white surface, one bottom hairline.
- Left: brand only. Center: current Project context when inside a Project. Right: global search and account when signed in; **登录** on logged-out Landing.
- It does not become a permanent global menu or a surface for provider, health, environment, Profile, Dataset or job diagnostics.
- It contains no context-specific action. Data preview, upload, research-scope and report actions belong to their owned page/workbench.

## Local Project navigation

- 44px high, 4 links: Overview, Data, Research, Reports.
- Project selection happens in Console/Projects, not a cluttered third vertical nav.
- Active state is text-weight plus an underline; a tab does not look like a pill or badge.

## Page structures

| Page | Scroll owner | Primary focus | Secondary context |
| --- | --- | --- | --- |
| Landing | Browser | Research workbench scene and outcome | Workflow below fold |
| Console | Browser | Continue research / recent Projects | modest project facts |
| Projects | Browser | Project list | archive link |
| Project Overview | Browser | research progress | Project data inventory |
| Data | fixed workbench | selected scientific object | Navigator + Inspector |
| Research | fixed workbench | current work/result | Conversation + Activity |
| Reports | Browser | Run Report list | Project association |
| Report Reader | Browser | Figure/document | source/process at end |

## Quick Preview

Data links in Console, Project Overview, and Research may invoke a `~68vw` right-side Quick Preview. The original page stays present but is occluded/visually subordinate; this is intentional inspection, not a cramped 400px drawer. It has dialog semantics, Escape close, and focus restoration. It is unavailable inside the formal Data Viewer, preventing Preview -> Preview nesting.
