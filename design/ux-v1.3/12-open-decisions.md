# Open Decisions

## Frozen design decisions

The following have enough UX-V1.3 and UX-V1.3.1 prototype evidence to be the production-design baseline, subject to implementation accessibility acceptance:

| Decision | Frozen value |
| --- | --- |
| Mineral Green | `#0B6B57`, scarce accent only |
| Font stack | IBM Plex Sans + Noto Sans SC + Microsoft YaHei fallback |
| Conversation width | 36%, keyboard/pointer adjustable between 30-45% |
| Data Navigator | 264px wide desktop; 236px tighter desktop |
| Inspector | 344px wide desktop; 320px tighter desktop |
| Quick Preview | 68vw large right-side scientific viewer |
| Landing | outcome-led two-column workbench scene with visible next workflow band |
| Activity | 224px Running rail; Complete collapses to a full-width compact summary |
| Table density | 40px default header/row; 42px only for an explicit comfortable mode |
| Product chrome | Simplified Chinese; canonical scientific/source identifiers retained where appropriate |

## Still requiring Product or engineering decision

| Decision | Why unresolved | Required next owner |
| --- | --- | --- |
| Authentication mechanism | The modal intentionally shows only email/password form geometry; actual email/password, SSO, or another method is not frozen. | Product + authentication/backend owner |
| Final visual recapture | Chrome screenshot permission and viewport override failed in this closure run. | Design QA environment owner, before production UI acceptance |
| Production font delivery | Stack is frozen; loading, fallback metrics, licensing and FOUT behavior remain implementation verification. | Frontend owner |

## Decisions that are not open

- Project is the main user-facing research boundary.
- Workspace is hidden terminology in normal IA but retained internally.
- Data Viewer, not dashboard cards, owns Data.
- Conversation and current work coexist on desktop.
- Running uses actual named facts, never fake percentage or fake streaming.
- Incremental artifact appearance is part of the target interaction.
- Results use Figure/Finding/Limitation/Evidence hierarchy.
- Current Reports are Run Reports, not fictional Project aggregate reports.
