"use client";

import { useEffect, useId, useMemo, useRef, useState } from "react";
import { getPlannerArtifactContent } from "../../app/lib/planner-api";
import { readReportContent, ReportReadTimeoutError } from "./report-read";
import { renderScientificReportFigure } from "../../app/lib/scientific-report-figure";
import { createDeferredScientificViewer } from "../../scientific-viewers/DeferredScientificViewer";
import { asRecord, displayValue, formatColumnLabel, isNumericTableColumn, regressionMetricRows, tableRows } from "../../app/lib/scientific-report-table-data";
import type { ReportViewerArtifact } from "../../app/lib/scientific-report-api";
import { LazyScientificResultViewer } from "../../scientific-viewers/LazyScientificViewers";
import { isSavedElementReference } from "../../scientific-viewers/workspace/saved-element-reference";
import { isSavedLocalEnvironment } from "../../scientific-viewers/workspace/saved-local-environment";

const StructurePreview = createDeferredScientificViewer(() => import("../../scientific-viewers/viewer-scene/ViewerSceneRendererSurface")
  .then((module) => ({ default: module.ViewerSceneRendererSurface })));

const PlotPreview = createDeferredScientificViewer(() => import("../../scientific-viewers/workspace/WorkspaceGenericPlot")
  .then((module) => ({ default: module.WorkspaceGenericPlot })));

const LocalEnvironmentPreview = createDeferredScientificViewer(() => import("../../scientific-viewers/workspace/LocalEnvironmentPolyhedraPanel")
  .then((module) => ({ default: module.LocalEnvironmentReportPreview })));

type JsonRecord = Record<string, unknown>;

type PreviewProps = {
  jobId: string;
  artifactId: string;
  kind: "figure" | "table";
  title: string;
  viewer?: { projectId: string; artifacts: ReportViewerArtifact[] };
};

export function ScientificReportArtifactPreview(props: PreviewProps) {
  if (props.viewer) return <ReportVolumetricPreview key={JSON.stringify([props.jobId, props.artifactId, props.viewer])} {...props} viewer={props.viewer} />;
  return <ReportArtifactPreviewContent key={`${props.jobId}:${props.artifactId}:${props.kind}`} {...props} />;
}

function ReportVolumetricPreview({ jobId, artifactId, title, viewer }: PreviewProps & { viewer: NonNullable<PreviewProps["viewer"]> }) {
  const [opened, setOpened] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const selected = viewer.artifacts.filter(item => item.id === artifactId && item.jobId === jobId && item.type === "volumetric_dataset_json");
  const exact = selected.length === 1 && viewer.artifacts.every(item => item.jobId === jobId && item.toolCallId === selected[0].toolCallId);
  if (!exact) return <p role="alert">体数据来源无法准确对应，请返回来源研究查看。</p>;
  return <div className="scientific-report-artifact-preview">
    <button type="button" className="product-secondary-action" aria-expanded={expanded}
      onClick={() => { setOpened(true); setExpanded(value => !value); }}>{expanded ? "收起页内预览" : "在报告内查看"}</button>
    {opened ? <section hidden={!expanded} style={expanded ? undefined : { display: "none" }}
      className="scientific-report-artifact-preview-panel" aria-label={`图形预览：${title}`}>
      <LazyScientificResultViewer projectId={viewer.projectId} jobId={jobId} selected={selected[0]} artifacts={viewer.artifacts} />
    </section> : null}
  </div>;
}

function ReportArtifactPreviewContent({
  jobId,
  artifactId,
  kind,
  title,
}: PreviewProps) {
  const [state, setState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [payload, setPayload] = useState<unknown>(null);
  const [error, setError] = useState("");
  const [expanded, setExpanded] = useState(false);
  const pending = useRef<AbortController | null>(null);
  useEffect(() => () => pending.current?.abort(), []);

  async function openPreview() {
    if (state === "loading") return;
    if (state === "ready") {
      setExpanded((current) => !current);
      return;
    }
    setState("loading");
    setError("");
    const controller = new AbortController();
    pending.current = controller;
    try {
      const bytes = await readReportContent((signal) => getPlannerArtifactContent(jobId, artifactId, { signal, maximumBytes: 8 * 1024 * 1024 }), controller.signal);
      if (controller.signal.aborted) return;
      const text = new TextDecoder().decode(bytes);
      const next = JSON.parse(text) as unknown;
      setPayload(next);
      setState("ready");
      setExpanded(true);
    } catch (reason) {
      if (controller.signal.aborted) return;
      setError(describeArtifactPreviewError(reason));
      setState("error");
    }
  }

  return (
    <div className="scientific-report-artifact-preview" aria-busy={state === "loading"}>
      <button
        type="button"
        className="product-secondary-action"
        onClick={() => void openPreview()}
        aria-expanded={state === "ready" && expanded}
        disabled={state === "loading"}
      >
        {state === "loading" ? "正在读取…" : state === "ready" && expanded ? "收起页内预览" : state === "error" ? "重新加载预览" : "在报告内查看"}
      </button>
      {state === "error" ? (
        <p className="scientific-report-artifact-preview-error" role="alert">
          {error} 报告正文仍可阅读。
        </p>
      ) : null}
      {state === "ready" ? (
        <section className="scientific-report-artifact-preview-panel" hidden={!expanded} style={expanded ? undefined : { display: "none" }} aria-label={`${kind === "figure" ? "图形" : "数据表"}预览：${title}`}>
          {kind === "figure" ? expanded ? <FigurePreview payload={payload} title={title} /> : null : <TablePreview payload={payload} title={title} />}
        </section>
      ) : null}
    </div>
  );
}

function describeArtifactPreviewError(reason: unknown): string {
  if (reason instanceof ReportReadTimeoutError) return "预览读取超时，请重试。";
  if (isPlannerApiFailure(reason)) {
    if (reason.status === 401) return "登录状态已过期，请重新登录后重试。";
    if (reason.status === 403) return "当前账号无权查看此科学结果，请确认项目访问权限。";
    if (reason.status === 404) return "找不到这项科学结果，请确认来源是否仍可访问。";
    if (reason.status === 410) return "这项科学结果已过期，报告仍保留其历史引用。";
    if (reason.status === 413) return "内容超出页内预览范围，可下载完整结果查看。";
    return "科学结果暂时无法读取，请重试。";
  }
  if (reason instanceof SyntaxError) return "科学结果格式无法预览，可下载原始结果查看。";
  if (reason instanceof Error && [
    "ARTIFACT_CONTENT_LIMIT_EXCEEDED",
    "ARTIFACT_CONTENT_BYTE_MISMATCH",
    "ARTIFACT_CONTENT_LIMIT_INVALID",
  ].includes(reason.message)) {
    return "当前内容无法完整预览，可下载原始结果查看。";
  }
  return "科学结果暂时无法读取，请重试。";
}

function isPlannerApiFailure(reason: unknown): reason is { readonly status: number } {
  return Boolean(reason && typeof reason === "object" && "status" in reason && typeof reason.status === "number");
}

function FigurePreview({ payload, title }: { payload: unknown; title: string }) {
  const plotContainer = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(640);
  const [failedImage, setFailedImage] = useState<string | null>(null);
  useEffect(() => {
    const element = plotContainer.current;
    if (!element || typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(([entry]) => {
      if (entry.contentRect.width > 0) setWidth(Math.round(entry.contentRect.width));
    });
    observer.observe(element);
    return () => observer.disconnect();
  }, []);
  const rendered = useMemo(() => asRecord(payload)?.kind === "viewer_scene" || isSavedLocalEnvironment(payload) ? null : renderScientificReportFigure(payload, title, { width, compact: true }), [payload, title, width]);
  const record = asRecord(payload);
  if (record?.kind === "viewer_scene") return <StructurePreview payload={payload} />;
  if (isSavedLocalEnvironment(payload)) return <LocalEnvironmentPreview payload={payload} />;
  return <div className="scientific-report-inline-figure" ref={plotContainer}>
    {rendered && failedImage !== rendered.svg ? <>
      <img className="scientific-report-saved-figure" src={`data:image/svg+xml;charset=utf-8,${encodeURIComponent(rendered.svg)}`}
        alt={`${title}持久化数据预览`} onError={() => setFailedImage(rendered.svg)} />
      <p role="status" className={isSavedElementReference(payload) ? "sr-only" : undefined}>完整显示 {rendered.pointCount} 个数据点</p>
      {rendered.axes.length ? <details className="scientific-report-axis-details"><summary>坐标轴来源</summary>
        <div className="scientific-report-inline-axis-summary" role="group" aria-label="权威坐标轴信息">
          {rendered.axes.map((axis, index) => <div key={index}>
            <strong>{index === 0 ? "X" : "Y"} 轴 · {axis.label}</strong>
            {axis.range ? <span>范围：{axis.range}</span> : null}
            {axis.ticks ? <span>刻度：{axis.ticks}</span> : null}
          </div>)}
        </div>
      </details> : null}
    </> : record?.schemaVersion === "phase10n5.electronic_band_plot.v1" || record?.schema_version === "phase10h1.phonon_band_plot.v1" ? <div>
      <p role="alert">{rendered ? "能带图片暂时无法显示。" : "能带路径或参考线信息不完整，无法生成可信预览。请查看原始结果文件。"}</p>
      {rendered ? <button type="button" className="product-secondary-action" onClick={() => setFailedImage(null)}>重新绘制能带图</button> : null}
    </div> : <PlotPreview content={payload} maximumPoints={20_000} />}
  </div>;
}

function TablePreview({ payload, title }: { payload: unknown; title: string }) {
  const metricRows = regressionMetricRows(payload);
  if (!metricRows) return <RowTablePreview payload={payload} title={title} />;
  return <div className="scientific-report-inline-table-wrap scientific-report-metrics-table">
    <table>
      <caption className="sr-only">{title}持久化指标</caption>
      <thead><tr><th scope="col">项目</th><th scope="col">值</th></tr></thead>
      <tbody>{metricRows.map(([label, value]) => <tr key={label}>
        <th scope="row">{label}</th><td><TableValue value={value} /></td>
      </tr>)}</tbody>
    </table>
  </div>;
}

function RowTablePreview({ payload, title }: { payload: unknown; title: string }) {
  const rows = useMemo(() => tableRows(payload), [payload]);
  const [page, setPage] = useState(0);
  const [query, setQuery] = useState("");
  const [chosenColumns, setChosenColumns] = useState<Set<string> | null>(null);
  const [columnsOpen, setColumnsOpen] = useState(false);
  const columnsId = useId();
  const columnsButton = useRef<HTMLButtonElement>(null);
  const allColumns = useMemo(() => Array.from(new Set(rows.flatMap(row => Object.keys(row)))), [rows]);
  const numericColumns = useMemo(() => new Set(allColumns.filter(column => isNumericTableColumn(rows, column))), [rows, allColumns]);
  const primaryColumns = allColumns.filter(column => !["stateId", "bandIdentity", "channelIdentity", "energyPointId"].includes(column));
  const defaultColumns = (primaryColumns.length ? primaryColumns : allColumns).slice(0, asRecord(payload)?.schema_version === "phase10h1.phonon_band_table.v1" ? 7 : 8);
  const columns = allColumns.filter(column => chosenColumns ? chosenColumns.has(column) : defaultColumns.includes(column));
  const filtered = useMemo(() => {
    const term = query.trim().toLocaleLowerCase();
    return term ? rows.filter(row => allColumns.some(column => displayValue(row[column]).toLocaleLowerCase().includes(term))) : rows;
  }, [rows, allColumns, query]);
  if (!rows.length) {
    return <p className="scientific-report-artifact-preview-empty">此结果暂无可预览的表格行，可打开源文件查看。</p>;
  }
  const pageCount = Math.max(1, Math.ceil(filtered.length / 24));
  const currentPage = Math.min(page, pageCount - 1);
  const previewRows = filtered.slice(currentPage * 24, (currentPage + 1) * 24);
  const rowKeys = scientificReportTableRowKeys(previewRows);
  return (
    <div>
      <div className="scientific-report-table-tools">
        <input type="search" aria-label="搜索表格内容" placeholder="搜索表格内容" value={query} onChange={event => { setQuery(event.target.value); setPage(0); }} />
        <button ref={columnsButton} type="button" className="product-secondary-action" aria-expanded={columnsOpen} aria-controls={columnsId} onClick={() => setColumnsOpen(value => !value)}>列显示</button>
      </div>
      {columnsOpen ? <fieldset id={columnsId} className="scientific-report-table-columns" onKeyDown={event => {
        if (event.key === "Escape") { event.preventDefault(); setColumnsOpen(false); columnsButton.current?.focus(); }
      }}>
        <legend className="sr-only">显示列</legend>
        {allColumns.map(column => <label key={column}><input type="checkbox" checked={columns.includes(column)} disabled={columns.length === 1 && columns[0] === column} onChange={event => {
          const next = new Set(columns);
          if (event.target.checked) next.add(column); else next.delete(column);
          setChosenColumns(next);
        }} />{formatColumnLabel(column, payload)}</label>)}
      </fieldset> : null}
      <div className="scientific-report-table-pagination">
        <p role="status">
          {query.trim() ? `匹配 ${filtered.length} / ${rows.length} 行` : `显示 ${currentPage * 24 + 1}–${Math.min(rows.length, (currentPage + 1) * 24)} / ${rows.length} 行`}
          {query.trim() && pageCount > 1 ? `，当前 ${currentPage * 24 + 1}–${Math.min(filtered.length, (currentPage + 1) * 24)}` : ""}
          {columns.length < allColumns.length ? ` · ${columns.length} / ${allColumns.length} 列` : ""}
        </p>
        {pageCount > 1 ? <nav className="scientific-report-artifact-actions" aria-label="报告数据表分页">
          <button type="button" className="product-secondary-action" disabled={currentPage === 0} onClick={() => setPage(currentPage - 1)}>上一页</button>
          <TablePageInput page={currentPage + 1} pages={pageCount} onPage={value => setPage(value - 1)} />
          <button type="button" className="product-secondary-action" disabled={currentPage + 1 >= pageCount} onClick={() => setPage(currentPage + 1)}>下一页</button>
        </nav> : null}
      </div>
      <div className="scientific-report-inline-table-wrap scientific-report-row-table" role="region" aria-label="持久化数据表预览" tabIndex={0}>
        <table>
          <caption className="sr-only">{title}持久化数据表</caption>
          <thead><tr>{columns.map((column) => <th key={column} scope="col" title={column} className={numericColumns.has(column) ? "scientific-report-table-number" : undefined}>{formatColumnLabel(column, payload)}</th>)}</tr></thead>
          <tbody>{previewRows.map((row, index) => <tr key={rowKeys[index]}>{columns.map((column) => <td key={column} className={numericColumns.has(column) ? "scientific-report-table-number" : undefined}><TableValue value={row[column]} /></td>)}</tr>)}</tbody>
        </table>
      </div>
      {!filtered.length ? <p className="scientific-report-table-empty">没有匹配的数据。<button type="button" className="product-secondary-action" onClick={() => { setQuery(""); setPage(0); }}>清除搜索</button></p> : null}
    </div>
  );
}

function TableValue({ value }: { value: unknown }) {
  const text = displayValue(value);
  if (text.length <= 72) return <>{text}</>;
  return <details className="scientific-report-table-value"><summary>{text.slice(0, 28)}…{text.slice(-12)}<span className="sr-only">，查看完整值</span></summary><p>{text}</p></details>;
}

function TablePageInput({ page, pages, onPage }: { page: number; pages: number; onPage: (value: number) => void }) {
  const [input, setInput] = useState({ page, pages, draft: String(page) });
  // Reconcile navigation during rendering; a delayed mount effect must not
  // replace the user's first edit after an asynchronous preview opens.
  if (input.page !== page || input.pages !== pages) {
    setInput({ page, pages, draft: String(page) });
  }
  const draft = input.draft;
  const setDraft = (value: string) => setInput({ page, pages, draft: value });
  const commit = () => {
    const value = Number(draft);
    const next = draft.trim() && Number.isFinite(value) ? Math.max(1, Math.min(pages, Math.trunc(value))) : page;
    setDraft(String(next));
    onPage(next);
  };
  return <label className="scientific-report-table-page">第 <input type="number" aria-label="表格页码" min={1} max={pages} step={1} value={draft}
    onChange={event => setDraft(event.target.value)} onBlur={commit} onKeyDown={event => {
      if (event.key === "Enter") { event.preventDefault(); commit(); }
      if (event.key === "Escape") { event.preventDefault(); setDraft(String(page)); }
    }} /> / {pages} 页</label>;
}

export function scientificReportTableRowKeys(rows: JsonRecord[]): string[] {
  const identityFields = ["id", "sample_id", "sampleRef", "site_index", "structureId", "material_id"];
  const candidates = rows.map((row) => {
    for (const field of identityFields) {
      const value = row[field];
      if (typeof value === "string" && value.trim()) return `${field}:${value}`;
      if (typeof value === "number" && Number.isFinite(value)) return `${field}:${value}`;
    }
    return null;
  });
  const candidateCounts = new Map<string, number>();
  candidates.forEach((candidate) => {
    if (candidate) candidateCounts.set(candidate, (candidateCounts.get(candidate) || 0) + 1);
  });
  const contentOccurrences = new Map<string, number>();
  return rows.map((row, index) => {
    const candidate = candidates[index];
    if (candidate && candidateCounts.get(candidate) === 1) return `semantic:${candidate}`;
    const content = stableJson(row);
    const occurrence = contentOccurrences.get(content) || 0;
    contentOccurrences.set(content, occurrence + 1);
    return `content:${content}:${occurrence}`;
  });
}

function stableJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map((item) => stableJson(item)).join(",")}]`;
  const record = asRecord(value);
  if (record) {
    return `{${Object.keys(record).sort().map((key) => `${JSON.stringify(key)}:${stableJson(record[key])}`).join(",")}}`;
  }
  return JSON.stringify(value) ?? String(value);
}
