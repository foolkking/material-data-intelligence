# Phase 10H-1 Phonon Band Plot Contract

`phase10h1.phonon_band_plot.v1` is inert application-owned Plotly JSON. The
frontend does not execute this payload: it independently validates the
canonical band and maps one line trace per branch and path segment. Splitting
traces prevents lines crossing discontinuities. X is wave-vector path distance;
Y is frequency in THz, including negative values and a zero line.

Plotly loads from the locked local package as a lazy core plus scatter chunk.
The frontend refuses plot initialization above 500,000 values or 4,096 traces,
shows `PHONON_BAND_PREVIEW_LIMIT_EXCEEDED`, and retains table/JSON access. It
does not silently sample scientific data. Unmount purges Plotly resources.
