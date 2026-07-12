# Phase 10F-18 Implementation

The Python contract validates v1 and v2 identities, strict periodic endpoint objects, integer offset bounds, source semantics, distance/displacement consistency, duplicates, stable ids, and caps. Both `structure.viewer_scene` and `structure.viewer_3d` use the same adapter topology generator.

The frontend validator mirrors the strict boundary. The mapper computes endpoint Cartesian positions from stored offsets without minimum-image reselection. Supercells replicate complete edges only when both endpoints are displayed. Shared `LineSegments` geometry remains bounded. The inspector exposes target site/image, stored distance, source, authority, and a highlight action.
