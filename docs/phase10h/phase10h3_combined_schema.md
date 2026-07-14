# Phase 10H-3 Combined Schema

| Artifact | Schema |
|---|---|
| Combined references and display policy | `phase10h.phonon_band_dos.v1` |
| Product summary | `phase10h.phonon_band_dos_summary.v1` |
| Ordered compatibility report | `phase10h.phonon_band_dos_compatibility_report.v1` |
| Shared-axis plot data | `phase10h.phonon_band_dos_plot.v1` |
| Bounded tables | `phase10h.phonon_band_dos_table.v1` |
| Ordered manifest | `phase10h.phonon_band_dos_manifest.v1` |

The combined artifact stores validated source references and hashes, not copied
scientific arrays. Display arrays live in the bounded plot artifact. Objects
have exact fields, deterministic ordering, finite values, application caps, and
explicit no-JavaScript/no-HTML/no-external-asset flags. Stable band and DOS
contracts are unchanged.
