# Release Security Model

- The LLM is a bounded Planner, Router, and Explainer. It is not a scientific executor and cannot directly execute arbitrary Python, shell, filesystem, or network operations.
- Every executable ToolCall is validated against the 62-entry Tool Registry and dispatched to a registered Adapter.
- Artifacts are inert data. HTML, JavaScript, iframes, dynamic modules, external Artifact URLs, and Artifact-supplied renderer code do not execute.
- Recipes and recommendations are non-executable.
- Project, Job, source version, resource ID, contract, checksum, and lineage form exact identity. Latest, nearest, filename, MIME, array position, or fuzzy rebinding is forbidden.
- Cross-project and cross-Job resources are rejected. Stale sources and hash mismatches are rejected.
- `DEEPSEEK_KEY` is the only live-provider key source. Values, prefixes, lengths, hashes, and raw secret-bearing outputs must not enter prompts, logs, Artifacts, Recipes, Reports, or evidence.
