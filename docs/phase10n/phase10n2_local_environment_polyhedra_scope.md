# Phase 10N-2 Scope: Local Environment + Coordination Polyhedra

Status: `REVIEWER_GATE / NOT QUEUED / NOT EXECUTABLE`.

N2 consumes exact N1 neighbor Artifacts through AnalysisPlan 0.2. It may not rerun or
guess neighbors in the browser. Proposed tools are `structure.local_environment` and
`structure.coordination_polyhedra`.

`phase10n2.local_environment.v1` records central/neighbor identities, reference geometry
ID/version, class/score, coverage and unsupported reasons. `phase10n2.polyhedron.v1`
records exact vertices/faces, periodic images, geometry reference, distortion metric
definition/version, numeric metrics, coverage and warnings. Reference geometries and
distortion formulas must be explicitly versioned; "environment" is algorithm-classified,
not chemically proven.

Workspace products are per-site environment tables, polyhedron overlay, distortion
metrics and Inspector detail. Cross-selection is by exact structure/site/neighbor
identity. Static table/figure fallback is mandatory. Projectors expose only computed
class, score, metrics, coverage and limitations.

Caps: 5,000 centers, 64 vertices and 128 faces per polyhedron, 32 classes and 10,000
overlay objects. Degenerate geometry, missing N1 dependency, unsupported disorder,
nonfinite metric and cap errors are typed.

Bond-valence analysis and oxidation-state inference remain out of scope. ChemEnv may be
evaluated as an algorithm source only after locked-version/license/fixture review; its
current registry mapping is not scientific product authority. No new dependency, API,
table or migration is proposed.
