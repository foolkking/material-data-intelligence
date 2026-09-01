export type ResearchRunDisplaySource = {
  userQuestion?: string | null;
  toolIds?: string[];
  artifactTypes?: string[];
};

export type ResearchRunStatusSource = {
  status?: string | null;
  researchTurnStatus?: string | null;
};

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
  if (tools.includes("correlation") || artifacts.includes("correlation")) return "形成能与带隙的相关关系";
  if (tools.includes("coordination") || tools.includes("local_environment") || artifacts.includes("coordination") || artifacts.includes("local_environment")) return "局部配位环境分析";
  if (tools.includes("scatter")) return "材料属性关系";
  if (tools.includes("histogram")) return "材料属性分布";
  if (tools.includes("numeric_summary")) return "材料属性统计摘要";
  if (tools.includes("composition") || artifacts.includes("composition_space")) return "材料组成空间分析";
  if (tools.includes("regression") || artifacts.includes("regression")) return "材料属性回归评估";
  if (tools.includes("classification") || artifacts.includes("classification")) return "材料分类评估";
  if (tools.includes("uncertainty") || artifacts.includes("uncertainty")) return "预测不确定性评估";
  if (run.userQuestion?.trim()) return run.userQuestion.trim();
  return "已完成的材料数据分析";
}
