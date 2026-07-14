# Phase 10H-5 Displacement and Supercell Policy

For canonical mass-weighted eigenvectors, animation uses:

```text
u(l,kappa,phase) = display_scale / envelope
  * Re[(e_kappa / sqrt(m_kappa)) * exp(i*(2*pi*q.R_l + phase))]
```

`envelope` is the maximum per-atom complex norm after mass unweighting and is fixed for the mode. It is not recomputed per frame. Therefore phase nodes may have zero displacement, `u(phase+2*pi)=u(phase)`, and a real eigenvector moves sinusoidally rather than at constant magnitude. Global phase remains artifact-canonical; the UI changes only viewer phase.

Gamma replicas share phase. Non-Gamma uses exact reciprocal-fractional `2*pi*q.cell_image`. V1 supports deterministic positive diagonal supercells with each axis in `1..3`; a q component must be rational within `1e-8` with denominator at most three. A requested manual repeat must satisfy integer `q_i*n_i`. General integer matrices and noncommensurate approximation are rejected.

Caps are 512 canonical atoms, 768 displayed atoms/vectors, three cells per axis, 32 trail points, and 16 MB artifact JSON. Supercells remain renderer-local and never become structures or persisted animation frames.
