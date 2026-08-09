# Phase 11 Tolerance Registry

The canonical audit inventory is [tolerance_inventory.json](evidence/phase11_0_validation_baseline_reconciliation/tolerance_inventory.json). Tolerances are quantity- and contract-specific. Scientific entity identity, Tool/version, hashes, checksums, Plan bindings, and evidence identity are exact.

Every tolerance has an owner phase, unit, reference provenance, reason, scientific justification, platform-variance relevance, and review status. There is no global scientific epsilon. A failed fixture cannot justify widening a tolerance, deleting a difficult case, or rewriting an expected value.

Future semantic tolerance changes require a documented scientific reason and reviewer approval. Phase 11-3 may characterize observed variance but cannot silently change a sealed tolerance.
