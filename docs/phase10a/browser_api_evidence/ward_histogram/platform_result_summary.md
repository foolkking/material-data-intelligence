# ward_histogram Platform Result Summary

## 1. Verdict
PASS

## 2. Source benchmark case
- case_id: ward_metallic_glasses_csv_xz
- case_type: direct_uploadable_data
- verification_status: DIRECT_VERIFIED
- pinned source commit: db47a447ca53b9415243b1c8f01578da10aec00b

## 3. Prompt
请查看 Ward metallic glasses 表格中 D_max 数值列的分布，并生成直方图 histogram。

## 4. Plan
- tool: viz.histogram
- params: `{"column": "D_max", "bins": 20, "title": "D_max distribution"}`
- planId: plan_334f21237d9b4dcc842c54b2
- planHash: 9188c6c8098fe2bc5253040f1959228eb99c9a2403cade6af7b00ca67ae2681f

## 5. Job
- jobId: job_e4b44a680fb24fb6bab9c69b
- status: completed
- timeline: artifact.ready, data.loaded, job.completed, job.created, job.running, plan.loaded, plan.persisted, tool.completed, tool.started

## 6. Artifacts
- histogram.json (plotly_json)
- histogram.html (plotly_html)
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
- Plan Preview tool is viz.histogram
- toolCall viz.histogram completed
- params.column == D_max
- job completed
- timeline has plan.loaded
- timeline has data.loaded
- timeline has tool.completed
- timeline has job.completed
- does not call ml.basic_metrics
- no D_max vs dTx regression metrics
- histogram.json artifact exists
- histogram.json.chartType == histogram
- histogram.json.column == D_max
- histogram.json.count > 0
- histogram.json.binCounts exists
- summary.md artifact exists
- recipe.json artifact exists
### Failed
- none

## 10. Boundaries
- uses real LLM: false
- uses mock planner: true
- default CI real LLM: false
- secret leakage: redacted scan required before commit
