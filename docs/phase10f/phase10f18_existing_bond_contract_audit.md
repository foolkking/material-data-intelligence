# Existing Bond Contract Audit

`viewer_scene.v1` bonds contain `from`, `to`, `distance`, and style metadata. They have no endpoint image offsets, generation source, authoritative flag, or stable periodic identity. The Phase 10F-17 renderer can therefore interpret them only as same-cell edges and replicate only same-cell topology.

Old flow: `Structure -> bounded pair candidate -> v1 bond -> validator -> mapper -> same-cell LineSegments -> inspector`. Missing image identity made cross-boundary inference unsafe.
