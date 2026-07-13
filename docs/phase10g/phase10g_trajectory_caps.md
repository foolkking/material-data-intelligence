# Caps and Storage

Contract hard caps are 4096 atoms, 10000 frames, 12 million position numeric values, 64 MB canonical JSON, 16 KB top metadata, 4 KB frame metadata, 128-character labels, 32 warnings, and numeric magnitude `1e12`. Products are checked with division-based overflow-safe preflight before iteration/allocation.

Future viewer guidance is 256 atoms/200 frames interactive and 2048 atoms/2000 frames degraded. These are planning values, not viewer evidence or readiness claims.

V1 stores bounded JSON for validation and interoperability. Large trajectory parsing should introduce local indexed/chunk artifacts in a later phase; this contract neither streams remote frames nor requires whole-trajectory browser loading.
