# Phase 12-1 Status Visual Mapping

The exact mapping is in
[`status_visual_mapping.json`](evidence/phase12_1_design_system_2_0/status_visual_mapping.json).
It maps existing source states to a presentation variant while retaining the source
label and authority. Every row has `colorOnlyMeaning = false` and
`scientificAuthorityChanged = false`.

Warnings, limitations, partial states, unsupported states, stale states and errors
are deliberately distinct. A persistent scientific limitation is not represented
as a dismissible toast. A disabled control remains distinct from an unavailable
capability or an in-flight request.
