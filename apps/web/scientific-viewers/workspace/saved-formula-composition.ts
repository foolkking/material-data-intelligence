import { readPlotCoordinates, readPlotNumericVector } from "./workspace-plot-data";

type Row = Record<string, unknown>;
const record = (value: unknown): Row => value && typeof value === "object" && !Array.isArray(value) ? value as Row : {};

export const isSavedFormulaComposition = (value: unknown) => record(value).artifactType === "composition.from_formula";

/** Read the saved percentages; never parse the formula or recalculate its chemistry. */
export function readSavedFormulaComposition(value: unknown) {
  const root = record(value), figure = record(root.plotlyFigure);
  if (!isSavedFormulaComposition(root) || root.schemaVersion !== "mdi.project.parameter-figure/1.0"
    || root.inputOrigin !== "USER_PARAMETERS" || root.sampleAnalysis !== false
    || typeof root.inputHash !== "string" || !/^[a-f0-9]{64}$/.test(root.inputHash)
    || !Array.isArray(figure.data) || figure.data.length !== 1) return null;
  const trace = record(figure.data[0]), x = readPlotCoordinates(trace.x), y = readPlotNumericVector(trace.y);
  if (trace.type !== "bar" || !x || !y || !x.length || x.length > 32 || x.length !== y.length
    || x.some(symbol => typeof symbol !== "string" || !/^[A-Z][a-z]?$/u.test(symbol))
    || new Set(x).size !== x.length || y.some(value => value <= 0 || value > 100)
    || Math.abs(y.reduce((total, value) => total + value, 0) - 100) > 1e-8) return null;
  return { label: "原子百分比（%）", elements: x.map((symbol, index) => ({ element: String(symbol), count: y[index], fraction: null })),
    textLabels: y.map(value => `${Number(value.toPrecision(6))}%`), omittedElements: 0, notes: [] as string[] };
}
