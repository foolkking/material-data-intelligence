# Phase 10H-4 Normalization

The stored representation is `mass_weighted_eigenvector` with
`euclidean_unit_norm`: `sum_i |e_i|^2 = 1` within `1e-9`. This is distinct from
real-space displacement normalization and display amplitude. Source vectors are
normalized once at the approved boundary; validators do not silently repair
persisted values.
