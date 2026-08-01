# Current Persistence Inventory

Audit baseline: `8f304fa08ddab1cefd69848f621f8438fc2038d5`. Current Alembic head: `0006_phase10l4_interpretation`.

Current durable authorities cover Project, Dataset/version, DataProfile, AnalysisIntent, eligibility and decision, AnalysisPlan, Job/event, ToolCall, Artifact, dependency execution and lineage, evidence bundle/items, interpretation/claims/links, Report, and VisualizationRecipe.

`sessions` and `messages` tables exist without a current repository/API/product flow and do not own scientific Workspace identity or layout. They are not selected as Workspace persistence.

Confirmed absences:

- no `scientific_workspaces` table;
- no Workspace panel table;
- no layout revision/recovery table;
- no persisted global exact selection context.

Historical Job records are sufficient for exact lazy projection when their identity chain is present. Records with missing modern identity require explicit read-only projection; no bulk scientific backfill is authorized.
