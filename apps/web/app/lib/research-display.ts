import { projectScienceNames } from "./project-science-labels";

export type ResearchRunDisplaySource = {
  userQuestion?: string | null;
  toolIds?: string[];
  artifactTypes?: string[];
};

export type ResearchRunStatusSource = {
  status?: string | null;
  researchTurnStatus?: string | null;
};

export type ResearchSourceDataset = { datasetId: string; name: string };

export function researchRunSourceDatasets(
  run: { datasetId?: string | null; sourceDatasetIds?: readonly string[] },
  datasets: readonly ResearchSourceDataset[],
): ResearchSourceDataset[] {
  const ids = run.sourceDatasetIds === undefined
    ? run.datasetId ? [run.datasetId] : []
    : run.sourceDatasetIds;
  const names = new Map(datasets.map((dataset) => [dataset.datasetId, dataset.name]));
  return [...new Set(ids)].map((datasetId) => ({
    datasetId,
    name: names.has(datasetId) ? names.get(datasetId)?.trim() || "未命名数据" : "来源数据不可用",
  }));
}

export function researchRunFailureMessage(events: ReadonlyArray<{
  eventType?: string;
  message?: string | null;
  payload?: Record<string, unknown> | null;
}>): string {
  const failure = [...events].reverse().find((event) =>
    event.eventType === "job.failed" || event.eventType === "tool.failed",
  );
  const message = failure?.message || "";
  const code = String(failure?.payload?.errorCode || failure?.payload?.error_code || message.split(":", 1)[0]).toUpperCase();
  if (code === "TOOL_INPUT_INVALID") {
    return message.includes("Requested target column does not exist")
      ? "分析所需的目标列不存在。请打开数据确认列名，再修改问题重试。"
      : "分析输入未通过工具校验。请确认所选数据与问题中的参数后重试。";
  }
  if (message === "Requested DataProfile is unavailable for this dataset.") {
    return "本次分析需要的数据描述无法读取。请打开数据检查导入状态后重试。";
  }
  return "本次分析执行失败。当前记录没有可展示的具体原因；可检查数据后修改问题重试。";
}

export function researchRunStatusLabel(run: ResearchRunStatusSource) {
  const status = String(run.researchTurnStatus || run.status || "")
    .trim()
    .toUpperCase();
  if (["COMPLETED", "SUCCEEDED"].includes(status)) return "分析完成";
  if (["PARTIAL", "PARTIAL_SUCCESS"].includes(status)) return "部分完成";
  if (status === "FAILED") return "分析失败";
  if (["CANCELED", "CANCELLED"].includes(status)) return "分析已取消";
  if (status === "ANSWERED") return "回答完成";
  if (status === "CLARIFICATION_REQUIRED") return "等待补充信息";
  if (status === "UNSUPPORTED") return "当前请求不受支持";
  return "分析进行中";
}

export function researchRunTitle(run: ResearchRunDisplaySource) {
  if (run.toolIds?.length && run.toolIds.every(id => projectScienceNames[id])) return [...new Set(run.toolIds.map(id => projectScienceNames[id]))].join("、");
  const tools = (run.toolIds || []).join(" ").toLowerCase();
  const artifacts = (run.artifactTypes || []).join(" ").toLowerCase();
  const hasTrajectoryMsd = tools.includes("trajectory.msd") || artifacts.includes("trajectory_msd");
  const hasTrajectoryDiffusion = tools.includes("trajectory.diffusion") || artifacts.includes("trajectory_diffusion");
  if (tools.includes("experimental_xrd")) return "实验与理论 XRD 峰比较";
  if (tools.includes("structure.rdf")) return "静态结构径向分布函数（RDF）";
  if (hasTrajectoryMsd && hasTrajectoryDiffusion) return "均方位移（MSD）与轨迹扩散";
  if (hasTrajectoryDiffusion) return "轨迹扩散分析";
  if (hasTrajectoryMsd) return "均方位移（MSD）";
  if (tools.includes("trajectory.rdf") || artifacts.includes("trajectory_rdf")) return "轨迹径向分布函数（RDF）";
  if (tools.includes("trajectory")) return "AIMD 轨迹分析";
  if (tools.includes("phonon")) return "声子色散与态密度";
  if (tools.includes("electronic")) return "电子能带与态密度";
  if (tools.includes("correlation") || artifacts.includes("correlation")) return run.userQuestion?.trim() || "材料属性相关性分析";
  if (tools.includes("coordination") || tools.includes("local_environment") || artifacts.includes("coordination") || artifacts.includes("local_environment")) return "局部配位环境分析";
  if (tools.includes("scatter")) return "材料属性关系";
  if (tools.includes("histogram")) return "材料属性分布";
  if (tools.includes("numeric_summary")) return "材料属性统计摘要";
  if (tools.includes("composition") || artifacts.includes("composition_space")) return "材料组成空间分析";
  if (tools.includes("regression") || artifacts.includes("regression")) return "材料属性回归评估";
  if (tools.includes("classification") || artifacts.includes("classification")) return "材料分类评估";
  if (tools.includes("uncertainty") || artifacts.includes("uncertainty")) return "预测不确定性评估";
  if (run.userQuestion?.trim()) return run.userQuestion.trim();
  return "材料数据分析";
}
