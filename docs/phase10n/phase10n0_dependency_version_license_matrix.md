# Phase 10N-0 Dependency, Version and License Matrix

Version authority is `pyproject.toml` plus `uv.lock`. The two NumPy/SciPy versions
below are lock resolution branches for Python/platform markers; they are not an
upgrade proposal.

| Dependency | Locked version | License evidence | Current use | Candidate N use | New dependency decision |
| --- | --- | --- | --- | --- | --- |
| pymatgen | 2026.5.4; core 2026.5.18 | PyPI release metadata: MIT; repository source available | structure, XRD, BZ and scientific structures | CrystalNN/VoronoiNN; theoretical/XRD; electronic consumer proposal | NO for N1/N3/N5 |
| ASE | 3.29.0 | PyPI 3.29.0 metadata: LGPL-2.1-or-later | trajectory/material parsing support | N4 optional conversion only if contract-approved | NO proposed |
| phonopy | not top-level locked | PyPI metadata identifies BSD-3-Clause for latest; exact locked release absent | bounded source wrappers and existing phonon fixtures | no new N1-N5 requirement | do not add in N0; phase-specific review only |
| spglib | 2.7.0 | PyPI release metadata: BSD-3-Clause | structure symmetry/BZ foundations | N1/N2 structure identity support | NO |
| seekpath | not top-level locked | PyPI metadata identifies MIT for latest; exact locked release absent | no top-level dependency authority found | possible N5 path normalization only if current contracts need it | NO in N0; conditional review |
| NumPy | 2.4.6 / 2.5.0 markers | PyPI release metadata: BSD-3-Clause, 0BSD, MIT, Zlib, CC0 components | all numeric adapters | N3-N5 numeric arrays | NO |
| SciPy | 1.17.1 / 1.18.0 markers | PyPI release metadata: BSD-family; bundled components require notices | existing numerical support | N3 peak detection/matching; N4 fits | NO |
| pandas | 3.0.3 | PyPI release metadata: BSD-3-Clause | tabular and semantic profiles | N3 input table handling | NO |
| Plotly | 6.8.0 | PyPI release metadata: MIT | static plot Artifacts | N3-N5 report-safe plots | NO |
| scikit-learn | 1.9.0 | PyPI release metadata: BSD-3-Clause | Materials ML evaluation | no direct N1-N5 algorithm authority | NO |
| pymatviz | 0.18.0 | lock records version; PyPI license field not machine-declared in audit | existing XRD/RDF/phonon visualization adapters | no N1-N5 scientific authority | NO; verify upstream notice before redistribution |
| Three.js | 0.185.1 | package is MIT-licensed in the existing frontend dependency policy | M4 heavy Viewers | N1/N2 overlay and N5 BZ linkage consumers | NO |

## License and upstream limits

The online official-upstream lookup tool returned HTTP 404 in this run. License values
above are bounded to PyPI release metadata and the repository lock. `pymatviz` has no
machine-readable license field in the inspected release metadata, so its exact upstream
notice remains a release-audit prerequisite before any N phase ships it. No dependency
was installed, upgraded, or placed in the lock.

## Runtime and browser impact

All candidate numeric computation remains server-side in a registered Adapter. The
browser may consume inert validated numeric/display payloads and render them, but it may
not import scientific libraries, recompute values, execute files, or call external
scientific services. N1-N5 do not require a new browser dependency under this proposal.
