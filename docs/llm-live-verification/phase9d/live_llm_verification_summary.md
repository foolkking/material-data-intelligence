# Phase 9D True LLM Live Verification Summary

## Verification environment

- Date: 2026-07-05
- Phase baseline: `phase9d0-llm-config-path-repair-baseline`
- Provider: `openai_compatible`
- Base URL: `https://generativelanguage.googleapis.com/v1beta/openai`
- Browser/API evidence model: `gemini-2.5-flash`
- Final gated full-chain test model: `gemini-3-flash-preview`
- API key: configured from user environment / SecretStore; not printed or persisted
- Dataset: `dataset_0002` / `profile_dataset_0002_v1`
- Prompt: `请比较 PBE 与 r2SCAN 两列原子能量数据，计算基础误差指标，并生成结果摘要。`

## Gated integration test

- Command: `python -m pytest -q -m llm_integration`
- Result before evidence capture: `2 passed`
- Final result after Gemini model selection: `1 passed, 165 deselected` with `gemini-3-flash-preview`
- Gate: requires `MDI_RUN_LLM_INTEGRATION=1` and live provider env; default CI does not set these variables.
- Safety: tests use the OpenAI-compatible provider only through the explicit live integration marker.

Latest rerun status after Gemini compatibility repair:

- `generativelanguage.googleapis.com` is now called without `response_format`, because Gemini AI Studio's OpenAI-compatible endpoint returned HTTP 400 for that field.
- A Gemini 2.5 Flash Lite full-chain attempt reached the provider but failed safely with provider-side HTTP 503.
- A Gemini 3 Flash Preview full-chain attempt passed: live provider JSON -> PlanValidator -> persisted AnalysisPlan -> `/planner/jobs` -> QueueWorkerRuntime -> Tool Registry + Adapter -> Artifact/Result.
- `antigravity-preview-05-2026` was checked after the user requested it. Gemini reports that model only supports Interactions API, so it is not compatible with the current OpenAI-compatible chat/completions provider path.
- The current Phase 9D live-provider path is verified for the OpenAI-compatible Gemini endpoint with `gemini-3-flash-preview`.

## API evidence

- API summary: `api/phase9d_api_summary.json`
- Project creation: `api/project_create_redacted.json`
- Secret creation: `api/secret_create_redacted.json`
- Dataset upload/profile: `api/dataset_upload_redacted.json`
- Provider resolve: `api/provider_resolve_redacted.json`
- Planner preview: `api/planner_preview_redacted.json`
- Planner validate: `api/planner_validate_redacted.json`
- Planner job: `api/planner_job_redacted.json`
- Events: `api/events_redacted.json`
- Tool calls: `api/tool_calls_redacted.json`
- Artifacts: `api/artifacts_redacted.json`
- Result: `api/result_redacted.json`

The API path verified live provider output parsed into a validated `AnalysisPlan`, persisted the plan, created a job bound through `jobs.plan_id`, and completed queue execution through Tool Registry + Adapter.

## Browser evidence

- Browser summary: `browser_live_summary.json`
- Provider status screenshot: `01_provider_status.png`
- Live plan preview screenshot: `02_live_plan_preview.png`
- Agent process screenshot: `03_agent_process_completed.png`
- Results/export screenshot: `04_results_export.png`
- Developer audit redacted screenshot: `05_developer_audit_redacted.png`

Browser live job:

- Job ID: `job_96fbd9a69eb645ac9d0cd441`
- Plan ID: `plan_ba087d8b351d43ddbeae6019`
- Plan hash: `971c66ba0a4fb8616a867d9928ab54e0480c79ed2528ed375e5762dbe2da4db7`
- Job status: `completed`
- Tool calls: `ml.basic_metrics`
- Artifacts: `metrics.json`, `summary.md`
- Events include: `plan.persisted`, `plan.loaded`, `data.loaded`, `tool.started`, `tool.completed`, `job.completed`

## Security and redaction

- API key is not present in screenshots.
- API key is not present in redacted JSON evidence.
- Auth token headers are not saved.
- Raw provider completion is not persisted by default.
- JobEvent, Artifact, Result, and AnalysisPlan evidence contain plan/tool provenance, not secrets.

## Known boundaries

- Production KMS/envelope encryption is still future work.
- Multi-step DAG/data-dependency scheduling is still future work.
- Worker supervision/dead-letter policy is still future work.
- Broader official pymatviz adapter coverage is still future work.
