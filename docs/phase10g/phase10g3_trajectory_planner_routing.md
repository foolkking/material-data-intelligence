# Phase 10G-3 Trajectory Planner Routing

Mock Planner selects `structure.trajectory_viewer` only when a normalized trajectory exists and the prompt explicitly requests playback, a trajectory viewer, frame-by-frame inspection, or atomic motion. English and Chinese cases are covered.

The emitted AnalysisPlan has one strict viewer step, one trajectory input reference, the exact four artifact types, and application-owned defaults. PlanValidator rejects unknown options, dynamic bond flags, editing flags, external frame references, arbitrary renderer config, unsupported speed, and over-limit supercells with `PARAMS_SCHEMA_INVALID`.

RDF, diffusion/MSD/VACF, velocity distribution, dynamic-bond inference, editing/trim/merge, comparison/clustering, and video prompts do not route to the viewer. Static structure intent still selects `structure.viewer_3d`; trajectory intent never selects the static tool.

The service-backed integration gate executes the formal trajectory job through PostgreSQL, Redis, MinIO, QueueWorkerRuntime, Tool Registry, and the adapter. Browser renderer availability remains independent from backend job success.
