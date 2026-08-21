# API App

FastAPI application boundary for the Material Data Intelligence platform.

Current Phase 1 scope:

- `mdi_api.main:create_app()` builds the API app.
- `/health`, `/auth/me`, `/projects`, `/datasets`, `/tools`, and `/tools/mvp`
  establish module boundaries for later persistence-backed implementations.
- `mdi_api.db.metadata` defines the first Auth / Project / Dataset tables:
  `users`, `organizations`, `projects`, `project_members`, `datasets`, and
  `files`.

Local run:

```powershell
uvicorn mdi_api.main:app --reload
```

For the optional live Planner/Interpretation provider, either set the built-in
server profile (`MDI_LLM_PROVIDER=deepseek`, `DEEPSEEK_KEY`, and an allowlisted
`DEEPSEEK_MODEL`) or configure an OpenAI-compatible connection from the
authenticated Model Settings dialog. The dialog writes to
`POST /planner/providers/configure`, discovers models with
`GET /planner/providers/{provider}/models`, and saves the selected model group
with `PATCH /planner/providers/{provider}/models`. API keys are write-only from
the browser and encrypted server-side; they are never returned to the browser,
prompt, Artifact, Report, or export. Set `MDI_PROVIDER_ENCRYPTION_KEY` to a
stable Fernet key when configured connections must survive API restarts.
