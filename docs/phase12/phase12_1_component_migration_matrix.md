# Phase 12-1 Component Migration Matrix

The complete 38-row component disposition is maintained in
[`component_migration_matrix.json`](evidence/phase12_1_design_system_2_0/component_migration_matrix.json).
Every component has one allowed migration state. Shared Planner and Material
Intelligence status presentation are adapted to DS2. Specialized viewers retain
their scientific interactions and are marked `UNCHANGED_SPECIALIZED` or deferred
to their original Phase 12 owner. `UI_COMPONENT_MIGRATION_UNCLASSIFIED = 0`.

DS2 provides shared Button, icon-button, input, select, textarea, tab/segmented,
status, panel, table, dialog/drawer/sheet, toast/alert/callout, skeleton/loading
and empty/error visual foundations through the existing CSS architecture. It does
not introduce a parallel UI framework or a production styleguide route.
