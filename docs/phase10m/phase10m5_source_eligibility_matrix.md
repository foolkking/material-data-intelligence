# Phase 10M-5 Source Eligibility Matrix

The read-only projector covers all 42 M4 Artifact contracts through an exact
contract/version map. Filename, title, label, MIME alone, array order, fuzzy
matching, and latest-version rebinding are prohibited.

| Source | Report classification | Representation |
| --- | --- | --- |
| Approved plot/image contract | `REPORT_FIGURE_SOURCE` | Static plot plus numeric/table fallback |
| Approved table contract | `REPORT_TABLE_SOURCE` | Bounded semantic table with units/identity |
| Grounded ScientificClaim | `REPORT_FINDING_SOURCE` | Immutable validated claim text and refs |
| ScientificEvidenceItem | `REPORT_EVIDENCE_SOURCE` | Exact normalized evidence record |
| Lineage/environment/reference | `REPORT_PROVENANCE_SOURCE` | Exact metadata reference |
| Warning/failure/blocked/missing | `REPORT_DISCLOSURE_ONLY` | Mandatory inert disclosure |
| Structure/trajectory/BZ/volume without static figure | `REPORT_METADATA_ONLY` | Artifact identity and approved fallback |
| Unknown/version mismatch/integrity failure | `REPORT_UNSUPPORTED` | Typed reason, no guessed preview |

Each item carries exact source kind/ID/hash, contract/version, Project,
Dataset/version, Job, ToolCall, panel, lineage, allowed roles, fallback, and
authorization state. Initial inventory is metadata-only and does not load
heavy Artifact payloads.
