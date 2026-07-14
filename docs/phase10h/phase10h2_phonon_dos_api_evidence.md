# Phonon DOS API and Browser Evidence

`scripts/generate_phase10h2_phonon_dos_evidence.py` creates a real Mock Planner
plan, runs QueueWorkerRuntime twice, retrieves persisted artifacts, and verifies
determinism plus canonical/static-source/invalid cases.

`apps/web/test/phonon-dos-browser-evidence.mjs` consumes the live artifacts in
PlannerWorkbench and records Chromium, Firefox, WebKit, mobile, accessibility,
degraded, invalid, console, network, screenshots, metrics, and hashes under
`evidence/phase10h2_phonon_dos/`.
