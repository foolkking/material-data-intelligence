# Material Data Intelligence & Visualization Platform

This project designs a material data intelligence and visualization platform, not a thin pymatviz web wrapper.

Core capabilities:

- Natural-language material analysis requests.
- Upload CIF / POSCAR / XYZ / CSV / JSON limited / ZIP material datasets.
- Generate deterministic Data Profiles before Agent planning.
- Use an LLM Agent to produce a structured JSON Analysis Plan.
- Execute only Tool Registry approved pymatviz / MatterViz / Plotly / pymatgen / ASE / phonopy adapters.
- Generate interactive charts, 3D material viewers, Artifacts, Recipes, and Reports.
- Show Agent Timeline, tool calls, parameters, logs, reproducible code snippets, and results.
- Provide an AI assistant style workspace with a global dataset/model bar, a collapsible data-context viewer, and a main three-tab work area for Agent process, conversation/Plan Preview, and results/export.
- Design for asynchronous jobs, BYOK, permissions, audit logs, sandboxing, and domain extension.

## New Session Startup

Every Coding Agent or LLM session must read these files first:

1. `persistent/PROJECT_BRIEF.md`
2. `persistent/DESIGN_PROGRESS.md`
3. `persistent/TASK_BOARD.md`
4. `persistent/ARCHITECTURE_DECISIONS.md`
5. `docs/index.md`
6. `docs/13_SHARED_SCHEMA_SPEC.md`
7. The docs file for the phase currently being implemented.

## Persistent Update Rules

After each design or implementation phase, update:

- `persistent/DESIGN_PROGRESS.md`
- `persistent/TASK_BOARD.md`
- `persistent/ARCHITECTURE_DECISIONS.md`
- `persistent/OPEN_QUESTIONS.md`
- `persistent/CHANGELOG.md`

## Current Status

The codebase has progressed beyond the early shell: Phase 8B persisted AnalysisPlans and queue-worker exact execution are frozen, Phase 8C exposes planner provenance in the frontend, Phase 9A adds a gated OpenAI-compatible provider path without default real-LLM CI calls, and Phase 9B productizes the demo Planner workspace plus official direct-example evidence. Phase 9C updates the frontend design baseline to an AI assistant workspace: top global dataset/model context, resizable/collapsible left data viewer, and a main three-tab area for Agent process, conversation/Plan Preview, and results/export. Current verification remains based on the committed backend/frontend suites and service-backed CI integration from the frozen phase commits.

Current scope guard: live LLM verification is still gated and not default; production Secret encryption/KMS, multi-step DAG/data-dependency execution, worker supervision/dead-letter policy, advanced material viewer polish, and richer official example routing remain future work.

## Sharing Archive

When sharing this design outside the local Git workspace, do not include `.git/`. Prefer:

```bash
git archive --format=zip HEAD -o material-data-intelligence-design.zip
```

For manual zipping, exclude `.git/*`, `node_modules/*`, `.venv/*`, and runtime storage directories.
