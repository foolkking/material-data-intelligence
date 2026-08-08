# Phase 10N-2 Local Environment And Polyhedra Contract

`structure.local_environment_polyhedra@0.1.0` consumes one immutable periodic
Structure and one exact persisted N1 coordination Artifact. The single production
payload is `phase10n2.local_environment_polyhedra.v1`; summary and Recipe exports are
non-authoritative projections of that payload.

The Adapter never discovers neighbors. It reconstructs Cartesian neighbor vectors only
from exact N1 relation identities, site indices and periodic images against the exact
bound Structure. It validates N1 distances within `1e-6 angstrom` and rejects identity,
checksum, contract, producer or structure mismatches.

The classification algorithm is `mdi.angular_spectrum_reference_match@1.0.0`; scientific
faces use locked `scipy.spatial.ConvexHull@1.17.1`. DataProfile stays at 2.1. Generic
Artifact persistence and AnalysisPlan 0.2 dependency authority are reused.
