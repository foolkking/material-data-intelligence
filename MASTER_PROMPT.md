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
9. The docs file for the current implementation phase.

Core constraints:

- This is a full material data intelligence workspace, not a pymatviz web wrapper.
- LLMs produce JSON Analysis Plans only; they do not execute arbitrary code.
- Tool calls must go through Tool Registry, Schema validation, permissions, budget checks, and sandboxed workers.
- Long-running work is asynchronous and visible through JobEvent / Agent Timeline.
- Data Profiles are deterministic inputs to Agent planning.
- Artifacts, Recipes, Reports, metrics, tables, logs, and parameters must be auditable and reproducible.
- BYOK / Secret values must never be written to prompts, logs, Artifacts, Recipes, Reports, or export packages.
- The frontend is an AI assistant workspace, but this does not move execution authority to the browser: the UI uses a top dataset/model context bar, a collapsible data-context viewer, and a main three-tab work area for Agent process, conversation/Plan Preview, and results/export.

After meaningful design or implementation work, update the relevant `persistent/*.md` files.
