# Phase 10M-4 Renderer Registry

Status: local implementation in progress; exact-SHA CI is pending.

## Contract

`workspace-renderer-registry.ts` is the sole application-owned renderer
registry. Each entry is keyed by exact Artifact type and Artifact version and
declares a fixed renderer contract/version, classification, component,
payload mode, heavy/WebGL flags, selection inputs/outputs, accessibility
fallback, byte/row/point caps, active-only loading, security class, and bounded
bundle members.

All current registry entries use Artifact version `1` and renderer contract
version `1.0`. Registry construction rejects duplicate or incomplete entries.
The inventory contains all 42 Artifact types in the shared Artifact enum.

## Inventory

| Artifact family | Artifact types | Renderer classification and action |
| --- | --- | --- |
| Generic plot | `plotly_json` | `PRODUCTION_ADAPTED_RENDERER`; validated Plotly plus table fallback |
| Executable/active document formats | `plotly_html`, `matterviz_html`, `report_html` | `INERT_FALLBACK`; download only |
| Static media metadata | `preview_png`, `figure_pdf`, `matterviz_snapshot_png` | `METADATA_ONLY` |
| SVG | `figure_svg` | `INERT_FALLBACK`; download only, never DOM execution |
| Structure | `structure_json` | `PRODUCTION_ADAPTED_RENDERER`; heavy WebGL |
| Trajectory | `trajectory_json` and three trajectory support artifacts | main artifact is a bundled heavy renderer; support artifacts use bounded JSON |
| Phonon | band, DOS, combined, compatibility, summary, report, manifest | band/DOS/combined use bundled validated views; support artifacts use bounded JSON |
| Phonon animation | animation, summary, manifest | main artifact is a bundled heavy WebGL renderer |
| Brillouin zone | reciprocal lattice, BZ, k-path, manifest | bundled heavy WebGL renderer |
| Volumetric | grid, payload, field, dataset, manifest, overlay | bundled heavy WebGL renderer |
| Volumetric binary | `volumetric_binary` | `METADATA_ONLY`; consumed only through a validated bundle |
| Generic numeric/table | `metrics_json`, `table_json`, `quality_issues_json` | `PRODUCTION_ADAPTED_RENDERER`; bounded semantic table |
| CSV | `table_csv` | `INERT_FALLBACK`; download only |
| Text | `summary_md`, `report_md` | `PRODUCTION_ADAPTED_RENDERER`; safe text, no raw HTML |
| Audit JSON | `recipe_json`, `analysis_plan_json` | `PRODUCTION_ADAPTED_RENDERER`; inert bounded JSON |

`table_json` may select Dataset Materials Explorer, Materials ML, or
Composition Space only after payload validation finds an exact checked-in
`schemaVersion + artifactType` product pair. Generic table behavior remains the
fallback. This is contract adaptation, not filename or MIME inference.

## Product Contract Adaptations

| Embedded product schema | Product type | Renderer |
| --- | --- | --- |
| `phase10k2.dataset_materials_explorer.v1` | `dataset.materials_explorer` | Dataset Materials Explorer |
| `phase10k4.composition_space.v1` | `dataset.composition_space` | Composition Space Explorer |
| `phase10k3.materials_ml_regression.v1` | `ml.regression_evaluation` | Materials ML Evaluation |
| `phase10k3.materials_ml_uncertainty.v1` | `ml.uncertainty_evaluation` | Materials ML Evaluation |
| `phase10k3.materials_ml_classification.v1` | `ml.classification_evaluation` | Materials ML Evaluation |

No entry grants component-name, module-path, callback, shader, HTML,
JavaScript, iframe, URL, or scientific execution authority.

## Caps

JSON payloads are capped at 16 MiB, text at 2 MiB, and bounded binary download
or volumetric bundle members at 64 MiB. Default renderer caps are 1,000 rows
and 100,000 points. Bundles contain at most 16 artifacts. Exceeding a cap is a
typed failure, not silent truncation.
