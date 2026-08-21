"use client";

import { useState } from "react";
import type { Artifact } from "../../lib/planner-api";
import { VolumetricIsosurfaceSurface } from "./VolumetricIsosurfaceSurface";
import { VolumetricSliceVolumeSurface } from "./VolumetricSliceVolumeSurface";

type JsonRecord = Record<string, unknown>;

export function VolumetricPreviewPanel({ artifacts }: { artifacts: Artifact[] }) {
  const datasetArtifact = artifacts.find((artifact) => artifact.type === "volumetric_dataset_json");
  const manifestArtifact = artifacts.find((artifact) => artifact.type === "volumetric_manifest_json");
  const [tab, setTab] = useState<"surface" | "slice" | "volume" | "metadata" | "manifest">("surface");
  if (!datasetArtifact && !manifestArtifact) return null;
  const dataset = record(payload(datasetArtifact));
  const manifest = record(payload(manifestArtifact));
  const grid = record(dataset?.grid);
  const provenance = record(dataset?.provenance);
  const capabilities = record(manifest?.capabilities);
  const security = record(manifest?.security) ?? record(dataset?.security);
  const fields = Array.isArray(dataset?.fields) ? dataset.fields : [];
  const payloads = Array.isArray(dataset?.payloads) ? dataset.payloads : [];
  return <section className="panel viewer-static-preview" data-testid="volumetric-metadata-preview">
    <div className="panel-heading"><div><h3>体数据场</h3><span>已验证的等值面、晶格切片与直接体渲染</span></div></div>
    <p className="notice">规范化场数据可通过有界等值面、定量晶格轴切片或 WebGL2 体渲染查看；元数据和清单仍可独立读取。</p>
    <dl className="mini-grid volumetric-metadata-summary" data-testid="volumetric-metadata-summary">
      <dt>结构版本</dt><dd data-testid="volumetric-schema-version">{text(dataset?.schema_version)}</dd>
      <dt>源格式</dt><dd data-testid="volumetric-source-format">{text(provenance?.source_format)}</dd>
      <dt>网格形状</dt><dd data-testid="volumetric-grid-shape">{Array.isArray(grid?.shape) ? grid.shape.join(" x ") : "未提供"}</dd>
      <dt>场变量</dt><dd>{fields.map((field) => { const item = record(field); return item?.quantity ?? item?.field_name; }).filter(Boolean).join(", ") || "未提供"}</dd>
      <dt>包含渲染器</dt><dd data-testid="volumetric-renderer-included">{flag(capabilities?.renderer_included ?? security?.renderer_included)}</dd>
    </dl>
    <div className="viewer-preview-tabs" role="tablist" aria-label="体数据查看模式">
      <button type="button" role="tab" aria-selected={tab === "surface"} className={tab === "surface" ? "active" : "secondary"} onClick={() => setTab("surface")}>等值面</button>
      <button type="button" role="tab" aria-selected={tab === "slice"} className={tab === "slice" ? "active" : "secondary"} onClick={() => setTab("slice")}>晶格切片</button>
      <button type="button" role="tab" aria-selected={tab === "volume"} className={tab === "volume" ? "active" : "secondary"} onClick={() => setTab("volume")}>体渲染</button>
      <button type="button" role="tab" aria-selected={tab === "metadata"} className={tab === "metadata" ? "active" : "secondary"} onClick={() => setTab("metadata")}>元数据</button>
      <button type="button" role="tab" aria-selected={tab === "manifest"} className={tab === "manifest" ? "active" : "secondary"} onClick={() => setTab("manifest")}>数据清单</button>
    </div>
    <div className="viewer-preview-tab-panel" role="tabpanel">
      {tab === "surface" ? <VolumetricIsosurfaceSurface artifacts={artifacts} /> : null}
      {tab === "slice" || tab === "volume" ? <VolumetricSliceVolumeSurface artifacts={artifacts} mode={tab} /> : null}
      {tab === "metadata" ? <div data-testid="volumetric-metadata-json-preview"><dl className="mini-grid">
        <dt>结构版本</dt><dd>{text(dataset?.schema_version)}</dd>
        <dt>源格式</dt><dd>{text(provenance?.source_format)}</dd>
        <dt>网格形状</dt><dd>{Array.isArray(grid?.shape) ? grid.shape.join(" x ") : "未提供"}</dd>
        <dt>采样位置</dt><dd>{text(grid?.sample_location)}</dd>
        <dt>边界条件</dt><dd>{Array.isArray(grid?.boundary_conditions) ? grid.boundary_conditions.join(", ") : "未提供"}</dd>
        <dt>场变量</dt><dd>{fields.length}</dd><dt>数据载荷</dt><dd>{payloads.length}</dd>
        <dt>包含渲染器</dt><dd>{flag(capabilities?.renderer_included ?? security?.renderer_included)}</dd>
        <dt>允许外部 URL</dt><dd>{flag(security?.external_urls_allowed)}</dd>
      </dl><pre className="json-preview">{JSON.stringify(dataset, null, 2)}</pre></div> : null}
      {tab === "manifest" ? <pre className="json-preview" data-testid="volumetric-manifest-preview">{JSON.stringify(manifest, null, 2)}</pre> : null}
    </div>
  </section>;
}

function payload(artifact?: Artifact): unknown { return artifact ? artifact.content ?? artifact.payload ?? artifact.metadata?.preview ?? null : null; }
function record(value: unknown): JsonRecord | null { return typeof value === "object" && value !== null && !Array.isArray(value) ? value as JsonRecord : null; }
function text(value: unknown): string { return typeof value === "string" || typeof value === "number" ? String(value) : "unknown"; }
function flag(value: unknown): string { return value === true ? "true" : value === false ? "false" : "unknown"; }
