# Phase 10E-5 API Transcript

## Service Mode
- Planner: deterministic mock planner, no real LLM.
- Execution: in-memory persisted AnalysisPlan plus QueueWorkerRuntime.
- Artifact storage: temporary local runtime directory copied into evidence artifacts.
- Tool: `structure.xrd`.

## Successful Cases
- simple_cubic_cif (small CIF): job `job_9fe50c27dfb44879938d57ac`, plan `plan_193fd7ceb30640cdb84a760f`, selected `structure.xrd`, artifacts recipe.json, summary.md, xrd_pattern.json, xrd_plot.json, peaks 6.
- nacl_poscar (small POSCAR): job `job_93f51bf2b4dc44c395a39bb2`, plan `plan_882e2350b54b4db7b3aa9ee6`, selected `structure.xrd`, artifacts recipe.json, summary.md, xrd_pattern.json, xrd_plot.json, peaks 23.
- generated_structure_json (generated pymatgen Structure JSON): job `job_f90cb1c843304aabb19eb1ab`, plan `plan_4c542c1dd6a54b189a0cda73`, selected `structure.xrd`, artifacts recipe.json, summary.md, xrd_pattern.json, xrd_plot.json, peaks 18.

## Negative Routing
RDF, coordination histogram, full viewer, WebGL, Brillouin zone, phonon, experimental fitting, Rietveld refinement, Voronoi, and CrystalNN prompts did not select `structure.xrd`.
