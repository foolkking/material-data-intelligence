# ward_correlation Platform Result Summary

## 1. Verdict
PASS

## 2. Source benchmark case
- case_id: ward_metallic_glasses_csv_xz
- case_type: direct_uploadable_data
- verification_status: DIRECT_VERIFIED
- pinned source commit: db47a447ca53b9415243b1c8f01578da10aec00b

## 3. Prompt
请分析 Ward metallic glasses 表格中数值字段之间的相关性，并生成相关矩阵 correlation matrix。

## 4. Plan
- tool: viz.correlation
- params: `{"numericColumns": ["D_max", "dTx"], "method": "pearson", "minNonNullCount": 2}`
- planId: plan_b97cba0c2fd249cfac00cfca
- planHash: f4334204fd416cfdffbd0d81130575369819d6725f99a999fc69801856d13a4a

## 5. Job
- jobId: job_f3faed1162134846b4c8c48f
- status: completed
- timeline: artifact.ready, data.loaded, job.completed, job.created, job.running, plan.loaded, plan.persisted, tool.completed, tool.started

## 6. Artifacts
- correlation_matrix.json (table_json)
- correlation_heatmap.json (plotly_json)
- correlation_heatmap.html (plotly_html)
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
- Plan Preview tool is viz.correlation
- toolCall viz.correlation completed
- job completed
- timeline has plan.loaded
- timeline has data.loaded
- timeline has tool.completed
- timeline has job.completed
- does not call ml.basic_metrics
- no D_max vs dTx regression metrics
- correlation_matrix.json artifact exists
- correlation_matrix.json.columns >= 2
- correlation_matrix.json.matrix exists
- correlation_heatmap.json artifact exists
- summary.md artifact exists
- recipe.json artifact exists
### Failed
- none

## 10. Boundaries
- uses real LLM: false
- uses mock planner: true
- default CI real LLM: false
- secret leakage: redacted scan required before commit
