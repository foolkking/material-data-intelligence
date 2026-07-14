# Phase 10H-3 Combined API Evidence

`scripts/generate_phase10h3_phonon_band_dos_evidence.py` creates a mock-planner
request, validated AnalysisPlan, queued runtime execution, persisted artifact
listing, deterministic replay, and incompatible-job rejection. No real LLM or
external service is called.

The browser runner consumes those persisted payloads through the local
PlannerWorkbench API surface and validates them before Plotly. Captures include
job/events/tool calls/artifacts, hashes, compatible/convertible/incompatible
cases, and no-partial-artifact evidence.
