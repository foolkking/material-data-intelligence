# ward_composition_summary Platform Result Summary

## 1. Verdict
PASS

## 2. Source benchmark case
- case_id: ward_metallic_glasses_csv_xz
- case_type: direct_uploadable_data
- verification_status: DIRECT_VERIFIED
- pinned source commit: db47a447ca53b9415243b1c8f01578da10aec00b

## 3. Prompt
请统计 Ward metallic glasses 表格中 composition 字段的元素组成分布 composition summary。

## 4. Plan
- tool: composition.summary
- params: {"formulaColumn": "composition"}
- planId: plan_f6c98d2d2835438689364ddf
- planHash: 4379e3b712e24b182f3d601b7ac58990da7dd74d461cb656570fb751ce5a77c0

## 5. Job
- jobId: job_b7d2f69b76e7431f96e3d85e
- status: completed
- timeline: job.created, plan.persisted, job.running, plan.loaded, data.loaded, tool.started, artifact.ready, artifact.ready, artifact.ready, tool.completed, job.completed

## 6. Artifacts
- artifacts/composition_summary.json
- artifacts/summary.md
- artifacts/recipe.json

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
- passed: 15
- failed: 0

## 10. Boundaries
- uses real LLM: no
- uses mock planner: yes
- default CI real LLM: no
- secret leakage: redacted evidence only
