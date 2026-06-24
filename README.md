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

The repository is currently documentation-first. The next engineering step is to follow `docs/12_MVP_ROADMAP.md` and create the implementation scaffold.

## Sharing Archive

When sharing this design outside the local Git workspace, do not include `.git/`. Prefer:

```bash
git archive --format=zip HEAD -o material-data-intelligence-design.zip
```

For manual zipping, exclude `.git/*`, `node_modules/*`, `.venv/*`, and runtime storage directories.
