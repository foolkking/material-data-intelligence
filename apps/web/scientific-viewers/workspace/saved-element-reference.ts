import { readPlatformReferences } from "../../app/lib/platform-reference";
import { readPlotCoordinates, readPlotNumericVector } from "./workspace-plot-data";

type Row = Record<string, unknown>;
const record = (value: unknown): Row => value && typeof value === "object" && !Array.isArray(value) ? value as Row : {};
const finite = (value: unknown): value is number => typeof value === "number" && Number.isFinite(value);
const SYMBOLS = "H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og".split(" ");
export const isSavedElementReference = (value: unknown) => ["reference.periodic_table", "reference.compare_elements"].includes(String(record(value).artifactType));
export const isSavedElementComparison = (value: unknown) => record(value).artifactType === "reference.compare_elements";

/** Verify saved identities, selection and missing values without calculating properties. */
export function readSavedElementReference(value: unknown) {
  const root = record(value), comparison = isSavedElementComparison(root);
  if (!isSavedElementReference(root) || root.schemaVersion !== "mdi.reference.element-figure/1.0"
    || root.inputOrigin !== "PLATFORM_REFERENCE" || root.sampleAnalysis !== false || root.log !== false
    || !["atomic_number", "covalent_radius"].includes(String(root.property))
    || !Array.isArray(root.elementIdentities) || root.elementIdentities.length !== 118) return null;
  const identities = new Map<string, { symbol: string; atomicNumber: number; name: string }>();
  for (const [index, raw] of root.elementIdentities.entries()) {
    const item = record(raw);
    if (item.symbol !== SYMBOLS[index] || item.atomicNumber !== index + 1 || typeof item.name !== "string" || !/^[A-Za-z -]{1,64}$/u.test(item.name)) return null;
    identities.set(SYMBOLS[index], { symbol: SYMBOLS[index], atomicNumber: index + 1, name: item.name });
  }
  const symbols = (raw: unknown, min: number, max: number): string[] | null => Array.isArray(raw) && raw.length >= min && raw.length <= max
    && raw.every(item => typeof item === "string" && identities.has(item)) && new Set(raw).size === raw.length ? raw : null;
  const selected = symbols(root.selectedElements, comparison ? 2 : 1, comparison ? 20 : 118);
  const missing = symbols(root.missingElements, 0, 118), highlighted = symbols(root.highlightElements, 0, comparison ? 0 : 118);
  const values = record(root.elementValues), keys = Object.keys(values), property = String(root.property);
  if (!selected || !missing || !highlighted || !keys.length || root.elementCount !== selected.length || root.valueCount !== keys.length
    || keys.some(key => !selected.includes(key) || !finite(values[key]) || Number(values[key]) <= 0)
    || selected.some(key => !keys.includes(key) && !missing.includes(key)) || missing.some(key => !selected.includes(key) || keys.includes(key))
    || highlighted.some(key => !selected.includes(key))
    || property === "atomic_number" && (missing.length > 0 || keys.some(key => values[key] !== identities.get(key)!.atomicNumber))
    || root.unit !== (property === "covalent_radius" ? "angstrom" : null)) return null;
  const source = record(root.referenceSource), definition = record(source.propertyDefinition);
  const references = readPlatformReferences([{ ...source, name: "元素参考资料", properties: { [property]: definition } }]);
  if (references.length !== 1 || references[0].referenceId !== "elements" || definition.unit !== root.unit) return null;
  const label = property === "covalent_radius" ? "参考共价半径（Å）" : "原子序数";
  if (root.valueLabel !== label) return null;
  return { property, label, values: values as Record<string, number>, selected, missing, highlighted, identities, references,
    notes: missing.length ? [`参考值缺失：${missing.join("、")}`] : [] };
}

export function readSavedElementComparison(value: unknown) {
  const reference = readSavedElementReference(value), figure = record(record(value).plotlyFigure);
  if (!isSavedElementComparison(value) || !reference || !Array.isArray(figure.data) || figure.data.length !== 1) return null;
  const trace = record(figure.data[0]), x = readPlotCoordinates(trace.x), y = readPlotNumericVector(trace.y);
  const selected = reference.selected.filter(symbol => !reference.missing.includes(symbol));
  if (trace.type !== "bar" || !x || !y || x.length !== selected.length || y.length !== x.length
    || selected.some((symbol, index) => x[index] !== symbol || y[index] !== reference.values[symbol])) return null;
  return { ...reference, elements: selected.map(symbol => ({ element: symbol, count: reference.values[symbol], fraction: null })),
    textLabels: selected.map(symbol => String(reference.values[symbol])), omittedElements: 0 };
}
