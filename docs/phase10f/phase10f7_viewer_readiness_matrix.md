# Phase 10F-7 Viewer Readiness Matrix

| Readiness Area | Current Status | Gap | Risk | Required Before Implementation | Decision |
|---|---|---|---|---|---|
| artifact contract | Phase 10D has inert static scene metadata | Future viewer-facing schema not finalized | low | Finalize `viewer_scene.json`, summary, recipe, params, limits, warnings, and security fields | READY for next contract phase |
| scene normalization | Existing parser and Phase 10D metadata provide lattice/site serialization | vNext coordinate precision and style policy need finalization | low | Fixed rounding, ordering, color/radius policy, and invalid-geometry behavior | PARTIAL_READY |
| bond inference | Existing metadata can carry bonds, but advanced inference is not in scope | Safe helper policy and caps need finalization | medium | Optional bonds only or approved bounded helper | PARTIAL_READY |
| renderer choice | No renderer approved for this phase | WebGL/Three.js/canvas/server image path not selected | high | Separate renderer architecture approval and dependency review | NOT_READY |
| frontend integration | Static artifact preview exists | Interactive viewer UI not designed or evidenced | high | Static JSON evidence first; renderer UI later | PARTIAL_READY |
| WebGL / Three.js dependency review | No new dependency approved | Supply-chain, bundle, CI, and browser security review missing | high | Explicit approval and tests | NOT_READY |
| sandboxing | General artifact security exists | Renderer-specific sandbox boundary missing | high | Iframe/sandbox or equivalent isolation design if renderer is approved | NOT_READY |
| security tests | No-JS/no-external-URL scans exist | Renderer-specific malicious-scene tests missing | high | Add no-script, no-external, malformed-scene, oversized-scene tests | PARTIAL_READY |
| browser evidence | Real browser evidence pattern exists | Viewer JSON-only vs renderer evidence split must be formalized | medium | Phase-specific screenshot and console/network audit protocol | PARTIAL_READY |
| planner routing | Static physics negative routing exists | Viewer positive/negative routing not implemented | medium | Add routing tests in a future implementation phase | PARTIAL_READY |
| performance caps | Proposed caps defined in Phase 10F-7 | Not enforced in a viewer contract | medium | Enforce site, bond, species, expansion, and JSON-byte caps | PARTIAL_READY |
| CI stability | Static physics and fixture replay CI are green | Renderer browser tests may increase flake risk | medium | Keep Phase 10F-8 contract-only; add renderer tests only after approval | READY for contract phase |
| fixture pack | Static physics fixture pack exists | Viewer fixture pack not created | medium | Add small viewer-scene fixtures later if contract is approved | PARTIAL_READY |
| official examples | Official static physics PASS remains none | Viewer official cases not verified | medium | Do not claim official PASS without eligible provenance and direct replay | PARTIAL_READY |
| phonon separation | Phonon is consistently deferred | Future routing must keep phonon separate | medium | Negative routing and docs boundary | READY for planning |
| Brillouin zone separation | Brillouin-zone 3D is consistently deferred | Future routing must keep it separate | medium | Separate readiness plan before implementation | READY for planning |

## Final Decisions

- viewer_scene artifact contract readiness: READY for next planning/contract phase.
- renderer implementation readiness: NOT_READY.
- full `structure.viewer_3d` implementation readiness: NOT_READY.
