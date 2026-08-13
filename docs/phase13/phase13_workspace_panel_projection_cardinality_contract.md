# Workspace Panel Projection Cardinality Contract

`ArtifactCount != WorkspacePanelCount` is a permanent invariant. A Workspace panel
is a product-level navigation surface, not a persisted Artifact row. Structural
surfaces are projected from the existing Workspace contract. Supporting Artifacts
for a logical Job result are reached through the existing Job-scoped Artifact Gallery
and exact typed renderer dispatch.

Grouping authority is exact Artifact type/version, renderer contract/version, bundle
contract, and Job/project lineage. Filename, MIME alone, array position, ToolCall
position, timestamps, latest/nearest selection, and fuzzy labels are not authority.

The cap remains 32. Thirty-two legitimate distinct non-groupable surfaces pass; 33
reject with typed `PANEL_CAP_EXCEEDED`; truncation is forbidden. Existing persisted
Workspaces are not backfilled and GET does not reproject or write membership.
