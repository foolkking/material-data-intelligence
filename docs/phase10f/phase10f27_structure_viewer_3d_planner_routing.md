# Phase 10F-27 structure.viewer_3d Planner Routing

Natural interactive-viewer intent in Chinese or English selects
`structure.viewer_3d`. Explicit inert scene JSON requests select
`structure.viewer_scene`. Deprecated metadata/export wording is redirected by
the established compatibility policy rather than advertising legacy producers.

Trajectory, phonon animation, Brillouin-zone, volumetric, and editing prompts
must not select the minimal structure viewer. Routing tests use MockLLMProvider
with a fixed local catalog; no real LLM or network request is used. Every
resulting plan still passes the unchanged PlanValidator and Tool Registry gate.
