import { useEffect, useState } from "react";

import type { RenderAtom, RenderBond } from "./viewerSceneRendererTypes";

const MAX_ACCESSIBLE_NEIGHBOR_ROWS = 100;

export function ViewerSiteInspector({ atom, atoms, bonds, source, repeat, onClear, onJumpPrimary, onShowNeighbors, onClearNeighbors, onHighlightNeighbor }: {
  readonly atom: RenderAtom | null;
  readonly atoms: readonly RenderAtom[];
  readonly bonds: readonly RenderBond[];
  readonly source: string;
  readonly repeat: readonly [number, number, number];
  readonly onClear: () => void;
  readonly onJumpPrimary: () => void;
  readonly onShowNeighbors: () => void;
  readonly onClearNeighbors: () => void;
  readonly onHighlightNeighbor: (target: RenderAtom["ref"], bondId: string) => void;
}) {
  const [highlightedBondId, setHighlightedBondId] = useState<string | null>(null);
  useEffect(() => setHighlightedBondId(null), [atom?.id]);
  if (!atom) return <aside className="viewer-site-inspector" aria-label="已选位点检查器" data-testid="viewer-site-inspector"><p>尚未选择位点。请选择原子以查看规范身份和周期身份。</p></aside>;
  const connected = bonds.flatMap((bond) => sameRef(bond.fromRef,atom.ref) ? [{bond,target:bond.toRef}] : sameRef(bond.toRef,atom.ref) ? [{bond,target:bond.fromRef}] : []).sort((a,b)=>a.target.siteIndex-b.target.siteIndex||compareOffset(a.target.imageOffset,b.target.imageOffset));
  const visibleConnected = connected.slice(0, MAX_ACCESSIBLE_NEIGHBOR_ROWS);
  const primary = atom.ref.imageOffset.every((value) => value === 0);
  const copyCoordinates = () => copyText(atom.position.join(", "));
  const copySite = () => copyText(JSON.stringify({ index: atom.siteIndex, image_offset: atom.ref.imageOffset, label: atom.label, element: atom.element, occupancy: atom.occupancy, canonical_xyz: atom.canonicalPosition, displayed_xyz: atom.position, frac: atom.fractionalPosition }, null, 2));
  return (
    <aside className="viewer-site-inspector" aria-label="已选位点检查器" data-testid="viewer-site-inspector">
      <div className="viewer-inspector-heading"><strong>位点检查器</strong><button type="button" className="compact secondary" onClick={onClear}>清除选择</button></div>
      <dl className="mini-grid">
        <div><dt>规范位点索引</dt><dd data-testid="viewer-selected-site-index">{atom.siteIndex}</dd></div>
        <div><dt>周期偏移</dt><dd data-testid="viewer-selected-site-image-offset">[{atom.ref.imageOffset.join(", ")}]</dd></div>
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
        <div><dt>相邻键合</dt><dd data-testid="viewer-selected-site-neighbors">{connected.length ? connected.map((item)=>`${item.target.siteIndex}@[${item.target.imageOffset.join(",")}]`).join("；") : "无"}（{connected.length}）</dd></div>
      </dl>
      <div className="viewer-neighbor-table-scroll">
        <table data-testid="viewer-periodic-neighbor-table">
          <caption>{atom.siteIndex}@[{atom.ref.imageOffset.join(",")}] 的周期相邻关系。显示 {visibleConnected.length} / {connected.length}。</caption>
          <thead><tr><th scope="col">目标</th><th scope="col">物种</th><th scope="col">周期位置</th><th scope="col">距离（Å）</th><th scope="col">来源</th><th scope="col">权威</th><th scope="col">边界</th></tr></thead>
          <tbody>{visibleConnected.map(({bond,target})=>{
            const crossBoundary=target.imageOffset.some((value,index)=>value!==atom.ref.imageOffset[index]);
            const targetAtom=atoms.find((candidate)=>sameRef(candidate.ref,target));
            return <tr key={bond.id} data-testid="viewer-periodic-neighbor-row"><td><button type="button" className="compact secondary" aria-pressed={highlightedBondId===bond.id} aria-label={`高亮指向位点 ${target.siteIndex}、周期位置 ${target.imageOffset.join(", ")} 的键`} onClick={()=>{setHighlightedBondId(bond.id);onHighlightNeighbor(target,bond.id);}}>{target.siteIndex}</button></td><td>{targetAtom?.species ?? "未知"}</td><td data-testid="viewer-periodic-neighbor-offset">[{target.imageOffset.join(", ")}]</td><td data-testid="viewer-periodic-neighbor-distance">{bond.distanceAngstrom.toFixed(6)}</td><td data-testid="viewer-periodic-neighbor-source">{bond.source}</td><td data-testid="viewer-periodic-neighbor-authoritative">{bond.authoritative ? "是" : "否"}</td><td>{bond.fromSiteIndex===bond.toSiteIndex ? "自周期" : crossBoundary ? "跨边界" : "同晶胞"}</td></tr>;
          })}</tbody>
        </table>
      </div>
      {connected.length > visibleConnected.length ? <p className="notice" role="status">相邻表最多显示 {MAX_ACCESSIBLE_NEIGHBOR_ROWS} 行。</p> : null}
      <p className="viewer-inspector-note">相邻关系来自受限且非权威的场景键合。副本仅属于渲染器本地视图状态。</p>
      <div className="button-row"><button type="button" className="compact secondary" onClick={copyCoordinates}>复制坐标</button><button type="button" className="compact secondary" onClick={copySite}>复制位点 JSON</button>{!primary ? <button type="button" className="compact secondary" onClick={onJumpPrimary}>跳转到主位点</button> : null}<button type="button" className="compact secondary" onClick={onShowNeighbors}>显示相邻周期位置</button><button type="button" className="compact secondary" onClick={onClearNeighbors}>清除周期位置</button></div>
    </aside>
  );
}

function sameRef(a:RenderAtom["ref"],b:RenderAtom["ref"]){return a.siteIndex===b.siteIndex&&a.imageOffset.every((value,index)=>value===b.imageOffset[index]);}
function compareOffset(a:readonly number[],b:readonly number[]){return a[0]-b[0]||a[1]-b[1]||a[2]-b[2];}

function copyText(value: string) {
  const operation = navigator.clipboard?.writeText(value);
  if (operation) void operation.catch(() => undefined);
}
