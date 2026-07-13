# Phase 10H Imaginary Frequency Policy

An imaginary mode is encoded as a negative real THz value. For example, `-1.5` means a mode with imaginary magnitude `1.5 THz`. Strings such as `1.5i`, NaN, separate mixed flags, absolute-value conversion, and silent clipping are prohibited.

`frequency_zero_tolerance` classifies values only:

```text
frequency < -tolerance  -> imaginary
abs(frequency) <= tolerance -> near_zero
otherwise -> real
```

The original frequency is never mutated. The validator records acoustic-sum-rule metadata but applies no ASR correction and never sets the first three Gamma modes to zero.
