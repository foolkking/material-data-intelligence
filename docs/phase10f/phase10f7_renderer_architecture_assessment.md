# Phase 10F-7 Renderer Architecture Assessment

## 1. Scope

This assessment compares renderer options for future advanced structure viewer work. It does not implement a renderer or add a dependency.

## 2. Renderer Options

| Renderer Option | Requires New Dependency | JS Runtime Risk | External URL Risk | Security Isolation Needed | Browser Evidence Complexity | CI Risk | Recommendation |
|---|---:|---|---|---|---|---|---|
| no-renderer JSON-only phase | false | low | low | existing artifact-preview boundary | low | low | Recommended for Phase 10F-8 contract work |
| server-side static image generation | maybe | low in browser, medium on server | low if local only | resource and file-read caps | medium | medium | Future scope after contract finalization |
| browser canvas 2D projection | maybe | medium | low if bundled locally | renderer-data boundary | medium | medium | Future scope, not Phase 10F-7 |
| WebGL renderer | true | high | medium unless fully bundled | strict sandbox, dependency review, network audit | high | high | FUTURE_SCOPE, explicit approval required |
| Three.js renderer | true | high | medium unless fully bundled | strict sandbox, dependency review, network audit | high | high | FUTURE_SCOPE, explicit approval required |
| external viewer library | likely | high | medium to high | strict supply-chain and sandbox review | high | high | Not recommended until approved |
| iframe / sandbox isolation | maybe | reduces renderer blast radius | low if local-only | required if renderer is added | high | medium | Architecture control, not a renderer by itself |

## 3. Required Decision

- Do not implement a renderer in Phase 10F-7.
- Prefer the next phase to harden an inert `viewer_scene.json` artifact contract before any WebGL or Three.js renderer.
- Any future WebGL or Three.js path is `FUTURE_SCOPE` and requires explicit approval, sandboxing plan, dependency review, browser security tests, and console/network evidence.

## 4. Minimum Future Renderer Gate

A future renderer phase must first prove:

- artifact data cannot execute code
- renderer dependencies are approved and locally bundled
- no external requests occur during preview
- browser evidence includes real screenshots plus console/network audit
- oversized or malformed scenes are rejected or safely truncated
- planner routing does not mix viewer prompts with static physics, phonon, Brillouin-zone, or fitting prompts
