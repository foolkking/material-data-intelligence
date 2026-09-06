"use client";

import { useState } from "react";
import { getPlannerArtifactContent } from "../lib/planner-api";

type JsonRecord = Record<string, unknown>;

export function ScientificReportArtifactPreview({
  jobId,
  artifactId,
  kind,
  title,
}: {
  jobId: string;
  artifactId: string;
  kind: "figure" | "table";
  title: string;
}) {
  const [state, setState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [payload, setPayload] = useState<unknown>(null);
  const [error, setError] = useState("");

  async function openPreview() {
    if (state === "loading") return;
    if (state === "ready") {
      setState("idle");
      setPayload(null);
      return;
    }
    setState("loading");
    setError("");
    try {
      const bytes = await getPlannerArtifactContent(jobId, artifactId, { maximumBytes: 8 * 1024 * 1024 });
      const text = new TextDecoder().decode(bytes);
      const next = JSON.parse(text) as unknown;
      setPayload(next);
      setState("ready");
    } catch (reason) {
      setError(describeArtifactPreviewError(reason));
      setState("error");
    }
  }

  return (
    <div className="scientific-report-artifact-preview">
      <button
        type="button"
        className="product-secondary-action"
        onClick={() => void openPreview()}
        aria-expanded={state === "ready"}
      >
        {state === "loading" ? "正在读取…" : state === "ready" ? "收起页内预览" : "在报告内查看"}
      </button>
      {state === "error" ? (
        <p className="scientific-report-artifact-preview-error" role="alert">
          {error} 可继续打开权威 Artifact 查看完整内容。
        </p>
      ) : null}
      {state === "ready" ? (
        <section className="scientific-report-artifact-preview-panel" aria-label={`${kind === "figure" ? "图形" : "数据表"}预览：${title}`}>
          <div className="scientific-report-artifact-preview-heading">
            <div>
              <span className="scientific-surface-kicker">持久化科学数据</span>
              <h3>{title}</h3>
            </div>
            <small>只读呈现 · 不会重新执行科学计算</small>
          </div>
          {kind === "figure" ? <FigurePreview payload={payload} title={title} /> : <TablePreview payload={payload} title={title} />}
        </section>
      ) : null}
    </div>
  );
}

function describeArtifactPreviewError(reason: unknown): string {
  if (isPlannerApiFailure(reason)) {
    if (reason.status === 401) return "ARTIFACT_SESSION_EXPIRED：登录状态已过期，请重新登录后重试。";
    if (reason.status === 403) return "ARTIFACT_ACCESS_DENIED：当前项目无权查看此 Artifact。";
    if (reason.status === 404) return "ARTIFACT_NOT_FOUND：权威 Artifact 尚不存在或已被移除。";
    if (reason.status === 410) return "ARTIFACT_GONE：权威 Artifact 已过期，原始科学结果仍保留其历史引用。";
    if (reason.status === 413) return "ARTIFACT_CONTENT_TOO_LARGE：权威 Artifact 超出报告页内安全预览范围。";
    return "ARTIFACT_CONTENT_UNAVAILABLE：权威 Artifact 暂时无法读取。";
  }
  if (reason instanceof SyntaxError) return "ARTIFACT_CONTENT_INVALID：权威 Artifact 内容不是有效的结构化数据。";
  if (reason instanceof Error && [
    "ARTIFACT_CONTENT_LIMIT_EXCEEDED",
    "ARTIFACT_CONTENT_BYTE_MISMATCH",
    "ARTIFACT_CONTENT_LIMIT_INVALID",
  ].includes(reason.message)) {
    return `${reason.message}：当前内容超出安全预览范围。`;
  }
  if (reason instanceof Error && /^[A-Z][A-Z0-9_]{2,80}$/u.test(reason.message)) {
    return `${reason.message}：权威 Artifact 暂时无法读取。`;
  }
  return "ARTIFACT_CONTENT_UNAVAILABLE：权威 Artifact 暂时无法读取。";
}

function isPlannerApiFailure(reason: unknown): reason is { readonly status: number } {
  return Boolean(reason && typeof reason === "object" && "status" in reason && typeof reason.status === "number");
}

function FigurePreview({ payload, title }: { payload: unknown; title: string }) {
  const record = asRecord(payload);
  const figure = asRecord(record?.figure);
  // Persisted scientific figures use both the bounded internal `series` shape
  // and the Plotly-compatible `data` shape. Both are authoritative payloads;
  // the report preview only projects their finite x/y points and never
  // recalculates the underlying science.
  const seriesCandidates = Array.isArray(record?.series)
    ? record.series
    : Array.isArray(record?.data)
      ? record.data
      : Array.isArray(figure?.data)
        ? figure.data
        : Array.isArray(figure?.series)
          ? figure.series
      : [];
  const series = seriesCandidates
    .map(asRecord)
    .filter((item): item is JsonRecord => Boolean(item));
  const tracePoints = series.map((item, traceIndex) => {
    const x = Array.isArray(item.x) ? item.x : [];
    const y = Array.isArray(item.y) ? item.y : [];
    return {
      name: typeof item.name === "string" && item.name.trim() ? item.name : `序列 ${traceIndex + 1}`,
      points: y.map((value, index) => ({
        x: numberValue(x[index]),
        order: index,
        y: numberValue(value),
      })).filter((point): point is { x: number | null; order: number; y: number } => point.y !== null),
    };
  }).filter((trace) => trace.points.length);
  const totalPointCount = tracePoints.reduce((total, trace) => total + trace.points.length, 0);
  let remainingPointBudget = 96;
  let sampled = false;
  const displayedTraces = tracePoints.map((trace) => {
    const points = samplePreviewPoints(trace.points, Math.max(0, remainingPointBudget));
    sampled ||= points.length < trace.points.length;
    remainingPointBudget -= points.length;
    return { ...trace, points };
  }).filter((trace) => trace.points.length);
  const points = displayedTraces.flatMap((trace) => trace.points);
  if (!points.length) {
    return <p className="scientific-report-artifact-preview-empty">该 Artifact 没有可绘制的有限序列；请打开权威 Artifact 查看结构化内容。</p>;
  }
  const width = 640;
  const height = 240;
  const left = 42;
  const bottom = 34;
  const plotWidth = width - left - 16;
  const plotHeight = height - bottom - 18;
  const minimum = Math.min(0, ...points.map((point) => point.y || 0));
  const maximum = Math.max(0, ...points.map((point) => point.y || 0));
  const range = Math.max(1e-9, maximum - minimum);
  const yCoordinate = (value: number) => height - bottom - ((value - minimum) / range) * plotHeight;
  const usesAuthoritativeNumericX = points.every((point) => point.x !== null);
  const numericXValues = usesAuthoritativeNumericX ? points.map((point) => point.x as number) : [];
  const xMinimum = numericXValues.length ? Math.min(...numericXValues) : 0;
  const xMaximum = numericXValues.length ? Math.max(...numericXValues) : 0;
  const xRange = xMaximum - xMinimum;
  const xCoordinate = (point: { x: number | null; order: number }, traceLength: number) => {
    if (usesAuthoritativeNumericX) {
      return xRange > 0
        ? left + (((point.x as number) - xMinimum) / xRange) * plotWidth
        : left + plotWidth / 2;
    }
    const step = plotWidth / Math.max(1, traceLength - 1);
    return left + point.order * step;
  };
  const baseline = yCoordinate(0);
  const layout = asRecord(record?.layout) || asRecord(figure?.layout);
  const xAxis = asRecord(layout?.xaxis);
  const yAxis = asRecord(layout?.yaxis);
  const xAxisTitle = xAxis?.title;
  const yAxisTitle = yAxis?.title;
  const xLabel = axisTitleText(xAxisTitle) || "采样序列";
  const yLabel = axisTitleText(yAxisTitle) || "数值";
  const xRangeLabel = axisRangeText(xAxis?.range);
  const yRangeLabel = axisRangeText(yAxis?.range);
  const xTickLabel = axisTickText(xAxis);
  const yTickLabel = axisTickText(yAxis);
  const axisSummary = `${xLabel}，范围 ${xRangeLabel}，刻度 ${xTickLabel}；${yLabel}，范围 ${yRangeLabel}，刻度 ${yTickLabel}`;
  const palette = ["#0b6b57", "#b06d2f", "#4267a8", "#7e4f9b", "#7b5e2b"];
  return (
    <div className="scientific-report-inline-figure">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${title}持久化数据预览`} focusable="false">
        <desc>{axisSummary}</desc>
        <line x1={left} y1="18" x2={left} y2={height - bottom} />
        <line x1={left} y1={baseline} x2={width - 16} y2={baseline} />
        {displayedTraces.map((trace, traceIndex) => {
          const polyline = trace.points.map((point) => `${xCoordinate(point, trace.points.length)},${yCoordinate(point.y || 0)}`).join(" ");
          return <g key={trace.name} className="scientific-report-inline-trace">
            {trace.points.length > 1 ? <polyline points={polyline} stroke={palette[traceIndex % palette.length]} /> : null}
            {trace.points.map((point) => <circle key={`${String(point.x)}:${point.order}`} cx={xCoordinate(point, trace.points.length)} cy={yCoordinate(point.y || 0)} r="3.5" fill={palette[traceIndex % palette.length]} />)}
          </g>;
        })}
        <text x={width / 2} y={height - 4} textAnchor="middle">{xLabel}</text>
        <text x="12" y={height / 2} textAnchor="middle" transform={`rotate(-90 12 ${height / 2})`}>{yLabel}</text>
      </svg>
      <div className="scientific-report-inline-axis-summary" role="group" aria-label="权威坐标轴信息">
        <div>
          <strong>X 轴 · {xLabel}</strong>
          <span>范围：{xRangeLabel}</span>
          <span>刻度：{xTickLabel}</span>
        </div>
        <div>
          <strong>Y 轴 · {yLabel}</strong>
          <span>范围：{yRangeLabel}</span>
          <span>刻度：{yTickLabel}</span>
        </div>
      </div>
      <ul className="scientific-report-inline-legend" aria-label="图形序列图例">
        {displayedTraces.map((trace, traceIndex) => (
          <li key={`legend:${trace.name}`}>
            <span
              className="scientific-report-inline-legend-swatch"
              aria-hidden="true"
              style={{ backgroundColor: palette[traceIndex % palette.length] }}
            />
            <span>{trace.name}</span>
            <small>{trace.points.length} 个点</small>
          </li>
        ))}
      </ul>
      <p role="status" aria-live="polite">
        共显示 {points.length}/{totalPointCount} 个有限数据点；抽样策略：
        {sampled ? "固定端点 + 全局最小/最大值 + 分桶局部极值" : "无抽样（完整有限点）"}；
        保留 {displayedTraces.length} 条序列；完整数值仍保留在权威 Artifact 中。
      </p>
    </div>
  );
}

type PreviewPoint = { x: number | null; order: number; y: number };

function samplePreviewPoints(points: PreviewPoint[], target: number): PreviewPoint[] {
  if (points.length <= target) return points;
  if (target < 3) return points.slice(0, target);
  const indices = new Set<number>([0, points.length - 1]);
  let minimum = 0;
  let maximum = 0;
  for (let index = 1; index < points.length; index += 1) {
    if (points[index].y < points[minimum].y) minimum = index;
    if (points[index].y > points[maximum].y) maximum = index;
  }
  if (indices.size < target) indices.add(minimum);
  if (indices.size < target) indices.add(maximum);
  const buckets = Math.max(1, Math.floor((target - 2) / 2));
  const localExtrema: number[] = [];
  for (let bucket = 0; bucket < buckets; bucket += 1) {
    const start = Math.floor((bucket * (points.length - 1)) / buckets);
    const end = Math.max(start + 1, Math.floor(((bucket + 1) * (points.length - 1)) / buckets));
    let localMinimum = start;
    let localMaximum = start;
    for (let index = start; index <= Math.min(end, points.length - 1); index += 1) {
      if (points[index].y < points[localMinimum].y) localMinimum = index;
      if (points[index].y > points[localMaximum].y) localMaximum = index;
    }
    localExtrema.push(localMinimum, localMaximum);
  }
  for (const index of localExtrema) {
    if (indices.size >= target) break;
    indices.add(index);
  }
  for (let index = 1; indices.size < target && index < points.length - 1; index += 1) indices.add(index);
  return [...indices].sort((a, b) => a - b).slice(0, target).map((index) => points[index]);
}

function axisTitleText(value: unknown): string | null {
  if (typeof value === "string" && value.trim()) return value;
  const record = asRecord(value);
  return typeof record?.text === "string" && record.text.trim() ? record.text : null;
}

function axisRangeText(value: unknown): string {
  if (!Array.isArray(value) || value.length < 2) return "Artifact 未提供";
  const range = value.slice(0, 2).map(numberValue);
  if (range.some((item) => item === null)) return "Artifact 未提供";
  return `${String(range[0])} 至 ${String(range[1])}`;
}

function axisTickText(axis: JsonRecord | null): string {
  if (!axis || !Array.isArray(axis.tickvals)) return "Artifact 未提供";
  const labels = axis.tickvals
    .slice(0, 6)
    .map((value, index) => {
      const tickText = Array.isArray(axis.ticktext) ? axis.ticktext[index] : undefined;
      return tickText === undefined ? String(value) : String(tickText);
    });
  if (!labels.length) return "Artifact 未提供";
  const omitted = Math.max(0, axis.tickvals.length - labels.length);
  return labels.join(" · ") + (omitted ? ` · 另有 ${omitted} 个` : "");
}

function TablePreview({ payload, title }: { payload: unknown; title: string }) {
  const rows = tableRows(payload);
  if (!rows.length) {
    return <p className="scientific-report-artifact-preview-empty">该 Artifact 暂无可识别的表格行；请打开权威数据表查看完整结构化内容。</p>;
  }
  const allColumns = Array.from(new Set(rows.flatMap((row) => Object.keys(row))));
  const columns = allColumns.slice(0, 8);
  const omittedColumns = allColumns.slice(columns.length);
  const previewRows = rows.slice(0, 24);
  const omittedRowCount = Math.max(0, rows.length - previewRows.length);
  const rowKeys = scientificReportTableRowKeys(previewRows);
  return (
    <div className="scientific-report-inline-table-wrap" role="region" aria-label="持久化数据表预览" tabIndex={0}>
      <table>
        <caption className="sr-only">{title}持久化数据表</caption>
        <thead><tr>{columns.map((column) => <th key={column} scope="col" title={column}>{formatColumnLabel(column)}</th>)}</tr></thead>
        <tbody>{previewRows.map((row, index) => <tr key={rowKeys[index]}>{columns.map((column) => <td key={column}>{displayValue(row[column])}</td>)}</tr>)}</tbody>
      </table>
      <p>
        显示前 {Math.min(rows.length, 24)} 行
        {omittedRowCount ? `；另有 ${omittedRowCount} 行未显示` : ""}
        {omittedColumns.length ? `；显示前 ${columns.length} 列，另有 ${omittedColumns.length} 列未显示` : ""}
        ；完整数据仍保留在权威 Artifact 中。
      </p>
      {omittedColumns.length ? (
        <details className="scientific-report-inline-table-omitted">
          <summary>查看未显示列（{omittedColumns.length}）</summary>
          <ul>
            {omittedColumns.map((column) => <li key={column}>{formatColumnLabel(column)}</li>)}
          </ul>
        </details>
      ) : null}
    </div>
  );
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

function tableRows(payload: unknown): JsonRecord[] {
  const record = asRecord(payload);
  if (!record) return [];
  const nestedTable = asRecord(record.table);
  const direct = [record.rows, record.data, record.site_details, nestedTable?.rows, nestedTable?.data];
  for (const candidate of direct) {
    if (Array.isArray(candidate)) {
      const rows = candidate.map(asRecord).filter((item): item is JsonRecord => Boolean(item));
      if (rows.length) return rows;
    }
  }
  const histogram = asRecord(record.histogram)?.bins;
  if (Array.isArray(histogram)) return histogram.map(asRecord).filter((item): item is JsonRecord => Boolean(item));
  if (record.artifactType === "trajectory.msd") {
    return trajectoryMsdRows(record);
  }
  if (record.artifactType === "trajectory.diffusion") {
    return trajectoryDiffusionRows(record);
  }
  return [];
}

function trajectoryMsdRows(record: JsonRecord): JsonRecord[] {
  const times = Array.isArray(record.lagTimesPs) ? record.lagTimesPs : [];
  const total = Array.isArray(record.totalMsdAngstrom2) ? record.totalMsdAngstrom2 : [];
  const directional = asRecord(record.directionalMsdAngstrom2);
  const x = Array.isArray(directional?.x) ? directional.x : [];
  const y = Array.isArray(directional?.y) ? directional.y : [];
  const z = Array.isArray(directional?.z) ? directional.z : [];
  const count = Math.min(times.length, total.length);
  return Array.from({ length: Math.min(count, 96) }, (_, index) => ({
    lag_time_ps: times[index],
    total_msd_angstrom2: total[index],
    x_msd_angstrom2: x[index],
    y_msd_angstrom2: y[index],
    z_msd_angstrom2: z[index],
  }));
}

function trajectoryDiffusionRows(record: JsonRecord): JsonRecord[] {
  const estimate = asRecord(record.diffusionEstimate);
  const fit = asRecord(record.fit);
  const window = asRecord(record.fitWindow);
  const diagnostic = asRecord(record.regimeDiagnostic);
  if (!estimate && !fit && !window) return [];
  return [{
    fit_start_ps: window?.startPs,
    fit_end_ps: window?.endPs,
    fit_points: window?.pointCount ?? fit?.pointCount,
    diffusion_coefficient_angstrom2_per_ps: estimate?.value,
    diffusion_unit: estimate?.unit,
    r_squared: fit?.rSquared,
    rmse_angstrom2: fit?.rmseAngstrom2,
    regime_status: diagnostic?.status,
  }];
}

function asRecord(value: unknown): JsonRecord | null {
  return value && typeof value === "object" && !Array.isArray(value) ? value as JsonRecord : null;
}

function numberValue(value: unknown): number | null {
  const number = typeof value === "number" ? value : Number(value);
  return Number.isFinite(number) ? number : null;
}

function displayValue(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return String(value);
  if (Array.isArray(value)) return `[${value.map((item) => displayValue(item)).join(", ")}]`;
  return JSON.stringify(value);
}

function formatColumnLabel(value: string): string {
  const labels: Record<string, string> = {
    coordination_number: "配位数",
    element: "元素",
    neighbor_count_before_truncation: "截断前邻居数",
    neighbor_distances_angstrom: "邻居距离 (Å)",
    neighbor_elements: "邻居元素",
    neighbor_indices: "邻居索引",
    site_index: "位点索引",
    structureId: "结构标识",
    sample_id: "样本标识",
    band_gap: "带隙",
    lag_time_ps: "滞后时间 (ps)",
    total_msd_angstrom2: "总 MSD (Å²)",
    x_msd_angstrom2: "X 方向 MSD (Å²)",
    y_msd_angstrom2: "Y 方向 MSD (Å²)",
    z_msd_angstrom2: "Z 方向 MSD (Å²)",
    fit_start_ps: "拟合起点 (ps)",
    fit_end_ps: "拟合终点 (ps)",
    fit_points: "拟合点数",
    diffusion_coefficient_angstrom2_per_ps: "扩散系数 (Å²/ps)",
    diffusion_unit: "扩散系数单位",
    r_squared: "R²",
    rmse_angstrom2: "RMSE (Å²)",
    regime_status: "区间诊断",
  };
  return labels[value] || value.replaceAll("_", " ");
}
