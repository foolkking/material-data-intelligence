export type PlatformReference = {
  referenceId: string; version: string; contentHash: string; name: string;
  sources: Array<{ name: string; url: string; version?: string; license?: string; use?: string }>;
  properties: Record<string, { label: string; unit?: string | null; definition: string; coverage?: string; citation?: string }>;
};
const record = (v: unknown): Record<string, unknown> => v && typeof v === "object" && !Array.isArray(v) ? v as Record<string, unknown> : {};
const text = (v: unknown, max = 1024): v is string => typeof v === "string" && v.length > 0 && v.length <= max;

export function publicReferenceUrl(value: unknown): string | null {
  if (!text(value)) return null;
  try {
    const url = new URL(value);
    return url.protocol === "https:" && !url.username && !url.password ? url.href : null;
  } catch { return null; }
}

/** Only explicitly saved public source fields reach source panels and exports. */
export function readPlatformReferences(value: unknown): PlatformReference[] {
  if (!Array.isArray(value) || !value.length || value.length > 8) return [];
  const result: PlatformReference[] = [];
  for (const raw of value) {
    const source = record(raw);
    if (!text(source.referenceId, 96) || !/^[a-z][a-z0-9_.-]+$/u.test(source.referenceId)
      || !text(source.version, 64) || !text(source.contentHash, 64) || !/^[a-f0-9]{64}$/u.test(source.contentHash)
      || !Array.isArray(source.sources) || !source.sources.length || source.sources.length > 8) return [];
    const publications: PlatformReference["sources"] = [];
    for (const rawPublication of source.sources) {
      const publication = record(rawPublication), url = publicReferenceUrl(publication.url);
      if (!text(publication.name, 256) || !url) return [];
      publications.push({ name: publication.name, url,
        ...(text(publication.version, 64) ? { version: publication.version } : {}),
        ...(text(publication.license, 128) ? { license: publication.license } : {}),
        ...(text(publication.use, 512) ? { use: publication.use } : {}) });
    }
    const properties: PlatformReference["properties"] = {};
    if (Object.keys(record(source.properties)).length > 8) return [];
    for (const [key, rawProperty] of Object.entries(record(source.properties))) {
      const property = record(rawProperty);
      if (!text(property.label, 128) || !text(property.definition, 2048)) return [];
      properties[key] = { label: property.label, definition: property.definition,
        ...(text(property.unit, 64) ? { unit: property.unit } : {}),
        ...(text(property.coverage, 512) ? { coverage: property.coverage } : {}),
        ...(text(property.citation, 1024) ? { citation: property.citation } : {}) };
    }
    result.push({ referenceId: source.referenceId, version: source.version, contentHash: source.contentHash,
      name: text(source.name, 256) ? source.name : source.referenceId, sources: publications, properties });
  }
  return new Set(result.map(source => source.referenceId)).size === result.length ? result : [];
}

const xml = (v: string) => v.replace(/[&<>"']/gu, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);
const markdown = (v: string) => v.replace(/[&<>|\\`*_\[\]]/gu, c => `&#${c.charCodeAt(0)};`).replace(/\r?\n/gu, " ");
export function referenceSourcesHtml(sources: PlatformReference[]): string {
  return sources.map(source => `<li><strong>${xml(source.name)}</strong> · ${xml(source.version)}<ul>${source.sources.map(publication =>
    `<li><a href="${xml(publication.url)}">${xml(publication.name)}</a>${publication.version ? ` · ${xml(publication.version)}` : ""}${publication.license ? ` · ${xml(publication.license)}` : ""}</li>`).join("")}</ul></li>`).join("");
}
export function referenceSourcesMarkdown(sources: PlatformReference[]): string[] {
  return sources.flatMap(source => [`- ${markdown(source.name)} · ${markdown(source.version)}`,
    ...source.sources.map(publication => `  - [${markdown(publication.name)}](<${publication.url.replace(/[<>]/gu, encodeURIComponent)}>)${publication.version ? ` · ${markdown(publication.version)}` : ""}${publication.license ? ` · ${markdown(publication.license)}` : ""}`)]);
}
