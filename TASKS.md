# Task Queue

---TASK---
状态：待处理
# Phase 10J-7：Electronic Band / DOS Contract

目标：在不实现 parser、adapter、Tool Registry、Planner、Runtime 或前端产品的前提下，冻结电子能带与电子 DOS 的 canonical inert contracts。

必须覆盖：

* structure、calculation、reciprocal lattice、k-point、BZ/k-path identity；
* reciprocal units 与 physics-`2*pi` policy；
* energy unit/reference、Fermi energy、band index、spin、occupation；
* metallicity、direct/indirect gap、degeneracy、crossing、segment discontinuity；
* DOS energy grid、total/spin/projected DOS、units、normalization、integrated-state validation、smearing 与 projection completeness；
* deterministic caps、validation、provenance、security、fixtures、tests、docs、evidence 与 current-HEAD CI。

边界：只消费已有 electronic results；不得运行 DFT/HPC，不得联网获取计算结果，不得实现 Fermi Surface，不得新增 renderer。

Entry criteria 与详细 scope：`docs/phase10j/phase10j7_electronic_band_dos_contract_next_scope.md`。
---END---

---TASK---
状态：待处理
# Phase 10J-8：Electronic Band / DOS Parser & Adapter

目标：在 J-7 contract 通过后，审计并选择 bounded source-format first batch，实现 format detection、parser、canonical conversion、严格 public tool identities/params、Tool Registry、PlanValidator、Planner、QueueWorkerRuntime、inert artifacts、parse report、manifest、summary、recipe、API evidence、tests 与 current-HEAD CI。

边界：不得承诺未经审计的格式；不得运行电子结构计算、外部 API、notebook/script 或实现 Fermi Surface。
---END---

---TASK---
状态：待处理
# Phase 10J-9：Electronic Band + DOS Product / Brillouin Zone Link

目标：基于 J-7/J-8 validated artifacts，实现 electronic band、DOS、projected DOS、spin channels、Fermi line、shared energy axis、gap/metal behavior、table、JSON、PNG、mobile、accessibility、browser matrix，以及与 Phase 10I BZ 的双向 linking。

边界：必须复用 canonical reciprocal-space identity，不得重新定义 BZ/k-path semantics，不得运行 DFT，不得实现 Fermi Surface extraction。
---END---

---TASK---
状态：待处理
# Phase 10J-10：Fermi Surface Contract

目标：定义 regular validated 3D k-mesh、reciprocal coordinates、periodicity、first-BZ mapping、band/spin identity、energy reference、Fermi energy、iso-energy、interpolation、degeneracy、multiple sheets、mesh completeness、topology identity、caps、validation、provenance 与 security contracts。

边界：普通 1D high-symmetry band path 必须 typed reject；本阶段不得实现 extraction 或 renderer。
---END---

---TASK---
状态：待处理
# Phase 10J-11：Fermi Surface Extraction / Renderer

目标：在 J-10 contract 通过后，实现 bounded `E(k)-E_F` periodic scalar extraction、deterministic surface sheets、first-BZ clipping、BZ overlay、reciprocal axes、opacity、picking、inspector、camera、clipping、PNG、JSON fallback、Three.js reuse、GPU/resource caps、lifecycle 与 browser evidence。

边界：不得从 1D path 伪造 surface，不得运行 DFT、外部 API、notebook/script 或加载 artifact code/assets。
---END---

---TASK---
状态：待处理
# Phase 10J-12：Electronic / Fermi Evidence Closure

目标：完成 semiconductor、metal、spin-polarized、multiple-sheet、degeneracy、insufficient-mesh rejection、BZ clipping、periodic seams、deterministic extraction、API、Chromium/Firefox/WebKit、mobile、accessibility、performance、GPU caps、context loss、network、secret、service-backed、no-skipped 与 current-HEAD CI closure。

边界：只做 reference validation、hardening 与 evidence closure；不得扩大 scientific scope。
---END---
