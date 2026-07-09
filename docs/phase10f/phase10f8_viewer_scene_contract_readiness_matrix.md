# Phase 10F-8 Viewer Scene Contract Readiness Matrix

| Readiness Area | Current Status | Gap | Risk | Required Before Implementation | Decision |
|---|---|---|---|---|---|
| artifact identity readiness | `viewer_scene`, `viewer_scene.v1`, and `phase10f8.viewer_scene.v1` are planned | Implementation schema not created | low | Final schema and tests in a later phase | READY |
| JSON shape readiness | Required top-level fields are planned | Exact JSON Schema not implemented | low | Schema file and fixture validation | READY |
| manifest contract readiness | Manifest identity and renderer-absent fields are planned | Compatibility bridge to Phase 10D `viewer_assets_manifest.json` not implemented | low | Schema and compatibility tests | READY |
| validation contract readiness | Caps and rejection/warning policy are planned | Validator code not implemented | medium | Typed validation errors/warnings and fixture tests | READY |
| security boundary readiness | No-JS/no-URL/no-renderer-required boundary is fixed | Malicious artifact tests not implemented | medium | Security tests before implementation | READY |
| browser JSON-only preview readiness | Existing Phase 10D static preview supports scene/manifest display | Phase 10F-9 contract fixture evidence not captured | low | JSON-only evidence screenshots/audit | READY |
| renderer handoff readiness | Data-only handoff boundary is planned | Renderer sandbox, dependency review, and loader validation not finalized | high | Dedicated renderer architecture/security phase | PARTIAL_READY |
| full renderer implementation readiness | Renderer options were assessed in Phase 10F-7 | No approved renderer, sandbox, dependency, or evidence plan | high | Explicit approval and dedicated implementation plan | NOT_READY |
| `structure.viewer_3d` implementation readiness | Historical inventory exists, but no approval | Tool semantics, routing, renderer, and evidence remain unresolved | high | Contract evidence, renderer readiness, and routing approval | NOT_READY |
| planner routing | Future routing policy exists from Phase 10F-7 | No routing implementation in this phase | medium | Separate planner/routing phase after tool approval | NOT_READY |
| CI stability | Docs-only contract phase has low CI risk | Implementation tests not present | low | Later schema/test implementation | READY for docs phase |
| phonon separation | Phonon remains separate future scope | None for this contract | low | Keep phonon out of viewer_scene v1 | READY |
| Brillouin-zone separation | Brillouin-zone 3D remains separate future scope | None for this contract | low | Keep Brillouin-zone out of viewer_scene v1 | READY |

## Final Decisions

- viewer_scene artifact contract planning: `READY`
- JSON-only preview planning: `READY`
- renderer handoff: `PARTIAL_READY`
- renderer implementation: `NOT_READY`
- full `structure.viewer_3d` implementation: `NOT_READY`

Phase 10F-9 may proceed to JSON-only preview evidence / contract fixture planning. It must not proceed directly to full viewer, WebGL, Three.js, renderer bundle, or phonon implementation.
