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
- Design for asynchronous jobs, protected BYOK, auditability, reproducibility,
  and bounded scientific capability extension.

The initial complete product joins Material Data Profile capability discovery,
dataset/materials intelligence, materials ML evaluation, capability-aware
planning, bounded multi-tool analysis, scientific visualization, interpretation,
and a unified report/workspace experience. It analyzes existing data; it does
not run DFT/HPC jobs or arbitrary user code.

## Canonical Product Documents

* [`docs/phase13/release/README.md`](docs/phase13/release/README.md) - current Initial Release documentation
* [`docs/phase13/reproducibility/README.md`](docs/phase13/reproducibility/README.md) - deterministic seven-demo reproduction
* [`docs/phase13/release/quick-start.md`](docs/phase13/release/quick-start.md) - verified installation and service startup
* [`docs/phase13/release/limitations.md`](docs/phase13/release/limitations.md) - current claim and limitation boundaries
* [`docs/00_PROJECT_GOAL.md`](docs/00_PROJECT_GOAL.md)
* [`docs/01_PRODUCT_REQUIREMENTS.md`](docs/01_PRODUCT_REQUIREMENTS.md)
* [`docs/ROADMAP.md`](docs/ROADMAP.md)
* [`docs/CAPABILITY_STATUS_MATRIX.md`](docs/CAPABILITY_STATUS_MATRIX.md)
* [`docs/FUTURE_SCOPE.md`](docs/FUTURE_SCOPE.md)
* [`docs/NOT_PLANNED_SCOPE.md`](docs/NOT_PLANNED_SCOPE.md)

## New Session Startup

Every Coding Agent or LLM session must read these files first:

1. `persistent/PROJECT_BRIEF.md`
2. `persistent/DESIGN_PROGRESS.md`
3. `persistent/TASK_BOARD.md`
4. `persistent/ARCHITECTURE_DECISIONS.md`
5. `docs/index.md`
6. `docs/13_SHARED_SCHEMA_SPEC.md`
7. `docs/ROADMAP.md`
8. `docs/FUTURE_SCOPE.md`
9. `docs/NOT_PLANNED_SCOPE.md`
10. The docs file for the phase currently being implemented.

## Persistent Update Rules

After each design or implementation phase, update:

- `persistent/DESIGN_PROGRESS.md`
- `persistent/TASK_BOARD.md`
- `persistent/ARCHITECTURE_DECISIONS.md`
- `persistent/OPEN_QUESTIONS.md`
- `persistent/CHANGELOG.md`

## Current Status

Phase 13-2 Attempt 6 passed all seven fresh canonical real-user service-backed
workflows and P13X2 `8/8`. Phase 13-3 is producing the current documentation
and reproducibility package. The current Fact Model is
`92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a` and
the current Scope Baseline is
`bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba`.

Phase 13-4 remains reviewer-gated. Initial Release completion has not been
declared, and no Phase 14 exists. Fermi Surface remains Future Scope;
enterprise SaaS, deployment productization, and a plugin marketplace remain
Not Planned.

## Sharing Archive

When sharing this design outside the local Git workspace, do not include `.git/`. Prefer:

```bash
git archive --format=zip HEAD -o material-data-intelligence-design.zip
```

For manual zipping, exclude `.git/*`, `node_modules/*`, `.venv/*`, and runtime storage directories.
