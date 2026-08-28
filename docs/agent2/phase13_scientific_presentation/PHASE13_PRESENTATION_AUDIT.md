# PHASE13_PRESENTATION_AUDIT

## Scope

This audit records the existing presentation authorities before Phase 13
normalization. Phase 13 is a derived communication layer; it does not replace
ScientificResult, Artifact, Viewer, Evidence, or Report authority.

| Area | Classification | Existing authority / reuse |
|---|---|---|
| ScientificResult bundle | AUTHORITATIVE | API canonical projector and `GroundedScientificInterpretation` |
| Artifact projection | REUSABLE | `scientific-result-projection.ts` assigns bounded figure/table roles |
| Scientific Viewer | AUTHORITATIVE | `ScientificViewerRegistry`, `ScientificViewerShell`, adapter |
| Research response | REUSABLE | `ResearchPages.tsx`, grounded claims/evidence/limitations |
| Report snapshot | AUTHORITATIVE | `ScientificReportView` and report composition APIs |
| Report renderer | REUSABLE | `ScientificReportRoute.tsx` and legacy `ReportReaderPage` |
| Evidence | AUTHORITATIVE | interpretation evidence endpoint and persisted evidence items |
| Dataset table | REUSABLE | existing Materials Explorer/table renderer with stable sample identity |
| Presentation compiler | MISSING | added as bounded `compileScientificPresentation` |
| Presentation blocks | MISSING | added as typed, provenance-bearing blocks; no executable UI payload |

## Contract decision

The new compiler consumes grounded claims, typed evidence, bounded artifacts,
and exact source references. It emits narrative, finding, metric, figure,
table, viewer, evidence, limitation, and warning blocks. It never performs
scientific computation, resolves “latest”, accepts HTML/JS, or invokes a Tool.

## Visual direction

The UI uses a quiet editorial laboratory treatment: dense but readable
research-workbench spacing, restrained ink/surface tokens, and one acid-green
accent for provenance and action. Existing product tokens and Viewer components
remain the visual system authority.
