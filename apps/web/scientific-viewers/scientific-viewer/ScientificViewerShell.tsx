"use client";

import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import { useId, type ReactNode } from "react";

import type { ScientificSelection } from "./scientificSelection";
import type { ScientificViewerDescriptor } from "./scientificViewerRegistry";

export function ScientificViewerShell({
  title,
  descriptor,
  versionLabel,
  exactVersionId,
  relevance = "CURRENT",
  metadata = {},
  limitations = [],
  selection = null,
  onClearSelection,
  primaryActionHref,
  lifecycleAction,
  children,
}: Readonly<{
  title: string;
  descriptor: ScientificViewerDescriptor;
  versionLabel: string;
  exactVersionId?: string | null;
  relevance?: "CURRENT" | "STALE" | "SOURCE_MISSING" | "INVALIDATED";
  metadata?: Record<string, unknown>;
  limitations?: readonly string[];
  selection?: ScientificSelection | null;
  onClearSelection?: () => void;
  primaryActionHref?: string | null;
  lifecycleAction?: { label: string; onClick: () => void; disabled?: boolean; disabledReason?: string } | null;
  children: ReactNode;
}>) {
  const instanceId = useId().replace(/[^A-Za-z0-9_-]/gu, "");
  const titleId = `scientific-viewer-title-${instanceId || "instance"}`;
  const limitationsId = `viewer-limitations-${instanceId || "instance"}`;
  const metadataEntries = Object.entries(metadata);
  const sourceEntries = metadataEntries.filter(([key]) => isSourceIdentifier(key));
  const properties = metadataEntries.filter(([key]) => !isSourceIdentifier(key)).filter(([key, value], index, entries) =>
    !entries.slice(0, index).some(([otherKey, otherValue]) => humanize(otherKey) === humanize(key) && Object.is(otherValue, value)),
  );
  const visibleMetadataEntries = properties.slice(0, 16);
  const additionalMetadataEntries = properties.slice(16);
  const notice = relevanceNotice(relevance);
  const lifecycleReasonId = `scientific-viewer-lifecycle-reason-${instanceId || "instance"}`;
  const downloadMetadata = () => {
    const snapshot = {
      contract_version: "scientific-viewer-metadata.v1",
      title,
      version_label: versionLabel,
      exact_version_id: exactVersionId || null,
      relevance,
      metadata: Object.fromEntries(metadataEntries.slice(0, 32)),
    };
    const url = URL.createObjectURL(new Blob([JSON.stringify(snapshot, null, 2)], { type: "application/json" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = "scientific-viewer-metadata.json";
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 0);
  };
  return <article className="scientific-viewer-shell" data-viewer={descriptor.rendererKey} aria-labelledby={titleId}>
    <header className="scientific-viewer-shell-header">
      <div><h2 id={titleId}>{title}</h2><p>{scientificTypeLabel(descriptor.scientificType)} · {versionLabel}{descriptor.support === "FALLBACK" ? " · 专业视图暂不可用" : ""}</p></div>
      <div className="scientific-viewer-shell-actions">
        {lifecycleAction ? <><button type="button" className="product-secondary-action" onClick={lifecycleAction.onClick} disabled={lifecycleAction.disabled} aria-describedby={lifecycleAction.disabledReason ? lifecycleReasonId : undefined}>{lifecycleAction.label}</button>{lifecycleAction.disabledReason ? <span id={lifecycleReasonId} className="sr-only" role="status">{lifecycleAction.disabledReason}</span> : null}</> : null}
        {primaryActionHref ? <Link className="product-primary-action" href={primaryActionHref}>研究此数据</Link> : null}
      </div>
    </header>
    {notice ? <div className={`scientific-relevance-notice ${relevance.toLowerCase()}`} role="note"><strong>{notice.title}</strong><span>{notice.detail}</span></div> : null}
    <div className="scientific-viewer-shell-body">{children}</div>
    {selection ? <aside className="scientific-selection-rail" aria-live="polite"><div><span>当前选择</span><strong>{selection.displayLabel}</strong></div><p>此选择绑定当前数据版本，可用于询问、结果解释与证据定位。</p>{onClearSelection ? <button type="button" className="product-secondary-action" onClick={onClearSelection}>清除选择</button> : null}</aside> : null}
    <footer className="scientific-viewer-shell-footer">
      {limitations.length ? <section aria-labelledby={limitationsId}><h3 id={limitationsId}>限制与说明</h3><ul>{limitations.map((item) => <li key={item}>{item}</li>)}</ul></section> : null}
      <details className="scientific-viewer-source-details"><summary>查看数据详情</summary>
        <div className="scientific-viewer-source-content">
          {properties.length ? <section aria-label="数据属性">
            <h3>数据属性</h3>
            <dl>{visibleMetadataEntries.map(([key, value]) => <div key={key}><dt>{humanize(key)}</dt><dd>{displayValue(value)}</dd></div>)}</dl>
            {additionalMetadataEntries.length ? <details className="scientific-viewer-additional-metadata">
              <summary>查看其余 {additionalMetadataEntries.length} 项元数据</summary>
              <dl>{additionalMetadataEntries.map(([key, value]) => <div key={key}><dt>{humanize(key)}</dt><dd>{displayValue(value)}</dd></div>)}</dl>
            </details> : null}
          </section> : null}
          <details className="scientific-viewer-identifiers"><summary>来源标识与查看器</summary>
            <dl>
              {exactVersionId ? <div><dt>精确版本</dt><dd><code>{exactVersionId}</code></dd></div> : null}
              {sourceEntries.map(([key, value]) => <div key={key}><dt>{humanize(key)}</dt><dd><code>{displayValue(value)}</code></dd></div>)}
              <div><dt>查看器</dt><dd><code>{descriptor.viewerId}</code></dd></div>
              <div><dt>契约版本</dt><dd>{descriptor.viewerVersion}</dd></div>
              <div><dt>预览上限</dt><dd>{(descriptor.maximumPayloadBytes / 1024 / 1024).toFixed(0)} MiB</dd></div>
            </dl>
          </details>
          <button type="button" className="product-secondary-action" onClick={downloadMetadata}>导出元数据摘要</button>
        </div>
      </details>
    </footer>
  </article>;
}

function relevanceNotice(status: string) {
  if (status === "STALE") return { title: "历史数据版本", detail: "此视图绑定原始版本；当前对象已有更新版本，系统不会自动替换。" };
  if (status === "SOURCE_MISSING") return { title: "原始来源当前不可访问", detail: "科学元数据与精确版本身份仍然保留；系统不会以较新版本或其他结果替代缺失的原始科学数据。" };
  if (status === "INVALIDATED") return { title: "历史记录已失效", detail: "此内容仅用于审计，不应视为当前有效科研证据。" };
  return null;
}

function scientificTypeLabel(type: string) {
  return ({ "materials.dataset": "材料数据表", "materials.table": "科研材料表", "structure.crystal": "晶体结构", "trajectory.atomic": "原子轨迹", "diffraction.xrd.experimental": "实验 XRD", "diffraction.xrd.theoretical": "理论 XRD", "analysis.rdf": "径向分布函数", "electronic.band_structure": "电子能带", "electronic.dos": "电子态密度", "phonon.band_structure": "声子能带", "phonon.dos": "声子态密度", "reciprocal.brillouin_zone": "布里渊区", "volumetric.charge_density": "电荷密度" } as Record<string, string>)[type] || "科学数据";
}

function metadataKey(value: string) { return value.replace(/([a-z])([A-Z])/g, "$1_$2").toLowerCase(); }
function isSourceIdentifier(key: string) { return /(?:^|_)(?:id|hash|sha256|refs?)$/.test(metadataKey(key)); }
function humanize(value: string) {
  return ({ columns: "数据列", detected_format: "文件格式", ncolumns: "列数", n_columns: "列数", column_count: "列数", nrows: "行数", n_rows: "行数", row_count: "行数", formula: "化学式", site_count: "原子数", dataset_id: "数据集标识", source_resource_id: "来源文件标识", object_id: "对象标识", version_id: "版本标识", content_hash: "内容指纹", semantic_hash: "语义指纹" } as Record<string, string>)[metadataKey(value)]
    || value.replace(/([a-z])([A-Z])/g, "$1 $2").replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}
function displayValue(value: unknown): string {
  if (typeof value === "string" || typeof value === "number") return String(value);
  if (typeof value === "boolean") return value ? "是" : "否";
  if (Array.isArray(value)) {
    if (!value.length) return "无";
    const labels = value.map(item => typeof item === "string" || typeof item === "number" ? String(item)
      : item && typeof item === "object" && typeof item.name === "string" ? item.name : null);
    if (labels.every((label): label is string => label !== null) && labels.join("、").length <= 240) return labels.join("、");
    return `${value.length} 项`;
  }
  return value && typeof value === "object" ? `${Object.keys(value).length} 个字段` : "未提供";
}
