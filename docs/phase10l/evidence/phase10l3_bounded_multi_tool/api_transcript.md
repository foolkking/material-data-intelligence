# Sanitized API Transcript

```json
{
  "nonReady": {
    "capability_decision": null,
    "capability_outcome": null,
    "dependency_bindings": [],
    "eligibility_resolution": null,
    "enqueued": false,
    "error_code": "INTENT_CLARIFICATION_REQUIRED",
    "executed": false,
    "graph_hash": null,
    "intent": {
      "ambiguities": [
        {
          "blocking": true,
          "candidates": [
            {
              "label": "phonon: phonon_band_1",
              "semanticId": "resource:phonon_band_1:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
              "value": "phonon_band_1"
            },
            {
              "label": "phonon: phonon_dos_1",
              "semanticId": "resource:phonon_dos_1:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
              "value": "phonon_dos_1"
            }
          ],
          "code": "RESOURCE_SELECTION_AMBIGUOUS",
          "field": "dataScope.resourceRefs",
          "message": "Multiple phonon resources are available.",
          "source": "RESOURCE_SELECTION"
        }
      ],
      "clarification": {
        "answers": [],
        "maxQuestionsPerRound": 3,
        "maxRounds": 1,
        "questions": [
          {
            "bindsTo": "dataScope.resourceRefs",
            "code": "SELECT_RESOURCE",
            "options": [
              {
                "label": "phonon: phonon_band_1",
                "semanticId": "resource:phonon_band_1:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "value": "phonon_band_1"
              },
              {
                "label": "phonon: phonon_dos_1",
                "semanticId": "resource:phonon_dos_1:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                "value": "phonon_dos_1"
              }
            ],
            "prompt": "Which phonon resource should be analyzed?",
            "questionId": "select_phonon_resource",
            "required": true,
            "type": "SELECT_ONE"
          }
        ],
        "round": 0
      },
      "constraints": {
        "clarificationAllowed": true,
        "costPreference": null,
        "descriptiveOnly": false,
        "excludeResourceIds": [],
        "excludeScientificIntents": [],
        "forbidDerivedInterpretation": false,
        "groupIds": [],
        "includeResourceIds": [],
        "includeScientificIntents": [],
        "maxAnalyses": null,
        "maxToolCalls": null,
        "modelIds": [],
        "outputPreferences": [],
        "targetIds": [],
        "timePreference": null
      },
      "dataScope": {
        "datasetId": "dataset_1",
        "datasetVersion": "dataset_version_2",
        "groupIds": [],
        "modelIds": [],
        "origin": "USER_EXPLICIT",
        "profileContractVersion": "2.0",
        "profileId": "profile_1",
        "profileSemanticHash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "resourceRefs": [],
        "sampleIds": []
      },
      "datasetId": "dataset_1",
      "desiredOutputs": [
        "summary",
        "warnings",
        "plot",
        "table"
      ],
      "intentHash": "c86c3507374f25c2c7e26095b12bd0d5994c07c998e9e98561bbfc60ef1ba588",
      "intentId": "intent_c86c3507374f25c2c7e26095",
      "language": "en",
      "missingFacts": [],
      "normalizedGoal": "Analyze this phonon calculation.",
      "optionalCapabilityNeeds": [],
      "outcome": "NEEDS_CLARIFICATION",
      "profileId": "profile_1",
      "provenance": {
        "answerBindings": [],
        "createdAt": "2026-07-30T00:00:00+00:00",
        "model": "bounded-rules-v1",
        "parentIntentId": null,
        "promptVersion": "phase10l1.intent.v1",
        "provider": "deterministic_mock"
      },
      "rawGoal": "Analyze this phonon calculation.",
      "requiredCapabilityNeeds": [
        "phonon_resource"
      ],
      "schemaVersion": "1.0",
      "scientificIntents": [
        "phonon_analysis"
      ],
      "targetSemantics": [],
      "unsupportedReasons": [],
      "warnings": []
    },
    "intent_id": "intent_c86c3507374f25c2c7e26095",
    "intent_outcome": "NEEDS_CLARIFICATION",
    "job_id": null,
    "ok": false,
    "plan": null,
    "plan_hash": null,
    "plan_id": null,
    "plan_schema_version": null,
    "plan_source": "llm",
    "planner_provider": "mock",
    "provider_visible_tool_ids": [],
    "topological_order": [],
    "validation_errors": []
  },
  "nonReadyPersisted": {
    "executions": 0,
    "jobs": 0,
    "plannedBindings": 0,
    "plans": 0
  },
  "profile": {
    "analysisReadiness": [],
    "createdAt": "2026-07-30T00:00:00+00:00",
    "datasetId": "dataset_1",
    "datasetType": "mixed",
    "files": [],
    "objects": [],
    "phononSummary": null,
    "profileContractVersion": "2.0",
    "profileCoverage": null,
    "profileId": "profile_1",
    "qualityIssues": [],
    "recommendedTasks": [],
    "resourceSemantics": [
      {
        "capabilities": [
          "phonon"
        ],
        "facts": {},
        "kind": "phonon",
        "objectHash": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "objectId": "phonon_band_1",
        "objectType": "PhononBand",
        "warnings": []
      },
      {
        "capabilities": [
          "phonon"
        ],
        "facts": {},
        "kind": "phonon",
        "objectHash": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
        "objectId": "phonon_dos_1",
        "objectType": "PhononDos",
        "warnings": []
      }
    ],
    "sampleIdentity": {
      "datasetVersion": "dataset_version_2",
      "explicitColumn": null,
      "fallbackPolicy": "dataset_version_object_hash_row_index",
      "objectIds": [
        "table_1"
      ],
      "policy": "object_hash_row_index"
    },
    "schemaVersion": "0.1",
    "semanticColumns": [
      {
        "ambiguities": [],
        "column": "formula",
        "dtype": "string",
        "finiteCount": null,
        "missingCount": 0,
        "nonFiniteCount": null,
        "objectId": "table_1",
        "roles": [
          {
            "authority": "canonical_name",
            "details": {},
            "groupId": null,
            "role": "material_formula"
          }
        ],
        "rowsInspected": 0,
        "totalRows": 0,
        "uniqueCount": 0,
        "unit": null
      }
    ],
    "semanticGroups": [],
    "semanticHash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "semanticRulesVersion": "phase10k1.material_profile_semantics.v1",
    "structureSummary": null,
    "tableSummary": null,
    "trajectorySummary": null,
    "version": "2"
  },
  "ready": {
    "capability_decision": {
      "decisionHash": "cc6222c2b00369b8ad5417eeae015a3bf4724907e24b056111842623ba8e4823",
      "decisionId": "decision_cc6222c2b00369b8ad5417ee",
      "diagnostics": [],
      "intentHash": "af647d24626215fa9a56999c46e5154aef6baf3bc9a77f688049b7bc9cb7d9d3",
      "intentId": "intent_af647d24626215fa9a56999c",
      "outcome": "PLAN_READY",
      "profileId": "profile_1",
      "profileSemanticHash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "provenance": {
        "initialDecisionHash": null,
        "model": "mock",
        "provider": "deterministic_mock",
        "providerContractVersion": "1.0",
        "repairCount": 0,
        "repairDiagnostics": []
      },
      "registrySnapshotHash": "465482cd226ed056aec57ab4437f90d85b4c8c12507ca62a50f6574b3f8cade0",
      "registrySnapshotId": "registry_465482cd226ed056aec57ab4",
      "resolutionHash": "4b67a9ae7ddec82d1f57ad87b60e5cc657204a0c8616f4d786b94206538b7ca8",
      "resolutionId": "resolution_4b67a9ae7ddec82d1f57ad87",
      "schemaVersion": "1.0",
      "selections": [
        {
          "artifactTypes": [
            "phonon_band_json",
            "phonon_summary_json",
            "phonon_report_json",
            "phonon_manifest_json",
            "plotly_json",
            "table_json",
            "recipe_json"
          ],
          "boundParameters": [],
          "coveredCapabilityNeeds": [
            "phonon_resource"
          ],
          "coveredDesiredOutputs": [
            "plot",
            "summary",
            "table",
            "warnings"
          ],
          "coveredScientificIntents": [
            "phonon_analysis"
          ],
          "inputResourceIds": [
            "phonon_band_1"
          ],
          "rankFacts": [
            1,
            1,
            4,
            1,
            0,
            2,
            "phonon.band",
            "0.1.0"
          ],
          "targetSemanticIds": [],
          "toolId": "phonon.band",
          "toolName": "Phonon Band",
          "toolVersion": "0.1.0"
        },
        {
          "artifactTypes": [
            "phonon_band_dos_json",
            "phonon_summary_json",
            "phonon_compatibility_json",
            "plotly_json",
            "table_json",
            "phonon_manifest_json",
            "recipe_json"
          ],
          "boundParameters": [],
          "coveredCapabilityNeeds": [
            "phonon_resource"
          ],
          "coveredDesiredOutputs": [
            "plot",
            "summary",
            "table",
            "warnings"
          ],
          "coveredScientificIntents": [
            "phonon_analysis"
          ],
          "inputResourceIds": [
            "phonon_band_1",
            "phonon_dos_1"
          ],
          "rankFacts": [
            1,
            1,
            4,
            2,
            0,
            2,
            "phonon.band_dos",
            "0.1.0"
          ],
          "targetSemanticIds": [],
          "toolId": "phonon.band_dos",
          "toolName": "Phonon Band Dos",
          "toolVersion": "0.1.0"
        },
        {
          "artifactTypes": [
            "phonon_dos_json",
            "phonon_summary_json",
            "phonon_report_json",
            "phonon_manifest_json",
            "plotly_json",
            "table_json",
            "recipe_json"
          ],
          "boundParameters": [],
          "coveredCapabilityNeeds": [
            "phonon_resource"
          ],
          "coveredDesiredOutputs": [
            "plot",
            "summary",
            "table",
            "warnings"
          ],
          "coveredScientificIntents": [
            "phonon_analysis"
          ],
          "inputResourceIds": [
            "phonon_dos_1"
          ],
          "rankFacts": [
            1,
            1,
            4,
            1,
            0,
            2,
            "phonon.dos",
            "0.1.0"
          ],
          "targetSemanticIds": [],
          "toolId": "phonon.dos",
          "toolName": "Phonon Dos",
          "toolVersion": "0.1.0"
        }
      ],
      "unfulfilledDesiredOutputs": [],
      "warnings": []
    },
    "capability_outcome": "PLAN_READY",
    "dependency_bindings": [
      {
        "artifactContractVersion": "phase10h.phonon_band.v1",
        "artifactKind": "phonon_band_json",
        "bindingId": "binding_303aad4395ff146fbb2d52f831690216",
        "cardinality": "EXACTLY_ONE",
        "consumerInputPort": "band",
        "consumerStepId": "step_002",
        "mediaType": "application/json",
        "producerOutputPort": "canonical-band",
        "producerStepId": "step_001"
      },
      {
        "artifactContractVersion": "phase10h.phonon_dos.v1",
        "artifactKind": "phonon_dos_json",
        "bindingId": "binding_0fa32a7e77acf87d9c8b926906d17173",
        "cardinality": "EXACTLY_ONE",
        "consumerInputPort": "dos",
        "consumerStepId": "step_002",
        "mediaType": "application/json",
        "producerOutputPort": "canonical-dos",
        "producerStepId": "step_003"
      }
    ],
    "eligibility_resolution": {
      "datasetId": "dataset_1",
      "datasetVersion": "dataset_version_2",
      "diagnostics": [
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "composition.chem_sys_sunburst"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "composition.chem_sys_sunburst"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "composition.chem_sys_sunburst"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "composition.chem_sys_sunburst"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "composition.chem_sys_treemap"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "composition.chem_sys_treemap"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "composition.chem_sys_treemap"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "composition.chem_sys_treemap"
        },
        {
          "code": "TOOL_NOT_AVAILABLE",
          "field": "availability",
          "message": "The tool is not available in the current product/runtime.",
          "repairable": false,
          "toolId": "composition.cluster_2d"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "composition.cluster_2d"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "composition.cluster_2d"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "composition.cluster_2d"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "composition.cluster_2d"
        },
        {
          "code": "TOOL_NOT_AVAILABLE",
          "field": "availability",
          "message": "The tool is not available in the current product/runtime.",
          "repairable": false,
          "toolId": "composition.cluster_3d"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "composition.cluster_3d"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "composition.cluster_3d"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "composition.cluster_3d"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "composition.cluster_3d"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "composition.elements_hist"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "composition.elements_hist"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "composition.elements_hist"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "composition.elements_hist"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "composition.formula_statistics"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "composition.formula_statistics"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "composition.formula_statistics"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "composition.formula_statistics"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "composition.ptable_heatmap"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "composition.ptable_heatmap"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "composition.ptable_heatmap"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "composition.ptable_heatmap"
        },
        {
          "code": "TOOL_NOT_AVAILABLE",
          "field": "availability",
          "message": "The tool is not available in the current product/runtime.",
          "repairable": false,
          "toolId": "composition.ptable_heatmap_splits"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "composition.ptable_heatmap_splits"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "composition.ptable_heatmap_splits"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "composition.ptable_heatmap_splits"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "composition.ptable_heatmap_splits"
        },
        {
          "code": "TOOL_NOT_AVAILABLE",
          "field": "availability",
          "message": "The tool is not available in the current product/runtime.",
          "repairable": false,
          "toolId": "composition.ptable_hists"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "composition.ptable_hists"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "composition.ptable_hists"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "composition.ptable_hists"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "composition.ptable_hists"
        },
        {
          "code": "TOOL_NOT_AVAILABLE",
          "field": "availability",
          "message": "The tool is not available in the current product/runtime.",
          "repairable": false,
          "toolId": "composition.ptable_scatter"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "composition.ptable_scatter"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "composition.ptable_scatter"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "composition.ptable_scatter"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "composition.ptable_scatter"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "composition.summary"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "composition.summary"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "composition.summary"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "composition.summary"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "dataset.composition_space"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "dataset.composition_space"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "dataset.composition_space"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "dataset.composition_space"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "dataset.composition_space"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "dataset.materials_explorer"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "dataset.materials_explorer"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "dataset.materials_explorer"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "dataset.materials_explorer"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "dataset.materials_explorer"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "ml.basic_metrics"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "ml.basic_metrics"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "ml.basic_metrics"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "ml.basic_metrics"
        },
        {
          "code": "TARGET_SEMANTICS_MISMATCH",
          "field": "targetSemantics",
          "message": "Exact target/model semantics do not satisfy the tool contract.",
          "repairable": false,
          "toolId": "ml.basic_metrics"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "ml.basic_metrics"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "ml.basic_metrics"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "ml.classification_evaluation"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "ml.classification_evaluation"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "ml.classification_evaluation"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "ml.classification_evaluation"
        },
        {
          "code": "TARGET_SEMANTICS_MISMATCH",
          "field": "targetSemantics",
          "message": "Exact target/model semantics do not satisfy the tool contract.",
          "repairable": false,
          "toolId": "ml.classification_evaluation"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "ml.classification_evaluation"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "ml.density_scatter"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "ml.density_scatter"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "ml.density_scatter"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "ml.density_scatter"
        },
        {
          "code": "TARGET_SEMANTICS_MISMATCH",
          "field": "targetSemantics",
          "message": "Exact target/model semantics do not satisfy the tool contract.",
          "repairable": false,
          "toolId": "ml.density_scatter"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "ml.density_scatter"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "ml.density_scatter"
        },
        {
          "code": "TOOL_NOT_AVAILABLE",
          "field": "availability",
          "message": "The tool is not available in the current product/runtime.",
          "repairable": false,
          "toolId": "ml.error_by_chem_sys"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "ml.error_by_chem_sys"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "ml.error_by_chem_sys"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "ml.error_by_chem_sys"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "ml.error_by_chem_sys"
        },
        {
          "code": "TOOL_NOT_AVAILABLE",
          "field": "availability",
          "message": "The tool is not available in the current product/runtime.",
          "repairable": false,
          "toolId": "ml.error_by_element"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "ml.error_by_element"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "ml.error_by_element"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "ml.error_by_element"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "ml.error_by_element"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "ml.error_distribution"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "ml.error_distribution"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "ml.error_distribution"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "ml.error_distribution"
        },
        {
          "code": "TARGET_SEMANTICS_MISMATCH",
          "field": "targetSemantics",
          "message": "Exact target/model semantics do not satisfy the tool contract.",
          "repairable": false,
          "toolId": "ml.error_distribution"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "ml.error_distribution"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "ml.error_distribution"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "ml.outlier_table"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "ml.outlier_table"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "ml.outlier_table"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "ml.outlier_table"
        },
        {
          "code": "TARGET_SEMANTICS_MISMATCH",
          "field": "targetSemantics",
          "message": "Exact target/model semantics do not satisfy the tool contract.",
          "repairable": false,
          "toolId": "ml.outlier_table"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "ml.outlier_table"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "ml.outlier_table"
        },
        {
          "code": "TOOL_NOT_AVAILABLE",
          "field": "availability",
          "message": "The tool is not available in the current product/runtime.",
          "repairable": false,
          "toolId": "ml.parity_plot"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "ml.parity_plot"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "ml.parity_plot"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "ml.parity_plot"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "ml.parity_plot"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "ml.regression_evaluation"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "ml.regression_evaluation"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "ml.regression_evaluation"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "ml.regression_evaluation"
        },
        {
          "code": "TARGET_SEMANTICS_MISMATCH",
          "field": "targetSemantics",
          "message": "Exact target/model semantics do not satisfy the tool contract.",
          "repairable": false,
          "toolId": "ml.regression_evaluation"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "ml.regression_evaluation"
        },
        {
          "code": "TOOL_NOT_AVAILABLE",
          "field": "availability",
          "message": "The tool is not available in the current product/runtime.",
          "repairable": false,
          "toolId": "ml.uncertainty_calibration"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "ml.uncertainty_calibration"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "ml.uncertainty_calibration"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "ml.uncertainty_calibration"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "ml.uncertainty_calibration"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "ml.uncertainty_evaluation"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "ml.uncertainty_evaluation"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "ml.uncertainty_evaluation"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "ml.uncertainty_evaluation"
        },
        {
          "code": "TARGET_SEMANTICS_MISMATCH",
          "field": "targetSemantics",
          "message": "Exact target/model semantics do not satisfy the tool contract.",
          "repairable": false,
          "toolId": "ml.uncertainty_evaluation"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "ml.uncertainty_evaluation"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "phonon.animation"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "phonon.animation"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.brillouin_zone"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.brillouin_zone"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.brillouin_zone"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.brillouin_zone"
        },
        {
          "code": "TOOL_NOT_AVAILABLE",
          "field": "availability",
          "message": "The tool is not available in the current product/runtime.",
          "repairable": false,
          "toolId": "structure.chem_env_sunburst"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.chem_env_sunburst"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.chem_env_sunburst"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.chem_env_sunburst"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.chem_env_sunburst"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.composition_from_structure"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.composition_from_structure"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.composition_from_structure"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.composition_from_structure"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.coordination_hist"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.coordination_hist"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.coordination_hist"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.coordination_hist"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.lattice_summary"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.lattice_summary"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.lattice_summary"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.lattice_summary"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.preview_metadata"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.preview_metadata"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.preview_metadata"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.preview_metadata"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.rdf"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.rdf"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.rdf"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.rdf"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.spacegroup_summary"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.spacegroup_summary"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.spacegroup_summary"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.spacegroup_summary"
        },
        {
          "code": "TOOL_NOT_AVAILABLE",
          "field": "availability",
          "message": "The tool is not available in the current product/runtime.",
          "repairable": false,
          "toolId": "structure.structure_2d"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.structure_2d"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.structure_2d"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.structure_2d"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.structure_2d"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.structure_3d"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.structure_3d"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.structure_3d"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.structure_3d"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.summary"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.summary"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.summary"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.summary"
        },
        {
          "code": "TOOL_NOT_AVAILABLE",
          "field": "availability",
          "message": "The tool is not available in the current product/runtime.",
          "repairable": false,
          "toolId": "structure.trajectory_import"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.trajectory_import"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.trajectory_import"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.trajectory_import"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.trajectory_import"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.trajectory_viewer"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.trajectory_viewer"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.trajectory_viewer"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.trajectory_viewer"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.viewer_3d"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.viewer_3d"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.viewer_3d"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.viewer_3d"
        },
        {
          "code": "TOOL_NOT_AVAILABLE",
          "field": "availability",
          "message": "The tool is not available in the current product/runtime.",
          "repairable": false,
          "toolId": "structure.viewer_export_package"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.viewer_export_package"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.viewer_export_package"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.viewer_export_package"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.viewer_export_package"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.viewer_scene"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.viewer_scene"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.viewer_scene"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.viewer_scene"
        },
        {
          "code": "TOOL_NOT_AVAILABLE",
          "field": "availability",
          "message": "The tool is not available in the current product/runtime.",
          "repairable": false,
          "toolId": "structure.viewer_scene_metadata"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.viewer_scene_metadata"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.viewer_scene_metadata"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.viewer_scene_metadata"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.viewer_scene_metadata"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.volumetric_data"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.volumetric_data"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.volumetric_data"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.volumetric_data"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "structure.xrd"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "structure.xrd"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "structure.xrd"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "structure.xrd"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "table.distribution_summary"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "table.distribution_summary"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "table.distribution_summary"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "table.distribution_summary"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "table.distribution_summary"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "table.numeric_summary"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "table.numeric_summary"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "table.numeric_summary"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "table.numeric_summary"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "table.numeric_summary"
        },
        {
          "code": "TOOL_NOT_AVAILABLE",
          "field": "availability",
          "message": "The tool is not available in the current product/runtime.",
          "repairable": false,
          "toolId": "trajectory.viewer"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "trajectory.viewer"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "trajectory.viewer"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "trajectory.viewer"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "trajectory.viewer"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "viz.correlation"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "viz.correlation"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "viz.correlation"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "viz.correlation"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "viz.correlation"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "viz.histogram"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "viz.histogram"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "viz.histogram"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "viz.histogram"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "viz.histogram"
        },
        {
          "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
          "field": "scientificIntents",
          "message": "The tool does not support a requested scientific intent.",
          "repairable": false,
          "toolId": "viz.scatter"
        },
        {
          "code": "CAPABILITY_NEED_UNSUPPORTED",
          "field": "requiredCapabilityNeeds",
          "message": "The tool does not support every required capability need.",
          "repairable": false,
          "toolId": "viz.scatter"
        },
        {
          "code": "PROFILE_PREREQUISITE_MISSING",
          "field": "profile",
          "message": "Required exact DataProfile facts are unavailable.",
          "repairable": false,
          "toolId": "viz.scatter"
        },
        {
          "code": "RESOURCE_KIND_MISMATCH",
          "field": "dataScope.resourceRefs",
          "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
          "repairable": false,
          "toolId": "viz.scatter"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "viz.scatter"
        },
        {
          "code": "REQUIRED_PARAMETER_UNBOUND",
          "field": "parameterBindings",
          "message": "A required parameter has no exact permitted binding.",
          "repairable": false,
          "toolId": "viz.scatter"
        }
      ],
      "eligibleToolIds": [
        "phonon.band",
        "phonon.band_dos",
        "phonon.dos"
      ],
      "evaluatedCandidates": [
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "composition.chem_sys_sunburst",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "composition.chem_sys_sunburst"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "composition.chem_sys_sunburst"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "composition.chem_sys_sunburst"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "composition.chem_sys_sunburst"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "composition.chem_sys_sunburst",
          "toolName": "Composition Chem Sys Sunburst",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "composition_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "composition.chem_sys_treemap",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "composition.chem_sys_treemap"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "composition.chem_sys_treemap"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "composition.chem_sys_treemap"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "composition.chem_sys_treemap"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "composition.chem_sys_treemap",
          "toolName": "Composition Chem Sys Treemap",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "composition_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": false,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "composition.cluster_2d",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "TOOL_NOT_AVAILABLE",
              "field": "availability",
              "message": "The tool is not available in the current product/runtime.",
              "repairable": false,
              "toolId": "composition.cluster_2d"
            },
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "composition.cluster_2d"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "composition.cluster_2d"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "composition.cluster_2d"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "composition.cluster_2d"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "composition.cluster_2d",
          "toolName": "Composition Cluster 2D",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "composition_data",
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": false,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "composition.cluster_3d",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "TOOL_NOT_AVAILABLE",
              "field": "availability",
              "message": "The tool is not available in the current product/runtime.",
              "repairable": false,
              "toolId": "composition.cluster_3d"
            },
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "composition.cluster_3d"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "composition.cluster_3d"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "composition.cluster_3d"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "composition.cluster_3d"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "composition.cluster_3d",
          "toolName": "Composition Cluster 3D",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "composition_data",
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "composition.elements_hist",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "composition.elements_hist"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "composition.elements_hist"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "composition.elements_hist"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "composition.elements_hist"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "composition.elements_hist",
          "toolName": "Composition Elements Hist",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "composition_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "composition.formula_statistics",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "composition.formula_statistics"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "composition.formula_statistics"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "composition.formula_statistics"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "composition.formula_statistics"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "composition.formula_statistics",
          "toolName": "Composition Formula Statistics",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "composition_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "composition.ptable_heatmap",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "composition.ptable_heatmap"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "composition.ptable_heatmap"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "composition.ptable_heatmap"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "composition.ptable_heatmap"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "composition.ptable_heatmap",
          "toolName": "Composition Ptable Heatmap",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "composition_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": false,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "composition.ptable_heatmap_splits",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "TOOL_NOT_AVAILABLE",
              "field": "availability",
              "message": "The tool is not available in the current product/runtime.",
              "repairable": false,
              "toolId": "composition.ptable_heatmap_splits"
            },
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "composition.ptable_heatmap_splits"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "composition.ptable_heatmap_splits"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "composition.ptable_heatmap_splits"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "composition.ptable_heatmap_splits"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "composition.ptable_heatmap_splits",
          "toolName": "Composition Ptable Heatmap Splits",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "composition_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": false,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "composition.ptable_hists",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "TOOL_NOT_AVAILABLE",
              "field": "availability",
              "message": "The tool is not available in the current product/runtime.",
              "repairable": false,
              "toolId": "composition.ptable_hists"
            },
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "composition.ptable_hists"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "composition.ptable_hists"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "composition.ptable_hists"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "composition.ptable_hists"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "composition.ptable_hists",
          "toolName": "Composition Ptable Hists",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "composition_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": false,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "composition.ptable_scatter",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "TOOL_NOT_AVAILABLE",
              "field": "availability",
              "message": "The tool is not available in the current product/runtime.",
              "repairable": false,
              "toolId": "composition.ptable_scatter"
            },
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "composition.ptable_scatter"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "composition.ptable_scatter"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "composition.ptable_scatter"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "composition.ptable_scatter"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "composition.ptable_scatter",
          "toolName": "Composition Ptable Scatter",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "composition_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "composition.summary",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "composition.summary"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "composition.summary"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "composition.summary"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "composition.summary"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "composition.summary",
          "toolName": "Composition Summary",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "composition_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            4,
            0,
            0,
            2,
            "dataset.composition_space",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "dataset.composition_space"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "dataset.composition_space"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "dataset.composition_space"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "dataset.composition_space"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "dataset.composition_space"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "dataset.composition_space",
          "toolName": "Dataset Composition Space",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "composition_data",
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            2,
            "dataset.materials_explorer",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "dataset.materials_explorer"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "dataset.materials_explorer"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "dataset.materials_explorer"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "dataset.materials_explorer"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "dataset.materials_explorer"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "dataset.materials_explorer",
          "toolName": "Dataset Materials Explorer",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            2,
            0,
            0,
            1,
            "ml.basic_metrics",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "ml.basic_metrics"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "ml.basic_metrics"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "ml.basic_metrics"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "ml.basic_metrics"
            },
            {
              "code": "TARGET_SEMANTICS_MISMATCH",
              "field": "targetSemantics",
              "message": "Exact target/model semantics do not satisfy the tool contract.",
              "repairable": false,
              "toolId": "ml.basic_metrics"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "ml.basic_metrics"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "ml.basic_metrics"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "ml.basic_metrics",
          "toolName": "Ml Basic Metrics",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "regression_semantics",
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "ml.classification_evaluation",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "ml.classification_evaluation"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "ml.classification_evaluation"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "ml.classification_evaluation"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "ml.classification_evaluation"
            },
            {
              "code": "TARGET_SEMANTICS_MISMATCH",
              "field": "targetSemantics",
              "message": "Exact target/model semantics do not satisfy the tool contract.",
              "repairable": false,
              "toolId": "ml.classification_evaluation"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "ml.classification_evaluation"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "ml.classification_evaluation",
          "toolName": "Ml Classification Evaluation",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "classification_semantics",
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "ml.density_scatter",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "ml.density_scatter"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "ml.density_scatter"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "ml.density_scatter"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "ml.density_scatter"
            },
            {
              "code": "TARGET_SEMANTICS_MISMATCH",
              "field": "targetSemantics",
              "message": "Exact target/model semantics do not satisfy the tool contract.",
              "repairable": false,
              "toolId": "ml.density_scatter"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "ml.density_scatter"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "ml.density_scatter"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "ml.density_scatter",
          "toolName": "Ml Density Scatter",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "regression_semantics",
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": false,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            4,
            0,
            0,
            1,
            "ml.error_by_chem_sys",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "TOOL_NOT_AVAILABLE",
              "field": "availability",
              "message": "The tool is not available in the current product/runtime.",
              "repairable": false,
              "toolId": "ml.error_by_chem_sys"
            },
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "ml.error_by_chem_sys"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "ml.error_by_chem_sys"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "ml.error_by_chem_sys"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "ml.error_by_chem_sys"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "ml.error_by_chem_sys",
          "toolName": "Ml Error By Chem Sys",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "regression_semantics",
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": false,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            4,
            0,
            0,
            1,
            "ml.error_by_element",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "TOOL_NOT_AVAILABLE",
              "field": "availability",
              "message": "The tool is not available in the current product/runtime.",
              "repairable": false,
              "toolId": "ml.error_by_element"
            },
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "ml.error_by_element"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "ml.error_by_element"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "ml.error_by_element"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "ml.error_by_element"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "ml.error_by_element",
          "toolName": "Ml Error By Element",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "regression_semantics",
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            4,
            0,
            0,
            1,
            "ml.error_distribution",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "ml.error_distribution"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "ml.error_distribution"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "ml.error_distribution"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "ml.error_distribution"
            },
            {
              "code": "TARGET_SEMANTICS_MISMATCH",
              "field": "targetSemantics",
              "message": "Exact target/model semantics do not satisfy the tool contract.",
              "repairable": false,
              "toolId": "ml.error_distribution"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "ml.error_distribution"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "ml.error_distribution"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "ml.error_distribution",
          "toolName": "Ml Error Distribution",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "regression_semantics",
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "ml.outlier_table",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "ml.outlier_table"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "ml.outlier_table"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "ml.outlier_table"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "ml.outlier_table"
            },
            {
              "code": "TARGET_SEMANTICS_MISMATCH",
              "field": "targetSemantics",
              "message": "Exact target/model semantics do not satisfy the tool contract.",
              "repairable": false,
              "toolId": "ml.outlier_table"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "ml.outlier_table"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "ml.outlier_table"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "ml.outlier_table",
          "toolName": "Ml Outlier Table",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "regression_semantics",
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": false,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "ml.parity_plot",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "TOOL_NOT_AVAILABLE",
              "field": "availability",
              "message": "The tool is not available in the current product/runtime.",
              "repairable": false,
              "toolId": "ml.parity_plot"
            },
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "ml.parity_plot"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "ml.parity_plot"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "ml.parity_plot"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "ml.parity_plot"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "ml.parity_plot",
          "toolName": "Ml Parity Plot",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "regression_semantics",
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "ml.regression_evaluation",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "ml.regression_evaluation"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "ml.regression_evaluation"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "ml.regression_evaluation"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "ml.regression_evaluation"
            },
            {
              "code": "TARGET_SEMANTICS_MISMATCH",
              "field": "targetSemantics",
              "message": "Exact target/model semantics do not satisfy the tool contract.",
              "repairable": false,
              "toolId": "ml.regression_evaluation"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "ml.regression_evaluation"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "ml.regression_evaluation",
          "toolName": "Ml Regression Evaluation",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "regression_semantics",
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": false,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "ml.uncertainty_calibration",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "TOOL_NOT_AVAILABLE",
              "field": "availability",
              "message": "The tool is not available in the current product/runtime.",
              "repairable": false,
              "toolId": "ml.uncertainty_calibration"
            },
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "ml.uncertainty_calibration"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "ml.uncertainty_calibration"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "ml.uncertainty_calibration"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "ml.uncertainty_calibration"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "ml.uncertainty_calibration",
          "toolName": "Ml Uncertainty Calibration",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "regression_semantics",
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "ml.uncertainty_evaluation",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "ml.uncertainty_evaluation"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "ml.uncertainty_evaluation"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "ml.uncertainty_evaluation"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "ml.uncertainty_evaluation"
            },
            {
              "code": "TARGET_SEMANTICS_MISMATCH",
              "field": "targetSemantics",
              "message": "Exact target/model semantics do not satisfy the tool contract.",
              "repairable": false,
              "toolId": "ml.uncertainty_evaluation"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "ml.uncertainty_evaluation"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "ml.uncertainty_evaluation",
          "toolName": "Ml Uncertainty Evaluation",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "regression_semantics",
            "tabular_data",
            "uncertainty_semantics"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [
            "phonon_resource"
          ],
          "matchedDesiredOutputs": [
            "plot"
          ],
          "matchedScientificIntents": [
            "phonon_analysis"
          ],
          "rankFacts": [
            1,
            1,
            1,
            0,
            0,
            2,
            "phonon.animation",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "phonon.animation"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "phonon.animation"
            }
          ],
          "satisfiedProfileCapabilities": [
            "phonon_resource"
          ],
          "targetSemanticIds": [],
          "toolId": "phonon.animation",
          "toolName": "Phonon Animation",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": []
        },
        {
          "acceptedResourceIds": [
            "phonon_band_1"
          ],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": true,
          "independentComposable": true,
          "matchedCapabilityNeeds": [
            "phonon_resource"
          ],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [
            "phonon_analysis"
          ],
          "rankFacts": [
            1,
            1,
            4,
            1,
            0,
            2,
            "phonon.band",
            "0.1.0"
          ],
          "reasons": [],
          "satisfiedProfileCapabilities": [
            "phonon_resource"
          ],
          "targetSemanticIds": [],
          "toolId": "phonon.band",
          "toolName": "Phonon Band",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": []
        },
        {
          "acceptedResourceIds": [
            "phonon_band_1",
            "phonon_dos_1"
          ],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": true,
          "independentComposable": true,
          "matchedCapabilityNeeds": [
            "phonon_resource"
          ],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [
            "phonon_analysis"
          ],
          "rankFacts": [
            1,
            1,
            4,
            2,
            0,
            2,
            "phonon.band_dos",
            "0.1.0"
          ],
          "reasons": [],
          "satisfiedProfileCapabilities": [
            "phonon_resource"
          ],
          "targetSemanticIds": [],
          "toolId": "phonon.band_dos",
          "toolName": "Phonon Band Dos",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": []
        },
        {
          "acceptedResourceIds": [
            "phonon_dos_1"
          ],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": true,
          "independentComposable": true,
          "matchedCapabilityNeeds": [
            "phonon_resource"
          ],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [
            "phonon_analysis"
          ],
          "rankFacts": [
            1,
            1,
            4,
            1,
            0,
            2,
            "phonon.dos",
            "0.1.0"
          ],
          "reasons": [],
          "satisfiedProfileCapabilities": [
            "phonon_resource"
          ],
          "targetSemanticIds": [],
          "toolId": "phonon.dos",
          "toolName": "Phonon Dos",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": []
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            2,
            "structure.brillouin_zone",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.brillouin_zone"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.brillouin_zone"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.brillouin_zone"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.brillouin_zone"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.brillouin_zone",
          "toolName": "Structure Brillouin Zone",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "reciprocal_space_resource",
            "structure_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": false,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            2,
            "structure.chem_env_sunburst",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "TOOL_NOT_AVAILABLE",
              "field": "availability",
              "message": "The tool is not available in the current product/runtime.",
              "repairable": false,
              "toolId": "structure.chem_env_sunburst"
            },
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.chem_env_sunburst"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.chem_env_sunburst"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.chem_env_sunburst"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.chem_env_sunburst"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.chem_env_sunburst",
          "toolName": "Structure Chem Env Sunburst",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "structure_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            2,
            "structure.composition_from_structure",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.composition_from_structure"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.composition_from_structure"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.composition_from_structure"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.composition_from_structure"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.composition_from_structure",
          "toolName": "Structure Composition From Structure",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "structure_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            4,
            0,
            0,
            2,
            "structure.coordination_hist",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.coordination_hist"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.coordination_hist"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.coordination_hist"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.coordination_hist"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.coordination_hist",
          "toolName": "Structure Coordination Hist",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "structure_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            2,
            "structure.lattice_summary",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.lattice_summary"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.lattice_summary"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.lattice_summary"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.lattice_summary"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.lattice_summary",
          "toolName": "Structure Lattice Summary",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "structure_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            2,
            0,
            0,
            2,
            "structure.preview_metadata",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.preview_metadata"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.preview_metadata"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.preview_metadata"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.preview_metadata"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.preview_metadata",
          "toolName": "Structure Preview Metadata",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "structure_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            4,
            0,
            0,
            2,
            "structure.rdf",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.rdf"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.rdf"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.rdf"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.rdf"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.rdf",
          "toolName": "Structure Rdf",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "structure_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            2,
            "structure.spacegroup_summary",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.spacegroup_summary"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.spacegroup_summary"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.spacegroup_summary"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.spacegroup_summary"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.spacegroup_summary",
          "toolName": "Structure Spacegroup Summary",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "structure_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": false,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            2,
            "structure.structure_2d",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "TOOL_NOT_AVAILABLE",
              "field": "availability",
              "message": "The tool is not available in the current product/runtime.",
              "repairable": false,
              "toolId": "structure.structure_2d"
            },
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.structure_2d"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.structure_2d"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.structure_2d"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.structure_2d"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.structure_2d",
          "toolName": "Structure Structure 2D",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "structure_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": "primary_interactive_structure_view",
          "costClass": 2,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            2,
            "structure.structure_3d",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.structure_3d"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.structure_3d"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.structure_3d"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.structure_3d"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.structure_3d",
          "toolName": "Structure Structure 3D",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "structure_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            2,
            0,
            0,
            2,
            "structure.summary",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.summary"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.summary"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.summary"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.summary"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.summary",
          "toolName": "Structure Summary",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "structure_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": false,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            2,
            0,
            0,
            2,
            "structure.trajectory_import",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "TOOL_NOT_AVAILABLE",
              "field": "availability",
              "message": "The tool is not available in the current product/runtime.",
              "repairable": false,
              "toolId": "structure.trajectory_import"
            },
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.trajectory_import"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.trajectory_import"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.trajectory_import"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.trajectory_import"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.trajectory_import",
          "toolName": "Structure Trajectory Import",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "trajectory_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            2,
            "structure.trajectory_viewer",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.trajectory_viewer"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.trajectory_viewer"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.trajectory_viewer"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.trajectory_viewer"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.trajectory_viewer",
          "toolName": "Structure Trajectory Viewer",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "trajectory_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": "primary_interactive_structure_view",
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            4,
            0,
            0,
            1,
            "structure.viewer_3d",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.viewer_3d"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.viewer_3d"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.viewer_3d"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.viewer_3d"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.viewer_3d",
          "toolName": "Structure Viewer 3D",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "structure_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": false,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            2,
            "structure.viewer_export_package",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "TOOL_NOT_AVAILABLE",
              "field": "availability",
              "message": "The tool is not available in the current product/runtime.",
              "repairable": false,
              "toolId": "structure.viewer_export_package"
            },
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.viewer_export_package"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.viewer_export_package"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.viewer_export_package"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.viewer_export_package"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.viewer_export_package",
          "toolName": "Structure Viewer Export Package",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "structure_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": "primary_interactive_structure_view",
          "costClass": 2,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            4,
            0,
            0,
            2,
            "structure.viewer_scene",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.viewer_scene"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.viewer_scene"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.viewer_scene"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.viewer_scene"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.viewer_scene",
          "toolName": "Structure Viewer Scene",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "structure_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": false,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            2,
            0,
            0,
            2,
            "structure.viewer_scene_metadata",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "TOOL_NOT_AVAILABLE",
              "field": "availability",
              "message": "The tool is not available in the current product/runtime.",
              "repairable": false,
              "toolId": "structure.viewer_scene_metadata"
            },
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.viewer_scene_metadata"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.viewer_scene_metadata"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.viewer_scene_metadata"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.viewer_scene_metadata"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.viewer_scene_metadata",
          "toolName": "Structure Viewer Scene Metadata",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "structure_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            2,
            "structure.volumetric_data",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.volumetric_data"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.volumetric_data"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.volumetric_data"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.volumetric_data"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.volumetric_data",
          "toolName": "Structure Volumetric Data",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "volumetric_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            4,
            0,
            0,
            2,
            "structure.xrd",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "structure.xrd"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "structure.xrd"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "structure.xrd"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "structure.xrd"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "structure.xrd",
          "toolName": "Structure Xrd",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "structure_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "table.distribution_summary",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "table.distribution_summary"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "table.distribution_summary"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "table.distribution_summary"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "table.distribution_summary"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "table.distribution_summary"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "table.distribution_summary",
          "toolName": "Table Distribution Summary",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "table.numeric_summary",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "table.numeric_summary"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "table.numeric_summary"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "table.numeric_summary"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "table.numeric_summary"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "table.numeric_summary"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "table.numeric_summary",
          "toolName": "Table Numeric Summary",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 2,
          "eligible": false,
          "independentComposable": false,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            2,
            "trajectory.viewer",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "TOOL_NOT_AVAILABLE",
              "field": "availability",
              "message": "The tool is not available in the current product/runtime.",
              "repairable": false,
              "toolId": "trajectory.viewer"
            },
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "trajectory.viewer"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "trajectory.viewer"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "trajectory.viewer"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "trajectory.viewer"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "trajectory.viewer",
          "toolName": "Trajectory Viewer",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "trajectory_resource"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "table",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            4,
            0,
            0,
            1,
            "viz.correlation",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "viz.correlation"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "viz.correlation"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "viz.correlation"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "viz.correlation"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "viz.correlation"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "viz.correlation",
          "toolName": "Viz Correlation",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "viz.histogram",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "viz.histogram"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "viz.histogram"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "viz.histogram"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "viz.histogram"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "viz.histogram"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "viz.histogram",
          "toolName": "Viz Histogram",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "tabular_data"
          ]
        },
        {
          "acceptedResourceIds": [],
          "bindingDomains": [],
          "collisionGroup": null,
          "costClass": 1,
          "eligible": false,
          "independentComposable": true,
          "matchedCapabilityNeeds": [],
          "matchedDesiredOutputs": [
            "plot",
            "summary",
            "warnings"
          ],
          "matchedScientificIntents": [],
          "rankFacts": [
            0,
            0,
            3,
            0,
            0,
            1,
            "viz.scatter",
            "0.1.0"
          ],
          "reasons": [
            {
              "code": "SCIENTIFIC_INTENT_UNSUPPORTED",
              "field": "scientificIntents",
              "message": "The tool does not support a requested scientific intent.",
              "repairable": false,
              "toolId": "viz.scatter"
            },
            {
              "code": "CAPABILITY_NEED_UNSUPPORTED",
              "field": "requiredCapabilityNeeds",
              "message": "The tool does not support every required capability need.",
              "repairable": false,
              "toolId": "viz.scatter"
            },
            {
              "code": "PROFILE_PREREQUISITE_MISSING",
              "field": "profile",
              "message": "Required exact DataProfile facts are unavailable.",
              "repairable": false,
              "toolId": "viz.scatter"
            },
            {
              "code": "RESOURCE_KIND_MISMATCH",
              "field": "dataScope.resourceRefs",
              "message": "Exact resource kinds or cardinality do not satisfy the tool input contract.",
              "repairable": false,
              "toolId": "viz.scatter"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "viz.scatter"
            },
            {
              "code": "REQUIRED_PARAMETER_UNBOUND",
              "field": "parameterBindings",
              "message": "A required parameter has no exact permitted binding.",
              "repairable": false,
              "toolId": "viz.scatter"
            }
          ],
          "satisfiedProfileCapabilities": [],
          "targetSemanticIds": [],
          "toolId": "viz.scatter",
          "toolName": "Viz Scatter",
          "toolVersion": "0.1.0",
          "unsatisfiedProfileCapabilities": [
            "tabular_data"
          ]
        }
      ],
      "intentHash": "af647d24626215fa9a56999c46e5154aef6baf3bc9a77f688049b7bc9cb7d9d3",
      "intentId": "intent_af647d24626215fa9a56999c",
      "profileContractVersion": "2.0",
      "profileId": "profile_1",
      "profileSemanticHash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "provenance": {
        "resolver": "deterministic_eligibility_resolver",
        "resolverVersion": "1.0"
      },
      "registrySnapshotHash": "465482cd226ed056aec57ab4437f90d85b4c8c12507ca62a50f6574b3f8cade0",
      "registrySnapshotId": "registry_465482cd226ed056aec57ab4",
      "rejectedToolIds": [
        "composition.chem_sys_sunburst",
        "composition.chem_sys_treemap",
        "composition.cluster_2d",
        "composition.cluster_3d",
        "composition.elements_hist",
        "composition.formula_statistics",
        "composition.ptable_heatmap",
        "composition.ptable_heatmap_splits",
        "composition.ptable_hists",
        "composition.ptable_scatter",
        "composition.summary",
        "dataset.composition_space",
        "dataset.materials_explorer",
        "ml.basic_metrics",
        "ml.classification_evaluation",
        "ml.density_scatter",
        "ml.error_by_chem_sys",
        "ml.error_by_element",
        "ml.error_distribution",
        "ml.outlier_table",
        "ml.parity_plot",
        "ml.regression_evaluation",
        "ml.uncertainty_calibration",
        "ml.uncertainty_evaluation",
        "phonon.animation",
        "structure.brillouin_zone",
        "structure.chem_env_sunburst",
        "structure.composition_from_structure",
        "structure.coordination_hist",
        "structure.lattice_summary",
        "structure.preview_metadata",
        "structure.rdf",
        "structure.spacegroup_summary",
        "structure.structure_2d",
        "structure.structure_3d",
        "structure.summary",
        "structure.trajectory_import",
        "structure.trajectory_viewer",
        "structure.viewer_3d",
        "structure.viewer_export_package",
        "structure.viewer_scene",
        "structure.viewer_scene_metadata",
        "structure.volumetric_data",
        "structure.xrd",
        "table.distribution_summary",
        "table.numeric_summary",
        "trajectory.viewer",
        "viz.correlation",
        "viz.histogram",
        "viz.scatter"
      ],
      "resolutionHash": "4b67a9ae7ddec82d1f57ad87b60e5cc657204a0c8616f4d786b94206538b7ca8",
      "resolutionId": "resolution_4b67a9ae7ddec82d1f57ad87",
      "resourceIdentities": [
        {
          "kind": "phonon",
          "objectHash": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
          "objectId": "phonon_band_1",
          "objectType": "PhononBand"
        },
        {
          "kind": "phonon",
          "objectHash": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
          "objectId": "phonon_dos_1",
          "objectType": "PhononDos"
        }
      ],
      "schemaVersion": "1.0",
      "warnings": []
    },
    "enqueued": false,
    "error_code": null,
    "executed": false,
    "graph_hash": "815f559ff6d4cf559a69e938cf3c4e66ec10eeecaf9a7b64d457bd602163f52f",
    "intent": {
      "ambiguities": [],
      "clarification": {
        "answers": [],
        "maxQuestionsPerRound": 3,
        "maxRounds": 1,
        "questions": [],
        "round": 0
      },
      "constraints": {
        "clarificationAllowed": true,
        "costPreference": null,
        "descriptiveOnly": false,
        "excludeResourceIds": [],
        "excludeScientificIntents": [],
        "forbidDerivedInterpretation": false,
        "groupIds": [],
        "includeResourceIds": [
          "phonon_band_1",
          "phonon_dos_1"
        ],
        "includeScientificIntents": [],
        "maxAnalyses": null,
        "maxToolCalls": null,
        "modelIds": [],
        "outputPreferences": [],
        "targetIds": [],
        "timePreference": null
      },
      "dataScope": {
        "datasetId": "dataset_1",
        "datasetVersion": "dataset_version_2",
        "groupIds": [],
        "modelIds": [],
        "origin": "USER_EXPLICIT",
        "profileContractVersion": "2.0",
        "profileId": "profile_1",
        "profileSemanticHash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "resourceRefs": [
          {
            "kind": "phonon",
            "objectHash": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "objectId": "phonon_band_1",
            "objectType": "PhononBand",
            "origin": "USER_EXPLICIT"
          },
          {
            "kind": "phonon",
            "objectHash": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
            "objectId": "phonon_dos_1",
            "objectType": "PhononDos",
            "origin": "USER_EXPLICIT"
          }
        ],
        "sampleIds": []
      },
      "datasetId": "dataset_1",
      "desiredOutputs": [
        "summary",
        "warnings",
        "plot",
        "table"
      ],
      "intentHash": "af647d24626215fa9a56999c46e5154aef6baf3bc9a77f688049b7bc9cb7d9d3",
      "intentId": "intent_af647d24626215fa9a56999c",
      "language": "en",
      "missingFacts": [],
      "normalizedGoal": "Analyze this phonon calculation.",
      "optionalCapabilityNeeds": [],
      "outcome": "READY",
      "profileId": "profile_1",
      "provenance": {
        "answerBindings": [],
        "createdAt": "2026-07-30T00:00:00+00:00",
        "model": "bounded-rules-v1",
        "parentIntentId": null,
        "promptVersion": "phase10l1.intent.v1",
        "provider": "deterministic_mock"
      },
      "rawGoal": "Analyze this phonon calculation.",
      "requiredCapabilityNeeds": [
        "phonon_resource"
      ],
      "schemaVersion": "1.0",
      "scientificIntents": [
        "phonon_analysis"
      ],
      "targetSemantics": [],
      "unsupportedReasons": [],
      "warnings": []
    },
    "intent_id": "intent_af647d24626215fa9a56999c",
    "intent_outcome": "READY",
    "job_id": "job_041bd32f00364bb8ada11416",
    "ok": true,
    "plan": {
      "assumptions": [
        "Capability selection used exact persisted Intent/Profile/Registry identities."
      ],
      "datasetId": "dataset_1",
      "dependencyBindings": [
        {
          "artifactContractVersion": "phase10h.phonon_band.v1",
          "artifactKind": "phonon_band_json",
          "bindingId": "binding_303aad4395ff146fbb2d52f831690216",
          "cardinality": "EXACTLY_ONE",
          "consumerInputPort": "band",
          "consumerStepId": "step_002",
          "mediaType": "application/json",
          "producerOutputPort": "canonical-band",
          "producerStepId": "step_001"
        },
        {
          "artifactContractVersion": "phase10h.phonon_dos.v1",
          "artifactKind": "phonon_dos_json",
          "bindingId": "binding_0fa32a7e77acf87d9c8b926906d17173",
          "cardinality": "EXACTLY_ONE",
          "consumerInputPort": "dos",
          "consumerStepId": "step_002",
          "mediaType": "application/json",
          "producerOutputPort": "canonical-dos",
          "producerStepId": "step_003"
        }
      ],
      "expectedArtifacts": [
        {
          "fromStepId": "step_001",
          "name": "phonon_band_phonon_band_json.json",
          "type": "phonon_band_json"
        },
        {
          "fromStepId": "step_002",
          "name": "phonon_band_dos_phonon_band_dos_json.json",
          "type": "phonon_band_dos_json"
        },
        {
          "fromStepId": "step_003",
          "name": "phonon_dos_phonon_dos_json.json",
          "type": "phonon_dos_json"
        }
      ],
      "goal": "Analyze this phonon calculation.",
      "graphHash": "815f559ff6d4cf559a69e938cf3c4e66ec10eeecaf9a7b64d457bd602163f52f",
      "profileId": "profile_1",
      "schemaVersion": "0.2",
      "steps": [
        {
          "constraints": null,
          "inputRefs": [
            {
              "columnName": null,
              "fieldRole": "band",
              "objectType": "PhononBand",
              "ref": "phonon_band_1",
              "refType": "normalized_object"
            }
          ],
          "output": {
            "artifactTypes": [
              "phonon_band_json",
              "phonon_summary_json",
              "phonon_report_json",
              "phonon_manifest_json",
              "plotly_json",
              "table_json",
              "recipe_json"
            ],
            "displayTarget": "phonon"
          },
          "params": {},
          "purpose": "Satisfy the validated structured AnalysisIntent with an eligible registered capability.",
          "reason": "Selected from exact Intent, DataProfile, Registry, and parameter-binding facts.",
          "stepId": "step_001",
          "toolId": "phonon.band"
        },
        {
          "constraints": null,
          "inputRefs": [],
          "output": {
            "artifactTypes": [
              "phonon_band_dos_json",
              "phonon_summary_json",
              "phonon_compatibility_json",
              "plotly_json",
              "table_json",
              "phonon_manifest_json",
              "recipe_json"
            ],
            "displayTarget": "phonon"
          },
          "params": {},
          "purpose": "Satisfy the validated structured AnalysisIntent with an eligible registered capability.",
          "reason": "Selected from exact Intent, DataProfile, Registry, and parameter-binding facts.",
          "stepId": "step_002",
          "toolId": "phonon.band_dos"
        },
        {
          "constraints": null,
          "inputRefs": [
            {
              "columnName": null,
              "fieldRole": "dos",
              "objectType": "PhononDos",
              "ref": "phonon_dos_1",
              "refType": "normalized_object"
            }
          ],
          "output": {
            "artifactTypes": [
              "phonon_dos_json",
              "phonon_summary_json",
              "phonon_report_json",
              "phonon_manifest_json",
              "plotly_json",
              "table_json",
              "recipe_json"
            ],
            "displayTarget": "phonon"
          },
          "params": {},
          "purpose": "Satisfy the validated structured AnalysisIntent with an eligible registered capability.",
          "reason": "Selected from exact Intent, DataProfile, Registry, and parameter-binding facts.",
          "stepId": "step_003",
          "toolId": "phonon.dos"
        }
      ],
      "toolRegistryVersion": "0.1.0",
      "warnings": []
    },
    "plan_hash": "e774978ac1f1ed04ab13ff6940c6f87749878a0a52eb1f7de4cbdfed1d0fff29",
    "plan_id": "plan_c4f7db491ad542f79ed6387f",
    "plan_schema_version": "0.2",
    "plan_source": "capability_planner",
    "planner_provider": "mock",
    "provider_visible_tool_ids": [
      "phonon.band",
      "phonon.band_dos",
      "phonon.dos"
    ],
    "topological_order": [
      "step_001",
      "step_003",
      "step_002"
    ],
    "validation_errors": []
  },
  "readyPersisted": {
    "jobs": 1,
    "plannedBindings": 2,
    "plans": 1
  }
}
```
