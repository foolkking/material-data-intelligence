# Projected Phonon DOS

Identity is canonical atom index plus matching species, or canonical species.
Ordering is atoms by index then species lexicographically. Duplicates and
display-label identities fail.

`complete` enables canonical sum checking. `partial` and `unknown` make no sum
claim and are never rescaled. Atom and species totals are supported;
directional/local-axis projections are deferred because no basis field exists.
