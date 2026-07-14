# Phase 10H-1 Phonon Band API Evidence

`scripts/generate_phase10h1_phonon_band_evidence.py` creates a real mock-planner
job, persists its validated AnalysisPlan, executes `phonon.band` through
`QueueWorkerRuntime`, retrieves tool calls and seven artifacts, and repeats the
run to compare deterministic payloads. No real LLM or network is used.

`apps/web/test/phonon-band-browser-evidence.mjs` serves the real frontend and
replays those live adapter artifacts through local API routes. It records
stable, imaginary, discontinuous, over-preview-budget, invalid, mobile, and
three-browser cases in the Phase 10H-1 evidence directory.
