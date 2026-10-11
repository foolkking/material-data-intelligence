type JsonRecord = Record<string, unknown>;
type RdfSeries = { radius: number[]; values: number[]; counts: number[] };
const record = (value: unknown): JsonRecord | null => value !== null && typeof value === "object" && !Array.isArray(value) ? value as JsonRecord : null;
const label = (value: unknown): value is string => typeof value === "string" && Boolean(value.trim());
const nonnegative = (value: unknown): value is number => typeof value === "number" && Number.isFinite(value) && value >= 0;

function series(radius: unknown, values: unknown, counts: unknown, maxBins: number): RdfSeries | null {
  if (!Array.isArray(radius) || !radius.length || radius.length > maxBins
      || !radius.every((value, index) => nonnegative(value) && (index === 0 || value > radius[index - 1]))
      || !Array.isArray(values) || values.length !== radius.length || !values.every(nonnegative)
      || !Array.isArray(counts) || counts.length !== radius.length
      || !counts.every(value => nonnegative(value) && Number.isSafeInteger(value))) return null;
  return { radius, values, counts };
}

function rows(data: RdfSeries, pair: string, pairColumn: string): JsonRecord[] {
  return data.radius.map((radius, index) => ({
    [pairColumn]: pair, "距离 r (Å)": radius, "g(r)": data.values[index], "计数": data.counts[index],
  }));
}

/** Present saved RDF arrays only. Invalid known schemas must not fall through to generic rows. */
export function savedRdfTableRows(payload: unknown): JsonRecord[] | null {
  const value = record(payload);
  if (value?.artifactType === "structure.rdf") {
    if (value.schema_version !== "phase10e7.rdf.v1") return [];
    const rdf = record(value.rdf), partial = value.partial_rdf;
    const total = series(rdf?.r_angstrom, rdf?.g_r, rdf?.counts, 5000);
    if (!total || !Array.isArray(partial) || partial.length > 256) return [];
    const pairs = new Set<string>();
    const distributions: { data: RdfSeries; pair: string }[] = [{ data: total, pair: "全部原子对" }];
    for (const item of partial) {
      const part = record(item);
      if (!part || !label(part.center_element) || !label(part.neighbor_element)) return [];
      const identity = JSON.stringify([part.center_element, part.neighbor_element]);
      const data = series(part.r_angstrom, part.g_r, part.counts, 5000);
      if (pairs.has(identity) || !data || data.radius.length !== total.radius.length
          || data.radius.some((radius, index) => radius !== total.radius[index])) return [];
      pairs.add(identity);
      distributions.push({ data, pair: `${part.center_element} → ${part.neighbor_element}` });
    }
    return distributions.flatMap(({ data, pair }) => rows(data, pair, "中心 → 邻居"));
  }
  if (value?.artifactType === "trajectory.rdf") {
    const units = record(value.units), pair = record(value.speciesPair);
    if (value.schema_version !== "phase10n4.trajectory_rdf.v1" || units?.r !== "angstrom" || units.gR !== "dimensionless"
        || !pair || pair.ordered !== false || !label(pair.speciesA) || !label(pair.speciesB)) return [];
    const data = series(value.binCentersAngstrom, value.gR, value.pairCounts, 2048);
    return data ? rows(data, `${pair.speciesA} – ${pair.speciesB}`, "原子对") : [];
  }
  return null;
}
