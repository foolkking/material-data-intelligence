# Reviewer Instructions

You are reviewing a bounded scientific-assistant response, not judging a
person or a provider brand. Do not infer hidden implementation details.

## Before starting

- Declare your expertise for each assigned case as `PRIMARY`, `COMPETENT` or
  `LIMITED`.
- Declare `NO_CONFLICT` only when you did not implement A–I, design the tested
  prompts/validators, know the Workstream I failures, or author the case.
- Complete calibration cases independently. Reveal calibration guidance only
  after calibration is locked.

## Pass 1

Read the research question, System Response and normal source/method/
limitation disclosure. Do not inspect Pass 2 evidence until Pass 1 is locked.
Record scientific acceptability, misleading issue, usefulness and whether the
response is suitable as an input to the next research decision.

## Pass 2

After release, inspect the exact Results, literature passages, conditions,
methods, scope, lineage and claim mapping. Score the eight rubric dimensions,
select a verdict, answer the research-decision question and review only the
most important claims. Record scientific defects, not stylistic preferences.

Do not rewrite the answer, add outside literature, or use provider/model
identity as evidence. A cautious “insufficient evidence” outcome can be the
best answer.

## Submission

Preserve the response and evidence hashes. Set `locked=true`, provide an ISO
timestamp, complete conflict/expertise fields and submit the JSON to the
administrator. Pass 2 cannot be imported before the same reviewer’s locked
Pass 1. Submitted records are immutable; corrections are new auditable
records, not silent edits.

