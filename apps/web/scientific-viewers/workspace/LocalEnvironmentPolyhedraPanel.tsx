"use client";

import { useMemo, useState } from "react";

import type { Artifact } from "../../app/lib/planner-api";
import type { ScientificWorkspace, WorkspaceSelectionContext } from "../../app/lib/workspace-api";
import { coordinationSiteSelection, localEnvironmentSelection } from "../../shared/workspace/workspace-selection-runtime";
import { LocalEnvironmentPolyhedronView } from "./LocalEnvironmentPolyhedronView";
import styles from "./LocalEnvironmentPolyhedra.module.css";

import { readSavedLocalEnvironment, algorithmLabel, classificationLabel, geometryLabel, faceReason, metricLabel, metricUnit,
  type SavedEnvironmentSite as SiteResult, type SavedLocalEnvironment as Payload } from "./saved-local-environment";

type N2SelectionKind = "LOCAL_ENVIRONMENT" | "COORDINATION_POLYHEDRON" | "POLYHEDRON_VERTEX" | "POLYHEDRON_FACE";

export function LocalEnvironmentPolyhedraPanel({ artifacts, selected, workspace, onSelection }: Readonly<{
  artifacts: readonly Artifact[];
  selected: Artifact;
  workspace: ScientificWorkspace;
  onSelection?: (selection: WorkspaceSelectionContext) => void;
}>) {
  const loaded = useMemo(() => artifacts.map(parsePayload).filter((item): item is { artifact: Artifact; payload: Payload } => item !== null), [artifacts]);
  const active = useMemo(() => parsePayload(selected), [selected]);
  if (!active) return <InvalidEnvironment />;
  const comparison = loaded.filter((item) => item.payload.scope.sourceResourceHash === active.payload.scope.sourceResourceHash);
  return <LocalEnvironmentContent key={active.artifact.artifactId ?? active.artifact.id} payload={active.payload} comparison={comparison}
    onSiteSelection={onSelection ? (site) => onSelection(coordinationSiteSelection(workspace, active.artifact, {
      sourceResourceId: active.payload.scope.sourceResourceId, structureHash: site.structureHash, siteId: site.siteId,
    })) : undefined}
    onExactSelection={onSelection ? (site, kind, exactId) => onSelection(localEnvironmentSelection(workspace, active.artifact, {
      kind, sourceResourceId: active.payload.scope.sourceResourceId, structureHash: site.structureHash, siteId: site.siteId,
      sourceArtifactId: active.payload.sourceCoordination.artifactId,
      sourceArtifactChecksum: active.payload.sourceCoordination.artifactChecksum,
      environmentId: kind === "LOCAL_ENVIRONMENT" || kind === "COORDINATION_POLYHEDRON" ? site.environmentIdentity : undefined,
      polyhedronId: kind !== "LOCAL_ENVIRONMENT" ? site.polyhedronIdentity : undefined,
      vertexId: kind === "POLYHEDRON_VERTEX" ? exactId : undefined,
      faceId: kind === "POLYHEDRON_FACE" ? exactId : undefined,
      geometryReferenceId: kind === "LOCAL_ENVIRONMENT" || kind === "COORDINATION_POLYHEDRON" ? site.classification.referenceGeometryId : undefined,
    })) : undefined} />;
}

export function LocalEnvironmentReportPreview({ payload }: Readonly<{ payload: unknown }>) {
  const saved = useMemo(() => readSavedLocalEnvironment(payload), [payload]);
  return saved ? <LocalEnvironmentContent payload={saved} /> : <InvalidEnvironment />;
}

function InvalidEnvironment() {
  return <section className={styles.panel} role="alert"><h5>配位多面体暂不可用</h5><p>结果内容未通过校验，请重新加载该结果。</p><details><summary>错误详情</summary><code>N2_LOCAL_ENVIRONMENT_CONTRACT_INVALID</code></details></section>;
}

function LocalEnvironmentContent({ payload, comparison = [], onSiteSelection, onExactSelection }: Readonly<{
  payload: Payload;
  comparison?: readonly { artifact: Artifact; payload: Payload }[];
  onSiteSelection?: (site: SiteResult) => void;
  onExactSelection?: (site: SiteResult, kind: N2SelectionKind, exactId?: string) => void;
}>) {
  const [activeSiteId, setActiveSiteId] = useState<string | null>(null);
  const sites = payload.siteResults;
  const siteIndex = Math.max(0, sites.findIndex((item) => item.siteId === activeSiteId));
  const site = sites[siteIndex] ?? null;
  const selectSite = (item: SiteResult) => {
    setActiveSiteId(item.siteId);
    onSiteSelection?.(item);
  };
  return <section className={styles.panel} aria-label="局域配位与多面体" data-testid="local-environment-polyhedra-panel">
    <header className={styles.heading}>
      <h5>配位多面体</h5>
      <span className={styles.secondary}>{algorithmLabel(payload.sourceCoordination.algorithmId)} · {payload.coverage.evaluatedSites}/{payload.coverage.requestedSites} 个位点</span>
    </header>
    {payload.coverage.status !== "COMPLETE" ? <p role="status" className={styles.notice}>{payload.coverage.status === "PARTIAL" ? "部分位点未能生成几何结果。" : "未能生成可用的位点几何。"} {payload.coverage.unavailableSites} 个位点不可用。</p> : null}
    {sites.length > 0 ? <details className={styles.disclosure}><summary>位点列表（{sites.length}）</summary>
      <SiteList sites={sites} selectedSiteId={site?.siteId} onSelect={selectSite} />
    </details> : null}
    {site ? <>
      <div className={styles.heading}>
        <div className={styles.siteHeading}>
          <h6>位点 {site.siteIndex} · {site.classification.status === "CLASSIFIED" ? geometryLabel(site.classification.referenceGeometryId) : classificationLabel(site.classification.status)}</h6>
          {site.classification.status !== "CLASSIFIED" && site.classification.referenceGeometryId ? <span className={styles.secondary}>最近参考：{geometryLabel(site.classification.referenceGeometryId)}</span> : null}
        </div>
        {sites.length > 1 ? <div className={styles.navigation} role="group" aria-label="切换配位位点">
          <button type="button" aria-label="上一个位点" disabled={siteIndex === 0} onClick={() => selectSite(sites[siteIndex - 1])}>←</button>
          <span className={styles.secondary}>{siteIndex + 1} / {sites.length}</span>
          <button type="button" aria-label="下一个位点" disabled={siteIndex === sites.length - 1} onClick={() => selectSite(sites[siteIndex + 1])}>→</button>
        </div> : null}
      </div>
      <EnvironmentInspector key={site.environmentIdentity}
        site={site}
        onExactSelection={onExactSelection ? (kind, exactId) => onExactSelection(site, kind, exactId) : undefined} />
    </> : <p role="status">没有已保存的位点几何，可展开来源查看执行状态。</p>}
    <p className={styles.notice}>几何近邻由 {algorithmLabel(payload.sourceCoordination.algorithmId)} 判定，不代表确定的化学键。</p>
    {comparison.length > 1 ? <details className={styles.disclosure}><summary>不同来源的配位结果（{comparison.length}）</summary>
      <div className={"workspace-table-scroll " + styles.scroll} role="region" aria-label="配位来源比较" tabIndex={0}>
        <table><thead><tr><th scope="col">近邻方法</th><th scope="col">已评估位点</th><th scope="col">已分类位点</th><th scope="col">来源</th></tr></thead>
          <tbody>{comparison.map((item) => <tr key={item.artifact.artifactId ?? item.artifact.id}>
            <th scope="row">{algorithmLabel(item.payload.sourceCoordination.algorithmId)}</th><td>{item.payload.coverage.evaluatedSites}</td><td>{item.payload.coverage.classifiedSites}</td><td>{item.payload.sourceCoordination.artifactId}</td>
          </tr>)}</tbody></table>
      </div>
    </details> : null}
    <details className={styles.disclosure}><summary>来源与参数</summary><div className={styles.detailsBody}>
      <dl className={styles.metadata}>
        <dt>近邻方法</dt><dd>{algorithmLabel(payload.sourceCoordination.algorithmId)} {payload.sourceCoordination.algorithmVersion}</dd>
        <dt>原始配位结果</dt><dd><code>{payload.sourceCoordination.artifactId}</code></dd>
        <dt>配位结果校验值</dt><dd><code>{payload.sourceCoordination.artifactChecksum}</code></dd>
        <dt>几何参考</dt><dd>{payload.referenceCatalog.catalogId} · {payload.referenceCatalog.catalogVersion}</dd>
        <dt>分类算法</dt><dd>{payload.algorithm.classification}</dd>
        <dt>表面构建</dt><dd>{payload.algorithm.faceConstruction}</dd>
        <dt>参数校验值</dt><dd><code>{payload.parameterHash}</code></dd>
      </dl>
      <pre>{JSON.stringify({ parameters: payload.resolvedParameters, scope: payload.scope, coverage: payload.coverage, sourceCoordination: payload.sourceCoordination, warnings: payload.warnings, selectedSite: site }, null, 2)}</pre>
    </div></details>
  </section>;
}

function SiteList({ sites, selectedSiteId, onSelect }: Readonly<{ sites: readonly SiteResult[]; selectedSiteId?: string; onSelect: (site: SiteResult) => void }>) {
  const [page, setPage] = useState(0);
  const pageCount = Math.ceil(sites.length / 50);
  const currentPage = Math.min(page, pageCount - 1);
  const rows = sites.slice(currentPage * 50, (currentPage + 1) * 50);
  return <div className={styles.detailsBody}>
    <div className={"workspace-table-scroll " + styles.scroll} role="region" aria-label="位点配位列表" tabIndex={0}>
      <table><thead><tr><th scope="col">位点</th><th scope="col">分类</th><th scope="col">参考几何</th><th scope="col">匹配分数</th></tr></thead>
        <tbody>{rows.map((site) => <tr key={site.siteId} data-selected={site.siteId === selectedSiteId}>
          <td><button type="button" aria-label={"选择位点 " + site.siteIndex} aria-pressed={site.siteId === selectedSiteId} onClick={() => onSelect(site)}>{site.siteIndex}</button></td>
          <td>{classificationLabel(site.classification.status)}</td><td>{geometryLabel(site.classification.referenceGeometryId)}</td><td>{displayNumber(site.classification.geometryScore)}</td>
        </tr>)}</tbody></table>
    </div>
    {pageCount > 1 ? <div className={styles.pagination}>
      <span>{currentPage * 50 + 1}–{currentPage * 50 + rows.length} / {sites.length}</span>
      <button type="button" disabled={currentPage === 0} onClick={() => setPage(currentPage - 1)}>上一页位点</button>
      <button type="button" disabled={currentPage === pageCount - 1} onClick={() => setPage(currentPage + 1)}>下一页位点</button>
    </div> : null}
  </div>;
}

function EnvironmentInspector({ site, onExactSelection }: Readonly<{ site: SiteResult; onExactSelection?: (kind: N2SelectionKind, exactId?: string) => void }>) {
  const [selected, setSelected] = useState<{ kind: N2SelectionKind; id?: string } | null>(null);
  const select = (kind: N2SelectionKind, id?: string) => { setSelected({ kind, id }); onExactSelection?.(kind, id); };
  const vertexNumbers = new Map(site.polyhedron.vertices.map((vertex, index) => [vertex.vertexIdentity, index + 1]));
  return <section className={styles.inspector} aria-label={"位点 " + site.siteIndex + " 配位详情"}>
    {site.polyhedron.vertices.length ? <LocalEnvironmentPolyhedronView vertices={site.polyhedron.vertices} faces={site.polyhedron.faces}
      selectedVertexId={selected?.kind === "POLYHEDRON_VERTEX" ? selected.id : undefined} selectedFaceId={selected?.kind === "POLYHEDRON_FACE" ? selected.id : undefined} /> : <p role="status">该位点没有已保存的近邻顶点。</p>}
    {site.polyhedron.status === "UNAVAILABLE" ? <p role="status" className={styles.notice}>{faceReason(site.polyhedron.unavailableReason)}</p> : null}
    {site.classification.status === "AMBIGUOUS" ? <p role="status" className={styles.notice}>存在多个相近的参考几何，分类尚不唯一。</p> : null}
    <dl className={styles.metrics}>
      <div><dt>配位权重和</dt><dd>{displayNumber(site.sourceCoordinationValue)}</dd></div>
      <div><dt>平均近邻距离</dt><dd>{displayNumber(site.distortionMetrics.radialDistanceMean)} Å</dd></div>
      <div><dt>几何匹配分数</dt><dd>{displayNumber(site.classification.geometryScore)}</dd></div>
    </dl>
    {onExactSelection ? <div className={styles.actions}>
      <button type="button" aria-pressed={selected?.kind === "LOCAL_ENVIRONMENT"} onClick={() => select("LOCAL_ENVIRONMENT")}>选中配位环境</button>
      <button type="button" aria-pressed={selected?.kind === "COORDINATION_POLYHEDRON"} onClick={() => select("COORDINATION_POLYHEDRON")}>选中多面体</button>
    </div> : null}
    <details className={styles.disclosure}><summary>顶点与周期近邻（{site.polyhedron.vertices.length}）</summary>
      <div className={"workspace-table-scroll " + styles.scroll} role="region" aria-label="多面体顶点数据" tabIndex={0}>
        <table><thead><tr><th scope="col">顶点</th><th scope="col">周期偏移</th><th scope="col">相对坐标（Å）</th><th scope="col">距离（Å）</th></tr></thead>
          <tbody>{site.polyhedron.vertices.map((vertex, index) => <tr key={vertex.vertexIdentity} data-selected={selected?.id === vertex.vertexIdentity}>
            <td><button type="button" title={vertex.neighborSiteId} aria-pressed={selected?.id === vertex.vertexIdentity} onClick={() => select("POLYHEDRON_VERTEX", vertex.vertexIdentity)}>顶点 {index + 1}</button></td>
            <td>[{vertex.periodicImage.join(", ")}]</td><td>[{vertex.relativeCartesian.map(displayNumber).join(", ")}]</td><td>{displayNumber(vertex.distance)}</td>
          </tr>)}</tbody></table>
      </div>
    </details>
    {site.polyhedron.faces.length ? <details className={styles.disclosure}><summary>多面体的面（{site.polyhedron.faces.length}）</summary>
      <div className={"workspace-table-scroll " + styles.scroll} role="region" aria-label="多面体面数据" tabIndex={0}>
        <table><thead><tr><th scope="col">面</th><th scope="col">组成顶点</th></tr></thead><tbody>{site.polyhedron.faces.map((face, index) =>
          <tr key={face.faceIdentity} data-selected={selected?.id === face.faceIdentity}><td><button type="button" aria-pressed={selected?.id === face.faceIdentity} onClick={() => select("POLYHEDRON_FACE", face.faceIdentity)}>面 {index + 1}</button></td>
            <td>{face.vertexIdentities.map((identity) => vertexNumbers.get(identity)).join(" · ")}</td></tr>)}</tbody></table>
      </div>
    </details> : null}
    <details className={styles.disclosure}><summary>几何指标</summary>
      <div className={"workspace-table-scroll " + styles.scroll} role="region" aria-label="配位几何指标" tabIndex={0}>
        <table><thead><tr><th scope="col">指标</th><th scope="col">值</th></tr></thead><tbody>
          {Object.entries(site.distortionMetrics).filter(([key]) => !key.endsWith("Unit")).map(([key, value]) => <tr key={key}><th scope="row">{metricLabel(key)}</th><td>{displayNumber(value)}{metricUnit(key)}</td></tr>)}
          <tr><th scope="row">配位权重定义</th><td>{site.sourceCoordinationSemantics === "crystalnn_weight_sum" ? "CrystalNN 权重和" : "VoronoiNN 归一化立体角权重和"}</td></tr>
        </tbody></table>
      </div>
      {site.classification.alternatives.length ? <pre>{JSON.stringify(site.classification.alternatives, null, 2)}</pre> : null}
    </details>
  </section>;
}

function parsePayload(artifact: Artifact): { artifact: Artifact; payload: Payload } | null {
  const payload = readSavedLocalEnvironment(artifact.content ?? artifact.payload);
  return payload ? { artifact, payload } : null;
}

function displayNumber(value: unknown) { return typeof value === "number" && Number.isFinite(value) ? String(value) : "—"; }
