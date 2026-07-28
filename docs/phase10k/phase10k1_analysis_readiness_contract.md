# Phase 10K-1 Analysis Readiness Contract

## Two Independent Axes

`dataStatus` answers whether the profiled data contains the required facts.
`platformStatus` answers whether the current executable Registry/adapter product
exists. It is resolved only from an explicit Tool Registry snapshot supplied by
the application runtime; direct low-level profiling without that context returns
`NOT_EVALUATED`. A `READY` data status never promotes a planned tool.

```text
dataStatus: READY | MISSING_REQUIRED_DATA | AMBIGUOUS | UNSUPPORTED_DATA_KIND
platformStatus: AVAILABLE | NOT_IMPLEMENTED | NOT_EVALUATED
```

Every result carries stable reason codes, required semantics, and matching group
IDs. Runtime and Planner do not read roadmap documents to derive these values.

## Minimum Data Conditions

| Capability | Data condition | Current platform status |
| --- | --- | --- |
| table distribution | DataFrame resource | AVAILABLE |
| scatter/correlation | at least two finite numeric columns | AVAILABLE |
| histogram | at least one finite numeric column | AVAILABLE |
| composition/formula/element views | formula role or structure composition | AVAILABLE |
| structure summary | periodic Structure resource | AVAILABLE |
| trajectory visualization | Trajectory resource | AVAILABLE |
| phonon visualization | validated phonon resource | AVAILABLE |
| volumetric visualization | VolumetricData resource | AVAILABLE |
| regression evaluation | one complete target/prediction group | NOT_IMPLEMENTED in the 10K product layer |
| uncertainty evaluation | complete prediction group with uncertainty | NOT_IMPLEMENTED |
| classification evaluation | complete classification group | NOT_IMPLEMENTED |
| composition space | formula role | NOT_IMPLEMENTED |
| dataset structure statistics | Structure resource | NOT_IMPLEMENTED |

`AVAILABLE` references existing tool identities only; it does not claim every
future dataset workflow exists. Regression/uncertainty/classification product
semantics remain Phase 10K-3 even though legacy atomic ML adapters exist.

## Failure and Ambiguity

- missing semantics produce `MISSING:<role>` reasons;
- multiple target candidates produce `AMBIGUOUS` and
  `MULTIPLE_TARGET_COLUMNS`;
- unsupported resources produce `UNSUPPORTED_DATA_KIND`;
- invalid formulas remain row-level warnings and are not replaced with guessed
  compositions;
- missing units remain unknown; column-name unit parsing is not authoritative;
- non-finite-only numeric columns cannot satisfy numeric readiness;
- invalid probability rows make the classification group incomplete.

Readiness is a deterministic fact layer for later consumers. It is not Planner
logic, a recommendation engine, or an authorization to execute a tool.
