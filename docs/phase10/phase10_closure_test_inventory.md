# Phase 10 Closure Test Inventory

## Existing assets

The audit found dedicated adapter, routing, schema, periodic mathematics,
renderer, accessibility, picking, supercell, clipping, export, and browser
tests. Re-running all historical browser suites in every CI run would duplicate
coverage and exceed the intended closure budget.

## Selected tests

- `tests/integration/test_phase10_product_closure.py`: two bounded local
  composition tests plus one service-backed formal viewer test.
- `phase10ProductClosure.test.ts`: two frontend composition/fallback tests.
- `phase10-product-closure-browser-evidence.mjs`: one product-path browser
  suite with Chromium full coverage and Firefox/WebKit/mobile smoke.
- `phase10-closure-evidence-check.mjs`: fast committed-evidence integrity gate.

The inventory, commands, exit codes, and selected historical test files are
machine-readable in `test_inventory.json`. Tests use bounded deterministic
orthogonal, triclinic, self-periodic, degraded, and refused cases; no giant or
random fixture is committed.
