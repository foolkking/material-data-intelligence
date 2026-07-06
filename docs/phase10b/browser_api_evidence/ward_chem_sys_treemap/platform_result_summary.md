# Platform Result Summary

## Verdict
PASS

## What was verified
`composition.chem_sys_treemap` completed through dataset/profile, planner preview, PlanValidator validation, persisted planner job execution, Tool Registry + Adapter execution, artifact generation, result/report/recipe display, browser screenshots, and redacted API captures.

## Generated artifacts
- chem_sys_treemap.json (plotly_json, 36728 bytes)
- chem_sys_treemap.html (plotly_html, 34344 bytes)
- summary.md (summary_md, 376 bytes)
- recipe.json (recipe_json, 656 bytes)

## Browser evidence
- browser_screenshots/01_dataset_profile.png
- browser_screenshots/02_plan_preview.png
- browser_screenshots/03_agent_process_completed.png
- browser_screenshots/04_results_artifacts.png
- browser_screenshots/05_developer_audit_redacted.png

## API evidence
- api_redacted/artifacts_response.json
- api_redacted/events_response.json
- api_redacted/job_response.json
- api_redacted/planner_preview_response.json
- api_redacted/planner_validate_response.json
- api_redacted/profile_response.json
- api_redacted/provider_resolve_response.json
- api_redacted/result_response.json
- api_redacted/tool_calls_response.json
- api_redacted/upload_or_dataset_response.json

## Security
API captures were redacted before writing. This case uses Mock Planner and no live LLM.

## Boundary
This evidence only covers `ward_chem_sys_treemap` and does not claim unsupported or non-direct official examples are verified.
