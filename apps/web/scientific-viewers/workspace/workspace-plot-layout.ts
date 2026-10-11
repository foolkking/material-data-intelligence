import { readPlotCoordinates } from "./workspace-plot-data";

type RecordValue = Record<string, unknown>;
const record = (value: unknown): RecordValue | null => value && typeof value === "object" && !Array.isArray(value) ? value as RecordValue : null;
const finite = (value: unknown): value is number => typeof value === "number" && Number.isFinite(value);
const axisRef = (value: unknown) => typeof value === "string" && /^[xy][2-8]?$/.test(value);
const sceneRef = (value: unknown) => typeof value === "string" && /^scene[2-4]?$/.test(value);
const colorRef = (value: unknown) => typeof value === "string" && /^coloraxis[2-8]?$/.test(value);
const label = (value: unknown) => String(record(value)?.text ?? value ?? "").replace(/<[^>]*>/g, "").slice(0, 160);
const pair = (value: unknown, domain = false): value is number[] => Array.isArray(value) && value.length === 2 && value.every(finite) && value[0] !== value[1]
  && (!domain || value[0] >= 0 && value[1] <= 1 && value[0] < value[1]);

/** Keep scientific coordinates and scale settings; presentation and executable
 * fields never pass through this allowlist. */
export function readPlotLayout(source: unknown, traces: RecordValue[]): RecordValue | null {
  const layout = record(source) ?? {};
  const result: RecordValue = {};
  const axes = new Set(["xaxis", "yaxis"]), scenes = new Set<string>();
  for (const key of Object.keys(layout)) {
    if (/^[xy]axis\d*$/.test(key)) {
      if (!/^[xy]axis[2-8]?$/.test(key)) return null;
      axes.add(key);
    }
    if (/^scene\d*$/.test(key)) { if (!sceneRef(key)) return null; scenes.add(key); }
    if (/^coloraxis\d*$/.test(key)) {
      if (!colorRef(key)) return null;
      const scale = readPlotColorScale(layout[key], "c");
      if (!scale) return null;
      result[key] = scale;
    }
  }
  for (const trace of traces) {
    for (const coordinate of ["x", "y"] as const) {
      const ref = trace[`${coordinate}axis`];
      if (ref !== undefined) {
        if (!axisRef(ref) || String(ref)[0] !== coordinate) return null;
        axes.add(`${coordinate}axis${String(ref).slice(1)}`);
      }
    }
    if (trace.type === "scatter3d" || trace.type === "mesh3d") {
      if (trace.scene !== undefined && !sceneRef(trace.scene)) return null;
      scenes.add(String(trace.scene ?? "scene"));
    }
    if (trace.coloraxis !== undefined && (!colorRef(trace.coloraxis) || !result[String(trace.coloraxis)])) return null;
  }
  for (const key of axes) {
    const axis = readAxis(layout[key]);
    if (!axis) return null;
    result[key] = axis;
  }
  for (const key of scenes) {
    const scene = record(layout[key]) ?? {};
    const xaxis = readAxis(scene.xaxis), yaxis = readAxis(scene.yaxis), zaxis = readAxis(scene.zaxis);
    if (!xaxis || !yaxis || !zaxis) return null;
    const domain = record(scene.domain);
    if (domain && (domain.x !== undefined && !pair(domain.x, true) || domain.y !== undefined && !pair(domain.y, true))) return null;
    result[key] = { aspectmode: "data", xaxis, yaxis, zaxis, ...(domain ? { domain: { x: domain.x, y: domain.y } } : {}) };
  }
  if (layout.barmode !== undefined) {
    if (!["group", "overlay", "stack", "relative"].includes(String(layout.barmode))) return null;
    result.barmode = layout.barmode;
  }
  // These transformations need their own scientific presentation contract.
  if (layout.grid !== undefined || layout.barnorm) return null;
  return result;
}

function readAxis(value: unknown): RecordValue | null {
  if (value !== undefined && !record(value)) return null;
  const axis = record(value) ?? {}, result: RecordValue = { title: { text: label(axis.title) }, automargin: true };
  // Logarithmic minor ticks must display their actual values (0.9, not 9).
  if (axis.type === "log") { result.tickformat = ".4~g"; result.nticks = 3; }
  const enums: Record<string, unknown[]> = {
    type: ["-", "linear", "log", "date", "category"], autorange: [true, false, "reversed", "min", "max", "min reversed", "max reversed"],
    side: ["top", "bottom", "left", "right"], tickmode: ["auto", "linear", "array"],
    categoryorder: ["trace", "category ascending", "category descending", "array", "total ascending", "total descending"],
    constrain: ["range", "domain"],
  };
  for (const [key, choices] of Object.entries(enums)) if (axis[key] !== undefined) {
    if (!choices.includes(axis[key])) return null;
    result[key] = axis[key];
  }
  if (axis.range !== undefined) {
    const range = axis.range;
    if (!pair(range) && !(axis.type === "date" && Array.isArray(range) && range.length === 2 && range.every(value => typeof value === "string" && value.length <= 100 && Number.isFinite(Date.parse(value))))) return null;
    result.range = [...range as unknown[]];
  }
  if (axis.domain !== undefined) { if (!pair(axis.domain, true)) return null; result.domain = [...axis.domain]; }
  for (const key of ["anchor", "overlaying", "matches", "scaleanchor"]) if (axis[key] !== undefined) {
    if (!axisRef(axis[key]) && axis[key] !== false && !(key === "anchor" && axis[key] === "free")) return null;
    result[key] = axis[key];
  }
  for (const key of ["position", "scaleratio", "tickangle"]) if (axis[key] !== undefined) {
    const number = axis[key];
    if (!finite(number) || key === "position" && (number < 0 || number > 1) || key === "scaleratio" && number <= 0 || key === "tickangle" && Math.abs(number) > 180) return null;
    result[key] = number;
  }
  for (const key of ["showticklabels", "zeroline"]) if (axis[key] !== undefined) {
    if (typeof axis[key] !== "boolean") return null;
    result[key] = axis[key];
  }
  for (const key of ["tickvals", "ticktext", "categoryarray"]) if (axis[key] !== undefined) {
    const values = readPlotCoordinates(axis[key]);
    if (!values || values.length > 256 || values.includes(null)) return null;
    result[key] = values.map(value => typeof value === "string" ? label(value) : value);
  }
  if (axis.rangebreaks !== undefined) return null;
  return result;
}

const colorNames = new Set(["Viridis", "Cividis", "RdBu", "RdYlBu", "RdYlGn", "Blues", "Reds", "Greys", "Greens", "YlGnBu", "YlOrRd", "Plasma", "Inferno", "Magma", "Turbo", "Jet", "Hot", "Rainbow", "Picnic", "Portland", "Electric", "Blackbody", "Earth"]);
function color(value: unknown): boolean {
  if (typeof value !== "string") return false;
  if (/^#[0-9a-f]{3}(?:[0-9a-f]{3})?$/i.test(value) || /^(?:red|blue|white|black|gray|grey|navy|green|yellow)$/i.test(value)) return true;
  const rgb = /^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*(0(?:\.\d+)?|1(?:\.0+)?))?\s*\)$/.exec(value);
  return Boolean(rgb && rgb.slice(1, 4).every(value => Number(value) <= 255));
}

export function readPlotColorScale(source: unknown, prefix: "z" | "c" = "z"): RecordValue | null {
  const trace = record(source);
  if (!trace) return null;
  const result: RecordValue = {};
  for (const key of [`${prefix}min`, `${prefix}max`, `${prefix}mid`]) if (trace[key] !== undefined) {
    if (!finite(trace[key])) return null;
    result[key] = trace[key];
  }
  if (finite(result[`${prefix}min`]) && finite(result[`${prefix}max`]) && Number(result[`${prefix}min`]) > Number(result[`${prefix}max`])) return null;
  for (const key of [`${prefix}auto`, "reversescale", "showscale"]) if (trace[key] !== undefined) {
    if (typeof trace[key] !== "boolean") return null;
    result[key] = trace[key];
  }
  const scale = trace.colorscale;
  if (scale !== undefined) {
    if (typeof scale === "string") { if (!colorNames.has(scale)) return null; result.colorscale = scale; }
    else if (Array.isArray(scale) && scale.length >= 2 && scale.length <= 256 && scale.every((stop, index) => Array.isArray(stop) && stop.length === 2 && finite(stop[0]) && stop[0] >= 0 && stop[0] <= 1 && color(stop[1]) && (!index || stop[0] >= scale[index - 1][0])) && scale[0][0] === 0 && scale[scale.length - 1][0] === 1) result.colorscale = scale.map(stop => [...stop]);
    else return null;
  }
  if (trace.coloraxis !== undefined) { if (!colorRef(trace.coloraxis)) return null; result.coloraxis = trace.coloraxis; }
  if (trace.colorbar !== undefined) {
    const bar = record(trace.colorbar);
    if (!bar) return null;
    result.colorbar = { title: { text: label(bar.title) } };
  }
  return result;
}
