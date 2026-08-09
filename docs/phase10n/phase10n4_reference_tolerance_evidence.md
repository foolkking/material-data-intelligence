# Phase 10N-4 Reference and Tolerance Evidence

Reference fixtures are `SYNTHETIC_CONTROLLED` and include fixed periodic lattice RDF, species-pair/window cases, positive/negative/multiple boundary crossings, partial PBC, stationary motion, constant-velocity ballistic motion, isotropic and anisotropic random walks, species-separated motion, missing time, variable cell, short fit, poor fit, and checksum/foreign/stale rejection.

Exact equality applies to trajectory/frame/atom/species identity, PBC vector, Artifact checksum, Tool/version, parameter hash, selection identity, and dependency binding. Numeric tolerances are quantity-specific: cell `atol=1e-8 angstrom`, `rtol=1e-8`; unwrapped coordinates `1e-10 angstrom`; RDF bin edges `1e-12 angstrom`; `g(r)` `rtol=1e-9`, `atol=1e-12`; MSD `rtol=1e-9`, `atol=1e-12 angstrom^2`; OLS slope/intercept/D `rtol=1e-9`; R-squared/alpha `atol=1e-9`. These tolerances do not participate in identity or delete unexpected data.
