# Phase 10H-4 Displacement Reconstruction

For canonical mass-weighted vector `e_i`, display direction is
`u_i=e_i/sqrt(m_i)`. At reciprocal-fractional q and integer cell image `R`, a
static phase snapshot uses
`Re[u_i exp(i(2*pi*q.R + phase))]`. Gamma single-cell and non-Gamma image phase
are therefore unambiguous. This helper returns displacement vectors only; it is
not a trajectory, time integrator, animation, or scientific amplitude model.
