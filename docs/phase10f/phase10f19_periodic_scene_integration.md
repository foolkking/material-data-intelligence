# Phase 10F-19 Periodic Scene Integration Hardening

## Scope

This phase closes adapter -> scene -> manifest -> JSON preview -> inspector
metadata consistency. It does not add or modify rendering, planning, runtime, or
execution authority.

## Contract

`viewer_scene.v2` retains its Phase 10F-18 bond identity and adds exact
capability metadata. Periodic structure, periodic bonds, cross-boundary bonds,
and emitted neighbor graph are true. Trajectory, phonon, and volumetric support
are false. Capability overclaims are validation failures. v1 is unchanged.

`phase10f19.viewer_assets_manifest.v2` identifies the v2 scene contract,
periodic topology, and explicitly records that renderer and WebGL code are not
included. Executable assets and external resources remain `none`. The previous
manifest schema remains validator-compatible for historical artifacts.

## Preview

The JSON preview reports formula/sites/lattice, canonical bond count,
cross-boundary count, self-periodic count, emitted neighbor relationships,
security flags, and artifact renderer status. Endpoint rows use the same
`site_index@[image_offset]` identity as the contract and inspector.

## Security

Capabilities are fixed application-owned fields. They cannot provide code,
URLs, modules, renderer configuration, or external assets. Evidence reports
`NO_EXTERNAL_NETWORK_REQUESTS` and `NO_SECRET_PATTERN_HITS`.
