import type { RenderBond } from "./viewerSceneRendererTypes";

export function ViewerBondInspector({ bond, onClear }: { readonly bond: RenderBond | null; readonly onClear: () => void }) {
  if (!bond) return null;
  return <aside className="viewer-site-inspector" aria-label="Selected bond inspector" data-testid="viewer-bond-inspector">
    <div className="viewer-inspector-heading"><strong>Bond inspector</strong><button type="button" className="compact secondary" onClick={onClear}>Clear bond</button></div>
    <dl className="mini-grid">
      <div><dt>canonical bond id</dt><dd data-testid="viewer-selected-bond-id">{bond.id}</dd></div>
      <div><dt>from</dt><dd>{formatRef(bond.fromRef)}</dd></div>
      <div><dt>to</dt><dd>{formatRef(bond.toRef)}</dd></div>
      <div><dt>distance (A)</dt><dd>{bond.distanceAngstrom.toFixed(6)}</dd></div>
      <div><dt>source</dt><dd>{bond.source}</dd></div>
      <div><dt>authoritative</dt><dd>{bond.authoritative ? "yes" : "no"}</dd></div>
    </dl>
    <p className="viewer-inspector-note">Selection uses emitted canonical topology; no bond inference or topology mutation occurs.</p>
  </aside>;
}

function formatRef(ref: RenderBond["fromRef"]) { return `${ref.siteIndex}@[${ref.imageOffset.join(",")}]`; }
