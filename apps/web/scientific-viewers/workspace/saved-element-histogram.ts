import { readPlotCoordinates, readPlotNumericVector } from "./workspace-plot-data";

type Row = Record<string, unknown>;
const record = (value: unknown): Row => value && typeof value === "object" && !Array.isArray(value) ? value as Row : {};
const positive = (value: unknown): value is number => typeof value === "number" && Number.isFinite(value) && value > 0;
const close = (a: number, b: number) => Math.abs(a - b) <= 1e-12 * Math.max(1, Math.abs(a), Math.abs(b));

export function isSavedElementHistogram(value: unknown): boolean {
  return record(value).artifactType === "composition.elements_hist";
}

/** Compare saved scientific identities and counts; never choose between contradictory outputs. */
export function readSavedElementHistogram(value: unknown) {
  const root = record(value), figure = record(root.plotlyFigure);
  if (!isSavedElementHistogram(root) || root.chartType !== "bar"
    || root.schemaVersion !== undefined && root.schemaVersion !== "mdi.element-histogram/1.0"
    || !["occurrence", "stoichiometric", "fractional"].includes(String(root.countMode))
    || !Array.isArray(root.bars) || !root.bars.length || root.bars.length > 118
    || !Number.isSafeInteger(root.elementCount) || Number(root.elementCount) < root.bars.length || Number(root.elementCount) > 118
    || !Array.isArray(figure.data) || figure.data.length !== 1) return null;
  const trace = record(figure.data[0]), x = readPlotCoordinates(trace.x), y = readPlotNumericVector(trace.y);
  if (trace.type !== "bar" || !x || !y || x.length !== root.bars.length || y.length !== x.length
    || new Set(x).size !== x.length || !y.every(positive)) return null;
  const values = new Map<string, { element: string; count: number; fraction: number }>();
  for (const entry of root.bars) {
    const bar = record(entry);
    if (typeof bar.element !== "string" || !/^[A-Z][a-z]?$/u.test(bar.element) || values.has(bar.element)
      || !positive(bar.count) || !positive(bar.fraction) || bar.fraction > 1) return null;
    values.set(bar.element, { element: bar.element, count: bar.count, fraction: bar.fraction });
  }
  const total = [...values.values()].reduce((sum, bar) => sum + bar.count, 0);
  if (!Number.isFinite(total) || [...values.values()].some(bar => !close(bar.fraction, bar.count / total))) return null;
  const elements = [];
  for (let index = 0; index < x.length; index++) {
    const element = values.get(String(x[index]));
    if (!element || element.count !== y[index]) return null;
    elements.push(element);
  }
  const omittedElements = Number(root.elementCount) - elements.length;
  if (root.schemaVersion && (root.fractionScope !== "displayed_elements" || root.omittedElementCount !== omittedElements
    || !positive(root.retainedElementValue) || !close(root.retainedElementValue, total)
    || !positive(root.totalElementValue) || root.totalElementValue < total && !close(root.totalElementValue, total)
    || !omittedElements && !close(root.totalElementValue, total)
    || ![null, "count", "percent"].includes(root.showValues as string | null))) return null;
  let textLabels: string[] | null = null;
  if (root.schemaVersion && root.showValues !== null) {
    if (!Array.isArray(trace.text) || trace.text.length !== elements.length) return null;
    textLabels = [];
    for (let index = 0; index < trace.text.length; index++) {
      const text = trace.text[index];
      if (typeof text !== "string" || text.length > 64) return null;
      if (root.showValues === "count") {
        if (!/^[\d.eE+-]+$/u.test(text) || Number(text) !== elements[index].count) return null;
      } else if (!/^\d+(?:\.\d+)?%$/u.test(text) || Math.abs(Number(text.slice(0, -1)) - elements[index].fraction * 100) > 0.500000001) return null;
      textLabels.push(text);
    }
  }
  const label = root.countMode === "fractional" ? "分数贡献总和" : root.countMode === "stoichiometric" ? "化学计量总数" : "元素出现次数";
  return { elements, label, textLabels, omittedElements, notes: omittedElements
    ? [`仅显示前 ${elements.length} 个元素，省略 ${omittedElements} 个元素；百分比以显示元素的合计值为分母。`] : [] };
}
