# Known Limitations and Release Claims

Product support, input support, scientific validation, browser testing, service-backed testing, cross-platform replay, and independent reference provenance are separate authorities.

| ID | Category | Current status | User-facing limitation | Owner |
|---|---|---|---|---|
| LIM-001 | Scientific validation | Retained | Tool availability does not mean every numerical output was independently reference-validated. | Phase 11 authority |
| LIM-002 | Cross-platform | Retained | Linux and Windows invariant replay passed; independent numeric cross-platform reference validation is not applicable. | Release governance |
| LIM-003 | Browser | Retained | Chromium, Firefox, WebKit, and Chromium 390x844 were tested; universal browser/mobile certification is not claimed. | Phase 13 |
| LIM-004 | Phonon input | Retained | Typed Band/DOS imports are supported with limits; generic phonon YAML/JSON is mapping-only. | Product scope |
| LIM-005 | Provider | Retained | DeepSeek verification is optional and is not scientific or reference validation. | Provider policy |
| LIM-006 | Recipe | Retained | Recipes are declarative and non-executable. | Security model |
| LIM-007 | XRD | Retained | Peak correspondence is bounded by wavelength/tolerance policy; no phase confirmation, fraction, or Rietveld refinement. | Scientific contract |
| LIM-008 | Diffusion | Retained | Diffusion is an estimate over the selected fit window. | Scientific contract |

Forbidden public claims include autonomous research, arbitrary workflows or DAG execution, DFT/GW execution, generic phonon JSON support, executable Recipes, formal WCAG certification, universal browser support, and independent validation of all Tools or numerical outputs.
