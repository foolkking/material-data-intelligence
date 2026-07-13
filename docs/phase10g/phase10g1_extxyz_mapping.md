# EXTXYZ Mapping

The application-owned streaming parser accepts `species:S:1`, `pos:R:3`, optional integer `id`, velocity aliases, and force aliases. Unknown columns are consumed but dropped with a bounded warning. Metadata uses safe `shlex` tokenization only; no eval/literal-eval.

Every frame requires explicit nine-value row-vector `Lattice` and explicit all-periodic/all-nonperiodic PBC. Cartesian positions default to the EXTXYZ angstrom convention. Time/vector/scalar noncanonical units require exact approved metadata. Frame completeness, counts, descriptor shape, species, IDs, properties, time, lattice and PBC are cross-validated.

First-frame source ID order defines canonical stable-index order. Later rows may be reordered only by a complete unique stable ID set; reordering is recorded in the parse report.
