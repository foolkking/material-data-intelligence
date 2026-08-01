# Workspace Artifact Renderer Matrix

The table groups the complete shared Artifact enum by contract family. Producer detail is taken from the current 53-tool Registry inventory.

| Artifact contract family | Representative producers | Media | Identity | Existing renderer | Fallback / large data | Cross-selection | Evidence | Report | Workspace readiness |
|---|---|---|---|---|---|---|---|---|---|
| `plotly_json` | composition, viz, ML, XRD/RDF, phonon | JSON | tool/job/artifact hash; product-specific payload identity | product-specific panels or generic metadata | raw JSON; bounded artifact API | product-local | no generic projector | downloadable/reference | REUSABLE_FOUNDATION |
| `plotly_html` | composition, viz, ML | HTML artifact | artifact hash | not executed as authority | download/static metadata | none | unsupported | reference only | CONTRACT_UNSUPPORTED for inline panel |
| `preview_png`, `figure_svg`, `figure_pdf` | visualization/export producers | image/vector | artifact hash | image/download where present | metadata/download | none | unsupported | selectable static figure | PARTIAL |
| `matterviz_html`, snapshots | legacy trajectory/structure producers | HTML/PNG | artifact hash | current formal viewers use application-owned renderers | no artifact script authority | none | unsupported | legacy reference | LEGACY_READ_ONLY |
| `structure_json` | structure summary/viewer tools | JSON | object/resource/site identity | validated static/Three.js viewer | JSON fallback; bounded site/bond caps | exact site identity locally | structure summary only | reference/selectable panel | READY family |
| trajectory JSON/report/manifest | trajectory import/viewer | JSON | trajectory, atom, frame, resource hash | validated trajectory viewer | lazy bounded frame payload/cache | atom/frame locally | unsupported | reference/selectable panel | READY family |
| phonon band/DOS/combined/animation | phonon tools | JSON | structure, q-point, branch, mode, source hash | dedicated plots/animation | bounded tables/JSON | exact Band/BZ local link | band/DOS/combined projectors | reference/selectable panel | READY family |
| reciprocal/BZ/k-path/manifest | `structure.brillouin_zone` | JSON | reciprocal point/segment/path variant | application-owned BZ renderer | JSON/text fallback | exact Band/BZ local link | unsupported | reference/selectable panel | READY family |
| volumetric grid/payload/field/dataset/manifest/overlay | `structure.volumetric_data` | JSON plus binary | field/resource/grid/content hash | isosurface, slice, direct volume | metadata first; bounded byte loading/worker | field and local probe only | field projector | reference/selectable panel | READY family |
| `metrics_json` | ML metrics/error tools | JSON | target/model/sample scope | metrics panels | numeric fallback | product-local | basic metrics projector | selectable finding/table | READY family |
| `table_json`, `table_csv` | dataset/table/ML/structure/composition/phonon | JSON/CSV | contract-specific row/sample IDs | dataset/ML/table/product panels | paginated table/JSON/download | exact only where contract carries IDs | selected exact projectors | selectable table | REUSABLE_FOUNDATION |
| `quality_issues_json` | dataset explorer | JSON | dataset/profile issue refs | dataset quality UI | JSON fallback | dataset scope | carried through dataset projector payload | warning source | READY family |
| `summary_md` | many tools | Markdown text | artifact only | inert `<pre>` preview | text cap/download | none | explicitly untrusted | static source only | DISPLAY_ONLY |
| `report_md`, `report_html` | platform report | Markdown/HTML | Report/job/version | Markdown text preview; HTML not executed | download | claim/panel refs absent | no projector | first-class Report source | PARTIAL |
| `recipe_json` | most executable tools/platform recipe | JSON | job/plan/tool versions | inert Recipe preview | JSON fallback/download | none | unsupported | Recipe source | PARTIAL |
| `analysis_plan_json` | platform plan export | JSON | planId/hash/schema | plan UI/raw audit | JSON fallback | step identity | provenance only | provenance | READY foundation |

## Renderer authority

**REVIEWER-SEALED RECOMMENDATION**

Phase 10M registers renderer descriptors by exact Artifact type, contract family, and version. Unknown or unsupported contracts render metadata, provenance, a safe bounded JSON/text disclosure, and download eligibility. Generic fallback is never labeled a scientific panel.

No renderer executes artifact HTML, JavaScript, shader, module, callback, iframe source, external URL, filesystem path, or bucket key.
