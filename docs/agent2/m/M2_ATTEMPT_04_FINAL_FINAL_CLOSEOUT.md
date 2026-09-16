# MDI V0 — M2 attempt-04 final final closeout

本任务只补齐 M2-007 的五个 timing-only replay：F05、F07、F08、Interpretation failure recovery、API restart。所有技术语义与其他 M2 证据按 sealed attempt-02/03 精确哈希复用；不得修改生产代码、不得重跑完整故障 campaign、不得启动 M3。每个 replay 必须在资格隔离命名空间实际捕获 failure_start_at 与 recovery_complete_at，使用 UTC 同时钟并完成算术复核。最终生成 recovery_timeline_summary.json、recovery_timeline_validation.json、五个 replay artifact、phase_return.json，并运行 semantic checker、Completion Pack seal validator 和 bundle builder。
