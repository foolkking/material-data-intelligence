# Context and Frozen Decisions

## Purpose and boundary

UX-V1.3 converts the completed code-reality audit, product model, UX-V1.1 visual direction, and UX-V1.2 page/component specification into buildable design documentation and an isolated high-fidelity prototype. It does **not** change production UI or backend behavior.

## Current code facts used by this design

| Fact | Status | Design consequence |
| --- | --- | --- |
| Project is a persistent research boundary | EXISTS_IN_CODE | Project is the primary user-facing context. |
| Dataset + DataProfile is the current execution root | EXISTS_IN_CODE | Every executable analysis must expose/resolve a valid Dataset scope even when UI says “this Project”. |
| A Dataset may contain multiple files/resources | EXISTS_IN_CODE | Data Navigator can show a coherent Project inventory and detected resources. |
| Cross-Dataset Project analysis is unavailable | REQUIRES_NEW_BACKEND_CAPABILITY | Prototype Project-wide scope is target UX only; it must not claim runtime support. |
| Workspace is a run-internal result/layout/selection/report projection | EXISTS_IN_CODE | Hide the term in normal IA; preserve backend identity and capabilities. |
| Conversation is not a fully business-persistent model | REQUIRES_NEW_BACKEND_CAPABILITY | Prototype conversation continuity is a product target, not present backend fact. |
| AnalysisPlan is a validated safety/execution contract | EXISTS_IN_CODE | Production keeps it; UI presents a human-readable scientific plan. |
| Job/tool/artifact events exist; SSE is not a trusted continuous stream | PARTIAL | Running UX maps only discrete facts and never fabricated progress. |
| Artifact can persist before terminal job completion | EXISTS_IN_CODE | Incremental result composition is feasible with frontend adaptation. |
| Interpretation has an explicit terminal lifecycle | EXISTS_IN_CODE | Do not portray “interpretation” as an assured in-job streaming step. |
| Report is naturally a Run Report | EXISTS_IN_CODE | Prototype Reports collection stays run-scoped. |

Evidence sources: current architecture audit, `docs/phase12/evidence/phase12_0_current_ux_reality/route_inventory.json`, `scientific_viewer_matrix.json`, and the current frontend baseline recorded in `evidence/baseline/`.

## Frozen product model

```text
Landing -> Login -> Console -> Project
                              |- Overview
                              |- Data
                              |- Research
                              `- Reports (Run Reports)
```

The user mental model is `Project -> Data -> Research -> Run / Result`. Workspace is hidden terminology, not deleted architecture.

## Frozen visual model

`Scientific Instrument + Scientific Data Workspace + Scientific Publication`.

The evidence spine is the recurring interaction signature:

```text
Data scope -> human-readable method -> artifact / figure -> finding -> limitation -> evidence -> source & process
```

## Explicit non-goals

- No persistent conversation backend, Project catalog resolver, cross-Dataset execution, true stream transport, Project aggregate report, archive-tree backend, XLSX parser, production auth, or production UI refactor.
- No raw internal IDs, infrastructure health panels, fake live logs, fake percentage completion, or generic card dashboard in normal UX.
