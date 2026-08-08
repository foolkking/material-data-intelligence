# N1 Authority Audit

N2 consumes exactly one persisted N1 table Artifact. Binding validation checks
Artifact ID, checksum, contract version, producer Tool, source structure hash and
Project/Job scope before geometry analysis. The adapter reconstructs only the
Cartesian vector represented by each persisted site and periodic-image relation;
it does not perform a neighbor search.

`N2_RECOMPUTED_N1_NEIGHBORS = 0`
`N2_INDEPENDENT_NEIGHBOR_SEARCH = 0`
`N2_COORDINATION_ALGORITHM_FALLBACK = 0`
