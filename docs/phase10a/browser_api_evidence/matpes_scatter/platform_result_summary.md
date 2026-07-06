# matpes_scatter Platform Result Summary

## 1. Verdict
PASS

## 2. Source benchmark case
- case_id: matpes_atomic_energies_csv
- case_type: direct_uploadable_data
- verification_status: DIRECT_VERIFIED
- pinned source commit: db47a447ca53b9415243b1c8f01578da10aec00b

## 3. Prompt
请比较 PBE 与 r2SCAN 两列原子能量数据，并画散点图 scatter plot compare。

## 4. Plan
- tool: viz.scatter
- params: `{"xColumn": "PBE", "yColumn": "r2SCAN", "title": "PBE vs r2SCAN"}`
- planId: plan_be9e1d0fdd524972bf6b68c8
- planHash: b01da1ccc125511100c15812f4d22f1545af08c935cdbd9f37527cddcb20712b

## 5. Job
- jobId: job_67db9db18f044a638f580f41
- status: completed
- timeline: artifact.ready, data.loaded, job.completed, job.created, job.running, plan.loaded, plan.persisted, tool.completed, tool.started

## 6. Artifacts
- scatter.json (plotly_json)
- scatter.html (plotly_html)
- summary.md (summary_md)
- recipe.json (recipe_json)

## 7. Browser screenshots
- screenshots/01_upload_profile.png
- screenshots/02_chat_plan_preview.png
- screenshots/03_agent_process_completed.png
- screenshots/04_results_export.png
- screenshots/05_developer_audit_redacted.png

## 8. API captures
- api_redacted/upload_response.json
- api_redacted/profile_response.json
- api_redacted/provider_resolve_response.json
- api_redacted/planner_preview_response.json
- api_redacted/planner_validate_response.json
- api_redacted/planner_job_response.json
- api_redacted/events_response.json
- api_redacted/tool_calls_response.json
- api_redacted/artifacts_response.json
- api_redacted/result_response.json

## 9. Assertions
### Passed
- prompt does not contain y_true/y_pred
- Plan Preview tool is viz.scatter
- toolCall viz.scatter completed
- params.xColumn == PBE
- params.yColumn == r2SCAN
- job completed
- timeline has plan.loaded
- timeline has data.loaded
- timeline has tool.completed
- timeline has job.completed
- scatter.json artifact exists
- scatter.json.chartType == scatter
- scatter.json.xColumn == PBE
- scatter.json.yColumn == r2SCAN
- scatter.json.pointCount == 89
- scatter.json.pointCount > 0
- summary.md artifact exists
- recipe.json artifact exists
### Failed
- none

## 10. Boundaries
- uses real LLM: false
- uses mock planner: true
- default CI real LLM: false
- secret leakage: redacted scan required before commit
