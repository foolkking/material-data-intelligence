# MDI V0 — M2 FINAL CLOSEOUT — attempt-03

状态：处理中
范围：仅补齐 M2-006 浏览器重连和 M2-007 已有证据的恢复耗时计算。

保护边界：
- M2 attempt-01/02 sealed evidence immutable；不得重跑已接受 F01/F02/F04/F05/F06/F07/F08、Result-before-next-stage、DB failure、client disconnect、duplicate/delayed delivery。
- 不修改生产代码、科学工具、leases/fencing、队列、Artifact/Result/Interpretation 语义。
- 不启动 M3。
- 使用 M2 attempt-02 的隔离命名空间；如需切换进程，先核对 PID、启动时间、命令、cwd、PPID、角色、namespace/端口，关闭并确认旧任务进程退出、端口和资源释放后再启动新进程；共享/canonical 服务和未知 PID 不得停止。

执行目标：
1. 读取当前前端 API 路由方式，记录 browser_reconnect_transport_analysis.json。
2. 不使用新的 Next dev 编译作为默认方案；优先用资格专属 loopback reverse proxy，复用真实当前前端静态资源，并将 /api 路由到 M2 attempt-03/复用的隔离 API。
3. 选择 attempt-02 已持久化 Result-before-next-stage 的精确 Project/Research/Turn/Result/ObjectVersion，先浏览器打开并截图 before_reconnect.png；关闭浏览器会话；用全新浏览器会话经正常产品 UI 重开同一路由并截图 after_reconnect.png。
4. 用 API/DB 快照机械证明 Project、Turn、Result、source ObjectVersion、ToolCall/ScientificResult 计数不变，browser reconnect recomputation=0。
5. 从 attempt-02 已封存的权威时间戳计算所有适用故障的 failure_start_at、recovery_complete_at、elapsed_recovery_seconds；不得使用 NOT_EXPOSED_BY_CURRENT_INSTRUMENTATION 代替可计算值。必要时只对缺少时间戳的单一案例做 timing-only replay。
6. 保留 attempt-02 frontend native OOM 为 FAILED_QUALIFICATION_METHOD，不隐藏、不当作产品恢复失败。

必须生成：
phase_return.json
browser_reconnect_transport_analysis.json
browser_reconnect_recovery.json
browser/before_reconnect.png
browser/after_reconnect.png
recovery_timeline_summary.json
recovery_timeline_validation.json
validate_m2_semantic_coherence.py
service_state.txt
以及复用证据的 exact provenance/hash 记录。

状态门：
- 所有 M2-001...M2-008 仅在证据真实满足时关闭；M2-006 需真实正常产品 UI + M2 隔离 API 状态 + 新浏览器会话；M2-007 需所有适用故障时间算术校验 PASS。
- 若浏览器路径或任何时间戳仍无法真实完成，返回 PARTIAL，不伪造截图或耗时。
- 官方校验仅针对 attempt-03：validate_m2_semantic_coherence.py、tools/validate_return.py --seal、tools/build_review_bundle.py，输出 E:\mdi-v0-review\M2_attempt-03.zip。
- 最终停止在 M3 之前。
