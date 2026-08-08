# Tolerance Audit

Identity, site IDs, neighbor IDs, periodic images, checksums and geometry IDs
are exact. Geometry coordinates use 1e-6 Angstrom source consistency validation;
classification uses the bounded angular-spectrum RMS distance and a frozen
0.01 tie tolerance. Numeric metrics use quantity-specific finite comparisons;
no global tolerance, silent clipping or neighbor deletion is used.
