# Phase 11 Support and Validation Cross-Matrix

Input support, Tool validation level, scientific reference strength, platform integration, and coverage
verdict are independent fields. In particular:

| Evidence | May establish | Does not establish |
| --- | --- | --- |
| Direct platform parser/runtime path | input-path support | independent numeric truth |
| Internal regression | deterministic software behavior | cross-library correctness |
| `PASS_INVARIANT` benchmark | stated invariant | numeric reference equality |
| Linux/Windows replay | locked-environment invariant agreement | universal numeric reproducibility |
| Browser evidence | rendering and interaction | scientific numeric equality |
| Service evidence | persistence, queue, identity, lineage | scientific numeric correctness |
| Mapping-only example | source-to-platform mapping | verified official reference |
