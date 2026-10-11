import type { RenderBond, ValidatedRenderScene } from "./viewerSceneRendererTypes";

export function ViewerBondInspector({ bond, onClear, neighborMethod }: { readonly bond: RenderBond | null; readonly onClear: () => void; readonly neighborMethod?: NonNullable<ValidatedRenderScene["connectivity"]>["method"] }) {
  if (!bond) return null;
  if (neighborMethod) return <aside className="viewer-site-inspector" aria-label="已选近邻连接" data-testid="viewer-bond-inspector">
    <div className="viewer-inspector-heading"><strong>近邻连接</strong><button type="button" className="compact secondary" onClick={onClear}>清除连接</button></div>
    <dl className="viewer-site-essentials">
      <div><dt>起点</dt><dd>{formatRef(bond.fromRef)}</dd></div>
      <div><dt>终点</dt><dd>{formatRef(bond.toRef)}</dd></div>
      <div><dt>距离（Å）</dt><dd>{bond.distanceAngstrom.toFixed(6)}</dd></div>
    </dl>
    <details className="viewer-site-details"><summary>来源与判定</summary>
      <p>{neighborMethod === "ideal_first_shell" ? "理想模型中已保存的最短周期近邻，不表示确定的化学键或键级。" : "参考共价半径筛选的距离候选，未确定化学键或键级。"}</p>
      <dl className="mini-grid"><div><dt>连接标识</dt><dd data-testid="viewer-selected-bond-id">{bond.id}</dd></div></dl>
    </details>
  </aside>;
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
