# Viewer Scene Artifact

## Input
- source resource: normalized_object
- parser: pymatgen.Structure
- formula: H2
- site count: 2
- species count: 1

## Scene
- contract version: viewer_scene.v2
- coordinate basis: cartesian_angstrom
- site count: 2
- periodic bond count: 1
- cross-boundary bond count: 1
- bond source policy: distance_cutoff
- bond topology authoritative: false
- lattice included: True
- cell expansion: [1, 1, 1]

## Caps and Warnings
- max sites: 256
- max bonds: 2048
- max species: 32
- truncation status: False
- warnings: VIEWER_SCENE_BONDS_NON_AUTHORITATIVE

## Preview
- inert JSON preview supported
- validated client renderer supported
- renderer code is not embedded in this artifact

## Security
- no artifact JavaScript
- no HTML payload
- no external URLs
- no remote textures
- no renderer bundle or executable asset in the artifact

## Deferred
- CrystalNN/VoronoiNN authoritative coordination
- bond order and valence
- trajectory and phonon animation
