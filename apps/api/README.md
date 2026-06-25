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
