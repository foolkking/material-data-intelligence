# Phase 10H-2 Phonon DOS

Phase 10H-2 promotes the unique `phonon.dos` entry to an MVP static product.
It accepts one approved `PhononDos` object, executes through validated
AnalysisPlan, Tool Registry, and QueueWorkerRuntime, and persists seven inert
JSON artifacts.

The flow is `PhononDos -> phonon.dos -> phase10h.phonon_dos.v1 -> artifact
storage -> independent TypeScript validation -> local Plotly/table/JSON`.
Approved inputs are canonical JSON and bounded phonopy total/projected text
wrappers with explicit structure, units, normalization, projection identity,
broadening, and source metadata. The adapter never runs phonopy or guesses
columns.

The stable DOS contract is unchanged. DOS-only products use additive
`phase10h2.phonon_dos_summary.v1` and
`phase10h2.phonon_dos_manifest.v1` because the stable family contracts require
a real band. No synthetic band is generated. Combined views, eigenvectors,
animation, thermal properties, calculations, and remote inputs remain deferred.
