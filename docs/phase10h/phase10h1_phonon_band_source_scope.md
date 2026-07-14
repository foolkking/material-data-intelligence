# Phase 10H-1 Phonon Band Source Scope

## Approved

- Strict canonical `phase10h.phonon_band.v1` JSON.
- Static phonopy `band.yaml` wrapped with an explicit SHA-256 structure identity.

The YAML path uses the existing PyYAML `safe_load` plus byte, node, depth,
anchor, alias, tag, field, numeric, and contract caps. It never runs phonopy.

## Deferred or rejected

Pymatgen serialized phonon objects are deferred until a stable persisted
producer exists. URLs, archives, pickle, notebooks, scripts, plugins, arbitrary
YAML tags, and solver execution are rejected. No dependency was added.
