# Screenshot Metadata

Capture time: `2026-08-01T19:33:22+08:00` audit session
Source repository SHA: `8f304fa08ddab1cefd69848f621f8438fc2038d5`
Mode: local UI replay from sanitized persisted captures; not service-backed and not a live provider run.

| File group | Browser | Viewport | Route | Case |
| --- | --- | --- | --- | --- |
| `chromium_desktop_ready_case_*.png` | Chromium 129.0.6668.29 | 1440x1100 | `/` | L5 dataset, structure, ML, phonon, volumetric |
| `firefox_desktop_ready_case_*.png` | Firefox installed Playwright build | 1440x1100 | `/` | same L5 five ready cases |
| `webkit_desktop_ready_case_*.png` | WebKit installed Playwright build | 1440x1100 | `/` | same L5 five ready cases |
| `chromium_desktop_non_ready_*.png` | Chromium | 1440x1100 | `/` | clarification, unsupported, capability mismatch |
| `chromium_mobile_390x844_*.png` | Chromium | 390x844 | `/` | L5 ready and non-ready states |
| `desktop_deterministic.png`, `desktop_strict_provider.png` | Chromium | 1440x1100 | `/` | L4 findings/evidence modes |
| `desktop_partial.png`, `desktop_no_supported_evidence.png` | Chromium | 1440x1100 | `/` | L4 partial and no-evidence states |
| `desktop_validation_failure.png`, `desktop_source_integrity_failure.png` | Chromium | 1440x1100 | `/` | L4 typed failures |
| `mobile_deterministic.png`, `mobile_partial.png`, `mobile_no_supported_evidence.png` | Chromium | 390x844 | `/` | L4 mobile findings states |

Firefox and WebKit mobile were not run by the existing runner and are
explicitly `UNAVAILABLE`; no mobile result is inferred from desktop.
