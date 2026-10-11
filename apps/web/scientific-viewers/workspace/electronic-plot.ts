export type ElectronicPoint = readonly [number, number];
export type ElectronicCurve = { id: string; label: string; spin: string; segments: ElectronicPoint[][]; sampled: boolean };
export type ElectronicPlotData = { curves: ElectronicCurve[]; xDomain: [number, number]; yDomain: [number, number]; ticks: { value: number; label: string }[]; totalSeries: number; invalidSeries: number };
type Row = Record<string, unknown>;
export const ELECTRONIC_POINT_LIMIT = 2_400;

export function electronicPlotData(payload: Row, kind: "band" | "dos"): ElectronicPlotData {
  const kpoints = rows(payload.kpoints);
  const source = kind === "band" ? rows(payload.bands) : [...rows(payload.totalDos), ...rows(payload.projections)];
  const x = finiteValues(kind === "band" ? kpoints.map(point => point.pathDistance) : payload.energiesEv);
  const cap = kind === "band" ? 48 : 24;
  const curves: ElectronicCurve[] = [];
  let invalidSeries = 0;
  let yMin = Infinity, yMax = -Infinity;
  const cuts = new Set<number>();
  let validPath = true;
  if (kind === "band") {
    const indices = new Map(kpoints.map((point, index) => [point.kpointId, index]));
    for (const segment of rows(payload.pathSegments)) {
      if (segment.breakAfter !== true) continue;
      const end = indices.get(segment.endKpointId);
      if (end === undefined) validPath = false;
      else if (end + 1 < kpoints.length) cuts.add(end + 1);
    }
  }
  for (const [index, item] of source.slice(0, cap).entries()) {
    const y = finiteValues(kind === "band" ? item.energiesEv : item.values);
    if (!validPath || !x || !y || !x.length || y.length !== x.length) { invalidSeries++; continue; }
    const indices = sampledIndices(y, cuts, ELECTRONIC_POINT_LIMIT);
    if (!indices) { invalidSeries++; continue; }
    for (const value of y) { yMin = Math.min(yMin, value); yMax = Math.max(yMax, value); }
    const segments: ElectronicPoint[][] = [];
    let current: ElectronicPoint[] = [];
    for (const i of indices) {
      if (cuts.has(i) && current.length) { segments.push(current); current = []; }
      current.push([x[i], y[i]]);
    }
    if (current.length) segments.push(current);
    const spin = typeof item.spinChannel === "string" ? item.spinChannel : "none";
    const label = kind === "band" ? `能带 ${String(item.bandId ?? index + 1)}` : typeof item.label === "string" ? item.label : item.projectionKind ? String(item.channelId ?? `投影 ${index + 1}`) : "总态密度";
    curves.push({ id: String(item.bandIdentity ?? item.channelIdentity ?? index), label: `${label}${spin === "none" ? "" : ` · ${electronicSpinLabel(spin)}`}`, spin, segments, sampled: indices.length < y.length });
  }
  const ticks = new Map<number, string>();
  if (kind === "band" && x) for (const [index, point] of kpoints.entries()) {
    if (typeof point.label !== "string" || !point.label.trim()) continue;
    const label = point.label.trim();
    ticks.set(x[index], ticks.has(x[index]) ? [...new Set([ticks.get(x[index]), label])].join(" | ") : label);
  }
  return { curves, xDomain: domain(x ?? []), yDomain: range(yMin, yMax, kind === "dos"), ticks: [...ticks].map(([value, label]) => ({ value, label })), totalSeries: source.length, invalidSeries };
}

// Keep original coordinate/value pairs, segment endpoints and bucket extrema.
// Sampling only limits display geometry; it never changes the source payload.
function sampledIndices(y: number[], cuts: ReadonlySet<number>, limit: number): number[] | null {
  if (y.length <= limit) return y.map((_, i) => i);
  const selected = new Set([0, y.length - 1]);
  for (const cut of cuts) { selected.add(cut - 1); selected.add(cut); }
  if (selected.size > limit) return null;
  const buckets = Math.floor((limit - selected.size) / 2);
  for (let bucket = 0; bucket < buckets; bucket++) {
    const start = Math.floor(bucket * y.length / buckets), end = Math.floor((bucket + 1) * y.length / buckets);
    let min = start, max = start;
    for (let i = start + 1; i < end; i++) { if (y[i] < y[min]) min = i; if (y[i] > y[max]) max = i; }
    selected.add(min); selected.add(max);
  }
  for (let i = 0; i < limit && selected.size < limit; i++) selected.add(Math.round(i * (y.length - 1) / (limit - 1)));
  return [...selected].sort((a, b) => a - b);
}
function domain(values: readonly number[]): [number, number] {
  let min = Infinity, max = -Infinity;
  for (const value of values) { min = Math.min(min, value); max = Math.max(max, value); }
  return range(min, max);
}
function range(min: number, max: number, includeZero = false): [number, number] {
  if (!Number.isFinite(min) || !Number.isFinite(max)) return [0, 1];
  if (includeZero) { min = Math.min(0, min); max = Math.max(0, max); }
  if (min === max) { const padding = Math.max(Math.abs(min) * 0.05, 1); return [min - padding, max + padding]; }
  return [min, max];
}
function finiteValues(value: unknown): number[] | null { return Array.isArray(value) && value.every(item => typeof item === "number" && Number.isFinite(item)) ? value : null; }
function rows(value: unknown): Row[] { return Array.isArray(value) ? value.filter((item): item is Row => item !== null && typeof item === "object" && !Array.isArray(item)) : []; }
export function electronicSpinLabel(spin: string): string { return ({ none: "未区分自旋", up: "自旋 ↑", down: "自旋 ↓" } as Record<string, string>)[spin] ?? spin; }
export function electronicNumber(value: number): string { return Math.abs(value) >= 10_000 || (value !== 0 && Math.abs(value) < 0.001) ? value.toExponential(2) : Number(value.toPrecision(4)).toString(); }
