# V0 Product Scope Alignment

Status: CURRENT  
Date: 2026-09-11

## Product Definition

The current release scope is `V0`.

Material Data Intelligence is a natural-language-driven materials research
analysis and visualization workbench:

```text
Material Data
→ Research Question
→ Context / Intent
→ Capability / Tool / Adapter
→ Artifact
→ ScientificResult
→ Grounded Interpretation
→ Viewer / Workspace
→ Report
```

Bounded research strategy may continue from a Result to an evidence gap and
the minimum necessary next analysis. It is not an unlimited autonomous
scientist.

## Scope-Drift Inventory

| SURFACE | OBSERVATION | CLASSIFICATION | DISPOSITION |
|---|---|---|---|
| Current project state | J human review was described as the current engineering action and sole blocker. | `DOC_ONLY` | J is now a parallel external-validation lane and does not block Pre-M or M. |
| Canonical roadmap | The current A-I → Pre-M → M route was absent; historical phase chronology dominated the active authority. | `DOC_ONLY` | A new current V0 authority section supersedes conflicting route statements while retaining history. |
| Workstream K | No active runtime or queued K implementation was found. Its role was not explicit in the current roadmap. | `DOC_ONLY` | K is `CONDITIONAL_ONLY` on reproducible major/critical defects from real J reviews. |
| Workstream M | Long-running, scale and fault-tolerance closure was not represented as the required next V0 engineering stage after Pre-M. | `DOC_ONLY` | M0-M6 is restored as a required V0 stage. |
| Secondary LLM critic/reviewer | No critic service, reviewer provider, scientific-review mode, `RISK_AWARE` mode, reviewer-result persistence or frontend reviewer control was found in active runtime. | `NOT_PRESENT` | Explicitly prohibited from V0 active scope. No runtime removal was required. |
| `STRICT_PROVIDER` interpretation mode | One provider proposes a grounded Interpretation from an authorized evidence projection; deterministic validation and one bounded repair constrain it. It does not review another model response. | `ACTIVE_VALID_PRIMARY_PATH` | Preserved. It is an existing primary interpretation mode, not a critic/reviewer. |
| Workstream I | Claim-support, scope, method, causality, comparison, lineage and limitation checks are active derived guards. | `ACTIVE_VALID_GUARD` | Preserved as a structured scientific reasoning guard, not an expert scientist or certification authority. |
| Workstream J tooling and artifacts | Offline scripts, frozen responses, reviewer assignments and packets have no imports from application runtime. | `DORMANT_OFFLINE_EVALUATION` | Preserved byte-for-byte as parallel independent-human-validation infrastructure. |
| Expert mode/review UI | No AI expert-review mode was found. | `NOT_PRESENT` | No Expert Mode was added. Future professional controls may only mean direct user control of methods, parameters, presets, viewers and analysis scope. |

## Corrected Route

```text
A-I
COMPLETE
  ↓
V0 ALIGNMENT CORRECTION
COMPLETE
  ↓
Pre-M0  Reality Audit
Pre-M1  Context Integrity & Epistemic Purity
Pre-M2  User Control & Scientific Lifecycle
Pre-M3  Core UI/UX & Context Experience
Pre-M4  Scientific Presentation System
Pre-M5  Complex Material Data Qualification
Pre-M6  Pre-M Integrated Acceptance
  ↓
M0-M6  Long-running Research, Scale & Fault Tolerance
  ↓
Final V0 Integrated Acceptance
```

Parallel lane:

```text
J = REVIEW_READY
J_FORMAL_RESPONSES = FROZEN
INDEPENDENT_HUMAN_EXPERT_VALIDATION = PENDING
SCIENTIST_VALIDATION_MATURITY = NOT_YET_ASSESSED
```

J does not block Pre-M or M. K is not a planned optimization phase:

```text
K = CONDITIONAL_ONLY
```

It may be authorized only when actual independent J feedback establishes a
reproducible major or critical scientific defect, and any closure must use
fresh held-out validation.

## V0 Exclusions

The following are `OUT_OF_V0` or `DEFERRED` and are not active roadmap items:

- secondary LLM critic or scientific reviewer;
- AI-as-independent-expert or AI-as-human-validation substitute;
- unlimited autonomous research;
- arbitrary DAG/workflow builders;
- arbitrary Python, notebook or shell execution;
- full DFT/GW execution platform;
- large collaboration platform;
- enterprise governance, billing or marketplace;
- multi-region infrastructure;
- full multi-provider orchestration;
- autonomous literature-driven discovery;
- active-learning closed-loop discovery.

Historical documents may retain earlier proposals. This current authority
supersedes them for V0 routing without rewriting historical evidence.

## Preserved Authorities

No scientific or execution authority changed. The following remain intact:

- exact ScientificObject and ScientificObjectVersion identity;
- Dataset/Profile semantics;
- AnalysisPlan, Job, ToolCall, Artifact and six queue boundaries;
- ScientificResult and LiteratureEvidence authority;
- Capability, Tool and Adapter contracts and qualification fingerprints;
- ContextSnapshot provenance and Research Memory's non-truth role;
- Interpretation, Report and Workspace semantics;
- bounded autonomy, Evidence Gap, Hypothesis and Research Strategy;
- all validated H/I implementation and frozen J evaluation evidence.

## Alignment Verdict

```text
V0_PRODUCT_SCOPE = RECONCILED
SECONDARY_LLM_CRITIC = NOT_IN_V0_ACTIVE_SCOPE
AI_AS_HUMAN_EXPERT = PROHIBITED
WORKSTREAM_I = SCIENTIFIC_REASONING_GUARD
WORKSTREAM_J = PARALLEL_EXTERNAL_HUMAN_VALIDATION
INDEPENDENT_HUMAN_EXPERT_VALIDATION = PENDING
WORKSTREAM_K = CONDITIONAL_ONLY
PRE_M = NEXT_ENGINEERING_STAGE
WORKSTREAM_M = REQUIRED_V0_STAGE
ACTIVE_RUNTIME_SCOPE_DRIFT = 0
UNRESOLVED_DIRECTION_BLOCKERS = 0
READY_FOR_PRE_M = YES
```

## Route and maturity reconciliation

```text
V0_PRODUCT_MODEL = MATERIAL_RESEARCH_WORKBENCH
I_ROLE = SCIENTIFIC_REASONING_GUARD
J_ROLE = PARALLEL_HUMAN_VALIDATION
K_ROLE = CONDITIONAL_ONLY
M_ROLE = REQUIRED_V0_STAGE
G_BEHAVIORAL_SEMANTIC_READINESS = COMPLETE
DEEP_VISUAL_COMPLEX_CONTENT_QUALIFICATION = PENDING_PRE_M
UI_LAYOUT_SPEC_AS_IMPLEMENTATION_PROOF = 0
ATTACHMENT_CONTEXT_EXPERIENCE = REQUIRED_PRE_M_WORK
COMPLEX_MATERIAL_DATA = REQUIRED_PRE_M_WORK
PRE_M_ROUTE = DEFINED
M_ROUTE = DEFINED
FINAL_V0_ROUTE = DEFINED
ROUTE_RECONCILIATION_BLOCKERS = 0
READY_FOR_PRE_M = YES
```

Route deltas are recorded in
`docs/alignment/generated/v0_route_maturity_delta_ledger.json`.

## Pre-M completion addendum — 2026-09-11

The route gate above was satisfied and Pre-M0 through Pre-M6 were executed
without starting M. Current status:

```text
ROUTE_RECONCILIATION = PASS
SCIENTIFIC_AUTHORITY = PASS
NO_TRANSITIVE_SCIENTIFIC_AUTHORITY = PASS
CONTEXT_INTEGRITY = PASS
CONTEXT_TRANSPARENCY = PASS
PARAMETER_AUTHORITY = PASS
HISTORICAL_INTEGRITY = PASS
PARTIAL_INGESTION = PASS
SCIENTIST_UI_UX = DEEP_CURRENT_PRODUCT_VALIDATED
SCIENTIFIC_VIEWERS = PASS
LINKED_SELECTION = PASS
REPORT_QUALITY = PASS
COMPLEX_MATERIAL_DATA = PASS_WITH_EXPLICIT_LIMITS
PRE_M_BLOCKERS = 0
READY_FOR_M = YES
```

The detailed evidence is under `docs/agent2/pre-m/`. J remains frozen and
pending; M is the next required V0 stage and was not started.

## Production Semantic Audit Addendum — 2026-09-11

The follow-up semantic code-diff audit reviewed 56 modified production files,
the production LLM call sites, Context/Report authority wiring, and runtime
imports. It found no secondary reviewer/critic runtime and no Workstream J
production dependency. One authority-boundary defect was corrected: a Report
manifest entry had labeled validated Interpretation prose as
`SCIENTIFIC_RESULT`; it now uses `INTERPRETATION` / `DERIVED_SUMMARY`, with
fail-closed manifest compatibility checks.

Because production semantic behavior changed after the frozen J preparation
candidate was generated:

```text
CURRENT_J_CANDIDATE = PRE-CORRECTION_SCIENTIFIC_CANDIDATE
J_FROZEN_EVIDENCE = PRESERVED
```

The frozen J evidence was not regenerated or modified. A future formal
evaluation candidate must be generated only after Pre-M scientific semantics
are stable.
