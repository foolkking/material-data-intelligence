# Phase 10N-3 Peak Detection Contract

The internal detector is `mdi.experimental_xrd_peak_detection@1.0.0`, implemented with locked `scipy.signal.find_peaks` from SciPy 1.17.1. Supported normalization is `none`, `max_to_1` or `max_to_100`; smoothing and background fitting are disabled. The bounded parameters are minimum prominence `[0,1]`, minimum relative height `[0,1]`, minimum separation `[0,10] degree`, and maximum 10,000 peaks.

Detection is completed before theoretical matching and cannot inspect match success. It never shifts, adds or removes peaks to improve correspondence.
