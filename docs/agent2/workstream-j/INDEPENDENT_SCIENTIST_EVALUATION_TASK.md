# Workstream J — Independent Scientist Evaluation

## Scope

Prepare a frozen, reviewer-blinded independent scientist evaluation of the
canonical A–I candidate in `E:\1project\mdi-b0-5a1`.

This task is evaluation infrastructure only. It must not change scientific
reasoning behavior, prompts, validators, provider configuration, Results,
LiteratureEvidence, or product authority.

## Required preparation

- Capture one immutable evaluation-baseline manifest.
- Define 24 held-out scored cases, 4 calibration cases, and up to 6 optional
  shadow cases. Workstream I's 27 cases remain internal regression evidence and
  are not the J scored corpus.
- Generate formal responses through the currently configured canonical
  provider path where available, then freeze response and evidence hashes.
- Generate reviewer-blinded packets with Pass 1/Pass 2 separation, assignments,
  conflict metadata, blank submission forms, and no expected labels, provider
  identity, hidden reasoning, or developer notes.
- Provide strict import, integrity, disagreement, and reporting tooling.
- Add no human scores unless they are submitted by real independent reviewers.

## Human boundary

No reviewer identities, scores, comments, expertise, or validation outcome may
be invented or inferred. If no real submissions exist, the truthful outcome is:

```text
J_STATUS = REVIEW_READY
J_REVIEW_INFRASTRUCTURE = READY
J_FORMAL_RESPONSES = FROZEN
INDEPENDENT_HUMAN_EXPERT_VALIDATION = PENDING
SCIENTIST_VALIDATION_MATURITY = NOT_YET_ASSESSED
```

## Completion rule

Preparation may be marked complete only when the frozen assets and validation
commands are reproducible. The Workstream J human-validation task remains
pending until at least three independent qualified reviewers submit locked
records. Do not claim J `COMPLETE` or an independent validation verdict during
preparation.
