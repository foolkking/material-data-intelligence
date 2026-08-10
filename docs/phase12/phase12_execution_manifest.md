# Phase 12 Execution Manifest

Phase 12-0 executes `scripts/generate_phase12_0_ux_audit.py` against the local
frontend and sealed Phase 11 evidence. The script emits inventory and planning
records only; it performs no LLM call, network access, scientific calculation or
production mutation. `tests/test_phase12_0_ux_audit.py` validates baseline,
classification, decisions and manifest hashes.

Subphases execute only after individual reviewer authorization and keep the
acceptance ID set synchronized with backlog and this lock.

## Phase 12-1

Phase 12-1 executes `scripts/generate_phase12_1_design_system_evidence.py` over
the sealed 12-0 evidence, `globals.css`, and the component inventory. It emits
deterministic presentation-governance records only. The script does not call a
provider, use a network, calculate scientific values, mutate production data, or
become a runtime design-system authority.
