# Periodic Measurement Semantics

Two explicit modes exist:

* `displayed_positions`: unchanged Phase 10F-16 Cartesian behavior.
* `minimum_image`: bounded exact periodic image resolution.

Distance resolves the target image relative to the selected source. Angle anchors B and independently resolves A and C relative to B. Dihedral anchors B, resolves A and C, then resolves D relative to the selected C image. Signed dihedral remains in `[-180, 180]`. The UI displays every resolved image offset.
