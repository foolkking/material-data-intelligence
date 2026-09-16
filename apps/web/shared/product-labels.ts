export function scientistProjectLabel(
  name: string | null | undefined,
  projectId?: string | null,
): string {
  const value = String(name || "").trim();
  const identity = String(projectId || "").trim();
  if (!value || (identity && value === identity)) return "材料研究项目";
  return value;
}

export function scientistDatasetLabel(
  name: string | null | undefined,
  datasetId?: string | null,
): string {
  const value = String(name || "").trim();
  const identity = String(datasetId || "").trim();
  if (!value || (identity && value === identity)) return "当前项目材料数据";
  return value;
}
