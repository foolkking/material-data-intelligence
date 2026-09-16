# Pre-M1 Context Integrity & Epistemic Purity

Status: `PASS`  
Date: 2026-09-11

## Authority rule

```text
NO_TRANSITIVE_SCIENTIFIC_AUTHORITY = ENFORCED
```

Direct claim support is limited to:

- `ScientificResult`;
- deterministic `SCIENTIFIC_FINDING` facts projected from a Result;
- `LiteratureEvidence` within its persisted scope.

`Interpretation`, `Report`, `Memory`, `Hypothesis`, assistant prose and repeated
historical summaries remain continuity/presentation material. Pinning changes
selection priority only; it never upgrades authority.

## Context roles

The current projection uses:

```text
EVIDENCE
CONTINUITY
SUBJECT
CONSTRAINT
PREFERENCE
```

`support_eligible` is deterministic and validated fail-closed. Kind/authority
incompatibility is rejected. A Result-derived finding remains support-eligible
because it carries deterministic Result lineage; a raw object, report sentence
or memory statement does not.

## Dereference and stage boundaries

Historical Interpretation/Report/Memory content may help identify a subject or
continue a conversation. Scientific support must return to the nearest exact
Result or LiteratureEvidence reference. If no authority exists, the product
may state only that a historical note made the claim.

Provider-facing operations remain separate (`ORCHESTRATOR`, `PLANNER`,
`INTERPRETER`, `DATA`, `REPORT`) with bounded policies. Tool/Adapter execution
has zero LLM calls. Product disclosure may show user prompt, interpreted
objective, validated plan and selected Context; it never exposes system/developer
prompts, hidden reasoning, secrets or raw provider requests.

## Regression evidence

- Context/Result reuse regression: `17 passed`.
- Complex-family Context/reasoning/knowledge/report suite:
  `380 passed, 1 skipped`.
- Explicit negative boundaries:
  `NO_REPORT_AS_SCIENTIFIC_EVIDENCE`,
  `NO_MEMORY_AS_SCIENTIFIC_EVIDENCE`,
  `NO_J_EVALUATION_RUNTIME_IMPORT`.

One Pre-M regression was found and fixed: automatic `SCIENTIFIC_FINDING`
projection initially defaulted to non-supporting despite carrying exact
ScientificResult fact lineage. The deterministic policy now classifies it as
evidence while retaining all derived prose as non-supporting.
