# Periodic Bond Cap Policy

| Layer | Limit | Behavior |
| --- | ---: | --- |
| Adapter canonical bonds | 2048 | Stable sort, bounded output, explicit truncation warning |
| Contract validator | artifact `max_bonds`, at most 2048 | Reject over-cap artifacts |
| Endpoint image component | absolute value <= 3 | Reject contract input; adapter omits with warning |
| Renderer displayed bonds | 8192 | Refuse derived supercell, retain current view/JSON |

Deduplication occurs before adapter cap counting and again during renderer derivation. No renderer-side silent truncation occurs.
