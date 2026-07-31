# Partial Execution Interpretation Policy

`ALL_SUCCEEDED` may use every supported successful Artifact.
`PARTIAL_RESULTS` uses only successful, lineage-valid Artifacts and must show
failed/blocked steps and missing desired outputs before findings; its outcome
is `INTERPRETATION_READY_WITH_LIMITS`. `ALL_FAILED` produces no scientific
finding. Integrity aborts are never interpreted.

Success in an independent branch is not generalized to the full Plan, and a
failed or blocked ToolCall cannot become normal result evidence.
