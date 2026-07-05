# AGENTS.md

Start by reading `persistent/PROJECT_BRIEF.md`, `persistent/DESIGN_PROGRESS.md`, `persistent/TASK_BOARD.md`, `persistent/ARCHITECTURE_DECISIONS.md`, `docs/index.md`, and `docs/13_SHARED_SCHEMA_SPEC.md`.

## Agent Working Rules

1. Do not turn this project into a pymatviz web wrapper.
2. Do not let the LLM directly execute arbitrary Python, shell, filesystem, or network actions.
3. The Agent can only produce a structured JSON Analysis Plan.
4. Every executable tool call must go through Tool Registry validation.
5. Every long-running parse, planning, visualization, rendering, export, or report task must run asynchronously.
6. The frontend must show Agent Timeline and structured process records, not hidden chain of thought.
7. Every Artifact, Recipe, and Report must be auditable and reproducible.
8. User Secret / BYOK values must never enter prompts, logs, Artifacts, Recipes, Reports, or export packages.
9. Update persistent files after every meaningful design or implementation change.
10. Frontend UI redesigns must not move execution authority into the browser; Planner jobs still flow through validated/persisted AnalysisPlans, QueueWorkerRuntime, Tool Registry, and Adapter execution.

## Documentation Rules

- Keep `docs/` and `persistent/` tracked in git.
- Prefer updating existing design files over creating duplicate notes.
- Add new shared schemas to `docs/13_SHARED_SCHEMA_SPEC.md`.
- Keep MVP / V1 / V2 scope consistent across docs.
- Keep the Phase 9C frontend baseline consistent: top global context bar, collapsible/resizable left data-context viewer, and one active main workspace tab among Agent process, conversation/Plan, and results/export.
