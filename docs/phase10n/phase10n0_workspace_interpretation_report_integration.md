# Phase 10N-0 Workspace, Interpretation, Report and Recipe Integration

Future N1-N5 products reuse the existing generic persistence and strict M4/M5 authority.
No Workspace, Report or Recipe authority change is proposed.

| Capability | Workspace surface | Selection | Projected facts | Report / Recipe |
| --- | --- | --- | --- | --- |
| N1 | site coordination table, structure overlay, algorithm comparison | exact structure/site/neighbor/image | CN, weights, distances, coverage, warnings | table/plot; exact algorithm/version/params |
| N2 | polyhedron overlay, environment/distortion table, site Inspector | N1 site and neighbor identities | geometry class, score, distortion, unsupported reasons | static table/figure; N1 dependency retained |
| N3 | experimental/theoretical overlay, peak and match tables | experimental/theoretical peak IDs | matched/unmatched peaks, residuals, coverage | static plot/tables; preprocessing/matching policy |
| N4 | RDF, MSD and fit diagnostics linked to trajectory | exact trajectory/atom/frame/window | curves, fit window, diagnostics, exclusions | plots/tables; unwrapping/time/correction policy |
| N5 | Band, DOS and combined view with BZ linkage | exact k-point/path/band/spin/channel | gap/classification threshold, DOS channels, reference | plot/tables; exact supplied source and energy reference |

Heavy renderers remain active-only with a static table/text alternative. Selection
compatibility is explicit; a consumer-only Viewer is not represented as a production
emitter. Unknown versions use inert fallback and never guess by file name or MIME type.

Interpretation projectors expose only bounded computed facts, coverage, warnings,
diagnostics, algorithm/version, parameters, units and unsupported conclusions. The LLM
does not recompute values. Missing projector or interpretation leaves methods/results
readable and findings unavailable.

Report source eligibility includes approved figures/tables/facts with mandatory warnings,
limitations, failures and provenance. Recipe retains Profile, Intent, Eligibility, Plan,
tools, versions, params, dependency ports, source hashes and execution-disabled flags.
Report does not compute and Recipe does not execute.
