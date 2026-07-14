# Phase 10H-3 Performance Policy

The backend caps artifact bytes, warnings, traces, rows, visible projections,
and plot values. The frontend rechecks one million numeric values and 4096
traces before Plotly. Up to 500,000 values is interactive; larger approved data
may be degraded; over hard cap is refused without sampling or mutation.

Evidence records render time, trace count, one plot host, mobile overflow, lazy
load fallback, and cleanup. This is a bounded smoke baseline, not a universal
FPS or hardware guarantee.
