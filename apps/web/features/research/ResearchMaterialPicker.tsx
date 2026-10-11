"use client";

import { useEffect, useRef, useState } from "react";
import { ProductModal } from "../../shared/ui/ObjectManagement";
import { getDatasetResearchSources, type ResearchSourceResource } from "../../app/lib/planner-api";
import { readSessionRequest } from "./session-management";
import { admitResearchMaterial, materialKey, materialTypes, resolveMaterialSource, validateMaterials, type ResearchMaterial, type ResearchMaterials } from "./research-materials";
import styles from "./ResearchMaterials.module.css";

type Dataset = { datasetId: string; name: string; status: string };
export function ResearchMaterialPicker({ projectId, datasets, loadInitial, onApply, onClose, returnFocus }: {
  projectId: string; datasets: Dataset[]; loadInitial: (signal: AbortSignal) => Promise<ResearchMaterials>;
  onApply: (value: ResearchMaterials) => void; onClose: () => void; returnFocus: HTMLElement | null;
}) {
  const [selection, setSelection] = useState<ResearchMaterials>({ items: [], selections: [] });
  const [initialState, setInitialState] = useState("loading");
  const [initialRetry, setInitialRetry] = useState(0);
  const initialReader = useRef(loadInitial);
  const [datasetId, setDatasetId] = useState(datasets[0]?.datasetId || "");
  const [query, setQuery] = useState("");
  const [resources, setResources] = useState<ResearchSourceResource[]>([]);
  const [catalogState, setCatalogState] = useState("loading");
  const [catalogRetry, setCatalogRetry] = useState(0);
  const [error, setError] = useState("");
  const [pending, setPending] = useState("");
  const operation = useRef<AbortController | null>(null);
  const resolved = useRef(new Map<string, ResearchMaterial>());
  useEffect(() => () => operation.current?.abort(), []);
  useEffect(() => {
    const controller = new AbortController();
    setInitialState("loading");
    void readSessionRequest(async signal => {
      const value = validateMaterials(await initialReader.current(signal), projectId);
      const items: ResearchMaterial[] = [];
      for (let offset = 0; offset < value.items.length; offset += 4) {
        signal.throwIfAborted();
        items.push(...await Promise.all(value.items.slice(offset, offset + 4).map(item => resolveMaterialSource(item, signal))));
      }
      return { ...value, items };
    }, controller.signal).then(value => {
      if (controller.signal.aborted) return;
      setSelection(validateMaterials(value, projectId)); setInitialState("ready");
    }).catch(() => { if (!controller.signal.aborted) setInitialState("error"); });
    return () => controller.abort();
  }, [projectId, initialRetry]);
  useEffect(() => {
    const controller = new AbortController();
    setResources([]); setCatalogState(datasetId ? "loading" : "ready"); setQuery("");
    if (datasetId) void readSessionRequest(signal => getDatasetResearchSources(datasetId, signal), controller.signal).then(value => {
      if (controller.signal.aborted) return;
      if (value.projectId !== projectId || value.datasetId !== datasetId || !Array.isArray(value.resources) ||
          value.resources.some(r => r.datasetId !== datasetId || !r.objectId || !r.objectHash || !materialTypes[r.objectType]) ||
          new Set(value.resources.map(r => r.objectId)).size !== value.resources.length) throw new Error("Source catalog mismatch");
      setResources(value.resources); setCatalogState("ready");
    }).catch(() => { if (!controller.signal.aborted) setCatalogState("error"); });
    return () => controller.abort();
  }, [projectId, datasetId, catalogRetry]);
  const sourceKey = (source: ResearchSourceResource) => JSON.stringify([source.datasetId, source.objectId, source.objectHash]);
  function selected(source: ResearchSourceResource) {
    const saved = resolved.current.get(sourceKey(source));
    return selection.items.find(item => saved ? materialKey(item.ref) === materialKey(saved.ref)
      : item.datasetId === source.datasetId && item.resourceId === source.objectId && item.sourceHash === source.objectHash);
  }
  function remove(item: ResearchMaterial) {
    setSelection(current => ({ items: current.items.filter(x => materialKey(x.ref) !== materialKey(item.ref)),
      selections: current.selections.filter(x => materialKey(x.object_ref) !== materialKey(item.ref)) }));
    setError("");
  }
  async function toggle(source: ResearchSourceResource) {
    if (operation.current || initialState !== "ready") return;
    const existing = selected(source);
    if (existing) { remove(existing); return; }
    const controller = new AbortController(); operation.current = controller;
    setPending(sourceKey(source)); setError("");
    try {
      const item = resolved.current.get(sourceKey(source)) || await readSessionRequest(signal => admitResearchMaterial(projectId, source, signal), controller.signal);
      if (controller.signal.aborted) return;
      resolved.current.set(sourceKey(source), item);
      const items = [...selection.items.filter(x => materialKey(x.ref) !== materialKey(item.ref)), item];
      setSelection(validateMaterials({ ...selection, items }, projectId));
    } catch (reason) {
      if (!controller.signal.aborted) setError(reason instanceof Error && /来源|版本|最多|选择/.test(reason.message)
        ? reason.message : "暂时无法取得此材料的版本，请重试。已选材料仍保留。");
    } finally {
      if (operation.current === controller) { operation.current = null; setPending(""); }
    }
  }
  const shown = resources.filter(r => `${r.displayName || ""} ${materialTypes[r.objectType] || r.objectType}`.toLocaleLowerCase().includes(query.toLocaleLowerCase()));
  return <ProductModal title="选择材料" eyebrow="" onClose={onClose} returnFocus={returnFocus} footer={<>
    <button type="button" className="product-secondary-action" onClick={onClose}>取消</button>
    <button type="button" className="product-primary-action" disabled={initialState !== "ready" || Boolean(pending) || !selection.items.length}
      onClick={() => onApply(validateMaterials(selection, projectId))}>使用所选材料{selection.items.length ? `（${selection.items.length}）` : ""}</button>
  </>}>
    <div className={styles.picker}>
      {initialState === "loading" ? <p role="status">正在读取当前来源…</p> : initialState === "error" ? <div role="alert"><p>当前来源暂时无法读取。</p><button type="button" className="product-secondary-action" onClick={() => setInitialRetry(x => x + 1)}>重新读取当前来源</button></div> : <>
        {selection.items.length ? <section aria-label="已选材料" className={styles.selected}>
          <h3>已选 {selection.items.length} 项</h3>
          <ul>{selection.items.map(item => <li key={materialKey(item.ref)}>
            <span><strong>{item.ref.display_name || materialTypes[item.ref.object_type] || item.ref.object_type}</strong><span>{materialTypes[item.ref.object_type]} · 版本 {item.ref.version_id.slice(0, 8)}</span></span>
            <button type="button" disabled={Boolean(pending)} aria-label={`移除 ${item.ref.display_name || item.ref.object_id}`} onClick={() => remove(item)}>×</button>
          </li>)}</ul>
        </section> : null}
        <div className={styles.filters}>
          <label>数据集<select value={datasetId} disabled={Boolean(pending)} onChange={e => setDatasetId(e.target.value)}>
            {datasets.map(d => <option key={d.datasetId} value={d.datasetId}>{d.name}</option>)}
          </select></label>
          <label>查找文件<input type="search" value={query} onChange={e => setQuery(e.target.value)} /></label>
        </div>
        {catalogState === "loading" ? <p role="status">正在读取材料…</p> : catalogState === "error" ? <div role="alert"><p>材料列表暂时无法读取。</p><button type="button" className="product-secondary-action" onClick={() => setCatalogRetry(x => x + 1)}>重新读取材料列表</button></div>
          : !resources.length ? <p>此数据集还没有可用于研究的数据。</p> : !shown.length ? <p>没有匹配的文件。</p> : <ul className={styles.options} aria-label="可选材料">
            {shown.map(source => <li key={source.objectId}><label>
              <input type="checkbox" checked={Boolean(selected(source))} disabled={Boolean(pending)} onChange={() => void toggle(source)} />
              <span><strong>{source.displayName || source.objectId}</strong><span>{materialTypes[source.objectType]}{pending === sourceKey(source) ? " · 正在读取版本…" : ""}</span></span>
            </label></li>)}
          </ul>}
        {error ? <div role="alert" className={styles.error}><p>{error}</p><button type="button" className="product-link-button" onClick={() => { resolved.current.clear(); setCatalogRetry(x => x + 1); setError(""); }}>重新读取材料列表</button></div> : null}
      </>}
    </div>
  </ProductModal>;
}
