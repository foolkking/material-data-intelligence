# Phase 10H-3 Combined Plot Contract

`phase10h.phonon_band_dos_plot.v1` contains bounded display arrays, source
ticks/discontinuities, one shared frequency domain, DOS series, projections,
and an application display tier. Interactive, degraded, and refused tiers use
fixed numeric-value and trace caps. Refusal retains summaries, compatibility,
tables, and JSON.

Plotly core/scatter are lazy local imports. Artifact data cannot define trace
types, callbacks, templates, HTML, URLs, modules, or scripts. Resize listeners
and Plotly state are purged on rerender/unmount. PNG export uses fixed local
dimensions and the current validated figure.
