# Phase 10N-3 Workspace, Selection and Interpretation

The active-only Workspace renderer presents an accessible experimental line, theoretical sticks, peak markers, matched and unmatched tables, residual summary, warnings and provenance. It consumes persisted values and performs no scientific recomputation. Display series are bounded to 50,000 points.

Selection 1.0 additively supports `EXPERIMENTAL_XRD_PEAK`, `THEORETICAL_XRD_PEAK` and `XRD_MATCH`, each bound to Project/Job/Artifact/checksum and exact source identities. The projector exposes only bounded counts, wavelength, tolerance and residual summaries. Reports retain limitations; Recipes remain declarative and non-executable.
