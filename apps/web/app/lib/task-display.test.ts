import { describe, expect, it } from "vitest";
import { taskHasEnded, taskIsInProgress, taskRecordTitle, taskResultSummary, taskStatusLabel } from "./task-display";

describe("task presentation", () => {
  it.each(["created", "queued", "running", "CANCELING", "cancel_requested"])("keeps %s in progress until a terminal status arrives", (status) => {
    expect(taskIsInProgress(status)).toBe(true);
    expect(taskHasEnded(status)).toBe(false);
  });
  it.each(["completed", "succeeded", "failed", "partial_success", "cancelled", "canceled"])("recognizes %s as an ended task", (status) => {
    expect(taskHasEnded(status)).toBe(true);
    expect(taskIsInProgress(status)).toBe(false);
  });
  it("does not pretend missing or unknown statuses are completed", () => {
    for (const status of [null, undefined, "", "unexpected"]) {
      expect(taskHasEnded(status)).toBe(false);
      expect(taskIsInProgress(status)).toBe(false);
      expect(taskStatusLabel(status)).toBe("状态待确认");
    }
    expect(taskStatusLabel(" FAILED ")).toBe("失败");
  });
  it("uses the original question or an honest creation-time fallback", () => {
    expect(taskRecordTitle({ researchQuestion: "  比较材料结构  " })).toBe("比较材料结构");
    expect(taskRecordTitle({ createdAt: "2026-09-05T00:00:00Z" })).toMatch(/09\/05.*的研究$/);
    expect(taskRecordTitle({ createdAt: "unavailable" })).toBe("研究任务");
    expect(taskRecordTitle({})).toBe("研究任务");
  });
  it("summarizes real outputs without technical names or zero-count clutter", () => {
    expect(taskResultSummary({ jobStatus: "failed", artifactCount: 2, interpretationCount: 1 })).toBe("2 项结果 · 1 份解读");
    expect(taskResultSummary({ jobStatus: "completed", artifactCount: 1, interpretationCount: 0 })).toBe("1 项结果");
    expect(taskResultSummary({ jobStatus: "queued", artifactCount: 0, interpretationCount: 0 })).toBe("正在等待结果");
    expect(taskResultSummary({ jobStatus: "failed", artifactCount: 0, interpretationCount: 0 })).toBe("暂无可查看的结果");
  });
});
