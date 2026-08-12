# Phase 13-1 Capability and Report Fix-Forward #4

`P13-R4-001` selected Branch B. The historical Demo 1 wording requested composition distribution, which the frozen Intent contract correctly classifies as composition analysis, while the sealed demo required explicit composition-space output. The current canonical prompt now explicitly requests a materials-dataset quality summary and composition-space map. Production Intent, Eligibility and Planner behavior are unchanged.

`P13-R4-002` was caused by two broad Workspace gates: the projection omitted the Report panel until a Report already existed, and the frontend used the Workspace scientific `readOnly` flag as a global Report Finalize gate. Every Workspace now projects the non-scientific Report action surface, while M5 derives action eligibility from exact persisted Profile, Intent, Eligibility, selection, Plan, Job and source integrity facts. Current valid Plan 0.1 sources may compose an immutable Report/Recipe while scientific mutation remains forbidden; incomplete legacy, stale and cross-project sources remain unavailable.

Fact Model `e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06` is unchanged. Scope Baseline `f188b3e15aa94111787297ffde07b37f90cfdd1fe4e910e39f941e956b455455` supersedes `eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94` because the current Demo 1 canonical prompt changed.
