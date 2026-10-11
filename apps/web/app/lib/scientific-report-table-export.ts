import { displayValue, formatColumnLabel, isNumericTableColumn, regressionMetricRows, tableRows } from "./scientific-report-table-data";

export type ReportTablePreview = {
  columns: string[];
  numericColumns: boolean[];
  rows: string[][];
  totalRows: number;
  totalColumns: number;
  notes: string[];
};
export type ReportTableExport = { jobId: string; artifactId: string; preview: ReportTablePreview | null };

/** Bounded presentation of saved values. Originals remain byte-for-byte in the archive. */
export function readReportTablePreview(payload: unknown): ReportTablePreview | null {
  const metrics = regressionMetricRows(payload);
  const rows: Record<string, unknown>[] = metrics ? metrics.map(([label, value]) => ({ "项目": label, "值": value })) : tableRows(payload);
  if (!rows.length) return null;
  const keys = [...new Set(rows.flatMap(row => Object.keys(row)))];
  if (!keys.length) return null;
  const columns = keys.slice(0, 64), notes: string[] = [];
  let shortened = false, missing = false;
  const preview = rows.slice(0, 80).map(row => columns.map(key => {
    if (row[key] === null || row[key] === undefined) missing = true;
    const value = displayValue(row[key]);
    if (value.length <= 1024) return value;
    shortened = true;
    return value.slice(0, 1024) + "…";
  }));
  if (preview.length < rows.length || columns.length < keys.length) notes.push(`预览 ${preview.length} / ${rows.length} 行、${columns.length} / ${keys.length} 列；完整数据见原始数据表。`);
  if (shortened) notes.push("部分长值已缩略；完整内容见原始数据表。");
  if (missing) notes.push("— 表示该项没有保存的数值。");
  const numericColumns = columns.map(key => isNumericTableColumn(rows, key));
  return { columns: columns.map(key => formatColumnLabel(key, payload)), numericColumns, rows: preview, totalRows: rows.length, totalColumns: keys.length, notes };
}

const html = (text: string) => text.replace(/[&<>"']/g, value => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[value]!);
const markdown = (text: string) => text.replace(/[&<>|\\`*_\[\]]/g, value => `&#${value.charCodeAt(0)};`).replace(/\r\n?|\n/g, "<br>");

type ColumnGroup = Pick<ReportTablePreview, "columns" | "numericColumns" | "rows">;

function columnGroups(preview: ReportTablePreview): ColumnGroup[] {
  if (preview.columns.length <= 6) return [preview];
  // Repeat the identifying column. A displayed row number disambiguates repeated
  // or missing identities without claiming an additional scientific source key.
  const numbered = new Set(preview.rows.map(row => row[0])).size < preview.rows.length;
  const width = numbered ? 4 : 5;
  const groups: ColumnGroup[] = [];
  for (let start = 1; start < preview.columns.length; start += width) {
    const indices = [0, ...Array.from({ length: Math.min(width, preview.columns.length - start) }, (_, i) => start + i)];
    groups.push({
      columns: [...(numbered ? ["行号"] : []), ...indices.map(i => preview.columns[i])],
      numericColumns: [...(numbered ? [true] : []), ...indices.map(i => preview.numericColumns[i])],
      rows: preview.rows.map((row, index) => [...(numbered ? [String(index + 1)] : []), ...indices.map(i => row[i])]),
    });
  }
  return groups;
}

export function renderReportTableHtml(preview: ReportTablePreview | null, title: string): string {
  if (!preview) return "<p>此数据结构暂不支持表格预览，请查看原始数据表。</p>";
  const groups = columnGroups(preview);
  return groups.map((group, index) => {
    const label = title + (groups.length > 1 ? ` · 列组 ${index + 1} / ${groups.length}` : "");
    return `<div class="report-table-scroll" role="region" tabindex="0" aria-label="${html(label)}"><table><caption>${html(label)}</caption><thead><tr>${group.columns.map((column, i) => `<th scope="col"${group.numericColumns[i] ? ' class="table-number"' : ""}>${html(column)}</th>`).join("")}</tr></thead><tbody>${group.rows.map(row => `<tr>${row.map((value, i) => {
    const tag = i === 0 ? "th" : "td";
    return `<${tag}${i === 0 ? ' scope="row"' : ""}${group.numericColumns[i] ? ' class="table-number"' : ""}>${html(value)}</${tag}>`;
    }).join("")}</tr>`).join("")}</tbody></table></div>`;
  }).join("") + preview.notes.map(note => `<p class="report-table-note">${html(note)}</p>`).join("");
}

export function renderReportTableMarkdown(preview: ReportTablePreview | null): string {
  if (!preview) return "此数据结构暂不支持表格预览，请查看原始数据表。";
  return [...columnGroups(preview).flatMap(group => ["", `| ${group.columns.map(markdown).join(" | ")} |`,
    `| ${group.columns.map(() => "---").join(" | ")} |`, ...group.rows.map(row => `| ${row.map(markdown).join(" | ")} |`), ""]),
    ...preview.notes, ""].join("\n");
}
