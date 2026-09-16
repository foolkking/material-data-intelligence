# M3 attempt-02 — targeted closeout

- Preserve sealed M3 attempt-01.
- First diagnose the 4096-atom RDF failure; do not call it fairness starvation.
- Select an accepted, supported heavy workload that passes alone before F12.
- Correct fairness bounds: queued RDF Research = 34.9059 s; local no-provider = 0.25 s.
- Execute valid F12 normal+heavy and heavy+heavy only after solo heavy control.
- Execute controlled F09 429/timeout/exhaustion through the real provider path, with bounded backoff/jitter/concurrency evidence.
- Execute five bounded capacity-release cycles, project active-limit release, and double-release race where applicable.
- Add truthful task health/user-state evidence and browser evidence only if genuinely available.
- Preserve six queues, M0/M1/M2 and attempt-01 exact hashes. No M4.
- Before process changes, revalidate PID/start/cmd/cwd/PPID/role/namespace; stop only owned processes and verify release.
- No shared-service stop/flush, no user data, no arbitrary public-limit uplift.
