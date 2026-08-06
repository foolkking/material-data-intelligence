# Phase 10M Final Capability Matrix

| Capability | Authority | Workspace surface | Status | Explicit limits |
| --- | --- | --- | --- | --- |
| Workspace persistence | ScientificWorkspace 1.0 | route/list/Save/history | READY | one Workspace per Job |
| Workspace shell | M2 route and panel contracts | nine typed groups | READY | one active panel |
| canonical selection | WorkspaceSelectionContext 1.0 | URL/store/Inspector | READY_WITH_EXPLICIT_LIMITS | formal mappings only |
| Artifact Gallery | M4 renderer registry | Results | READY | metadata-first |
| Dataset Explorer | dataset materials contract | Data/Results | READY | bounded samples |
| Materials ML | ML evaluation contracts | Results | READY | existing evaluation types |
| Composition Space | composition contract | Results | READY | stable sample identities |
| Structure Viewer | production renderer | Results | READY_WITH_EXPLICIT_LIMITS | approved structure contract |
| Trajectory Viewer | production renderer | Results | READY_WITH_EXPLICIT_LIMITS | no RDF/MSD/diffusion |
| Phonon Viewer | production renderer | Results | READY_WITH_EXPLICIT_LIMITS | current band/DOS products |
| Brillouin Zone Viewer | production renderer | Results | READY_WITH_EXPLICIT_LIMITS | formal reciprocal mappings |
| Volumetric Viewer | production renderer | Results | READY_WITH_EXPLICIT_LIMITS | current bounded fields/caps |
| interpretation | GroundedScientificInterpretation | Findings | READY_WITH_EXPLICIT_LIMITS | no invention; may be unavailable |
| evidence | ScientificEvidenceBundle | Evidence | READY | exact IDs/hashes |
| Report | ReportCompositionSnapshot 1.0 | Report | READY | immutable after finalize |
| Recipe | RecipeReplayManifest 1.0 | Report detail | READY | non-executable |
| Save | Workspace PATCH/ETag | header | READY | explicit, no automatic merge |
| Reload | server + URL precedence | route | READY | transient state discarded |
| Recovery | persisted source authorities | typed states | READY_WITH_EXPLICIT_LIMITS | no offline/latest rebinding |
| mobile | one-surface model | 390x844 | READY | no compressed three-column UI |
| accessibility | semantic/keyboard/focus contracts | all core panels | READY_WITH_EXPLICIT_LIMITS | tested product journey |
| legacy records | historical projection | read-only panels | LEGACY_READ_ONLY | no identity upgrade |
| unknown contract | inert metadata | generic fallback | UNSUPPORTED | no renderer guessing |
