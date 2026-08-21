# Result, Inspector, and Report Specification

## Result format

```text
Scientific Result
  title
  data/sample context
  main Figure
  caption + units + scope
  Key Finding
  Limitation
  supporting Figure/table
  Analysis method
  Evidence
  Source & process
```

The primary result is a readable scientific document, not a collection of metric cards. Main Figure is visually largest; lower material is evidence/support.

## Finding language

- **Observation:** directly states what the selected samples/figure show.
- **Interpretation:** explicitly bounded by available data and analysis method.
- **Limitation:** visible below the finding, not a hidden disclaimer.
- **Unsupported inference:** never promoted to a finding.

## Language policy in scientific reading

Result, Inspector and Report chrome uses Simplified Chinese: **科学结果**, **主要发现**, **局限性**, **依据**, and **来源与过程**. Formulas, units, source property names, filenames, and published scientific abbreviations remain canonical. Raw identifiers and execution contracts are deeper technical disclosure, never result-page furniture.

## Inspector

- Default width: `344px` desktop, target range `320-360px`.
- Opens from a table row, scatter point, structure site, or XRD peak.
- Contextual rather than global: object selection decides content.
- Header: `详情`; sections: `详情`, `依据`, `来源与过程`.
- The inspector is dismissible and never becomes a required top-level Workspace tab.
- On narrow mobile it becomes a full-width lower/side sheet with Escape/close and restored focus.

## Report

Current architecture is naturally **Run Report**. The Reports page therefore lists run-level documents and the reader includes run scope, main Figure, methods/limitations, and source/process. A cross-run aggregate Project Report is **REQUIRES_NEW_BACKEND_CAPABILITY** and is intentionally not represented as a current product feature.

## Evidence path

```text
selected scientific object / plot point / site / peak
  -> Inspector details
  -> evidence source
  -> source and process lineage
```

The Project/Workspace terminology boundary is kept invisible in the default path. Deep technical lineage exists only in the last disclosure layer for expert/audit use.
