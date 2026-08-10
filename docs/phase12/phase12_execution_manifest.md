# Phase 12 Execution Manifest

Phase 12-0 executes `scripts/generate_phase12_0_ux_audit.py` against the local
frontend and sealed Phase 11 evidence. The script emits inventory and planning
records only; it performs no LLM call, network access, scientific calculation or
production mutation. `tests/test_phase12_0_ux_audit.py` validates baseline,
classification, decisions and manifest hashes.

Subphases execute only after individual reviewer authorization and keep the
acceptance ID set synchronized with backlog and this lock.
