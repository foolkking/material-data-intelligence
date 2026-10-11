import { readPlotNumericVector } from "./workspace-plot-data";

type RecordValue = Record<string, unknown>;
const MAX_NODES = 100_000;

/** Resolve hierarchy by saved identity, never by the display label when IDs exist. */
export function readPlotHierarchy(trace: RecordValue): RecordValue | null {
  const labels = strings(trace.labels), parents = strings(trace.parents);
  const values = readPlotNumericVector(trace.values);
  const ids = trace.ids === undefined ? labels : strings(trace.ids);
  if (!labels?.length || !parents || !values || !ids || labels.length > MAX_NODES
    || parents.length !== labels.length || values.length !== labels.length || ids.length !== labels.length
    || values.some(value => value < 0) || ids.some(id => !id)) return null;
  const indices = new Map(ids.map((id, index) => [id, index]));
  if (indices.size !== ids.length) return null;
  const parentIndices = parents.map(parent => parent === "" ? -1 : indices.get(parent) ?? -2);
  if (parentIndices.includes(-2)) return null;
  // Iterative marking bounds validation even for deeply nested untrusted data.
  const state = new Uint8Array(ids.length);
  for (let index = 0; index < ids.length; index += 1) {
    let current = index;
    const path: number[] = [];
    while (current >= 0 && state[current] === 0) {
      state[current] = 1;
      path.push(current);
      current = parentIndices[current];
    }
    if (current >= 0 && state[current] === 1) return null;
    for (const visited of path) state[visited] = 2;
  }
  const branchvalues = trace.branchvalues ?? "remainder";
  if (branchvalues !== "total" && branchvalues !== "remainder") return null;
  if (branchvalues === "total") {
    const sums = new Float64Array(ids.length);
    for (let index = 0; index < ids.length; index += 1) if (parentIndices[index] >= 0) sums[parentIndices[index]] += values[index];
    // Tolerance is relative to the actual total, including sub-unit data.
    // An absolute floor would admit children many times larger than a tiny parent.
    if (values.some((value, index) => !Number.isFinite(sums[index])
      || sums[index] > value && (sums[index] - value) / sums[index] > 1e-10)) return null;
  }
  if (trace.level !== undefined && (typeof trace.level !== "string" || trace.level !== "" && !indices.has(trace.level))) return null;
  if (trace.maxdepth !== undefined && (!Number.isSafeInteger(trace.maxdepth) || Number(trace.maxdepth) < -1 || trace.maxdepth === 0)) return null;
  if (trace.sort !== undefined && typeof trace.sort !== "boolean") return null;
  const textinfo = trace.textinfo === undefined ? "label" : trace.textinfo;
  if (typeof textinfo !== "string" || textinfo !== "none" && !textinfo.split("+").every(value => ["label", "value", "percent root", "percent parent", "percent entry", "current path"].includes(value))) return null;
  const domain = trace.domain as RecordValue | undefined;
  if (domain !== undefined && (!domain || typeof domain !== "object" || Array.isArray(domain)
    || Object.keys(domain).some(key => key !== "x" && key !== "y")
    || Object.values(domain).some(value => !Array.isArray(value) || value.length !== 2
      || !value.every(number => typeof number === "number" && Number.isFinite(number))
      || value[0] < 0 || value[1] > 1 || value[0] >= value[1]))) return null;
  // Keep opaque IDs out of Plotly's displayed strings while maintaining a
  // one-to-one mapping. The exact originals remain in the numerical table.
  const renderIds = ids.map((_, index) => `node-${index}`);
  return {
    ids: renderIds,
    labels: labels.map(label => label.replace(/<[^>]*>/g, "").slice(0, 160)),
    parents: parentIndices.map(index => index < 0 ? "" : renderIds[index]), values, branchvalues, textinfo,
    ...(domain ? { domain: Object.fromEntries(Object.entries(domain).map(([key, value]) => [key, [...value as number[]]])) } : {}),
    ...(trace.level !== undefined ? { level: trace.level === "" ? "" : renderIds[indices.get(String(trace.level))!] } : {}),
    ...(trace.maxdepth !== undefined ? { maxdepth: trace.maxdepth } : {}),
    ...(trace.sort !== undefined ? { sort: trace.sort } : {}),
  };
}

function strings(value: unknown): string[] | null {
  return Array.isArray(value) && value.length <= MAX_NODES
    && value.every(item => typeof item === "string" && item.length <= 1024) ? [...value] : null;
}
