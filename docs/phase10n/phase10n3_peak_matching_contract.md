# Phase 10N-3 Peak Matching Contract

`mdi.xrd_ordered_position_match@1.0.0` constructs only candidates within an explicit finite `[0.001, 2.0] degree 2theta` tolerance. Candidates are canonically ordered by absolute position residual and exact peak identities, then greedily accepted under a strict one-experimental-to-one-theoretical constraint. Intensity is display metadata, not primary match authority.

The matcher stores signed and absolute delta 2theta, both unmatched sets, and count/fraction/MAE/RMSE/maximum/median summaries. Zero matches is a valid result. No global shift, wavelength fit, lattice fit, structure refinement, Rietveld operation or phase search occurs.
