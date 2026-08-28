# Phase 14-R Mature Product Coverage Matrix

This matrix is intentionally truthful. `PASS` requires current code,
same-stack service evidence and authenticated browser evidence; `PARTIAL`
means a bounded implementation exists but one or more acceptance dimensions
remain open.

| Area | User entry | Authority | Desktop | Mobile | Browser | Service-backed | Historical | Security | Performance | Provenance | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Authentication/projects | Home/project shell | project authorization | PASS | PARTIAL | PASS (Phase 14) | PASS | N/A | PASS | PARTIAL | PASS | PARTIAL |
| Data/version lifecycle | Data Platform | ScientificObject/Version | PASS | PARTIAL | PASS (Phase 12/14) | PASS | PASS | PASS | PARTIAL | PASS | PARTIAL |
| Dataset query/handoff | Materials Explorer | exact Dataset version/sample | PASS | PARTIAL | PASS (Phase 12/14) | PASS | PASS | PASS | PARTIAL | PASS | PARTIAL |
| Research execution | Research composer | Turn/Plan/Job/Result | PASS | PARTIAL | PASS (Phase 14) | PASS | PASS | PASS | PARTIAL | PASS | PARTIAL |
| Presentation/Viewers | Workbench/Result | ScientificResult | PASS | PARTIAL | PARTIAL | PARTIAL | PARTIAL | PARTIAL | PARTIAL | PARTIAL | PARTIAL |
| Evidence | Finding disclosure | Result/Artifact/version | PARTIAL | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | PARTIAL | PARTIAL | NOT_QUALIFIED | PARTIAL | PARTIAL |
| Reports | Reports/Workbench | immutable snapshot | PASS | PARTIAL | PARTIAL | PARTIAL | PARTIAL | PARTIAL | NOT_QUALIFIED | PASS | PARTIAL |
| History/resume | Project history | explicit ResearchTurn relation | PASS | PARTIAL | PASS (Phase 14) | PASS | PASS | PASS | PARTIAL | PASS | PARTIAL |
| Archive/restore | object actions | lifecycle service | PASS | PARTIAL | PASS (Phase 12/14) | PASS | PASS | PASS | PARTIAL | PASS | PARTIAL |
| Result reuse | follow-up Research | exact reusable Result | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | PARTIAL | PASS | NOT_QUALIFIED | PARTIAL | NOT_QUALIFIED |
| Context transparency | Research context | ContextSnapshot/ContextManifest/memory | PASS | PARTIAL | PASS (authorized manifest endpoint + disclosure) | PASS (focused API tests) | PARTIAL | PASS | PARTIAL | PASS | PARTIAL |
| Lifecycle management | project/data/report actions | lifecycle contract | PARTIAL | NOT_QUALIFIED | PARTIAL | PARTIAL | PARTIAL | PARTIAL | NOT_QUALIFIED | PARTIAL | NOT_QUALIFIED |
| Search/organization | global search | authorized read models | PARTIAL | NOT_QUALIFIED | PARTIAL | NOT_QUALIFIED | PARTIAL | PARTIAL | NOT_QUALIFIED | PARTIAL | PARTIAL |
| Task/recovery | task center/reconnect | persisted Job/queue state | PARTIAL | NOT_QUALIFIED | NOT_QUALIFIED | PARTIAL | PARTIAL | PASS | NOT_QUALIFIED | PARTIAL | NOT_QUALIFIED |
| Retention/export | trash/export | retention policy | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | NOT_QUALIFIED | PARTIAL | PARTIAL | NOT_QUALIFIED | PARTIAL | NOT_QUALIFIED |
| Evaluation/operations | internal qualification | test/ops evidence | PARTIAL | N/A | NOT_QUALIFIED | PARTIAL | N/A | PARTIAL | NOT_QUALIFIED | PASS | NOT_QUALIFIED |
