import { isResearchCancellationPending, RESEARCH_CANCELLING_LABEL } from "./research-status";

export function taskStatusLabel(status: string | null | undefined): string {
  if (isResearchCancellationPending(status)) return RESEARCH_CANCELLING_LABEL;
  return ({
    created: "已创建", queued: "排队中", running: "运行中",
    cancelled: "已取消", canceled: "已取消", completed: "已完成",
    succeeded: "已完成", partial_success: "部分完成", failed: "失败",
  } as Record<string, string>)[String(status || "").trim().toLowerCase()] || "状态待确认";
}

export function taskIsInProgress(status: string | null | undefined): boolean {
  return isResearchCancellationPending(status) || ["created", "queued", "running"].includes(String(status || "").trim().toLowerCase());
}

export function taskHasEnded(status: string | null | undefined): boolean {
  return ["cancelled", "canceled", "completed", "succeeded", "partial_success", "failed"].includes(String(status || "").trim().toLowerCase());
}

export function taskRecordTitle(task: { researchQuestion?: string | null; createdAt?: string | null }): string {
  if (task.researchQuestion?.trim()) return task.researchQuestion.trim();
  const date = task.createdAt ? new Date(task.createdAt) : null;
  if (!date || Number.isNaN(date.getTime())) return "研究任务";
  const time = date.toLocaleString("zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" });
  return `${time} 的研究`;
}

export function taskResultSummary(task: { jobStatus: string | null; artifactCount: number; interpretationCount: number }): string {
  const parts = [task.artifactCount > 0 ? `${task.artifactCount} 项结果` : null, task.interpretationCount > 0 ? `${task.interpretationCount} 份解读` : null].filter(Boolean);
  if (parts.length) return parts.join(" · ");
  return taskIsInProgress(task.jobStatus) ? "正在等待结果" : "暂无可查看的结果";
}
