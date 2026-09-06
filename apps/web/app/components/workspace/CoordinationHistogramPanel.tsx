"use client";

import { useId, useMemo, useState } from "react";

import type { Artifact } from "../../lib/planner-api";

type JsonRecord = Record<string, unknown>;
type HistogramBin = Readonly<{
  coordinationNumber: number;
  count: number;
  fraction: number;
}>;
type HistogramSeries = Readonly<{
  id: string;
  label: string;
  bins: readonly HistogramBin[];
  totalSites: number;
}>;

const HISTOGRAM_SCHEMA = "phase10e1.coordination_hist.v1";
const PLOT_SCHEMA = "phase10e1.static_chart.v1";
const MAX_BINS = 128;
const MAX_ELEMENTS = 118;
const MAX_PAIRS = 512;
const MAX_WARNINGS = 128;

export function CoordinationHistogramPanel({ artifacts }: Readonly<{ artifacts: readonly Artifact[] }>) {
  const assessment = useMemo(() => inspectCoordinationHistogram(artifacts), [artifacts]);
  const [seriesId, setSeriesId] = useState("all");

  if (!assessment.ok) {
    return (
      <section className="workspace-generic-renderer coordination-histogram" role="status" data-testid="coordination-histogram-invalid">
        <header>
          <div>
            <span className="scientific-surface-kicker">配位环境</span>
            <h5>配位数分布不可用</h5>
          </div>
        </header>
        <p>持久化 Artifact 未通过受约束的配位分布契约校验，系统不会猜测或重算科学结果。</p>
        <code>{assessment.reason}</code>
      </section>
    );
  }

  const { payload, plot } = assessment;
  const structure = record(payload.structure);
  const parameters = record(payload.parameters);
  const histogram = record(payload.histogram);
  const limits = record(payload.limits);
  const series = histogramSeries(payload);
  const activeSeries = series.find((item) => item.id === seriesId) ?? series[0];
  const chartSummaryId = useId();
  const pairs = records(payload.pair_counts).slice(0, MAX_PAIRS);
  const warnings = textList(payload.warnings).slice(0, MAX_WARNINGS);

  return (
    <section className="workspace-generic-renderer coordination-histogram" aria-label="配位数分布" data-testid="coordination-histogram-panel">
      <header className="coordination-histogram-heading">
        <div>
          <span className="scientific-surface-kicker">确定性结构统计</span>
          <h5>配位数分布</h5>
          <p>按固定距离截断统计邻近原子；图表和表格均来自同一持久化结果。</p>
        </div>
        <span className="badge">{text(structure.formula) || "结构"}</span>
      </header>

      <dl className="coordination-histogram-metrics">
        <Metric label="位点数" value={integer(histogram.total_sites)} />
        <Metric label="结构数" value={integer(payload.structureCount)} />
        <Metric label="元素" value={textList(structure.species).join("、") || "未提供"} />
        <Metric label="截断半径" value={`${format(parameters.cutoff_angstrom)} Å`} />
        <Metric label="邻居策略" value={text(parameters.neighbor_policy) === "distance_cutoff" ? "固定距离截断" : text(parameters.neighbor_policy)} />
        <Metric label="数据完整性" value={limits.truncated === true ? "已截断" : "完整"} tone={limits.truncated === true ? "warning" : "success"} />
      </dl>

      <div className="coordination-histogram-toolbar">
        <label>
          查看范围
          <select value={activeSeries.id} onChange={(event) => setSeriesId(event.target.value)} aria-label="选择配位分布范围">
            {series.map((item) => <option key={item.id} value={item.id}>{item.label} · {item.totalSites} 位点</option>)}
          </select>
        </label>
        <p>{plot ? `配位数直方图 · ${localizedCoordinationAxis(text(record(plot.x_axis).label), "配位数")} / ${localizedCoordinationAxis(text(record(plot.y_axis).label), "位点数")}` : "使用权威表格数据生成有界显示。"}</p>
      </div>

      <div className="coordination-histogram-main">
        <figure className="coordination-histogram-figure">
          <figcaption>
            <strong>{activeSeries.label}</strong>
            <span>横轴为配位数，纵轴为位点数量；百分比按该范围内位点计算。</span>
          </figcaption>
          <HistogramChart series={activeSeries} summaryId={chartSummaryId} />
        </figure>

        <section className="coordination-histogram-table" aria-label="配位数分布数值表">
          <h6>数值分布</h6>
          <div className="workspace-table-scroll">
            <table aria-label="配位数分布数值表">
              <thead><tr><th scope="col">配位数</th><th scope="col">位点数</th><th scope="col">占比</th></tr></thead>
              <tbody>
                {activeSeries.bins.map((bin) => (
                  <tr key={bin.coordinationNumber}>
                    <th scope="row">{bin.coordinationNumber}</th>
                    <td>{bin.count}</td>
                    <td>{percent(bin.fraction)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      {pairs.length ? (
        <details className="coordination-histogram-detail">
          <summary>元素邻接计数 · {pairs.length} 组</summary>
          <div className="workspace-table-scroll">
            <table>
              <thead><tr><th scope="col">中心元素</th><th scope="col">邻近元素</th><th scope="col">计数</th></tr></thead>
              <tbody>{pairs.map((pair, index) => <tr key={`${text(pair.center_element)}:${text(pair.neighbor_element)}:${index}`}><td>{text(pair.center_element)}</td><td>{text(pair.neighbor_element)}</td><td>{integer(pair.count)}</td></tr>)}</tbody>
            </table>
          </div>
        </details>
      ) : null}

      <section className="coordination-histogram-method" aria-label="方法与限制">
        <div>
          <h6>方法边界</h6>
          <p>本结果仅执行固定距离截断邻居统计，不等同于 CrystalNN、VoronoiNN 或化学键级判断。</p>
        </div>
        <dl>
          <Metric label="最大位点数" value={integer(limits.max_sites)} />
          <Metric label="每位点最大邻居" value={integer(limits.max_neighbors_per_site)} />
          <Metric label="截断前位点数" value={integer(limits.site_count_before_truncation)} />
        </dl>
      </section>

      {warnings.length ? (
        <details className="coordination-histogram-detail">
          <summary>警告与限制 · {warnings.length}</summary>
          <ul>{warnings.map((warning, index) => <li key={`${warning}:${index}`}>{warningLabel(warning)}</li>)}</ul>
        </details>
      ) : null}
    </section>
  );
}

export function inspectCoordinationHistogram(
  artifacts: readonly Artifact[],
): { ok: true; payload: JsonRecord; plot: JsonRecord | null } | { ok: false; reason: string } {
  const payload = artifacts
    .map(artifactPayload)
    .find((item) => item?.schema_version === HISTOGRAM_SCHEMA && item.artifactType === "structure.coordination_hist");
  if (!payload) return { ok: false, reason: "COORDINATION_HISTOGRAM_CONTRACT_MISSING" };
  const security = record(payload.security);
  if (security.contains_javascript !== false
    || !Array.isArray(security.external_urls)
    || security.external_urls.length !== 0
    || security.external_urls_allowed !== false) {
    return { ok: false, reason: "COORDINATION_HISTOGRAM_SECURITY_INVALID" };
  }
  const histogram = record(payload.histogram);
  const bins = normalizedBins(histogram.bins);
  if (!bins.length
    || bins.length > MAX_BINS
    || bins.reduce((sum, item) => sum + item.count, 0) !== Number(histogram.total_sites)) {
    return { ok: false, reason: "COORDINATION_HISTOGRAM_BINS_INVALID" };
  }
  const byElement = records(payload.by_element);
  if (byElement.length > MAX_ELEMENTS || byElement.some((item) => !safeElement(item.element) || !normalizedBins(item.bins).length)) {
    return { ok: false, reason: "COORDINATION_HISTOGRAM_ELEMENT_GROUP_INVALID" };
  }
  if (records(payload.pair_counts).length > MAX_PAIRS || textList(payload.warnings).length > MAX_WARNINGS) {
    return { ok: false, reason: "COORDINATION_HISTOGRAM_PREVIEW_CAP_EXCEEDED" };
  }
  const plot = artifacts
    .map(artifactPayload)
    .find((item) => item?.schema_version === PLOT_SCHEMA && item.artifactType === "structure.coordination_hist_plot") ?? null;
  return { ok: true, payload, plot };
}

function HistogramChart({ series, summaryId }: Readonly<{ series: HistogramSeries; summaryId: string }>) {
  const maximum = Math.max(1, ...series.bins.map((item) => item.count));
  return (
    <>
      <div className="coordination-histogram-chart" role="img" aria-label={`${series.label}配位数分布，共 ${series.totalSites} 个位点`} aria-describedby={summaryId}>
        {series.bins.map((bin) => (
          <div className="coordination-histogram-bar-column" key={bin.coordinationNumber}>
            <span className="coordination-histogram-bar-value">{bin.count}</span>
            <span className="coordination-histogram-bar-track">
              <span className="coordination-histogram-bar" style={{ height: `${Math.max(3, bin.count / maximum * 100)}%` }} />
            </span>
            <span className="coordination-histogram-bar-label">{bin.coordinationNumber}</span>
          </div>
        ))}
      </div>
      <p id={summaryId} className="sr-only" data-testid="coordination-histogram-accessible-summary">
        {series.label}数据摘要：{series.bins.map((bin) => `配位数 ${bin.coordinationNumber}，${bin.count} 个位点，占比 ${percent(bin.fraction)}`).join("；")}。
      </p>
    </>
  );
}

function Metric({ label, value, tone }: Readonly<{ label: string; value: string; tone?: "success" | "warning" }>) {
  return <div data-tone={tone}><dt>{label}</dt><dd>{value || "未提供"}</dd></div>;
}

function histogramSeries(payload: JsonRecord): HistogramSeries[] {
  const histogram = record(payload.histogram);
  return [
    { id: "all", label: "全部位点", bins: normalizedBins(histogram.bins), totalSites: Number(histogram.total_sites) },
    ...records(payload.by_element).map((item) => ({
      id: `element:${text(item.element)}`,
      label: `${text(item.element)} 位点`,
      bins: normalizedBins(item.bins),
      totalSites: Number(item.total_sites),
    })),
  ];
}

function normalizedBins(value: unknown): HistogramBin[] {
  return records(value).flatMap((item) => {
    const coordinationNumber = Number(item.coordination_number);
    const count = Number(item.count);
    const fraction = Number(item.fraction);
    if (!Number.isSafeInteger(coordinationNumber)
      || coordinationNumber < 0
      || !Number.isSafeInteger(count)
      || count < 0
      || !Number.isFinite(fraction)
      || fraction < 0
      || fraction > 1.000001) return [];
    return [{ coordinationNumber, count, fraction }];
  });
}

function artifactPayload(artifact: Artifact): JsonRecord | null {
  const value = artifact.content ?? artifact.payload;
  return value && typeof value === "object" && !Array.isArray(value) ? value as JsonRecord : null;
}

function record(value: unknown): JsonRecord {
  return value && typeof value === "object" && !Array.isArray(value) ? value as JsonRecord : {};
}

function records(value: unknown): JsonRecord[] {
  return Array.isArray(value) ? value.filter((item): item is JsonRecord => Boolean(item && typeof item === "object" && !Array.isArray(item))) : [];
}

function text(value: unknown): string {
  return typeof value === "string" || typeof value === "number" ? String(value) : "";
}

function localizedCoordinationAxis(value: string, fallback: string): string {
  const normalized = value.trim().toLowerCase();
  if (!normalized) return fallback;
  if (normalized === "coordination number") return "配位数";
  if (normalized === "site count" || normalized === "sites") return "位点数";
  return value;
}

function textList(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

function integer(value: unknown): string {
  const parsed = Number(value);
  return Number.isSafeInteger(parsed) ? parsed.toLocaleString("zh-CN") : "未提供";
}

function format(value: unknown): string {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toLocaleString("zh-CN", { maximumFractionDigits: 6 }) : "未提供";
}

function percent(value: number): string {
  return `${(value * 100).toLocaleString("zh-CN", { maximumFractionDigits: 2 })}%`;
}

function safeElement(value: unknown): boolean {
  return typeof value === "string" && /^[A-Z][a-z]?$/.test(value);
}

function warningLabel(value: string): string {
  const labels: Readonly<Record<string, string>> = {
    COORDINATION_NEIGHBOR_POLICY_DISTANCE_CUTOFF_ONLY: "仅使用固定距离截断邻居策略。",
    COORDINATION_CUTOFF_SENSITIVE: "配位统计对截断半径敏感。",
    COORDINATION_ADVANCED_ENVIRONMENT_CLASSIFICATION_NOT_PERFORMED: "未执行高级局域环境分类。",
    COORDINATION_PARTIAL_OCCUPANCY_PRESENT: "源结构包含部分占位。",
  };
  const exact = labels[value];
  if (exact) return exact;
  if (value.startsWith("COORDINATION_SITES_TRUNCATED")) return `位点预览已按资源上限截断。${value.includes(":") ? ` ${value.split(":").slice(1).join(":").trim()}` : ""}`;
  if (value.startsWith("COORDINATION_NEIGHBORS_TRUNCATED")) return `邻居列表已按每位点上限截断。${value.includes(":") ? ` ${value.split(":").slice(1).join(":").trim()}` : ""}`;
  return value;
}
