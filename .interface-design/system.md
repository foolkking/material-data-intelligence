# Material Agent Platform Design System

**Authority:** This file is authoritative for future production UI work. It records the frozen UX-V1.3 visual system for the Material Agent Platform. Production implementation may refine a token only when the change is documented and reviewed against this system and the associated UX-V1.3 evidence.

## Product Visual Identity

**Scientific Research Workbench** combines three deliberately restrained languages:

1. **Scientific instrument:** precise controls, measured contrast, visible units, reliable state.
2. **Scientific data workspace:** one dominant work surface with data context and a contextual Inspector at its edges.
3. **Scientific publication:** results are read as Figure, caption, finding, limitation, evidence, then source/process.

The product is neither a generic AI chat application nor a KPI dashboard. A Project is a durable research context. `Workspace`, plans, jobs, queues, providers, IDs, and registry contracts remain implementation concepts unless a progressive technical disclosure explicitly needs them.

## Focal Point Rules

- Every view has exactly one primary focal point.
- Data views prioritize the scientific object or table; navigation and metadata cannot compete with it.
- Research shows the conversation and current work together on desktop. The right workbench owns the result and running state; the left pane owns the question and continuity.
- Result views prioritize the Figure. Finding and limitation follow it in reading order.
- Error, empty, clarification, and unsupported states lead with the scientific consequence and available next actions, never an internal lifecycle failure.
- A card is a bounded repeated item, modal, or framed tool only. Page sections are bands, columns, documents, or workbench regions, not floating card collections.

## Typography

**Preferred stack:** `IBM Plex Sans`, `Noto Sans SC`, `Microsoft YaHei`, sans-serif. Load the first two where licensing/performance permits; retain the CJK fallback for Windows.

| Role | Size / line height | Weight | Usage |
| --- | --- | --- | --- |
| Landing title | 42-64 / 1.06 | 600 | Product statement only |
| Page title | 28 / 1.25 | 600 | Console and Project pages |
| Result/report title | 28-36 / 1.18 | 600 | Scientific document lead |
| View title | 20 / 1.35 | 600 | Viewer and workbench heading |
| Section title | 16-17 / 1.45 | 600 | Local hierarchy |
| Body | 15-16 / 1.55-1.75 | 400 | Research prose and explanations |
| Utility | 13 / 1.5 | 400-500 | Metadata and controls |
| Technical disclosure | 13 / 1.45 | 400 | Only progressive disclosure |

No default body text below 13px. Letter spacing is normal (never negative in small utility labels); all-caps may use 0.06-0.08em only for compact section eyebrows.

## Language Policy

`PRODUCT_CHROME_LANGUAGE = zh-CN`. Navigation, actions, states, dialogs, toolbar labels, Inspector, report controls, empty states, and system-facing copy use Simplified Chinese by default.

- Preserve canonical/source language for user-created file, dataset, and Project names; material formulas; scientific symbols; units; and appropriate source property names, such as `BaTiO3`, `DOS`, `XRD`, `eV`, `Å`, and `formation_energy`.
- Where a mature Chinese research term improves comprehension, use Chinese explanation with the canonical name when useful: `形成能（formation energy）`, `带隙（band gap）`.
- English technical contracts, IDs, schema/version data, and tool lineage belong only in progressive disclosure such as **技术详情** or **来源与过程**. They are not default UI chrome.

## Color

| Token | Value | Role |
| --- | --- | --- |
| Canvas | `#F5F7F6` | App background / quiet contextual region |
| Surface | `#FFFFFF` | Main readable work surface |
| Surface subtle | `#EFF2F0` | Toolbar, selected-neutral, quiet panels |
| Border | `#D9DFDC` | Default division |
| Border strong | `#AEB9B3` | Durable boundaries / current context |
| Text primary | `#18211D` | Primary reading text |
| Text secondary | `#59655F` | Supporting explanation |
| Text tertiary | `#78837D` | Utility metadata |
| Mineral Green | `#0B6B57` | Primary action, selection, active research, scientific highlight |
| Mineral soft | `#E3F0EC` | Restrained selected context only |
| Warning | `#8A5B0D` | Constraint, limitation, unsupported condition |
| Danger | `#A64034` | Failed scientific step / destructive outcome |
| Information | `#315E78` | Neutral technical or data context |

Mineral Green is scarce. It must not become a page wash, decorative gradient, or dashboard theme. Status has text and an icon/shape in addition to color.

## Geometry, Density, and Surfaces

- Spacing scale: `4, 8, 12, 16, 24, 32, 48, 64`.
- Radius: control `4px`; input `6px`; panel `8px`; overlays `<=10px`.
- Content has no shadow. Only popovers, drawers, modals, and floating prototype controls may use a shadow.
- Use one-pixel borders to show ownership, not a border around every text block.
- Desktop shell: GlobalBar `56px`; ProjectNav `44px`.
- Data Navigator seed `264px` (reduce to `236px` at tighter desktop); Inspector seed `344px` (reduce to `320px` at tighter desktop); Research activity seed `224px`.
- Research desktop split: Conversation default `420px`, keyboard/pointer adjustable
  from `320px` to `640px`; Workbench retains at least `480px`. The bounded
  pixel model keeps the composer and result readable across ordinary desktop
  widths and matches the production splitter semantics.
- Report reader: `820-900px` readable measure.
- Quick Preview: `~68vw`, not a 400px drawer.
- Default scientific table/header row height is `40px`; this keeps 13px data and 12px unit labels readable without turning data browsing into a comfortable-form layout. `42px` is reserved for an explicitly selected comfortable density mode.

## Navigation and Controls

- Global navigation is a 56px context bar, not a permanent 220px sidebar.
- A Project uses a 44px local nav: Overview, Data, Research, Reports.
- Do not put `Workspace` in primary user navigation or expose raw internal IDs by default.
- Use icon-only buttons only for familiar operations and always give them an accessible name/tooltip.
- Primary actions use Mineral Green. Secondary commands are outlined; passive controls are quiet.
- Search, filters, columns, and sort belong adjacent to the data they affect. Do not hide core table work behind generic command menus.
- GlobalBar contains global context, search, and identity only. Data, Research, and Reports commands live with the page/workbench that owns their state. A Data Viewer does not offer a nested “preview.”

### Object Management

- Project and Dataset rows remain navigation-first. Management is available from one shared action menu, not a permanent row of buttons.
- Desktop right-click is an accelerator, never the only path. The identical menu is reachable from a familiar `More` trigger, `Shift+F10`/the keyboard context-menu key, and a persistent touch target on coarse-pointer devices.
- The `More` trigger may stay visually quiet until row hover or keyboard focus on pointer-precise desktop. It remains in the tab order and always has an accessible name.
- Multi-object operations use an explicit selection mode. Entering selection mode replaces row navigation with checkboxes and introduces one transient batch toolbar; leaving it restores normal navigation.
- Destructive lifecycle is asymmetric: non-empty scientific Projects, Datasets, Runs, Artifacts, Evidence, and Reports are archived or otherwise hidden reversibly. Physical deletion is offered only for an owner-controlled object proven empty by the server and requires typed-name confirmation.
- Read-only members retain navigation and scientific viewing. Upload, rename, archive, restore, delete, and batch-selection controls are omitted unless the server projects an explicit write-capable role.
- Management dialogs use a maximum `640px` reading width, one clear title, concise consequences, focus containment, Escape dismissal, and focus restoration. On mobile, menus become bottom-sheet-like surfaces and dialog actions become full-width targets.

## Data and Workbenches

- Scientific data owns the largest region of the Data page.
- Navigator is a scroll-contained source/context list; Viewer has its own surface and scrolling; Inspector is selection-driven and independently scrollable.
- A table is a scientific object: stable headers, units with properties, row selection, column/row scanning, and explicit horizontal scrolling when necessary.
- Structure, trajectory, XRD, electronic, volumetric, archive, and generic file states must use different appropriate viewer compositions. Do not force all of them into cards.
- Archive UI may show **detected content** only when that is what the runtime can prove. Do not invent a file tree or multi-resource capability.
- On desktop, close/hide contextual panes before reducing the primary viewer below a usable scientific reading size.

## Result and Evidence Rules

The canonical result ordering is:

`Title -> data/sample context -> Figure -> caption with units -> Key Finding -> Limitation -> supporting outputs -> method -> evidence/source/process`.

- A Figure is never a decorative chart. It has a caption, named scientific variables, units, scope, and a limitation if interpretation is bounded.
- Finding language distinguishes observed relationship, interpretation, and unsupported inference.
- Evidence is reachable from a selected row, plot point, structure site, or XRD peak through Inspector.
- Inspector tabs/sections use: **Details**, **Evidence**, **Source & process**. Deep lineage is progressive disclosure.
- Report is a Run Report under current backend reality, not a fabricated aggregate Project Report.

## States and Motion

- Running uses real discrete facts: data selected, plan prepared, data loaded, a specific scientific operation active, artifact available, result interpretation available after terminal lifecycle.
- Never show invented percentages, "almost done," token-stream mimicry, or fake real-time logs.
- Incremental artifacts appear only after the corresponding tool/artifact event exists. The user can read the artifact while a later real step remains active.
- **Running** is process plus emerging result: Activity stays visible beside live scientific output. **Complete** is result-first: collapse the completed activity to a compact summary and reveal full history on demand. **Partial** and **Failed** keep process more visible because completed, failed, and remaining work must be understood together.
- `Unsupported`: say which scientific requirement is absent, list available properties, offer supported alternatives, and tuck technical detail behind a disclosure.
- `Clarification`: ask the smallest question that changes scientific scope.
- `Partial`: retain and label completed outputs; explain the incomplete scientific portion.
- `Failed`: preserve inputs and completed artifacts; offer scoped recovery.
- Motion is reserved for a subtle active-step indicator and overlays. Transitions are 120-180ms, with `prefers-reduced-motion` disabling nonessential animation.

## Accessibility

- All information needed to understand a state is textual and not color-only.
- Keyboard sequence follows visual reading order. The splitter is keyboard adjustable. Escape closes Inspector/preview and focus returns to the triggering control.
- A visible focus ring uses a high-contrast green outline with an offset.
- At 200% zoom, no essential control is clipped; workbench panes may reflow but must preserve access to the active object.
- Mobile text inputs use at least 16px to avoid browser zoom. Target size is at least 36px for desktop controls and comfortable on touch surfaces.
- Fixed workbench regions have deliberate scroll ownership. Browser scroll is used for Landing, Console, Overview, and Report; individual regions scroll in Data and Research.

## Anti-Slop Rules

Do:

- Use real material labels, formulas, units, samples, and scientific limitations in examples.
- Make the active scientific question and current object legible at a glance.
- Use whitespace to separate ownership regions, not decorative cards.
- Show one trustworthy status path instead of a general infrastructure health surface.

Do not:

- Use generic AI gradients, glassmorphism, purple AI palettes, molecule decoration, bento dashboards, huge radii, or shadow-based section cards.
- Expose Profile IDs, Dataset IDs, Plan IDs, Job IDs, Tool IDs, Queue/Worker/Provider details, or workspace terminology in default research flow.
- Put every section inside a card; use meaningless badges; reduce body copy to 11-12px; make every viewer look identical.
- Treat a spinner as evidence of a real event; substitute fake percentage progress for runtime facts; fabricate archive trees or empty result modules.
