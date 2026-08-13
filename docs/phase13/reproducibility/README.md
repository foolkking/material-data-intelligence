# Initial Release Reproducibility

This package is the human companion to `manifest.json` (`931d6214cb11dbcad628f5b33ea97e043bbfeb54fbccc2f8c87cffebad9537e2`). It validates current contracts without creating a new Phase 13-2 attempt or a second E2E authority.

## Mode A: deterministic reproduction

Required. No `DEEPSEEK_KEY` and no real LLM calls.

```powershell
uv sync --frozen --extra test
uv run python scripts/generate_phase13_3_documentation_reproducibility.py
uv run python -m pytest -q tests/test_phase13_3_documentation_reproducibility.py
```

For service-backed checks, start PostgreSQL, Redis, and MinIO as documented in [Quick Start](../release/quick-start.md). The retained Attempt 6 harness remains the full real-user E2E authority; this package verifies its current inputs, fixtures, prompts, contracts, and references.

## Mode B: optional DeepSeek verification

Optional and not run by Phase 13-3. Set `DEEPSEEK_KEY` and use the existing bounded provider verification only after Mode A passes. Models are `deepseek-v4-flash` and `deepseek-v4-pro`; retry-until-pass is forbidden. Provider PASS is not science PASS.

## Demo entries

- [Demo 1: Dataset Intelligence + Composition Space](demo1.md)
- [Demo 2: Materials ML](demo2.md)
- [Demo 3: Structure + coordination + local environment + polyhedra + experimental XRD](demo3.md)
- [Demo 4: Trajectory + RDF + MSD + diffusion](demo4.md)
- [Demo 5: Phonon + Brillouin Zone](demo5.md)
- [Demo 6: Volumetric](demo6.md)
- [Demo 7: Electronic Band + DOS](demo7.md)
