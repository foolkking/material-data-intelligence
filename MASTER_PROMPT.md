# MASTER_PROMPT

You are working on the Material Data Intelligence & Visualization Platform.

Before making changes, read:

1. `README.md`
2. `AGENTS.md`
3. `persistent/PROJECT_BRIEF.md`
4. `persistent/DESIGN_PROGRESS.md`
5. `persistent/TASK_BOARD.md`
6. `persistent/ARCHITECTURE_DECISIONS.md`
7. `docs/index.md`
8. `docs/13_SHARED_SCHEMA_SPEC.md`
9. `docs/ROADMAP.md`
10. `docs/CAPABILITY_STATUS_MATRIX.md`
11. `docs/FUTURE_SCOPE.md`
12. `docs/NOT_PLANNED_SCOPE.md`
13. The docs file for the current implementation phase.

Core constraints:

- This is a full material data intelligence workspace, not a pymatviz web wrapper.
- LLMs produce JSON Analysis Plans only; they do not execute arbitrary code.
- Tool calls must go through Tool Registry, Schema validation, permissions, budget checks, and sandboxed workers.
- Long-running work is asynchronous and visible through JobEvent / Agent Timeline.
- Data Profiles are deterministic inputs to Agent planning.
- Artifacts, Recipes, Reports, metrics, tables, logs, and parameters must be auditable and reproducible.
- BYOK / Secret values must never be written to prompts, logs, Artifacts, Recipes, Reports, or export packages.
- The frontend is an AI assistant workspace, but this does not move execution authority to the browser: the UI uses a top dataset/model context bar, a collapsible data-context viewer, and a main three-tab work area for Agent process, conversation/Plan Preview, and results/export.
- `docs/ROADMAP.md` is the only current roadmap authority. Historical phase
  plans remain records and cannot override it.
- Future Scope cannot be promoted into `TASKS.md` without explicit reviewer/user
  approval.
- Not Planned capabilities cannot be reintroduced merely because they are
  technically possible.
- Never start an incomplete task prompt. The next approved direction after J-6
  is Phase 10K-0, but it starts only when its full task is supplied.

After meaningful design or implementation work, update the relevant `persistent/*.md` files.
