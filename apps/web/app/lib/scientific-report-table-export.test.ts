// @vitest-environment node
import { createHash } from "node:crypto";
import { unzipSync } from "fflate/node";
import { describe, expect, it } from "vitest";
import { readReportTablePreview, renderReportTableHtml, renderReportTableMarkdown } from "./scientific-report-table-export";
import { buildScientificReportBundle } from "./scientific-report-bundle";
import type { ScientificReportView } from "./scientific-report-api";

const correlation = () => ({ chartType: "correlation_heatmap", method: "pearson", columns: ["A", "B", "constant"],
  matrix: [[1, 0, null], [0, 1, null], [null, null, null]], pairCount: 3, validPairCount: 1, missingPairCount: 2, minNonNullCount: 1 });

describe("saved report tables", () => {
  it("renders controlled conversion units as scientific symbols while preserving exact originals", () => {
    const payload = { schemaVersion: "mdi.project.parameter-table/1.0", artifactType: "reference.convert_units", sampleAnalysis: false,
      rows: [{ "原数值": 0.5, "原单位": "nm", "换算结果": 5, "目标单位": "angstrom", "备注": "angstrom" },
        { "原数值": 20, "原单位": "degC", "换算结果": 293.15, "目标单位": "K", "备注": null }] };
    const original = JSON.stringify(payload), preview = readReportTablePreview(payload)!;
    expect(preview.rows[0]).toEqual(["0.5", "nm", "5", "Å", "angstrom"]);
    expect(preview.rows[1]).toEqual(["20", "°C", "293.15", "K", "—"]);
    expect(renderReportTableHtml(preview, "单位换算")).toContain("<td>Å</td>");
    expect(renderReportTableMarkdown(preview)).toContain("| 0.5 | nm | 5 | Å | angstrom |");
    expect(JSON.stringify(payload)).toBe(original);
  });

  it.each([{}, { sampleAnalysis: true }, { schemaVersion: "unknown" }, { artifactType: "viz.inline_xy" }])("leaves unit-like user text unchanged outside the exact conversion contract: %j", override => {
    const contract = { schemaVersion: "mdi.project.parameter-table/1.0", artifactType: "reference.convert_units", sampleAnalysis: false };
    const payload = { ...(Object.keys(override).length ? { ...contract, ...override } : {}), rows: [{ "原单位": "angstrom", "目标单位": "degC" }] };
    expect(readReportTablePreview(payload)!.rows[0]).toEqual(["angstrom", "degC"]);
  });

  it("uses the recorded parameter column order instead of serialized object-key order", () => {
    const payload = { schemaVersion: "mdi.project.parameter-table/1.0", artifactType: "generation.function_curve", sampleAnalysis: false,
      columns: ["x", "sin(x)", "cos(x)"], rows: [{ "cos(x)": 1, "sin(x)": 0, x: 0, extra: "angstrom" }] };
    const before = JSON.stringify(payload), preview = readReportTablePreview(payload)!;
    expect(preview.columns).toEqual(["x", "sin(x)", "cos(x)", "extra"]);
    expect(preview.rows[0]).toEqual(["0", "0", "1", "angstrom"]);
    expect(JSON.stringify(payload)).toBe(before);
  });

  it("retains every matrix coordinate, zero and missing value", () => {
    const payload = correlation(), original = JSON.stringify(payload), preview = readReportTablePreview(payload)!;
    expect(preview.columns).toEqual(["变量 A", "变量 B", "相关系数"]);
    expect(preview.rows).toHaveLength(9);
    expect(preview.rows[1]).toEqual(["A", "B", "0"]);
    expect(preview.rows[2]).toEqual(["A", "constant", "—"]);
    expect(renderReportTableHtml(preview,"矩阵")).toContain('<td class="table-number">0</td>');
    expect(renderReportTableMarkdown(preview)).toContain('| A | B | 0 |');
    expect(JSON.stringify(payload)).toBe(original);
  });

  it.each([
    { ...correlation(), columns: ["A", "A", "constant"] },
    { ...correlation(), matrix: [[1, 0], [0, 1], [null, null]] },
    { ...correlation(), matrix: [[1, true, null], [true, 1, null], [null, null, null]] },
  ])("keeps malformed matrices as downloadable originals", payload => expect(readReportTablePreview(payload)).toBeNull());

  it("shows saved numeric and categorical statistics without deriving missing values", () => {
    const preview = readReportTablePreview({ rowCount: 4, columns: [{name:"energy/~eV",missingCount:1}],
      numericColumns: {"energy/~eV":{ count:3,mean:0.12345678901234568,std:null,min:0,median:0.1,max:0.4 }},
      categoricalColumns: {kind:{count:3,unique:2,valueCounts:{a:2,b:1}}} })!;
    expect(preview.rows[0][preview.columns.indexOf("平均值")]).toBe('0.12345678901234568');
    expect(preview.rows[0][preview.columns.indexOf("缺失")]).toBe('1');
    expect(preview.rows[1][preview.columns.indexOf("缺失")]).toBe('—');
    expect(preview.rows[1][preview.columns.indexOf("类别计数")]).toBe('"a"：2\n"b"：1');
  });

  it("presents saved top categories with their exact labels and counts", () => {
    const preview=readReportTablePreview({rowCount:3,numericColumns:{},categoricalColumns:{kind:{count:3,topValues:[
      {value:'a | b',count:2},{value:'<script>',count:1},
    ]}}})!;
    expect(preview.rows[0][preview.columns.indexOf("高频类别")]).toBe('"a | b"：2\n"<script>"：1');
    expect(renderReportTableHtml(preview,'分类')).not.toContain('<script>');
    expect(renderReportTableMarkdown(preview)).toContain('&#124;');
  });

  it("escapes markup and Markdown syntax without executing table cells", () => {
    const preview=readReportTablePreview({rows:[{value:'<script>alert(1)</script> [x](https://example.test) | a\nb `c`'}]})!;
    const html=renderReportTableHtml(preview,'<img src=x onerror=alert(1)>');
    expect(html).not.toContain('<script>'); expect(html).not.toContain('<img');
    expect(html).toContain('&lt;script&gt;');
    const md=renderReportTableMarkdown(preview);
    expect(md).not.toContain('<script>'); expect(md).not.toContain('[x]('); expect(md).not.toContain('`c`');
    expect(md).toContain('&#124; a<br>b');
  });

  it("discloses row, column and cell limits while retaining the original", () => {
    const payload={rows:Array.from({length:90},(_,row)=>Object.fromEntries(Array.from({length:15},(_,col)=>['c'+col,row===0&&col===0?'X'.repeat(1500):row+col])))};
    const preview=readReportTablePreview(payload)!;
    expect(preview.rows).toHaveLength(80); expect(preview.columns).toHaveLength(15);
    expect(preview.notes.join('')).toContain('80 / 90 行、15 / 15 列');
    expect(preview.notes.join('')).toContain('长值已缩略');
    expect(payload.rows[0].c0).toHaveLength(1500);
  });

  it("keeps every wide-table field in bounded column groups with stable row identities", () => {
    const payload={rows:Array.from({length:2},(_,r)=>Object.fromEntries(Array.from({length:15},(_,c)=>['column'+c,c===0?'repeated':`row${r}-field${c}`])))};
    const preview=readReportTablePreview(payload)!;
    const html=renderReportTableHtml(preview,'宽表'), md=renderReportTableMarkdown(preview);
    const tables=[...html.matchAll(/<table>[\s\S]*?<\/table>/g)].map(match=>match[0]);
    expect(tables.length).toBeGreaterThan(1);
    for(const table of tables) {
      const head=table.match(/<thead>([\s\S]*?)<\/thead>/)![1];
      expect((head.match(/<th /g)||[]).length).toBeLessThanOrEqual(6);
      expect(head).toContain('行号'); expect(head).toContain('column0');
      expect(table).toContain('>1</th>'); expect(table).toContain('>2</th>');
    }
    for(let r=0;r<2;r++)for(let c=1;c<15;c++) {
      expect(html.match(new RegExp(`>row${r}-field${c}<`,'g'))).toHaveLength(1);
      expect(md).toContain(`row${r}-field${c} |`);
    }
    expect(preview.notes).toEqual([]);
  });

  it("discloses exceptionally wide input limits without dropping columns from normal summaries", () => {
    const preview=readReportTablePreview({rows:[Object.fromEntries(Array.from({length:70},(_,c)=>['c'+c,c]))]})!;
    expect(preview.columns).toHaveLength(64);
    expect(preview.notes.join('')).toContain('64 / 70 列');
  });

  it("packages exact job-bound values into HTML and Markdown alongside byte-identical originals", async () => {
    const view={report_id:'r',snapshot_id:'s',project_id:'p',created_at:'2026-10-07',source_fingerprint:'source',
      report:{contract_version:'2.0',title:'数据表',summary:'概览',research_question:'比较结果',primary_figures:[],method_summary:'保存的数值',
        main_findings:[],limitations:[],data_sources:[],evidence_refs:[],reproducibility_summary:'来源版本',supporting_results:[],omitted_supporting_items:[]},
      table_sources:[{table_ref:'a',title:'相关系数',job_id:'job-a',artifact_ids:['same-id']},
        {table_ref:'b',title:'另一份数据',job_id:'job-b',artifact_ids:['same-id']}]} as unknown as ScientificReportView;
    const data=new Map([['job-a',JSON.stringify(correlation())],['job-b',JSON.stringify({rows:[{x:42.125,y:0}]})]]);
    const archive=await buildScientificReportBundle(view,async(job,id)=>{
      expect(id).toBe('same-id'); const bytes=new TextEncoder().encode(data.get(job)!);
      return new Response(bytes,{headers:{'content-type':'application/json','x-content-length-validated':String(bytes.length),'x-content-sha256':createHash('sha256').update(bytes).digest('hex')}});
    },new AbortController().signal);
    const files=unzipSync(archive), decode=(key:string)=>new TextDecoder().decode(files[key]);
    expect(decode('report.html')).toContain('<td class="table-number">0</td>'); expect(decode('report.html')).toContain('42.125');
    expect(decode('report.md')).toContain('| A | B | 0 |'); expect(decode('report.md')).toContain('| 42.125 | 0 |');
    expect(decode('artifacts/artifact-001.json')).toBe(data.get('job-a'));
    expect(decode('artifacts/artifact-002.json')).toBe(data.get('job-b'));
    const manifest=JSON.parse(decode('bundle-manifest.json'));
    for(const entry of manifest.files)expect(createHash('sha256').update(files[entry.path]).digest('hex')).toBe(entry.sha256);
  });
});
