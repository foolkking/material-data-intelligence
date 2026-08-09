# Phase 11 Validation Governance

## Authority Model

Validation is multi-axis. Each Tool records software execution, scientific reference, numeric validation, Artifact contract, platform integration, browser presentation, reproducibility, and known limitations separately. A PASS on one axis does not raise another axis.

Reference priority is:

1. analytic or mathematical truth;
2. official library or specification reference;
3. independent cross-library reference;
4. official-derived reviewed fixture;
5. controlled synthetic fixture;
6. internal regression expectation;
7. mapping-only evidence.

The corresponding provenance types are `ANALYTIC_REFERENCE`, `OFFICIAL_LIBRARY_REFERENCE`, `OFFICIAL_PROJECT_EXAMPLE`, `INDEPENDENT_CROSS_LIBRARY_REFERENCE`, `CONTROLLED_SYNTHETIC_REFERENCE`, `REPOSITORY_INTERNAL_EXPECTED_VALUE`, `MAPPING_ONLY`, and `NO_REFERENCE`.

## Honest Boundaries

```text
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
BROWSER_PASS_EQUALS_NUMERIC_REFERENCE_PASS = NO
SERVICE_PASS_EQUALS_NUMERIC_REFERENCE_PASS = NO
FIXTURE_EXISTS_EQUALS_REFERENCE_VERIFIED = NO
MAPPING_EQUALS_VERIFIED = NO
SELF_REFERENCE_EQUALS_INDEPENDENT_REFERENCE = NO
LATEST_EVIDENCE_WINS_AUTHORITY = NO
GLOBAL_SCIENTIFIC_EPSILON = NONE
PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED
```

Screenshots and browser runs validate presentation and interaction. Service-backed runs validate persistence, queueing, storage, lineage, scope, and checksums. Neither is numeric scientific reference authority.

## Coverage Verdicts

- `DIRECT_VERIFIED`: platform-native input and runtime path plus reviewed expected values/invariants and owned tolerances.
- `OFFICIAL_DERIVED_VERIFIED`: retained official source, license disposition, immutable transformation record, reviewed expected values, and passing platform comparison.
- `REFERENCE_VERIFIED`: analytic, specification, or independent reference with exact provenance and passing comparison.
- `MAPPING_ONLY`: contract or example mapping exists without direct platform verification.
- `EXTRACTION_REQUIRED`: suitable source is identified but a governed fixture has not been extracted.
- `FUTURE_SCOPE`: deliberately outside the approved Initial Release.
- `UNSUPPORTED`: no approved platform input/runtime path.

## Governance

Reference authority follows provenance, Tool/version, contract, source and fixture hashes, expected values, units, tolerance, and review state, never recency. Authoritative fixtures are immutable; changes require a new fixture version and retained history. Unknown or unclear redistribution rights are `LICENSE_REVIEW_REQUIRED`.

The primary scientific environment is the current locked repository environment. Phase 11-3 covers supported CI/runtime platforms and the established Chromium, Firefox, WebKit, and Chromium 390x844 presentation matrix.
