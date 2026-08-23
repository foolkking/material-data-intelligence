---TASK---
状态：处理中
任务名称：Agent-2.0 Phase 7 — Multi-turn Research Memory, Result Reuse & Continuation
开始时间：2026-08-23T15:00:00+08:00

已实现 durable ResearchSession state、auditable context items、explicit Session
constraints、authorized pin/unpin、bounded long-session candidate assembly、opaque
provider references、finding references、context budget、previous-result reuse 与
continuation integration。frontend `571` tests、typecheck/build、full backend
`1737 passed, 67 skipped` 与 authenticated 1280/390px browser no-overflow 已通过。当前仍需关闭
fresh PostgreSQL/Redis/MinIO RDF/second-family multi-turn qualification、live provider
qualification 与 final current-head CI。

本地 isolated fresh PostgreSQL/Redis/MinIO 已完成 base→0023。dedicated
Phase 7 service run 已定位并修复 Windows `localhost -> ::1` 导致的
inherited Phase 4 Worker PostgreSQL connect stall；readiness 后 execution
timing 已与 cold startup 分离，180 秒 execution bound 未增加。Phase 6
fresh interpretation failure 已确认为 Phase 7 fixture 缺少 grounded finding/
ResultItem 的 schema contract defect，已用真实 persisted Fact/ResultItem 修复，
未放宽 Phase 6 validator。Phase 6 service `2 passed`，Phase 7 service
`4 passed, 0 skipped`，live DeepSeek 三个 gated case 已通过；仍需提交/push、
把 dedicated selection 纳入 CI，并取得 final exact-SHA CI。

不得启动 Phase 8；完整闭环前保持“处理中”。
---END---

---TASK---
状态：失败
任务名称：Phase E-R1.6 — Canonical Live-Agent Browser Qualification Restart
开始时间：2026-08-17T00:00:00+08:00

# R1.6 Execution Override

This new task supersedes obsolete digest/exact-SHA qualification gates while
preserving the complete historical Phase E protocol below in this repository.
The sole authority is `Phase_BC_R1_6_Qualification_Authority_Reconciled`; its
machine-readable Case contracts and ordered `executionTurns[]` override older
prose. The campaign starts fresh at `Q-DATASET-001`, uses real Browser, real
DeepSeek, real Planner, Queue, fresh Worker, registered Adapters, persisted
Artifacts, Workspace/Renderer, grounded Interpretation, applicable Reports,
and inert non-executed Recipes. No historical Project, Job, Artifact, Plan,
provider response, or PASS is reused.

Qualification is content-first: no package digest, Case digest, checksum
manifest, Git identifier, or hash comparison is a PASS/FAIL gate. Product
state must be committed and have zero production-runtime uncommitted changes.
Ordinary product defects may be repaired autonomously, but qualification-
relevant contract drift, authority conflict, scientific expansion, fixture
defect, provider outage, or secret/MFA blocker stops the campaign. Any
runtime-sensitive repair requires a complete new Phase D re-seal and fresh
campaign state. The historical failed Phase E task remains unchanged.

Before Case 1, re-read and validate the actual R1.6 package and Phase D seal,
derive all campaign denominators, create fresh campaign evidence, and record
the complete user-to-runtime trace. Expected-rejection Cases must stop before
Plan creation. Multi-turn Cases submit each declared turn independently.
Recipes remain non-executable; supplemental tools and paraphrase expansion are
out of scope. The complete repository test suite must be reported truthfully;
historical governance/evidence failures are not an overall CI PASS.

The complete inherited historical Phase E normative protocol is preserved in
the existing historical task body in this file and is applicable except where
this R1.6 override retires digest/exact-SHA gates or conflicts with the R1.6
machine-readable authority. Execute this task through processing to completed
or a truthful hard-blocked result, append the result to `results.md`, and
preserve all per-Case/per-turn evidence.

失败时间：2026-08-17T02:20:46+08:00

失败原因：`PHASE_E / BLOCKED_AUTHORITY_CONFLICT`。真实浏览器入口完成了
Q-TRAJECTORY-001 的 EXTXYZ 上传与 DataProfile 建立；第一 turn 通过真实
Provider、Planner、Queue、Worker、Artifact、Workspace/Renderer、Report
链路完成 `structure.trajectory_viewer`。第二 turn 也通过真实用户提交与
Provider 生成了 3-step 的 `trajectory.diffusion`、`trajectory.msd`、
`trajectory.rdf` 依赖计划，但 Worker 对两个分析 Tool 均返回
`TOOL_RESOURCE_LIMIT / TRAJECTORY_TOO_LARGE`。

冻结 R1.6 轨迹实际包含 650 frames、516 atoms；已发布
`trajectory_analytics` Adapter 的正式上限为 200 frames、5000 atoms。
Case 同时要求覆盖完整 supplied time range。提高上限、截断 frames、重采样、
或生成替代数据都会改变已发布科学契约或冻结 authority，不能在 Phase E
内自主实施。未调用注入路径，未修改 R1.6 package，未伪造
Artifact/ToolCall/Report/Recipe。

证据：
`_qualification/evidence/phase_e_r1_6/discovery_20260817_r1_6_01/cases/Q-TRAJECTORY-001/`
以及 `TRAJECTORY_RUNTIME_CAP_BLOCKER.json`。历史失败尝试均保留在
`_qualification/evidence/phase_e_r1_6/discovery_20260817_r1_6_01/attempts/`。

需要 Reviewer 的最小动作：批准新的真实、可溯源且在现有 200-frame
上限内的 Q-TRAJECTORY authority fixture，或单独批准 trajectory analytics
资源上限/科学契约变更并创建新的 qualification authority。未生成
16/16 PASS、未执行后续 Cases、未声明 Phase E 完成。
---END---

---TASK---
状态：失败
任务名称：Phase B/C-R1.5 — Comprehensive Qualification Authority + Executability Reconciliation
开始时间：2026-08-16T19:15:00+08:00

依据 Reviewer 授权执行 R1.5。保留 R1.2、R1.3 与 R1.4 的历史 authority、失败 task 和 evidence，不启动 Phase E。先建立 `R1_5_BLOCKER_TRIAGE.json`，将 Q-TABLE、三项 ML、XRD、Trajectory、Phonon 的七个 R1.4 blocker 分别且完整地分类为 qualification question/fixture defect、preflight false-negative/implementation defect、existing-product defect，或需要 Reviewer 的真实 product contract gap。

只在完成全部分类后，才能做最小的 qualification question、fixture、preflight 或已发布产品 implementation correction。禁止为通过 qualification 放宽 DataProfile/Intent/Eligibility/ToolPlannerMetadata 科学语义、目标猜测、Plan cap、Tool/Adapter/Artifact/Renderer/support disposition。R1.5 validator 必须区分 source binding、同 Plan producer 产生的 artifact dependency，及 runtime-only IDs；必须解决 current seven-demo entry-slice 的两个测试错误，而不是删除/skip 测试。

完整修复后必须对 16 Cases/26 turns 做无 LLM、无 Job 的预检；只有完全通过才可生成无 qualification checksum manifest 的 R1.5 authority，并独立完成 Phase D re-seal。若仍有必须由 Reviewer 决策的 gap，记录所有已发现 conflicts，标记失败，且不得生成 partial package、不得运行 Phase D/Phase E。

失败时间：2026-08-16T20:08:17+08:00

失败原因：`PHASE_BC_R1_5 / QUALIFICATION_AUTHORITY_CONFLICT`。R1.5 先完成七个 blocker 的完整分类，再以当前 parser/Profile/Intent/Eligibility/Planner 合同重跑 16 Cases、26 个 analysis turns 的无 LLM 预检。15/16 Cases 已通过；唯一未闭合的 `Q-TABLE-001` 被确认为 `TRUE_PRODUCT_CONTRACT_GAP_REQUIRING_REVIEWER`：已验证的 JARVIS 候选提供 `formation_energy`、`band_gap` 和 `density`，numeric summary/correlation 可以精确绑定，但当前已发布非 ML normal-user Intent 不会生成 `material_property` target semantics，导致 required `viz.histogram` 与 `viz.scatter` 无法得到精确参数绑定。不能通过问题重试、fixture 伪造、目标猜测或放宽产品语义解决。

已完成：Q-ML-REG、Q-ML-UNC、Q-ML-CLASS 已证明为 representation-only fixture/question reconciliation；Q-XRD 已证明为 planned-artifact dependency 的 preflight false negative；Q-TRAJECTORY 修复了官方 EXTXYZ parser 对自身 schema-bounded 数值坐标 payload 的 generic inert-node-budget 误拒；Q-PHONON 已验证为 `atom_ordering` metadata-only fixture correction；seven-demo entry-slice 的两个历史错误已修复为当前 accepted composition routing expectation。所有这些路径及源码证据保存在 `_qualification/evidence/phase_bc_r1_5/`。

修改文件：`packages/artifact-core/mdi_artifact_core/trajectory_contract.py`、`tests/test_phase10g1_trajectory_parser_adapter.py`、`scripts/generate_phase13_1_product_entry_fix_forward.py`、`scripts/phase_bc_r1_5_executability_preflight.py`、`_qualification/work/phase_bc_r1_5/`、`_qualification/evidence/phase_bc_r1_5/`、`persistent/*.md`、`results.md`、本任务记录。未修改 R1.2 package、科学来源、DataProfile、AnalysisIntent、Eligibility、ToolPlannerMetadata、Registry、Plan cap 或支持 disposition。

测试结果：trajectory contract/parser/entry-slice 为 `53 passed, 4 warnings`；Intent/Planner/entry-slice 为 `85 passed, 4 warnings`，此前 `83 passed, 2 errors` 的 preflight errors 已为 0。R1.5 脚本完成全部预检，无 execution error；20 个 JSON evidence parse、secret scan、private-path scan、零执行计数和内容优先 integrity policy 检查均 PASS。`REAL_LLM_CALLS=0`、formal qualification executions/Jobs/ToolCalls/Artifacts 均为 0。未生成 R1.5 package，未启动 Phase D 或 Phase E。
---END---

---TASK---
状态：失败
任务名称：Phase B/C-R1.4 — Q-TABLE Explicit Property-Target Authority Reconciliation + Full Executability Preflight
开始时间：2026-08-16T18:05:00+08:00

依据 Reviewer 授权，保留所有历史失败任务、R1.2 package 与 R1.3 evidence。只在 qualification authority、非生产 validator、governance/docs/evidence 中解决 Q-TABLE：使用当前已认可的真实 JARVIS 材料表与明确、自然语言 property targets，保持四个独立 turns 及 required Tools `table.numeric_summary`、`viz.histogram`、`viz.correlation`、`viz.scatter`。不得改变 DataProfile 语义、Intent 词汇、Eligibility 科学规则、ToolPlannerMetadata、Planner 猜测、科学 Tool、Plan cap 或支持边界。

本任务采用 `CONTENT_AND_CONTRACT_VALIDATION`：退役 qualification-only digest/checksum 生成、验证、门槛和新 manifest；历史 records 可保留为非规范性记录。保护内容使用直接 byte-for-byte equality，确定性 ZIP 以两个构建文件直接比较验证。不得移除产品上传安全与资源持久化所需的内容哈希。

必须用当前 parser/Profile/Intent/Eligibility/Planner contracts 对四个 revised Q-TABLE turns 及全部 16 Cases 执行非 LLM、非 Job 的完整 executability preflight。任何新的 primary frozen-authority conflict 必须记录全部已发现 conflicts 并停止，不能建立 R1.4 或 Phase D。全部 preflight PASS 后，生成无 checksum manifest 的 R1.4 package，执行完整 Phase D re-seal；无论结果均不得启动 Phase E。

失败时间：2026-08-16T19:10:11+08:00

失败原因：`PHASE_BC_R1_4 / QUALIFICATION_AUTHORITY_CONFLICT`。完整 16 Case、26 个 analysis turn 的无 LLM 预检完成，9 Case PASS、7 Case BLOCKED。`PHASE_BC_R14_AUTH_001` 是 Q-TABLE：真实 JARVIS 候选能产生 `formation_energy`、`band_gap` 与 `density` material-property Profile facts，修订后的 numeric-summary 与 correlation 可绑定，但 histogram 和 scatter 仍因当前 deterministic Intent 不产生 exact target semantics 而无 required scalar parameter binding。另发现 `PHASE_BC_R14_AUTH_002`（三个 ML Case 的 deterministic target-semantic readiness）、`PHASE_BC_R14_AUTH_003`（Q-XRD direct Eligibility 未表达理论 XRD Artifact dependency）、`PHASE_BC_R14_AUTH_004`（Q-TRAJECTORY current parser `TRAJECTORY_NESTING_LIMIT_EXCEEDED`）及 `PHASE_BC_R14_AUTH_005`（Q-PHONON typed imports `PHONON_SPECIES_ORDER_INVALID`）。这些均不能在本 task 的 production/authority boundary 内自行绕过。

已尝试：以不依赖 qualification digest 的新非生产预检器运行当前 parser、DataProfile、deterministic Intent、Eligibility、ToolPlannerMetadata、entry import 及 plan cap；并单独复现 R1.2 的原始 Q-TABLE fixture/questions 失败。新增 content-and-contract qualification integrity policy；未修改 R1.2 ZIP、科学 fixture、DataProfile、Intent、Eligibility、ToolPlannerMetadata、Registry、Plan cap 或任何 production source。

修改文件：`scripts/phase_bc_r1_4_executability_preflight.py`、`docs/qualification/QUALIFICATION_INTEGRITY_POLICY.md`、`docs/index.md`、`persistent/PROJECT_BRIEF.md`、`persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`、`persistent/ARCHITECTURE_DECISIONS.md`、`_qualification/work/phase_bc_r1_4/`、`_qualification/evidence/phase_bc_r1_4/attempt_01_authority_preflight/`、`results.md`、本任务记录。

测试结果：预检连续运行完成并输出完整 16 Case contract evidence；`py_compile` PASS；直接 Intent/Planner tests 为 `74 passed`。扩展命令为 `83 passed, 2 errors`，错误来自现有 seven-demo entry-slice ready assertion，未被标记为 R1.4 PASS。14 个 JSON evidence 均 parse；secret/private-path hits 为 0；qualification digest fields/checksum files 为 0；real LLM、formal qualification execution、Job 与 Artifact 计数均为 0。未创建 R1.4 package，未执行 Phase D 或 Phase E。
---END---

---TASK---
状态：失败
任务名称：Phase B/C-R1.3 — Q-TABLE-001 Authority-Compatible Fixture Replacement + Required-Tool Binding Preflight + Phase D Re-Seal
开始时间：2026-08-16T16:30:00+08:00

依据 Reviewer 授权执行 Phase B/C-R1.3。保留所有历史 Phase B/C、Phase D 与 Phase E 失败记录及 R1.2 ZIP（SHA-256 `7a77b1db55c93454b97914bae3ee9d30e0f08ccc38bfd986c5907f65e38d1d04`）不变。

仅允许以当前 DataProfile 已批准的 `material_property` 语义替换 Q-TABLE-001 的真实、可溯源材料数据表；保持其四个独立 turn 和 required Tools：`table.numeric_summary`、`viz.histogram`、`viz.correlation`、`viz.scatter`。不得放宽 DataProfile、ToolPlannerMetadata、Registry、AnalysisPlan、科学支持边界或将 `dataset.materials_explorer` 用作替代。必须先产出 DataProfile 语义与 Tool binding 要求清单，使用实际导入/Profile/Eligibility/binding 代码证明旧 R1.2 fixture 会失败、新 fixture 的四个 Tool 均可绑定。

允许优先复用具完整出处/许可的仓库真实资产；不足时可进行受控真实公开数据获取。不得使用合成/随机/单元测试数据、行号连接、假属性、单位猜测、科学数值变换，或通过重命名任意数值列伪造 approved material_property。除 Q-TABLE 外其余 15 Cases 的科学和来源字节必须不变。

必须增强非生产 qualification validator，以对全部 16 Cases 的每个 analysis execution turn 验证 required Tool、Profile、资源、参数/目标/单位/伴随资源 binding 与 Intent 兼容性。R1.2 旧 Q-TABLE 必须复现 `REQUIRED_TOOL_PARAMETER_UNBOUND`；R1.3 必须全量 PASS。全过程禁止真实 LLM、正式 qualification execution、新 Qualification Job 与 Artifact。

通过后建立独立、可重复构建的 `Phase_BC_R1_3_Qualification_Authority_Reconciled.zip`，记录 supersedes R1.2、完整来源/字节/validator/evidence 信息，并运行完整 Phase D re-seal 绑定当前已提交产品 SHA 与新 package SHA。Phase D 期间仍禁止 LLM 和正式 qualification。即使 Phase D PASS，也不得启动 Phase E。

成功标准：16 Cases execution-ready、所有 required Tool bindings 完整、R1.3 hash/root/case manifests/deterministic build PASS、Phase D complete PASS、无 production runtime 未提交 diff、无 package/fixture 未授权变更。失败时记录精确 blocker，不启动 Phase E。

失败时间：2026-08-16T17:52:17+08:00

失败原因：`PHASE_BC_R13_AUTH_001 / BLOCKED_AUTHORITY_CONFLICT`。真实且可溯源的 JARVIS-DFT-3D 候选（Figshare `10.6084/m9.figshare.6815699.v11`，CC BY 4.0）能让当前 DataProfile 识别 `formation_energy`、`band_gap`、`density` 三个 `material_property`；但冻结的四个 Q-TABLE turn 仍不能通过当前生产 Intent/Target binding。前三个问题文本为 `INTENT_NOT_RECOGNIZED`，scatter 仅有空 `targetSemantics`，而当前两个标量参数不能从一个未声明的 material-property target domain 得到不退化且无歧义的 x/y 对。修复需要改写 frozen execution-turn/selection contract，或另行授权正常用户 property-target 选择行为；本任务明确禁止这些变更。

已尝试：使用实际 parser/Profile/Intent/Eligibility/Planner metadata 对旧 R1.2 fixture 与 64 行 JARVIS 候选进行确定性 preflight；复现旧 fixture 无 material_property，复现候选在 Intent/target binding 停止。未修改 DataProfile、ToolPlannerMetadata、Registry、Planner、科学支持或 R1.2 ZIP。因完整 required-tool binding 不可能成立，未创建 R1.3 package，未启动 Phase D 或 Phase E。

修改文件：`scripts/phase_bc_r1_3_qtable_preflight.py`、`scripts/verify_phase_bc_r1_3_evidence.py`、`_qualification/work/phase_bc_r1_3/`、`_qualification/evidence/phase_bc_r1_3/attempt_01_blocked_authority_conflict/`、`persistent/*.md`、`results.md`、本任务记录。

测试结果：preflight 连续两次输出哈希相同；`PYTHONPATH=<repo> uv run python -m pytest tests/test_phase10l1_analysis_intent.py tests/test_phase10l2_capability_planner.py -q` 为 `74 passed`；证据 JSON、SHA256SUMS、secret/private-path 与零执行计数校验均 PASS。首次未设置 `PYTHONPATH` 的 pytest 调用在 collection 阶段失败，已用项目正确导入路径重跑通过。
---END---

---TASK---
状态：失败
任务名称：Phase E-R1.2 — Canonical Live-Agent Browser Qualification Restart
开始时间：2026-08-16T16:00:00+08:00
准入时间：2026-08-16T16:00:00+08:00

# Phase E-R1.2 Supersession Override

This override has higher authority than the inherited historical Phase E body
below. The machine-readable R1.2 package has higher authority than either prose
when it is more specific.

## Entry authority

- Product candidate: `51e45c9436bef73f0c8ea1ccc5eb681dba1d21b8`.
- Migration head: `0008_phase_d_r1_namespace`.
- Sole execution package:
  `_qualification/inputs/Phase_BC_R1_2_Qualification_Authority_Reconciled.zip`.
- Required package SHA-256:
  `7a77b1db55c93454b97914bae3ee9d30e0f08ccc38bfd986c5907f65e38d1d04`.
- Expected package shape: 19,222,447 bytes, 138 sorted entries, 16 Cases,
  deterministic build, zero root/case hash mismatches, and static validator
  PASS. Recompute all facts before the first formal Case.
- Phase D authority is `PASS / LIVE_QUALIFICATION_ENVIRONMENT_RESEALED` with
  `READY_FOR_PHASE_E = YES`. Revalidate if runtime-sensitive production code
  changes.
- Historical package hashes `3fa4038b...`, `6a1e3f...`, and `bf1198f...` are
  immutable provenance only and must never be used for this execution.

## Historical task boundary

The inherited task below is copied from the historical failed Phase E task only
to retain its still-valid normative protocol. That old task, its status,
Q-DATASET discovery PASS, Q-COMPOSITION authority conflict, Projects, Jobs,
Artifacts, LLM responses, candidate history, and evidence remain historical.
This restart begins at `Q-DATASET-001` with new state and never rewrites or
reuses historical execution evidence.

## R1.2 execution authority

- Resolve conflicts in this order: R1.2 package manifests and Case contracts,
  this override, then inherited historical prose.
- Derive Case order and all denominators from `CASE_INDEX.json`,
  `PRIMARY_QUALIFICATION_EXECUTION_AUTHORITY.json`, and each `CASE.json`.
- Record total Cases, analysis Cases, expected rejection Cases, execution
  turns, required Tool assertions and unique IDs, report/recipe/renderer/
  limitation assertions in `PRIMARY_EXECUTION_AUTHORITY_SNAPSHOT.json` and
  `EXECUTION_TURN_MATRIX.json` before execution.
- A Case is not one Plan. For analysis Cases, submit
  `executionTurns[].question` in declared order. Each turn is one real normal-
  user submission and can create its own Intent, Eligibility, Plan, Job,
  ToolCalls, Artifacts, and Workspace. Never combine turns or exceed the
  current four-step Plan cap.
- For every turn, observed Tools must contain all
  `turn.requiredExecutionTools`. Across a Case, the union of observed required
  Tools must satisfy `case.requiredExecutionTools`.
- `requiredExecutionTools` are mandatory. `allowedExecutionTools` are
  permissible but nonmandatory. `forbiddenExecutionTools` must not run.
  `campaignCoverageContributions` are potential coverage only and never a PASS
  obligation.
- Apply exact per-Case `requiredArtifacts`, `requiredRenderers`,
  `requiredLimitations`, `requiredReportBehavior`, and
  `requiredRecipeBehavior`. The historical all-16 Report/Recipe denominator is
  superseded. Recipe execution remains forbidden.
- An `EXPECTED_REJECTION` or `analysisExecutionExpected=false` Case may PASS
  only through its declared typed pre-Plan rejection, with no Plan, Job,
  ToolCall, Artifact, Report, or Recipe where the Case contract requires
  absence. Do not implement unsupported product behavior to force execution.

## Normal-user and scientific boundaries

- Every analysis turn starts in the real Browser UI and uses the declared
  `UPLOAD_*` assets through the normal input path. Direct API/DB inspection is
  evidence-only after the Browser action and cannot initiate qualification.
- Use binary-safe upload, bounded multi-resource import, same-Dataset companion
  binding, and parser/resource semantic roles. Filename, array position,
  selection order, and upload order have no semantic authority.
- Q-ARCHIVE must preserve exact Browser/server/materialized SHA-256 and byte
  counts. ZIP remains a container and is never manually injected or extracted
  outside the safe parser authority.
- Q-XRD uses the R1.2 real Figshare `Apatite7_64` CuKa measurement paired with
  COD 4317043 hydroxyapatite at exactly 1.54184 angstrom. No relabeling,
  reprojection, synthesis, or wavelength guessing is permitted.
- Q-ELECTRONIC preserves Band/DOS material, calculation, energy-reference,
  units, and declared Fermi identities. Q-PHONON uses only declared typed
  companions; generic YAML/JSON and `phonon.animation` are not promoted.
- Preserve source authority for ML predictions/uncertainties/classes,
  trajectory identities/time/cell/species, electronic identities, and all
  scientific values and units.
- Required scientific integrity counters remain zero: fabrication, unit or
  wavelength/q-path guessing, missing-data fabrication, unauthorized support
  expansion, package or fixture mutation.

## Real execution

Each normal analysis turn must traverse:

```text
Browser -> Product UI -> persisted imported resources -> DataProfile
-> exact execution-turn question -> real sealed DeepSeek provider
-> AnalysisIntent -> Eligibility -> Planner -> validated AnalysisPlan
-> Browser Run -> Redis queue -> current fresh Worker -> registered Adapter
-> persisted ToolCall/Artifact -> Workspace -> actual Renderer/Viewer
-> grounded Interpretation -> applicable Report -> applicable inert Recipe
```

No mock, stub, old response replay, external provider call plus injection,
handcrafted Intent/Plan/Job/ToolCall/Artifact/Report, or hidden backend fixture
injection is permitted. Record provider/model/trace/retry/fallback safely; never
record the key. `REAL_LLM_CALLS > 0` is expected. A semantic failure is a
product defect, not a reason to retry-farm the provider.

## Campaign and remediation lifecycle

1. Create a fresh Phase E-R1.2 campaign and fresh per-Case state in canonical
   order, starting at Q-DATASET-001.
2. Run a full discovery/remediation campaign. Ordinary product defects must be
   diagnosed, minimally fixed, regression-tested, committed, runtime-restarted,
   and rerun from fresh affected state. Continue through all Cases unless a
   hard-stop condition applies.
3. Any repair that changes Registry scientific contracts, Plan schema/cap,
   support disposition, normal-user semantic input authority, Artifact or
   Renderer contract, scientific boundary, XRD authority, or execution
   readiness is `BLOCKED_AUTHORITY_CONFLICT` and stops the campaign.
4. Any repair that changes migration, durable persistence, runtime config,
   queue/Worker initialization, object-store bootstrap, provider policy/config,
   fresh namespace behavior, or input transport requires a complete Phase D
   re-seal before further formal Case execution.
5. Every authoritative candidate is an immutable Git commit with zero
   production-runtime uncommitted diffs. Preserve unrelated governance changes.
6. Discovery PASS records are historical only and may span SHAs; they cannot be
   assembled into final 16/16 qualification.
7. After discovery defects close, commit one final candidate, run actual
   governed exact-SHA unit/frontend/typecheck/build/service/migration/
   qualification/security gates, and run a complete Phase D re-seal against
   the exact final SHA and unchanged R1.2 package.
8. Create a new empty final campaign and rerun all Cases, all execution turns,
   and expected rejections from Case 1 on that single SHA. Any production
   runtime change invalidates the whole final campaign and requires a new
   candidate, CI, Phase D, namespace, and restart from Case 1.

## Final assertions and evidence

Final PASS requires 16/16 Cases, all derived analysis/rejection Cases and
execution turns, all user submissions, per-turn and Case-union required Tool
assertions, required Artifact/Renderer/UI-open/limitation assertions,
contract-applicable Report Preview/Finalize/Recipe assertions, and expected
pre-Plan rejection assertions at 100%; Recipe executions and unexpected
provider fallbacks are zero.

Report required, allowed, potential, and supplemental Tool coverage separately.
Do not qualify supplemental `phonon.animation` or
`structure.composition_from_structure`, and do not claim full paraphrase
robustness beyond the retained 7/16 authority.

The final injection counters are all zero: handcrafted Intent, Plan, Job,
ToolCall, Artifact, Report, and replayed LLM response. At closure independently
recompute the R1.2 ZIP, root, and all Case hashes and prove no package changes.

Evidence must include the inherited historical requirements plus:
`PHASE_E_FINAL_RESULT.md`, `CAMPAIGN_MANIFEST.json`,
`PRIMARY_EXECUTION_AUTHORITY_SNAPSHOT.json`, `EXECUTION_TURN_MATRIX.json`,
`EXPECTED_REJECTION_EVIDENCE.json`, `FINAL_CASE_INDEX.json`,
`FINAL_QUALIFICATION_MATRIX.json`, `CANDIDATE_HISTORY.json`,
`DEFECT_LEDGER.json`, `REMEDIATION_LINEAGE.json`, Tool/Artifact/Renderer/
Interpretation/Report-Recipe coverage, provider/browser/runtime/scientific/
input-transport/XRD summaries, final Phase D/environment/worktree/test/package
references, SHA256SUMS, and per-Case/per-turn trace evidence. Validate JSON,
evidence hashes, secrets, private paths, package immutability, completeness, and
production diff classification.

## Queue and stop rules

The new task moves `pending -> processing -> completed or failed`. It is not
archived before result and required exact-SHA lifecycle closure. The old failed
task remains byte-identical history.

Routine product defects do not stop autonomous work. Stop only for a genuine
frozen-authority/fixture conflict, qualification-relevant authority drift,
required scientific expansion, human-only credential/MFA, administrator or
external-service hard blocker, legal/license blocker, or unsafe repository
corruption.

Successful terminal state is:

```text
PHASE_E = PASS /
R1_2_CANONICAL_LIVE_AGENT_BROWSER_QUALIFICATION_COMPLETE

FINAL_REQUALIFICATION = PASS / SINGLE_EXACT_SHA_ALL_CASES
FINAL_CASES = 16/16 PASS
QUALIFICATION_PACKAGE_SHA256 =
7a77b1db55c93454b97914bae3ee9d30e0f08ccc38bfd986c5907f65e38d1d04
FINAL_PHASE_D = PASS
READY_FOR_REVIEWER = YES
```

On PASS or a genuine hard blocker, stop and return the complete Reviewer
package. Do not begin paraphrase, supplemental, negative expansion, or any
later product/qualification phase.

# Inherited Historical Phase E Normative Protocol (verbatim copy)

# Phase E — Autonomous 16-Case Live-Agent Browser Qualification & Exact-SHA Closure

## Real Browser + Real DeepSeek + Real Runtime + Autonomous Product Remediation + Final Exact-SHA Requalification

你现在获得授权执行完整：

# Phase E — Canonical Live-Agent Browser Qualification Campaign

并在发现真实产品缺陷时自主执行：

```text
triage
→ root-cause analysis
→ minimal production remediation
→ regression tests
→ candidate commit
→ environment revalidation
→ affected-case rerun
→ final all-case exact-SHA requalification
```

最终目标不是：

```text
“尽量多跑几个 Case”
```

而是获得一个可审计的最终结论：

```text
16 个 frozen canonical qualification cases

在同一个最终 committed exact repository SHA 上

通过真实 Browser
+
真实产品 UI
+
真实 DeepSeek provider path
+
真实 Planner
+
真实 Queue
+
fresh Worker
+
真实 registered Adapter
+
真实 persisted Artifact
+
真实 Workspace / Renderer / Viewer
+
真实 grounded Interpretation
+
真实 Report Preview / Finalize
+
non-executed Recipe

完成 16/16 Canonical Live Qualification。
```

---

# 0. Critical Entry Gate

本 Prompt 只有在前一个 Phase D Autonomous Closure 已经明确得到：

```text
PHASE_D =
PASS /
LIVE_QUALIFICATION_ENVIRONMENT_SEALED

READY_FOR_PHASE_E = YES

BLOCKERS = []
```

时才允许继续。

必须读取实际 Phase D final evidence。

不能只相信聊天摘要或 console 文本。

至少确认：

```text
FINAL_CANDIDATE_COMMITTED = YES

FINAL_REPOSITORY_HEAD_SHA = <exact SHA>

PRODUCTION_RUNTIME_AFFECTING_UNCOMMITTED_DIFFS = 0

FRESH_DATABASE_BOOTSTRAP = PASS

DATABASE_HEALTHY = YES

MIGRATION_AT_EXPECTED_HEAD = YES

QUEUE_BACKEND_HEALTHY = YES

OBJECT_STORAGE_HEALTHY = YES

BACKEND_HEALTHY = YES

FRONTEND_HEALTHY = YES

FRESH_WORKER_AVAILABLE = YES

PROJECT_DURABLY_PERSISTED = YES

PROJECT_SURVIVES_BACKEND_PROCESS_RESTART = YES

WORKSPACE_HISTORY_PROJECT_RESOLUTION = PASS

FRESH_QUALIFICATION_NAMESPACE_READY = YES

BROWSER_APP_SHELL_ACCESSIBLE = YES

PROVIDER_CONFIGURATION_RESOLVES = YES

REQUIRED_PROVIDER_CREDENTIAL_PRESENT = YES

REAL_LLM_CALLS = 0

FORMAL_QUALIFICATION_CASE_EXECUTIONS = 0
```

如果 Phase D 没有真正 PASS：

```text
DO NOT START PHASE E
```

返回：

```text
PHASE_E =
BLOCKED /
PHASE_D_ENTRY_GATE_NOT_SATISFIED
```

---

# 1. Frozen Qualification Authority

Phase E 唯一 primary qualification authority 仍然是：

```text
_qualification/inputs/
Phase_B_Closure_Phase_C_Contract_Normalized_PARAPHRASE_COVERAGE_FIXED.zip
```

Expected SHA256：

```text
3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952
```

开始 Phase E 前必须再次独立计算。

Require：

```text
QUALIFICATION_PACKAGE_EXTERNAL_SHA256_MATCH = YES

ROOT_HASH_MISMATCHES = 0

CASE_HASH_MISMATCHES = 0

QUALIFICATION_CASE_COUNT = 16

CANONICAL_PRIMARY_READY = 16/16
```

不得仅继承 Phase D 的 hash 结果。

---

# 2. Frozen Authority Mutation Ban

整个 Phase E campaign 永远禁止修改：

```text
Phase B/C qualification ZIP

CASE.json

CASE_INDEX.json

QUALIFICATION_CASE_MANIFEST.json

PHASE_A_AUTHORITY.json

UPLOAD_*

SOURCE_*

LICENSE.txt

PROVENANCE.json

SHA256SUMS.txt

canonical positive question

scientific values

units

wavelength

q-path

prediction

uncertainty

sample identity

material identity

calculation identity

semantic kind

expected capability

expected Tool

expected Artifact

expected Renderer

expected limitation

expected report behavior

expected Recipe behavior
```

Qualification failure：

```text
MUST NOT
→ mutate qualification authority
```

---

# 3. Existing Paraphrase Truth Remains Separate

Current authority remains:

```text
CANONICAL_PRIMARY_READY = 16/16

DISTINCT_PARAPHRASE_ROBUSTNESS_AUTHORITY = 7/16
```

本 Prompt 的 primary campaign：

```text
CANONICAL ONLY
```

不要把 NATURAL_PARAPHRASE 混进这 16 个 primary executions。

不要在本阶段宣称：

```text
FULL_PARAPHRASE_ROBUSTNESS = PASS
```

Phase E canonical PASS 与 paraphrase robustness 是两个不同 claim。

---

# 4. Primary Case Set

Primary canonical qualification set：

```text
Q-DATASET-001
Q-COMPOSITION-001
Q-TABLE-001

Q-ML-REG-001
Q-ML-UNC-001
Q-ML-CLASS-001

Q-STRUCTURE-001
Q-ATOMIC-VIEW-001
Q-COORD-001
Q-XRD-001
Q-STRUCTURE-RDF-001

Q-TRAJECTORY-001

Q-PHONON-001

Q-VOLUME-001

Q-ELECTRONIC-001

Q-ARCHIVE-001
```

但是：

```text
CASE.json
+
QUALIFICATION_CASE_MANIFEST.json
+
CASE_INDEX.json
```

是 machine-readable authority。

如果列表文字与 package contract 冲突：

STOP and classify the authority conflict.

不要自己决定哪个更方便。

---

# 5. Stable Execution Order

优先使用 package 中定义的 canonical case order。

如果 package 未规定执行顺序，使用：

```text
01 Q-DATASET-001
02 Q-COMPOSITION-001
03 Q-TABLE-001

04 Q-ML-REG-001
05 Q-ML-UNC-001
06 Q-ML-CLASS-001

07 Q-STRUCTURE-001
08 Q-ATOMIC-VIEW-001
09 Q-COORD-001
10 Q-XRD-001
11 Q-STRUCTURE-RDF-001

12 Q-TRAJECTORY-001

13 Q-PHONON-001

14 Q-VOLUME-001

15 Q-ELECTRONIC-001

16 Q-ARCHIVE-001
```

保持 stable ordering，使失败和最终 rerun 可比较。

---

# 6. Qualification Means Real User Flow

每个 Case 必须通过真实产品用户路径启动。

Required chain：

```text
Browser
↓
Product UI
↓
Fresh case namespace
↓
Upload / Typed Import through supported user path
↓
Product Parser / Importer
↓
Persisted Resource
↓
DataProfile
↓
CANONICAL_POSITIVE entered by Browser user action
↓
actual backend
↓
actual configured DeepSeek provider
↓
AnalysisIntent
↓
Eligibility
↓
Planner
↓
AnalysisPlan
↓
Browser user Run action
↓
Queue
↓
fresh Worker
↓
registered Adapter
↓
ToolCall
↓
persisted Artifact
↓
Workspace
↓
Renderer / Viewer
↓
grounded Interpretation
↓
Report Preview
↓
Report Finalize
↓
Recipe
```

Anything materially bypassing this chain is not a valid primary Case execution.

---

# 7. Real DeepSeek Is Required

Unlike Phase D:

```text
REAL_LLM_CALLS > 0
```

is now expected.

Every canonical Case requiring Agent reasoning must use the actual configured
production provider path.

Do not:

```text
mock DeepSeek

stub response

record/replay previous model response

call DeepSeek outside the product and inject the response

handcraft AnalysisIntent

handcraft AnalysisPlan

manually create Job

manually insert ToolCall

manually insert Artifact
```

Record for each Case, when available and safe:

```text
provider
model identity
request/trace identity
latency
retry count
fallback occurrence
```

Never record API keys.

---

# 8. Provider Fallback Policy

Qualification requires the intended configured provider/model policy.

If an unexpected fallback provider/model is used:

```text
CASE = FAIL
```

unless repository authority explicitly defines that fallback as part of the
qualified production policy.

Final closure should target:

```text
UNEXPECTED_PROVIDER_FALLBACKS = 0
```

---

# 9. No Retry Farming

A semantic/product failure must not be converted into PASS by repeatedly asking
the same question until the LLM happens to produce a favorable result.

For a given candidate SHA and fresh Case execution:

```text
one normal user submission
```

is the primary qualification attempt.

Built-in product retry policy may operate normally.

Manual rerun is allowed only when:

```text
a confirmed infrastructure/provider transport failure occurred
```

for example:

```text
connection reset
provider 5xx
rate limit handled outside expected product policy
browser automation transport failure
```

Such rerun must be clearly labeled:

```text
NON_SEMANTIC_TRANSIENT_RETRY
```

A wrong intent, wrong plan, wrong Tool selection or hallucinated result is:

```text
PRODUCT / AGENT FAILURE
```

not a transient retry opportunity.

Fix the product, create a new candidate, then rerun from a fresh namespace.

---

# 10. Case Isolation

Prefer:

```text
one fresh project/workspace qualification namespace per Case
```

unless the frozen Case contract explicitly requires a shared product context.

Each Case must have fresh:

```text
Project identity
Workspace identity
Resource identity
Conversation/session identity where applicable
Job identity
ToolCall identity
Artifact identity
Report identity
```

Do not reuse previous Case Artifacts as current evidence.

Do not let one Case accidentally discover another Case's resources.

---

# 11. Case Fixture Handling

For each Case:

read its actual:

```text
CASE.json
PROVENANCE.json
README.md
```

and declared assets.

Upload only:

```text
UPLOAD_*
```

through the product-supported user entry path.

`SOURCE_*` is provenance authority unless the contract explicitly says it is
also a user upload asset.

Do not upload SOURCE files merely because they contain richer data.

---

# 12. File Order Has No Scientific Authority

Never infer semantic role from:

```text
file order
filename order
ZIP order
upload order
```

Use:

```text
CASE asset role
semanticKind
resource identity
companion relationship
product DataProfile
```

as authority.

This is especially important for paired/multi-resource Cases.

---

# 13. Q-XRD-001 Special Contract

Treat XRD qualification as an actual paired scientific resource scenario.

Expected conceptual relationship:

```text
Crystal Structure
+
Experimental XRD
```

Require correct:

```text
material/phase relationship
wavelength identity
2θ/intensity semantics
resource role binding
```

Do not:

```text
guess wavelength
reproject wavelength
fabricate phase correspondence
bind by upload order
```

If current product cannot correctly establish required resource semantics:

CASE FAILS.

Fix product behavior only if frozen existing product authority says it should
support this scenario.

---

# 14. Q-PHONON-001 Special Contract

Normal-user qualification input is based on the frozen typed resources.

Conceptually:

```text
Structure
+
Phonon Band
+
Phonon DOS
```

Do not convert:

```text
generic phonon YAML/JSON
```

into newly executable support.

Do not add eigenvector import to make phonon animation qualify.

Current phonon animation gap remains outside the execution-ready normal-user
surface unless current frozen authority explicitly changes through a separately
reviewed product decision.

---

# 15. Q-ELECTRONIC-001 Special Contract

Electronic Band and Electronic DOS must preserve compatible scientific identity.

Require contract authority for:

```text
same/compatible material identity
same/compatible calculation context
energy units
energy reference
source-supplied Fermi identity where required
```

Do not combine unrelated resources merely because both parse.

---

# 16. Q-TRAJECTORY-001 Special Contract

Require actual trajectory semantics defined by the Case contract, including
where applicable:

```text
stable atom/species identity
coordinates
units
cell/PBC
monotonic physical time
sufficient frames
```

Do not silently promote a structure-animation file into a diffusion-capable
trajectory.

---

# 17. ML Case Integrity

For:

```text
Q-ML-REG-001
Q-ML-UNC-001
Q-ML-CLASS-001
```

do not manufacture model output inside qualification.

Preserve source-defined:

```text
target
prediction
uncertainty
class
probability
model identity
sample identity
```

where required by the Case.

Never derive an artificial uncertainty from residuals simply to satisfy the
product.

---

# 18. Q-ARCHIVE-001 Semantic Rule

Always preserve:

```text
ZIP = container format
```

not:

```text
ZIP = scientific semantic kind
```

Qualification should prove the product correctly dispatches contained supported
resources according to its existing archive/import contract.

Do not add new archive semantics to force success.

---

# 19. Per-Case Phase 1 — Import Qualification

For each Case first verify:

```text
UPLOAD_ACCEPTED

EXPECTED_ENTRY_PATH_USED

EXPECTED_NUMBER_OF_RESOURCES_CREATED

SEMANTIC_KINDS_CORRECT

RESOURCE_ROLES_CORRECT

RESOURCE_IDENTITIES_STABLE

REQUIRED_COMPANION_RELATIONSHIPS_CORRECT

DATAPROFILE_CREATED

DATAPROFILE_FACTS_CORRECT

NO_UNEXPECTED_IMPORT_WARNING

NO_UNEXPECTED_IMPORT_DATA_LOSS
```

Do not proceed blindly if import already violated the Case contract.

---

# 20. Per-Case Phase 2 — Agent Qualification

Enter the exact:

```text
CANONICAL_POSITIVE
```

question from Case authority via Browser UI.

Do not rewrite it.

Do not make it “clearer”.

Capture:

```text
user message identity
conversation/session identity
provider/model identity
resulting AnalysisIntent identity
```

Verify:

```text
NO_UNEXPECTED_CLARIFICATION

INTENT_MATCHES_CASE_REQUIREMENT

RESOURCE_REFERENCES_CORRECT

NO_CROSS_CASE_RESOURCE_REFERENCE
```

If clarification is not expected and the Agent asks unnecessary clarification:

CASE FAILS.

---

# 21. Eligibility Qualification

Verify actual product Eligibility path.

Require:

```text
expected eligibility disposition
required facts satisfied
required resources resolved
no unsupported capability promotion
no hidden missing requirement
```

Do not bypass Eligibility to reach execution.

---

# 22. Planner Qualification

Inspect the actual generated Plan.

Do not manually edit it unless normal product UX explicitly includes a user
approval action that does not change qualification semantics.

Verify against `CASE.json`:

```text
expected capabilities represented

expected Tools represented

required dependencies represented

correct resource bindings

correct ordering/dependency graph

no forbidden Tool substitutions

no unsupported capability

no synthetic resource

no scientific value invention
```

A plan that merely “looks plausible” is not sufficient.

---

# 23. Run Must Be User-Initiated Through Product UI

The actual analysis execution must begin via normal Browser product action.

Do not invoke the Job API directly as the qualification initiator.

Backend/API/DB tools may be used for:

```text
observation
evidence collection
cross-checking
```

after the normal user action.

They may not replace the user action.

---

# 24. Queue / Worker Qualification

For each Case record:

```text
Job ID
Queue identity
Worker identity
Worker repository SHA
ToolCall IDs
terminal Job state
timestamps
```

Require:

```text
JOB_DISPATCHED_THROUGH_CANONICAL_QUEUE = YES

WORKER_IS_CURRENT_CANDIDATE = YES

REGISTERED_ADAPTER_PATH = YES
```

No hand-created Job counts.

---

# 25. Expected Tools Are Contract Assertions

Case PASS requires its contract-relevant expected Tool behavior.

Do not reduce Tool assertions to:

```text
some Job succeeded
```

For each case derive:

```text
EXPECTED_TOOL_SET
OBSERVED_TOOL_SET
MISSING_TOOLS
UNEXPECTED_TOOLS
```

Unexpected auxiliary internal Tools may be allowed only if current product
authority explicitly allows them and they do not change scientific semantics.

Any required Tool missing:

```text
CASE FAIL
```

---

# 26. Artifact Qualification

For every expected Case-relevant Artifact record:

```text
Artifact ID
artifactType
artifactContractVersion
producer ToolCall
project identity
resource lineage
required fields
identity fields
storage object identity/hash when available
```

Require:

```text
EXPECTED_ARTIFACTS_PRODUCED = YES
```

Do not treat Job success as Artifact success.

---

# 27. Artifact Scientific Integrity

Artifact content must remain grounded in:

```text
uploaded source
product scientific computation
registered Adapter output
```

Do not allow:

```text
LLM-generated numeric arrays
LLM-generated units
LLM-generated scientific values
frontend-invented data
```

to substitute for Artifact authority.

If the Artifact has scientific validation invariants defined in current
repository authority, run those appropriate assertions.

---

# 28. UI / Renderer Qualification

Every Case-relevant expected Artifact must be opened through the actual UI.

Do not qualify Renderer coverage purely from registry mapping.

For each Artifact verify:

```text
Artifact reachable in Workspace

correct renderer selected

viewer loads

no fatal runtime error

required metadata visible

required units visible

required limitation visible

required numeric/table fallback visible where specified

selection behavior works where required

Inspector behavior works where required
```

Capture Browser evidence.

---

# 29. Renderer Must Not Recompute Scientific Results

Verify that Viewer/Renderer displays persisted scientific authority rather than
silently performing a competing frontend scientific calculation.

Frontend presentation transformations are allowed according to repository
contract.

New scientific derivation that changes authoritative values is not.

---

# 30. Grounded Interpretation Qualification

Inspect Interpretation/Findings generated by the real Agent.

Case-specific contract is authority.

At minimum check:

```text
observations grounded in produced Artifacts

numeric claims traceable

units traceable

resource/material identity correct

limitations preserved
```

Forbidden interpretation behavior includes:

```text
invented numeric value

invented unit

invented phase confirmation

invented stability conclusion

unsupported causal claim

unsupported scientific certainty

silently upgrading SUPPORTED_WITH_LIMITS to unrestricted support
```

A scientifically overclaiming interpretation is a Case failure even if Tools
and Artifacts were correct.

---

# 31. SUPPORTED_WITH_LIMITS Must Prove the Limit

For every Case whose support disposition is:

```text
SUPPORTED_WITH_LIMITS
```

success alone is insufficient.

Require:

```text
LIMITATION_PRESERVED = YES
```

at every applicable layer:

```text
eligibility
plan
artifact metadata
viewer
interpretation
report
```

according to repository/Case contract.

Qualification must prove the limitation is not lost.

---

# 32. Report Preview Qualification

For all 16 primary Cases:

```text
REPORT_PREVIEW_EXPECTED = YES
```

Open/generate Report Preview through normal product UI.

Verify:

```text
report references correct project/resources

report evidence references actual Artifacts

numeric/scientific claims are grounded

limitations preserved

no unrelated Case data

no hallucinated scientific results
```

Require:

```text
REPORT_PREVIEW_PASS = YES
```

---

# 33. Report Finalize Qualification

For all 16 Cases:

```text
REPORT_FINALIZE_EXPECTED = YES
```

Finalize through normal product UI.

Record:

```text
Report ID
final version identity
artifact/evidence references
```

Require:

```text
REPORT_FINALIZE_PASS = YES
```

Do not directly mutate report persistence to manufacture a finalized state.

---

# 34. Recipe Qualification

For all 16 Cases:

```text
RECIPE_EXPECTED = YES
```

Verify:

```text
Recipe exists
Recipe is structurally valid
Recipe reflects actual workflow
Recipe references appropriate resources/capabilities
```

But:

```text
RECIPE_EXECUTION = FORBIDDEN
```

for this primary Phase E campaign.

Require:

```text
RECIPE_PRESENT = YES
RECIPE_EXECUTED = NO
```

---

# 35. Browser Error Qualification

During every Case inspect:

```text
console errors
page exceptions
failed network requests
viewer runtime errors
```

Classify:

```text
blocking
qualification-relevant
known-benign
unrelated
```

Do not silently ignore Browser errors.

Final target:

```text
UNEXPECTED_QUALIFICATION_RELEVANT_BROWSER_ERRORS = 0
```

---

# 36. Backend / Worker Error Qualification

Capture relevant backend/Worker evidence around each Case.

Inspect for:

```text
tracebacks
unhandled exceptions
retry storms
serialization errors
database failures
object-store failures
queue failures
adapter failures
```

A Job returning success while the logs contain qualification-relevant hidden
errors must be investigated.

---

# 37. Per-Case Evidence Package

Create a dedicated evidence directory for each Case.

Suggested conceptual layout:

```text
phase_e/
  campaign_<id>/
    cases/
      Q-DATASET-001/
      ...
      Q-ARCHIVE-001/
```

Follow repository governance when a canonical location already exists.

Each case should contain at minimum:

```text
CASE_EXECUTION.json

IMPORT_EVIDENCE.json

AGENT_EVIDENCE.json

PLAN_EVIDENCE.json

RUNTIME_EVIDENCE.json

TOOLCALL_EVIDENCE.json

ARTIFACT_EVIDENCE.json

UI_RENDERER_EVIDENCE.json

INTERPRETATION_EVIDENCE.json

REPORT_EVIDENCE.json

RECIPE_EVIDENCE.json

BROWSER_EVIDENCE.json

CASE_RESULT.md

SHA256SUMS.txt
```

Use actual available evidence contracts where repository governance already
defines equivalents.

---

# 38. Per-Case Mechanical Decision

Each Case must finish as exactly one:

```text
PASS

FAIL_PRODUCT_DEFECT

FAIL_SCIENTIFIC_DEFECT

FAIL_AGENT_ROUTING

FAIL_ELIGIBILITY

FAIL_PLANNER

FAIL_RUNTIME

FAIL_ADAPTER

FAIL_ARTIFACT

FAIL_RENDERER_UI

FAIL_INTERPRETATION

FAIL_REPORT

FAIL_RECIPE

FAIL_PROVIDER

FAIL_INFRASTRUCTURE

BLOCKED_EXTERNAL

BLOCKED_AUTHORITY_CONFLICT
```

Do not use:

```text
PARTIAL_PASS
MOSTLY_PASS
GOOD_ENOUGH
```

as final primary qualification status.

---

# 39. Failure Classification

When a Case fails, classify root cause into one primary category:

```text
INPUT_IMPORT_DEFECT

PARSER_DEFECT

DATAPROFILE_DEFECT

AGENT_ROUTING_DEFECT

LLM_INTEGRATION_DEFECT

ELIGIBILITY_DEFECT

PLANNER_DEFECT

RUNTIME_DEFECT

QUEUE_DEFECT

WORKER_DEFECT

ADAPTER_DEFECT

SCIENTIFIC_IMPLEMENTATION_DEFECT

ARTIFACT_CONTRACT_DEFECT

PERSISTENCE_DEFECT

RENDERER_UI_DEFECT

INTERPRETATION_GROUNDING_DEFECT

REPORT_DEFECT

RECIPE_DEFECT

PROVIDER_TRANSIENT

INFRASTRUCTURE_TRANSIENT

QUALIFICATION_CONTRACT_DEFECT

FIXTURE_DEFECT

EXTERNAL_PERMISSION_BLOCKER

SCOPE_EXPANSION_REQUIRED
```

---

# 40. Autonomous Product Remediation Is Authorized

For actual product defects revealed by a valid frozen qualification Case, you
are authorized to:

```text
inspect
diagnose
modify production code
add regression tests
run tests
restart services
commit remediation
rerun qualification
```

without stopping to request routine approval.

The intent is:

```text
fix the product
```

not:

```text
fix the test
```

---

# 41. Authorized Product Fix Areas

When repository evidence supports the existing intended behavior, remediation
may include:

```text
parser/importer bug fixes

DataProfile bug fixes

resource identity fixes

Agent routing fixes

provider integration fixes

Eligibility fixes

Planner fixes

execution graph fixes

queue/Worker fixes

Adapter fixes

scientific implementation bug fixes within already-supported capability

Artifact persistence fixes

Artifact contract implementation fixes

Renderer/viewer fixes

Workspace fixes

Interpretation grounding fixes

Report fixes

Recipe generation fixes

migration/persistence fixes

runtime configuration fixes
```

Every change must preserve frozen support authority.

---

# 42. Scientific Fix Boundary

A bug in an already-supported scientific capability may be fixed.

But do not:

```text
add new scientific capability

change unsupported → supported

change mapping-only → executable

remove an existing documented limitation

fabricate missing scientific data

alter qualification source values
```

If success requires support expansion:

```text
SCOPE_EXPANSION_REQUIRED
```

and STOP.

---

# 43. Frozen Authority Conflict Rule

If strong evidence indicates:

```text
CASE.json itself is scientifically incorrect

fixture provenance is incorrect

UPLOAD asset was incorrectly normalized

expected Tool/Artifact contract contradicts frozen repository authority

qualification package contains an internal contradiction
```

do NOT silently repair it.

Classify:

```text
BLOCKED_AUTHORITY_CONFLICT
```

Produce precise evidence and stop the campaign for Reviewer action.

Changing frozen Phase B/C authority requires a separately versioned reopening
of Phase B/C.

---

# 44. Regression Test Requirement

Every production defect fixed during Phase E must receive an appropriate
regression test whenever practical.

A valid regression test should:

```text
fail before fix
pass after fix
```

and target the actual defect layer.

Examples:

```text
parser defect → parser/import integration test

planner defect → planner contract test

adapter defect → service-backed Adapter test

renderer defect → frontend/browser/component test

scientific bug → scientific invariant/reference regression

persistence defect → production repository integration test
```

Do not substitute a low-level test for a failed higher-level Case.

---

# 45. Focused Fix Verification

After each fix:

```text
run new regression
+
run directly affected existing tests
```

before returning to Live qualification.

Do not immediately spend another real LLM execution on obviously broken code
without first passing local deterministic tests.

---

# 46. Commit Every Runtime Candidate

Every set of production runtime changes used for a new Live rerun must be
represented by an immutable local Git commit before qualification evidence is
considered authoritative.

Require:

```text
CANDIDATE_COMMITTED = YES
PRODUCTION_RUNTIME_AFFECTING_UNCOMMITTED_DIFFS = 0
```

No push is required unless separately authorized.

Do not force-push.

Do not rewrite unrelated history.

---

# 47. Service Identity After Fix

After a production fix:

restart/reload every affected runtime component so that the next Case actually
uses the new candidate.

At minimum consider:

```text
Backend
Frontend
Worker
```

and migrations/bootstrap when affected.

Record:

```text
candidate SHA
backend candidate identity
frontend candidate identity
worker candidate identity
```

A Worker still running old code invalidates the rerun.

---

# 48. Phase D Re-Seal Trigger

If a Phase E remediation changes any of:

```text
migration

database/bootstrap

project/workspace persistence

runtime configuration

Compose/runtime authority

queue configuration

Worker initialization

object-store bootstrap

provider configuration/policy

Registry initialization

input support contract

fresh namespace behavior
```

then before further canonical Case execution:

```text
RE-RUN COMPLETE PHASE D
```

against the new candidate.

Require again:

```text
PHASE_D = PASS
READY_FOR_PHASE_E = YES
```

Do not assume the earlier environment seal survives such changes.

---

# 49. Lightweight Environment Revalidation

For fixes that do not alter Phase D-sensitive environment contracts, at least
reconfirm before Live rerun:

```text
DB healthy
Redis healthy
MinIO healthy
Backend healthy
Frontend healthy
fresh/current Worker
Browser reachable
provider configuration
production runtime diff = 0
```

Final campaign closure still requires a complete Phase D pass on the final SHA.

---

# 50. Failure Rerun Rule

After fixing a Case:

rerun that Case from a completely fresh Case namespace.

Do not reuse:

```text
old resource
old Plan
old Job
old Artifact
old Report
old LLM response
```

The rerun is a new user flow.

Historical failed evidence remains preserved.

---

# 51. Previously Passed Cases After Production Change

A previous PASS obtained on an older SHA remains:

```text
HISTORICAL_PASS
```

It does not become final evidence for the new SHA.

You may continue diagnostic progression through remaining Cases to discover
additional defects efficiently.

But you must not claim final closure from mixed SHAs.

---

# 52. Discovery Campaign vs Final Campaign

Treat Phase E as two logical layers.

## Layer 1 — Discovery / Remediation Campaign

Purpose:

```text
run all 16 cases
discover defects
repair product
learn the full failure surface
```

Historical Case PASS/FAIL evidence may occur across multiple candidate SHAs.

This is acceptable for diagnosis.

It is NOT final qualification.

## Layer 2 — Final Exact-SHA Requalification

After all discovered defects are fixed:

```text
freeze ONE final candidate SHA
```

then run all 16 from scratch.

Only Layer 2 can produce final:

```text
16/16 PASS
```

---

# 53. Discovery Campaign Should Continue After Ordinary Failure

Do not necessarily stop the entire discovery campaign after the first product
failure.

For an ordinary autonomous-remediable defect:

```text
diagnose
fix
test
commit
revalidate environment
rerun failed Case
```

then continue.

Where a defect is likely to affect multiple later Cases, fix it before
continuing.

Where safe and useful, continue to expose additional independent defects rather
than waiting for Reviewer approval.

---

# 54. Hard Stop Conditions

Stop only for:

```text
BLOCKED_AUTHORITY_CONFLICT

FIXTURE_DEFECT requiring frozen package change

SCOPE_EXPANSION_REQUIRED

missing human-only secret

MFA/login requiring human

administrator/system permission unavailable

external service/account outage that cannot be safely remediated

irrecoverable repository corruption

external license/legal acceptance requirement
```

For these return the minimum required human action.

Do not stop for normal production bugs.

---

# 55. Final Candidate Preparation

Once:

```text
all 16 canonical scenarios
have passed at least once after their known defects were addressed
```

prepare the final candidate.

Require:

```text
FINAL_CANDIDATE_COMMITTED = YES

FINAL_REPOSITORY_HEAD_SHA = <exact SHA>

PRODUCTION_RUNTIME_AFFECTING_UNCOMMITTED_DIFFS = 0
```

Run all relevant deterministic regression suites.

No production runtime change is allowed after final candidate freeze without
creating a new candidate SHA.

---

# 56. Final Phase D Re-Seal

Before final 16-case requalification:

run COMPLETE Phase D against:

```text
FINAL_REPOSITORY_HEAD_SHA
```

Require:

```text
PHASE_D =
PASS /
LIVE_QUALIFICATION_ENVIRONMENT_SEALED

READY_FOR_PHASE_E = YES
```

on that same SHA.

This final Phase D evidence supersedes earlier environment seals for final
qualification purposes.

---

# 57. Final Runtime Freshness

For final qualification use:

```text
fresh Backend candidate
fresh Frontend candidate
fresh Worker candidate
fresh qualification campaign namespace
```

Do not reuse the discovery campaign's project/workspace state as final evidence.

Durable infrastructure may reuse isolated Postgres/Redis/MinIO services if
their sealed identity is unchanged and data isolation is proven.

But final Case state must be fresh.

---

# 58. Final 16-Case Campaign

Run all 16 canonical cases again from the beginning using the stable Case order.

Every Case must execute against:

```text
SAME FINAL_REPOSITORY_HEAD_SHA
```

and the same sealed environment identity.

Require all per-Case assertions again.

Do not inherit PASS status from discovery executions.

---

# 59. Production Change During Final Campaign

If Case N fails and requires any production runtime code change:

```text
FINAL CAMPAIGN IS INVALIDATED
```

Fix defect.

Add regression.

Commit a new candidate SHA.

Run complete Phase D again.

Create fresh final campaign namespace.

Restart the entire 16-case final requalification.

Previously completed final Cases become historical evidence only.

This rule is mandatory.

---

# 60. No Cross-SHA PASS Stitching

Absolutely forbidden:

```text
Case 1 PASS @ SHA A
Case 2 PASS @ SHA B
Case 3 PASS @ SHA C
...
→ claim 16/16
```

Final authority requires:

```text
ALL 16 CASES
@
ONE EXACT SHA
```

---

# 61. Final Case PASS Gate

A Case is final PASS only if all contract-applicable assertions pass.

At minimum:

```text
INPUT_IMPORT = PASS

DATAPROFILE = PASS

LIVE_AGENT = PASS

EXPECTED_PROVIDER_PATH = PASS

ANALYSIS_INTENT = PASS

ELIGIBILITY = PASS

PLAN = PASS

EXPECTED_TOOL_BEHAVIOR = PASS

QUEUE_WORKER_RUNTIME = PASS

EXPECTED_ARTIFACTS = PASS

ARTIFACT_LINEAGE = PASS

UI_RENDERERS = PASS

VIEWER_ASSERTIONS = PASS

LIMITATION_ASSERTIONS = PASS where applicable

INTERPRETATION_GROUNDING = PASS

REPORT_PREVIEW = PASS

REPORT_FINALIZE = PASS

RECIPE_PRESENT = PASS

RECIPE_EXECUTED = NO

UNEXPECTED_BROWSER_FATAL_ERRORS = 0

UNEXPECTED_RUNTIME_FATAL_ERRORS = 0
```

---

# 62. Overall Canonical Phase E PASS Gate

Final Phase E PASS requires:

```text
FINAL_CANONICAL_CASES_EXECUTED = 16/16

FINAL_CANONICAL_CASES_PASS = 16/16

FINAL_LIVE_BROWSER_CASES = 16/16

FINAL_REAL_AGENT_CASES = 16/16

FINAL_REAL_DEEPSEEK_CASES = 16/16
```

where Agent/DeepSeek applicability is according to actual frozen product path.

Also require:

```text
EXPECTED_TOOL_ASSERTIONS = 100%

EXPECTED_ARTIFACT_ASSERTIONS = 100%

CASE_RELEVANT_ARTIFACTS_OPENED_IN_UI = 100%

EXPECTED_RENDERER_ASSERTIONS = 100%

REQUIRED_LIMITATION_ASSERTIONS = 100%

REPORT_PREVIEW = 16/16

REPORT_FINALIZE = 16/16

RECIPE_PRESENT = 16/16

RECIPE_EXECUTED = 0/16
```

---

# 63. Injection / Bypass Final Gate

Require:

```text
HANDCRAFTED_INTENT_INJECTION = 0

HANDCRAFTED_PLAN_INJECTION = 0

HANDCRAFTED_JOB_INJECTION = 0

HANDCRAFTED_TOOLCALL_INJECTION = 0

HANDCRAFTED_ARTIFACT_INJECTION = 0

HANDCRAFTED_REPORT_INJECTION = 0

REPLAYED_LLM_RESPONSE = 0
```

---

# 64. Provider Final Gate

Require:

```text
UNEXPECTED_PROVIDER_FALLBACKS = 0
```

and record actual provider/model identities for the final campaign.

Do not expose secrets.

---

# 65. Scientific Integrity Final Gate

Require:

```text
SCIENTIFIC_FIXTURE_CHANGES = 0

SCIENTIFIC_VALUE_FABRICATION = 0

UNIT_GUESSING = 0

WAVELENGTH_REPROJECTION = 0

Q_PATH_GUESSING = 0

MISSING_DATA_FABRICATION = 0

UNAUTHORIZED_SUPPORT_EXPANSION = 0
```

---

# 66. Qualification Authority Final Gate

At the end, recompute again:

```text
QUALIFICATION_PACKAGE_SHA256

root SHA256SUMS

all case SHA256SUMS
```

Require unchanged:

```text
QUALIFICATION_PACKAGE_SHA256 =
3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952

ROOT_HASH_MISMATCHES = 0

CASE_HASH_MISMATCHES = 0
```

This proves the test did not mutate its own authority.

---

# 67. Final Coverage Matrix

Generate:

```text
FINAL_QUALIFICATION_MATRIX.json
```

At minimum include dimensions:

```text
Case
×
Input
×
Semantic Kind
×
Capability Family
×
Tool
×
Artifact
×
Renderer
×
Interpretation
×
Report
×
Recipe
×
Support Disposition
×
Final Status
```

Derive actual coverage from observed final executions.

Do not merely copy Phase A planned coverage.

---

# 68. Repository vs Live-Execution Surface

Keep separate:

```text
repository capability surface
```

from:

```text
normal-user live execution-ready surface
```

Do not claim all repository capabilities live-qualified when the input path does
not permit normal-user execution.

Example principle:

```text
capability exists in Registry
!=
live-user qualification applicable
```

Preserve known execution-readiness limitations.

---

# 69. Phonon Animation Claim

Unless a separately approved product change has legitimately changed frozen
support authority:

do not claim phonon animation live-qualified merely because phonon Band/DOS
Case passes.

Report it separately as the actual current authority dictates.

Do not manufacture eigenvector input.

---

# 70. Paraphrase Claim

Final canonical Phase E closure does NOT automatically change:

```text
PARAPHRASE_ROBUSTNESS_CURRENT_AUTHORITY = 7/16
```

Final report must explicitly say:

```text
CANONICAL_PRIMARY_QUALIFICATION = 16/16 PASS
```

separately from:

```text
FULL_PARAPHRASE_ROBUSTNESS =
NOT ESTABLISHED BY THIS CAMPAIGN
```

unless a separately authorized paraphrase campaign was actually executed.

---

# 71. Negative / Clarification Claim

Likewise, do not claim:

```text
FULL_NEGATIVE_BOUNDARY_QUALIFICATION
```

or:

```text
FULL_CLARIFICATION_QUALIFICATION
```

unless those independent Cases were actually run.

This Prompt's final 16-case campaign is canonical positive qualification.

---

# 72. Final Evidence Root

Create one final campaign evidence root following repository governance.

At minimum preserve:

```text
discovery runs

failed case executions

remediation commits

regression evidence

candidate transitions

final Phase D seal

final 16-case executions

final qualification matrix
```

Never delete failed historical evidence just because a later rerun passes.

---

# 73. Campaign-Level Evidence

At minimum generate:

```text
PHASE_E_FINAL_RESULT.md

CAMPAIGN_MANIFEST.json

CANDIDATE_HISTORY.json

DEFECT_LEDGER.json

REMEDIATION_LINEAGE.json

FINAL_ENVIRONMENT_REFERENCE.json

FINAL_PHASE_D_REFERENCE.json

FINAL_CASE_INDEX.json

FINAL_QUALIFICATION_MATRIX.json

TOOL_COVERAGE.json

ARTIFACT_COVERAGE.json

RENDERER_COVERAGE.json

INTERPRETATION_COVERAGE.json

REPORT_RECIPE_COVERAGE.json

PROVIDER_EXECUTION_SUMMARY.json

BROWSER_ERROR_SUMMARY.json

RUNTIME_ERROR_SUMMARY.json

SCIENTIFIC_INTEGRITY_SUMMARY.json

WORKTREE_CLASSIFICATION.json

TEST_RESULTS.json

SHA256SUMS.txt
```

Use existing repository contracts if equivalent canonical artifacts already
exist.

---

# 74. Candidate History

`CANDIDATE_HISTORY.json` must record every candidate used during the campaign:

```text
candidate SHA

parent SHA

reason created

defects fixed

tests run

Phase D re-seal required?

Case executions performed

final/non-final
```

This makes mixed-SHA discovery history auditable without contaminating the
final result.

---

# 75. Defect Ledger

For every discovered defect record:

```text
defectId

firstObservedCase

firstObservedSHA

classification

symptom

rootCause

repository authority

production files changed

scientific behavior affected?

support surface affected?

regression tests

fix commit SHA

affected historical Case results

final disposition
```

Do not hide defects that were later repaired.

---

# 76. Screenshot / Browser Evidence

Capture sufficient Browser evidence to prove actual user-flow assertions.

Prefer meaningful checkpoints rather than indiscriminate screenshots.

For each Case capture at least where applicable:

```text
import/resource readiness

canonical question submitted

generated plan

terminal result/workspace

key viewer(s)

interpretation

Report Preview

finalized Report

Recipe
```

Store without leaking secrets/private credentials.

---

# 77. IDs and Lineage

For each final Case preserve identifiers sufficient to trace:

```text
Project
Workspace
Conversation/session
Resource(s)
AnalysisIntent
Eligibility result
AnalysisPlan
Job
ToolCall(s)
Artifact(s)
Report
Recipe
```

where the product exposes those identities.

The Reviewer must be able to follow:

```text
user action
→ runtime
→ scientific result
→ rendered evidence
```

---

# 78. Evidence Hashing

Generate SHA256 manifests for stable evidence.

Do not hash volatile files in a way that makes the evidence package
self-invalidating.

Document hash policy.

Final evidence self-check requires:

```text
MISSING_EVIDENCE_FILES = 0

EVIDENCE_HASH_MISMATCHES = 0
```

---

# 79. Secret / Privacy Scan

Before closure scan evidence for:

```text
API keys
passwords
tokens
database passwords
MinIO secret keys
authorization headers
private credentials
```

Require:

```text
SECRET_SCAN = PASS
```

Redact credentials while preserving non-secret execution identity.

---

# 80. Final Git Truth

At final closure record:

```text
FINAL_REPOSITORY_HEAD_SHA

HEAD_EQUALS_ORIGIN_MASTER

GLOBAL_WORKTREE_CLEAN

PRODUCTION_RUNTIME_AFFECTING_UNCOMMITTED_DIFFS
```

Do not force origin equality.

Final required runtime condition:

```text
PRODUCTION_RUNTIME_AFFECTING_UNCOMMITTED_DIFFS = 0
```

Evidence/governance files may remain locally dirty if accurately classified.

---

# 81. Final Regression Suite

Before final closure, run all repository-defined test suites materially affected
by campaign remediation.

Include appropriate:

```text
migration
persistence
import/parser
DataProfile
Agent/planner
runtime
Worker
Adapter
scientific
Artifact
Workspace
Renderer/UI
Report
Recipe
qualification governance
```

according to actual defects found.

Record exact commands and results.

---

# 82. Final Result — PASS

Only if all 16 final canonical cases pass at ONE exact SHA:

```text
PHASE_E =
PASS /
CANONICAL_LIVE_AGENT_BROWSER_QUALIFICATION_COMPLETE

FINAL_REQUALIFICATION =
PASS /
SINGLE_EXACT_SHA_16_OF_16

FINAL_CANONICAL_CASES =
16/16 PASS

READY_FOR_REVIEWER =
YES
```

Report at minimum:

```text
FINAL_REPOSITORY_HEAD_SHA = ...

FINAL_MIGRATION_HEAD = ...

QUALIFICATION_PACKAGE_SHA256 =
3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952

FINAL_PHASE_D = PASS

CANONICAL_CASES_EXECUTED = 16/16

CANONICAL_CASES_PASS = 16/16

LIVE_BROWSER_CASES = 16/16

LIVE_AGENT_CASES = 16/16

REAL_PROVIDER_CASES = 16/16
or exact applicable count with explanation

EXPECTED_TOOL_ASSERTIONS = 100%

EXPECTED_ARTIFACT_ASSERTIONS = 100%

CASE_RELEVANT_ARTIFACTS_OPENED_IN_UI = 100%

EXPECTED_RENDERER_ASSERTIONS = 100%

REQUIRED_LIMITATION_ASSERTIONS = 100%

REPORT_PREVIEW = 16/16

REPORT_FINALIZE = 16/16

RECIPE_PRESENT = 16/16

RECIPE_EXECUTED = 0

UNEXPECTED_PROVIDER_FALLBACKS = 0

HANDCRAFTED_INTENT_INJECTION = 0

HANDCRAFTED_PLAN_INJECTION = 0

HANDCRAFTED_JOB_INJECTION = 0

HANDCRAFTED_ARTIFACT_INJECTION = 0

REPLAYED_LLM_RESPONSE = 0

QUALIFICATION_PACKAGE_CHANGES = 0

SCIENTIFIC_FIXTURE_CHANGES = 0

PRODUCTION_RUNTIME_AFFECTING_UNCOMMITTED_DIFFS = 0

OPEN_CANONICAL_BLOCKING_DEFECTS = 0

PARAPHRASE_ROBUSTNESS_CURRENT_AUTHORITY = 7/16

FULL_PARAPHRASE_ROBUSTNESS_CLAIMED = NO

FULL_NEGATIVE_BOUNDARY_QUALIFICATION_CLAIMED = NO

READY_FOR_REVIEWER = YES
```

---

# 83. Final Result — BLOCKED

Do not end BLOCKED for ordinary product defects that are authorized for
autonomous remediation.

BLOCKED is allowed only for an actual hard stop such as:

```text
frozen qualification authority conflict

fixture defect requiring package revision

scientific support-surface expansion required

human-only credential/MFA

administrator/system action unavailable

external service/account hard failure

repository corruption unsafe to repair autonomously
```

Then output:

```text
PHASE_E =
BLOCKED /
HARD_QUALIFICATION_BLOCKER

FINAL_REQUALIFICATION = NOT_COMPLETE

READY_FOR_REVIEWER = YES
```

and specify:

```text
blockerId

classification

affected Case(s)

first observed SHA

root cause

why autonomous remediation cannot continue

frozen authority affected?

minimum human/reviewer action required

which evidence remains valid

what must be invalidated/rerun after resolution
```

---

# 84. Do Not Hide Partial Progress

If a hard blocker stops final completion, still return:

```text
cases attempted
cases passed historically
cases failed
defects repaired
candidate SHAs
final-candidate status
```

But do not turn historical mixed-SHA PASSes into a final percentage.

---

# 85. Final Reviewer Package

When complete, package all final campaign evidence into one Reviewer-friendly
artifact or directory.

It must contain enough information for an independent Reviewer to answer:

```text
1. Which exact code was qualified?

2. Which exact Phase B/C package was used?

3. Were all 16 canonical cases run through Browser?

4. Were real LLM/provider calls used?

5. Did the normal product chain create Plans/Jobs/Artifacts?

6. Did a fresh Worker execute the work?

7. Were all required Artifacts actually opened and rendered?

8. Were scientific limitations preserved?

9. Were interpretations grounded?

10. Did Report Preview and Finalize work?

11. Was Recipe produced but not executed?

12. What defects were discovered?

13. What was changed to fix them?

14. Were all final Cases rerun after the final production change?

15. Did all 16 final PASSes occur on one exact SHA?

16. Was the frozen qualification package unchanged?

17. What remains explicitly unqualified?
```

---

# 86. Critical Operational Principle

The objective is not:

```text
MAKE THE DASHBOARD GREEN
```

The objective is:

```text
DISCOVER THE TRUTH
→ FIX REAL PRODUCT DEFECTS
→ PRESERVE TEST AUTHORITY
→ REQUALIFY THE ACTUAL PRODUCT
→ PROVE 16/16 ON ONE EXACT SHA
```

A truthful FAIL is better than an artificial PASS.

A repaired product followed by complete requalification is the desired outcome.

---

# 87. Final Stop Boundary

Once either:

```text
PHASE_E =
PASS /
CANONICAL_LIVE_AGENT_BROWSER_QUALIFICATION_COMPLETE
```

or a genuine:

```text
HARD_QUALIFICATION_BLOCKER
```

has been reached:

STOP.

Do not autonomously start:

```text
paraphrase robustness expansion
negative boundary campaign
clarification campaign
new scientific capability implementation
phonon animation support expansion
future release work
```

Return the complete evidence package for independent Reviewer evaluation.

The Reviewer will decide whether to:

```text
ACCEPT Phase E

request remediation

authorize paraphrase qualification

authorize negative/boundary qualification

proceed to comprehensive final qualification archive
```

失败时间：2026-08-16T16:48:44+08:00

失败原因：`PHASE_E_R12_AUTH_001 / BLOCKED_AUTHORITY_CONFLICT`。R1.2
`Q-TABLE-001` 要求 `table.numeric_summary`、`viz.histogram`、
`viz.correlation` 和 `viz.scatter` 通过 `material_property_data` 绑定执行，
但 frozen CSV 的 normal-user DataProfile 只有 `tabular_data`，实际
`material_property` 列为 0，且当前 UI 没有列语义映射入口。真实 Browser / DeepSeek
turn 因此只允许并执行了 Case 禁止的 `dataset.materials_explorer`。继续修复将需要
改变 frozen Case，或改变 DataProfile / ToolPlannerMetadata qualification-relevant
contract，触发本任务明确 hard stop。

已尝试的方法：完整重算 R1.2 package 与 16 Case authority；执行 fresh
Q-DATASET-001；修复并提交 Q-COMPOSITION-001 的 composition-only Intent/Planner
路由，重新构建 current-SHA API/Worker 并 fresh PASS；随后按顺序执行
Q-TABLE-001，机械对比 Case required facts、实际 Profile semantic columns、
Eligibility rejection codes、Planner selection 与 normal-user UI entry surface。
未修改 frozen package 或 fixture，未通过重试 farming 绕过失败。

修改文件：`services/llm/mdi_llm/analysis_intent.py`、
`services/llm/mdi_llm/capability_planner.py`、
`tests/test_phase10l1_analysis_intent.py`、
`tests/test_phase10l2_capability_planner.py`、persistent governance 文件、
`apps/web/test/phase-e-r1-2-live-qualification.mjs`、
`_qualification/evidence/phase_e_r1_2/discovery_20260816_01/`。

修改摘要：提交 `610de07887d7c221e377bc1d8d01882df9d5a6d2` 修复 explicit
formula / element / chemical-system composition routing；保留 Q-DATASET 自动化失败、
Q-COMPOSITION product failure 与所有 fresh rerun evidence；生成 partial Reviewer
package、authority blocker、candidate/defect/remediation lineage 及完整 SHA256SUMS。

测试结果：Intent/Planner/Phase13 focused `88 passed`；current-SHA Docker API、
PostgreSQL、Redis、MinIO、Worker 与 provider configuration 健康；Q-DATASET 与
Q-COMPOSITION 为 `PASS_DISCOVERY`，Q-TABLE 为
`BLOCKED_AUTHORITY_CONFLICT`。Evidence JSON 170 个全部可解析，220 项
SHA256SUMS 自检通过，secret hits 0，private-path hits 0。Final exact-SHA CI、
final Phase D 与 final 16-Case campaign 因 hard stop 未执行，不能声明 PASS。

提交/CI 状态：product remediation 已本地提交为
`610de07887d7c221e377bc1d8d01882df9d5a6d2`；未 push；remote exact-SHA CI
未运行。R1.2 package SHA-256 仍为
`7a77b1db55c93454b97914bae3ee9d30e0f08ccc38bfd986c5907f65e38d1d04`。
---END---

# Task Queue

---TASK---
Task: Phase D-R2 - Normal-User Input Transport Contract Closure + R1.2 Refreeze
Status: failed

Authority: reviewer-authorized remediation starting from committed candidate
`2d7f92d266c51a3401a36f619082e5840e0d60f9` and immutable historical R1.1
package SHA-256
`bf1198f0281119af6b0485518ace053d99e827d0ed3d31d077ddf94ed8d4f87f`.

Scope: audit the released support authority for Archive, XRD, and Electronic
resources; repair only byte-safe and bounded normal-user input transport for
already-supported resources; add transport contracts and validation; commit
the production remediation; refreeze a separately versioned R1.2 package; then
run and close a complete Phase D re-seal against the committed remediation SHA
and R1.2 package.

Boundaries: no new scientific capability, Registry Tool, support disposition,
scientific algorithm, AnalysisPlan schema/cap, Adapter, Artifact/Renderer
scientific authority, Report semantics, Recipe execution, Phase E execution,
qualification Job, formal qualification submission, or real LLM call.

Failure time: 2026-08-16T10:53:23+08:00

Failure reason: the mandatory repository support-authority audit classified
`Q-ARCHIVE-001` and `Q-ELECTRONIC-001` as already-supported resources with
normal-user transport defects, but classified `Q-XRD-001` as
`AUTHORITY_AMBIGUOUS`. The frozen experimental XRD resource declares wavelength
`1.9373 angstrom`, while the current released `structure.xrd` Tool accepts only
CuKa and runtime authority fixes that wavelength at `1.54184 angstrom`. Current
preflight and comparison Adapter contracts must return
`XRD_WAVELENGTH_MISMATCH`; byte-safe multi-resource transport cannot make the
frozen Case execution-ready. The task explicitly requires a hard stop and
Reviewer authority decision for category C.

Attempted methods: mechanically inspected the frozen Case/assets, parser,
Profile, Registry, Planner metadata, Worker preflight, XRD and comparison
Adapters, renderer, release docs, and tests; independently verified both frozen
asset hashes and the two conflicting wavelengths; ran the current XRD contract
test suite. A preliminary transport draft made before the cross-layer audit
completed was fully reverted, leaving zero production runtime changes.

Modified files: `TASKS.md`, `results.md`, and new non-production blocker
evidence under
`_qualification/evidence/phase_d_r2/attempt_01_blocked_authority_conflict/`.
No production source, R1.1 package, scientific fixture, support disposition,
Registry contract, AnalysisPlan contract, or dependency was changed.

Test result: `uv run pytest tests/test_phase10n3_experimental_xrd.py -q`
passed (`10 passed`). R1.1 package SHA-256 remained
`bf1198f0281119af6b0485518ace053d99e827d0ed3d31d077ddf94ed8d4f87f`.
JSON parse, evidence SHA-256 self-check, frozen asset hash verification, and
zero-execution checks passed. Phase B/C-R1.2, Phase D re-seal, and Phase E were
not started.
---END---

---TASK---
Task: Phase D R1.1 - Live Qualification Environment Re-Seal
Status: failed

Authority: committed repository candidate at task entry plus
`_qualification/inputs/Phase_BC_R1_1_Qualification_Authority_Reconciled.zip`
SHA-256 `bf1198f0281119af6b0485518ace053d99e827d0ed3d31d077ddf94ed8d4f87f`.

Scope: independently verify the complete R1.1 package and execution contracts,
seal the repository-approved isolated PostgreSQL/Redis/MinIO/backend/frontend/
fresh-worker/browser/provider environment, prove fresh Alembic-bootstrapped
durable namespace persistence and restart survival, preserve zero qualification
execution/LLM counters, and generate permanent re-seal evidence.

Phase E-R1.1 dependency state: `BLOCKED_BY_PHASE_D_RESEAL`. Do not create or
process the Phase E-R1.1 task unless this Phase D task completes with every
mechanical gate PASS. Preserve all historical Phase D and Phase E failed tasks
and evidence unchanged.

Failure time: 2026-08-16T10:31:44+08:00

Failure reason: the R1.1 package, current repository fingerprint, durable
runtime, fresh database and namespace, worker, browser shell, and provider
configuration all passed their focused gates. A repository-grounded normal-user
entry-path audit then found three frozen authority conflicts. `Q-ARCHIVE-001`
declares an execution-ready UI ZIP upload, but the generic UI uses `File.text()`
and the backend writes UTF-8 text, changing the frozen ZIP bytes. `Q-XRD-001`
and `Q-ELECTRONIC-001` each require paired resources in one dataset while the
generic UI submits exactly one file. Adding binary or generic multi-resource
upload support would change the normal-user scientific input contract and is a
hard stop under this task's authority-drift policy.

Modified files: `TASKS.md`, `results.md`, and the new non-production evidence
root `_qualification/evidence/phase_d/attempt_07_r1_1_reseal_blocked_authority_conflict/`.
No production source, frozen package, scientific fixture, dependency, or
support contract was changed.

Test result: package external SHA, root hashes, and all 16 case hashes PASS;
R1.1 static and cross-field validators PASS; focused qualification/migration/
worker tests `17 passed`; JSON parse, evidence SHA-256 self-check, secret scan,
private-path scan, and zero-execution checks PASS. The normal-user input
authority audit is `FAIL_BLOCKING` with `PHASE_D_R11_AUTH_001` through
`PHASE_D_R11_AUTH_003`.

Result: `PHASE_D = BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_RESEALED` and
`READY_FOR_PHASE_E = NO`. Phase E-R1.1 was not created or started.
---END---

---TASK---
Task: Phase D Attempt 4 - Complete Live Qualification Environment Seal
Status: failed

Authorized scope: preserve Attempts 1-3, reverify the frozen repository and
qualification package identities, start the unchanged repository-approved
PostgreSQL/Redis/MinIO Compose services in an isolated project, and complete the
Phase D runtime, worker, browser-shell, provider-configuration, namespace, and
evidence gates.

Boundaries: no Phase E execution, qualification fixture upload, formal
qualification case, live LLM call, qualification Job or Artifact,
production/scientific/dependency/contract change, destructive data operation, or
mutation of the frozen qualification package.

Failure time: 2026-08-16T01:43:24+08:00

Failure reason: all frozen-package, Docker, PostgreSQL, migration, Redis,
MinIO, backend, frontend, fresh worker, provider-configuration, browser-shell,
worktree, and zero-execution gates passed. The official Alembic path reaches
`0007_phase10m1_workspace_domain` but does not create the `users` and
`organizations` tables required by `SqlAlchemyProjectRepository.save()`. The
fresh empty project created through `POST /projects` therefore cannot be
persisted through the canonical repository boundary, and Workspace history
returns typed `PROJECT_NOT_FOUND`.

Result: `PHASE_D = BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED`.
Only `PHASE_D-B007` remains unresolved; `PHASE_D-B001` through
`PHASE_D-B006` and `PHASE_D-B008` are resolved. No test-only
`metadata.create_all`, hand-written DDL, qualification execution, live LLM call,
or production/package mutation was used. Evidence:
`_qualification/evidence/phase_d/attempt_04/`.
---END---

---TASK---
Task: Phase D Attempt 3 - Docker Runtime Controlled Resume
Status: failed

Authorized scope: verify the newly available repository-approved Docker/Compose
runtime, preserve Attempts 1 and 2, and rerun the complete Phase D environment
seal without executing Phase E or any qualification case.

Boundaries: no production/scientific/dependency/contract changes, no destructive
service or volume operations, no reuse of unknown development state, no live
LLM call, and no qualification Job or Artifact.

Failure time: 2026-08-16T01:11:42+08:00

Failure reason: Docker CLI/Engine/Compose are healthy, but the unmodified
checked-in Compose publishes PostgreSQL and Redis on fixed host ports 5432 and
6379. Those ports are occupied by existing non-Docker PostgreSQL and Memurai
services. Reviewer-authorized service stop and direct process termination were
attempted, but Windows denied both operations without elevated service/process
permissions. No partial Compose startup was performed.

Result: `PHASE_D = BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED`.
Root blocker: `PHASE_D-B008`. `PHASE_D-B002` through `PHASE_D-B007` remain
unresolved derived gates. Evidence: `_qualification/evidence/phase_d/attempt_03/`.
---END---

---TASK---
Task: Phase D Attempt 2 - Live Qualification Environment Seal Controlled Resume
Status: failed

Authorized resolution: copy the verified repository-root qualification ZIP byte
for byte to `_qualification/inputs/`, preserve Attempt 1 blocked evidence, then
resume Phase D from package verification through the complete environment seal.

Boundaries: no formal qualification case, live LLM call, qualification Job or
Artifact, production/scientific/dependency/contract change, or Phase E execution.

PHASE_D-B001 resolution: source and destination SHA-256 both equal
`3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952`;
both are 19,073,044 bytes and byte-for-byte comparison passed. Source retained.

Failure time: 2026-08-16T00:25:15+08:00

Failure reason: the frozen package and browser/provider checks pass, but the
durable runtime cannot be sealed. PostgreSQL rejects the repository
qualification connection, Redis and MinIO are unavailable, the fresh worker
cannot connect to `mdi-jobs`, the backend durable runtime health is incomplete,
and a safe fresh qualification namespace therefore cannot be established.

Result: `PHASE_D = BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED`.
Blockers: `PHASE_D-B002` through `PHASE_D-B007`. No formal qualification case,
real LLM call, qualification Job, or qualification Artifact was executed.
Evidence: `_qualification/evidence/phase_d/attempt_02/`.
---END---

---TASK---
Task: Phase D - Live Qualification Environment Seal
Status: failed

Authorized scope: verify the frozen Phase B/C qualification package and seal
the non-case runtime environment without production changes, qualification case
execution, browser qualification, or live LLM calls.

Failure time: 2026-08-16T00:03:08+08:00

Failure reason: the authoritative package path
`_qualification/inputs/Phase_B_Closure_Phase_C_Contract_Normalized_PARAPHRASE_COVERAGE_FIXED.zip`
does not exist. A same-named ZIP exists at repository root and has the expected
SHA-256, but Phase D is not authorized to copy, move, repackage, or substitute it
for the required authority path.

Result: `PHASE_D = BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED`.
No services, worker, browser, provider invocation, or formal qualification case
were started. Evidence: `_qualification/evidence/phase_d/`.
---END---

---TASK---
 状态：失败

失败时间：2026-08-16T04:51:17+08:00

失败原因：`Q-COMPOSITION-001` 触发任务定义的
`BLOCKED_AUTHORITY_CONFLICT`。冻结 Case 只有 CSV 表格资产，却要求
`structure_resource` 和仅接受周期 `Structure` 的
`structure.composition_from_structure`；同时冻结期望为 7 个 Tool/7 steps，
而当前发布 `AnalysisPlan`/capability selection 合同上限为 4。Phase E 明确
要求缺少任何 expected Tool 即 Case FAIL，并禁止静默修订 frozen package。

修改文件：Phase E 产品修复已分别提交为 `90420e9`、`bd9ec3b`、
`991ef71`、`821ed3a`、`8768f54`、`2d7f92d`；停止证据位于
`_qualification/evidence/phase_e/campaign_20260816_blocked_authority_conflict/`。

修改摘要：修复了 discovery 中实际出现的 Intent、Planner 和
Interpretation 缺陷；`Q-DATASET-001` 在 `8768f54` 上完成 discovery PASS。
`Q-COMPOSITION-001` 在 `2d7f92d` 上通过真实 Browser、DeepSeek、Queue、
Worker 和 Adapter 到达 completed Job 后，机械对比发现 frozen authority
与 Registry/Input/Plan contract 冲突，按 hard-stop 规则终止。

测试结果：最后一组 focused tests 为 38 + 32 + 34 passed；Ruff PASS；
`git diff --check` PASS。未运行 full/final regression、exact-SHA CI 或 16-case
final requalification，因为 authority conflict 要求立即停止。冻结 ZIP SHA-256
仍为 `3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952`。

# Phase E — Autonomous 16-Case Live-Agent Browser Qualification & Exact-SHA Closure

## Real Browser + Real DeepSeek + Real Runtime + Autonomous Product Remediation + Final Exact-SHA Requalification

你现在获得授权执行完整：

# Phase E — Canonical Live-Agent Browser Qualification Campaign

并在发现真实产品缺陷时自主执行：

```text
triage
→ root-cause analysis
→ minimal production remediation
→ regression tests
→ candidate commit
→ environment revalidation
→ affected-case rerun
→ final all-case exact-SHA requalification
```

最终目标不是：

```text
“尽量多跑几个 Case”
```

而是获得一个可审计的最终结论：

```text
16 个 frozen canonical qualification cases

在同一个最终 committed exact repository SHA 上

通过真实 Browser
+
真实产品 UI
+
真实 DeepSeek provider path
+
真实 Planner
+
真实 Queue
+
fresh Worker
+
真实 registered Adapter
+
真实 persisted Artifact
+
真实 Workspace / Renderer / Viewer
+
真实 grounded Interpretation
+
真实 Report Preview / Finalize
+
non-executed Recipe

完成 16/16 Canonical Live Qualification。
```

---

# 0. Critical Entry Gate

本 Prompt 只有在前一个 Phase D Autonomous Closure 已经明确得到：

```text
PHASE_D =
PASS /
LIVE_QUALIFICATION_ENVIRONMENT_SEALED

READY_FOR_PHASE_E = YES

BLOCKERS = []
```

时才允许继续。

必须读取实际 Phase D final evidence。

不能只相信聊天摘要或 console 文本。

至少确认：

```text
FINAL_CANDIDATE_COMMITTED = YES

FINAL_REPOSITORY_HEAD_SHA = <exact SHA>

PRODUCTION_RUNTIME_AFFECTING_UNCOMMITTED_DIFFS = 0

FRESH_DATABASE_BOOTSTRAP = PASS

DATABASE_HEALTHY = YES

MIGRATION_AT_EXPECTED_HEAD = YES

QUEUE_BACKEND_HEALTHY = YES

OBJECT_STORAGE_HEALTHY = YES

BACKEND_HEALTHY = YES

FRONTEND_HEALTHY = YES

FRESH_WORKER_AVAILABLE = YES

PROJECT_DURABLY_PERSISTED = YES

PROJECT_SURVIVES_BACKEND_PROCESS_RESTART = YES

WORKSPACE_HISTORY_PROJECT_RESOLUTION = PASS

FRESH_QUALIFICATION_NAMESPACE_READY = YES

BROWSER_APP_SHELL_ACCESSIBLE = YES

PROVIDER_CONFIGURATION_RESOLVES = YES

REQUIRED_PROVIDER_CREDENTIAL_PRESENT = YES

REAL_LLM_CALLS = 0

FORMAL_QUALIFICATION_CASE_EXECUTIONS = 0
```

如果 Phase D 没有真正 PASS：

```text
DO NOT START PHASE E
```

返回：

```text
PHASE_E =
BLOCKED /
PHASE_D_ENTRY_GATE_NOT_SATISFIED
```

---

# 1. Frozen Qualification Authority

Phase E 唯一 primary qualification authority 仍然是：

```text
_qualification/inputs/
Phase_B_Closure_Phase_C_Contract_Normalized_PARAPHRASE_COVERAGE_FIXED.zip
```

Expected SHA256：

```text
3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952
```

开始 Phase E 前必须再次独立计算。

Require：

```text
QUALIFICATION_PACKAGE_EXTERNAL_SHA256_MATCH = YES

ROOT_HASH_MISMATCHES = 0

CASE_HASH_MISMATCHES = 0

QUALIFICATION_CASE_COUNT = 16

CANONICAL_PRIMARY_READY = 16/16
```

不得仅继承 Phase D 的 hash 结果。

---

# 2. Frozen Authority Mutation Ban

整个 Phase E campaign 永远禁止修改：

```text
Phase B/C qualification ZIP

CASE.json

CASE_INDEX.json

QUALIFICATION_CASE_MANIFEST.json

PHASE_A_AUTHORITY.json

UPLOAD_*

SOURCE_*

LICENSE.txt

PROVENANCE.json

SHA256SUMS.txt

canonical positive question

scientific values

units

wavelength

q-path

prediction

uncertainty

sample identity

material identity

calculation identity

semantic kind

expected capability

expected Tool

expected Artifact

expected Renderer

expected limitation

expected report behavior

expected Recipe behavior
```

Qualification failure：

```text
MUST NOT
→ mutate qualification authority
```

---

# 3. Existing Paraphrase Truth Remains Separate

Current authority remains:

```text
CANONICAL_PRIMARY_READY = 16/16

DISTINCT_PARAPHRASE_ROBUSTNESS_AUTHORITY = 7/16
```

本 Prompt 的 primary campaign：

```text
CANONICAL ONLY
```

不要把 NATURAL_PARAPHRASE 混进这 16 个 primary executions。

不要在本阶段宣称：

```text
FULL_PARAPHRASE_ROBUSTNESS = PASS
```

Phase E canonical PASS 与 paraphrase robustness 是两个不同 claim。

---

# 4. Primary Case Set

Primary canonical qualification set：

```text
Q-DATASET-001
Q-COMPOSITION-001
Q-TABLE-001

Q-ML-REG-001
Q-ML-UNC-001
Q-ML-CLASS-001

Q-STRUCTURE-001
Q-ATOMIC-VIEW-001
Q-COORD-001
Q-XRD-001
Q-STRUCTURE-RDF-001

Q-TRAJECTORY-001

Q-PHONON-001

Q-VOLUME-001

Q-ELECTRONIC-001

Q-ARCHIVE-001
```

但是：

```text
CASE.json
+
QUALIFICATION_CASE_MANIFEST.json
+
CASE_INDEX.json
```

是 machine-readable authority。

如果列表文字与 package contract 冲突：

STOP and classify the authority conflict.

不要自己决定哪个更方便。

---

# 5. Stable Execution Order

优先使用 package 中定义的 canonical case order。

如果 package 未规定执行顺序，使用：

```text
01 Q-DATASET-001
02 Q-COMPOSITION-001
03 Q-TABLE-001

04 Q-ML-REG-001
05 Q-ML-UNC-001
06 Q-ML-CLASS-001

07 Q-STRUCTURE-001
08 Q-ATOMIC-VIEW-001
09 Q-COORD-001
10 Q-XRD-001
11 Q-STRUCTURE-RDF-001

12 Q-TRAJECTORY-001

13 Q-PHONON-001

14 Q-VOLUME-001

15 Q-ELECTRONIC-001

16 Q-ARCHIVE-001
```

保持 stable ordering，使失败和最终 rerun 可比较。

---

# 6. Qualification Means Real User Flow

每个 Case 必须通过真实产品用户路径启动。

Required chain：

```text
Browser
↓
Product UI
↓
Fresh case namespace
↓
Upload / Typed Import through supported user path
↓
Product Parser / Importer
↓
Persisted Resource
↓
DataProfile
↓
CANONICAL_POSITIVE entered by Browser user action
↓
actual backend
↓
actual configured DeepSeek provider
↓
AnalysisIntent
↓
Eligibility
↓
Planner
↓
AnalysisPlan
↓
Browser user Run action
↓
Queue
↓
fresh Worker
↓
registered Adapter
↓
ToolCall
↓
persisted Artifact
↓
Workspace
↓
Renderer / Viewer
↓
grounded Interpretation
↓
Report Preview
↓
Report Finalize
↓
Recipe
```

Anything materially bypassing this chain is not a valid primary Case execution.

---

# 7. Real DeepSeek Is Required

Unlike Phase D:

```text
REAL_LLM_CALLS > 0
```

is now expected.

Every canonical Case requiring Agent reasoning must use the actual configured
production provider path.

Do not:

```text
mock DeepSeek

stub response

record/replay previous model response

call DeepSeek outside the product and inject the response

handcraft AnalysisIntent

handcraft AnalysisPlan

manually create Job

manually insert ToolCall

manually insert Artifact
```

Record for each Case, when available and safe:

```text
provider
model identity
request/trace identity
latency
retry count
fallback occurrence
```

Never record API keys.

---

# 8. Provider Fallback Policy

Qualification requires the intended configured provider/model policy.

If an unexpected fallback provider/model is used:

```text
CASE = FAIL
```

unless repository authority explicitly defines that fallback as part of the
qualified production policy.

Final closure should target:

```text
UNEXPECTED_PROVIDER_FALLBACKS = 0
```

---

# 9. No Retry Farming

A semantic/product failure must not be converted into PASS by repeatedly asking
the same question until the LLM happens to produce a favorable result.

For a given candidate SHA and fresh Case execution:

```text
one normal user submission
```

is the primary qualification attempt.

Built-in product retry policy may operate normally.

Manual rerun is allowed only when:

```text
a confirmed infrastructure/provider transport failure occurred
```

for example:

```text
connection reset
provider 5xx
rate limit handled outside expected product policy
browser automation transport failure
```

Such rerun must be clearly labeled:

```text
NON_SEMANTIC_TRANSIENT_RETRY
```

A wrong intent, wrong plan, wrong Tool selection or hallucinated result is:

```text
PRODUCT / AGENT FAILURE
```

not a transient retry opportunity.

Fix the product, create a new candidate, then rerun from a fresh namespace.

---

# 10. Case Isolation

Prefer:

```text
one fresh project/workspace qualification namespace per Case
```

unless the frozen Case contract explicitly requires a shared product context.

Each Case must have fresh:

```text
Project identity
Workspace identity
Resource identity
Conversation/session identity where applicable
Job identity
ToolCall identity
Artifact identity
Report identity
```

Do not reuse previous Case Artifacts as current evidence.

Do not let one Case accidentally discover another Case's resources.

---

# 11. Case Fixture Handling

For each Case:

read its actual:

```text
CASE.json
PROVENANCE.json
README.md
```

and declared assets.

Upload only:

```text
UPLOAD_*
```

through the product-supported user entry path.

`SOURCE_*` is provenance authority unless the contract explicitly says it is
also a user upload asset.

Do not upload SOURCE files merely because they contain richer data.

---

# 12. File Order Has No Scientific Authority

Never infer semantic role from:

```text
file order
filename order
ZIP order
upload order
```

Use:

```text
CASE asset role
semanticKind
resource identity
companion relationship
product DataProfile
```

as authority.

This is especially important for paired/multi-resource Cases.

---

# 13. Q-XRD-001 Special Contract

Treat XRD qualification as an actual paired scientific resource scenario.

Expected conceptual relationship:

```text
Crystal Structure
+
Experimental XRD
```

Require correct:

```text
material/phase relationship
wavelength identity
2θ/intensity semantics
resource role binding
```

Do not:

```text
guess wavelength
reproject wavelength
fabricate phase correspondence
bind by upload order
```

If current product cannot correctly establish required resource semantics:

CASE FAILS.

Fix product behavior only if frozen existing product authority says it should
support this scenario.

---

# 14. Q-PHONON-001 Special Contract

Normal-user qualification input is based on the frozen typed resources.

Conceptually:

```text
Structure
+
Phonon Band
+
Phonon DOS
```

Do not convert:

```text
generic phonon YAML/JSON
```

into newly executable support.

Do not add eigenvector import to make phonon animation qualify.

Current phonon animation gap remains outside the execution-ready normal-user
surface unless current frozen authority explicitly changes through a separately
reviewed product decision.

---

# 15. Q-ELECTRONIC-001 Special Contract

Electronic Band and Electronic DOS must preserve compatible scientific identity.

Require contract authority for:

```text
same/compatible material identity
same/compatible calculation context
energy units
energy reference
source-supplied Fermi identity where required
```

Do not combine unrelated resources merely because both parse.

---

# 16. Q-TRAJECTORY-001 Special Contract

Require actual trajectory semantics defined by the Case contract, including
where applicable:

```text
stable atom/species identity
coordinates
units
cell/PBC
monotonic physical time
sufficient frames
```

Do not silently promote a structure-animation file into a diffusion-capable
trajectory.

---

# 17. ML Case Integrity

For:

```text
Q-ML-REG-001
Q-ML-UNC-001
Q-ML-CLASS-001
```

do not manufacture model output inside qualification.

Preserve source-defined:

```text
target
prediction
uncertainty
class
probability
model identity
sample identity
```

where required by the Case.

Never derive an artificial uncertainty from residuals simply to satisfy the
product.

---

# 18. Q-ARCHIVE-001 Semantic Rule

Always preserve:

```text
ZIP = container format
```

not:

```text
ZIP = scientific semantic kind
```

Qualification should prove the product correctly dispatches contained supported
resources according to its existing archive/import contract.

Do not add new archive semantics to force success.

---

# 19. Per-Case Phase 1 — Import Qualification

For each Case first verify:

```text
UPLOAD_ACCEPTED

EXPECTED_ENTRY_PATH_USED

EXPECTED_NUMBER_OF_RESOURCES_CREATED

SEMANTIC_KINDS_CORRECT

RESOURCE_ROLES_CORRECT

RESOURCE_IDENTITIES_STABLE

REQUIRED_COMPANION_RELATIONSHIPS_CORRECT

DATAPROFILE_CREATED

DATAPROFILE_FACTS_CORRECT

NO_UNEXPECTED_IMPORT_WARNING

NO_UNEXPECTED_IMPORT_DATA_LOSS
```

Do not proceed blindly if import already violated the Case contract.

---

# 20. Per-Case Phase 2 — Agent Qualification

Enter the exact:

```text
CANONICAL_POSITIVE
```

question from Case authority via Browser UI.

Do not rewrite it.

Do not make it “clearer”.

Capture:

```text
user message identity
conversation/session identity
provider/model identity
resulting AnalysisIntent identity
```

Verify:

```text
NO_UNEXPECTED_CLARIFICATION

INTENT_MATCHES_CASE_REQUIREMENT

RESOURCE_REFERENCES_CORRECT

NO_CROSS_CASE_RESOURCE_REFERENCE
```

If clarification is not expected and the Agent asks unnecessary clarification:

CASE FAILS.

---

# 21. Eligibility Qualification

Verify actual product Eligibility path.

Require:

```text
expected eligibility disposition
required facts satisfied
required resources resolved
no unsupported capability promotion
no hidden missing requirement
```

Do not bypass Eligibility to reach execution.

---

# 22. Planner Qualification

Inspect the actual generated Plan.

Do not manually edit it unless normal product UX explicitly includes a user
approval action that does not change qualification semantics.

Verify against `CASE.json`:

```text
expected capabilities represented

expected Tools represented

required dependencies represented

correct resource bindings

correct ordering/dependency graph

no forbidden Tool substitutions

no unsupported capability

no synthetic resource

no scientific value invention
```

A plan that merely “looks plausible” is not sufficient.

---

# 23. Run Must Be User-Initiated Through Product UI

The actual analysis execution must begin via normal Browser product action.

Do not invoke the Job API directly as the qualification initiator.

Backend/API/DB tools may be used for:

```text
observation
evidence collection
cross-checking
```

after the normal user action.

They may not replace the user action.

---

# 24. Queue / Worker Qualification

For each Case record:

```text
Job ID
Queue identity
Worker identity
Worker repository SHA
ToolCall IDs
terminal Job state
timestamps
```

Require:

```text
JOB_DISPATCHED_THROUGH_CANONICAL_QUEUE = YES

WORKER_IS_CURRENT_CANDIDATE = YES

REGISTERED_ADAPTER_PATH = YES
```

No hand-created Job counts.

---

# 25. Expected Tools Are Contract Assertions

Case PASS requires its contract-relevant expected Tool behavior.

Do not reduce Tool assertions to:

```text
some Job succeeded
```

For each case derive:

```text
EXPECTED_TOOL_SET
OBSERVED_TOOL_SET
MISSING_TOOLS
UNEXPECTED_TOOLS
```

Unexpected auxiliary internal Tools may be allowed only if current product
authority explicitly allows them and they do not change scientific semantics.

Any required Tool missing:

```text
CASE FAIL
```

---

# 26. Artifact Qualification

For every expected Case-relevant Artifact record:

```text
Artifact ID
artifactType
artifactContractVersion
producer ToolCall
project identity
resource lineage
required fields
identity fields
storage object identity/hash when available
```

Require:

```text
EXPECTED_ARTIFACTS_PRODUCED = YES
```

Do not treat Job success as Artifact success.

---

# 27. Artifact Scientific Integrity

Artifact content must remain grounded in:

```text
uploaded source
product scientific computation
registered Adapter output
```

Do not allow:

```text
LLM-generated numeric arrays
LLM-generated units
LLM-generated scientific values
frontend-invented data
```

to substitute for Artifact authority.

If the Artifact has scientific validation invariants defined in current
repository authority, run those appropriate assertions.

---

# 28. UI / Renderer Qualification

Every Case-relevant expected Artifact must be opened through the actual UI.

Do not qualify Renderer coverage purely from registry mapping.

For each Artifact verify:

```text
Artifact reachable in Workspace

correct renderer selected

viewer loads

no fatal runtime error

required metadata visible

required units visible

required limitation visible

required numeric/table fallback visible where specified

selection behavior works where required

Inspector behavior works where required
```

Capture Browser evidence.

---

# 29. Renderer Must Not Recompute Scientific Results

Verify that Viewer/Renderer displays persisted scientific authority rather than
silently performing a competing frontend scientific calculation.

Frontend presentation transformations are allowed according to repository
contract.

New scientific derivation that changes authoritative values is not.

---

# 30. Grounded Interpretation Qualification

Inspect Interpretation/Findings generated by the real Agent.

Case-specific contract is authority.

At minimum check:

```text
observations grounded in produced Artifacts

numeric claims traceable

units traceable

resource/material identity correct

limitations preserved
```

Forbidden interpretation behavior includes:

```text
invented numeric value

invented unit

invented phase confirmation

invented stability conclusion

unsupported causal claim

unsupported scientific certainty

silently upgrading SUPPORTED_WITH_LIMITS to unrestricted support
```

A scientifically overclaiming interpretation is a Case failure even if Tools
and Artifacts were correct.

---

# 31. SUPPORTED_WITH_LIMITS Must Prove the Limit

For every Case whose support disposition is:

```text
SUPPORTED_WITH_LIMITS
```

success alone is insufficient.

Require:

```text
LIMITATION_PRESERVED = YES
```

at every applicable layer:

```text
eligibility
plan
artifact metadata
viewer
interpretation
report
```

according to repository/Case contract.

Qualification must prove the limitation is not lost.

---

# 32. Report Preview Qualification

For all 16 primary Cases:

```text
REPORT_PREVIEW_EXPECTED = YES
```

Open/generate Report Preview through normal product UI.

Verify:

```text
report references correct project/resources

report evidence references actual Artifacts

numeric/scientific claims are grounded

limitations preserved

no unrelated Case data

no hallucinated scientific results
```

Require:

```text
REPORT_PREVIEW_PASS = YES
```

---

# 33. Report Finalize Qualification

For all 16 Cases:

```text
REPORT_FINALIZE_EXPECTED = YES
```

Finalize through normal product UI.

Record:

```text
Report ID
final version identity
artifact/evidence references
```

Require:

```text
REPORT_FINALIZE_PASS = YES
```

Do not directly mutate report persistence to manufacture a finalized state.

---

# 34. Recipe Qualification

For all 16 Cases:

```text
RECIPE_EXPECTED = YES
```

Verify:

```text
Recipe exists
Recipe is structurally valid
Recipe reflects actual workflow
Recipe references appropriate resources/capabilities
```

But:

```text
RECIPE_EXECUTION = FORBIDDEN
```

for this primary Phase E campaign.

Require:

```text
RECIPE_PRESENT = YES
RECIPE_EXECUTED = NO
```

---

# 35. Browser Error Qualification

During every Case inspect:

```text
console errors
page exceptions
failed network requests
viewer runtime errors
```

Classify:

```text
blocking
qualification-relevant
known-benign
unrelated
```

Do not silently ignore Browser errors.

Final target:

```text
UNEXPECTED_QUALIFICATION_RELEVANT_BROWSER_ERRORS = 0
```

---

# 36. Backend / Worker Error Qualification

Capture relevant backend/Worker evidence around each Case.

Inspect for:

```text
tracebacks
unhandled exceptions
retry storms
serialization errors
database failures
object-store failures
queue failures
adapter failures
```

A Job returning success while the logs contain qualification-relevant hidden
errors must be investigated.

---

# 37. Per-Case Evidence Package

Create a dedicated evidence directory for each Case.

Suggested conceptual layout:

```text
phase_e/
  campaign_<id>/
    cases/
      Q-DATASET-001/
      ...
      Q-ARCHIVE-001/
```

Follow repository governance when a canonical location already exists.

Each case should contain at minimum:

```text
CASE_EXECUTION.json

IMPORT_EVIDENCE.json

AGENT_EVIDENCE.json

PLAN_EVIDENCE.json

RUNTIME_EVIDENCE.json

TOOLCALL_EVIDENCE.json

ARTIFACT_EVIDENCE.json

UI_RENDERER_EVIDENCE.json

INTERPRETATION_EVIDENCE.json

REPORT_EVIDENCE.json

RECIPE_EVIDENCE.json

BROWSER_EVIDENCE.json

CASE_RESULT.md

SHA256SUMS.txt
```

Use actual available evidence contracts where repository governance already
defines equivalents.

---

# 38. Per-Case Mechanical Decision

Each Case must finish as exactly one:

```text
PASS

FAIL_PRODUCT_DEFECT

FAIL_SCIENTIFIC_DEFECT

FAIL_AGENT_ROUTING

FAIL_ELIGIBILITY

FAIL_PLANNER

FAIL_RUNTIME

FAIL_ADAPTER

FAIL_ARTIFACT

FAIL_RENDERER_UI

FAIL_INTERPRETATION

FAIL_REPORT

FAIL_RECIPE

FAIL_PROVIDER

FAIL_INFRASTRUCTURE

BLOCKED_EXTERNAL

BLOCKED_AUTHORITY_CONFLICT
```

Do not use:

```text
PARTIAL_PASS
MOSTLY_PASS
GOOD_ENOUGH
```

as final primary qualification status.

---

# 39. Failure Classification

When a Case fails, classify root cause into one primary category:

```text
INPUT_IMPORT_DEFECT

PARSER_DEFECT

DATAPROFILE_DEFECT

AGENT_ROUTING_DEFECT

LLM_INTEGRATION_DEFECT

ELIGIBILITY_DEFECT

PLANNER_DEFECT

RUNTIME_DEFECT

QUEUE_DEFECT

WORKER_DEFECT

ADAPTER_DEFECT

SCIENTIFIC_IMPLEMENTATION_DEFECT

ARTIFACT_CONTRACT_DEFECT

PERSISTENCE_DEFECT

RENDERER_UI_DEFECT

INTERPRETATION_GROUNDING_DEFECT

REPORT_DEFECT

RECIPE_DEFECT

PROVIDER_TRANSIENT

INFRASTRUCTURE_TRANSIENT

QUALIFICATION_CONTRACT_DEFECT

FIXTURE_DEFECT

EXTERNAL_PERMISSION_BLOCKER

SCOPE_EXPANSION_REQUIRED
```

---

# 40. Autonomous Product Remediation Is Authorized

For actual product defects revealed by a valid frozen qualification Case, you
are authorized to:

```text
inspect
diagnose
modify production code
add regression tests
run tests
restart services
commit remediation
rerun qualification
```

without stopping to request routine approval.

The intent is:

```text
fix the product
```

not:

```text
fix the test
```

---

# 41. Authorized Product Fix Areas

When repository evidence supports the existing intended behavior, remediation
may include:

```text
parser/importer bug fixes

DataProfile bug fixes

resource identity fixes

Agent routing fixes

provider integration fixes

Eligibility fixes

Planner fixes

execution graph fixes

queue/Worker fixes

Adapter fixes

scientific implementation bug fixes within already-supported capability

Artifact persistence fixes

Artifact contract implementation fixes

Renderer/viewer fixes

Workspace fixes

Interpretation grounding fixes

Report fixes

Recipe generation fixes

migration/persistence fixes

runtime configuration fixes
```

Every change must preserve frozen support authority.

---

# 42. Scientific Fix Boundary

A bug in an already-supported scientific capability may be fixed.

But do not:

```text
add new scientific capability

change unsupported → supported

change mapping-only → executable

remove an existing documented limitation

fabricate missing scientific data

alter qualification source values
```

If success requires support expansion:

```text
SCOPE_EXPANSION_REQUIRED
```

and STOP.

---

# 43. Frozen Authority Conflict Rule

If strong evidence indicates:

```text
CASE.json itself is scientifically incorrect

fixture provenance is incorrect

UPLOAD asset was incorrectly normalized

expected Tool/Artifact contract contradicts frozen repository authority

qualification package contains an internal contradiction
```

do NOT silently repair it.

Classify:

```text
BLOCKED_AUTHORITY_CONFLICT
```

Produce precise evidence and stop the campaign for Reviewer action.

Changing frozen Phase B/C authority requires a separately versioned reopening
of Phase B/C.

---

# 44. Regression Test Requirement

Every production defect fixed during Phase E must receive an appropriate
regression test whenever practical.

A valid regression test should:

```text
fail before fix
pass after fix
```

and target the actual defect layer.

Examples:

```text
parser defect → parser/import integration test

planner defect → planner contract test

adapter defect → service-backed Adapter test

renderer defect → frontend/browser/component test

scientific bug → scientific invariant/reference regression

persistence defect → production repository integration test
```

Do not substitute a low-level test for a failed higher-level Case.

---

# 45. Focused Fix Verification

After each fix:

```text
run new regression
+
run directly affected existing tests
```

before returning to Live qualification.

Do not immediately spend another real LLM execution on obviously broken code
without first passing local deterministic tests.

---

# 46. Commit Every Runtime Candidate

Every set of production runtime changes used for a new Live rerun must be
represented by an immutable local Git commit before qualification evidence is
considered authoritative.

Require:

```text
CANDIDATE_COMMITTED = YES
PRODUCTION_RUNTIME_AFFECTING_UNCOMMITTED_DIFFS = 0
```

No push is required unless separately authorized.

Do not force-push.

Do not rewrite unrelated history.

---

# 47. Service Identity After Fix

After a production fix:

restart/reload every affected runtime component so that the next Case actually
uses the new candidate.

At minimum consider:

```text
Backend
Frontend
Worker
```

and migrations/bootstrap when affected.

Record:

```text
candidate SHA
backend candidate identity
frontend candidate identity
worker candidate identity
```

A Worker still running old code invalidates the rerun.

---

# 48. Phase D Re-Seal Trigger

If a Phase E remediation changes any of:

```text
migration

database/bootstrap

project/workspace persistence

runtime configuration

Compose/runtime authority

queue configuration

Worker initialization

object-store bootstrap

provider configuration/policy

Registry initialization

input support contract

fresh namespace behavior
```

then before further canonical Case execution:

```text
RE-RUN COMPLETE PHASE D
```

against the new candidate.

Require again:

```text
PHASE_D = PASS
READY_FOR_PHASE_E = YES
```

Do not assume the earlier environment seal survives such changes.

---

# 49. Lightweight Environment Revalidation

For fixes that do not alter Phase D-sensitive environment contracts, at least
reconfirm before Live rerun:

```text
DB healthy
Redis healthy
MinIO healthy
Backend healthy
Frontend healthy
fresh/current Worker
Browser reachable
provider configuration
production runtime diff = 0
```

Final campaign closure still requires a complete Phase D pass on the final SHA.

---

# 50. Failure Rerun Rule

After fixing a Case:

rerun that Case from a completely fresh Case namespace.

Do not reuse:

```text
old resource
old Plan
old Job
old Artifact
old Report
old LLM response
```

The rerun is a new user flow.

Historical failed evidence remains preserved.

---

# 51. Previously Passed Cases After Production Change

A previous PASS obtained on an older SHA remains:

```text
HISTORICAL_PASS
```

It does not become final evidence for the new SHA.

You may continue diagnostic progression through remaining Cases to discover
additional defects efficiently.

But you must not claim final closure from mixed SHAs.

---

# 52. Discovery Campaign vs Final Campaign

Treat Phase E as two logical layers.

## Layer 1 — Discovery / Remediation Campaign

Purpose:

```text
run all 16 cases
discover defects
repair product
learn the full failure surface
```

Historical Case PASS/FAIL evidence may occur across multiple candidate SHAs.

This is acceptable for diagnosis.

It is NOT final qualification.

## Layer 2 — Final Exact-SHA Requalification

After all discovered defects are fixed:

```text
freeze ONE final candidate SHA
```

then run all 16 from scratch.

Only Layer 2 can produce final:

```text
16/16 PASS
```

---

# 53. Discovery Campaign Should Continue After Ordinary Failure

Do not necessarily stop the entire discovery campaign after the first product
failure.

For an ordinary autonomous-remediable defect:

```text
diagnose
fix
test
commit
revalidate environment
rerun failed Case
```

then continue.

Where a defect is likely to affect multiple later Cases, fix it before
continuing.

Where safe and useful, continue to expose additional independent defects rather
than waiting for Reviewer approval.

---

# 54. Hard Stop Conditions

Stop only for:

```text
BLOCKED_AUTHORITY_CONFLICT

FIXTURE_DEFECT requiring frozen package change

SCOPE_EXPANSION_REQUIRED

missing human-only secret

MFA/login requiring human

administrator/system permission unavailable

external service/account outage that cannot be safely remediated

irrecoverable repository corruption

external license/legal acceptance requirement
```

For these return the minimum required human action.

Do not stop for normal production bugs.

---

# 55. Final Candidate Preparation

Once:

```text
all 16 canonical scenarios
have passed at least once after their known defects were addressed
```

prepare the final candidate.

Require:

```text
FINAL_CANDIDATE_COMMITTED = YES

FINAL_REPOSITORY_HEAD_SHA = <exact SHA>

PRODUCTION_RUNTIME_AFFECTING_UNCOMMITTED_DIFFS = 0
```

Run all relevant deterministic regression suites.

No production runtime change is allowed after final candidate freeze without
creating a new candidate SHA.

---

# 56. Final Phase D Re-Seal

Before final 16-case requalification:

run COMPLETE Phase D against:

```text
FINAL_REPOSITORY_HEAD_SHA
```

Require:

```text
PHASE_D =
PASS /
LIVE_QUALIFICATION_ENVIRONMENT_SEALED

READY_FOR_PHASE_E = YES
```

on that same SHA.

This final Phase D evidence supersedes earlier environment seals for final
qualification purposes.

---

# 57. Final Runtime Freshness

For final qualification use:

```text
fresh Backend candidate
fresh Frontend candidate
fresh Worker candidate
fresh qualification campaign namespace
```

Do not reuse the discovery campaign's project/workspace state as final evidence.

Durable infrastructure may reuse isolated Postgres/Redis/MinIO services if
their sealed identity is unchanged and data isolation is proven.

But final Case state must be fresh.

---

# 58. Final 16-Case Campaign

Run all 16 canonical cases again from the beginning using the stable Case order.

Every Case must execute against:

```text
SAME FINAL_REPOSITORY_HEAD_SHA
```

and the same sealed environment identity.

Require all per-Case assertions again.

Do not inherit PASS status from discovery executions.

---

# 59. Production Change During Final Campaign

If Case N fails and requires any production runtime code change:

```text
FINAL CAMPAIGN IS INVALIDATED
```

Fix defect.

Add regression.

Commit a new candidate SHA.

Run complete Phase D again.

Create fresh final campaign namespace.

Restart the entire 16-case final requalification.

Previously completed final Cases become historical evidence only.

This rule is mandatory.

---

# 60. No Cross-SHA PASS Stitching

Absolutely forbidden:

```text
Case 1 PASS @ SHA A
Case 2 PASS @ SHA B
Case 3 PASS @ SHA C
...
→ claim 16/16
```

Final authority requires:

```text
ALL 16 CASES
@
ONE EXACT SHA
```

---

# 61. Final Case PASS Gate

A Case is final PASS only if all contract-applicable assertions pass.

At minimum:

```text
INPUT_IMPORT = PASS

DATAPROFILE = PASS

LIVE_AGENT = PASS

EXPECTED_PROVIDER_PATH = PASS

ANALYSIS_INTENT = PASS

ELIGIBILITY = PASS

PLAN = PASS

EXPECTED_TOOL_BEHAVIOR = PASS

QUEUE_WORKER_RUNTIME = PASS

EXPECTED_ARTIFACTS = PASS

ARTIFACT_LINEAGE = PASS

UI_RENDERERS = PASS

VIEWER_ASSERTIONS = PASS

LIMITATION_ASSERTIONS = PASS where applicable

INTERPRETATION_GROUNDING = PASS

REPORT_PREVIEW = PASS

REPORT_FINALIZE = PASS

RECIPE_PRESENT = PASS

RECIPE_EXECUTED = NO

UNEXPECTED_BROWSER_FATAL_ERRORS = 0

UNEXPECTED_RUNTIME_FATAL_ERRORS = 0
```

---

# 62. Overall Canonical Phase E PASS Gate

Final Phase E PASS requires:

```text
FINAL_CANONICAL_CASES_EXECUTED = 16/16

FINAL_CANONICAL_CASES_PASS = 16/16

FINAL_LIVE_BROWSER_CASES = 16/16

FINAL_REAL_AGENT_CASES = 16/16

FINAL_REAL_DEEPSEEK_CASES = 16/16
```

where Agent/DeepSeek applicability is according to actual frozen product path.

Also require:

```text
EXPECTED_TOOL_ASSERTIONS = 100%

EXPECTED_ARTIFACT_ASSERTIONS = 100%

CASE_RELEVANT_ARTIFACTS_OPENED_IN_UI = 100%

EXPECTED_RENDERER_ASSERTIONS = 100%

REQUIRED_LIMITATION_ASSERTIONS = 100%

REPORT_PREVIEW = 16/16

REPORT_FINALIZE = 16/16

RECIPE_PRESENT = 16/16

RECIPE_EXECUTED = 0/16
```

---

# 63. Injection / Bypass Final Gate

Require:

```text
HANDCRAFTED_INTENT_INJECTION = 0

HANDCRAFTED_PLAN_INJECTION = 0

HANDCRAFTED_JOB_INJECTION = 0

HANDCRAFTED_TOOLCALL_INJECTION = 0

HANDCRAFTED_ARTIFACT_INJECTION = 0

HANDCRAFTED_REPORT_INJECTION = 0

REPLAYED_LLM_RESPONSE = 0
```

---

# 64. Provider Final Gate

Require:

```text
UNEXPECTED_PROVIDER_FALLBACKS = 0
```

and record actual provider/model identities for the final campaign.

Do not expose secrets.

---

# 65. Scientific Integrity Final Gate

Require:

```text
SCIENTIFIC_FIXTURE_CHANGES = 0

SCIENTIFIC_VALUE_FABRICATION = 0

UNIT_GUESSING = 0

WAVELENGTH_REPROJECTION = 0

Q_PATH_GUESSING = 0

MISSING_DATA_FABRICATION = 0

UNAUTHORIZED_SUPPORT_EXPANSION = 0
```

---

# 66. Qualification Authority Final Gate

At the end, recompute again:

```text
QUALIFICATION_PACKAGE_SHA256

root SHA256SUMS

all case SHA256SUMS
```

Require unchanged:

```text
QUALIFICATION_PACKAGE_SHA256 =
3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952

ROOT_HASH_MISMATCHES = 0

CASE_HASH_MISMATCHES = 0
```

This proves the test did not mutate its own authority.

---

# 67. Final Coverage Matrix

Generate:

```text
FINAL_QUALIFICATION_MATRIX.json
```

At minimum include dimensions:

```text
Case
×
Input
×
Semantic Kind
×
Capability Family
×
Tool
×
Artifact
×
Renderer
×
Interpretation
×
Report
×
Recipe
×
Support Disposition
×
Final Status
```

Derive actual coverage from observed final executions.

Do not merely copy Phase A planned coverage.

---

# 68. Repository vs Live-Execution Surface

Keep separate:

```text
repository capability surface
```

from:

```text
normal-user live execution-ready surface
```

Do not claim all repository capabilities live-qualified when the input path does
not permit normal-user execution.

Example principle:

```text
capability exists in Registry
!=
live-user qualification applicable
```

Preserve known execution-readiness limitations.

---

# 69. Phonon Animation Claim

Unless a separately approved product change has legitimately changed frozen
support authority:

do not claim phonon animation live-qualified merely because phonon Band/DOS
Case passes.

Report it separately as the actual current authority dictates.

Do not manufacture eigenvector input.

---

# 70. Paraphrase Claim

Final canonical Phase E closure does NOT automatically change:

```text
PARAPHRASE_ROBUSTNESS_CURRENT_AUTHORITY = 7/16
```

Final report must explicitly say:

```text
CANONICAL_PRIMARY_QUALIFICATION = 16/16 PASS
```

separately from:

```text
FULL_PARAPHRASE_ROBUSTNESS =
NOT ESTABLISHED BY THIS CAMPAIGN
```

unless a separately authorized paraphrase campaign was actually executed.

---

# 71. Negative / Clarification Claim

Likewise, do not claim:

```text
FULL_NEGATIVE_BOUNDARY_QUALIFICATION
```

or:

```text
FULL_CLARIFICATION_QUALIFICATION
```

unless those independent Cases were actually run.

This Prompt's final 16-case campaign is canonical positive qualification.

---

# 72. Final Evidence Root

Create one final campaign evidence root following repository governance.

At minimum preserve:

```text
discovery runs

failed case executions

remediation commits

regression evidence

candidate transitions

final Phase D seal

final 16-case executions

final qualification matrix
```

Never delete failed historical evidence just because a later rerun passes.

---

# 73. Campaign-Level Evidence

At minimum generate:

```text
PHASE_E_FINAL_RESULT.md

CAMPAIGN_MANIFEST.json

CANDIDATE_HISTORY.json

DEFECT_LEDGER.json

REMEDIATION_LINEAGE.json

FINAL_ENVIRONMENT_REFERENCE.json

FINAL_PHASE_D_REFERENCE.json

FINAL_CASE_INDEX.json

FINAL_QUALIFICATION_MATRIX.json

TOOL_COVERAGE.json

ARTIFACT_COVERAGE.json

RENDERER_COVERAGE.json

INTERPRETATION_COVERAGE.json

REPORT_RECIPE_COVERAGE.json

PROVIDER_EXECUTION_SUMMARY.json

BROWSER_ERROR_SUMMARY.json

RUNTIME_ERROR_SUMMARY.json

SCIENTIFIC_INTEGRITY_SUMMARY.json

WORKTREE_CLASSIFICATION.json

TEST_RESULTS.json

SHA256SUMS.txt
```

Use existing repository contracts if equivalent canonical artifacts already
exist.

---

# 74. Candidate History

`CANDIDATE_HISTORY.json` must record every candidate used during the campaign:

```text
candidate SHA

parent SHA

reason created

defects fixed

tests run

Phase D re-seal required?

Case executions performed

final/non-final
```

This makes mixed-SHA discovery history auditable without contaminating the
final result.

---

# 75. Defect Ledger

For every discovered defect record:

```text
defectId

firstObservedCase

firstObservedSHA

classification

symptom

rootCause

repository authority

production files changed

scientific behavior affected?

support surface affected?

regression tests

fix commit SHA

affected historical Case results

final disposition
```

Do not hide defects that were later repaired.

---

# 76. Screenshot / Browser Evidence

Capture sufficient Browser evidence to prove actual user-flow assertions.

Prefer meaningful checkpoints rather than indiscriminate screenshots.

For each Case capture at least where applicable:

```text
import/resource readiness

canonical question submitted

generated plan

terminal result/workspace

key viewer(s)

interpretation

Report Preview

finalized Report

Recipe
```

Store without leaking secrets/private credentials.

---

# 77. IDs and Lineage

For each final Case preserve identifiers sufficient to trace:

```text
Project
Workspace
Conversation/session
Resource(s)
AnalysisIntent
Eligibility result
AnalysisPlan
Job
ToolCall(s)
Artifact(s)
Report
Recipe
```

where the product exposes those identities.

The Reviewer must be able to follow:

```text
user action
→ runtime
→ scientific result
→ rendered evidence
```

---

# 78. Evidence Hashing

Generate SHA256 manifests for stable evidence.

Do not hash volatile files in a way that makes the evidence package
self-invalidating.

Document hash policy.

Final evidence self-check requires:

```text
MISSING_EVIDENCE_FILES = 0

EVIDENCE_HASH_MISMATCHES = 0
```

---

# 79. Secret / Privacy Scan

Before closure scan evidence for:

```text
API keys
passwords
tokens
database passwords
MinIO secret keys
authorization headers
private credentials
```

Require:

```text
SECRET_SCAN = PASS
```

Redact credentials while preserving non-secret execution identity.

---

# 80. Final Git Truth

At final closure record:

```text
FINAL_REPOSITORY_HEAD_SHA

HEAD_EQUALS_ORIGIN_MASTER

GLOBAL_WORKTREE_CLEAN

PRODUCTION_RUNTIME_AFFECTING_UNCOMMITTED_DIFFS
```

Do not force origin equality.

Final required runtime condition:

```text
PRODUCTION_RUNTIME_AFFECTING_UNCOMMITTED_DIFFS = 0
```

Evidence/governance files may remain locally dirty if accurately classified.

---

# 81. Final Regression Suite

Before final closure, run all repository-defined test suites materially affected
by campaign remediation.

Include appropriate:

```text
migration
persistence
import/parser
DataProfile
Agent/planner
runtime
Worker
Adapter
scientific
Artifact
Workspace
Renderer/UI
Report
Recipe
qualification governance
```

according to actual defects found.

Record exact commands and results.

---

# 82. Final Result — PASS

Only if all 16 final canonical cases pass at ONE exact SHA:

```text
PHASE_E =
PASS /
CANONICAL_LIVE_AGENT_BROWSER_QUALIFICATION_COMPLETE

FINAL_REQUALIFICATION =
PASS /
SINGLE_EXACT_SHA_16_OF_16

FINAL_CANONICAL_CASES =
16/16 PASS

READY_FOR_REVIEWER =
YES
```

Report at minimum:

```text
FINAL_REPOSITORY_HEAD_SHA = ...

FINAL_MIGRATION_HEAD = ...

QUALIFICATION_PACKAGE_SHA256 =
3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952

FINAL_PHASE_D = PASS

CANONICAL_CASES_EXECUTED = 16/16

CANONICAL_CASES_PASS = 16/16

LIVE_BROWSER_CASES = 16/16

LIVE_AGENT_CASES = 16/16

REAL_PROVIDER_CASES = 16/16
or exact applicable count with explanation

EXPECTED_TOOL_ASSERTIONS = 100%

EXPECTED_ARTIFACT_ASSERTIONS = 100%

CASE_RELEVANT_ARTIFACTS_OPENED_IN_UI = 100%

EXPECTED_RENDERER_ASSERTIONS = 100%

REQUIRED_LIMITATION_ASSERTIONS = 100%

REPORT_PREVIEW = 16/16

REPORT_FINALIZE = 16/16

RECIPE_PRESENT = 16/16

RECIPE_EXECUTED = 0

UNEXPECTED_PROVIDER_FALLBACKS = 0

HANDCRAFTED_INTENT_INJECTION = 0

HANDCRAFTED_PLAN_INJECTION = 0

HANDCRAFTED_JOB_INJECTION = 0

HANDCRAFTED_ARTIFACT_INJECTION = 0

REPLAYED_LLM_RESPONSE = 0

QUALIFICATION_PACKAGE_CHANGES = 0

SCIENTIFIC_FIXTURE_CHANGES = 0

PRODUCTION_RUNTIME_AFFECTING_UNCOMMITTED_DIFFS = 0

OPEN_CANONICAL_BLOCKING_DEFECTS = 0

PARAPHRASE_ROBUSTNESS_CURRENT_AUTHORITY = 7/16

FULL_PARAPHRASE_ROBUSTNESS_CLAIMED = NO

FULL_NEGATIVE_BOUNDARY_QUALIFICATION_CLAIMED = NO

READY_FOR_REVIEWER = YES
```

---

# 83. Final Result — BLOCKED

Do not end BLOCKED for ordinary product defects that are authorized for
autonomous remediation.

BLOCKED is allowed only for an actual hard stop such as:

```text
frozen qualification authority conflict

fixture defect requiring package revision

scientific support-surface expansion required

human-only credential/MFA

administrator/system action unavailable

external service/account hard failure

repository corruption unsafe to repair autonomously
```

Then output:

```text
PHASE_E =
BLOCKED /
HARD_QUALIFICATION_BLOCKER

FINAL_REQUALIFICATION = NOT_COMPLETE

READY_FOR_REVIEWER = YES
```

and specify:

```text
blockerId

classification

affected Case(s)

first observed SHA

root cause

why autonomous remediation cannot continue

frozen authority affected?

minimum human/reviewer action required

which evidence remains valid

what must be invalidated/rerun after resolution
```

---

# 84. Do Not Hide Partial Progress

If a hard blocker stops final completion, still return:

```text
cases attempted
cases passed historically
cases failed
defects repaired
candidate SHAs
final-candidate status
```

But do not turn historical mixed-SHA PASSes into a final percentage.

---

# 85. Final Reviewer Package

When complete, package all final campaign evidence into one Reviewer-friendly
artifact or directory.

It must contain enough information for an independent Reviewer to answer:

```text
1. Which exact code was qualified?

2. Which exact Phase B/C package was used?

3. Were all 16 canonical cases run through Browser?

4. Were real LLM/provider calls used?

5. Did the normal product chain create Plans/Jobs/Artifacts?

6. Did a fresh Worker execute the work?

7. Were all required Artifacts actually opened and rendered?

8. Were scientific limitations preserved?

9. Were interpretations grounded?

10. Did Report Preview and Finalize work?

11. Was Recipe produced but not executed?

12. What defects were discovered?

13. What was changed to fix them?

14. Were all final Cases rerun after the final production change?

15. Did all 16 final PASSes occur on one exact SHA?

16. Was the frozen qualification package unchanged?

17. What remains explicitly unqualified?
```

---

# 86. Critical Operational Principle

The objective is not:

```text
MAKE THE DASHBOARD GREEN
```

The objective is:

```text
DISCOVER THE TRUTH
→ FIX REAL PRODUCT DEFECTS
→ PRESERVE TEST AUTHORITY
→ REQUALIFY THE ACTUAL PRODUCT
→ PROVE 16/16 ON ONE EXACT SHA
```

A truthful FAIL is better than an artificial PASS.

A repaired product followed by complete requalification is the desired outcome.

---

# 87. Final Stop Boundary

Once either:

```text
PHASE_E =
PASS /
CANONICAL_LIVE_AGENT_BROWSER_QUALIFICATION_COMPLETE
```

or a genuine:

```text
HARD_QUALIFICATION_BLOCKER
```

has been reached:

STOP.

Do not autonomously start:

```text
paraphrase robustness expansion
negative boundary campaign
clarification campaign
new scientific capability implementation
phonon animation support expansion
future release work
```

Return the complete evidence package for independent Reviewer evaluation.

The Reviewer will decide whether to:

```text
ACCEPT Phase E

request remediation

authorize paraphrase qualification

authorize negative/boundary qualification

proceed to comprehensive final qualification archive
```


---END---
