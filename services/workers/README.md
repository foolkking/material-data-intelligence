# Worker service

MDI runs one project-owned RQ worker process with six logical queues:

1. orchestration
2. planning
3. execution
4. result projection
5. interpretation
6. report

The worker executes only registry-approved adapters and persists state through the API/application repositories. Queue ownership, leases, cancellation, timeout recovery and publication fencing are database-authoritative. A process that exists without a ready queue registration is not healthy.

Use the repository controller so the worker receives the same external runtime environment as the API:

    .\scripts\dev.ps1 status
    .\scripts\dev.ps1 restart -Scope app

Do not start a second worker against the project Redis instance during normal development. Keep the running worker and user browser available across work rounds.
