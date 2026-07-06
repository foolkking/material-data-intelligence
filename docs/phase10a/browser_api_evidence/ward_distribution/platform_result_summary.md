# ward_distribution Platform Result Summary

## 1. Verdict
PASS

## 2. Source benchmark case
- case_id: ward_metallic_glasses_csv_xz
- case_type: direct_uploadable_data
- verification_status: DIRECT_VERIFIED
- pinned source commit: db47a447ca53b9415243b1c8f01578da10aec00b

## 3. Prompt
请分析 Ward metallic glasses 表格的数值分布、缺失值、分位数和类别字段统计 distribution summary。

## 4. Plan
- tool: table.distribution_summary
- params: `{"maxCategories": 12, "numericColumns": ["D_max", "dTx"], "categoricalColumns": ["material_id", "composition", "gfa_type"]}`
- planId: plan_ad845d07ccf04029943512e7
- planHash: 29975b163e08a59ee0eb16f45963230efd61cb80a44f4f16ea3e3d32af0bd00e

## 5. Job
- jobId: job_bcaab519b99f43159f09cef0
- status: completed
- timeline: artifact.ready, data.loaded, job.completed, job.created, job.running, plan.loaded, plan.persisted, tool.completed, tool.started

## 6. Artifacts
- distribution_summary.json (table_json)
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
- Plan Preview tool is table.distribution_summary
- toolCall table.distribution_summary completed
- job completed
- timeline has plan.loaded
- timeline has data.loaded
- timeline has tool.completed
- timeline has job.completed
- does not call ml.basic_metrics
- no D_max vs dTx regression metrics
- distribution_summary.json artifact exists
- distribution_summary.json.rowCount == 8415
- distribution_summary.json.columnCount > 0
- numericColumns exists
- categoricalColumns exists
- recommendedVisualizations exists
- summary.md artifact exists
- recipe.json artifact exists
### Failed
- none

## 10. Boundaries
- uses real LLM: false
- uses mock planner: true
- default CI real LLM: false
- secret leakage: redacted scan required before commit
