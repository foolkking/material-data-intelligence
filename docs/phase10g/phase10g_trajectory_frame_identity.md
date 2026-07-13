# Frame and Atom Identity

`atom_identity_mode` is exactly `stable_index`. `atoms.records[i].atom_id` is `i`; species, occupancy 1.0, and unique bounded label are fixed at top level. Every frame carries `atom_ids = [0..N-1]`, so count changes and reorder are rejected without coordinate matching or inferred correspondence.

`frame_index` starts at zero, is contiguous, and agrees with array order. Duplicate indices receive a typed error. `step` is optional, nonnegative, and monotonic. MD `time` is finite and monotonic. Frames never add/remove atoms or redefine species.
