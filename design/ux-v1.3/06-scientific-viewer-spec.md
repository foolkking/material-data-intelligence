# Scientific Viewer Specification

## Viewer capability and design matrix

| Type | Current code reality | Prototype treatment | Production implication |
| --- | --- | --- | --- |
| Tabular materials data | EXISTS_IN_CODE | large table, units, search/filter/columns, selected row Inspector | reuse/standardize viewer shell |
| Composition / properties | EXISTS_IN_CODE | property table and result scatter | preserve scientific labels and units |
| Structure | EXISTS_IN_CODE | large 3D-style structure canvas, site selection, Inspector | reuse renderer after shell decoupling |
| Trajectory | EXISTS_IN_CODE | canvas + factual frame/footer control | renderer exists; playback state must map to real frame data |
| XRD | EXISTS_IN_CODE | plot, peak selection, source Inspector | viewer-specific chrome |
| RDF/MSD/diffusion | EXISTS_IN_CODE | plot-family treatment, not separately visualized in fixture | reuse after viewer shell alignment |
| Band + DOS / electronic | EXISTS_IN_CODE | paired scientific plot in one object surface | reuse renderer after shell decoupling |
| Phonon / Brillouin zone | EXISTS_IN_CODE | viewer-family treatment, not separately visualized in fixture | verify exact renderer controls |
| Volumetric | EXISTS_IN_CODE | large scalar-field stage + legend/status | preserve WebGL presentation boundary |
| ZIP detected content | PARTIAL | detected-resource list, no fabricated file tree | backend parser/resource inventory determines final UI |
| Generic unsupported file | EXISTS_IN_CODE | readable unsupported state | preserve original file context/recovery |

Evidence: `docs/phase12/evidence/phase12_0_current_ux_reality/scientific_viewer_matrix.json` lists existing viewer capability classes. UX-V1.3 does not expand backend parser support.

## Common viewer chrome

```text
Viewer toolbar: selected object name | Project Data | local commands | Inspector
Viewer main: object-specific primary surface
Viewer footer: factual context, units/legend/frame, scoped controls
```

The chrome is shared, not the canvas. A table needs column work; a structure needs selection; XRD needs axis/peak context; a volume needs scale; archive needs proven detected content.

## Selection contract

Viewer selection emits a scientific object identity (row/sample, site, peak, artifact point) to Inspector. Inspector then presents:

1. **详情**: immediate scientific properties.
2. **依据**: the source row/resource/object relationship.
3. **来源与过程**: progressively disclosed input/tool/output lineage.

Current selection/evidence capabilities are reusable in part; browser shell restructuring must not invent selection identity or provenance beyond backend facts.

## Archive decision

The design label is **Detected content**, not “archive tree”. A ZIP can only show individual resources, nested folders, or multi-resource analysis eligibility when parser/resource runtime facts prove them. The prototype explicitly communicates this gap.
