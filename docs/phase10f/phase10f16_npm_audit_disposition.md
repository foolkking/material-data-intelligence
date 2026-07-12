# Phase 10F-16 npm Audit Disposition

Official-registry audit reports seven nodes: Vitest critical; Vite high;
`@vitest/mocker`, `vite-node`, esbuild, Next, and PostCSS moderate.

| Package | Path | Reachability | Action |
|---|---|---|---|
| vitest | direct dev dependency | UI server is not enabled in production/CI | DEFERRED_WITH_OWNER (frontend tooling) |
| vite | via Vitest | development test server only | NOT_REACHABLE |
| esbuild | via Vite/Vitest | development transform server only | NOT_REACHABLE |
| @vitest/mocker | via Vitest/Vite | tests only | NOT_REACHABLE |
| vite-node | via Vitest/Vite | tests only | NOT_REACHABLE |
| next | direct runtime/build | advisory is through PostCSS; no untrusted CSS stringify path | DEFERRED_WITH_OWNER (frontend platform) |
| postcss | via Next | build-time application-owned CSS only | NOT_REACHABLE |

Audit's Vitest fix is a major upgrade to 4.1.10; its Next suggestion is an unsafe
downgrade to 9.3.3. Neither was applied in this phase. Review on the next planned
Next/Vitest compatibility upgrade or if any affected server becomes externally
reachable. No new renderer-reachable finding was introduced.
