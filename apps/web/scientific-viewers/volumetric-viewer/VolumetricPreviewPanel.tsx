"use client";

import { useEffect, useId, useRef, useState } from "react";
import type { Artifact } from "../../app/lib/planner-api";
import { VolumetricIsosurfaceSurface } from "./VolumetricIsosurfaceSurface";
import { VolumetricSliceVolumeSurface } from "./VolumetricSliceVolumeSurface";
import styles from "./VolumetricSurface.module.css";

type JsonRecord = Record<string, unknown>;
const MODES = [
  {id: "surface", label: "等值面"}, {id: "slice", label: "晶格切片"},
  {id: "volume", label: "体渲染"}, {id: "metadata", label: "元数据"}, {id: "manifest", label: "数据清单"},
] as const;
type Mode = typeof MODES[number]["id"];

type Props = { artifacts: Artifact[]; selectedFieldId?: string | null; onSelectField?: (fieldId: string) => void };

export function VolumetricPreviewPanel({ artifacts, selectedFieldId, onSelectField }: Props) {
  const identity = artifacts.filter((artifact) => artifact.type === "volumetric_dataset_json" || artifact.type === "volumetric_manifest_json")
    .map((artifact) => [artifact.id ?? artifact.artifactId, artifact.sha256, record(payload(artifact))?.content_hash]);
  return <VolumetricPreviewContent key={JSON.stringify(identity)} artifacts={artifacts} selectedFieldId={selectedFieldId} onSelectField={onSelectField} />;
}

function VolumetricPreviewContent({ artifacts, selectedFieldId = null, onSelectField }: Props) {
  const datasetArtifact = artifacts.find((artifact) => artifact.type === "volumetric_dataset_json");
  const manifestArtifact = artifacts.find((artifact) => artifact.type === "volumetric_manifest_json");
  const [tab, setTab] = useState<Mode>("surface");
  const [focusedMode, setFocusedMode] = useState<Mode>("surface");
  const tabPrefix = useId();
  const tabButtons = useRef<Partial<Record<Mode, HTMLButtonElement | null>>>({});
  const [fieldId, setFieldId] = useState<string | null>(selectedFieldId);
  useEffect(() => { if (selectedFieldId) setFieldId(selectedFieldId); }, [selectedFieldId]);
  if (!datasetArtifact && !manifestArtifact) return null;
  const dataset = record(payload(datasetArtifact));
  const manifest = record(payload(manifestArtifact));
  const grid = record(dataset?.grid);
  const provenance = record(dataset?.provenance);
  const capabilities = record(manifest?.capabilities);
  const security = record(manifest?.security) ?? record(dataset?.security);
  const fields = Array.isArray(dataset?.fields) ? dataset.fields : [];
  const payloads = Array.isArray(dataset?.payloads) ? dataset.payloads : [];
  return <section className={`panel viewer-static-preview ${styles.preview}`} data-testid="volumetric-metadata-preview">
    <div className="panel-heading"><span>{Array.isArray(grid?.shape) ? `${grid.shape.join(" × ")} 网格` : "网格未提供"}</span>
      {onSelectField && fieldId ? <button type="button" className="secondary" aria-pressed={selectedFieldId === fieldId} onClick={() => onSelectField(fieldId)}>{selectedFieldId === fieldId ? "已选择此字段" : "选择此字段用于研究"}</button> : null}
    </div>
    <div className="viewer-preview-tabs" role="tablist" aria-label="体数据查看模式">
      {MODES.map((mode, index) => <button key={mode.id} type="button" role="tab"
        id={`${tabPrefix}-${mode.id}`} aria-controls={`${tabPrefix}-panel`} aria-selected={tab === mode.id}
        tabIndex={focusedMode === mode.id ? 0 : -1} ref={node => { tabButtons.current[mode.id] = node; }}
        className={tab === mode.id ? "active" : "secondary"} onFocus={() => setFocusedMode(mode.id)}
        onClick={() => { setFocusedMode(mode.id); setTab(mode.id); }} onKeyDown={event => {
          const next = event.key === "ArrowRight" ? (index + 1) % MODES.length
            : event.key === "ArrowLeft" ? (index + MODES.length - 1) % MODES.length
              : event.key === "Home" ? 0 : event.key === "End" ? MODES.length - 1 : null;
          if (next === null) return;
          event.preventDefault();
          tabButtons.current[MODES[next].id]?.focus();
        }}>{mode.label}</button>)}
    </div>
    <div className="viewer-preview-tab-panel" role="tabpanel" id={`${tabPrefix}-panel`} aria-labelledby={`${tabPrefix}-${tab}`} tabIndex={0}>
      {tab === "surface" ? <VolumetricIsosurfaceSurface artifacts={artifacts} initialFieldId={fieldId} onFieldChange={setFieldId} /> : null}
      {tab === "slice" || tab === "volume" ? <VolumetricSliceVolumeSurface artifacts={artifacts} mode={tab} initialFieldId={fieldId} onFieldChange={setFieldId} /> : null}
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
