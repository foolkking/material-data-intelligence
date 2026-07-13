# Trajectory Identity

Canonical scientific identity is stable `atomIndex`. A displayed periodic instance is `atomIndex + imageOffset`; frame index is provenance, not atom identity. Instance grouping and ordering are deterministic across frames. Picks are accepted only against the committed frame mapping. Playback click pauses before selection.

Measurements use current committed Cartesian positions and show frame provenance. Frame changes clear active distance/angle/dihedral results; inspect selection may retain stable atom identity.
