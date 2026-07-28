---TASK---
 状态：处理中
你现在执行：

# Phase 10K-4：Composition Space / Embedding / Clustering

本阶段是 Phase 10K Material Intelligence Layer 的第四个正式实现阶段。

目标是：

> 将 Phase 10K-1 的 composition semantics、Phase 10K-2 的 Dataset Materials Explorer、Phase 10K-3 的 sample/model identity 继续向前推进，形成一个真正面向材料数据集的 **Composition Space Explorer**。

用户最终应该能够回答：

* 这批材料在组成空间里如何分布？
* 数据集覆盖了哪些组成区域？
* 哪些材料彼此组成相近？
* 是否存在明显 cluster？
* 哪些样本位于数据集边缘或是统计异常候选？
* 某个 property / prediction error 在组成空间中如何分布？
* train/test 或两个 dataset 的组成空间覆盖是否明显不同？
* 从一个点能否回到具体材料样本？

本阶段不是通用机器学习降维平台。

本阶段不训练模型。

本阶段不实现 Agent Intelligence。

---

# 0. Hard Entry Gate

首先验证真实 repository。

必须确认：

```text
Phase 10J-6 = ARCHIVED
Gate J6-R = PASS
Phase 10K-0 = ARCHIVED
Phase 10K-1 = ARCHIVED
Phase 10K-2 = ARCHIVED
Phase 10K-3 = ARCHIVED
Phase 10K-4 = NEXT
```

必须读取 Phase 10K-3 的真实：

* result
* implementation record
* DataProfile binding
* sample identity
* Materials ML contracts
* artifact/provenance conventions
* browser evidence
* completion record
* next-scope document

如果任意硬条件不满足：

输出：

`BLOCKED_BY_PHASE_10K_3`

然后停止。

不得自行假设 10K-3 已完成。

---

# 1. Canonical Context

当前 Phase 10K：

```text
10K-1
Material Data Profile 2.0

10K-2
Dataset Materials Explorer

10K-3
Materials ML Evaluation

10K-4
Composition Space / Embedding / Clustering

10K-5
Material Intelligence Integration + Browser/API Evidence
```

Phase 10K-4 是 Phase 10K 最后一个新的分析产品实现阶段。

10K-5 负责整个 Material Intelligence Layer 的集成与闭环。

---

# 2. 核心产品定义

Composition Space Explorer 不是：

> “随便选几列跑 PCA。”

它必须以：

**canonical material composition**

为输入。

核心链路：

```text
Material Samples
      ↓
Canonical Composition
      ↓
Composition Feature Representation
      ↓
Deterministic Projection
      ↓
Optional Bounded Clustering
      ↓
Composition Space Artifact
      ↓
Interactive Explorer
      ↓
Stable Sample Inspection
```

---

# 3. 本阶段允许

允许实现：

* canonical composition feature vectors
* element-fraction representation
* deterministic composition feature matrix
* PCA or another approved baseline projection
* 2D composition space
* optional 3D composition space where useful
* bounded clustering using existing approved dependency
* property coloring
* ML error coloring
* dataset/split coloring
* sample linkage
* cluster summaries
* statistical outlier candidates
* dataset coverage comparison
* Tool Registry integration where necessary
* strict params
* PlanValidator
* QueueWorkerRuntime
* deterministic artifacts
* frontend Composition Space Explorer
* browser/API evidence
* performance/caps
* accessibility
* docs/persistent
* current-head CI

---

# 4. Explicit Non-Scope

不得实现：

## Advanced Embeddings

除非 repository 已经安装并在 10K-0 正式批准：

* learned embeddings
* graph neural network embeddings
* Mat2Vec
* Matscholar embeddings
* MEGNet embeddings
* pretrained material foundation-model embeddings

## New ML Platform

* supervised training
* embedding training
* neural clustering
* hyperparameter optimization
* AutoML

## Phase 10L

* LLM automatic method selection
* automatic multi-tool analysis planning
* Agent interpretation
* autonomous anomaly explanation

## Phase 10M

* full Unified Workspace redesign

## Phase 10N

* CrystalNN
* Experimental XRD
* trajectory analytics
* Electronic Band/DOS

## Future

* active learning
* learned latent spaces
* arbitrary notebook analysis
* external ML services

---

# 5. Baseline Verification

进入：

```text
E:\1project\Material Data Intelligence
```

运行：

```bash
git status --short
git branch --show-current
git rev-parse HEAD
git rev-parse origin/master
git log --oneline -30
git diff --stat
git diff --check
```

记录：

* repo
* branch
* initial HEAD
* origin/master
* initial status
* 10K-3 implementation commit
* 10K-3 completion-record commit
* 10K-3 archive
* exact-head CI

---

# 6. Queue Transition

只有 Entry Gate PASS 后：

将：

`Phase 10K-4：Composition Space / Embedding / Clustering`

设为唯一 active task。

更新：

* `TASKS.md`
* `persistent/TASK_BOARD.md`

不得开始：

* 10K-5
* 10L

---

# 7. 必读前序实现

完整读取：

## Phase 10K-0

重点：

* composition embedding audit
* dependency audit
* pymatviz capability inventory
* PCA/UMAP/clustering findings

## Phase 10K-1

重点：

* formula/composition semantic authority
* sample identity
* invalid formula handling

## Phase 10K-2

重点：

* canonical element identity
* chemical-system identity
* Dataset Explorer
* dataset comparison
* sample linkage
* property semantics

## Phase 10K-3

重点：

* model-result identity
* prediction-error artifacts
* sample inspection
* chemistry-conditioned metrics

不得重新实现任何这些基础能力。

---

# 8. Pre-Implementation Audit

修改代码前先输出：

# Phase 10K-4 Entry / Composition Space Product Audit

必须回答：

1. 10K-3 是否已正式 ARCHIVED？
2. composition 目前的 canonical representation 是什么？
3. formula 解析和 element fractions 当前在哪里？
4. stable sample identity 如何复用？
5. dataset comparison 当前如何表达？
6. material property semantics 如何获取？
7. ML error/uncertainty artifacts 如何与 sample 绑定？
8. 当前 dependency 是否已有 numpy/scipy/sklearn/UMAP 等？
9. pymatviz 是否已有可复用 composition clustering / embedding capability？
10. 当前是否已有 PCA helper？
11. 当前是否已有 clustering helper？
12. 是否真正需要新增 dependency？
13. 第一版 composition feature representation 应是什么？
14. 第一版 projection method 应是什么？
15. 第一版 clustering 是否应该实现？
16. UMAP 是否应该进入 Initial Release？
17. 2D/3D 前端如何最小集成？
18. 哪些能力明确留到 Future？

Audit 后直接继续。

不要等待人工确认。

---

# 9. 最重要的设计原则

# Feature Representation 必须先于 Projection

不得把：

```text
PCA coordinates
```

当作 canonical material representation。

必须明确：

```text
Composition
    ↓
Feature Vector
    ↓
Projection
```

这样未来才能：

* 重算 PCA
* 更换 projection
* 比较 dataset
* clustering
* reproducibility

---

# 10. Canonical Composition Input

必须从 Phase 10K-1/10K-2 的正式 composition semantics 获取。

不得重新：

```python
parse_formula_from_column_guess(...)
```

如果 sample 没有有效 composition：

* exclude
* count
* warning

不得 silent drop。

---

# 11. 第一版 Composition Representation

优先实现：

# Normalized Element Fraction Vector

对于每个 composition：

例如：

```text
LiFePO4
```

转换成全 dataset element basis 上的：

```text
Li
Fe
P
O
...
```

并使用 normalized atomic fractions。

必须明确：

* basis order
* normalization
* missing element = 0
* deterministic order
* fractional occupancy behavior
* invalid composition handling

---

# 12. Element Basis

element basis 必须 deterministic。

推荐：

* canonical atomic-number order

或 repository 已有正式 element order。

不得按：

“本次遇到元素的 dict insertion order”

决定 feature columns。

---

# 13. Element Fraction Semantics

如果 composition：

```text
Li2O
```

应明确使用：

```text
Li = 2/3
O = 1/3
```

而不是 raw stoichiometric counts。

除非另有正式 representation。

初版优先：

atomic fraction。

---

# 14. Fractional Occupancy / Non-Integer Formula

必须支持 pymatgen Composition 当前正式允许的合法非整数 composition。

不得假设所有 coefficients 是整数。

---

# 15. Feature Provenance

Composition-space artifact 必须记录：

* feature type
* element basis
* normalization
* number of dimensions
* excluded samples
* composition parser/provider/version

---

# 16. Magpie / Advanced Descriptors Boundary

不要默认进入：

* Magpie
* matminer
* elemental property descriptors

除非：

1. repository 已经正式依赖；
2. 10K-0 已批准；
3. 当前 product requirement 确实需要。

初版 composition-space 的核心目标：

**composition coverage**

不是 materials-property featurization benchmark。

---

# 17. Projection Baseline

第一版必须至少实现一个：

**稳定、可解释、deterministic 的线性 projection。**

优先：

# PCA

前提是现有依赖能够安全支持。

如果 repository 没有 sklearn，但 numpy/scipy 足够：

可以实现经过严格测试的小型 PCA/SVD utility。

但不要重复造已有成熟依赖。

---

# 18. PCA Contract

必须明确：

* centering
* scaling
* dimensionality
* solver
* sign stability
* explained variance
* handling rank-deficient data
* constant features
* minimum samples

---

# 19. PCA Scaling Policy

对于 atomic-fraction vectors：

不要未经讨论自动 standardize 每个 element feature 到 unit variance。

因为：

稀有元素可能因此被极大放大。

必须根据 product/scientific semantics冻结：

* center only

或：

* explicit optional standardization

推荐默认：

基于 composition fraction 的明确、可解释 PCA policy。

文档必须说明。

---

# 20. PCA Determinism / Sign Ambiguity

PCA component sign 在数学上具有 ± ambiguity。

如果 artifacts/hashes/browser evidence 需要 deterministic coordinates：

必须实现稳定 sign convention。

例如：

对每个 component：

选择绝对值最大 loading 为正。

或使用当前 library 已保证并经过 fixture 固定的方法。

必须记录。

否则相同数据可能出现：

图左右镜像但科学上等价，

却破坏 deterministic artifact。

---

# 21. Explained Variance

PCA artifact 至少记录：

* explained variance ratio PC1
* PC2
* optional PC3
* cumulative variance

如果 variance undefined / zero：

typed warning。

---

# 22. Minimum Sample Rules

例如：

1 sample

不能进行有意义 PCA。

必须 typed reject/readiness。

2 samples：

可能只能形成 1 个非零 component。

必须明确。

不得强行输出虚假 2D plane。

---

# 23. Projection Dimensions

至少支持：

* 2D

可选：

* 3D

如果 frontend 已有成熟 Plotly 3D 且实现成本小，可以支持。

但 3D 不是 PASS blocker。

2D 是核心。

---

# 24. UMAP Policy

UMAP 属于：

**optional approved enhancement**

而不是 Phase 10K-4 的绝对 PASS 条件。

只有在：

* dependency 已存在
* 10K-0 明确批准
* deterministic seed/control 可固定
* caps 明确

时才实现。

否则：

记录：

`UMAP = FUTURE/OPTIONAL_NOT_IMPLEMENTED`

不得为了本阶段新增 `umap-learn`。

---

# 25. t-SNE

初版通常不需要。

如果没有现有正式需求：

`NOT_IMPLEMENTED`

不要为了算法数量加入。

---

# 26. Projection Method UI

如果第一版只有 PCA：

不要创建假 dropdown：

```text
PCA / UMAP / t-SNE
```

只展示：

`PCA Composition Space`

未来有第二种 method 再增加 selector。

---

# 27. Clustering

本阶段需要根据真实 dependency audit 决定：

是否实现一个 bounded baseline clustering。

用户要求的 canonical Phase 名包含：

`Clustering`

因此如果现有 dependencies 足够：

应至少实现一个明确、可靠的 baseline。

优先考虑：

* KMeans

或 repository 已有更合理 method。

---

# 28. Clustering Is Optional Overlay, Not Truth

Cluster 必须表示：

> composition-feature space 中算法产生的数据分组。

不能称：

* material family truth
* phase classification
* chemistry class

使用：

`composition cluster`

---

# 29. KMeans Requirements

如果选择 KMeans：

必须明确：

* feature space
* projected space or original feature space
* number of clusters
* initialization
* random seed
* number of initializations
* maximum iterations
* convergence

推荐：

**在 canonical composition feature space 聚类。**

不要只对 2D PCA coordinates 聚类，除非正式 contract 这样设计。

Projection：

用于显示。

Feature space：

用于 clustering。

---

# 30. Randomness

任何 clustering 带 random initialization：

必须固定 deterministic seed。

seed 必须记录在 provenance。

---

# 31. Cluster Count

不得自动“发现最佳 k”然后假装科学结论。

第一版建议：

* explicit bounded `n_clusters`

以及合理 default。

如果提供 automatic suggestion：

必须非常克制，并且只是 heuristic。

不应成为必做。

---

# 32. Invalid k

必须处理：

* k < 2
* k > samples
* too few unique samples
* duplicate-only dataset

typed error/warning。

---

# 33. Cluster Summary

每个 cluster 至少提供：

* cluster ID
* sample count
* dominant elements
* dominant chemical systems
* optional property mean/median if property selected
* bounded sample examples

---

# 34. Cluster ID

Cluster IDs：

```text
Cluster 0
Cluster 1
...
```

只是算法 label。

不得赋予：

“oxide cluster”

这样的自动 scientific name。

未来 10L 可以基于 structured summary解释，但仍不能伪造科学类别。

---

# 35. Property Coloring

Composition Space Explorer 必须允许使用 DataProfile 2.0 识别出的 numeric material property：

例如：

* formation energy
* band gap
* density

对点进行颜色映射。

必须：

* preserve units
* handle missing values
* disclose valid sample count

---

# 36. ML Error Coloring

这是 10K-3 与 10K-4 的重要连接。

如果 dataset 已有 Materials ML evaluation：

允许按：

* absolute error
* residual
* uncertainty

给 composition-space points coloring。

不得 frontend 自行重算 error。

必须消费正式 ML artifact/sample binding。

---

# 37. Dataset / Split Coloring

支持：

* dataset A / dataset B
* train / validation / test

前提：

split/group identity 是显式的。

可帮助观察：

composition coverage shift。

---

# 38. Categorical Coloring

对于：

* split
* cluster
* chemical system

必须使用离散 legend。

对于：

* property
* error
* uncertainty

使用连续 scale。

不要混淆。

---

# 39. Sample Inspection

每个点必须尽可能绑定：

stable sample identity。

点击/hover 至少可以展示：

* sample ID
* formula
* chemical system
* selected property
* cluster
* dataset/split
* ML error if selected

---

# 40. Sample Identity

不得使用：

projection array index

作为 identity。

必须复用：

Phase 10K-1 / 10K-2 stable sample identity。

---

# 41. Duplicate Compositions

多个不同 sample 可能拥有完全相同 composition。

例如：

同 composition、不同 structures。

它们在 element-fraction space 中坐标完全相同。

这是正确的。

不得人为 jitter canonical coordinates。

---

# 42. Display Overlap

为了 frontend 可见性：

可以考虑：

* opacity
* point size
* hover grouping

但不得修改 canonical coordinates。

如果 display jitter：

必须仅 display-only，且明确。

最好初版不使用 jitter。

---

# 43. Structure Identity Boundary

Composition space 只描述：

composition similarity/coverage。

同组成：

不代表结构相似。

UI 和 docs 必须明确。

不得输出：

“这些晶体结构相似”

仅因为 composition points 接近。

---

# 44. Similarity Boundary

如果提供 nearest neighbors：

必须称：

`nearest compositions in selected feature space`

而不是：

`similar materials`

除非上下文明示是 composition similarity。

---

# 45. Composition Distance

如果本阶段需要 nearest composition：

明确 metric，例如：

* Euclidean distance in normalized element-fraction space

但这不是 PASS 必需。

可以留到后续。

---

# 46. Statistical Outlier Candidates

本阶段可以实现：

**composition-space statistical outlier candidate**

但必须采用明确算法。

优先简单、可解释方法。

例如：

* distance from feature-space centroid
* PCA-space distance
* cluster distance

但不能随便选 threshold。

---

# 47. Outlier Product Boundary

如果 10K-0/10K-2 已将 anomaly detection 规划到 10K-4：

实现 bounded baseline。

否则可以只支持：

visual edge inspection

而不正式创建 anomaly Tool。

本阶段必须根据真实 prior decisions执行。

---

# 48. Outlier ≠ Invalid Material

永远只称：

* composition-space outlier
* statistical outlier candidate
* low-density composition region

不得写：

* invalid material
* chemically impossible
* bad data

---

# 49. Dataset Coverage Comparison

Composition Space 的高价值功能之一：

比较：

* dataset A vs B
* train vs test

在同一个 feature basis / projection 上。

---

# 50. Shared Projection Requirement

比较两个 dataset 时：

不得分别 PCA 后再把两个坐标图放一起比较。

正确做法：

在共同 feature basis 上：

* fit shared projection

或：

* fit reference projection then transform comparison set

contract 必须明确。

---

# 51. Train/Test PCA Leakage Boundary

本阶段不是模型训练。

如果只是 dataset exploration：

可以对 combined dataset fit PCA，

但必须明确：

`exploratory combined projection`

不能把它称为：

training-safe transformation。

如果用于 ML pipeline evaluation：

应支持：

fit on train → transform test

作为 explicit mode 或 future refinement。

---

# 52. Comparison Coverage Summary

至少可以输出：

* samples A/B
* element-basis overlap
* PCA range/coverage
* cluster representation counts
* samples in regions dominated by one dataset

但不要创造：

“coverage score = 82%”

除非有正式定义。

---

# 53. Tool Granularity

不要创建：

```text
composition.vectorize
composition.pca
composition.kmeans
composition.scatter2d
composition.color
```

五个碎 Tool。

优先一个 product-level capability。

例如候选：

```text
composition.space
```

或：

```text
dataset.composition_space
```

实际命名必须遵循 registry convention。

---

# 54. Product-Level Tool

一个正式 Composition Space Tool 可以包含 params：

* projection
* dimensions
* clustering enabled
* n_clusters
* color_by
* dataset/group mode

但参数必须严格 bounded。

---

# 55. Internal Helpers

以下可以作为内部 deterministic utilities：

* feature matrix builder
* PCA
* cluster fit
* color-value resolver
* cluster summary

不一定都是 Tool Registry entries。

---

# 56. Existing pymatviz Capability

如果 pymatviz 已有：

* `cluster_compositions`
* related composition embedding plot

必须认真评估复用。

不要为了 platform uniformity 重写。

但：

如果其 API 无法满足：

* stable sample identity
* structured artifacts
* deterministic projection contract
* runtime caps

可以：

复用其 scientific/visual component

而由 application-owned adapter 负责 contract。

---

# 57. Plotly Role

Plotly 适合：

* interactive scatter
* 3D scatter
* property coloring
* hover
* selection

如果当前 frontend 已成熟：

优先复用。

不要为 Composition Space 写新的 WebGL/Three.js renderer。

---

# 58. MatterViz Boundary

本阶段不需要为了使用 MatterViz 而强行迁移 composition scatter。

MatterViz 只在确实有合适组件时使用。

---

# 59. Scientific Calculation Authority

正式：

* feature vector
* PCA
* clustering
* explained variance
* cluster summary

必须在 backend deterministic execution 中产生。

Frontend 不独立计算正式科学结果。

---

# 60. Artifact Contract

至少需要一个结构化 Composition Space artifact。

内容建议包括：

* source dataset identity
* feature representation
* element basis
* valid/excluded samples
* projection method
* projection coordinates
* explained variance
* clustering metadata
* cluster labels
* optional selected property
* optional ML metric binding
* sample identities
* warnings

实际 schema 遵循现有 Artifact conventions。

---

# 61. Plot Artifact

Plotly artifact 可以消费正式 composition-space artifact。

不要让 Plotly JSON 成为唯一 scientific artifact。

---

# 62. Provenance

必须记录：

* resource/dataset ID
* dataset version/hash
* DataProfile version
* composition parser
* feature representation
* basis
* projection method
* projection params
* cluster method
* seed
* n_clusters
* property/color binding
* exclusions
* sample count
* tool/library versions

---

# 63. Deterministic Hashing

相同：

dataset + params

必须生成相同：

* feature basis
* PCA coordinates
* cluster labels
* sample order
* artifact hash

如果 clustering labels 可 permutation：

需要 deterministic relabeling。

---

# 64. Cluster Label Stability

KMeans 的 label numbers本身没有科学含义。

但 deterministic artifact 需要稳定。

可按 cluster centroid 的 canonical lexicographic ordering 重新编号。

或采用 equivalent deterministic convention。

必须文档化。

---

# 65. Caps

至少冻结：

* max samples
* max unique elements/features
* max projection dimensions
* max clusters
* max points rendered
* max cluster summaries
* max tooltip metadata
* max output artifact size

依据 current project caps。

---

# 66. Large Dataset Strategy

分析和显示必须区分。

如果 backend 支持较大 feature matrix：

可以全量 PCA/cluster 到 analysis cap。

Frontend 只显示 bounded points。

如果 display downsampling：

必须 deterministic。

---

# 67. Sampling

不得 random sampling。

如果需要：

使用 deterministic sampling。

并记录：

* full analyzed sample count
* displayed sample count
* policy

---

# 68. High-Dimensional Element Basis

如果 dataset 覆盖大量元素：

feature matrix 可能 80–100+ dimensions。

这是正常的。

不要因为维度高就自动改成 advanced descriptor。

---

# 69. Sparse Representation

内部是否使用 dense/sparse：

根据现有 dependency和规模。

不用为了技术炫技引入 sparse framework。

---

# 70. Invalid Samples

必须报告：

* total
* valid compositions
* invalid compositions
* excluded samples
* reason categories

不能 silent drop。

---

# 71. Dataset Explorer Integration

Phase 10K-4 必须集成到 Phase 10K-2 Dataset Explorer。

建议增加：

```text
Composition Space
```

section/tab。

仅当：

composition-space data readiness = READY

才展示。

---

# 72. Frontend First Frame

至少显示：

* 2D composition projection
* point count
* projection method
* explained variance
* optional cluster legend
* color selector
* sample details

---

# 73. Controls

至少根据实现支持：

* color by
* cluster on/off
* cluster count if implemented
* dataset/group display
* 2D/3D if both supported

不要暴露大量科学意义不明的算法参数。

---

# 74. Color Options

根据实际数据动态列出：

* none / cluster
* dataset/split
* supported numeric material properties
* ML error / uncertainty if正式 artifact 可用

不得让用户选择任意 string column 并称 material property。

---

# 75. Hover / Inspect

至少：

* formula
* sample ID
* chemical system
* cluster
* selected color value
* source dataset/group

---

# 76. Linked Samples

如果 current frontend architecture 允许：

点击一个点显示 bounded sample detail。

不要求 Phase 10M 级全局 cross-panel selection。

---

# 77. Overplotting

同坐标/密集区域必须仍可用。

可采用：

* opacity
* smaller markers
* density hints

不要修改 canonical coordinates。

---

# 78. Accessibility

Composition scatter 不是 accessibility 唯一载体。

必须同时提供：

* cluster summary table
* sample table
* projection summary
* explained variance text

Controls keyboard accessible。

不能 color-only 表达 cluster/group。

---

# 79. Mobile

移动端：

* chart responsive
* controls stack
* sample details readable
* no horizontal overflow except genuinely dense bounded table

---

# 80. API / Runtime Evidence

必须走真实：

```text
DataProfile 2.0
→ AnalysisPlan
→ PlanValidator
→ QueueWorkerRuntime
→ Composition Space Adapter
→ Structured Artifact
→ Plot Artifact
→ API
→ Frontend
```

不得 frontend-only PCA。

---

# 81. Mock Planner Reachability

如果 public tool 按项目惯例需要 deterministic Planner evidence：

增加最小 route，例如：

* “show composition space”
* “cluster these compositions”

但不要实现：

LLM 自动判断“这时候应该做 PCA”。

这属于 10L。

---

# 82. Analysis Readiness

必须消费 10K-1 readiness。

最低要求：

* valid composition samples
* sufficient sample count

如 clustering：

额外要求：

* enough valid samples
* enough unique compositions

---

# 83. Typed Errors

至少覆盖：

* no composition
* insufficient valid samples
* all compositions identical
* rank-deficient projection
* invalid dimension
* invalid cluster count
* cluster count > unique samples
* selected color property unavailable
* ML metric binding unavailable
* dataset comparison binding invalid
* cap exceeded

---

# 84. Fixtures

至少：

## Case A — Simple Ternary-Like Composition Dataset

多种：

A-B-C compositions。

验证 fraction matrix 和 PCA。

## Case B — Clearly Separated Composition Groups

例如两到三个明显 composition families。

验证 clustering。

## Case C — Identical Compositions

验证 rank/cluster edge case。

## Case D — Mixed Valid / Invalid Formula

验证 exclusion。

## Case E — Property Coloring

带 numeric property。

## Case F — ML Error Coloring

复用 10K-3 evaluation fixture。

## Case G — Train/Test or Dataset A/B

验证 shared projection。

## Case H — High Element Diversity

验证 high-dimensional element basis。

---

# 85. PCA Reference Tests

至少一个 tiny fixture 必须具有：

可以独立验证的 feature matrix。

必须测试：

* fractions
* centered matrix
* projection dimension
* explained variance
* sign convention

不要只 snapshot 最终 Plotly JSON。

---

# 86. Cluster Reference Tests

如果实现 KMeans：

fixture 应具有明显分组。

测试：

* deterministic labels
* cluster counts
* centroid/summary
* seed stability

不要把 clustering output 自己复制成 expected 后宣称验证。

---

# 87. Property / ML Binding Tests

验证：

projection coordinates 和：

* property
* error
* uncertainty

通过 stable sample identity绑定。

不得通过 position zip。

---

# 88. Comparison Tests

A/B 两个 dataset：

必须验证：

共享 feature basis。

共享 projection contract。

不能分别 fit 两套 PCA。

---

# 89. Performance Evidence

至少：

* small
* medium
* near-cap

记录：

* feature build duration
* PCA duration
* clustering duration
* artifact size
* frontend render

如果 clustering 未实现：

明确 N/A。

---

# 90. Browser Evidence

按 current project policy：

至少：

* Chromium
* Firefox
* WebKit
* mobile

真实 cases：

### Case 1

PCA composition space

### Case 2

clustered composition space

### Case 3

property coloring

### Case 4

dataset/split comparison

如果 cluster 因 audit 正式 defer：

对应 browser case 不应伪造 PASS。

---

# 91. Security

所有：

* formula
* sample ID
* property name
* dataset label
* cluster label

作为 untrusted text。

禁止：

* HTML execution
* artifact JS
* arbitrary URL
* arbitrary script

---

# 92. No External Network

必须：

`NO_COMPOSITION_SPACE_EXTERNAL_NETWORK_REQUESTS`

或 repository 等价 marker。

不得：

* 在线获取 elemental embeddings
* 调外部 ML API
* 下载预训练模型

---

# 93. Secret Scan

必须：

`NO_SECRET_PATTERN_HITS`

---

# 94. Dependency Policy

必须先证明 current dependency 足够。

如果 PCA/KMeans 需要一个当前不存在的新 dependency：

不要自动安装。

先判断：

是否能使用现有 numpy/scipy 或已有 sklearn。

如果确实无法合理实现：

输出：

`REVIEWER_DECISION_REQUIRED`

不要擅自改 lockfile。

UMAP 缺 dependency：

直接 defer。

---

# 95. Regression Requirements

确保不破坏：

* DataProfile 2.0
* Dataset Explorer
* Materials ML
* existing composition tools
* structure
* trajectory
* phonon
* BZ
* volumetric
* Planner
* Registry
* QueueWorkerRuntime

---

# 96. Backend Tests

至少：

* feature-vector correctness
* canonical element order
* fraction normalization
* invalid composition handling
* PCA
* sign determinism
* explained variance
* duplicate compositions
* clustering if implemented
* cluster deterministic relabel
* property binding
* ML binding
* comparison
* caps
* typed errors

---

# 97. Frontend Tests

至少：

* composition-space panel
* projection display
* explained variance
* property selector
* cluster control if implemented
* dataset/split mode
* sample inspection
* unavailable state
* invalid/partial state
* mobile
* accessibility

---

# 98. Evidence Markers

按 repository style。

建议语义：

```text
COMPOSITION_SPACE_RUNTIME_EVIDENCE_PASS
COMPOSITION_SPACE_PCA_EVIDENCE_PASS
COMPOSITION_SPACE_SAMPLE_LINKAGE_EVIDENCE_PASS
COMPOSITION_SPACE_PROPERTY_COLOR_EVIDENCE_PASS
COMPOSITION_SPACE_DATASET_COMPARISON_EVIDENCE_PASS
COMPOSITION_SPACE_CLUSTERING_EVIDENCE_PASS
COMPOSITION_SPACE_BROWSER_EVIDENCE_PASS
COMPOSITION_SPACE_PERFORMANCE_EVIDENCE_PASS
NO_COMPOSITION_SPACE_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

如果某 optional capability 未实现：

不要生成假 marker。

---

# 99. Documentation

建议：

```text
docs/phase10k/
  phase10k4_composition_space_implementation.md
  phase10k4_composition_feature_contract.md
  phase10k4_projection_clustering_contract.md
  phase10k4_fixture_matrix.md
  phase10k4_evidence.md
  phase10k5_next_scope.md
```

可以合并重复内容。

不要创建空壳文档。

---

# 100. Capability Matrix

更新 canonical Capability Status Matrix。

真实完成后：

* Composition Feature Space
* PCA Projection
* Property Coloring
* Dataset/Split Comparison
* Clustering
* Composition-Space Sample Inspection

分别写真实状态。

例如：

```text
PCA = READY
KMeans = READY
UMAP = FUTURE
t-SNE = FUTURE
Learned Embeddings = FUTURE
```

不要用一个：

`Embedding = READY`

掩盖差异。

---

# 101. Persistent Updates

更新：

```text
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/TOOL_REGISTRY_NOTES.md
```

必要时：

`persistent/ARCHITECTURE_DECISIONS.md`

---

# 102. OPEN_QUESTIONS

关闭：

* canonical composition vectorization
* PCA policy
* component sign convention
* clustering first-batch policy
* shared dataset projection policy

剩余未来：

* UMAP
* learned material embeddings
* advanced anomaly detection

应移入：

Future / non-blocking。

---

# 103. Architecture Decision

如果正式建立：

> Composition feature representation 与 visualization projection 分离

以及：

> clustering operates in canonical feature space rather than visual 2D projection

这是重要长期 contract。

如果现有 ADR 未覆盖：

新增/更新 ADR。

---

# 104. TOOL_REGISTRY_NOTES

记录：

* final Tool ID
* product-level granularity
* feature representation
* supported projection
* supported clustering
* readiness requirements
* sample binding
* explicit future methods

---

# 105. Required Checks

至少：

```bash
git diff --check
uv lock --check
uv run python -m pytest -q
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
```

以及 current project：

* service-backed integration
* no-skipped assertion
* docs consistency
* TASKS/result consistency
* evidence integrity
* secret scan

只能报告：

PASS / FAIL / SKIPPED / UNAVAILABLE。

---

# 106. Implementation Commit

完成：

* implementation
* tests
* docs
* evidence
* persistent

后：

```bash
git status --short
git diff --stat
git diff --check
```

只 stage 本阶段相关文件。

禁止：

```bash
git add .
```

建议 commit：

```text
Implement composition space explorer
```

遵循 repository 实际风格。

push：

`origin master`

---

# 107. Implementation-HEAD CI

必须验证 exact implementation SHA。

至少：

* Unit Tests
* Frontend Typecheck & Build
* Service-backed Integration
* no-skipped assertion

全部 success。

否则不得 PASS。

---

# 108. Completion Record

implementation CI success 后：

创建 Phase 10K-4 completion record。

必须记录：

* composition feature representation
* projection
* PCA policy
* clustering
* property coloring
* ML error coloring
* dataset comparison
* sample linkage
* frontend
* performance
* browser
* security
* explicit limits

然后 commit。

---

# 109. Completion-Record CI

验证 completion-record exact SHA。

只有 current-head CI success：

才 archive Phase 10K-4。

---

# 110. Queue Archive

最终：

```text
Phase 10K-4:
ARCHIVED

Phase 10K-5:
NEXT / AWAITING COMPLETE PROMPT
```

不得开始 10K-5。

---

# 111. Explicit Limits

本阶段最终必须明确：

Composition Space Explorer 不等于：

* crystal-structure similarity
* physical phase classification
* scientific material-family truth
* learned material representation
* anomaly proof
* model training

必须明确：

```text
Nearby points represent similarity in the declared composition feature space.
```

而不是：

```text
Nearby points are physically similar materials.
```

---

# 112. Final Report Format

最终严格输出：

# Phase 10K-4 Composition Space / Embedding / Clustering Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10K-3 implementation:
* completion record:
* archive:
* branch:
* initial HEAD:
* origin/master:
* initial status:

## 3. Dependency / Reuse Audit

* numpy:
* scipy:
* sklearn:
* pymatviz:
* Plotly:
* UMAP:
* new dependency:
* decision:

## 4. Composition Feature Contract

* composition source:
* feature representation:
* normalization:
* element basis:
* basis ordering:
* fractional compositions:
* invalid samples:
* provenance:

## 5. Projection

* supported method:
* PCA centering:
* scaling:
* dimensions:
* sign convention:
* explained variance:
* minimum samples:
* rank-deficient behavior:

## 6. Optional Projection Methods

分别：

* UMAP:
* t-SNE:
* learned embeddings:

必须真实写：

READY / NOT_IMPLEMENTED / FUTURE。

## 7. Clustering

* implemented:
* method:
* feature space:
* seed:
* cluster count:
* deterministic labels:
* summaries:
* invalid-k handling:
* scientific boundary:

## 8. Composition Space Product

* 2D:
* 3D:
* property coloring:
* ML error coloring:
* uncertainty coloring:
* dataset/split coloring:
* sample inspection:
* duplicate compositions:

## 9. Dataset Comparison

* shared element basis:
* shared projection:
* combined/reference policy:
* chemistry coverage:
* train/test handling:
* explicit limitations:

## 10. Outlier / Similarity Boundary

* composition outlier:
* nearest composition:
* structural similarity:
* scientific invalidity:

## 11. Tool Registry

* new tool:
* reused tools:
* internal helpers:
* strict params:
* readiness:
* PlanValidator:
* fragmented tools rejected:

## 12. Runtime / API

* DataProfile:
* AnalysisPlan:
* QueueWorkerRuntime:
* structured artifact:
* plot artifact:
* API:
* typed errors:

## 13. Frontend

* Composition Space section:
* controls:
* projection:
* coloring:
* clusters:
* sample details:
* empty states:
* mobile:
* accessibility:

## 14. Artifact / Provenance

* feature basis:
* projection:
* clustering:
* sample IDs:
* selected property:
* ML binding:
* dataset binding:
* versions:

## 15. Determinism

* feature order:
* PCA sign:
* cluster label:
* sampling:
* artifact hash:

## 16. Caps

* samples:
* features:
* clusters:
* rendered points:
* artifact size:

## 17. Fixtures / Validation

* basic compositions:
* separated groups:
* identical compositions:
* invalid formula:
* property coloring:
* ML error:
* dataset A/B:
* high element diversity:

## 18. Performance

* small:
* medium:
* near-cap:
* PCA:
* clustering:
* frontend:
* artifact size:

## 19. Browser Evidence

* Chromium:
* Firefox:
* WebKit:
* mobile:
* PCA:
* clustering:
* property:
* comparison:

## 20. Security

* untrusted text:
* arbitrary code:
* external network:
* artifact JS:
* secret scan:

必须：

```text
NO_COMPOSITION_SPACE_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

或 repository 等价 marker。

## 21. Explicit Non-Scope

确认未实现：

* model training
* learned embeddings
* arbitrary notebooks
* Agent planning
* Unified Workspace
* advanced anomaly science
* structure similarity unless explicitly existing

## 22. Files Changed

按：

* backend
* registry
* frontend
* tests
* docs
* evidence
* persistent

分类。

## 23. Checks

* git diff --check:
* uv lock:
* backend:
* frontend:
* typecheck:
* build:
* service-backed:
* no-skipped:
* docs:
* TASKS:
* evidence integrity:
* security:

## 24. Commit / CI

### Implementation

* commit:
* exact SHA:
* CI:
* unit:
* frontend:
* service-backed:

### Completion Record

* commit:
* exact SHA:
* CI:

## 25. Queue State

最终：

```text
Phase 10K-4:
ARCHIVED

Phase 10K-5:
NEXT / AWAITING COMPLETE PROMPT
```

## 26. Composition Space Readiness

分别：

* canonical composition vectors:
* PCA:
* clustering:
* property coloring:
* ML coloring:
* dataset comparison:
* sample linkage:
* frontend:
* browser:
* performance:
* security:

总体：

`READY`

或：

`READY_WITH_EXPLICIT_LIMITS`

## 27. Whether Allowed to Enter Phase 10K-5

只有全部满足才写“可以”：

* 10K-3 archived
* canonical composition feature contract complete
* deterministic projection complete
* PCA validation complete
* clustering completed or explicitly approved as deferred based on dependency audit
* sample identity preserved
* property coloring complete
* ML binding complete
* dataset comparison projection correct
* runtime/API evidence complete
* frontend evidence complete
* browser/accessibility PASS
* caps/performance PASS
* scientific boundaries explicit
* no external network
* secret scan PASS
* implementation exact-head CI success
* completion-record exact-head CI success
* TASKS archived
* origin/master == HEAD
* git clean

## 28. Next Phase

只能写：

**Phase 10K-5：Material Intelligence Integration + Browser/API Evidence**

不得开始实现。

---

# 113. PASS 标准

Phase 10K-4 只有满足以下全部硬条件才能 PASS：

1. Phase 10K-3 已归档。
2. composition semantics 只来自 DataProfile/正式 resource。
3. 不重复实现 formula detection。
4. canonical composition feature representation 完成。
5. element order deterministic。
6. atomic fraction normalization 明确。
7. invalid compositions 显式处理。
8. feature representation 与 projection 分离。
9. 至少一个 deterministic projection 正式实现。
10. PCA contract 完整。
11. PCA sign convention 稳定。
12. explained variance 正确。
13. rank/insufficient-sample edge cases 正确。
14. UMAP/t-SNE 没有因 scope 压力擅自新增依赖。
15. clustering 如果实现则 algorithm contract 明确。
16. clustering 在正式 feature space 中执行。
17. random seed 固定。
18. cluster labels deterministic。
19. cluster 不被称为科学分类真值。
20. property coloring 使用 DataProfile property semantics。
21. ML error coloring复用正式 10K-3 artifact。
22. sample binding 不使用数组位置猜测。
23. duplicate compositions 不被误写为 duplicate structures。
24. composition proximity 不被称为结构相似。
25. dataset comparison 使用共同 feature basis。
26. comparison 不对两边分别 PCA 后直接叠图。
27. product-level Tool granularity。
28. 不创建 vectorize/PCA/chart 等碎 Tool。
29. backend 是 scientific calculation authority。
30. frontend 不独立计算正式 PCA/clustering。
31. deterministic artifacts。
32. provenance 完整。
33. caps 明确。
34. frontend Composition Space Explorer 完成。
35. accessible non-chart representation 完成。
36. API/runtime evidence PASS。
37. browser evidence PASS。
38. mobile PASS。
39. performance PASS。
40. no external network。
41. no arbitrary code。
42. secret scan PASS。
43. 默认无新 dependency。
44. 不实现 Phase 10L。
45. 不实现 Phase 10M。
46. regression suite PASS。
47. implementation exact-SHA CI success。
48. completion-record exact-SHA CI success。
49. 10K-4 archived。
50. 10K-5 remains NEXT。
51. origin/master == HEAD。
52. git clean。

---

现在开始。

第一步：

**不要先写代码。**

先完成：

# Phase 10K-4 Entry / Composition Space Product Audit

基于真实 10K-0～10K-3 implementation 回答：

1. 当前 composition canonical representation 是什么？
2. stable sample identity 是什么？
3. dataset comparison identity 如何表达？
4. ML error/uncertainty 如何与 samples 绑定？
5. 当前已安装哪些 projection/clustering dependencies？
6. pymatviz 当前能复用什么？
7. element-fraction feature 是否足够作为第一版 canonical composition representation？
8. PCA 最合理的 implementation/provider 是什么？
9. PCA scaling policy 应是什么？
10. PCA sign determinism 如何解决？
11. clustering 是否可以在不增加 dependency 的情况下正式实现？
12. 第一版 clustering method 是什么？
13. UMAP 是否本阶段实现，还是明确 Future？
14. composition-space artifact 应包含什么？
15. product-level Tool 应是什么粒度？
16. frontend 最小产品应该是什么？
17. dataset A/B 或 train/test 如何在共同 projection 中比较？
18. 哪些 outlier/similarity claims 必须禁止？
19. 哪些功能明确留到 Future？
20. 本阶段 exact implementation scope 是什么？

Audit 完成后直接继续 implementation。

不要等待人工确认。

本轮最终停在：

**Phase 10K-5：Material Intelligence Integration + Browser/API Evidence = NEXT / AWAITING COMPLETE PROMPT**

---END---

---TASK---
 状态：待处理
你现在执行：

# Phase 10K-5：Material Intelligence Integration + Browser/API Evidence

这是 Phase 10K Material Intelligence Layer 的最终集成与证据闭环阶段。

本阶段**原则上不新增新的材料分析算法**。

目标是：

> 将 Phase 10K-1 ～ Phase 10K-4 已经完成的 DataProfile 2.0、Dataset Materials Explorer、Materials ML Evaluation、Composition Space / Embedding / Clustering 组合成一个真实、连续、可验证的 Material Intelligence 产品层。

最终必须证明：

```text
Materials Dataset
      ↓
Material Data Profile 2.0
      ↓
Dataset Overview / Composition / Structure / Properties / Quality
      ↓
Materials ML Evaluation（数据满足时）
      ↓
Composition Space（数据满足时）
      ↓
Structured Artifacts
      ↓
Frontend Product
      ↓
Report / Recipe Compatibility
```

并且整个链路保持：

* stable sample identity
* dataset/resource identity
* deterministic semantics
* consistent units
* provenance
* typed partial states
* browser/API consistency
* security
* bounded performance

本阶段完成后：

**Phase 10K Material Intelligence Layer 应正式 CLOSED。**

下一阶段才是：

**Phase 10L-0：Agent / Planner Capability Audit**

---

# 0. Hard Entry Gate

首先检查真实仓库。

必须确认：

```text
Phase 10J-6 = ARCHIVED
Gate J6-R = PASS

Phase 10K-0 = ARCHIVED
Phase 10K-1 = ARCHIVED
Phase 10K-2 = ARCHIVED
Phase 10K-3 = ARCHIVED
Phase 10K-4 = ARCHIVED

Phase 10K-5 = NEXT
```

必须读取 Phase 10K-4 的真实：

* result
* implementation record
* composition feature contract
* projection/clustering contract
* sample binding
* artifact schema
* frontend product
* browser evidence
* completion record
* next-scope document

同时必须确认：

* Phase 10K-1 DataProfile 2.0 completion
* Phase 10K-2 Dataset Explorer completion
* Phase 10K-3 Materials ML completion
* Phase 10K-4 Composition Space completion

如果任何前置 Phase 未真正 ARCHIVED：

输出：

`BLOCKED_BY_PREVIOUS_PHASE_10K`

然后停止。

不得通过跳过前置 closure 来执行 10K-5。

---

# 1. Canonical Phase 10K Definition

Phase 10K：

# Material Intelligence Layer

其完整组成是：

```text
10K-1
Material Data Profile 2.0

10K-2
Dataset Materials Explorer

10K-3
Materials ML Evaluation

10K-4
Composition Space / Embedding / Clustering

10K-5
Material Intelligence Integration + Browser/API Evidence
```

Phase 10K-5 的职责：

**integration / product closure / evidence**

而不是继续增加分析功能。

---

# 2. Explicit Non-Scope

本阶段禁止主动新增：

## New Dataset Algorithms

* 新的统计分析 family
* 新 anomaly algorithm
* 新 duplicate similarity algorithm
* 新 descriptor family

## New ML Algorithms

* 新 regression metric family
* SHAP
* feature importance
* model training
* AutoML

## New Embeddings

* UMAP，如果 10K-4 未实现
* t-SNE
* learned embedding
* foundation-model embedding

## Phase 10L

* capability-aware Planner
* multi-tool automatic planning
* LLM result interpretation
* automatic next-step recommendation
* multi-step Agent behavior

## Phase 10M

* global Unified Workspace redesign

## Phase 10N

* CrystalNN
* VoronoiNN
* Experimental XRD
* MSD/diffusion
* Electronic Band/DOS

## Future

* Fermi Surface
* Rietveld
* Bader
* notebook execution

---

# 3. Allowed Changes

本阶段允许：

* integration fixes
* schema compatibility fixes
* sample identity fixes
* artifact linkage fixes
* DataProfile → product availability integration
* frontend product composition
* API consistency fixes
* typed partial-state fixes
* browser bugs
* accessibility fixes
* performance fixes
* bounded lazy rendering
* report/recipe compatibility
* provenance fixes
* test/evidence expansion
* docs/persistent
* CI closure

如果发现新算法缺失：

不要顺手实现。

记录：

`DEFERRED_TO_APPROPRIATE_PHASE`

---

# 4. Baseline Verification

进入：

```text
E:\1project\Material Data Intelligence
```

运行：

```bash
git status --short
git branch --show-current
git rev-parse HEAD
git rev-parse origin/master
git log --oneline -35
git diff --stat
git diff --check
```

记录：

* branch
* initial HEAD
* origin/master
* status
* 10K-1 archive commit
* 10K-2 archive commit
* 10K-3 archive commit
* 10K-4 archive commit
* latest exact-head CI

必须使用真实值。

---

# 5. Queue Transition

只有 Entry Gate PASS 后：

将：

`Phase 10K-5：Material Intelligence Integration + Browser/API Evidence`

设为唯一 active task。

更新：

* `TASKS.md`
* `persistent/TASK_BOARD.md`

不得同时把：

* 10L-0
* 10L-1

设为 IN_PROGRESS。

---

# 6. 必读前序 Contract

完整读取：

## 10K-1

重点：

* DataProfile schema
* semantic roles
* analysis readiness
* ambiguity
* sample/resource identity
* version binding

## 10K-2

重点：

* Dataset Explorer architecture
* dataset summary
* composition
* structure stats
* properties
* quality
* comparison
* sample linkage

## 10K-3

重点：

* regression
* uncertainty
* classification
* chemistry-conditioned error
* model comparison
* ML artifacts

## 10K-4

重点：

* composition feature space
* PCA
* clustering
* property coloring
* ML error coloring
* dataset comparison projection
* composition-space artifacts

---

# 7. Pre-Implementation Integration Audit

修改代码前必须输出：

# Phase 10K-5 Material Intelligence Integration Audit

必须回答：

## DataProfile

* profile version:
* semantic roles:
* readiness:
* sample identity:
* resource version binding:

## Dataset Explorer

* overview:
* composition:
* structure:
* properties:
* quality:
* comparison:

## ML

* regression:
* uncertainty:
* classification:
* model comparison:
* chemistry-conditioned error:

## Composition Space

* feature representation:
* projection:
* clustering:
* property coloring:
* ML coloring:
* comparison:

## Integration

逐项回答：

1. 是否共享同一个 dataset identity？
2. 是否共享同一个 stable sample identity？
3. formula/composition 是否只有一个 semantic authority？
4. property identity 是否统一？
5. ML artifacts 是否能回指 dataset samples？
6. Composition Space 是否能消费正式 ML artifacts？
7. Dataset Explorer 是否能正确发现 ML/Composition Space availability？
8. API 是否使用一致 resource/version identity？
9. Frontend 是否存在重复计算？
10. 是否存在 frontend-only scientific truth？
11. Report/Recipe 能否引用全部 10K artifacts？
12. 是否存在 stale profile/artifact reuse 风险？
13. partial dataset coverage 是否被正确披露？
14. browser 是否存在不同模块行为不一致？

Audit 完成后直接修复 integration gaps。

不要等待人工确认。

---

# 8. Material Intelligence Product Contract

本阶段必须正式冻结 Phase 10K 的高层产品 contract。

一个材料 dataset 可以拥有：

```text
Dataset
│
├─ Profile
│
├─ Overview
│
├─ Composition
│
├─ Structure Statistics
│
├─ Properties
│
├─ Data Quality
│
├─ Comparison
│
├─ Model Evaluation
│
└─ Composition Space
```

但：

**只有数据满足条件的能力才 READY。**

不得显示假 capability。

---

# 9. Capability Availability

Frontend/product availability 必须来自：

```text
DataProfile semantics/readiness
+
actual platform capabilities
```

不能：

* 根据 column name 临时判断
* 根据 tab 是否存在猜
* 根据 artifact 是否碰巧出现猜

---

# 10. Data-Ready vs Platform-Ready

继续保持 10K-1 的严格区别。

例如：

dataset 有：

```text
target + prediction
```

则：

```text
regression_data_readiness = READY
```

但只有 10K-3 tool 真正存在时：

```text
regression_platform_capability = READY
```

本阶段必须检查这套逻辑已经真正贯穿 UI/API。

---

# 11. Single Semantic Authority

本阶段必须证明：

## Formula

只有 DataProfile/canonical composition layer 是 authority。

## Material Property

只有 DataProfile semantic roles 是 authority。

## Regression Task

只有 10K-1 semantic groups 是 authority。

## Sample Identity

只有 canonical resource/sample identity 是 authority。

不得在 10K-2/3/4 frontend 再各自重复推断。

---

# 12. Sample Identity End-to-End Test

这是本阶段最高优先级证据之一。

必须验证同一个 sample：

可以从：

```text
Dataset Explorer table
```

定位到：

```text
ML high-error sample
```

以及：

```text
Composition Space point
```

并确认 identity 一致。

不要求实现 Phase 10M 的全局 cross-panel selection。

但底层 identity 必须完全一致。

---

# 13. No Index-Based Accidental Binding

必须专门测试：

* sorted dataset table
* filtered dataset
* ML artifact sorting
* PCA coordinate order

即使这些顺序不同：

sample binding 仍然正确。

不得使用：

```text
array[17] ↔ array[17]
```

作为跨 artifact identity。

---

# 14. Resource Version Binding

必须验证：

dataset version A

生成：

profile/artifacts A。

如果 dataset 变成 version B：

不能错误复用：

* profile A
* ML artifact A
* Composition Space artifact A

除非现有 cache key明确包含 resource version/hash。

---

# 15. Stale Artifact Protection

如果存在 stale artifact risk：

本阶段必须修复。

至少通过：

* resource ID
* resource version/hash
* params hash
* profile version

进行有效绑定。

不要建立第二套 cache framework。

---

# 16. Partial Coverage

材料 dataset 很可能是：

```text
1000 samples
900 valid formulas
700 structures
600 predictions
```

系统必须同时表达：

* total dataset size
* composition coverage
* structure coverage
* ML coverage
* Composition Space coverage

不能让用户误以为：

某个图代表全部 1000 samples。

---

# 17. Coverage Disclosure

每个 product artifact 至少明确：

* total samples
* eligible samples
* evaluated samples
* excluded samples
* reason

根据产品不同使用相应字段。

---

# 18. Cross-Product Unit Consistency

例如：

`formation_energy`

在：

* Dataset Explorer
* ML target
* Composition Space coloring

必须使用同一个 unit semantics。

不能：

Dataset Explorer 显示 eV/atom

ML 显示 eV

如果来源其实相同。

---

# 19. Unknown Units

如果 unit unknown：

所有相关产品都应该一致显示：

`unit unavailable`

不能一个页面猜 unit、另一个不猜。

---

# 20. Cross-Product Property Identity

如果用户选择：

`band_gap`

用于：

* property distribution
* Composition Space coloring

必须绑定同一个 semantic property。

不得只根据显示 label。

---

# 21. Dataset Comparison Integration

10K-2 和 10K-4 都涉及 dataset comparison。

必须检查：

## Dataset Explorer comparison

统计 A/B 的：

* composition coverage
* property distribution
* structure coverage

## Composition Space comparison

在共同 feature/projection 中比较 A/B。

两者必须使用同一个：

* dataset identity
* split identity
* group policy

---

# 22. ML + Composition Space Integration

10K-4 如果支持：

* absolute error coloring
* residual coloring
* uncertainty coloring

必须消费：

10K-3 正式 artifact。

不得在 Composition Space frontend：

重新从 y_true/y_pred 计算。

---

# 23. Dataset Explorer + ML Integration

Dataset Explorer 的 Model Evaluation section：

必须只在：

DataProfile + actual ML platform capability

都满足时显示。

如果数据有 target/prediction，但 semantic binding ambiguous：

必须：

`AMBIGUOUS`

而不是自动选第一组。

---

# 24. Multiple ML Tasks

如果 dataset 同时有：

* energy task
* band-gap task

Frontend 必须允许明确选择 task。

不能将两个 metrics 混在一起。

Composition Space 的 ML coloring 同样必须绑定 selected task/model。

---

# 25. Multiple Models

如果同一个 target 有：

* model A
* model B

ML UI 和 Composition Space 都必须使用明确 model identity。

不得让 Composition Space 的：

`error`

含义不明确。

应该是：

```text
absolute_error:model_A
```

或 equivalent structured binding。

---

# 26. Classification Integration

如果 dataset 是 classification：

Composition Space 可按：

* true class
* predicted class
* correct/incorrect

着色，只有当 current 10K-4 contract 已支持 categorical binding 时才允许。

如果未实现：

不要为了 10K-5新增。

记录未来可扩展。

---

# 27. No New Scientific Calculation in Frontend

完整审计：

* metrics
* distributions
* PCA
* clustering
* chemistry groups

Frontend 不得有第二份正式 scientific calculation。

允许：

* formatting
* sorting
* filtering presentation
* display-only transformations

---

# 28. Artifact Authority

正式科学结果必须来自：

QueueWorkerRuntime produced artifacts。

Frontend fixtures 只能用于 component unit tests。

Browser product evidence：

必须使用真实 runtime artifacts。

---

# 29. Artifact Relationships

本阶段应确保可以追踪：

```text
Dataset
↓
Profile
↓
Analysis Tool
↓
Artifact
```

以及 dependent products：

```text
ML Evaluation Artifact
↓
Composition Space Coloring
```

如果当前 artifact metadata 已有 parent/source refs：

复用。

---

# 30. Artifact Bundle Productization

不要为 Phase 10K 创建一个巨大：

`material_intelligence_everything.v1`

把所有结果硬塞进去。

更合理：

保留独立 product artifacts，

由 Dataset Explorer / product layer组织。

这样才能：

* lazy load
* partial failure
* rerun one analysis
* preserve provenance

---

# 31. Partial Failure Isolation

如果：

Composition Space 失败，

不能让：

Dataset Overview

也消失。

如果：

ML unavailable，

Composition/Properties 仍然应工作。

这是本阶段必须验证的 integration property。

---

# 32. Error State Taxonomy

至少区分：

* data unavailable
* ambiguous semantics
* tool unavailable
* execution failed
* partial coverage
* cap exceeded

Frontend 不应该统一显示：

`Something went wrong`

---

# 33. No Capability Spam

Dataset Explorer 不应该默认一次运行：

所有 10K tools。

Phase 10K-5 仍然不是 Agent。

产品应支持：

* capability discovery
* user-selected analysis
* existing one-tool Planner routes

自动组合留给 10L。

---

# 34. Existing Planner Boundary

本阶段只能确保现有工具：

可以被 Planner reach。

不得实现：

```text
“analyze this dataset”
→ 自动跑 Dataset Explorer + ML + PCA
```

这正是 Phase 10L 的工作。

---

# 35. Product Navigation

本阶段可以在现有 dataset/product surface 中合理组织：

```text
Overview
Composition
Structure
Properties
Model Evaluation
Composition Space
Quality
Comparison
```

但不要提前做 Phase 10M Unified Workspace。

---

# 36. Phase 10M Boundary

10K-5 只完成：

**dataset/material-intelligence product surface。**

10M 才统一：

* Structure
* Trajectory
* Phonon
* BZ
* Volumetric
* Material Intelligence
* Reports

不要现在重写整个 PlannerWorkbench。

---

# 37. Frontend Integration Goal

用户选中一个 materials dataset 时：

应能够理解：

### What data is here?

Profile / Overview

### What chemistry is covered?

Composition

### What structural metadata exists?

Structure

### What properties exist?

Properties

### Are there data-quality issues?

Quality

### Is this a model-result dataset?

Model Evaluation

### How is composition space covered?

Composition Space

### How does another dataset/split compare?

Comparison

---

# 38. Capability-Driven Rendering

如果没有 structures：

不显示空 Structure charts。

应显示：

`Structure metadata unavailable`

或隐藏，并保留 availability explanation。

如果没有 ML：

Model Evaluation 不能显示误导性空 dashboard。

---

# 39. Consistent Empty States

建立统一风格：

* NOT_APPLICABLE
* MISSING_DATA
* AMBIGUOUS
* NOT_IMPLEMENTED
* FAILED

使用项目已有状态语言。

不要每个 component 自己写一套文案。

---

# 40. Frontend Performance

Phase 10K 产品已经包含很多 sections。

必须避免：

页面加载时一次初始化：

* every Plotly chart
* PCA scatter
* all property histograms
* ML charts

应评估：

* lazy render
* selected property
* conditional section
* bounded table

---

# 41. Frontend Bundle

不得为了本阶段添加大依赖。

检查：

build bundle

是否出现明显异常增长。

记录：

* current `/` first-load JS
* relevant route/page bundle if available

但没有明确 regression 就不要开启独立 optimization project。

---

# 42. API Product Surface

检查所有 Phase 10K artifacts 能否通过现有 API：

* discover
* fetch
* render
* associate with job/resource

不要建立专用 `/material-intelligence-everything` endpoint。

优先复用现有 resource/artifact/job APIs。

---

# 43. API Consistency

同一 artifact：

API 返回的：

* resource ID
* sample IDs
* units
* tool
* params
* version

必须与 frontend展示一致。

---

# 44. Real End-to-End Evidence

本阶段核心证据必须是真实：

```text
Mock Planner / approved deterministic path
→ /planner/jobs
→ persisted AnalysisPlan
→ QueueWorkerRuntime
→ Tool Adapter
→ Artifact
→ API retrieval
→ browser
```

不能：

直接调用 helper

然后称 E2E。

---

# 45. Required End-to-End Case A — Materials Dataset

准备一个真实 deterministic materials dataset。

至少包含：

* formula
* numeric material properties
* multiple chemical systems
* valid/invalid/missing cases

验证：

* Profile 2.0
* Dataset Overview
* Composition
* Properties
* Data Quality

---

# 46. Required Case B — Structure-Enriched Dataset

包含：

* table/sample identity
* bound structure metadata

验证：

* structure coverage
* site-count/density/volume/lattice stats
* partial coverage

如果 current project dataset→structure binding有明确 fixture：

复用。

---

# 47. Required Case C — Regression Dataset

包含：

* formula
* target
* prediction
* multiple chemistry groups

验证：

* Profile semantics
* Dataset Explorer
* ML Regression
* high-error sample linkage
* error-by-chemistry
* Composition Space error coloring if 10K-4 supports

---

# 48. Required Case D — Regression + Uncertainty

验证：

* uncertainty readiness
* ML uncertainty product
* high-uncertainty sample identity
* Composition Space uncertainty/error binding where supported

---

# 49. Required Case E — Classification

验证：

* classification semantics
* confusion/metrics
* classification frontend
* conditional ROC/PR behavior

不需要强行要求 Composition Space classification coloring。

---

# 50. Required Case F — Dataset Comparison

两个明确 datasets/groups。

验证：

* Dataset Explorer comparison
* chemistry overlap
* property comparison
* Composition Space shared projection

---

# 51. Required Case G — Partial Capability Dataset

例如：

只有：

```text
formula + property
```

没有：

* prediction
* structure

验证：

* Dataset Explorer works
* ML is correctly unavailable
* Composition Space works if enough compositions
* no blank/failure cascade

---

# 52. Required Case H — Ambiguous ML Semantics

例如存在多个无法安全配对的 prediction candidates。

验证：

* profile marks ambiguity
* Dataset Explorer still works
* ML does not silently choose one
* frontend explains ambiguity

---

# 53. Cross-Artifact Identity Evidence

必须专门输出 machine-readable evidence：

对至少一个 sample：

记录其 identity 在：

* source dataset
* Dataset Explorer
* ML artifact
* Composition Space artifact

完全一致。

建议 marker：

`MATERIAL_INTELLIGENCE_SAMPLE_IDENTITY_EVIDENCE_PASS`

---

# 54. Cross-Artifact Version Evidence

必须证明：

artifact source version 与 dataset version 匹配。

建议 marker：

`MATERIAL_INTELLIGENCE_VERSION_BINDING_EVIDENCE_PASS`

---

# 55. DataProfile Integration Evidence

证明：

10K-2/3/4 没有各自重新做 semantic detection。

可以通过：

* tests
* code path
* contract evidence

记录 marker：

`MATERIAL_INTELLIGENCE_PROFILE_AUTHORITY_EVIDENCE_PASS`

---

# 56. Partial Failure Evidence

设计一个合法失败场景。

例如：

Composition Space：

insufficient samples

但 Dataset Overview 仍正常。

证明：

`MATERIAL_INTELLIGENCE_PARTIAL_FAILURE_ISOLATION_PASS`

---

# 57. Report Compatibility

本阶段必须验证现有 Report/Artifact flow 可以至少引用：

* Dataset summary
* property figures
* ML metrics
* Composition Space figure

不要求重做完整 Report UI。

---

# 58. Recipe Compatibility

至少一个 E2E case 的 Recipe 应能记录：

* dataset/resource
* selected tool
* semantic task
* params
* artifact refs

重跑同 recipe：

结果 deterministic。

如果 current Recipe system 已有 hash/replay test：

扩展相关 fixture。

---

# 59. Reproducibility Evidence

至少证明：

同一个：

dataset + profile + tool params

重复执行：

关键 structured results 相同。

可生成：

`MATERIAL_INTELLIGENCE_REPRODUCIBILITY_PASS`

---

# 60. Browser Evidence Matrix

按 current browser policy：

至少：

* Chromium
* Firefox
* WebKit

并至少一个 mobile viewport。

需要验证的产品面：

* Profile
* Dataset Overview
* Properties
* Data Quality
* Model Evaluation
* Composition Space
* Comparison

不是每个 browser 都必须重新截图所有组合，但至少所有主要功能必须有真实覆盖矩阵。

---

# 61. Browser Evidence Must Use Runtime Artifacts

不得：

component fixture only

然后宣称 Browser E2E PASS。

关键 case 必须来自：

真实 persisted job/artifact。

---

# 62. Accessibility

必须验证：

## Profile

状态文字可读。

## Tables

headers/labels 正确。

## Property selector

keyboard usable。

## ML

metrics 有文本。

## Confusion Matrix

numeric alternative。

## Composition Space

sample/cluster summary table。

## Warnings

不依赖颜色。

---

# 63. Mobile

至少验证：

* Dataset Overview
* Model Evaluation
* Composition Space

在当前 mobile viewport 中：

* no catastrophic overflow
* controls usable
* chart readable
* sample detail readable

---

# 64. Performance Closure

Phase 10K-5 需要形成 Material Intelligence 的整体性能边界。

至少测试：

## Small

几十 samples。

## Medium

现实中等 dataset。

## Near Cap

接近 Phase 10K 已批准的 dataset size。

记录：

* profile duration
* dataset summary duration
* ML duration
* composition-space duration
* total artifact size
* frontend render sanity

---

# 65. 不需要“所有分析一次跑完”的性能数字

因为 10L 尚未实现自动 multi-tool plan。

可以分别测试各 capability。

但需要给一个：

**Material Intelligence product performance envelope**

说明典型使用时的上界。

---

# 66. Memory

特别检查：

* large Plotly point arrays
* composition coordinates
* ML sample tables
* duplicate full dataset copies

避免 frontend/Artifact 重复存储整个 source dataset。

---

# 67. Artifact Size

structured artifacts 不应把完整 dataset 每次复制进去。

应优先保存：

* sample refs
* derived values
* bounded tables
* summaries

如果当前 artifact 出现巨大重复 payload：

本阶段允许修复。

---

# 68. Security

所有 Phase 10K surfaces 继续视用户输入为 untrusted：

* formulas
* property names
* model names
* class labels
* sample IDs
* dataset names

禁止：

* raw HTML
* artifact JS
* arbitrary URL
* arbitrary script

---

# 69. No External Network

Material Intelligence Layer 不需要外部网络。

必须证明：

```text
NO_MATERIAL_INTELLIGENCE_EXTERNAL_NETWORK_REQUESTS
```

或 repository 等价 marker。

---

# 70. Secret Scan

必须：

```text
NO_SECRET_PATTERN_HITS
```

---

# 71. No New Dependency by Default

Phase 10K-5 是 integration phase。

原则：

**不得新增 dependency。**

如果 integration 竟然要求新 dependency：

停止并报告：

`REVIEWER_DECISION_REQUIRED`

通常说明前面 architecture 有问题。

---

# 72. No New Public Tool by Default

Phase 10K-5 原则：

**不新增新 scientific Tool ID。**

如果前序 product 因 integration 缺一个必要 aggregator：

先判断是否只是 frontend/product composition。

不要为了：

“run all intelligence”

创建：

`material_intelligence.all`

因为 10L 即将负责智能 planning。

---

# 73. 禁止创建“Run Everything” Tool

不要注册：

```text
dataset.full_analysis
material_intelligence.full_analysis
```

来一次运行 10K-2/3/4。

这会把 Agent planning 提前硬编码进 Tool。

10L 应根据用户目标选择工具。

---

# 74. Planner Regression

必须证明：

Phase 10K-5 没有偷偷让现有 Planner：

从一句：

“analyze dataset”

自动调用多个 10K tools。

这留给 10L。

---

# 75. Tool Registry Closure

形成 Phase 10K final Tool inventory。

至少列出：

## Existing Before 10K

table/composition/general tools。

## Added During 10K-2

dataset product tools。

## Added During 10K-3

ML product tools。

## Added During 10K-4

composition-space tool。

对每个：

* Tool ID
* semantics
* DataProfile requirements
* artifact output
* status

---

# 76. Capability Status Matrix Closure

更新 canonical Capability Status Matrix。

Phase 10K 完成时应如实体现：

## READY / READY_WITH_LIMITS

* Material Data Profile 2.0
* Dataset Overview
* Composition Explorer
* Structure Dataset Statistics
* Property Explorer
* Data Quality
* Dataset Comparison
* Regression Evaluation
* Chemistry-Conditioned Error
* Uncertainty Evaluation
* Classification Evaluation
* Model Comparison
* Composition Feature Space
* PCA
* approved clustering
* Property Coloring
* ML Error Coloring
* Composition-Space Dataset Comparison

具体依据真实 10K-1～4结果。

---

# 77. 不得模糊 Optional Capabilities

例如 10K-4 未实现 UMAP：

必须继续：

`FUTURE`

不得因为 Composition Space overall READY 而写：

“Embeddings READY”。

---

# 78. Documentation Closure

建议新增：

```text
docs/phase10k/
  phase10k5_material_intelligence_integration.md
  phase10k5_end_to_end_evidence_matrix.md
  phase10k5_cross_artifact_identity_evidence.md
  phase10k5_performance_security_closure.md
  phase10k_completion_summary.md
  phase10l0_next_scope.md
```

如果内容高度重复：

可以合并。

不要创建空壳文件。

---

# 79. Phase 10K Completion Summary

必须有一份正式总结说明：

# What Material Intelligence Now Means

至少回答：

* 数据如何被识别？
* dataset 如何被探索？
* model results 如何被评估？
* composition space 如何被探索？
* 哪些能力是 deterministic？
* Agent 尚未做什么？
* 还剩什么进入 10L？

---

# 80. Explicit Phase 10K Limits

必须写明：

Phase 10K 不包含：

* automatic analysis planning
* automatic tool combination
* LLM scientific interpretation
* global Unified Workspace
* CrystalNN/VoronoiNN
* Experimental XRD
* trajectory MSD/diffusion
* Electronic Band/DOS

这些不是 10K failure。

它们属于后续 roadmap。

---

# 81. Persistent Updates

更新：

```text
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/TOOL_REGISTRY_NOTES.md
```

必要时：

`persistent/ARCHITECTURE_DECISIONS.md`

---

# 82. DESIGN_PROGRESS

记录：

```text
Phase 10K Material Intelligence Layer = COMPLETE
```

前提：

10K-5 最终 PASS。

并列出：

* Profile
* Explorer
* ML
* Composition Space
* E2E integration

---

# 83. TASK_BOARD

执行期间：

```text
10K-5 = IN_PROGRESS
```

完成、归档后：

```text
Phase 10K = COMPLETE

10L-0 = NEXT
```

不得：

`10L-0 = IN_PROGRESS`

---

# 84. OPEN_QUESTIONS

关闭 Phase 10K 已解决的问题。

例如：

* semantic roles
* sample identity
* dataset statistics
* ML metrics
* PCA
* clustering baseline

仍属于：

10L：

* Planner capability representation
* multi-tool plan selection
* result interpretation

移到 active next-phase questions。

---

# 85. TOOL_REGISTRY_NOTES

写入：

**Phase 10K final capability surface**

并明确：

这些 tools 是：

Agent future planning vocabulary

而不是让用户记住所有 Tool ID。

---

# 86. Architecture Decision

如果 10K integration 最终确认：

> DataProfile = deterministic data truth
> Tools = deterministic analysis capability
> Planner = future selection layer

且现有 ADR 尚未完整记录：

更新 ADR。

这是进入 10L 前的重要 architecture boundary。

---

# 87. Phase 10K Product Evidence Cases

最终至少形成以下 evidence matrix：

| Case                | Profile | Dataset | ML                    | Composition Space | API  | Browser |
| ------------------- | ------- | ------- | --------------------- | ----------------- | ---- | ------- |
| Materials table     | PASS    | PASS    | N/A                   | PASS              | PASS | PASS    |
| Structure enriched  | PASS    | PASS    | N/A                   | applicable        | PASS | PASS    |
| Regression          | PASS    | PASS    | PASS                  | PASS              | PASS | PASS    |
| Uncertainty         | PASS    | PASS    | PASS                  | PASS              | PASS | PASS    |
| Classification      | PASS    | PASS    | PASS                  | as supported      | PASS | PASS    |
| Comparison          | PASS    | PASS    | as applicable         | PASS              | PASS | PASS    |
| Partial capability  | PASS    | PASS    | unavailable correctly | conditional       | PASS | PASS    |
| Ambiguous semantics | PASS    | PASS    | safely blocked        | conditional       | PASS | PASS    |

不得因为 N/A 而写 PASS。

---

# 88. Evidence Markers

使用 repository current style。

建议语义至少包括：

```text
MATERIAL_INTELLIGENCE_RUNTIME_INTEGRATION_PASS
MATERIAL_INTELLIGENCE_API_INTEGRATION_PASS
MATERIAL_INTELLIGENCE_BROWSER_INTEGRATION_PASS
MATERIAL_INTELLIGENCE_PROFILE_AUTHORITY_EVIDENCE_PASS
MATERIAL_INTELLIGENCE_SAMPLE_IDENTITY_EVIDENCE_PASS
MATERIAL_INTELLIGENCE_VERSION_BINDING_EVIDENCE_PASS
MATERIAL_INTELLIGENCE_PARTIAL_FAILURE_ISOLATION_PASS
MATERIAL_INTELLIGENCE_REPRODUCIBILITY_PASS
MATERIAL_INTELLIGENCE_PERFORMANCE_EVIDENCE_PASS
MATERIAL_INTELLIGENCE_ACCESSIBILITY_EVIDENCE_PASS
NO_MATERIAL_INTELLIGENCE_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

实际名称遵循现有 marker convention。

---

# 89. Browser Evidence Screens

截图/证据应重点证明：

* Dataset Overview
* ML Evaluation
* Composition Space
* partial/unavailable state
* mobile

不需要为每一个小 histogram 单独截图。

重点是：

产品完整性。

---

# 90. Regression Suite

必须确保 Phase 10K integration 没有破坏：

* Phase 1–9
* Phase 10A–E
* structure viewer
* trajectory
* phonon
* BZ
* volumetric
* DataProfile
* general visualization
* Planner
* QueueWorkerRuntime

---

# 91. Required Checks

至少：

```bash
git diff --check
uv lock --check
uv run python -m pytest -q
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
```

以及 current repository：

* service-backed integration
* no-skipped assertion
* docs consistency
* TASKS/result consistency
* Phase 10 evidence integrity
* secret scan

所有状态只能：

* PASS
* FAIL
* SKIPPED
* UNAVAILABLE

---

# 92. Service-Backed Evidence

现有项目使用：

* PostgreSQL
* Redis
* MinIO

它们在此阶段的作用仅是：

**真实持久化/队列/对象存储 integration evidence。**

不要扩展成 production/deployment project。

---

# 93. Implementation Commit

完成 integration fixes、tests、evidence、docs、persistent 后：

```bash
git status --short
git diff --stat
git diff --check
```

只 stage 本阶段文件。

禁止：

```bash
git add .
```

建议 commit：

```text
Integrate material intelligence product layer
```

实际遵循 repository style。

push：

`origin master`

---

# 94. Implementation-HEAD CI

验证 exact implementation SHA。

至少：

* Unit Tests
* Frontend Typecheck & Build
* Service-backed Integration
* no-skipped assertion

全部 success。

---

# 95. Phase 10K-5 Completion Record

implementation CI success 后：

写 Phase 10K-5 result。

必须记录：

* integration findings
* fixes
* sample identity
* version binding
* DataProfile authority
* product availability
* frontend
* API
* browser
* performance
* accessibility
* security
* Phase 10K limits

然后提交 completion record。

---

# 96. Completion-Record CI

completion-record exact SHA 必须再次 current-head CI。

只有 success：

才能 archive。

---

# 97. Queue Archive

最终：

```text
Phase 10K-5:
ARCHIVED

Phase 10K:
COMPLETE

Phase 10L-0:
NEXT / AWAITING COMPLETE PROMPT
```

不得开始 10L-0。

---

# 98. Phase 10K Final Readiness

Phase 10K 完成时必须分别给出：

## Data Understanding

* DataProfile 2.0:
* semantic roles:
* analysis readiness:
* ambiguity:

## Dataset Intelligence

* overview:
* composition:
* structure statistics:
* properties:
* quality:
* comparison:

## Materials ML

* regression:
* uncertainty:
* classification:
* chemistry-conditioned error:
* model comparison:

## Composition Intelligence

* feature representation:
* PCA:
* clustering:
* property coloring:
* ML coloring:
* comparison:

## Product Integration

* sample identity:
* resource version:
* artifacts:
* API:
* frontend:
* report/recipe:
* browser:
* accessibility:
* performance:
* security:

总体只能：

`READY`

或：

`READY_WITH_EXPLICIT_LIMITS`

---

# 99. Final Report Format

最终严格输出：

# Phase 10K-5 Material Intelligence Integration + Browser/API Evidence Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10K-4 implementation:
* completion record:
* archive:
* branch:
* initial HEAD:
* origin/master:
* initial status:

## 3. Phase 10K Component Status

### 10K-1

* Profile:
* semantics:
* readiness:

### 10K-2

* Dataset Explorer:

### 10K-3

* Materials ML:

### 10K-4

* Composition Space:

## 4. Integration Architecture

* dataset identity:
* version binding:
* sample identity:
* semantic authority:
* artifact relationships:
* frontend organization:

## 5. Cross-Artifact Identity

* Dataset Explorer:
* ML:
* Composition Space:
* sorted/filtered tests:
* result:

## 6. Version / Cache Binding

* dataset version:
* profile:
* artifacts:
* stale protection:
* result:

## 7. Capability Availability

* DataProfile readiness:
* actual Tool availability:
* frontend capability gating:
* ambiguous semantics:
* partial data:

## 8. Dataset Product

* Overview:
* Composition:
* Structure:
* Properties:
* Quality:
* Comparison:

## 9. ML Integration

* regression:
* uncertainty:
* classification:
* multiple models:
* chemistry:
* task identity:

## 10. Composition Space Integration

* composition semantics:
* property binding:
* ML binding:
* comparison:
* sample inspection:

## 11. API

* job:
* plan:
* runtime:
* artifacts:
* retrieval:
* version/provenance:

## 12. Frontend

* Profile:
* Dataset Overview:
* Properties:
* Data Quality:
* ML:
* Composition Space:
* Comparison:
* partial states:
* error isolation:

## 13. Report / Recipe

* artifact inclusion:
* provenance:
* recipe:
* deterministic rerun:

## 14. Evidence Cases

逐项：

* materials table
* structure-enriched
* regression
* uncertainty
* classification
* comparison
* partial capability
* ambiguous semantics

只能写：

PASS / N/A / FAILED

不得把 N/A 当 PASS。

## 15. Cross-Product Consistency

* units:
* property identity:
* sample identity:
* dataset identity:
* task/model identity:
* coverage disclosure:

## 16. Partial Failure Isolation

* tested failure:
* unaffected capabilities:
* frontend behavior:
* result:

## 17. Browser Matrix

* Chromium:
* Firefox:
* WebKit:
* mobile:

列出真正覆盖的 product cases。

## 18. Accessibility

* keyboard:
* labels:
* chart alternatives:
* tables:
* warnings:
* mobile:

## 19. Performance

* small:
* medium:
* near-cap:
* artifact sizes:
* frontend:
* memory:
* overall envelope:

## 20. Security

* untrusted text:
* arbitrary code:
* artifact JS:
* external network:
* secrets:

必须包含：

```text
NO_MATERIAL_INTELLIGENCE_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

或真实等价 marker。

## 21. Tool Registry Final Phase 10K Surface

列出：

* existing general tools
* dataset tools
* ML tools
* composition-space tools

以及：

* DataProfile requirements
* artifact types
* readiness

## 22. Explicit Phase 10K Limits

确认未实现：

* capability-aware Agent
* automatic multi-tool planning
* LLM result interpretation
* Unified Scientific Workspace
* CrystalNN/VoronoiNN
* Experimental XRD
* trajectory analytics
* Electronic Band/DOS
* Future advanced capabilities

## 23. Files Changed

* backend
* frontend
* tests
* evidence
* docs
* persistent

## 24. Checks

* git diff --check:
* uv lock:
* backend:
* frontend:
* typecheck:
* build:
* service-backed:
* no-skipped:
* docs:
* TASKS:
* evidence integrity:
* security:

## 25. Commit / CI

### Integration Implementation

* commit:
* exact SHA:
* CI run:
* unit:
* frontend:
* service-backed:

### Completion Record

* commit:
* exact SHA:
* CI:

## 26. Queue State

最终：

```text
Phase 10K-5:
ARCHIVED

Phase 10K:
COMPLETE

Phase 10L-0:
NEXT / AWAITING COMPLETE PROMPT
```

## 27. Phase 10K Final Readiness

分别：

* DataProfile:
* Dataset Explorer:
* Materials ML:
* Composition Space:
* API:
* frontend:
* sample identity:
* version binding:
* browser:
* accessibility:
* performance:
* security:

总体：

`READY`

或：

`READY_WITH_EXPLICIT_LIMITS`

## 28. Whether Allowed to Enter Phase 10L-0

只有全部满足才能写“可以”：

* 10K-1 archived
* 10K-2 archived
* 10K-3 archived
* 10K-4 archived
* 10K-5 implementation complete
* single semantic authority verified
* cross-artifact sample identity verified
* resource version binding verified
* stale artifact protection verified
* partial failure isolation verified
* API evidence complete
* browser evidence complete
* accessibility complete
* performance closure complete
* report/recipe compatibility verified
* no accidental Planner intelligence added
* no new uncontrolled dependency
* security PASS
* implementation exact-head CI success
* completion-record exact-head CI success
* 10K-5 archived
* Phase 10K marked COMPLETE
* origin/master == HEAD
* git clean

## 29. Next Phase

只能写：

**Phase 10L-0：Agent / Planner Capability Audit**

不得实现。

---

# 100. PASS 标准

Phase 10K-5 只有全部满足才 PASS：

1. 10K-1～10K-4 全部正式归档。
2. 不新增新的主要科学/ML算法。
3. DataProfile 是唯一 semantic authority。
4. formula semantics 没有重复实现。
5. property semantics 没有重复实现。
6. regression/classification semantics 没有重复实现。
7. sample identity 全链路一致。
8. 不使用数组位置进行跨 artifact binding。
9. resource version binding 正确。
10. stale artifact 不会错误复用。
11. partial dataset coverage 明确。
12. unit semantics 跨产品一致。
13. Dataset Explorer 与 ML integration正确。
14. ML 与 Composition Space binding正确。
15. multiple task/model identity明确。
16. Data-ready 与 platform-ready继续区分。
17. ambiguous semantics 不被 silent resolve。
18. frontend capability gating正确。
19. frontend不重新计算正式科学结果。
20. artifacts来自真实 runtime。
21. E2E API evidence真实通过。
22. materials table case通过。
23. structure-enriched case通过。
24. regression case通过。
25. uncertainty case通过。
26. classification case通过。
27. dataset comparison case通过。
28. partial capability case正确。
29. ambiguity case正确。
30. partial failure isolation正确。
31. report compatibility通过。
32. recipe/reproducibility通过。
33. browser Chromium通过。
34. browser Firefox通过。
35. browser WebKit通过。
36. mobile通过。
37. accessibility通过。
38. performance closure通过。
39. artifact size受控。
40. no external network。
41. secret scan PASS。
42. 不新增 Run Everything Tool。
43. 不实现 multi-tool Agent planning。
44. 不实现 LLM result interpretation。
45. 不实现 Unified Workspace。
46. 默认无新 dependency。
47. 全回归通过。
48. implementation exact-SHA CI success。
49. completion-record exact-SHA CI success。
50. 10K-5 archived。
51. Phase 10K = COMPLETE。
52. Phase 10L-0 remains NEXT。
53. origin/master == HEAD。
54. git clean。

---

现在开始。

第一步：

**不要立即修改代码。**

先输出：

# Phase 10K-5 Entry / Material Intelligence Integration Audit

必须基于真实 10K-1～10K-4 回答：

1. 10K-1～10K-4 是否全部 ARCHIVED？
2. DataProfile 的唯一 semantic authority 是否真的被所有 10K 产品复用？
3. stable sample identity 当前如何贯穿 Dataset / ML / Composition Space？
4. resource version/hash 是否贯穿所有 artifacts？
5. 是否存在 stale artifact 风险？
6. property/unit identity 是否跨产品一致？
7. Dataset Explorer 是否正确发现 ML/Composition Space availability？
8. ML artifact 是否被 Composition Space 正式消费，而不是 frontend重算？
9. multiple targets/models 是否有稳定 identity？
10. Dataset comparison 是否在 10K-2 / 10K-4 中使用相同 dataset/group identity？
11. 哪些产品存在 partial coverage？
12. partial coverage 是否披露？
13. 哪些产品存在 frontend-only scientific calculation？
14. 哪些 browser paths 还没有真实 runtime evidence？
15. Report/Recipe 当前能否承载 Phase 10K artifacts？
16. Phase 10K 当前最主要 integration bugs 是什么？
17. 哪些只是 product polish，而不是新 algorithm？
18. 哪些发现必须 defer 到 10L？
19. 是否需要任何新 public Tool？默认答案应为 NO，除非有明确 architecture blocker。
20. 完成本阶段后 Phase 10K 是否可以正式 CLOSED？

Audit 完成后直接修复 integration gaps、补充证据并完成 CI/归档。

不要等待人工确认。

本轮最终停在：

**Phase 10L-0：Agent / Planner Capability Audit = NEXT / AWAITING COMPLETE PROMPT**

---END---

---TASK---
 状态：待处理
你现在执行：

# Phase 10L-0：Agent / Planner Capability Audit

本阶段是 Phase 10L Intelligent Analysis Agent 的入口审计阶段。

这是一个：

**ARCHITECTURE AUDIT / CAPABILITY INVENTORY / GAP ANALYSIS GATE**

不是 Planner 实现阶段。

本阶段结束后必须：

**REVIEWER_GATE**

不得自动进入 Phase 10L-1。

---

# 0. 本阶段最高目标

本阶段必须基于真实 repository 回答：

> 当前项目中的 Agent / Planner 到底已经做到什么程度？

重点不是根据旧文档猜。

重点是审计真实：

* Mock Planner
* deterministic routing
* real LLM Planner
* DataProfile 2.0
* AnalysisPlan
* ToolCall
* Tool Registry
* Tool capability metadata
* PlanValidator
* QueueWorkerRuntime
* resource/artifact binding
* current multi-tool support
* frontend planner flow
* result interpretation
* error/repair behavior

最终需要判断：

当前 Planner 到底属于：

```text
KEYWORD_ROUTER

MOSTLY_PROMPT_ROUTED

PROFILE_AWARE_SINGLE_TOOL_PLANNER

CAPABILITY_AWARE_SINGLE_TOOL_PLANNER

PARTIAL_MULTI_TOOL_PLANNER

CAPABILITY_AWARE_MULTI_TOOL_PLANNER
```

只能根据真实实现选。

---

# 1. Hard Entry Gate

首先验证：

```text
Phase 10J-6 = ARCHIVED
Gate J6-R = PASS

Phase 10K-0 = ARCHIVED
Phase 10K-1 = ARCHIVED
Phase 10K-2 = ARCHIVED
Phase 10K-3 = ARCHIVED
Phase 10K-4 = ARCHIVED
Phase 10K-5 = ARCHIVED

Phase 10K = COMPLETE

Phase 10L-0 = NEXT
```

必须读取真实：

* Phase 10K-5 result
* Phase 10K completion summary
* current roadmap
* TASKS
* persistent state
* Tool Registry notes
* architecture decisions

如果 Phase 10K 尚未完整关闭：

输出：

`BLOCKED_BY_PHASE_10K`

并停止。

不得继续 Planner audit。

---

# 2. Reviewer Gate Rule

这是本阶段的硬规则。

Phase 10L-0 完成后：

```text
Phase 10L-0:
ARCHIVED

Phase 10L-1:
REVIEWER_GATE / NOT_QUEUED
```

或者符合当前 repository queue terminology 的等价状态。

不得：

* 自动创建 Phase 10L-1 executable task
* 自动进入 Analysis Intent implementation
* 自动修改 Planner contracts
* 自动开始 multi-tool planning
* 自动实现 result interpretation

最终必须停下来等待 reviewer 根据本阶段结果设计 10L-1。

---

# 3. Canonical Product Context

项目最终目标：

# Material Data Intelligence & Visualization Platform

核心流程：

```text
Materials Data
      ↓
Material Data Profile
      ↓
Natural Language Goal
      ↓
Analysis Intent
      ↓
Capability-Aware Planner
      ↓
Validated AnalysisPlan
      ↓
Tool Registry / Adapter
      ↓
Scientific Execution
      ↓
Artifacts
      ↓
Interpretation
      ↓
Report / Recipe
```

Phase 10K 已经负责：

* Material Data Profile 2.0
* Dataset Materials Explorer
* Materials ML
* Composition Space

Phase 10L 开始负责：

**如何让 Agent 正确理解目标并选择/组合这些能力。**

---

# 4. Phase 10L Current High-Level Direction

当前 roadmap 只冻结大方向：

```text
Phase 10L-0
Agent / Planner Capability Audit

Phase 10L-1
Analysis Intent Contract

Phase 10L-2
Capability-Aware Planner

Phase 10L-3
Bounded Multi-Tool Analysis

Phase 10L-4
Scientific Result Interpretation

Phase 10L-5
Natural-Language Analysis Evidence
```

但：

**10L-1～10L-5 的具体 contract 尚未冻结。**

本阶段必须通过真实代码判断：

这些子阶段是否需要：

* 合并
* 缩小
* 调整边界

不得自行改 ROADMAP。

只提出 reviewer recommendation。

---

# 5. Explicit Non-Scope

本阶段禁止修改：

* AnalysisPlan schema
* ToolCall schema
* DataProfile schema
* Tool Registry public contract
* PlanValidator behavior
* QueueWorkerRuntime behavior
* Mock Planner routing
* LLM Planner prompt
* LLM provider configuration
* frontend planning behavior
* artifact dependency semantics
* result interpretation
* report generation
* retry/repair behavior

禁止新增：

* Agent framework
* workflow engine
* DAG
* memory system
* RAG
* multi-agent architecture
* prompt chaining
* tool calling framework
* new LLM dependency

本阶段允许的代码变更原则上只有：

* audit-only helper/test if absolutely required
* documentation
* persistent records
* result/evidence
* queue state

如果审计需要修改 production Planner 才能“确认能力”：

说明审计设计有问题。

不得修改。

---

# 6. Baseline Verification

进入：

```text
E:\1project\Material Data Intelligence
```

运行：

```bash
git status --short
git branch --show-current
git rev-parse HEAD
git rev-parse origin/master
git log --oneline -40
git diff --stat
git diff --check
```

记录：

* repository
* branch
* HEAD
* origin/master
* status
* Phase 10K-5 implementation commit
* Phase 10K-5 completion-record commit
* Phase 10K archive state
* exact-head CI

工作区必须明确。

如果存在 unrelated source changes：

停止并报告。

---

# 7. Queue Transition

只有 Entry Gate PASS 后：

将：

`Phase 10L-0：Agent / Planner Capability Audit`

设为唯一 active task。

不得把：

`10L-1`

加入 active queue。

TASKS 中必须加入 reviewer barrier，例如：

```text
REVIEWER GATE AFTER PHASE 10L-0

Do not execute Phase 10L-1 automatically.
Phase 10L-1 requires reviewer approval based on the real
Phase 10L-0 Agent / Planner Capability Audit result.
```

实际格式遵循当前 repository。

---

# 8. 必读 Canonical Documentation

完整阅读：

```text
README.md
AGENTS.md
MASTER_PROMPT.md

docs/ROADMAP.md
docs/00_PROJECT_GOAL.md
docs/01_PRODUCT_REQUIREMENTS.md
```

或实际 canonical equivalents。

同时：

```text
persistent/PROJECT_BRIEF.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/TOOL_REGISTRY_NOTES.md
persistent/ARCHITECTURE_DECISIONS.md
```

以及 Phase 10K completion summary。

---

# 9. 必读历史 Planner 设计

必须定位并阅读所有与 Planner 有关的历史 docs。

搜索：

```bash
rg -n "Planner|AnalysisPlan|PlanValidator|Mock Planner|LLM Planner|tool routing|Tool Registry|intent|planning|repair|retry|tool selection" docs persistent README.md MASTER_PROMPT.md
```

重点阅读：

* Phase 1–9 Planner implementation/history
* real LLM phase
* PlanValidator
* Tool Registry
* QueueWorkerRuntime
* Phase 10 planner-routing changes
* Phase 10K DataProfile integration notes

历史文档：

只用于理解。

当前代码才是 implementation truth。

---

# 10. Planner Code Discovery

搜索真实代码：

```bash
rg -n "class .*Planner|def .*plan|MockPlanner|LLMPlanner|AnalysisPlan|PlanValidator|ToolCall|tool_registry|planner" .
```

排除：

* generated
* node_modules
* build artifacts
* evidence binary

建立：

# Planner Architecture File Map

至少列：

| Component          | File | Responsibility |
| ------------------ | ---- | -------------- |
| Planner API        |      |                |
| Mock Planner       |      |                |
| LLM Planner        |      |                |
| Prompt Builder     |      |                |
| AnalysisPlan Model |      |                |
| ToolCall Model     |      |                |
| PlanValidator      |      |                |
| Tool Registry      |      |                |
| Queue Runtime      |      |                |
| Planner UI         |      |                |

---

# 11. Audit A — AnalysisPlan Contract

完整审计当前 AnalysisPlan。

必须回答：

* schema name/version
* plan ID
* user goal storage
* dataset/resource binding
* ToolCall count
* ordering
* dependencies
* artifact input references
* output expectations
* validation state
* planner metadata
* model/provider metadata
* warnings
* provenance
* persistence

建立：

# Current AnalysisPlan Contract Matrix

---

# 12. Single Tool vs Multiple Tools

这是最关键问题之一。

必须通过代码和测试确认：

当前 `AnalysisPlan` 是否允许：

```text
ToolCall[]
```

如果允许多个：

进一步确认：

* 是独立顺序 list？
* 是否真正执行多个？
* 是否 validator 支持？
* runtime 是否支持？
* artifacts 是否各自持久化？
* 是否有 dependencies？

不要因为 schema 是 array 就写：

MULTI_TOOL_READY。

---

# 13. Multi-Tool Execution Reality

必须找到真实测试或运行代码证明：

### Case

一个 AnalysisPlan：

```text
Tool A
Tool B
```

是否真正执行。

分别审计：

* persistence
* validation
* queue execution
* failure handling
* artifact persistence
* frontend timeline

分类：

```text
NOT_SUPPORTED

SCHEMA_ONLY

SEQUENTIAL_INDEPENDENT

ORDERED_MULTI_TOOL

DEPENDENCY_AWARE
```

---

# 14. Dependency Representation

检查 AnalysisPlan 是否存在：

* `depends_on`
* artifact binding
* input from previous ToolCall
* dependency IDs
* step IDs
* resource outputs

如果不存在：

明确。

不得把 list order 称：

DAG。

---

# 15. Artifact Input Binding

非常重要。

检查一个 ToolCall 的 input 是否只能来自：

* dataset/resource

还是可以来自：

* previous artifact

例如：

```text
Tool A produces artifact X
Tool B consumes artifact X
```

当前支持程度必须明确。

---

# 16. Failure Semantics

如果 AnalysisPlan 有多个 ToolCall：

检查：

Tool A FAIL 时：

* Tool B 是否继续？
* 整个 job FAIL？
* partial artifacts保留？
* retry？
* error propagation？

这会直接决定 10L-3 scope。

---

# 17. Cancellation

审计 Planner-generated multi-tool job 的 cancellation semantics。

只记录现状。

不要修改。

---

# 18. Audit B — Mock / Deterministic Planner

找到 Mock Planner 全部 routing logic。

检查：

* keyword matching
* regex
* tool ID lookup
* resource type
* DataProfile
* column semantics
* Tool Registry metadata
* params generation
* fallback
* ambiguity

建立：

# Mock Planner Decision Inputs

| Signal             | Used? | How |
| ------------------ | ----: | --- |
| raw prompt         |       |     |
| keywords           |       |     |
| resource kind      |       |     |
| DataProfile        |       |     |
| semantic roles     |       |     |
| readiness          |       |     |
| Tool Registry      |       |     |
| explicit tool IDs  |       |     |
| previous artifacts |       |     |

---

# 19. Keyword Router Audit

必须真实统计：

当前 Mock Planner 中有多少 routing rule 属于类似：

```text
if "rdf" in prompt
if "xrd" in prompt
if "histogram" in prompt
```

不要只给 impression。

可以分类：

* exact command mapping
* keyword
* structured detection
* profile-aware
* registry-aware

不需要精确到无意义行数，但必须有实质证据。

---

# 20. Resource Awareness

例如用户说：

> analyze this dataset

Mock Planner 是否知道：

这是：

* table
* structure
* trajectory
* phonon
* volumetric

还是完全只看 prompt？

必须测试/代码证明。

---

# 21. DataProfile 2.0 Use

这是 Phase 10K → 10L 最重要衔接。

必须追踪：

DataProfile 2.0 是否进入 Planner。

包括：

* object passed?
* serialized context?
* only resource kind?
* readiness?
* semantic groups?
* ML task identities?
* properties?
* composition?

建立：

# Planner DataProfile Consumption Matrix

| Profile Information | Mock Planner | LLM Planner | Validator |
| ------------------- | -----------: | ----------: | --------: |
| resource kind       |              |             |           |
| formula             |              |             |           |
| material properties |              |             |           |
| structure presence  |              |             |           |
| trajectory          |              |             |           |
| phonon              |              |             |           |
| volumetric          |              |             |           |
| regression task     |              |             |           |
| uncertainty         |              |             |           |
| classification      |              |             |           |
| readiness           |              |             |           |

---

# 22. Planner Classification

Mock Planner 最终必须归类为：

```text
KEYWORD_ROUTED
MOSTLY_KEYWORD_ROUTED
PARTIAL_PROFILE_AWARE
PROFILE_AWARE
CAPABILITY_AWARE
```

并说明证据。

---

# 23. Audit C — Real LLM Planner

找到真实 LLM provider path。

必须确认：

* provider interface
* prompt template
* system prompt
* Tool Registry serialization
* DataProfile serialization
* model config
* JSON mode/schema
* timeout
* retry
* parse failure
* validation loop
* fallback
* mock isolation

不得调用真实 LLM。

本阶段只读代码/tests。

---

# 24. LLM Planner Prompt Inputs

明确 LLM 实际收到什么。

建立：

# LLM Planner Context Matrix

包括：

* user prompt
* dataset/resource metadata
* DataProfile
* Tool descriptions
* params schemas
* capability requirements
* artifact types
* safety instructions
* max tools
* previous errors
* previous plan
* conversation history

---

# 25. Tool Registry Exposure to LLM

检查是：

### A

只提供：

```text
tool ID + description
```

还是：

### B

提供：

```text
tool ID
description
params schema
resource compatibility
outputs
```

还是更完整 capability metadata。

必须真实记录。

---

# 26. Tool Capability Metadata Audit

当前 Tool Registry 每个 Tool 是否有：

* tool ID
* description
* domain
* input resource kind
* params schema
* output artifacts
* cost/resource cap
* scientific requirements
* semantic role requirements
* user-facing description
* planner hints

建立：

# Tool Capability Metadata Matrix

---

# 27. Planner-Friendly Registry

最终判断 Registry 当前更像：

```text
EXECUTION_REGISTRY
```

还是：

```text
PLANNER_CAPABILITY_REGISTRY
```

可能是：

`PARTIAL_PLANNER_CAPABILITY_REGISTRY`

说明缺口。

---

# 28. Analysis Eligibility

例如：

`ml.regression_evaluation`

是否在 Registry 中正式声明：

需要 regression semantic group？

还是只有 adapter 自己执行时才检查？

这个差异非常重要。

---

# 29. Audit D — PlanValidator

完整审计 PlanValidator。

检查：

* allowed Tool IDs
* params schema
* strict additionalProperties
* resource existence
* resource kind
* DataProfile
* semantic readiness
* artifact input
* caps
* tool count
* dependencies
* duplicate calls
* unsafe params

---

# 30. Validator Classification

PlanValidator 当前是：

```text
SCHEMA_VALIDATOR

SCHEMA_AND_REGISTRY_VALIDATOR

RESOURCE_AWARE_VALIDATOR

SEMANTIC_CAPABILITY_VALIDATOR

DEPENDENCY_AWARE_VALIDATOR
```

根据真实实现分类。

---

# 31. DataProfile Readiness in Validator

检查：

DataProfile 2.0 readiness 是否用于：

拒绝：

```text
regression tool on dataset without predictions
```

或者：

这种错误直到 Adapter runtime 才发现。

必须明确。

---

# 32. Params Generation

Planner 当前如何决定：

* x/y columns
* selected ML task
* property
* model
* structure resource
* volumetric field
* trajectory params

是：

* prompt extraction
* default
* DataProfile
* hardcoded
* adapter default
* LLM guessed

必须分类。

---

# 33. Ambiguous Semantics

DataProfile 可能返回：

`AMBIGUOUS`

当前 Planner 遇到时：

* reject?
* choose first?
* ask user?
* ignore?
* LLM decides?

必须查真实行为。

---

# 34. Clarification Support

检查现有 Planner/UI 是否存在：

* needs clarification state
* follow-up question
* unresolved field
* plan draft requiring user selection

如果不存在：

明确：

`NOT_IMPLEMENTED`

不要设计实现。

---

# 35. Audit E — Tool Selection

建立正式：

# Tool Selection Mechanism Inventory

对于至少以下 domain：

* general table
* composition
* structure
* trajectory
* phonon
* BZ
* volumetric
* dataset intelligence
* materials ML
* composition space

检查：

Planner 是如何选择 tool 的。

---

# 36. Capability Collision

检查是否存在多个 tool 都可以处理相似问题。

例如：

```text
viz.histogram
table.distribution_summary
dataset.materials_summary
```

Planner 当前如何区分？

如果只是 keyword：

记录 risk。

---

# 37. Tool Granularity Effect on Planner

Phase 10K 已刻意采用 product-level tools。

审计：

这是否使 Planner capability surface 更清晰。

记录：

* product-level tools
* low-level tools
* overlap

这会影响 10L-2。

---

# 38. Audit F — Planner Output Quality

使用现有 deterministic tests/fixtures，审计典型自然语言。

禁止调用真实 LLM。

可以使用：

* Mock Planner
* fixture-based LLM responses
* existing tests

测试以下代表性 prompt。

---

# 39. Case 1 — Composition

```text
分析这批材料主要有哪些元素和化学体系。
```

当前 Planner：

选择什么？

是否数据感知？

---

# 40. Case 2 — Structure

```text
看看这个晶体结构是否合理。
```

当前 Planner 能否：

理解这是 broad scientific intent？

还是只找到：

structure summary

或根本不匹配？

这里只记录。

---

# 41. Case 3 — ML

```text
分析这个模型在哪些材料上预测得不好。
```

当前 Planner 是否选择：

Materials ML Evaluation？

是否知道 chemistry-conditioned error？

还是只匹配 scatter？

---

# 42. Case 4 — Uncertainty

```text
这些不确定度可信吗？
```

当前 Planner 是否知道：

uncertainty readiness？

---

# 43. Case 5 — Phonon

```text
检查这个声子计算有没有明显问题。
```

当前 Planner 输出什么？

---

# 44. Case 6 — Volumetric

```text
看看这个电荷密度里主要有什么特征。
```

当前 Planner 输出什么？

---

# 45. Case 7 — Broad Dataset Intent

```text
帮我全面分析一下这批材料。
```

这是关键。

当前 Planner：

* 一个 tool？
* arbitrary first match？
* fails？
* multi-tool？
* LLM only？

记录。

不要修。

---

# 46. Case 8 — Explicit Tool-Like Intent

```text
画 formation_energy 的分布。
```

这种应该是现有 Planner 相对擅长的 case。

作为 baseline。

---

# 47. Planner Evaluation Matrix

建立：

| Prompt | Expected Capability Category | Current Mock Result | Current LLM Design Capability | Gap |
| ------ | ---------------------------- | ------------------- | ----------------------------- | --- |

注意：

这里的 “Expected” 是产品意图，不是官方 validation。

---

# 48. Audit G — Analysis Intent

检查 repository 是否已经存在类似：

* Intent
* UserIntent
* AnalysisIntent
* Goal
* AnalysisRequest
* PlannerRequest
* objective

如果已有：

必须审计。

不要因为 roadmap 叫：

`Analysis Intent Contract`

就新建重复对象。

---

# 49. Current Intent Representation

如果目前只有：

```text
prompt: string
```

明确。

如果已经有：

```text
goal
targets
constraints
output preferences
```

则记录。

这直接决定 10L-1 是否需要新 contract。

---

# 50. Intent vs Plan

必须检查当前 architecture 是否混合：

用户需求

和：

执行计划。

例如：

AnalysisPlan 是否直接保存 raw prompt，但没有独立 intent。

记录优缺点。

不要修改。

---

# 51. Audit H — Multi-Turn / Conversation

检查当前 Planner 是否接收：

* conversation history
* previous plan
* previous user correction
* selected resource context

如果没有：

明确。

但 Phase 10L Initial Release 不一定需要 full conversational memory。

不要自动把 multi-turn 变成 blocker。

---

# 52. Audit I — Plan Repair

检查现有：

* invalid JSON repair
* schema re-prompt
* validation-error repair
* fallback
* retry

区分：

## Transport / Parse Repair

例如 invalid JSON。

## Scientific Plan Repair

例如：

tool requires regression data but dataset lacks it。

后者可能尚未实现。

---

# 53. Plan Repair Authority

检查是否存在风险：

LLM 在 validation fail 后无限改计划。

当前 caps：

* retry count
* timeout
* provider limits

记录。

---

# 54. Audit J — Runtime / Planner Boundary

确认：

LLM 是否任何时候能够：

* execute Python
* shell
* arbitrary code
* direct filesystem
* direct scientific library calls

预期必须是：

NO。

如果不是：

高优先级风险。

---

# 55. Tool Execution Authority

正式应该是：

```text
Planner
↓
Validated AnalysisPlan
↓
QueueWorkerRuntime
↓
Registered Adapter
```

本阶段必须验证真实 architecture 仍然满足这一点。

---

# 56. Audit K — Frontend Planner UX

审计 PlannerWorkbench/current frontend。

检查用户目前能看到：

* natural-language prompt
* selected dataset/resource
* generated plan
* tool calls
* params
* validation
* execution timeline
* artifacts
* errors
* retry
* edit plan
* plan approval

建立：

# Planner UX Inventory

---

# 57. User Control

检查当前是否支持：

* inspect plan before execution
* edit params
* remove tool
* rerun
* cancel
* retry

只记录。

不要认为所有都必须进入 Phase 10L。

---

# 58. Broad Intent UX

如果 Planner 无法处理 broad intent：

当前 UI 是否引导用户：

* choose tool
* refine prompt
* select resource

记录。

---

# 59. Audit L — Result Interpretation

检查是否已经存在：

* LLM summary
* deterministic summary
* findings
* warnings
* next-step recommendations
* artifact explanation

Phase 10L-4 可能不是从零开始。

必须真实盘点。

---

# 60. Scientific Interpretation Authority

如果已有 LLM result summary：

检查它收到：

* raw artifact?
* structured summary?
* entire dataset?
* tool metadata?
* warnings?

以及是否存在：

“不要编造未计算结论”

的 contract。

---

# 61. Audit M — Planner Security

检查：

* prompt injection handling
* tool description exposure
* untrusted dataset names
* artifact contents
* provider prompt boundaries
* arbitrary tool ID
* arbitrary params
* unknown tool rejection
* output schema enforcement

只审计。

不要展开企业 security phase。

---

# 62. Tool Injection

检查用户 prompt 能否让 Planner输出：

不存在 tool

或：

危险 params。

PlanValidator 是否阻止？

必须有实际 test/code evidence。

---

# 63. Artifact Prompt Injection

如果未来/当前 LLM 会读取 artifact summary：

是否有 untrusted content boundary？

如果当前还没 result interpretation：

记录 future risk 给 10L-4。

---

# 64. Audit N — Caps / Resource Limits

Planner 层当前是否限制：

* max ToolCalls
* max prompt size
* max registry tools serialized
* max output size
* provider timeout
* retry count
* max plan complexity

这会影响 10L-3。

---

# 65. Max Tool Count

如果当前没有 multi-tool：

也检查 AnalysisPlan validator 是否已有：

max tool count。

记录。

---

# 66. Audit O — Current Tests

完整定位：

* Planner unit tests
* PlanValidator tests
* Mock Planner tests
* LLM fixture tests
* provider tests
* service-backed planning tests
* browser planner tests

建立：

# Planner Test Coverage Matrix

---

# 67. Do Not Mistake Fixture LLM for Real Provider Evidence

必须区分：

* Mock Planner
* fake LLM response
* recorded fixture
* gated real provider

不要写：

“LLM Planner scientifically validated”

仅因为 fixture PASS。

---

# 68. Real LLM Test Boundary

本阶段禁止调用真实 LLM。

只审计：

当前 gated real-provider integration 是否存在和如何工作。

不消耗用户 API key。

---

# 69. Audit P — Tool Registry Scale

统计当前正式 Tool Registry：

* total tools
* domains
* 10K additions
* overlapping low-level tools
* product-level tools

目的是判断：

LLM prompt 是否还能直接 serialise entire registry。

不要为此做 optimization。

---

# 70. Tool Description Quality

抽样审计至少：

* generic visualization
* structure
* trajectory
* phonon
* volumetric
* dataset
* ML
* composition space

检查 description 是否足以让 Planner区分。

---

# 71. Capability Requirements

特别检查 Tool Registry 是否能够表达：

```text
requires:
regression_task
```

或：

```text
resource_kind:
trajectory
```

如果没有：

这是 10L-2 可能要解决的重要 gap。

---

# 72. Audit Q — Plan / Recipe Relationship

检查：

AnalysisPlan

和：

Recipe

是否不同对象。

Recipe 是否可以：

* replay
* hold tool params
* reference resources

Planner 是否可以直接生成 Recipe？

当前如何？

这关系 10L architecture，但本阶段只记录。

---

# 73. Audit R — Planner Persistence

检查 Plan 是否：

* persisted before execution
* immutable
* editable
* versioned
* linked job
* linked user prompt
* linked planner/provider

记录。

---

# 74. Audit S — Planner Reproducibility

Mock Planner：

相同 prompt/data 是否 deterministic？

LLM Planner：

是否记录：

* provider
* model
* temperature
* prompt/schema version
* generated plan

确保以后可以审计。

---

# 75. Temperature / Randomness

如果 LLM provider config 有 temperature：

记录 current policy。

不要修改。

---

# 76. Audit T — Agent Terminology

检查 repository 中：

* Agent
* Planner
* Assistant
* Analysis Agent

是否混用。

本阶段建议文档统一概念，但不要大规模 rename source code。

最终至少冻结：

```text
Agent = user-facing intelligent orchestration concept
Planner = component that generates AnalysisPlan
Runtime = deterministic execution
```

如果 current architecture已有更准确定义：

遵循真实设计。

---

# 77. Current-State Architecture Diagram

本阶段必须形成基于真实代码的 diagram。

例如：

```text
User Prompt
   ↓
Planner Request
   ↓
Mock / LLM Planner
   ↓
AnalysisPlan
   ↓
PlanValidator
   ↓
Persisted Job
   ↓
QueueWorkerRuntime
   ↓
Tool Registry
   ↓
Adapters
   ↓
Artifacts
```

然后标注：

DataProfile 当前在哪里进入。

必须与真实代码一致。

---

# 78. Gap Analysis Categories

所有发现统一分类：

## READY

真实可用。

## REUSABLE_FOUNDATION

已有基础，但不满足 Agent product goal。

## PARTIAL

有部分行为。

## MISSING_10L

Phase 10L Initial Release 必须解决。

## DEFER_10M

属于 Workspace。

## DEFER_10N

属于 scientific tool coverage。

## FUTURE

非初版。

## NOT_NEEDED

不需要。

---

# 79. 必须形成 Agent / Planner Gap Matrix

新增：

```text
docs/phase10l/phase10l0_agent_planner_gap_matrix.md
```

或等价文件。

至少包含：

| Capability | Current Implementation | Evidence | Status | Target Phase |
| ---------- | ---------------------- | -------- | ------ | ------------ |

覆盖：

* user intent
* DataProfile awareness
* tool capability metadata
* tool selection
* params selection
* single-tool plan
* multi-tool plan
* dependencies
* artifact binding
* PlanValidator
* ambiguity
* clarification
* plan repair
* result interpretation
* user plan inspection
* execution safety

---

# 80. 必须形成 Planner Maturity Assessment

输出一个明确 maturity level。

建议：

## Level 0

Manual tool execution

## Level 1

Keyword routing

## Level 2

Structured single-tool planning

## Level 3

Data/profile-aware tool selection

## Level 4

Capability-aware multi-tool planning

## Level 5

Bounded interpretation/repair

选择当前真实 level。

也可以用 repository 更适合的等级，但必须定义。

---

# 81. 10L-1 Scope Recommendation

本阶段最终必须向 reviewer 推荐：

**Analysis Intent Contract 到底需不需要独立存在。**

可能结果：

### A — REQUIRED

当前只有 raw prompt。

需要明确 intent contract。

### B — LIGHTWEIGHT_EXTENSION

当前已有足够 PlannerRequest，只需增加少量结构化 fields。

### C — ALREADY_EXISTS

已有 equivalent。

则 10L-1 应调整为 hardening，而不是重复造 contract。

必须选一个。

---

# 82. 10L-2 Scope Recommendation

回答：

Capability-Aware Planner 真正缺什么？

候选：

* profile context
* structured capability metadata
* eligibility resolver
* tool ranking
* params binding
* ambiguity handling

只建议。

不实现。

---

# 83. 10L-3 Scope Recommendation

根据真实 multi-tool能力判断：

### Case A

已有 multi-tool execution：

只补 dependency/selection。

### Case B

schema 支持多 tool，但 runtime不完整：

需要 execution hardening。

### Case C

完全 single-tool：

可能需要 contract evolution。

必须明确。

---

# 84. 10L-4 Scope Recommendation

根据现有 summary/report能力判断：

* 从零实现？
* 扩展 existing LLM summary？
* 只需要 structured result context + guardrails？

必须给 recommendation。

---

# 85. 10L-5 Scope Recommendation

规划最终 natural-language evidence cases。

至少建议：

* dataset analysis
* structure analysis
* model evaluation
* phonon
* volumetric

但不要写 implementation prompt。

---

# 86. Critical Reviewer Decisions

最终列出：

# Reviewer Decisions Required Before Phase 10L-1

只列真正需要人工决定的架构点。

例如：

1. 是否需要独立 AnalysisIntent schema？
2. 是否允许 AnalysisPlan schema evolution？
3. multi-tool 采用 ordered sequence 还是 dependency graph？
4. artifact binding最小模型是什么？
5. clarification 是否进入 Initial Release？
6. plan repair 是否进入 Initial Release？
7. capability metadata 放 Tool Registry 还是独立 resolver？

不要自己决定这些高影响问题，除非 current architecture 已经事实上确定。

---

# 87. Architecture Constraints Already Frozen

以下不需要 reviewer重新决定：

## LLM Does Not Execute Code

继续成立。

## Tool Registry Is Execution Boundary

继续成立。

## PlanValidator Before Runtime

继续成立。

## DataProfile Is Deterministic Data Truth

继续成立。

## Scientific Calculations Are Deterministic Backend

继续成立。

## LLM Can Plan / Explain

但不能虚构未计算结果。

---

# 88. Documentation

建议新增：

```text
docs/phase10l/
  phase10l0_agent_planner_capability_audit.md
  phase10l0_agent_planner_gap_matrix.md
  phase10l0_current_planner_architecture.md
  phase10l0_phase10l_scope_recommendation.md
  phase10l0_reviewer_decisions.md
```

允许合并重复文档。

不要生成 10L-1 implementation prompt。

这是 reviewer gate。

---

# 89. Canonical Roadmap

不要修改：

Phase 10L high-level roadmap。

可以在 Phase 10L docs 中提出：

`RECOMMENDED INTERNAL SCOPE ADJUSTMENT`

但：

不得自行改变：

* Phase number
* future sequence
* current roadmap authority

---

# 90. Persistent Updates

更新：

```text
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/TOOL_REGISTRY_NOTES.md
persistent/ARCHITECTURE_DECISIONS.md
```

但 ARCHITECTURE_DECISIONS：

只记录审计确认的现状或既有事实。

不要提前冻结 reviewer 尚未批准的新 architecture。

---

# 91. DESIGN_PROGRESS

记录：

* Phase 10K complete
* Phase 10L-0 audit
* current Planner maturity
* critical gaps
* reviewer gate

---

# 92. TASK_BOARD

执行中：

```text
10L-0 = IN_PROGRESS
```

完成后：

```text
10L-0 = COMPLETE / ARCHIVED

10L-1 = REVIEWER_GATE
```

不得：

```text
10L-1 = NEXT_AUTOMATIC
```

---

# 93. OPEN_QUESTIONS

将真正需要 reviewer 决定的 Agent architecture问题列为 ACTIVE。

已经由代码事实回答的问题关闭。

---

# 94. TOOL_REGISTRY_NOTES

记录：

当前 Registry 对 Planner 的可用 metadata。

重点：

* resource requirements
* semantic requirements
* outputs
* descriptions
* caps

并指出 missing planner-facing metadata。

不修改 Tool definitions。

---

# 95. Architecture Decision Records

如果发现 repository 已经通过代码事实确立：

例如：

> AnalysisPlan supports ordered multiple ToolCalls

可以在 ADR/persistent 中记录现状。

但不要把：

“我们建议 future 使用 DAG”

写成已决定 ADR。

---

# 96. Audit Tests

本阶段不新增 production feature。

但可以运行现有 Planner tests。

至少：

```bash
uv run python -m pytest -q
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
```

以及：

* Planner-specific unit tests
* PlanValidator tests
* service-backed integration
* no-skipped assertion
* docs consistency
* TASKS/result consistency
* security scan

---

# 97. Optional Read-Only Probe Tests

如果需要确认 planner behavior：

允许使用：

* existing test client
* Mock Planner
* fixed fixtures
* local deterministic service stack

禁止：

* real LLM
* external network
* production provider

---

# 98. No Real LLM

本阶段必须明确：

```text
REAL_LLM_CALLS = 0
```

如果已有 test gate会自动 skip real provider：

如实报告。

不得用用户 API key。

---

# 99. External Network

必须：

```text
NO_PHASE10L0_EXTERNAL_NETWORK_REQUESTS
```

或 repository等价 marker。

---

# 100. Secret Scan

必须：

```text
NO_SECRET_PATTERN_HITS
```

---

# 101. No Source Implementation Changes

理想状态：

本阶段 source implementation changes：

`NONE`

如果为了 audit 增加非常小的 test helper：

必须解释。

不得修改 Planner行为。

最终 report 必须单独列：

`Production Planner Behavior Changes: NONE`

---

# 102. Commit

完成 audit/docs/persistent 后：

```bash
git status --short
git diff --stat
git diff --check
```

只 stage Phase 10L-0相关文件。

禁止：

```bash
git add .
```

建议 commit：

```text
Audit agent planner capabilities
```

遵循 repository style。

push：

`origin master`

---

# 103. Current-HEAD CI

必须验证 exact audit commit SHA：

* Unit Tests
* Frontend Typecheck & Build
* Service-backed Integration
* no-skipped assertion

全部 success。

---

# 104. Completion Record

CI success 后：

写 Phase 10L-0 completion record。

记录：

* current Planner architecture
* maturity
* DataProfile use
* registry use
* AnalysisPlan capabilities
* multi-tool reality
* validator
* result interpretation
* gaps
* recommended 10L scope
* reviewer decisions

然后 commit。

---

# 105. Completion-Record CI

验证 completion-record exact SHA。

成功后 archive 10L-0。

---

# 106. Queue Barrier

最终必须保证：

```text
Phase 10L-0:
ARCHIVED

Phase 10L-1:
REVIEWER_GATE / AWAITING REVIEWER PROMPT
```

TASKS 不得含可自动执行的 10L-1 implementation block。

---

# 107. Final Report Format

最终严格输出：

# Phase 10L-0 Agent / Planner Capability Audit Result

## 1. Conclusion

PASS / PARTIAL_PASS / FAIL

## 2. Baseline

* Phase 10K completion:
* 10K-5 archive:
* branch:
* initial HEAD:
* origin/master:
* git status:

## 3. Current Planner Architecture

列出真实 flow：

```text
...
```

包括：

* API
* Mock Planner
* LLM Planner
* AnalysisPlan
* PlanValidator
* Runtime
* Tool Registry
* Artifact

## 4. Current AnalysisPlan

* schema/version:
* ToolCall count:
* ordering:
* dependencies:
* artifact binding:
* persistence:
* versioning:
* failure semantics:

## 5. Multi-Tool Reality

明确选择：

* NOT_SUPPORTED
* SCHEMA_ONLY
* SEQUENTIAL_INDEPENDENT
* ORDERED_MULTI_TOOL
* DEPENDENCY_AWARE

并给证据。

## 6. Mock Planner

* routing style:
* keyword dependence:
* resource awareness:
* DataProfile awareness:
* Registry awareness:
* ambiguity:
* params generation:

最终 classification。

## 7. LLM Planner

* provider architecture:
* prompt inputs:
* DataProfile context:
* Tool Registry context:
* JSON/schema enforcement:
* validation:
* retry:
* repair:
* fallback:

本阶段：

`REAL_LLM_CALLS = 0`

## 8. DataProfile → Planner Integration

逐项：

* resource kind:
* composition:
* properties:
* structure:
* trajectory:
* phonon:
* volumetric:
* regression:
* uncertainty:
* classification:
* readiness:

分别：

Mock / LLM / Validator。

## 9. Tool Registry Planner Readiness

* total tools:
* domains:
* descriptions:
* params schemas:
* resource requirements:
* semantic requirements:
* output metadata:
* caps:
* planner hints:

最终：

EXECUTION_REGISTRY / PARTIAL_PLANNER_REGISTRY / PLANNER_CAPABILITY_REGISTRY

## 10. PlanValidator

* tool allowlist:
* params:
* resource:
* profile:
* semantics:
* caps:
* multi-tool:
* dependency:
* artifact binding:

最终 maturity classification。

## 11. Tool Selection

按 domain：

* table:
* composition:
* structure:
* trajectory:
* phonon:
* BZ:
* volumetric:
* dataset:
* ML:
* composition space:

说明 current mechanism。

## 12. Representative Prompt Audit

逐 case：

### Composition

prompt:
current result:
gap:

### Structure

...

### ML

...

### Uncertainty

...

### Phonon

...

### Volumetric

...

### Broad Dataset Intent

...

### Explicit Single Tool

...

## 13. Analysis Intent

* existing object:
* raw prompt only:
* structured goal:
* targets:
* constraints:
* desired outputs:

结论：

* REQUIRED
* LIGHTWEIGHT_EXTENSION
* ALREADY_EXISTS

## 14. Ambiguity / Clarification

* semantic ambiguity:
* clarification state:
* user follow-up:
* current behavior:

## 15. Plan Repair

* JSON repair:
* schema repair:
* validation repair:
* scientific capability repair:
* retry limits:

## 16. Result Interpretation

* existing deterministic summaries:
* LLM summaries:
* structured context:
* hallucination guardrails:
* next-step recommendations:

## 17. Frontend Planner UX

* prompt:
* resource selection:
* plan inspection:
* validation:
* execution:
* timeline:
* edit:
* retry:
* cancel:
* artifacts:

## 18. Security Boundary

* arbitrary Python:
* shell:
* direct library execution:
* unknown tools:
* invalid params:
* prompt injection:
* artifact content:
* external network:

## 19. Planner Test Coverage

* Mock:
* LLM fixture:
* PlanValidator:
* runtime:
* service-backed:
* browser:
* real-provider gated tests:

## 20. Planner Maturity

使用正式定义：

Level 0–5

或 audit文档中定义的等价体系。

给出：

`CURRENT_LEVEL = ...`

和证据。

## 21. Gap Matrix

按：

* READY
* REUSABLE_FOUNDATION
* PARTIAL
* MISSING_10L
* DEFER_10M
* DEFER_10N
* FUTURE
* NOT_NEEDED

总结。

## 22. Recommended Phase 10L Scope

### 10L-1

* recommendation:
* contract need:
* exact problem:

### 10L-2

* planner gap:
* capability metadata:
* profile context:
* selection:

### 10L-3

* current multi-tool baseline:
* required evolution:
* dependency/artifact binding:

### 10L-4

* current interpretation baseline:
* required work:

### 10L-5

* natural-language evidence recommendation:

## 23. Reviewer Decisions Required

列真正需要 reviewer 决策的问题。

不要自行决定。

## 24. Production Behavior Changes

必须输出：

```text
Production Planner Behavior Changes:
NONE
```

如果不是 NONE：

说明为什么，并且本阶段原则上不得 PASS。

## 25. Files Changed

只能主要是：

* docs
* persistent
* TASKS
* result/evidence
* tests if audit-only

## 26. Checks

* git diff --check:
* uv lock:
* backend:
* frontend:
* typecheck:
* build:
* Planner tests:
* PlanValidator:
* service-backed:
* no-skipped:
* docs:
* TASKS:
* security:

## 27. Security

必须：

```text
REAL_LLM_CALLS = 0
NO_PHASE10L0_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

或 repository真实等价 marker。

## 28. Commit / CI

### Audit Commit

* commit:
* exact SHA:
* CI:

### Completion Record

* commit:
* exact SHA:
* CI:

## 29. Queue State

必须：

```text
Phase 10L-0:
ARCHIVED

Phase 10L-1:
REVIEWER_GATE / AWAITING REVIEWER PROMPT
```

## 30. Whether Allowed to Enter Phase 10L-1 Automatically

必须写：

```text
NO
```

理由：

Phase 10L-1 requires reviewer review of the real Phase 10L-0 architecture audit.

## 31. Next Action

必须写：

> Return Phase 10K-5 and Phase 10L-0 results to the reviewer for Phase 10L architecture decision and Phase 10L-1 execution prompt.

不得开始实现。

---

# 108. PASS 标准

Phase 10L-0 只有全部满足才能 PASS：

1. Phase 10K 完整 CLOSED。
2. 真实审计 repository，不只读 docs。
3. AnalysisPlan contract审计完成。
4. multi-tool真实能力审计完成。
5. dependency representation审计完成。
6. artifact binding审计完成。
7. Mock Planner routing审计完成。
8. keyword dependency明确。
9. DataProfile use明确。
10. LLM Planner context明确。
11. Tool Registry planner metadata明确。
12. PlanValidator maturity明确。
13. params selection机制明确。
14. ambiguity behavior明确。
15. clarification能力明确。
16. plan repair能力明确。
17. runtime boundary明确。
18. Planner无法任意执行代码得到确认。
19. frontend Planner UX审计完成。
20. result interpretation baseline明确。
21. security boundary审计完成。
22. caps审计完成。
23. tests/evidence coverage审计完成。
24. representative prompts完成。
25. Planner maturity level明确。
26. Agent/Planner Gap Matrix完成。
27. 10L-1 scope recommendation完成。
28. 10L-2 scope recommendation完成。
29. 10L-3 scope recommendation完成。
30. 10L-4 scope recommendation完成。
31. 10L-5 evidence recommendation完成。
32. reviewer decision list完成。
33. 无 production Planner behavior change。
34. 无 AnalysisPlan schema change。
35. 无 Tool Registry contract change。
36. 无 PlanValidator behavior change。
37. 无 Runtime behavior change。
38. 无新 dependency。
39. 无真实 LLM call。
40. 无 external network。
41. secret scan PASS。
42. regression checks PASS。
43. audit exact-SHA CI success。
44. completion-record exact-SHA CI success。
45. 10L-0 archived。
46. 10L-1 NOT automatically queued。
47. reviewer gate明确。
48. origin/master == HEAD。
49. git clean。

---

现在开始。

第一步：

**不要修改 Planner implementation。**

先输出：

# Phase 10L-0 Entry / Current Planner Architecture Audit

必须基于真实代码回答：

1. Phase 10K 是否正式 COMPLETE？
2. 当前 Planner 入口在哪里？
3. Mock Planner 如何选择 tool？
4. LLM Planner 实际收到什么 context？
5. DataProfile 2.0 是否真的进入 Mock Planner？
6. DataProfile 2.0 是否真的进入 LLM Planner？
7. Tool Registry 向 Planner 暴露哪些 metadata？
8. AnalysisPlan 是 single-tool 还是 multi-tool？
9. 如果是 multi-tool，runtime 是否真的支持？
10. 是否存在 dependencies？
11. 是否支持 previous-artifact binding？
12. PlanValidator 到底验证到哪一层？
13. semantic readiness 在 Planner/Validator/Adapter 哪一层检查？
14. ambiguous semantics 当前如何处理？
15. 是否已有 structured intent object？
16. 是否已有 plan repair？
17. 是否已有 scientific result interpretation？
18. frontend 能否 inspect/edit plan？
19. 当前 Planner 最准确的 maturity classification 是什么？
20. Phase 10L-1～10L-5 各自真正需要解决什么？

Audit 完成后继续完成：

* Gap Matrix
* architecture docs
* persistent updates
* tests
* commit
* CI
* completion record
* archive

然后强制停止。

最终状态必须是：

**Phase 10L-1 = REVIEWER_GATE / AWAITING REVIEWER PROMPT**

---END---
