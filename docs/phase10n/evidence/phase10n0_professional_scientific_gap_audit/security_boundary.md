# Phase 10N-0 Performance, Security and Resource Caps

These are development caps proposed for future phase acceptance, not production capacity
claims. A phase may lower a cap after measured evidence but may not silently raise it.

| Phase | Proposed hard caps |
| --- | --- |
| N1 | 32 structures/request; 5,000 sites/structure; 1,000 neighbor candidates/site; 2 algorithms; 50,000 retained rows; 120 s Adapter timeout |
| N2 | 5,000 centers; 64 vertices and 128 faces/polyhedron; 32 environment classes; 10,000 overlay objects; 120 s timeout |
| N3 | 200,000 experimental points; 20,000 theoretical peaks; 10,000 detected peaks; 10,000 matched pairs; 32 MiB source; 120 s timeout |
| N4 | 20,000 frames; 20,000 atoms/frame; 64 species pairs; 32 time windows; 8,192 RDF bins; 64 fit candidates; 300 s timeout |
| N5 | 4,096 bands; 65,536 k-points; 262,144 DOS points; 2 spin channels; 512 projection channels; 500,000 display plot points; 180 s timeout |

N1-N5 must measure small, medium and near-cap fixtures before finalizing caps. Existing
Artifact payload limits, worker cancellation and timeout behavior remain authoritative.

## Security seal

All sources are untrusted inert data. Future parsers and Adapters must enforce bounded
bytes/depth/arrays, strict UTF-8, duplicate JSON-key rejection, `__proto__`/prototype-key
rejection, finite-number checks, NaN/Infinity rejection, compressed-file expansion caps,
parse timeout and exact checksum binding. Payloads may not contain executable HTML,
JavaScript, iframe/module code, external runtime URL behavior, shell commands, notebooks,
or filesystem paths.

```text
NO_ARBITRARY_PYTHON = PASS
NO_SHELL_AUTHORITY = PASS
NO_FILESYSTEM_AUTHORITY = PASS
NO_NOTEBOOK_OR_SCRIPT_EXECUTION = PASS
NO_EXTERNAL_SCIENTIFIC_API_AT_RUNTIME = PASS
NO_ARTIFACT_HTML_OR_JAVASCRIPT_EXECUTION = PASS
NO_CROSS_PROJECT_OR_CROSS_JOB_BINDING = PASS
NO_STALE_OR_LATEST_REBINDING = PASS
NO_CHECKSUM_BYPASS = PASS
NO_SECRET_PRIVATE_PATH_OR_STACK_DISCLOSURE = PASS
NO_RECOMMENDATION_OR_RECIPE_EXECUTION = PASS
```

The browser remains a presentation consumer. It does not perform coordination, peak
detection/matching, unwrapping, diffusion fitting, band-gap calculation or DOS
integration.
