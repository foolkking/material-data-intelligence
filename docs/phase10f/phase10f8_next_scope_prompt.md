# Phase 10F-8：Viewer Scene Artifact Contract Planning

## 目标

进入 Phase 10F-8：Viewer Scene Artifact Contract Planning。

本阶段只规划并可选择性 scaffold inert `viewer_scene.json` artifact contract。不要实现 full `structure.viewer_3d`，不要引入 WebGL / Three.js，不要实现 renderer，不要实现 phonon。

## 1. 前置确认

先运行：

```bash
cd "E:\1project\Material Data Intelligence"
git status --short
git log --oneline -80
git branch --show-current
git tag --points-at HEAD
```

必须确认：

1. 当前仓库是 `Material Data Intelligence`。
2. 当前分支是 `master`。
3. 当前 HEAD 在 Phase 10F-7 commit 之后或等于该 commit。
4. git status clean。
5. Phase 10F-7 readiness docs exist.
6. renderer implementation readiness remains `NOT_READY`.
7. full `structure.viewer_3d` implementation readiness remains `NOT_READY`.

如果 git status 不干净，不要继续。先输出当前变更并停止。

## 2. 读取文档

阅读：

- `docs/phase10f/phase10f7_advanced_viewer_readiness.md`
- `docs/phase10f/phase10f7_viewer_artifact_contract_proposal.md`
- `docs/phase10f/phase10f7_renderer_architecture_assessment.md`
- `docs/phase10f/phase10f7_viewer_security_boundary.md`
- `docs/phase10f/phase10f7_viewer_input_caps.md`
- `docs/phase10f/phase10f7_viewer_routing_policy.md`
- `docs/phase10f/phase10f7_viewer_browser_evidence_model.md`
- `docs/phase10f/phase10f7_viewer_readiness_matrix.md`
- Phase 10D static viewer scene metadata docs and evidence.

## 3. Scope

Allowed:

- finalize inert `viewer_scene.json` contract
- define `viewer_summary.md` and `viewer_recipe.json`
- define params schema
- define typed warnings/errors
- define security checks
- define static JSON preview evidence plan
- update docs and persistent files

Not allowed:

- full `structure.viewer_3d` implementation
- WebGL renderer
- Three.js integration
- renderer bundle
- browser 3D runtime
- phonon bands/DOS
- Brillouin-zone 3D
- notebook/script execution
- external API workflow
- real LLM
- artifact JavaScript

## 4. Artifact Contract Finalization

Finalize:

- schema version
- tool id policy
- source metadata
- structure summary
- scene coordinate system
- site fields
- optional bond fields
- unit-cell fields
- style fields
- limits
- warnings
- security fields

The contract must keep `viewer_scene.json` as inert data and must be previewable as static JSON without a renderer.

## 5. No-Renderer Policy

Phase 10F-8 must not add renderer code. If any scaffold is added, it must only generate or validate inert artifacts. `security.renderer_required` should remain false for the JSON-only phase.

## 6. Security Checks

Plan tests or checks for:

- no artifact JS
- no external URLs
- no remote textures or fonts
- no CDN
- no executable callbacks
- no arbitrary file reads
- bounded sites and bonds
- bounded JSON size
- invalid geometry rejection

## 7. Planner Routing Planning

Plan future routing only. Do not implement routing unless a later implementation phase explicitly approves it.

## 8. Test Strategy

Plan focused tests for:

- schema validation
- deterministic ordering
- caps and warnings
- security fields
- no renderer dependency
- no WebGL/Three.js import
- negative routing preservation

## 9. Docs / Persistent Updates

Update:

- Phase 10F-8 docs
- `persistent/DESIGN_PROGRESS.md`
- `persistent/TASK_BOARD.md`
- `persistent/CHANGELOG.md`
- `persistent/OPEN_QUESTIONS.md`
- `persistent/TOOL_REGISTRY_NOTES.md`
- `persistent/ARCHITECTURE_DECISIONS.md`

## 10. Checks / CI

Run:

```bash
git status --short
git diff --stat
git diff --check
uv lock --check
```

If project smoke checks are required, run:

```bash
npm --prefix apps/web run typecheck
uv run python -m pytest -q
```

Do not run a real LLM.

## 11. PASS / PARTIAL_PASS / FAIL

PASS requires:

1. viewer artifact contract finalization completed.
2. no renderer implementation.
3. no WebGL / Three.js.
4. no phonon.
5. security boundary documented.
6. tests/checks pass.
7. persistent files updated.

PARTIAL_PASS is allowed if contract finalization needs reviewer confirmation but no implementation boundary is crossed.

FAIL if full viewer, renderer, WebGL, Three.js, phonon, notebooks/scripts, external API, real LLM, dependency installation, runtime semantic changes, or artifact JS are introduced.

## 12. 下一阶段建议

If Phase 10F-8 passes, decide whether to proceed to inert `viewer_scene.json` implementation/scaffold or continue readiness gap closure. Do not directly enter full `structure.viewer_3d` implementation / WebGL implementation / Three.js integration / phonon implementation.
