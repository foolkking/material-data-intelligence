# Normalization and Artifacts

All parser output passes the Phase 10G canonical validator. Equal frame lattices become fixed mode; otherwise every lattice is retained as variable mode. Coordinates are not wrapped, fractionalized, interpolated, or inferred. Missing physical time never becomes simulated time.

`phase10g.trajectory_parse_report.v1` records format, counts, modes, detected properties, approved conversions, ID reorder, bounded warnings, input SHA-256, and determinism without raw source content or paths.

The canonical manifest hashes trajectory and summary, its non-circular data dependencies. Parse report and manifest are separately represented by artifact listing/metadata; a manifest cannot safely include its own hash. Four unique shared artifact types prevent artifact-ID collision.
