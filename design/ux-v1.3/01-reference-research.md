# Reference Research

Research was performed in a real Chrome session on 2026-08-18. The goal was pattern extraction, not visual copying. Browser evidence is retained where capture succeeded in `evidence/reference/`; inaccessible pages are disclosed rather than inferred.

## Landing: EnvForge

| Field | Observation |
| --- | --- |
| Reference / URL | EnvForge — <https://envforge.king.2bd.net/> |
| Page inspected | Public landing at desktop viewport |
| Problem it solves | Explains a complex, safety-constrained product before moving users to its private console. |
| What we borrow | An embedded, legible product work surface in the first viewport; an ordered explanation of the product flow; a clear Console transition rather than public/private navigation mixing. |
| Do not borrow | Migration-specific gates, operational metrics, repeated benefit cards, or administrative language. |
| Browser observation | Hero pairs short outcome-led copy with a real product composition; lower page makes the process order explicit. |
| Our mapping | Landing shows Data -> Research -> Result as a real workbench scene, not abstract molecular decoration. |

## Console and Project: Linear Projects

| Field | Observation |
| --- | --- |
| Reference / URL | Linear Projects — <https://linear.app/docs/projects> |
| Page inspected | Project documentation and project-details sidebar model |
| Problem it solves | A project provides a durable outcome-oriented context, with overview, properties, linked documents and a toggleable details sidebar. |
| What we borrow | Project as a durable container; list/overview transition; contextual details as a toggled secondary surface, not a permanent dashboard. |
| Do not borrow | Issue/roadmap metaphors, team administration, project status mechanics. |
| Browser observation | Linear describes Project overview plus a collapsible project details sidebar; projects can be scanned in list/board/timeline contexts. |
| Our mapping | Console resumes a Project, Project Overview shows research activity and data context, Inspector remains contextual. |

## Data: Hex Data Browser

| Field | Observation |
| --- | --- |
| Reference / URL | Hex Data Browser — <https://learn.hex.tech/docs/explore-data/data-browser> |
| Page inspected | Data Browser documentation |
| Problem it solves | Search and preview structured data from the homepage or within a project; expose schema/metadata while keeping the preview usable. |
| What we borrow | Searchable hierarchy, wide table preview, data-object deep links, metadata close to the object, explicit preview/open actions. |
| Do not borrow | Database/schema vocabulary in material-science default UX, 100-row-only limitation, or AI endorsement administration. |
| Browser observation | Hex supports browser access from Project context, table preview, metadata and object-specific search. |
| Our mapping | Project Data uses a Navigator + Viewer + contextual Inspector, with units in table headers and scientific resource types in the tree. |

## Data and Inspector: VS Code Workbench

| Field | Observation |
| --- | --- |
| Reference / URL | VS Code User Interface — <https://code.visualstudio.com/docs/editing/userinterface> |
| Page inspected | Workbench layout documentation |
| Problem it solves | Gives an editor the dominant space while explorer and secondary sidebar provide adjustable context. |
| What we borrow | Main-work-surface ownership; left explorer; secondary sidebar; adjustable split; preserved local layout; Escape-to-close overlay convention. |
| Do not borrow | Developer terminal/log panels, file-editor tabs as a scientific primary model, dense application chrome. |
| Browser observation | Documentation defines Editor, Primary Side Bar, Secondary Side Bar and Panel as distinct ownership regions; side-by-side regions are resizable. |
| Our mapping | Data Viewer and Research Workbench adopt this spatial ownership without adopting developer vocabulary. |

## Scientific data: NOMAD

| Field | Observation |
| --- | --- |
| Reference / URL | NOMAD entries — <https://nomad-lab.eu/prod/v1/gui/search/entries> |
| Page inspected | Live Explore entry search |
| Problem it solves | Filters a very large scientific inventory by material, method, workflow and property, then presents a sortable entry list. |
| What we borrow | Scientific facets, formula/method/properties as meaningful discovery fields, tabs/plots as secondary exploration modes, units as an explicit user control. |
| Do not borrow | Global repository-scale filter density, raw schema/ID prominence, or treating all data as search results. |
| Browser observation | Live page showed material, structure/symmetry, method, workflow, electronic/vibrational/mechanical property filters and a scientific table. |
| Our mapping | Scientific semantics appear in the Data Viewer and Inspector, not as Profile/Capability debug dumps. |

## Materials Project: scientific object presentation

| Field | Observation |
| --- | --- |
| Reference / URL | Materials Project documentation — <https://docs.materialsproject.org/>; material detail attempt <https://next-gen.materialsproject.org/materials/mp-2998> |
| Page inspected | Documentation landing; live material detail attempted |
| Problem it solves | Organizes precomputed material properties, methodologies, data access, and scientific applications. |
| What we borrow | Present the material/scientific object before implementation mechanics; separate method/data provenance from the primary object view. |
| Do not borrow | Public-database browsing IA or ID-first navigation. |
| Browser observation | Documentation loaded and establishes materials/properties/methodology/data access. The actual material detail page was blocked by Cloudflare verification, so visual-detail conclusions are **NOT VERIFIED**. |
| Our mapping | Structure and property viewers remain object-first; no visual inference was copied from an inaccessible live page. |

## Research: Hex Threads

| Field | Observation |
| --- | --- |
| Reference / URL | Hex Threads — <https://learn.hex.tech/docs/explore-data/threads> |
| Page inspected | Thread behavior and data-context documentation |
| Problem it solves | Lets a user ask data questions in a conversational interface while using curated semantic data context. |
| What we borrow | Conversation has durable context, return-to-recent-thread behavior, and data scope influences what the agent uses. |
| Do not borrow | Exposed hidden thinking text, raw tool-call theater, database administration or automatic multi-connection claims. |
| Browser observation | Threads use data/metadata context and show tool activity/results; the docs say tool/thinking detail collapses after response. |
| Our mapping | Research keeps question/assistant continuity on the left and maps only trustworthy scientific activity to the right; chain of thought is never surfaced. |

## Running: GitHub Actions

| Field | Observation |
| --- | --- |
| Reference / URL | VS Code public workflow runs — <https://github.com/microsoft/vscode/actions> and a live workflow-run detail |
| Page inspected | Workflow list and run detail |
| Problem it solves | Makes status and discrete work units scannable across a long asynchronous process. |
| What we borrow | Ordered step state, current work identification, completed/failed distinction, preserved results after a failed later step. |
| Do not borrow | Developer logs, job matrix detail, branch/commit focus, timings as false scientific progress. |
| Browser observation | Live run list exposes workflow/status/duration; run detail organizes named jobs and steps. |
| Our mapping | Activity panel has concrete scientific stages, never a percentage or a terminal log. |

## Result: scientific publication structure

| Field | Observation |
| --- | --- |
| Reference / URL | eLife figures and data — <https://elifesciences.org/articles/83867/figures> |
| Page inspected | Live figures/data page |
| Problem it solves | Makes figures individually readable through title, caption, supplementary material and downloadable data. |
| What we borrow | Figure-first hierarchy, caption as interpretation guardrail, visible scope, supporting outputs separate from the main figure. |
| Do not borrow | Journal metadata bulk, long-form publication chrome, disease-specific content. |
| Browser observation | Page presented numbered figures, descriptive captions, supplements and additional files as separate evidence strata. |
| Our mapping | Result uses Figure + caption + finding + limitation + supporting output + method/evidence rather than metric cards. |

## Reference synthesis

The shared pattern is spatial and epistemic discipline: put the substantive object in the large region; make context adjustable; give progress a named, observable stage; reveal deeper lineage on demand. The prototype borrows no brand palette, card grammar, public IA, or raw tool-output behavior from these products.

## UX-V1.3.1 targeted closure application

No new product direction was introduced during closure. The following already-inspected references were deliberately reapplied only to the unresolved surfaces:

| Closure surface | Reference re-applied | Specific pattern retained | Explicit non-copy |
| --- | --- | --- | --- |
| Landing login | EnvForge public/private boundary; Linear Project context | A public entry has one clear transition into the private product; login is a short modal task rather than a feature panel. | EnvForge operational/migration language and Linear brand styling. |
| Console continuation and Quick Preview | Linear Project context; VS Code Workbench | Continue work before collection browsing; an object can temporarily receive a large secondary work surface while the originating page remains contextual. | A permanent developer sidebar, file-tab model, or a 400px “details” drawer. |
| Completed research | GitHub Actions step-state model; eLife Figure reading order | A completed process becomes supporting history while the resulting scientific Figure takes reading priority. | Developer logs, duration theatre, commit context, or collapsed evidence that hides limitations. |
| Report reader | eLife figure/caption hierarchy | Reading controls stay quiet; figure, caption, finding and limitation own the document. | Journal metadata bulk or a dashboard treatment. |

The current Chrome session could not complete fresh external-page navigation, so this closure section makes no new visual-reference claim beyond the recorded UX-V1.3 research above.
