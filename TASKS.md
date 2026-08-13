# Task Queue

---TASK---
Task: Phase 13-3 Documentation + Reproducibility Package
状态：已完成

Scope:
- Reconcile current release documentation against Phase 13-2 Attempt 6 authority.
- Publish the seven-demo human and machine-readable reproducibility package.
- Verify clean-checkout commands, services, migration, links, hashes, claims,
  limitations, security, and cross-platform manifest determinism.
- Preserve production, scientific, provider, scope, and Phase 13-4 boundaries.

Authority:
- Reviewer authorization: Phase 13-3 Documentation + Reproducibility Package.
- Historical gate marker: Phase 13-2 Reviewer Prompt completed by Attempt 6 PASS.
- Entry HEAD: 9f31576dfb09318f073e625bb0cb029657017fd1.
- Phase 13-2 Attempt 6: PASS; exact-SHA CI 31682863560 PASS.

完成时间：2026-08-13 21:29:27 +08:00

修改文件：当前 release docs、七 Demo reproducibility contracts、Phase13-3
evidence/generator/tests、CI manifest parity helper、persistent governance docs。
生产代码与科学行为修改为 0。

修改摘要：完成 current-authority Initial Release documentation、Quick Start、
architecture/API/input-support/limitations/security/provider/troubleshooting，
并发布七 Demo 人类与机器可读复现包。manifest semantic hash 为
`931d6214cb11dbcad628f5b33ea97e043bbfeb54fbccc2f8c87cffebad9537e2`；7/7
Demo、11 个 fixture hash、7 个 prompt hash、claim/limitation/security/link/
private-path/secret gates 均通过。Windows clean-checkout 的 CRLF 漂移已由
UTF8/LF text canonicalization 修复，binary 仍按 raw bytes 处理。

测试结果：backend 1445 passed、1 skipped、51 integration deselected；frontend
460 passed；Phase13 focused 128 passed；service-backed 50 passed、0 skipped；
typecheck/build/uv lock/diff PASS；Chromium/Firefox/WebKit retained browser
replay PASS；Linux/Windows invariant replay 与 Phase13-3 manifest parity PASS。
npm audit = UNAVAILABLE_CONFIGURED_MIRROR_NOT_IMPLEMENTED。

提交/CI：implementation/evidence `c3aabd055e067c5a52a0c0238c625dbc035a96f0`，
exact-SHA CI `31703805747` PASS；completion record follows in this lifecycle commit。

Next phase:
- Phase 13-4 remains REVIEWER_GATE / AWAITING REVIEWER PROMPT.
- PHASE13_4_EXECUTABLE_TASK_CREATED = NO.
---END---
