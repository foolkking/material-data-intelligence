# Phase 10F-14 Renderer State Machine

| State | User result | Renderer initialized | Cleanup |
|---|---|---|---|
| idle / validating | pending | no | none |
| ready | valid scene awaiting effect | no | none |
| initializing_renderer | loading message and host | in progress | cancel stale instance |
| rendered | interactive canvas and controls | yes | required on tab/artifact/unmount |
| unsupported | readable fallback, JSON available | no | none |
| validation_failed | error codes, JSON available | no | none |
| renderer_failed | safe initialization fallback | failed | partial resources disposed |
| context_lost | safe context-loss fallback | no active canvas | dispose engine/context |
| disposed | no canvas | no | complete |

Stable selectors include renderer state, valid/invalid/unavailable/fallback, canvas and controls.
