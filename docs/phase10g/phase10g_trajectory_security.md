# Security Review

Trajectory payloads are inert data. Exact field allowlists and recursive scans reject executable keys, JavaScript/HTML markers, callbacks, modules, shaders, remote URLs/frames/assets, file URLs, and private absolute paths. Metadata is flat and bounded; provenance cannot include environment, hostname, username, tokens, or paths.

Numeric validation rejects nonfinite values, excessive magnitude, singular/ill-conditioned lattices, count mismatch, and overflow/cap bypass. JSON has no compressed/binary escape hatch. No parser, notebook, script, filesystem input, network call, real LLM, dependency, adapter, or renderer was added.

Generated audits report `NO_EXTERNAL_NETWORK_REQUESTS` and `NO_SECRET_PATTERN_HITS`.
