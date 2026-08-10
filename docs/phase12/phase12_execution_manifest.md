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

## Phase 12-2

Phase 12-2 executes `scripts/generate_phase12_2_navigation_planner_evidence.py`
against the existing route, Planner component, message catalogs, DS2 handoff and
sealed UX problem matrix. Evidence is local and deterministic; it performs no
LLM call, external network call, scientific calculation or production mutation.
The implementation must preserve existing route, API, plan, runtime, Workspace,
selection and provider authorities.

## Phase 12-3

Phase 12-3 uses the existing Workspace shell, Artifact Gallery, renderer
registry and selection-runtime tests. Evidence is deterministic and local: it
records presentation-only navigation groups, the result-first summary, shared
viewer chrome, metadata-first/lazy payload behavior and the exact URL selection
contract. It performs no LLM call, external network call, scientific
calculation, backend mutation or new runtime authority.

## Phase 12-4

Phase 12-4 executes `scripts/generate_phase12_4_findings_evidence.py` and
`tests/test_phase12_4_findings_evidence.py`. The generator records exact
claim/evidence membership, Inspector layers, provenance presentation, typed
negative states and authority non-change. It is deterministic, local and
non-scientific: it performs no provider call, external network access, evidence
projection, claim generation, Artifact mutation or runtime execution.

## Phase 12-5

Phase 12-5 executes `scripts/generate_phase12_5_report_recipe_evidence.py`,
`tests/test_phase12_5_report_recipe_evidence.py`, component tests, and the
existing Report/Recipe browser replay against the Phase 12-5 evidence root.
The generator is deterministic and local. Browser replay uses local fixtures
and three engines plus 390x844; neither path calls an LLM, external scientific
API, Recipe executor, or scientific computation authority.

## Phase 12-6

Phase 12-6 executes
`scripts/generate_phase12_6_responsive_accessibility_evidence.py`,
`tests/test_phase12_6_responsive_accessibility.py`, focused component tests,
the current Planner browser replay, and retained three-engine/mobile Workspace
replays. Evidence is deterministic and local. It performs no real assistive
technology claim, provider call, external network access, scientific
calculation, backend mutation, or new runtime authority.
