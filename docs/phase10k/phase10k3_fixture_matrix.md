# Phase 10K-3 Fixture Matrix

| Area | Required cases |
| --- | --- |
| Regression | perfect/noisy/bias/constant target, missing/non-finite, unit preservation, stable high-error link |
| Multiple models | shared target, common-valid-sample policy, deterministic ordering |
| Chemistry | element overlap, exact chemical systems, invalid/missing formula disclosure, bounded groups |
| Uncertainty | aligned source-defined values, ties, equal-count bins, retained-error curve, negative rejection |
| Classification | binary confusion/ROC/PR, no probability, multiclass curve refusal, unknown positive class, imbalance warning |
| Semantic boundary | missing, incomplete, and ambiguous Profile 2.0 groups; one canonical table binding |
| Security | HTML-like labels as text, strict params, URL rejection, cap refusal, inert artifacts |
| Performance | 4, 5,000, and 100,000 rows; bounded points/artifact bytes |
| Browser | Chromium, Firefox, WebKit, 390x844 mobile, numeric fallbacks, zero external requests |

The evidence fixtures are existing-result datasets. No model fitting, remote
lookup, arbitrary code, or real LLM call occurs.
