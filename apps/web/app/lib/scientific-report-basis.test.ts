import { createHash } from "node:crypto";
import { unzipSync } from "fflate";
import { describe, expect, it } from "vitest";
import { buildScientificReportMarkdown, type ScientificReportView } from "./scientific-report-api";
import { renderReportBasisHtml, renderReportBasisMarkdown, renderReportInputsHtml, renderReportInputsMarkdown, reportParameterInputs, reportBasisGroupLabel, reportBasisSourceDisplayLabel, resolveReportBasis } from "./scientific-report-basis";
import { buildScientificReportBundle } from "./scientific-report-bundle";
import referenceFigure from "../../scientific-viewers/workspace/element-reference-comparison.fixture.json";
import { readSavedElementReference } from "../../scientific-viewers/workspace/saved-element-reference";

function view(): ScientificReportView {
  const sources = ["old-version", "new-version"].map(version => ({ object_id: "same-object", version_id: version, object_type: "structure.crystal", display_name: "same.cif" }));
  return {
    report_id: "report", snapshot_id: "report-snapshot", project_id: "project", research_turn_id: "new-turn",
    scientific_result_snapshot_id: "original-result-snapshot", scientific_interpretation_id: "interpretation",
    title: "材料比较", relevance_at_generation: "CURRENT", current_effective_relevance: "CURRENT",
    grounding_status: "VALID", scientific_context: "比较数密度", finding_count: 1, figure_count: 0,
    source_fingerprint: "source", created_at: "2026-10-09",
    report: { contract_version: "2.0", title: "材料比较", summary: "使用保存的结果。", research_question: "比较数密度",
      main_findings: [{ statement: "独立保存的来源版本。", fact_refs: ["fact-old", "fact-new"], evidence_refs: ["evidence-old"], finding_refs: ["finding"] }],
      primary_figures: [], supporting_results: [], method_summary: "RDF", limitations: [], data_sources: [], evidence_refs: ["evidence-old"],
      reproducibility_summary: "结果快照", omitted_supporting_items: [] },
    scientific_basis: { project_id: "project", result_snapshot_id: "original-result-snapshot",
      facts: sources.map((source, index) => ({ fact_id: index ? "fact-new" : "fact-old", predicate: "rdf.number_density", subject_ref: "saved-scope",
        value_text: index ? "0.085023" : "3.1000000000000005", unit: "angstrom^-3", source_refs: [source],
        artifact_id: "same-artifact", artifact_name: "rdf.json", job_id: index ? "new-job" : "old-job" })),
      evidence: [{ evidence_id: "evidence-old", evidence_type: "COMMITTED_MACHINE_READABLE_ARTIFACT", source_refs: [sources[0]],
        artifact_id: "same-artifact", artifact_name: "rdf.json", job_id: "old-job" }],
    },
  };
}

function parameterView(): ScientificReportView {
  const report = view();
  const inputs = [
    { tool_call_id: "formula-call", tool_id: "composition.from_formula", input_origin: "USER_PARAMETERS", content_hash: "a".repeat(64), resolved_parameters: { formula: "Ca(OH)2" } },
    { tool_call_id: "csv-call", tool_id: "viz.inline_xy", input_origin: "USER_TEXT_DATA", content_hash: "b".repeat(64), resolved_parameters: { data_text: "x,signal\n0,0\n1,2\n2,1\n3,4", style: "line" } },
  ];
  report.scientific_basis = { project_id: report.project_id, result_snapshot_id: report.scientific_result_snapshot_id,
    input_origin: "MIXED", parameter_inputs: inputs, evidence: [], facts: inputs.map((input, index) => ({
      fact_id: `fact-${index}`, predicate: "input.rows", subject_ref: input.tool_call_id, value_text: "4", source_refs: [],
      tool_call_id: input.tool_call_id, tool_id: input.tool_id, input_origin: input.input_origin as "USER_PARAMETERS" | "USER_TEXT_DATA",
      input_hash: input.content_hash, artifact_id: `${input.tool_call_id}-table`, job_id: "job",
    })),
  };
  report.report!.main_findings = [{ statement: "使用明确输入。", fact_refs: ["fact-0", "fact-1"], evidence_refs: [], finding_refs: [] }];
  report.report!.evidence_refs = [];
  return report;
}

describe("report parameter inputs", () => {
  it("carries exact formula and CSV inputs with their hashes into Markdown and ZIP", async () => {
    const report = parameterView(), inputs = reportParameterInputs(report);
    report.report!.primary_figures = [{ figure_ref: "formula", caption: "化学式组成", fact_refs: ["fact-0"], evidence_refs: [] }];
    report.figure_sources = [{ figure_ref: "formula", artifact_ids: ["formula-plot"], job_id: "job" }];
    const before = JSON.stringify(report);
    const archive = await buildScientificReportBundle(report, async (_job, id) => {
      const raw = new TextEncoder().encode(JSON.stringify(id === "formula-plot" ? {
        schemaVersion: "mdi.project.parameter-figure/1.0", artifactType: "composition.from_formula", sampleAnalysis: false,
        inputHash: inputs[0].content_hash, inputOrigin: "USER_PARAMETERS",
        plotlyFigure: { data: [{ type: "bar", x: ["Ca", "O", "H"], y: [20, 40, 40] }], layout: { xaxis: { type: "category" }, yaxis: { title: "原子百分比（%）", range: [0, 100] } } },
      } : {}));
      return new Response(raw, { headers: {
        "content-type": "application/json", "x-content-length-validated": String(raw.length), "x-content-sha256": createHash("sha256").update(raw).digest("hex"),
      } });
    }, new AbortController().signal);
    const files = unzipSync(archive), text = (path: string) => new TextDecoder().decode(files[path]);
    for (const content of [buildScientificReportMarkdown(report), text("report.md"), text("report.html")]) {
      expect(content).toContain("输入参数与原始数据");
      expect(content).toContain("Ca(OH)2");
      expect(content).toContain("x,signal\n0,0\n1,2\n2,1\n3,4");
      expect(content).toContain("化学式组成 · 输入参数");
      expect(content).toContain("输入数据绘图 · 输入表格");
      expect(content).toContain(inputs[0].content_hash);
      expect(content).toContain(inputs[1].content_hash);
    }
    expect(JSON.parse(text("reproducibility.json")).parameter_inputs).toEqual(inputs);
    expect(JSON.parse(text("scientific-basis.json")).parameter_inputs).toEqual(inputs);
    expect(JSON.parse(text("bundle-manifest.json")).figures[0].images).toEqual(["figures/figure-1-1.svg"]);
    expect(text("figures/figure-1-1.svg")).toContain('data-element="Ca" data-value="20"');
    expect(JSON.stringify(report)).toBe(before);
  });

  it.each(["hash", "call", "tool", "origin", "sample", "duplicate", "uncited", "project", "snapshot"])("excludes inputs with an unbound %s", fault => {
    const report = parameterView(), basis = report.scientific_basis!;
    const inputs = basis.parameter_inputs as Array<Record<string, unknown>>;
    if (fault === "hash") basis.facts[0].input_hash = "f".repeat(64);
    if (fault === "call") basis.facts[0].tool_call_id = "unrelated";
    if (fault === "tool") basis.facts[0].tool_id = "generation.ideal_crystal";
    if (fault === "origin") basis.facts[0].input_origin = "IDEAL_MODEL";
    if (fault === "sample") basis.facts[0].source_refs = [{ object_id: "foreign", version_id: "unknown", object_type: "structure.crystal" }];
    if (fault === "duplicate") inputs.push({ ...inputs[0] });
    if (fault === "uncited") basis.facts.shift();
    if (fault === "project") basis.project_id = "foreign";
    if (fault === "snapshot") basis.result_snapshot_id = "unrelated";
    expect(reportParameterInputs(report).some(input => input.tool_call_id === "formula-call")).toBe(false);
    expect(renderReportInputsMarkdown(report)).not.toContain("Ca(OH)2");
    expect(renderReportInputsHtml(report)).not.toContain("Ca(OH)2");
  });

  it("preserves raw table text safely and shares scientific unit and function labels", () => {
    const report = parameterView(), inputs = reportParameterInputs(report);
    inputs[1].resolved_parameters.data_text = "x</pre><script>,y```\n0,0\n1,2";
    const html = renderReportInputsHtml(report), markdown = renderReportInputsMarkdown(report);
    expect(html).toContain("x&lt;/pre&gt;&lt;script&gt;");
    expect(html).not.toContain("<script>");
    expect(markdown).toContain("````text\nx</pre><script>,y```\n0,0\n1,2\n````");
    Object.assign(inputs[0], { tool_id: "reference.convert_units", resolved_parameters: { from_unit: "nm", to_unit: "angstrom", values: [0.5, 2, 5] } });
    report.scientific_basis!.facts[0].tool_id = "reference.convert_units";
    expect(renderReportInputsMarkdown(report)).toContain("目标单位：Å");
    expect(renderReportInputsHtml(report)).toContain("0.5、2、5");
    Object.assign(inputs[0], { tool_id: "generation.function_curve", resolved_parameters: { functions: [{ kind: "sine", amplitude: 1 }, { kind: "cosine", amplitude: 2 }] } });
    report.scientific_basis!.facts[0].tool_id = "generation.function_curve";
    for (const output of [renderReportInputsMarkdown(report), renderReportInputsHtml(report)]) {
      expect(output).toContain("正弦");
      expect(output).toContain("余弦");
      expect(output).not.toContain("[object Object]");
    }
  });
});

describe("report scientific basis", () => {
  it("separates parameter calls and preserves their source labels in both export formats", () => {
    const report = view();
    report.scientific_basis!.facts = ["first", "second"].map((id, index) => ({
      fact_id: id, predicate: "calculation.output_value", subject_ref: "value-0", value_text: index ? "100" : "10", unit: "angstrom", source_refs: [],
      artifact_id: `${id}-table`, job_id: "job", tool_id: "reference.convert_units", tool_call_id: `${id}-call`,
      input_origin: "USER_PARAMETERS", input_hash: (index ? "b" : "a").repeat(64),
    }));
    const refs = { fact_refs: ["first", "second"] };
    const basis = resolveReportBasis(report, refs);
    expect(basis.groups).toHaveLength(2);
    expect(basis.groups.map(group => group.facts.map(fact => fact.value))).toEqual([["10 Å"], ["100 Å"]]);
    expect(basis.groups.map(group => reportBasisGroupLabel(group, basis.sources))).toEqual(["单位换算 · 输入参数", "单位换算 · 输入参数"]);
    for (const output of [renderReportBasisMarkdown(report, refs), renderReportBasisHtml(report, refs)]) {
      expect(output).toContain("单位换算 · 输入参数");
      expect(output).not.toContain("来源未能核对");
      expect(output).not.toContain("same.cif");
    }
  });

  it.each(["hash", "call", "tool", "sample", "origin"])("does not label an unbound %s as a parameter source", fault => {
    const report = view(), fact = report.scientific_basis!.facts[0];
    Object.assign(fact, { source_refs: [], tool_call_id: "call", tool_id: "generation.ideal_crystal", input_origin: "IDEAL_MODEL", input_hash: "a".repeat(64) });
    if (fault === "hash") fact.input_hash = "bad";
    if (fault === "call") fact.tool_call_id = null;
    if (fault === "tool") fact.tool_id = "unknown";
    if (fault === "sample") fact.source_refs = [{ object_id: "unknown", version_id: "", object_type: "structure.crystal" }];
    if (fault === "origin") Object.assign(fact, { input_origin: "MIXED" });
    const basis = resolveReportBasis(report, { fact_refs: [fact.fact_id] });
    expect(basis.groups[0].inputTitle).toBeUndefined();
    expect(reportBasisGroupLabel(basis.groups[0], basis.sources)).toBe("来源未能核对");
  });

  it("keeps reference facts and ZIP figures sourced without inventing sample versions", async () => {
    const report = view(), source = readSavedElementReference(referenceFigure)!.references;
    report.report!.main_findings = [{ statement: "Si 的参考共价半径为 1.11 Å。", fact_refs: ["radius"], evidence_refs: [], finding_refs: [] }];
    report.report!.evidence_refs = [];
    report.report!.primary_figures = [{ figure_ref: "figure", caption: "元素参考性质比较", fact_refs: ["radius"], evidence_refs: [] }];
    report.figure_sources = [{ figure_ref: "figure", artifact_ids: ["reference"], job_id: "reference-job" }];
    const location = { source_refs: [], reference_source_ids: ["elements"], artifact_id: "reference", job_id: "reference-job", tool_call_id: "reference-call" };
    report.scientific_basis = { project_id: report.project_id, result_snapshot_id: report.scientific_result_snapshot_id,
      reference_sources: source, evidence: [], facts: [
        { ...location, fact_id: "symbol", predicate: "reference.element.symbol", subject_ref: "Si", value_text: "Si" },
        { ...location, fact_id: "radius", predicate: "reference.element.covalent_radius", subject_ref: "Si", value_text: "1.11", unit: "angstrom" },
      ] };
    const basis = resolveReportBasis(report, report.report!.main_findings[0]);
    expect(basis.facts[0].title).toBe("Si · 参考共价半径");
    expect(basis.groups[0].sources).toEqual([]);
    expect(basis.groups[0].referenceSources).toEqual(source);
    const raw = new TextEncoder().encode(JSON.stringify(referenceFigure));
    const archive = await buildScientificReportBundle(report, async () => new Response(raw, { headers: {
      "content-type": "application/json", "x-content-length-validated": String(raw.length), "x-content-sha256": createHash("sha256").update(raw).digest("hex"),
    } }), new AbortController().signal);
    const files = unzipSync(archive), text = (path: string) => new TextDecoder().decode(files[path]);
    for (const file of ["report.md", "report.html"]) {
      expect(text(file)).toContain("https://ase-lib.org/ase/data.html");
      expect(text(file)).toContain("LGPL-2.1-or-later");
      expect(text(file)).toContain("1.11 Å");
      expect(text(file)).not.toContain("来源未能核对");
    }
    expect(Object.keys(files).filter(path => path.endsWith(".svg")).length).toBeGreaterThan(0);
    expect(JSON.parse(text("reproducibility.json")).reference_sources[0].contentHash).toBe(source[0].contentHash);
    const entries = JSON.parse(text("bundle-manifest.json")).files;
    for (const entry of entries) expect(createHash("sha256").update(files[entry.path]).digest("hex")).toBe(entry.sha256);
    report.scientific_basis!.facts[1].reference_source_ids = ["unbound"];
    expect(resolveReportBasis(report, report.report!.main_findings[0]).facts[0].referenceSources).toEqual([]);
  });
  it("keeps exact values and same-name source versions separate when array order changes", () => {
    const report = view(), saved = structuredClone(report);
    report.scientific_basis!.facts.reverse();
    const basis = resolveReportBasis(report, report.report!.main_findings[0]);
    expect(basis.facts.map(fact => fact.value)).toEqual(["3.1000000000000005 Å⁻³", "0.085023 Å⁻³"]);
    expect(basis.groups.map(group => group.sources[0].version_id)).toEqual(["old-version", "new-version"]);
    expect(basis.comparisonTitle).toBe("数密度");
    expect(basis.files.map(file => file.job_id)).toEqual(["old-job", "new-job"]);
    expect(report.report).toEqual(saved.report);
  });

  it("does not combine incompatible units into one comparison column", () => {
    const report = view();
    report.scientific_basis!.facts[1].unit = "count";
    expect(resolveReportBasis(report, report.report!.main_findings[0]).comparisonTitle).toBeNull();
  });

  it("disambiguates same-named sources whose version IDs share a prefix", () => {
    const sources = view().scientific_basis!.facts.map((fact, index) => ({ ...fact.source_refs[0], version_id: `12345678-${index}` }));
    expect(sources.map(source => reportBasisSourceDisplayLabel(source, sources))).toEqual(["same.cif · 12345678-0", "same.cif · 12345678-1"]);
  });

  it.each(["project", "snapshot", "missing"])("does not expose values or file links with a %s binding mismatch", (caseName) => {
    const report = view();
    if (caseName === "project") report.scientific_basis!.project_id = "foreign";
    if (caseName === "snapshot") report.scientific_basis!.result_snapshot_id = "latest-result";
    if (caseName === "missing") delete report.scientific_basis;
    const basis = resolveReportBasis(report, report.report!.main_findings[0]);
    expect(basis.facts).toEqual([]); expect(basis.files).toEqual([]);
    expect(basis.missingFacts).toEqual(["fact-old", "fact-new"]);
    expect(basis.missingEvidence).toEqual(["evidence-old"]);
  });

  it("rejects duplicate fact and evidence IDs without picking either value", () => {
    const report = view(), raw = report.scientific_basis!;
    raw.facts.push({ ...raw.facts[0], value_text: "999" });
    raw.evidence.push({ ...raw.evidence[0], job_id: "different" });
    const basis = resolveReportBasis(report, report.report!.main_findings[0]);
    expect(basis.facts.map(fact => fact.fact_id)).toEqual(["fact-new"]);
    expect(basis.evidence).toEqual([]);
    expect(basis.missingFacts).toEqual(["fact-old"]);
  });

  it("does not use the only report input when a fact has no source or conflicting source metadata", () => {
    const report = view(), fact = report.scientific_basis!.facts[0];
    report.viewer_sources = [{ ...fact.source_refs[0], source_ref: "source", display_name: "live label", is_current_version: true, object_type: "different-type" }];
    expect(resolveReportBasis(report, { fact_refs: [fact.fact_id] }).facts[0].sources).toEqual([]);
    fact.source_refs = [];
    expect(resolveReportBasis(report, { fact_refs: [fact.fact_id] }).facts[0].sources).toEqual([]);
  });

  it.each(["0", "false", "null", "", "9007199254740993"])("preserves the saved value %s without coercion or number rounding", value => {
    const report = view(), fact = report.scientific_basis!.facts[0];
    fact.value_text = value; fact.unit = null;
    expect(resolveReportBasis(report, { fact_refs: [fact.fact_id] }).facts[0].value).toBe(value);
  });

  it("labels a cited column metric using the name from its exact saved subject", () => {
    const report = view(), fact = report.scientific_basis!.facts[0];
    fact.predicate = "table.numeric.mean";
    report.scientific_basis!.facts.push({ ...fact, fact_id: "name", predicate: "table.numeric.column", value_text: "density" });
    report.scientific_basis!.facts.push({ ...fact, fact_id: "wrong-name", predicate: "table.numeric.column", subject_ref: "different", value_text: "temperature" });
    const result = resolveReportBasis(report, { fact_refs: [fact.fact_id] });
    expect(result.facts[0].title).toBe("density · 均值");
    expect(result.facts).toHaveLength(1);
  });

  it("uses the same fact values in Markdown and HTML and joins artifact paths by job and ID", () => {
    const report = view(), refs = report.report!.main_findings[0];
    const files = [{ jobId: "old-job", artifactId: "same-artifact", path: "artifacts/old.json" }, { jobId: "new-job", artifactId: "same-artifact", path: "artifacts/new.json" }];
    const md = renderReportBasisMarkdown(report, refs, files), html = renderReportBasisHtml(report, refs, files);
    for (const output of [md, html]) for (const expected of ["3.1000000000000005 Å⁻³", "0.085023 Å⁻³", "old-version", "new-version", "artifacts/old.json", "artifacts/new.json"]) expect(output).toContain(expected);
    const exported = buildScientificReportMarkdown(report, { figures: [], artifacts: files });
    expect(exported).toContain("   | same.cif · new-vers | 0.085023 Å⁻³ |");
    expect(exported).toContain("Fact refs: fact-old, fact-new");
    const missing = renderReportBasisHtml(report, { fact_refs: ["missing"] });
    expect(missing).toContain("1 项引用事实暂不可读取。");
    expect(missing).not.toContain("0.085023");
  });

  it("treats saved text as inert text in both export formats", () => {
    const report = view(), fact = report.scientific_basis!.facts[0];
    fact.value_text = '<img src="https://example.invalid/tracker">';
    fact.source_refs[0].display_name = "[source](https://example.invalid)";
    const refs = { fact_refs: [fact.fact_id] };
    expect(renderReportBasisHtml(report, refs)).not.toContain("<img");
    expect(renderReportBasisMarkdown(report, refs)).not.toContain("[source](https://example.invalid)");
  });

  it("packages cited files even when they are not gallery figures, with exact facts and checksums", async () => {
    const report = view(), before = JSON.stringify(report), requests: string[] = [];
    const archive = await buildScientificReportBundle(report, async (job, artifact) => {
      requests.push(`${job}/${artifact}`);
      const data = new TextEncoder().encode(JSON.stringify({ source: job, value: job === "old-job" ? 3.1000000000000005 : 0.085023 }));
      return new Response(data, { headers: { "content-type": "application/json", "x-content-length-validated": String(data.length), "x-content-sha256": createHash("sha256").update(data).digest("hex") } });
    }, new AbortController().signal);
    const files = unzipSync(archive), text = (path: string) => new TextDecoder().decode(files[path]);
    expect(requests).toEqual(["old-job/same-artifact", "new-job/same-artifact"]);
    expect(JSON.parse(text("scientific-basis.json"))).toEqual(report.scientific_basis);
    for (const path of ["report.md", "report.html"]) {
      expect(text(path)).toContain("3.1000000000000005 Å⁻³");
      expect(text(path)).toContain("artifacts/artifact-001.json");
      expect(text(path)).toContain("artifacts/artifact-002.json");
    }
    for (const entry of JSON.parse(text("bundle-manifest.json")).files) expect(createHash("sha256").update(files[entry.path]).digest("hex")).toBe(entry.sha256);
    expect(JSON.stringify(report)).toBe(before);
  });
});
