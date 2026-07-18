# Phase 10J-1 Volumetric Parser Security Review

Uploaded text, comments, filenames, atoms, dimensions, numbers, and trailing sections are untrusted. Trusted code is the allowlisted detector/parser, fixed quantity maps, Phase 10J validators, Tool Registry, PlanValidator, QueueWorkerRuntime, and local artifact exporter.

Controls include source-byte precheck; bounded head, line, token, atom, dimension, voxel, value, field, payload, metadata, warning, and compression limits; finite-only numerics; exact single-file input; strict params; typed malformed/truncated/extra-value/null-byte/over-cap failures; and safe raw fallback only for contract-default high-ratio gzip. Multi-orbital CUBE is rejected and VASP augmentation is never silently merged.

Canonical output is inert JSON plus little-endian numeric bytes. There is no pickle, object array, JavaScript, HTML, CSS, shader, module, iframe, URL, remote asset, network call, arbitrary local path, source-controlled filename, notebook, script execution, or real LLM. No dependency or lockfile changed.

Required evidence markers are `NO_VOLUMETRIC_PARSER_EXTERNAL_NETWORK_REQUESTS` and `NO_SECRET_PATTERN_HITS`.
