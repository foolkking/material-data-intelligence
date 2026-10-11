import { readPlotNumericMatrix, readPlotNumericVector } from "./workspace-plot-data";
import { readPlotColorScale } from "./workspace-plot-layout";
import { readSavedElementReference } from "./saved-element-reference";
import { readablePlotLabelColor, savedReportColorScale } from "../../app/lib/scientific-report-color-scale";

type Row = Record<string, unknown>;
const record = (value: unknown): Row | null => value && typeof value === "object" && !Array.isArray(value) ? value as Row : null;
const finite = (value: unknown): value is number => typeof value === "number" && Number.isFinite(value);
const symbol = (value: string) => /^[A-Z][a-z]?$/.test(value);

export function isSavedPeriodicTable(content: unknown): boolean {
  return ["composition.ptable_heatmap", "reference.periodic_table"].includes(String(record(content)?.artifactType));
}

export function readPeriodicElementValues(content: unknown) {
  const source = record(content);
  if (!isSavedPeriodicTable(source)) return null;
  if (source?.artifactType === "reference.periodic_table") {
    const reference = readSavedElementReference(content);
    return reference ? { values: reference.values, label: reference.label } : null;
  }
  const values = record(source?.elementValues);
  if (!values) return null;
  const entries = Object.entries(values);
  if (!entries.length || entries.length > 118 || entries.some(([key, value]) => !symbol(key) || !finite(value) || value < 0)) return null;
  const mode = String(source?.countMode ?? "").trim().toLowerCase().replace(/[- ]/g, "_");
  if (!["", "occurrence", "formula_presence", "fractional", "fraction", "fractional_composition", "stoichiometric", "composition", "count", "stoichiometric_count"].includes(mode)) return null;
  const label = ["fractional", "fraction", "fractional_composition"].includes(mode) ? "累计原子分数"
    : ["stoichiometric", "composition", "count", "stoichiometric_count"].includes(mode) ? "化学计量数之和" : mode ? "出现次数" : "数值";
  return { values: Object.fromEntries(entries) as Record<string, number>, label };
}

/** The adapter stores three drawing layers and 180 grid annotations. Only its
 * named element values are scientific observations; background cells are not. */
export function readSavedPeriodicTable(content: unknown) {
  const source = record(content), entries = readPeriodicElementValues(source);
  const reference = source?.artifactType === "reference.periodic_table" ? readSavedElementReference(source) : null;
  const figure = record(source?.plotlyFigure), layout = record(figure?.layout);
  if (!entries || typeof source?.log !== "boolean" || !Array.isArray(figure?.data) || figure.data.length !== 3
    || !Array.isArray(layout?.annotations) || layout.annotations.length !== 180) return null;
  const traces = figure.data.map(record);
  if (traces.some(trace => !trace || trace.type !== "heatmap" || trace.transpose === true
    || ["x", "y", "x0", "y0", "dx", "dy", "xaxis", "yaxis", "coloraxis"].some(key => trace[key] !== undefined)
    || trace.zsmooth !== undefined && trace.zsmooth !== false)) return null;
  for (const key of ["xaxis", "yaxis"]) {
    const axis = record(layout[key]);
    if (axis && (axis.type !== undefined && axis.type !== "linear" || axis.range !== undefined
      || axis.autorange !== undefined && axis.autorange !== true)) return null;
  }
  const grids = traces.map(trace => readPlotNumericMatrix(trace!.z));
  if (grids.some(grid => !grid || grid.length !== 10 || grid.some(row => row.length !== 18))) return null;
  if (!grids[2]!.some(row => row.some(finite))) return null;
  const annotations: Row[] = [], positions = new Map<string, [number, number]>(), occupied = new Set<string>();
  for (const value of layout.annotations) {
    const annotation = record(value);
    if (!annotation || !Number.isSafeInteger(annotation.x) || !Number.isSafeInteger(annotation.y)
      || Number(annotation.x) < 0 || Number(annotation.x) > 17 || Number(annotation.y) < 0 || Number(annotation.y) > 9
      || annotation.xref !== "x" || annotation.yref !== "y" || annotation.showarrow !== false || typeof annotation.text !== "string") return null;
    const x = Number(annotation.x), y = Number(annotation.y), cell = `${x}:${y}`;
    if (occupied.has(cell)) return null;
    occupied.add(cell);
    const name = annotation.text.replace(/<br\s*\/?\s*>/gi, "\n").replace(/<[^>]*>/g, "").split("\n")[0].trim();
    if (!name) continue;
    if (!symbol(name) || positions.has(name)) return null;
    positions.set(name, [x, y]);
    const color = record(annotation.font)?.color;
    if (typeof color !== "string" || !/^#[0-9a-f]{6}$/i.test(color)) return null;
    const selected = !reference || reference.selected.includes(name);
    annotations.push({ x, y, xref: "x", yref: "y", text: name, showarrow: false, name: `element:${name}`,
      font: { color: selected ? color : "#79837e", size: 12, family: "ui-monospace, SFMono-Regular, Consolas, monospace" } });
  }
  if (!positions.size || positions.size > 118 || Object.keys(entries.values).some(name => !positions.has(name))) return null;
  if (reference && (positions.size !== 118 || [...positions.keys()].some(name => !reference.identities.has(name)))) return null;
  const shapes: Row[] = [];
  if (reference) {
    const savedShapes = layout.shapes === undefined ? [] : layout.shapes;
    if (!Array.isArray(savedShapes) || savedShapes.length !== reference.highlighted.length * 2) return null;
    for (const name of reference.highlighted) {
      const [x, y] = positions.get(name)!;
      for (const [kind, width, color] of [["outer", 5, "#ffffff"], ["inner", 2.5, "#17211e"]] as const) {
        const matched = savedShapes.map(record).filter(shape => shape?.name === `highlight-${kind}:${name}`);
        const shape = matched.length === 1 ? matched[0] : null, line = record(shape?.line);
        if (!shape || shape.type !== "rect" || shape.xref !== "x" || shape.yref !== "y" || shape.layer !== "above"
          || shape.x0 !== x - .44 || shape.x1 !== x + .44 || shape.y0 !== y - .44 || shape.y1 !== y + .44
          || shape.fillcolor !== "rgba(0,0,0,0)" || line?.width !== width || line.color !== color) return null;
        shapes.push({ type: "rect", name: shape.name, xref: "x", yref: "y", x0: x - .44, x1: x + .44,
          y0: y - .44, y1: y + .44, line: { width, color }, fillcolor: "rgba(0,0,0,0)", layer: "above" });
      }
    }
  }
  const namedCells = new Set([...positions.values()].map(([x, y]) => `${x}:${y}`));
  for (let y = 0; y < 10; y += 1) for (let x = 0; x < 18; x += 1) {
    const border = grids[0]![y][x], background = grids[1]![y][x];
    if (border !== null && border !== 1 || background !== null && background !== 1) return null;
    if (!namedCells.has(`${x}:${y}`) && (border !== null || background !== null || grids[2]![y][x] !== null)) return null;
  }
  for (const [name, [x, y]] of positions) {
    const raw = entries.values[name];
    const expected = raw === undefined || source.log && raw <= 0 ? null : source.log ? Math.log10(raw) : raw;
    const saved = grids[2]![y][x];
    if (expected === null ? saved !== null : saved === null || Math.abs(saved - expected) > Math.max(1, Math.abs(expected)) * 1e-10) return null;
  }
  const texts = Array.from({ length: 10 }, () => Array<string>(18).fill(""));
  for (const [name, [x, y]] of positions) {
    const identity = reference?.identities.get(name);
    texts[y][x] = reference && identity ? `${identity.atomicNumber} · ${name} · ${identity.name}<br>${reference.selected.includes(name)
      ? `${reference.label}：${entries.values[name] ?? "参考值缺失"}` : "未选入本次范围"}` : `${name}: ${entries.values[name] ?? "未提供"}`;
  }
  const data: Row[] = [];
  for (let index = 0; index < 3; index += 1) {
    const trace = traces[index]!;
    const colorscale = Array.isArray(trace.colorscale) ? trace.colorscale.map(stop => Array.isArray(stop) && stop[1] === "darkgray" ? [stop[0], "#a9a9a9"] : stop) : trace.colorscale;
    const scale = readPlotColorScale({ ...trace, colorscale });
    if (!scale || scale.colorscale === undefined || trace.showscale !== (index === 2) || !finite(trace.xgap) || !finite(trace.ygap)) return null;
    const bar = record(trace.colorbar);
    const tickvals = bar?.tickvals === undefined ? undefined : readPlotNumericVector(bar.tickvals);
    const ticktext = bar?.ticktext;
    if (tickvals === null || ticktext !== undefined && !tickvals) return null;
    if (tickvals) {
      if (!Array.isArray(ticktext) || tickvals.length !== ticktext.length || tickvals.length > 32 || !tickvals.every(finite)
        || ticktext.some(value => typeof value !== "string" || value.length > 32 || /[<>]/.test(value))) return null;
      if (source.log && tickvals.some((tick, i) => {
        const raw = Number(ticktext[i]), expected = 10 ** tick;
        return !finite(raw) || raw <= 0 || !finite(expected) || Math.abs(raw - expected) > Math.max(raw, expected) * 1e-8;
      })) return null;
    }
    data.push({ type: "heatmap", z: grids[index], ...scale, xgap: index ? 2 : 1, ygap: index ? 2 : 1,
      hoverinfo: index < (reference ? 1 : 2) ? "skip" : undefined,
      hovertemplate: index >= (reference ? 1 : 2) ? "%{text}<extra></extra>" : undefined, text: index >= (reference ? 1 : 2) ? texts : undefined,
      colorbar: { orientation: "h", x: 0.5, xanchor: "center", yref: "container", y: 0.015, yanchor: "bottom", len: 0.85, thickness: 10,
        title: { text: "" }, tickangle: 0, ...(tickvals ? { tickvals, ticktext } : { nticks: 4 }) },
    });
  }
  const title = record(layout.title)?.text;
  if (reference) {
    const scales = data.map(savedReportColorScale);
    if (scales.some(scale => !scale)) return null;
    for (const annotation of annotations) {
      const x = Number(annotation.x), y = Number(annotation.y);
      const layer = [2, 1, 0].find(index => grids[index]![y][x] !== null);
      const background = layer === undefined ? "#ffffff" : scales[layer]!.fill(grids[layer]![y][x]!);
      annotation.font = { ...record(annotation.font), color: readablePlotLabelColor(background) };
    }
  }
  const cells = [...positions].map(([name, [x, y]]) => ({ symbol: name, x, y, atomicNumber: reference?.identities.get(name)?.atomicNumber,
    selected: !reference || reference.selected.includes(name), highlighted: reference?.highlighted.includes(name) ?? false,
    color: String(record(annotations.find(a => a.text === name)?.font)?.color ?? "#17211e") }));
  const numberAnnotations = reference ? cells.map(cell => ({ x: cell.x, y: cell.y + .27, xref: "x", yref: "y", showarrow: false,
    text: String(cell.atomicNumber), name: `atomic-number:${cell.symbol}`, font: { size: 12, color: cell.color } })) : [];
  return { data, cells, pointCount: Object.keys(entries.values).length, layout: {
    autosize: true, margin: { l: 12, r: 12, t: 42, b: 84 }, paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff", showlegend: false, hovermode: "closest",
    title: { text: title === "Periodic Table Heatmap" ? "元素周期表" : typeof title === "string" ? title.replace(/<[^>]*>/g, "").slice(0, 160) : "元素周期表" },
    xaxis: { range: [-0.5, 17.5], showgrid: false, showticklabels: false, ticks: "", zeroline: false, fixedrange: true },
    yaxis: { range: [-0.5, 9.5], showgrid: false, showticklabels: false, ticks: "", zeroline: false, scaleanchor: "x", fixedrange: true },
    // A separate label avoids Plotly's horizontal colorbar title overlapping
    // the gradient when the bar uses container-relative coordinates.
    shapes,
    annotations: [...annotations, ...numberAnnotations, { x: 0.5, y: 0, xref: "paper", yref: "paper", yshift: -28, showarrow: false,
      text: `${entries.label}${source.log ? "（对数色阶）" : ""}`, font: { size: 12, color: "#333333" } }],
  } };
}

/** Keep all elements in view; secondary atomic numbers appear when cells have room. */
export function periodicLayoutForWidth(layout: Row, width: number): Row {
  if (!Array.isArray(layout.annotations) || !layout.annotations.some(a => String(record(a)?.name).startsWith("atomic-number:"))) return layout;
  const detailed = width >= 650;
  return { ...layout, annotations: layout.annotations.filter(a => detailed || !String(record(a)?.name).startsWith("atomic-number:")).map(value => {
    const annotation = record(value)!;
    return String(annotation.name).startsWith("element:") ? { ...annotation, y: Number(annotation.y) - (detailed ? .08 : 0),
      font: { ...record(annotation.font), size: detailed ? 14 : 12 } } : annotation;
  }) };
}
