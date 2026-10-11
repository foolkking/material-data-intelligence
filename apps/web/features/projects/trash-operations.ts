import { bulkDatasetAction, bulkProjectAction, type ProductSearchItem } from "../../app/lib/planner-api";
import { bulkUpdateResearchSessions } from "../../app/lib/product-api";
import { bulkUpdateScientificReportLifecycle } from "../../app/lib/scientific-report-api";
import { bulkUpdateScientificObjects } from "../../app/lib/scientific-viewer-api";

export type TrashKind = Exclude<ProductSearchItem["kind"], "result">;
export const TRASH_KIND_LABELS: Record<TrashKind, string> = {
  project: "项目", dataset: "上传数据", scientific_object: "数据视图", research: "研究", report: "报告",
};
export const trashIdentity = (item: ProductSearchItem) => `${item.kind}:${item.id}`;

/** Bound both transport and response bodies, including adapters that ignore abort. */
export async function trashRequest<T>(perform: (signal: AbortSignal) => Promise<T>, owner: AbortSignal): Promise<T> {
  owner.throwIfAborted();
  const controller = new AbortController();
  let interrupt = (_reason: unknown) => {};
  const interrupted = new Promise<never>((_, reject) => { interrupt = reject; });
  const cancel = () => { controller.abort(); interrupt(new Error("Request cancelled")); };
  owner.addEventListener("abort", cancel, { once: true });
  const timer = setTimeout(() => { controller.abort(); interrupt(new Error("Request timed out")); }, 10_000);
  try {
    return await Promise.race([interrupted, Promise.resolve().then(() => {
      controller.signal.throwIfAborted();
      return perform(controller.signal);
    })]);
  } finally {
    clearTimeout(timer);
    owner.removeEventListener("abort", cancel);
  }
}

function exactIds(actual: string[], expected: string[]) {
  return Array.isArray(actual) && actual.length === expected.length && new Set(actual).size === expected.length && expected.every((id) => actual.includes(id));
}

/** Each service owns its atomic batch; successful siblings can settle immediately. */
export function trashRestoreBatches(items: ProductSearchItem[]) {
  const groups = new Map<string, ProductSearchItem[]>();
  for (const item of items) {
    const group = ["project", "dataset"].includes(item.kind) ? item.kind : `${item.kind}:${item.projectId}`;
    groups.set(group, [...(groups.get(group) || []), item]);
  }
  const chunks = [...groups.values()].flatMap((group) =>
    Array.from({ length: Math.ceil(group.length / 100) }, (_, index) => group.slice(index * 100, (index + 1) * 100)),
  );
  return chunks.map((targets) => ({
    items: targets,
    run: async (signal: AbortSignal) => {
      const { kind, projectId } = targets[0];
      const ids = targets.map((item) => item.id);
      let valid = false;
      if (kind === "project") {
        const r = await bulkProjectAction(ids, "restore", signal);
        valid = r.action === "restore" && r.count === ids.length && exactIds(r.projectIds, ids);
      } else if (kind === "dataset") {
        const r = await bulkDatasetAction(ids, "restore", signal);
        valid = r.action === "restore" && r.count === ids.length && exactIds(r.datasetIds, ids);
      } else if (kind === "research") {
        const r = await bulkUpdateResearchSessions(projectId, ids, "RESTORE", signal);
        valid = r.action === "RESTORE" && r.count === ids.length && exactIds(r.sessionIds, ids);
      } else if (kind === "report") {
        const r = await bulkUpdateScientificReportLifecycle(projectId, ids, "ACTIVE", signal);
        valid = r.lifecycle === "ACTIVE" && r.count === ids.length && exactIds(r.reportIds, ids)
          && r.items.every((item) => item.project_id === projectId && ids.includes(item.report_id));
      } else if (kind === "scientific_object") {
        const r = await bulkUpdateScientificObjects(projectId, ids, "ACTIVE", signal);
        valid = r.project_id === projectId && r.lifecycle === "ACTIVE" && r.count === ids.length
          && exactIds(r.items.map((item) => item.id), ids)
          && r.items.every((item) => item.project_id === projectId && item.lifecycle_status === "ACTIVE");
      }
      if (!valid) throw new Error("Restore response identity mismatch");
    },
  }));
}
