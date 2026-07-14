# Phase 10H-4 Complex Representation

Complex vectors use one record per atom with `real[3]` and `imag[3]`. Components
are finite JSON numbers in Cartesian xyz order. Complex strings, Python repr,
untyped nested arrays, NaN, Infinity, real-only truncation, and component-wise
phase changes are rejected. Shared schema names are
`phase10h.complex_scalar.v1` and `phase10h.complex_vector3.v1`.
