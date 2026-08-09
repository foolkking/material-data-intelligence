# Phase 10N-5 Band Gap Classification Contract

`mdi.supplied_band_gap_scan@1.0.0` uses complete supplied occupations when available,
otherwise explicit supplied Fermi energy. VBM is the maximum occupied sampled state and
CBM the minimum unoccupied state. Ties sort by spin, k-point ID and band ID; direct means
the same exact k-point. Fermi crossing or gap <= `1e-5 eV` is
`METAL_LIKE_UNDER_POLICY`; larger gap is `NONZERO_GAP_UNDER_POLICY`; insufficient
authority is `CLASSIFICATION_UNAVAILABLE`. Results describe supplied sampled data only.
