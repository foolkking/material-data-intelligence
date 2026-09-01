"use client";

import { ProductLink as Link } from "../ProductNavigation";
import type { ReactNode } from "react";

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
  primaryActionHref?: string | null;
  lifecycleAction?: { label: string; onClick: () => void; disabled?: boolean } | null;
  children: ReactNode;
}>) {
  const notice = relevanceNotice(relevance);
  return <article className="scientific-viewer-shell" data-viewer={descriptor.rendererKey}>
    <header className="scientific-viewer-shell-header">
      <div><p className="product-kicker">{scientificTypeLabel(descriptor.scientificType)}</p><h2>{title}</h2><p>{versionLabel}{descriptor.support === "FALLBACK" ? " · 专业视图暂不可用" : ""}</p></div>
      <div className="scientific-viewer-shell-actions">
        {lifecycleAction ? <button type="button" className="product-secondary-action" onClick={lifecycleAction.onClick} disabled={lifecycleAction.disabled}>{lifecycleAction.label}</button> : null}
        {primaryActionHref ? <Link className="product-primary-action" href={primaryActionHref}>研究此数据</Link> : null}
      </div>
    </header>
    {notice ? <div className={`scientific-relevance-notice ${relevance.toLowerCase()}`} role="note"><strong>{notice.title}</strong><span>{notice.detail}</span></div> : null}
    <div className="scientific-viewer-shell-body">{children}</div>
    {selection ? <aside className="scientific-selection-rail" aria-live="polite"><div><span>当前选择</span><strong>{selection.displayLabel}</strong></div><p>此选择绑定当前数据版本，可用于询问、结果解释与证据定位。</p></aside> : null}
    <footer className="scientific-viewer-shell-footer">
      {limitations.length ? <section aria-labelledby="viewer-limitations"><h3 id="viewer-limitations">限制与说明</h3><ul>{limitations.map((item) => <li key={item}>{item}</li>)}</ul></section> : null}
      {exactVersionId ? <details className="scientific-viewer-version-details"><summary>精确版本</summary><code>{exactVersionId}</code><p>此视图始终绑定该不可变版本；不会自动替换为最新数据。</p></details> : null}
      <details><summary>科学元数据</summary><dl>{Object.entries(metadata).slice(0, 16).map(([key, value]) => <div key={key}><dt>{humanize(key)}</dt><dd>{displayValue(value)}</dd></div>)}</dl></details>
      <details><summary>技术详情</summary><p>Viewer: {descriptor.viewerId} · contract {descriptor.viewerVersion} · payload bound {(descriptor.maximumPayloadBytes / 1024 / 1024).toFixed(0)} MiB</p></details>
    </footer>
  </article>;
}

function relevanceNotice(status: string) {
  if (status === "STALE") return { title: "历史数据版本", detail: "此视图绑定原始版本；当前对象已有更新版本，系统不会自动替换。" };
  if (status === "SOURCE_MISSING") return { title: "原始来源当前不可访问", detail: "已保存的科学元数据仍可查看，但无法恢复完整交互内容。" };
  if (status === "INVALIDATED") return { title: "历史记录已失效", detail: "此内容仅用于审计，不应视为当前有效科研证据。" };
  return null;
}

function scientificTypeLabel(type: string) {
  return ({ "materials.dataset": "材料数据表", "materials.table": "科研材料表", "structure.crystal": "晶体结构", "trajectory.atomic": "原子轨迹", "diffraction.xrd.experimental": "实验 XRD", "diffraction.xrd.theoretical": "理论 XRD", "analysis.rdf": "径向分布函数", "electronic.band_structure": "电子能带", "electronic.dos": "电子态密度", "phonon.band_structure": "声子能带", "phonon.dos": "声子态密度", "reciprocal.brillouin_zone": "布里渊区", "volumetric.charge_density": "电荷密度" } as Record<string, string>)[type] || "科学数据";
}

function humanize(value: string) { return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase()); }
function displayValue(value: unknown) { return typeof value === "string" || typeof value === "number" ? String(value) : Array.isArray(value) ? `${value.length} 项` : value && typeof value === "object" ? `${Object.keys(value).length} 个字段` : "未提供"; }
