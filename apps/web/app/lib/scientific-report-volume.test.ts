// @vitest-environment node
import { createHash, webcrypto } from "node:crypto";
import { inflateSync } from "node:zlib";
import { unzipSync } from "fflate/node";
import { describe, expect, it, vi } from "vitest";
import fixture from "../../../../tests/fixtures/volumetric_contract/cubic_constant_scalar.json";
import { renderReportVolume } from "./scientific-report-volume";
import { buildScientificReportBundle } from "./scientific-report-bundle";
import type { ReportViewerArtifact, ScientificReportView } from "./scientific-report-api";

const sha = (bytes: Uint8Array) => createHash("sha256").update(bytes).digest("hex");
function savedVolume(uniform = false, labels?: { field: string; unit: string }, shape = [4, 4, 4]) {
  const dataset = structuredClone(fixture.raw_dataset), manifest = structuredClone(fixture.manifest);
  dataset.grid.shape = shape;
  dataset.grid.domain_extent_matrix = dataset.grid.step_matrix.map((row, axis) => row.map(value => value * shape[axis]));
  dataset.grid.structure_binding.lattice_matrix = dataset.grid.domain_extent_matrix;
  dataset.payloads[0].grid_shape = shape;
  dataset.payloads[0].logical_shape = [...shape, 1];
  dataset.payloads[0].value_count = shape.reduce((a, b) => a * b, 1);
  dataset.payloads[0].compressed_bytes = dataset.payloads[0].uncompressed_bytes = dataset.payloads[0].value_count * 8;
  if (labels) {
    dataset.fields[0].field_name = labels.field;
    dataset.fields[0].unit.canonical_unit = labels.unit;
    dataset.fields[0].unit.source_unit = labels.unit;
  }
  const values = Array.from({ length: dataset.payloads[0].value_count }, (_, i) => uniform ? 2 : Math.floor(i / (shape[1] * shape[2])) * 100 + Math.floor(i / shape[2]) % shape[1] * 10 + i % shape[2]);
  const binary = new Uint8Array(new Float64Array(values).buffer), hash = sha(binary);
  dataset.payloads[0].logical_sha256 = dataset.payloads[0].storage_sha256 = hash;
  dataset.payloads[0].payload_id = dataset.fields[0].payload_id = `payload:${hash}`;
  dataset.fields[0].payload_logical_sha256 = hash;
  dataset.fields[0].statistics.stored_components[0].minimum = Math.min(...values);
  dataset.fields[0].statistics.stored_components[0].maximum = Math.max(...values);
  const files = new Map<string, Uint8Array>();
  files.set("volumetric_dataset.json", new TextEncoder().encode(JSON.stringify(dataset)));
  files.set(dataset.payloads[0].artifact_name, binary);
  files.set("volumetric_grid.json", new TextEncoder().encode(JSON.stringify(dataset.grid)));
  manifest.artifacts = [...files].map(([name, bytes]) => ({ name, bytes: bytes.length, sha256: sha(bytes),
    kind: name.endsWith(".f64") ? "numeric_payload" : name.includes("dataset") ? "dataset" : "grid",
    media_type: name.endsWith(".f64") ? "application/octet-stream" : "application/json",
    schema_version: "phase10j.volumetric_payload.v1" })).sort((a,b)=>a.name.localeCompare(b.name));
  files.set("volumetric_manifest.json", new TextEncoder().encode(JSON.stringify(manifest)));
  const artifacts: ReportViewerArtifact[] = [...files].map(([name, bytes]) => ({
    id: name, name, jobId: "job-volume", toolCallId: "call-volume", sizeBytes: bytes.length, sha256: sha(bytes),
    contentType: name.endsWith(".f64") ? "application/octet-stream" : "application/json",
    type: name.includes("dataset") ? "volumetric_dataset_json" : name.includes("manifest") ? "volumetric_manifest_json" : name.endsWith(".f64") ? "volumetric_binary" : "volumetric_grid_json",
  }));
  return { artifacts, files, read: async (artifact: ReportViewerArtifact) => files.get(artifact.name)! };
}

vi.stubGlobal("crypto", webcrypto);
describe("volumetric report views and complete source bundle", () => {
  it("fits rectangular planes without stretching their saved grid proportions", async () => {
    const source = savedVolume(false, undefined, [2, 3, 8]);
    const { views } = await renderReportVolume(source.artifacts, source.read, new AbortController().signal);
    for (const view of views) {
      const plane = JSON.parse(view.data);
      for (const svg of [view.svg, view.compactSvg]) {
        const image = svg.match(/<image[^>]*width="([\d.]+)" height="([\d.]+)"/u)!;
        const width = Number(image[1]), height = Number(image[2]);
        expect(width / height).toBeCloseTo(plane.shape[1] / plane.shape[0], 10);
        expect(Math.max(width, height)).toBeLessThanOrEqual(svg === view.svg ? 480 : 232);
      }
      for (let row = 0; row < plane.shape[0]; row++) for (let col = 0; col < plane.shape[1]; col++) {
        const point = [0, 0, 0]; point[plane.axis] = plane.grid_index;
        point[plane.vertical_axis] = row; point[plane.horizontal_axis] = col;
        expect(plane.values[row * plane.shape[1] + col]).toBe(point[0] * 100 + point[1] * 10 + point[2]);
      }
    }
  });
  it("retains every exact sample in each canonical mid-plane and makes valid PNG images", async () => {
    const source = savedVolume();
    const rendered = await renderReportVolume(source.artifacts, source.read, new AbortController().signal);
    expect(rendered.unsupportedFields).toEqual([]);
    expect(rendered.views).toHaveLength(3);
    const planes = rendered.views.map(v => JSON.parse(v.data));
    expect(planes.map(p => [p.axis, p.grid_index, p.fractional_position, p.sampling])).toEqual([
      [0,2,0.5,"exact_grid_plane"], [1,2,0.5,"exact_grid_plane"], [2,2,0.5,"exact_grid_plane"],
    ]);
    expect(planes[0].values).toEqual([200,201,202,203,210,211,212,213,220,221,222,223,230,231,232,233]);
    expect(planes[1].values).toEqual([20,21,22,23,120,121,122,123,220,221,222,223,320,321,322,323]);
    expect(planes[2].values).toEqual([2,12,22,32,102,112,122,132,202,212,222,232,302,312,322,332]);
    for (const view of rendered.views) {
      expect(view.sampleCount).toBe(16);
      const png = Buffer.from(view.svg.match(/base64,([A-Za-z0-9+/=]+)/)![1], "base64");
      expect([...png.subarray(0,8)]).toEqual([137,80,78,71,13,10,26,10]);
      expect(png.readUInt32BE(16)).toBe(4); expect(png.readUInt32BE(20)).toBe(4);
      const idat = png.indexOf(Buffer.from("IDAT")), length = png.readUInt32BE(idat - 4);
      expect(inflateSync(png.subarray(idat + 4, idat + 4 + length))).toHaveLength(4 * (1 + 4 * 3));
    }
  });

  it("does not fabricate contrast for constant fields", async () => {
    const source = savedVolume(true);
    const { views } = await renderReportVolume(source.artifacts, source.read, new AbortController().signal);
    expect(views[0].svg).toContain("全部样本值：2");
    expect(JSON.parse(views[0].data).values).toEqual(Array(16).fill(2));
  });

  it("keeps long units complete and escapes source labels in compact images", async () => {
    const labels = { field: "一个很长的科学字段名称用来验证报告在窄屏上的呈现 <density>", unit: "electron/(angstrom^3*source_normalization_reference)" };
    const source = savedVolume(true, labels);
    const { views } = await renderReportVolume(source.artifacts, source.read, new AbortController().signal);
    expect(views[0].compactSvg).toContain("&lt;density&gt;");
    expect(views[0].compactSvg).not.toContain("<density>");
    expect([...views[0].compactSvg.matchAll(/<tspan[^>]*>(.*?)<\/tspan>/gu)].map(match => match[1]).join("")).toBe(labels.unit);
    expect(JSON.parse(views[0].data)).toMatchObject({ unit: labels.unit, field_name: labels.field, values: Array(16).fill(2) });
  });

  it("rejects missing, ambiguous, foreign and damaged numeric dependencies", async () => {
    const source = savedVolume(), run = (artifacts: ReportViewerArtifact[]) => renderReportVolume(artifacts, source.read, new AbortController().signal);
    await expect(run(source.artifacts.filter(a=>a.type !== "volumetric_binary"))).rejects.toThrow();
    await expect(run([...source.artifacts, source.artifacts[0]])).rejects.toThrow();
    await expect(run(source.artifacts.map(a=>a.type === "volumetric_binary" ? {...a, toolCallId:"foreign"} : a))).rejects.toThrow();
    source.files.get(source.artifacts.find(a=>a.type === "volumetric_binary")!.name)![0] ^= 1;
    await expect(run(source.artifacts)).rejects.toThrow();
  });

  it("packages original names and bytes, derived views and linked exact-value JSON", async () => {
    const source = savedVolume();
    const view = { report_id:"volume-report", snapshot_id:"snapshot", viewer_sources:[], title:"体数据", created_at:"2026-10-05T02:00:00Z",
      figure_sources:[{figure_ref:"volume",job_id:"job-volume",artifact_ids:["volumetric_dataset.json"],renderer:"volumetric",artifacts:source.artifacts}],
      report:{title:"体数据",summary:"合成测试",research_question:"检查体数据",primary_figures:[{figure_ref:"volume",caption:"体数据场",fact_refs:[],evidence_refs:[]}],
        method_summary:"读取保存结果",main_findings:[],limitations:[],data_sources:[],evidence_refs:[],reproducibility_summary:"保存值",supporting_results:[],omitted_supporting_items:[]},
    } as unknown as ScientificReportView;
    const zip = await buildScientificReportBundle(view, async(job,id)=>{
      expect(job).toBe("job-volume"); const a=source.artifacts.find(a=>a.id===id)!;
      return new Response(source.files.get(a.name)!.slice().buffer as ArrayBuffer,{headers:{"content-type":a.contentType,"x-content-sha256":a.sha256,"x-content-length-validated":String(a.sizeBytes)}});
    }, new AbortController().signal);
    const files = unzipSync(zip);
    for (const [name, data] of source.files) expect(sha(files[`artifacts/volume-1/${name}`])).toBe(sha(data));
    expect(JSON.parse(new TextDecoder().decode(files["figures/figure-1-3.json"])).values[15]).toBe(332);
    for (const name of ["report.html","report.md"]) expect(new TextDecoder().decode(files[name])).toContain("figures/figure-1-3.json");
  });
});
