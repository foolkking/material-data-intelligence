# Phase 10N-0 DataProfile, Registry, Planner and Contract Audit

## Current facts

- `DataProfile` currently emits `profileContractVersion: 2.0`, resource semantics,
  analysis readiness, sample identity and bounded coverage.
- Current resource kinds include structure, trajectory, phonon, reciprocal-space and
  volumetric needs. Electronic and experimental-XRD readiness are not production facts.
- Tool Registry version `0.1.0` currently contains 53 tools. N1-N5 proposed tools are
  absent. Registered Adapters, not Viewer components, are execution authority.
- AnalysisPlan 0.1 and bounded dependency-aware 0.2 are sufficient for the proposed
  N1-N5 compositions. No generic DAG extension is proposed.

## Profile proposal

| Capability | Existing fact | Additive fact proposal | Ambiguity outcome | Profile version proposal |
| --- | --- | --- | --- | --- |
| N1/N2 | periodic structure, lattice, sites, species/occupancy | stable structure/site identity, disorder and coordinate-basis readiness | `INELIGIBLE_AMBIGUOUS_SEMANTICS` | DataProfile `2.1` proposal owned by N1; backward-compatible additive |
| N3 | structure and tabular resource semantics | experimental-XRD kind, axis/intensity columns, units, wavelength, theoretical binding | reject missing wavelength/unit | same additive 2.1 proposal, N3 fields optional |
| N4 | trajectory resource, frame/atom/cell/time summary | identity continuity, wrapping, time unit, constant-count/species and variable-cell facts | reject or limited status | same additive 2.1 proposal, N4 fields optional |
| N5 | no formal electronic readiness | band/DOS resource, energy unit/reference, spin, path, projection completeness | unsupported or ambiguous | same additive 2.1 proposal, N5 fields optional |

This proposal requires no database migration because Profile JSON is already versioned
and persisted generically. It requires a future shared contract/schema update in N1 and
additive fact producers in their owning phases. Historical 2.0 Profiles remain readable;
missing facts make new tools ineligible, not silently inferred.

## Proposed tool and dependency map

| Phase | Proposed Tool IDs (not registered) | Plan model |
| --- | --- | --- |
| N1 | `structure.coordination_crystalnn`, `structure.coordination_voronoinn`, `structure.coordination_compare` | 0.1 independent or 0.2 compare dependency |
| N2 | `structure.local_environment`, `structure.coordination_polyhedra` | 0.2 depends on exact N1 neighbor Artifact |
| N3 | `xrd.experimental_pattern`, `xrd.peak_match` | 0.2 theoretical-XRD + experimental normalization/matching |
| N4 | `trajectory.rdf`, `trajectory.msd`, `trajectory.diffusion_fit` | 0.1 independent or 0.2 exact trajectory-derived dependencies |
| N5 | `electronic.band_structure`, `electronic.dos`, `electronic.band_dos` | 0.1 standalone or 0.2 combined-view dependency |

Final IDs/versions are `REVIEWER_DECISION_REQUIRED`. Each future Registry entry must
declare input kinds, Profile prerequisites, collision group, ranking hints, strict params,
outputs, cost/timeout/caps and no permissions beyond inert resource reads and Artifact
writes. Eligibility separates data readiness, platform availability and scientific
validity and returns current repository-convention typed reasons rather than keyword-only
selection.

## Database/API/dependency matrix

| Phase | New dependency | Lockfile | New contract | Profile | New public API | Table/migration | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| N1 | NO | NO | YES_PROPOSED_FOR_REVIEW | 2.1 additive proposed | NO | NO | use pymatgen |
| N2 | NO | NO | YES_PROPOSED_FOR_REVIEW | reuse 2.1 | NO | NO | consume N1 Artifact |
| N3 | NO | NO | YES_PROPOSED_FOR_REVIEW | add optional 2.1 facts | NO | NO | use SciPy/NumPy |
| N4 | NO | NO | YES_PROPOSED_FOR_REVIEW | add optional 2.1 facts | NO | NO | use NumPy/SciPy |
| N5 | NO | NO | YES_PROPOSED_FOR_REVIEW | add optional 2.1 facts | NO | NO | consume pymatgen MSON/JSON subset |
| N6 | NO | NO | NO | NO | NO | NO | integration/evidence only |

No implementation-critical `TBD` remains: all proposed changes have a phase owner and
reviewer gate.
