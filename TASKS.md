# Task Queue

---TASK---
状态：已完成

## Phase 13-6 - Final Archive + Presentation Package

Status: `ACTIVE / REVIEWER_AUTHORIZED`.

- Freeze the accepted Phase 13-5 release candidate at entry SHA
  `bde200acbe4e0d761d6c7a8338fbe68870fa82d6`.
- Build deterministic, sanitized release documentation, presentation,
  machine-readable manifests, evidence index, and canonical ZIP package.
- Preserve the current Fact, Scope, Phase 12, reproducibility, Registry,
  schema, migration, panel-cap, limitation, and input-support authorities.
- Production, scientific, Planner, Runtime, Workspace, Report, Recipe, input
  support, dependency, migration, and Phase 14 work are out of scope.
- `INITIAL_RELEASE_COMPLETE = NO` until the Phase13-6 implementation SHA passes
  exact-SHA CI and the append-only completion lifecycle is recorded.

```text
ACTIVE_EXECUTABLE_TASKS = 1
TASK_BLOCK_COUNT = 1
PHASE14_CREATED = NO
```

完成时间：2026-08-14

修改文件：`docs/phase13/final/**`、`docs/phase13/evidence/phase13_6_final_archive_presentation/**`、Phase 13-6 packaging/verification scripts、CI、documentation navigation、governance records and queue-lifecycle tests.

修改摘要：封板 Initial Release release candidate，生成 deterministic sanitized ZIP、InitialReleaseManifest、claim matrix、known-limitations linkage、forensic timeline、evidence index 和 presentation package；production/scientific/input-support behavior 保持不变。

测试结果：implementation/evidence SHA `48b270c6d2c6191b5707f6ee1c4d81a6ab9c8987` 的 exact-SHA CI `31768285019` PASS；Unit、Frontend/browser、PostgreSQL/Redis/MinIO、Linux 和 Windows jobs 全部 PASS。失败 candidates `ad0c98f4e469bb9215cd651ad6ed791527faf01c` / CI `31767331402` 与 `f7388b8ef402826d9a0f978c6c43f800449da5f3` / CI `31767878567` 均保留为 CI evidence portability history。
---END---
