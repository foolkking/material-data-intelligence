# Phase 10N-4 Time, Cell, PBC, and Unwrapping Contract

Canonical time is picosecond; accepted source units are femtosecond and picosecond through deterministic conversion. MSD requires finite, strictly increasing, constant-step physical time. Missing or irregular time is ineligible for production MSD and diffusion; RDF may use exact frame windows without physical time.

RDF supports fixed cells and per-frame variable cells when every cell is finite and nonsingular and the requested radius is safe in every included frame. MSD and diffusion require a fixed cell. Cell equality tolerances are absolute `1e-8 angstrom` and relative `1e-8`.

Wrapped MSD input is unwrapped server-side by `mdi.fixed_cell_fractional_minimum_image@1.0.0`: Cartesian positions are mapped to fixed-cell fractional displacement, nearest periodic images are applied only on enabled PBC axes, and accumulated displacement is mapped back to Cartesian coordinates. A post-wrap fractional component with magnitude at least `0.49` is `UNWRAPPING_AMBIGUOUS`; no coordinate perturbation or fallback is allowed. Unwrapped input remains unchanged. Frontend and Viewer unwrapping are prohibited.
