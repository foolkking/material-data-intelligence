# Case Selection Audit

## Benchmark Pack

- path: `C:\Users\86182\Desktop\pymatviz_official_examples_test_suite`
- status: present
- required files read:
  - `BENCHMARK_READINESS.md`
  - `NEXT_PHASE_CANDIDATES.md`
  - `CASE_INDEX.json`
  - `manifest.csv`
  - `manifest.json`
  - `audit/audit_report.json`
  - `cases/*/expected_contract.json`
  - `cases/*/input_manifest.json`
  - `cases/*/source_provenance.json`

## Benchmark Summary

| Metric | Count |
|---|---:|
| total cases | 61 |
| `DIRECT_VERIFIED` | 2 |
| `MAPPING_ONLY` | 20 |
| `EXTRACTION_REQUIRED` | 27 |
| `FUTURE_SCOPE` | 12 |
| raw-data cases | 2 |

Audit status: `ok: true`, issues: 0, warnings: 0.

## Direct-Uploadable Gate

Gate conditions:

1. Local input artifact is present.
2. Input can be uploaded through the current platform resource flow.
3. No notebook execution.
4. No external script execution.
5. No external API.
6. No network.
7. No new dependency.
8. No large benchmark file.
9. Expected output is comparable through the current artifact contract.
10. Tool mapping is one of `structure.coordination_hist`, `structure.xrd`, or `structure.rdf`.

## Static Physics Candidate Findings

No benchmark case passed the gate for `structure.coordination_hist`, `structure.xrd`, or `structure.rdf`.

Structure-adjacent and physics-adjacent official examples are currently not direct-uploadable static physics cases:

- `readme_structure_2d`: README function demo, maps to `structure.structure_2d`, not static physics.
- `readme_structure_3d`: README function demo, maps to `structure.structure_3d`, not static physics.
- `readme_widgets_structure_widget`: interactive widget demo, not static physics and not direct-uploadable.
- `readme_brillouin_zone_3d`: Brillouin-zone 3D future scope.
- `widgets_jupyter_demo`, `widgets_marimo_demo`, `widgets_vscode_interactive_demo`: widget/interactive examples.
- `matbench_phonons`, `phonons_mlip_phonons`, `readme_phonon_bands`, `readme_phonon_dos`, `readme_phonon_bands_and_dos`: phonon future scope, not static structure physics.

## Excluded Cases

- notebook-only / notebook-like: notebook examples remain extraction-required or future-scope.
- script-heavy: script-generated data cases remain extraction-required.
- external API required: cases requiring external data/API remain excluded.
- missing direct static physics input: README structure/function demos do not provide direct uploadable static physics fixtures.
- future scope: viewer, WebGL, Brillouin-zone, phonon, and widget cases remain future scope.

## PASS Evidence Rules

Only directly executed, direct-uploadable official cases can be marked PASS. Phase 10F-1 marks no static physics case PASS because no such official case exists in the current pack.
