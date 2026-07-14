# Phase 10H-5 Animation Contract

## Schemas

- `phase10h5.phonon_animation.v1`
- `phase10h5.phonon_animation_summary.v1`
- `phase10h5.phonon_animation_manifest.v1`
- `phase10h5.phonon_animation_recipe.v1`

The package is closed and declarative. It binds the exact canonical structure, source band hash, eigenvector-set hash, complete selected H4 eigenvector, mode reference, renderer-local supercell, display state, playback defaults, caps, warnings, security, and provenance. It contains no frame array, code, HTML, callback, shader, module, URL, texture, or external asset.

The selected mode is a 64-character canonical `mode_id`; frequency alone is never accepted. Compatibility validates structure identity, species and canonical atom order, band/eigenvector hash, q-point, branch, frequency tolerance, NAC, normalization, mass weighting, finite complex shape, and caps before artifacts are written.

The four output artifact types are `phonon_animation_json`, `phonon_animation_summary_json`, `phonon_animation_manifest_json`, and `recipe_json`. The manifest states that the renderer is not embedded and is application-owned.
