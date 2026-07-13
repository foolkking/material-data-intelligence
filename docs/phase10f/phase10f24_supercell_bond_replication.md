# Phase 10F-24 Supercell Bond Replication

Only canonical v2 periodic bonds are replicated. For source cell `t`, endpoint images become `from@t` and `to@(t+relativeOffset)`. An edge is emitted only when both endpoints are displayed. Stable symmetric endpoint keys remove reverse, adjacent-cell, and self-periodic duplicates. No distance-based frontend topology inference occurs.
