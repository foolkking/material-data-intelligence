# Phase 10F-17 Integrated Plan

Baseline: `5e7474be92e0ef75bed7a91ec5309c7fdea9e7f0` on `master`, clean.

The implementation keeps `viewer_scene.v1` immutable. The frontend validates the artifact, maps it to canonical atoms, derives bounded periodic view state, renders replicas with instancing, and preserves backend job semantics. Work closes mathematics, periodic identity, minimum-image measurements, bounded supercells, browser evidence, security review, tests, and CI.

The renderer accepts repeats from `1x1x1` through `3x3x3`, subject to derived caps. Displayed-position measurement remains the default; minimum-image mode is explicit. Cross-boundary bonds are not inferred because the canonical bond contract has no image endpoint.
