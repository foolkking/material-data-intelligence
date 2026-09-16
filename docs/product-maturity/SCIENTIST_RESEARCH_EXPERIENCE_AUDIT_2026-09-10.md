# Scientist Research Experience — Bounded Product Audit

Date: 2026-09-10  
Canonical runtime: `E:\1project\mdi-b0-5a1`  
Audience: materials researchers who understand their science but do not know Agent, Tool, worker, or persistence internals.

## Scope

This is a bounded Workstream G reality check, not a redesign audit. It inspected the current canonical Research product through a real browser and canonical API runtime, focusing on:

- ordinary Research entry;
- historical Result reopen;
- bounded-autonomy controls and progress;
- scientific findings, limitations, sources, and provenance;
- recovery actions;
- desktop and 390×844 mobile behavior.

The existing global shell, conversation/workbench split, viewer architecture, progressive disclosure, and mobile single-pane pattern were retained as the product baseline.

## Evidence Log

### Observed

- The Research page presents a conversation-centered left pane and scientific workbench.
- Bounded multi-step research is explicitly opt-in through the composer.
- Existing strategy projection exposes the current question, active evidence gap, active hypothesis, continuation/stop summary, and critical limitation.
- Historical scientific Results reopen into the workbench and preserve available figures/tables.
- Completed process detail collapses into a compact timeline item.
- Mobile switches between conversation and workbench without horizontal page overflow at 390×844.
- Failed/cancelled states expose recovery actions.

### Not observed or incomplete

- No compact Research Map showing resolved, partially addressed, unresolved, or unanswerable scientific questions.
- Hypotheses are not visually or semantically separated strongly enough from findings.
- Stop, cancel, retry, continue, and intentional rerun language does not consistently match lifecycle semantics.
- Raw technical identifiers appear in ordinary source/result presentation.
- Exact source version is available but often expressed through internal identity rather than scientist-facing labels.
- A generic cross-Result comparison compatibility workflow was not found in the inspected Research surface; existing comparison behavior is primarily capability/viewer-specific.
- Some historical pre-ResearchTurn runs reopen honestly but cannot reconstruct a research question or branch.

## Findings

### FLOW-01 — Research resolution is not summarized as a map

- Severity: High
- Evidence: The current strategy card shows one current question/gap/hypothesis, but not the relationship between the main objective, resolved questions, unresolved questions, evidence, and limitations.
- Consequence: A scientist can follow the latest operation but cannot quickly answer “what has been established and what remains open?” during or after multi-cycle research.
- Recommendation: Add a compact, read-only Research Map derived from durable strategy/evidence projections. Keep it in the Research timeline, not a fixed operational rail.

### TRUST-01 — Hypothesis presentation is too close to ordinary findings

- Severity: High
- Evidence: The active hypothesis appears as ordinary strategy text without an explicit epistemic status.
- Consequence: A tentative scientific explanation can be read as an established finding.
- Recommendation: Present hypotheses in a dedicated neutral/amber treatment with explicit status, supporting evidence, and limitation. Never use success styling for an untested hypothesis.

### COPY-01 — Research controls do not consistently communicate lifecycle semantics

- Severity: High
- Evidence: Active execution is labelled “停止研究” while the current action requests cancellation. Failed/cancelled recovery actions mix “继续研究” and “重新研究” without clearly distinguishing durable-boundary retry from intentional recomputation.
- Consequence: Users cannot reliably predict whether completed science will be preserved, reused, or recomputed.
- Recommendation: Name controls according to actual behavior: cancel current analysis, continue current research, retry failed analysis only when a durable retry exists, and run again for intentional new execution.

### DATA-01 — Internal identifiers dominate normal scientific presentation

- Severity: High
- Evidence: Raw object/profile/dataset identifiers are visible in ordinary source and viewer metadata, particularly prominent on mobile.
- Consequence: Scientific meaning is displaced by implementation identity, contrary to the result-first mental model.
- Recommendation: Use human-readable scientific source labels and version numbers by default. Move exact UUIDs and infrastructure identifiers into the deepest technical provenance disclosure.

### FBK-01 — Continue/stop rationale lacks durable scientist-facing continuity

- Severity: Medium
- Evidence: A current strategy card can explain the latest continuation or stop, but historical reopen does not consistently provide a durable question-resolution summary.
- Consequence: A returning scientist may see outputs without understanding why the Agent continued or stopped.
- Recommendation: Persist or project compact question/evidence/decision summaries and render them in the Research Map and final stop state.

### FLOW-02 — General comparison compatibility is not a first-class Research workflow

- Severity: Medium
- Evidence: Capability-specific viewers support comparison, but the inspected Research surface has no general entry for selecting two Results and explaining compatibility across quantity, units, method, normalization, and conditions.
- Consequence: Researchers need implementation knowledge or separate navigation to compare Results safely.
- Recommendation: Reuse Workstream F comparison-compatibility projections where available. If no generic authoritative projection exists, keep capability-specific comparison and record the general workflow as a bounded remaining gap rather than computing compatibility in the browser.

### STATE-01 — Legacy historical runs can lack a recoverable research question

- Severity: Medium
- Evidence: A reopened historical run explicitly states that no recoverable Research conversation is associated with it.
- Consequence: Results remain useful, but question/branch continuity is unavailable.
- Recommendation: Preserve the honest legacy state. Do not invent a question from Result text. Offer source/result inspection and start-new-research actions.

### MOBILE-01 — Mobile layout is structurally sound but scientific scanning is noisy

- Severity: Low
- Evidence: No blocking horizontal overflow was observed at 390×844, and pane switching works. Long raw identifiers and dense technical metadata remain highly visible.
- Consequence: The user can complete the flow, but scientific findings and limitations are harder to scan.
- Recommendation: Preserve the established mobile pattern; improve hierarchy and remove default raw-ID exposure rather than redesigning the layout.

## Product Decisions

1. Preserve the existing global shell, Research conversation/workbench split, responsive pane switching, viewers, and design tokens.
2. Add Research Map and hypothesis semantics to the existing Research timeline/activity responsibility.
3. Derive UI from durable A–F authorities; do not create a frontend research authority.
4. Rename controls to match actual lifecycle behavior. Do not claim safe retry where only a new run exists.
5. Lead with source display name/type and version; retain exact IDs only in advanced technical provenance.
6. Reuse server comparison compatibility if available. Do not create scientific compatibility calculations in the browser.
7. Treat pre-ResearchTurn historical runs as an explicit legacy limitation rather than fabricating continuity.

## Rejected Alternatives

- A fixed right-side activity rail: rejected because Research progress belongs in the conversation/timeline and the workbench is reserved for scientific content.
- A new graph editor for research strategy: rejected; a compact readable Research Map is sufficient.
- Client-side inference of scientific resolution or comparison compatibility: rejected because it would create a frontend scientific authority.
- A broad visual redesign: rejected because current friction is semantic/control/provenance clarity, not the design-system foundation.
- Raw strategy JSON or chain-of-thought disclosure: rejected; only structured observable scientific provenance is appropriate.

