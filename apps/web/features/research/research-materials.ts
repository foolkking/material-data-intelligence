import { admitDatasetResource, promoteDatasetTable, getResearchSourceVersion, type ResearchSourceResource } from "../../app/lib/planner-api";
import type { Agent2ScientificObjectRef, Agent2ScientificSelection } from "../../app/lib/agent2-research-api";

export type ResearchMaterial = { ref: Agent2ScientificObjectRef; datasetId?: string; resourceId?: string; sourceHash?: string };
export type ResearchMaterials = { items: ResearchMaterial[]; selections: Agent2ScientificSelection[] };
export const materialTypes: Record<string, string> = {
  DataFrame: "数据表", Structure: "晶体结构", Trajectory: "原子轨迹", ElectronicBand: "电子能带",
  ElectronicDos: "电子态密度", PhononBand: "声子能带", PhononDos: "声子态密度", VolumetricData: "体数据",
  "materials.table": "数据表", "structure.crystal": "晶体结构", "trajectory.atomic": "原子轨迹",
  "electronic.band_structure": "电子能带", "electronic.dos": "电子态密度", "phonon.band_structure": "声子能带",
  "phonon.dos": "声子态密度", "volumetric.field": "体数据", "diffraction.xrd.experimental": "实验 XRD",
};
const admittedTypes: Record<string, string[]> = {
  DataFrame: ["materials.table", "diffraction.xrd.experimental"], Structure: ["structure.crystal"],
  Trajectory: ["trajectory.atomic"], ElectronicBand: ["electronic.band_structure"], ElectronicDos: ["electronic.dos"],
  PhononBand: ["phonon.band_structure"], PhononDos: ["phonon.dos"], VolumetricData: ["volumetric.field"],
};
export const materialKey = (ref: Agent2ScientificObjectRef) => JSON.stringify([ref.project_id, ref.object_id, ref.version_id]);

export async function resolveMaterialSource(item: ResearchMaterial, signal: AbortSignal): Promise<ResearchMaterial> {
  if (item.datasetId && item.resourceId && item.sourceHash) return item;
  const version = await getResearchSourceVersion(item.ref.object_id, item.ref.version_id, signal);
  signal.throwIfAborted();
  if (version.id !== item.ref.version_id || version.scientific_object_id !== item.ref.object_id || version.object_type !== item.ref.object_type) throw new Error("材料版本不一致。");
  let refs = version.source_resource_refs_json;
  if (typeof refs === "string") refs = JSON.parse(refs);
  if (!Array.isArray(refs) || refs.some(r => r.project_id !== item.ref.project_id)) throw new Error("材料来源不一致。");
  const sources = refs.filter(r => typeof r.dataset_id === "string" && typeof r.resource_id === "string");
  if (sources.length !== 1) return item;
  return { ...item, datasetId: sources[0].dataset_id, resourceId: sources[0].resource_id, sourceHash: version.semantic_hash };
}

export function validateMaterials(value: ResearchMaterials, projectId: string): ResearchMaterials {
  if (!value || !Array.isArray(value.items) || !Array.isArray(value.selections) || value.items.length > 64 || value.selections.length > 64) throw new Error("材料选择无法恢复，请重新选择。");
  const seen = new Set<string>();
  for (const item of value.items) {
    const ref = item?.ref;
    if (!ref || ref.project_id !== projectId || ![ref.object_id, ref.version_id, ref.object_type].every(x => typeof x === "string" && x.length > 0) || seen.has(materialKey(ref))) throw new Error("材料的项目或精确版本不一致，请重新选择。");
    seen.add(materialKey(ref));
  }
  if (new Set(value.items.map(x => x.datasetId).filter(Boolean)).size > 8) throw new Error("一次最多选择 8 个数据集。");
  for (const selection of value.selections) {
    if (!selection?.object_ref || !seen.has(materialKey(selection.object_ref)) || selection.contract_version !== "1.0") throw new Error("科学点选与材料版本不一致，请重新选择。");
  }
  return value;
}

export function materialsContext(value: ResearchMaterials, projectId: string) {
  validateMaterials(value, projectId);
  if (!value.items.length) throw new Error("请至少选择一份材料数据。");
  const refs = value.items.map(x => x.ref);
  return { active_object_refs: refs, selection_refs: refs, explicit_object_refs: refs,
    scientific_selections: value.selections, explicit_result_ids: [] as string[], explicit_finding_refs: [] as string[] };
}

export async function admitResearchMaterial(projectId: string, source: ResearchSourceResource, signal: AbortSignal): Promise<ResearchMaterial> {
  signal.throwIfAborted();
  const response = source.objectType === "DataFrame"
    ? await promoteDatasetTable(projectId, source.datasetId, source.objectId)
    : await admitDatasetResource(projectId, source.datasetId, source.objectId, source.displayName);
  signal.throwIfAborted();
  const { object, version } = response;
  let refs = version?.source_resource_refs_json;
  if (typeof refs === "string") { try { refs = JSON.parse(refs); } catch { refs = null; } }
  if (!object?.id || !version?.id || object.project_id !== projectId || version.scientific_object_id !== object.id ||
      !admittedTypes[source.objectType]?.includes(object.object_type || "") ||
      !source.objectHash || version.semantic_hash !== source.objectHash ||
      !Array.isArray(refs) || !refs.some(r => r?.project_id === projectId && r.dataset_id === source.datasetId && r.resource_id === source.objectId)) {
    throw new Error("来源或版本已变化，请重新读取材料列表后再选择。");
  }
  return { datasetId: source.datasetId, resourceId: source.objectId, sourceHash: source.objectHash, ref: {
    project_id: projectId, object_id: object.id, version_id: version.id, object_type: object.object_type!,
    display_name: source.displayName || object.display_name,
  } };
}
