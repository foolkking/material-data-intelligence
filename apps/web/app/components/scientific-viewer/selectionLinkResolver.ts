import type { ScientificSelection } from "./scientificSelection";

export type SelectionLinkStatus = "LINKED" | "PARTIAL" | "UNSUPPORTED" | "NOT_FOUND";
export type SelectionLinkResult = Readonly<{
  status: SelectionLinkStatus;
  targetLocator: Readonly<Record<string, string | number>> | null;
  message: string;
}>;

export function resolveScientificSelectionLink(selection: ScientificSelection, targetRendererKey: string): SelectionLinkResult {
  const locator = selection.semanticLocator;
  if (/STRUCTURE|PERIODIC_SITE/.test(selection.selectionType) && ["structure-3d", "scientific-table"].includes(targetRendererKey)) {
    return linked(locator, "结构位点已定位到兼容视图。");
  }
  if (/XRD/.test(selection.selectionType) && ["xrd", "scientific-table"].includes(targetRendererKey)) {
    return linked(locator, "XRD 峰位已定位到图谱或峰表。");
  }
  if (/RDF/.test(selection.selectionType) && ["rdf", "scientific-table"].includes(targetRendererKey)) {
    return linked(locator, "RDF 区间已定位到曲线或支持表。");
  }
  if (["EVIDENCE_ITEM", "CLAIM"].includes(selection.selectionType)) {
    return Object.keys(locator).length
      ? Object.freeze({ status: "PARTIAL", targetLocator: locator, message: "已打开对应科学视图；当前证据只提供元数据定位。" })
      : Object.freeze({ status: "NOT_FOUND", targetLocator: null, message: "证据存在，但没有可恢复的交互定位信息。" });
  }
  return Object.freeze({ status: "UNSUPPORTED", targetLocator: null, message: "此选择与目标科学视图没有确定性映射。" });
}

function linked(locator: Readonly<Record<string, string | number>>, message: string): SelectionLinkResult {
  return Object.freeze({ status: "LINKED", targetLocator: locator, message });
}
