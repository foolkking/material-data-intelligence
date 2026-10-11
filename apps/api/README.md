# API application

The FastAPI boundary owns authentication, projects and datasets, scientific object versions, Research admission/planning, result and interpretation reads, report generation requests, model settings and administrative routes.

The API does not execute arbitrary model output. Research plans are checked against the active Tool Registry and requirement schemas; long work is queued for the project Worker. PostgreSQL is authoritative for workflow state and ownership, while MinIO stores immutable payloads and report artifacts.

Run the complete local stack from the repository root:

    .\scripts\dev.ps1 start

For a direct development process, load the external local.env and set the repository package paths before using uvicorn. Do not point tests or ad-hoc processes at the real service credentials. Model connections are configured through the authenticated settings API; keys are write-only to the browser and encrypted server-side.
