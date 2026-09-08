import type { RenderBond } from "./viewerSceneRendererTypes";

export function ViewerBondInspector({ bond, onClear }: { readonly bond: RenderBond | null; readonly onClear: () => void }) {
  if (!bond) return null;
  return <aside className="viewer-site-inspector" aria-label="已选键合检查器" data-testid="viewer-bond-inspector">
    <div className="viewer-inspector-heading"><strong>键合检查器</strong><button type="button" className="compact secondary" onClick={onClear}>清除键合</button></div>
    <dl className="mini-grid">
      <div><dt>规范键合 ID</dt><dd data-testid="viewer-selected-bond-id">{bond.id}</dd></div>
      <div><dt>起点</dt><dd>{formatRef(bond.fromRef)}</dd></div>
      <div><dt>终点</dt><dd>{formatRef(bond.toRef)}</dd></div>
      <div><dt>距离（Å）</dt><dd>{bond.distanceAngstrom.toFixed(6)}</dd></div>
      <div><dt>来源</dt><dd>{bond.source}</dd></div>
      <div><dt>权威数据</dt><dd>{bond.authoritative ? "是" : "否"}</dd></div>
    </dl>
    <p className="viewer-inspector-note">选择使用系统输出的规范拓扑；不会推断或修改键合拓扑。</p>
  </aside>;
}

function formatRef(ref: RenderBond["fromRef"]) { return `${ref.siteIndex}@[${ref.imageOffset.join(",")}]`; }
