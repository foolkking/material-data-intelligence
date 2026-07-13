# Phase 10H Frequency Units

Canonical frequency is cyclic frequency in `terahertz`, not angular frequency. `radian_per_second` and arbitrary unit expressions are unsupported.

Approved conversion boundaries are:

- `terahertz`
- `inverse_centimeter` (spectroscopic wavenumber)
- `millielectronvolt` (energy equivalent)

Conversions use exact SI defining constants: `h = 6.62607015e-34 J s`, `c = 299792458 m/s`, and `1 eV = 1.602176634e-19 J`. Thus 1 THz is approximately `33.3564095198152 cm^-1` and `4.135667696923859 meV`. Canonical artifacts remain THz; adapters, not validators, own source conversion.
