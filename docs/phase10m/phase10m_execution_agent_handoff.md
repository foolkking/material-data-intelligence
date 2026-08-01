# Phase 10M Execution Agent Handoff

Phase 10M-0 is a documentation seal, not implementation. A future agent starts only with a reviewer prompt naming one phase from the sealed backlog.

Before editing source, the agent must verify the exact completion baseline in `results.md`, clean `master == origin/master`, the prior verified archive, one authorized task, migration head, and no unknown work. It must then read the execution manifest and lock.

The agent implements only the named phase and its acceptance IDs. It preserves Job/Plan/Artifact/lineage/interpretation authority and does not reinterpret this audit as deployed behavior. Any source fact that contradicts a sealed decision is reviewer input, not authorization to redesign.

Phase 10M-1 is not active. No executable task or prompt is created by Phase 10M-0.
