# Phase 10H-3 Combined Band + DOS

Phase 10H-3 registers `phonon.band_dos` as the bounded static composition
product for one validated phonon band artifact and one validated phonon DOS
artifact. The backend performs compatibility checks before producing any
success artifacts. It does not calculate phonons or mutate either source.

The product emits six inert JSON artifacts: combined references, summary,
compatibility report, shared-axis plot data, bounded tables, and manifest. The
frontend independently validates the complete bundle before lazy-loading local
Plotly. The band panel uses q-path distance on x, the DOS panel uses density on
x, and both panels share one THz frequency y-axis.

Compatibility covers artifact hashes, structure identity, atom count and order,
cell lineage, calculation and force-constant lineage, frequency conversion,
imaginary-mode encoding, zero tolerance, NAC, DOS normalization, projection
identity, display caps, and frequency-domain policy. Status is `compatible`,
`convertible`, or `incompatible`; incompatible pairs produce no success
artifacts.

Evidence is under
[`evidence/phase10h3_combined_band_dos/`](evidence/phase10h3_combined_band_dos/).
Eigenvectors, animation, thermal properties, phonon calculation, scripts,
notebooks, remote artifacts, and arbitrary plotting remain out of scope.
