# Troubleshooting

| Symptom | Safe action |
|---|---|
| Stale Profile/source or Workspace source not current | Reopen the exact current dataset version and create a fresh Profile/Plan; do not bind latest implicitly. |
| Durable root resource missing | Re-import through the supported product entry and verify PostgreSQL metadata plus MinIO object health. |
| Hash mismatch | Treat as integrity failure; do not ignore or rewrite the checksum. |
| Cross-project source | Select a source owned by the current project. |
| Generic phonon JSON not execution-ready | Use explicit typed PhononBand and PhononDos import; generic YAML/JSON remains mapping-only. |
| Typed phonon validation failure | Check declared kind, schema version, required units/path facts, finite values, and caps; do not infer missing science. |
| `PANEL_CAP_EXCEEDED` | Reduce genuinely distinct product surfaces; do not raise the 32-panel cap or truncate panels. Supporting Artifacts remain in Gallery. |
| XRD wavelength mismatch | Supply compatible experimental data; no automatic wavelength conversion is authorized. |
| Provider key unavailable/failure | Use deterministic Mode A. Optional Mode B reads only `DEEPSEEK_KEY`; retain typed failure context. |
| Report Finalize unavailable | Inspect the server-provided action reason for stale, cross-project, missing/ineligible source, or legacy-incomplete state. Do not bypass via direct API. |
