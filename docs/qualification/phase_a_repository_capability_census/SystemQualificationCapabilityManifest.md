# System Qualification Capability Manifest

Schema: `SystemQualificationCapabilityManifest/1.0`

## 1. Executive summary

This repository-grounded census records what the sealed Initial Release can accept, plan, execute, persist, render, interpret, and compose into Reports and non-executable Recipes. It makes no web-derived support claim and performs no qualification run. The current Registry contains **62** Tools; **47** are Planner-available with registered Adapters. The Workspace renderer registry contains **42** exact Artifact declarations.

## 2. Current release authority

Initial Release remains complete. Registry 62, DataProfile 2.4, AnalysisIntent 1.0, EligibilityResolution 1.0, AnalysisPlan 0.1/0.2, migration 0007, panel cap 32, and layout-revision cap 128 are unchanged. See `current_authorities.json`.

## 3. User data entry paths

Four current user-accessible entry classes are inventoried in `user_entry_inventory.json`: generic UI upload, typed phonon Band+DOS+Structure import, exact persisted Dataset selection, and the documented inline upload API.

## 4. Supported file/container formats

`file_format_inventory.json` records 15 container/format families. A container name never establishes scientific meaning; `input_support_matrix.json` binds entry path, format, semantic kind, and disposition.

## 5. Semantic scientific data kinds

`semantic_data_kind_inventory.json` records 15 semantic kinds with exact Profile prerequisites, identities, units, companion/context resources, limits, and negative conditions.

## 6. Support dispositions

The normalized vocabulary is `SUPPORTED`, `SUPPORTED_WITH_LIMITS`, `MAPPING_ONLY`, `LEGACY_READ_ONLY`, `UNSUPPORTED`, and `UNKNOWN_REPOSITORY_AUTHORITY`. Current executable input combinations: 3 supported and 17 supported-with-limits. Generic phonon YAML/JSON contributes 3 mapping-only combinations; 3 combinations are explicitly unsupported.

## 7. Data/Profile prerequisites

Every executable case requires durable exact identity and DataProfile 2.4 facts appropriate to the semantic kind. Missing roles, targets, units, structure context, wavelength, energy reference, paired resources, contract versions, hashes, or project scope produce typed non-readiness rather than inference.

## 8. Capability families

`capability_family_inventory.json` defines 18 user-level families. A capability family is not a Tool ID; the many-to-many mapping is in `capability_matrix.json`.

## 9. Full Registry Tool inventory

`registry_tool_qualification_inventory.json` mechanically lists all 62 Registry entries, including 47 current release-relevant Tools, 12 future Tools, and 3 deployment-unavailable/legacy-only entries.

## 10. Capability to Tool mapping

See `capability_matrix.json` and `.csv`. All 47 current Planner-available Tools participate in at least one proposed case.

## 11. Tool to Artifact mapping

See `output_matrix.json` and `.csv`. Runtime authority remains QueueWorkerRuntime to registered Adapter to persisted Artifact.

## 12. Artifact to Renderer mapping

`artifact_qualification_inventory.json` and `renderer_qualification_inventory.json` cover all 42 exact renderer declarations. Filename, MIME, display label, and array position are never dispatch or identity authority.

## 13. Viewer behavior and assertions

Each Artifact inventory row contains future browser assertions and separates presentation assertions from scientific invariant/value assertions. No new expected scientific number is defined; absent authority is recorded as `NOT_DEFINED`.

## 14. Interpretation support

`interpretation_inventory.json` limits interpretation to grounded claims over persisted facts and exact lineage. No evidence means no scientific claim; partial results require explicit limitations.

## 15. Report / Recipe support

`report_recipe_inventory.json` records exact-source Report Preview/Finalize expectations. Recipes remain declarative and non-executable for every case.

## 16. Negative / clarification boundaries

`negative_case_catalog.json` records 19 repository-applicable boundaries, including unsupported/mapping-only inputs, missing semantics, unknown units, ambiguity, pairing, stale/hash/scope errors, contract/wavelength/cap limits, provider failure, partial execution, unsupported capability, and Future Scope.

## 17. Existing qualification evidence

`existing_evidence_matrix.json` distinguishes unit, integration, service-backed, browser replay, live LLM, fresh E2E, scientific reference/invariant, and mapping-only evidence. Retained DeepSeek captures tested five selected capability paths; browser playback did not initiate those LLM calls.

## 18. Proposed user-centric qualification cases

`proposed_qualification_cases.json` defines 36 grounded scenarios: 16 positive/supported-with-limits cases plus 20 negative, clarification, or non-ready boundary cases.

## 19. Minimum representative case set

`minimum_case_set.json` contains 16 cases optimized to cover current execution-ready user surfaces without a material-class-by-Tool Cartesian product. `extended_case_set.json` adds all boundaries, including the mapping-only phonon-animation entry case.

## 20. External real-data requirements

`external_data_requirements.json` defines one requirement per proposed case. Phase B should acquire only the 16 requirements marked `mustBeRealPublicData=true`; no data was downloaded in Phase A.

## 21. Coverage metrics

* Capability families with case coverage: 18/18
* Release-relevant Registry Tools with case participation: 47/47
* Supported input combinations with semantic-kind case coverage: 20/20
* Release-relevant Artifact types with case coverage: 35/38
* Release-relevant renderers with case coverage: 35/38

## 22. Authority conflicts

`authority_conflicts.json` records 0 conflicts. No unresolved P0/P1 Registry-to-Adapter or Artifact-to-renderer conflict was found.

## 23. Qualification design gaps

`qualification_design_gaps.json` records 8 explicit design gaps. Gaps are not product defects or support promotions.

## 24. Readiness for external data research

`QUALIFICATION_DATA_RESEARCH_READY = YES`. This authorizes only a future reviewer-controlled search/acquisition phase; Phase B was not executed.

## 25. Exact next-step handoff

Use `phase_b_external_qualification_dataset_research_handoff.json`. It contains only the real-data characteristics, accepted formats, licensing/provenance requirements, permitted normalization, and forbidden scientific transformations for the minimum representative case set.
