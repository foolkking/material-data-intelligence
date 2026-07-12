import type { RenderAtom, RenderBond } from "./viewerSceneRendererTypes";

export function ViewerSiteInspector({ atom, bonds, source, onClear }: {
  readonly atom: RenderAtom | null;
  readonly bonds: readonly RenderBond[];
  readonly source: string;
  readonly onClear: () => void;
}) {
  if (!atom) return <aside className="viewer-site-inspector" data-testid="viewer-site-inspector"><p>No site selected. Pick an atom to inspect canonical site data.</p></aside>;
  const connected = bonds.flatMap((bond) => bond.fromSiteIndex === atom.siteIndex ? [bond.toSiteIndex] : bond.toSiteIndex === atom.siteIndex ? [bond.fromSiteIndex] : []).sort((a, b) => a - b);
  const copyCoordinates = () => copyText(atom.position.join(", "));
  const copySite = () => copyText(JSON.stringify({ index: atom.siteIndex, label: atom.label, element: atom.element, occupancy: atom.occupancy, xyz: atom.position, frac: atom.fractionalPosition }, null, 2));
  return (
    <aside className="viewer-site-inspector" aria-label="Selected site inspector" data-testid="viewer-site-inspector">
      <div className="viewer-inspector-heading"><strong>Site inspector</strong><button type="button" className="compact secondary" onClick={onClear}>Clear selection</button></div>
      <dl className="mini-grid">
        <div><dt>site index</dt><dd data-testid="viewer-selected-site-index">{atom.siteIndex}</dd></div>
        <div><dt>label</dt><dd>{atom.label}</dd></div>
        <div><dt>species / element</dt><dd data-testid="viewer-selected-site-species">{atom.species} / {atom.element}</dd></div>
        <div><dt>occupancy</dt><dd>{atom.occupancy}</dd></div>
        <div><dt>fractional</dt><dd data-testid="viewer-selected-site-fractional">{atom.fractionalPosition?.join(", ") ?? "not provided"}</dd></div>
        <div><dt>Cartesian (Å)</dt><dd data-testid="viewer-selected-site-cartesian">{atom.position.join(", ")}</dd></div>
        <div><dt>display radius</dt><dd>{atom.radius}</dd></div>
        <div><dt>source</dt><dd>{source || "canonical viewer scene"}</dd></div>
        <div><dt>bond neighbors</dt><dd data-testid="viewer-selected-site-neighbors">{connected.length ? connected.join(", ") : "none"} ({connected.length})</dd></div>
      </dl>
      <p className="viewer-inspector-note">Neighbors are from bounded, non-authoritative scene bonds only.</p>
      <div className="button-row"><button type="button" className="compact secondary" onClick={copyCoordinates}>Copy coordinates</button><button type="button" className="compact secondary" onClick={copySite}>Copy site JSON</button></div>
    </aside>
  );
}

function copyText(value: string) {
  const operation = navigator.clipboard?.writeText(value);
  if (operation) void operation.catch(() => undefined);
}
