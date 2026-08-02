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
    <div className="panel-heading"><div><h3>Volumetric data</h3><span>Validated isosurface, lattice slice, and direct volume products</span></div></div>
    <p className="notice">Canonical inert field data can be inspected as bounded isosurfaces, quantitative lattice-axis slices, or a WebGL2 direct volume. Metadata and manifest JSON remain independently available.</p>
    <dl className="mini-grid volumetric-metadata-summary" data-testid="volumetric-metadata-summary">
      <dt>schema</dt><dd data-testid="volumetric-schema-version">{text(dataset?.schema_version)}</dd>
      <dt>source format</dt><dd data-testid="volumetric-source-format">{text(provenance?.source_format)}</dd>
      <dt>shape</dt><dd data-testid="volumetric-grid-shape">{Array.isArray(grid?.shape) ? grid.shape.join(" x ") : "unknown"}</dd>
      <dt>fields</dt><dd>{fields.map((field) => { const item = record(field); return item?.quantity ?? item?.field_name; }).filter(Boolean).join(", ") || "none"}</dd>
      <dt>renderer included</dt><dd data-testid="volumetric-renderer-included">{flag(capabilities?.renderer_included ?? security?.renderer_included)}</dd>
    </dl>
    <div className="viewer-preview-tabs" role="tablist" aria-label="Volumetric preview modes">
      <button type="button" role="tab" aria-selected={tab === "surface"} className={tab === "surface" ? "active" : "secondary"} onClick={() => setTab("surface")}>Isosurface</button>
      <button type="button" role="tab" aria-selected={tab === "slice"} className={tab === "slice" ? "active" : "secondary"} onClick={() => setTab("slice")}>Slice</button>
      <button type="button" role="tab" aria-selected={tab === "volume"} className={tab === "volume" ? "active" : "secondary"} onClick={() => setTab("volume")}>Volume</button>
      <button type="button" role="tab" aria-selected={tab === "metadata"} className={tab === "metadata" ? "active" : "secondary"} onClick={() => setTab("metadata")}>Metadata JSON</button>
      <button type="button" role="tab" aria-selected={tab === "manifest"} className={tab === "manifest" ? "active" : "secondary"} onClick={() => setTab("manifest")}>Manifest</button>
    </div>
    <div className="viewer-preview-tab-panel" role="tabpanel">
      {tab === "surface" ? <VolumetricIsosurfaceSurface artifacts={artifacts} /> : null}
      {tab === "slice" || tab === "volume" ? <VolumetricSliceVolumeSurface artifacts={artifacts} mode={tab} /> : null}
      {tab === "metadata" ? <div data-testid="volumetric-metadata-json-preview"><dl className="mini-grid">
        <dt>schema</dt><dd>{text(dataset?.schema_version)}</dd>
        <dt>source format</dt><dd>{text(provenance?.source_format)}</dd>
        <dt>shape</dt><dd>{Array.isArray(grid?.shape) ? grid.shape.join(" x ") : "unknown"}</dd>
        <dt>sample location</dt><dd>{text(grid?.sample_location)}</dd>
        <dt>boundary</dt><dd>{Array.isArray(grid?.boundary_conditions) ? grid.boundary_conditions.join(", ") : "unknown"}</dd>
        <dt>fields</dt><dd>{fields.length}</dd><dt>payloads</dt><dd>{payloads.length}</dd>
        <dt>renderer included</dt><dd>{flag(capabilities?.renderer_included ?? security?.renderer_included)}</dd>
        <dt>external URLs allowed</dt><dd>{flag(security?.external_urls_allowed)}</dd>
      </dl><pre className="json-preview">{JSON.stringify(dataset, null, 2)}</pre></div> : null}
      {tab === "manifest" ? <pre className="json-preview" data-testid="volumetric-manifest-preview">{JSON.stringify(manifest, null, 2)}</pre> : null}
    </div>
  </section>;
}

function payload(artifact?: Artifact): unknown { return artifact ? artifact.content ?? artifact.payload ?? artifact.metadata?.preview ?? null : null; }
function record(value: unknown): JsonRecord | null { return typeof value === "object" && value !== null && !Array.isArray(value) ? value as JsonRecord : null; }
function text(value: unknown): string { return typeof value === "string" || typeof value === "number" ? String(value) : "unknown"; }
function flag(value: unknown): string { return value === true ? "true" : value === false ? "false" : "unknown"; }
