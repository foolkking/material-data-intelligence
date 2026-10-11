import { useEffect, useState } from "react";

import type { RenderAtom, RenderBond, ValidatedRenderScene } from "./viewerSceneRendererTypes";
import { savedSiteNeighbors, samePeriodicSite as sameRef } from "./viewerSiteNeighbors";

const MAX_ACCESSIBLE_NEIGHBOR_ROWS = 100;

export function ViewerSiteInspector({ atom, atoms, bonds, sourceAtoms, sourceBonds, source, repeat, sourcePreview = false, neighborMethod, onClear, onJumpPrimary, onShowNeighbors, onClearNeighbors, onHighlightNeighbor }: {
  readonly atom: RenderAtom | null;
  readonly atoms: readonly RenderAtom[];
  readonly bonds: readonly RenderBond[];
  readonly sourceAtoms: readonly RenderAtom[];
  readonly sourceBonds: readonly RenderBond[];
  readonly source: string;
  readonly repeat: readonly [number, number, number];
  readonly sourcePreview?: boolean;
  readonly neighborMethod?: NonNullable<ValidatedRenderScene["connectivity"]>["method"];
  readonly onClear: () => void;
  readonly onJumpPrimary: () => void;
  readonly onShowNeighbors: () => void;
  readonly onClearNeighbors: () => void;
  readonly onHighlightNeighbor: (target: RenderAtom["ref"], bondId: string) => void;
}) {
  const [highlightedBondId, setHighlightedBondId] = useState<string | null>(null);
  const neighborConnections = Boolean(neighborMethod);
  const idealNeighbors = neighborMethod === "ideal_first_shell";
  useEffect(() => setHighlightedBondId(null), [atom?.id]);
  if (!atom) return <aside className="sr-only" aria-label="已选位点检查器" data-testid="viewer-site-inspector"><p>点击原子，查看元素和坐标。也可聚焦视图后按 N 依次选择。</p></aside>;
  const connected = savedSiteNeighbors(sourceBonds, atom.ref);
  const visibleConnected = connected.slice(0, MAX_ACCESSIBLE_NEIGHBOR_ROWS);
  const primary = atom.ref.imageOffset.every((value) => value === 0);
  const copyCoordinates = () => copyText(atom.position.join(", "));
  const copySite = () => copyText(JSON.stringify({ index: atom.siteIndex, image_offset: atom.ref.imageOffset, label: atom.label, element: atom.element, occupancy: atom.occupancy, canonical_xyz: atom.canonicalPosition, displayed_xyz: atom.position, frac: atom.fractionalPosition }, null, 2));
  return (
    <aside className="viewer-site-inspector" aria-label="已选位点检查器" data-testid="viewer-site-inspector">
      <div className="viewer-inspector-heading"><strong>{atom.label || atom.species} <span className="viewer-inspector-kind">{primary ? "原子详情" : "周期副本"}</span></strong><button type="button" className="compact secondary" onClick={onClear}>清除选择</button></div>
      <dl className="viewer-site-essentials">
        <div><dt>位点编号</dt><dd data-testid="viewer-selected-site-index">{atom.siteIndex}</dd></div>
        <div><dt>元素</dt><dd>{atom.element}</dd></div>
        <div><dt>周期偏移</dt><dd data-testid="viewer-selected-site-image-offset">[{atom.ref.imageOffset.join(", ")}]</dd></div>
        <div className="viewer-site-coordinate"><dt>坐标（Å）</dt><dd>{atom.position.map(value => value.toFixed(4)).join(", ")}</dd></div>
      </dl>
      <details className="viewer-site-details"><summary>完整坐标与相邻关系</summary>
      <dl className="mini-grid">
        <div><dt>身份</dt><dd>{primary ? "主位点" : "周期副本"}</dd></div>
        <div><dt>标签</dt><dd>{atom.label}</dd></div>
        <div><dt>物种 / 元素</dt><dd data-testid="viewer-selected-site-species">{atom.species} / {atom.element}</dd></div>
        <div><dt>占位率</dt><dd>{atom.occupancy}</dd></div>
        <div><dt>分数坐标</dt><dd data-testid="viewer-selected-site-fractional">{atom.fractionalPosition?.join(", ") ?? "未提供"}</dd></div>
        <div><dt>规范笛卡尔坐标（Å）</dt><dd>{atom.canonicalPosition.join(", ")}</dd></div>
        <div><dt>显示笛卡尔坐标（Å）</dt><dd data-testid="viewer-selected-site-cartesian">{atom.position.join(", ")}</dd></div>
        <div><dt>超晶胞</dt><dd>{repeat.join(" × ")}</dd></div>
        <div><dt>显示半径</dt><dd>{atom.radius}</dd></div>
        <div><dt>来源</dt><dd>{source || "规范结构场景"}</dd></div>
        <div><dt>{neighborConnections ? "近邻连接" : "相邻键合"}</dt><dd data-testid="viewer-selected-site-neighbors">{connected.length ? connected.map((item)=>`${item.target.siteIndex}@[${item.target.imageOffset.join(",")}]`).join("；") : "无"}（{connected.length}）</dd></div>
      </dl>
      <div className="viewer-neighbor-table-scroll" role="region" aria-label={sourcePreview ? "当前预览的近邻关系" : "已保存的相邻关系"} tabIndex={0}>
        <table data-testid="viewer-periodic-neighbor-table">
          <caption>{atom.siteIndex}@[{atom.ref.imageOffset.join(",")}] {sourcePreview ? "当前近邻连接" : "已保存的周期相邻关系"}。列出 {visibleConnected.length} / {connected.length}。</caption>
          <thead><tr><th scope="col">目标</th><th scope="col">物种</th><th scope="col">周期位置</th><th scope="col">距离（Å）</th><th scope="col">来源</th><th scope="col">{neighborConnections ? "类型" : "权威"}</th><th scope="col">边界</th><th scope="col">显示范围</th></tr></thead>
          <tbody>{visibleConnected.map(({bond,target})=>{
            const crossBoundary=target.imageOffset.some((value,index)=>value!==atom.ref.imageOffset[index]);
            const targetAtom=atoms.find((candidate)=>sameRef(candidate.ref,target)) ?? sourceAtoms.find((candidate)=>candidate.siteIndex===target.siteIndex);
            const displayedBond=bonds.find((candidate)=>(sameRef(candidate.fromRef,atom.ref)&&sameRef(candidate.toRef,target))||(sameRef(candidate.toRef,atom.ref)&&sameRef(candidate.fromRef,target)));
            const key=`${bond.id}:${target.siteIndex}@${target.imageOffset.join(",")}`;
            return <tr key={key} data-testid="viewer-periodic-neighbor-row"><td>{displayedBond ? <button type="button" className="compact secondary" aria-pressed={highlightedBondId===key} aria-label={`高亮指向位点 ${target.siteIndex}、周期位置 ${target.imageOffset.join(", ")} 的${neighborConnections ? "连接" : "键"}`} onClick={()=>{setHighlightedBondId(key);onHighlightNeighbor(target,displayedBond.id);}}>{target.siteIndex}</button> : target.siteIndex}</td><td>{targetAtom?.species ?? "未知"}</td><td data-testid="viewer-periodic-neighbor-offset">[{target.imageOffset.join(", ")}]</td><td data-testid="viewer-periodic-neighbor-distance">{bond.distanceAngstrom.toFixed(6)}</td><td data-testid="viewer-periodic-neighbor-source">{idealNeighbors ? "最短周期距离" : neighborConnections ? "参考共价半径" : bond.source}</td><td data-testid="viewer-periodic-neighbor-authoritative">{idealNeighbors ? "理想模型近邻" : neighborConnections ? "近邻候选" : bond.authoritative ? "是" : "否"}</td><td>{bond.fromSiteIndex===bond.toSiteIndex ? "自周期" : crossBoundary ? "跨边界" : "同晶胞"}</td><td>{displayedBond ? "范围内" : "范围外"}</td></tr>;
          })}</tbody>
        </table>
      </div>
      {connected.length > visibleConnected.length ? <p className="notice" role="status">相邻表最多显示 {MAX_ACCESSIBLE_NEIGHBOR_ROWS} 行。</p> : null}
      {!sourcePreview ? <p className="viewer-inspector-note">{idealNeighbors ? "仅列出理想模型中已保存的最短周期近邻，不代表样品的化学键或键级。" : "仅列出已保存的场景连接，不代表完整配位关系。"}</p> : null}
      <div className="button-row"><button type="button" className="compact secondary" onClick={copyCoordinates}>复制坐标</button><button type="button" className="compact secondary" onClick={copySite}>复制位点 JSON</button>{!primary ? <button type="button" className="compact secondary" onClick={onJumpPrimary}>跳转到主位点</button> : null}<button type="button" className="compact secondary" onClick={onShowNeighbors}>{neighborConnections ? "显示完整近邻" : "显示此原子的周期副本"}</button><button type="button" className="compact secondary" onClick={onClearNeighbors}>隐藏额外周期副本</button></div>
      </details>
    </aside>
  );
}

function copyText(value: string) {
  const operation = navigator.clipboard?.writeText(value);
  if (operation) void operation.catch(() => undefined);
}
