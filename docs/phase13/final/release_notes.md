# Initial Release Notes

## What shipped

The Initial Release provides seven canonical workflows: dataset intelligence and composition space; materials ML evaluation; structure, coordination, local environment, polyhedra, and experimental XRD; trajectory RDF/MSD/diffusion; supplied typed phonon Band/DOS plus Brillouin zone; volumetric visualization; and electronic Band/DOS.

The canonical path is DataProfile -> AnalysisIntent -> EligibilityResolution -> capability-aware Planner -> AnalysisPlan -> PlanValidator -> QueueWorkerRuntime -> registered Adapter -> persisted Artifact -> Grounded Interpretation -> ScientificWorkspace -> Report -> declarative Recipe.

Scientific computation authority belongs to registered Adapters and persisted Artifacts. The LLM is a Planner/Router/Explainer, not a scientific executor. Artifacts are inert data, Reports compose persisted facts, and Recipes are non-executable.

Typed PhononBand and PhononDos imports are `SUPPORTED_WITH_LIMITS`; generic phonon YAML/JSON remains `MAPPING_ONLY`. Workspaces use one Workspace per Job, a 32-panel cap, and Artifact Gallery reachability rather than one panel per Artifact.

Release acceptance tested Chromium, Firefox, WebKit, Chromium 390x844, PostgreSQL, Redis, MinIO, Linux invariant replay, and Windows invariant replay. These results do not imply universal browser certification or independent cross-platform numeric validation.

See [Known limitations](known_limitations.md), [Reproducibility](../reproducibility/README.md), [Security](../release/security.md), and the [Claim matrix](release_claim_matrix.md).
