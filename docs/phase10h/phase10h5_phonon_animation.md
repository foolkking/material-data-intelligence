# Phase 10H-5 Phonon Animation

## Result

`phonon.animation` is the single formal dynamic phonon visualization tool. It consumes exactly one role-bound canonical structure, `phase10h.phonon_band.v1`, and `phase10h.phonon_eigenvector_set.v1`. PlanValidator, persisted AnalysisPlan, QueueWorkerRuntime, and `PhononAnimationAdapter` emit an inert animation package, summary, manifest, and recipe.

The package stores no generated frames. The application-owned Three.js viewer reconstructs one phase snapshot from the validated complex eigenvector, updates existing instanced atom matrices, and keeps periodic identity as `siteIndex + imageOffset`. It reuses the static/trajectory renderer engine rather than creating a second WebGL lifecycle.

## Product

- Default state is paused; autoplay is false.
- Controls cover play/pause, phase, display scale, speed, vectors, bounded trails, bonds, cell, and camera reset.
- Exact mode binding uses band hash, q-point, branch, frequency, structure identity, atom order, and optional NAC direction.
- Band handoff is enabled only when the artifact hash and full mode reference match. No nearest-frequency search occurs.
- Invalid, incompatible, over-cap, unsupported-WebGL, initialization, frame-update, and context-loss states preserve inert JSON.
- Reduced-motion users receive a paused fixed-phase preview.

## Boundaries

This phase visualizes approved eigenvectors; it does not calculate phonons, force constants, thermal amplitudes, Raman/IR/neutron intensity, or trajectories. Animation display scale is not physical amplitude. Imaginary modes are unstable-direction phase morphs, not stable time oscillations.

See the adjacent contract, mathematics, renderer, security, evidence, and readiness documents. Replay with:

```bash
uv run python scripts/generate_phase10h5_phonon_animation_evidence.py
node apps/web/test/phonon-animation-browser-evidence.mjs
```
