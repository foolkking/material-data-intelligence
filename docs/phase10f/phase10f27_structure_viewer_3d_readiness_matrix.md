# Phase 10F-27 structure.viewer_3d Readiness Matrix

| Capability | Decision |
| --- | --- |
| unique formal tool identity | READY |
| platform registry ownership | READY |
| strict input/output contract | READY |
| planner routing and negative routing | READY |
| PlanValidator/runtime/adapter | READY |
| canonical scene v2 and manifest v2 | READY |
| live API/job/artifact evidence | READY |
| production renderer and JSON fallback | READY |
| Chromium/Firefox/WebKit/mobile | READY |
| accessibility/lifecycle/performance | READY |
| network and artifact security | READY |
| legacy compatibility | READY |
| full `structure.viewer_3d` product within documented scope | READY |
| trajectory | NOT_READY |
| phonon | NOT_READY |
| Brillouin zone | NOT_READY |
| volumetric rendering | NOT_READY |
| structure editing | NOT_READY |

Formal product readiness does not convert visual distance-cutoff topology into
authoritative chemistry and does not authorize advanced scientific domains.

Local closure: 104 frontend tests passed; 370 backend tests passed with 21
explicitly skipped and 11 existing library warnings; typecheck, production
build, lock check, the formal product runner, and all historical viewer runners
passed. Local service-backed execution was unavailable because Docker is not
installed; current-HEAD CI is the required service-backed and zero-skip gate.
