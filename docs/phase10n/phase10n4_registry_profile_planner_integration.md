# Phase 10N-4 Registry, Profile, and Planner Integration

Registry grows exactly 57 to 60 with `trajectory.rdf@0.1.0`, `trajectory.msd@0.1.0`, and `trajectory.diffusion@0.1.0`. No fourth N4 Tool exists. Static `structure.rdf@0.1.0` remains unchanged.

DataProfile evolves additively from 2.2 to 2.3 only for deterministic trajectory readiness: resource/hash, frame and atom count, stable atom/species semantics, coordinate representation/unit/wrapping, PBC/cell mode, and explicit time facts. Profiles 2.2 and earlier remain readable; there is no migration or backfill.

Eligibility never computes RDF, unwrapping, MSD, or diffusion. Planner routes exact trajectory intents and requires an explicit diffusion fit window. AnalysisPlan 0.2 binds `trajectory.msd` output port `trajectory-msd` to `trajectory.diffusion` input port `msd`; failed MSD blocks the descendant. Persisted compatible MSD reuse requires exact Artifact identity/checksum and contract. Latest/fuzzy binding and fallback are prohibited.
