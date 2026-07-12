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
  if (!atom) return <aside className="viewer-site-inspector" aria-label="Selected site inspector" data-testid="viewer-site-inspector"><p>No site selected. Pick an atom to inspect canonical and periodic identity.</p></aside>;
  const connected = bonds.flatMap((bond) => sameRef(bond.fromRef,atom.ref) ? [{bond,target:bond.toRef}] : sameRef(bond.toRef,atom.ref) ? [{bond,target:bond.fromRef}] : []).sort((a,b)=>a.target.siteIndex-b.target.siteIndex||compareOffset(a.target.imageOffset,b.target.imageOffset));
  const visibleConnected = connected.slice(0, MAX_ACCESSIBLE_NEIGHBOR_ROWS);
  const primary = atom.ref.imageOffset.every((value) => value === 0);
  const copyCoordinates = () => copyText(atom.position.join(", "));
  const copySite = () => copyText(JSON.stringify({ index: atom.siteIndex, image_offset: atom.ref.imageOffset, label: atom.label, element: atom.element, occupancy: atom.occupancy, canonical_xyz: atom.canonicalPosition, displayed_xyz: atom.position, frac: atom.fractionalPosition }, null, 2));
  return (
    <aside className="viewer-site-inspector" aria-label="Selected site inspector" data-testid="viewer-site-inspector">
      <div className="viewer-inspector-heading"><strong>Site inspector</strong><button type="button" className="compact secondary" onClick={onClear}>Clear selection</button></div>
      <dl className="mini-grid">
        <div><dt>canonical site index</dt><dd data-testid="viewer-selected-site-index">{atom.siteIndex}</dd></div>
        <div><dt>image offset</dt><dd data-testid="viewer-selected-site-image-offset">[{atom.ref.imageOffset.join(", ")}]</dd></div>
        <div><dt>identity</dt><dd>{primary ? "primary" : "periodic replica"}</dd></div>
        <div><dt>label</dt><dd>{atom.label}</dd></div>
        <div><dt>species / element</dt><dd data-testid="viewer-selected-site-species">{atom.species} / {atom.element}</dd></div>
        <div><dt>occupancy</dt><dd>{atom.occupancy}</dd></div>
        <div><dt>fractional</dt><dd data-testid="viewer-selected-site-fractional">{atom.fractionalPosition?.join(", ") ?? "not provided"}</dd></div>
        <div><dt>canonical Cartesian (A)</dt><dd>{atom.canonicalPosition.join(", ")}</dd></div>
        <div><dt>displayed Cartesian (A)</dt><dd data-testid="viewer-selected-site-cartesian">{atom.position.join(", ")}</dd></div>
        <div><dt>supercell</dt><dd>{repeat.join(" x ")}</dd></div>
        <div><dt>display radius</dt><dd>{atom.radius}</dd></div>
        <div><dt>source</dt><dd>{source || "canonical viewer scene"}</dd></div>
        <div><dt>bond neighbors</dt><dd data-testid="viewer-selected-site-neighbors">{connected.length ? connected.map((item)=>`${item.target.siteIndex}@[${item.target.imageOffset.join(",")}]`).join("; ") : "none"} ({connected.length})</dd></div>
      </dl>
      <div className="viewer-neighbor-table-scroll">
        <table data-testid="viewer-periodic-neighbor-table">
          <caption>Periodic neighbor relationships for {atom.siteIndex}@[{atom.ref.imageOffset.join(",")}]. Showing {visibleConnected.length} of {connected.length}.</caption>
          <thead><tr><th scope="col">Target</th><th scope="col">Species</th><th scope="col">Image</th><th scope="col">Distance (A)</th><th scope="col">Source</th><th scope="col">Authoritative</th><th scope="col">Boundary</th></tr></thead>
          <tbody>{visibleConnected.map(({bond,target})=>{
            const crossBoundary=target.imageOffset.some((value,index)=>value!==atom.ref.imageOffset[index]);
            const targetAtom=atoms.find((candidate)=>sameRef(candidate.ref,target));
            return <tr key={bond.id} data-testid="viewer-periodic-neighbor-row"><td><button type="button" className="compact secondary" aria-pressed={highlightedBondId===bond.id} aria-label={`Highlight bond to site ${target.siteIndex} at image ${target.imageOffset.join(", ")}`} onClick={()=>{setHighlightedBondId(bond.id);onHighlightNeighbor(target,bond.id);}}>{target.siteIndex}</button></td><td>{targetAtom?.species ?? "unknown"}</td><td data-testid="viewer-periodic-neighbor-offset">[{target.imageOffset.join(", ")}]</td><td data-testid="viewer-periodic-neighbor-distance">{bond.distanceAngstrom.toFixed(6)}</td><td data-testid="viewer-periodic-neighbor-source">{bond.source}</td><td data-testid="viewer-periodic-neighbor-authoritative">{bond.authoritative ? "yes" : "no"}</td><td>{bond.fromSiteIndex===bond.toSiteIndex ? "self-periodic" : crossBoundary ? "cross-boundary" : "same-cell"}</td></tr>;
          })}</tbody>
        </table>
      </div>
      {connected.length > visibleConnected.length ? <p className="notice" role="status">Neighbor table limited to {MAX_ACCESSIBLE_NEIGHBOR_ROWS} rows.</p> : null}
      <p className="viewer-inspector-note">Neighbors are from bounded, non-authoritative scene bonds only. Replicas are renderer-local view state.</p>
      <div className="button-row"><button type="button" className="compact secondary" onClick={copyCoordinates}>Copy coordinates</button><button type="button" className="compact secondary" onClick={copySite}>Copy site JSON</button>{!primary ? <button type="button" className="compact secondary" onClick={onJumpPrimary}>Jump to primary image</button> : null}<button type="button" className="compact secondary" onClick={onShowNeighbors}>Show neighboring images</button><button type="button" className="compact secondary" onClick={onClearNeighbors}>Clear images</button></div>
    </aside>
  );
}

function sameRef(a:RenderAtom["ref"],b:RenderAtom["ref"]){return a.siteIndex===b.siteIndex&&a.imageOffset.every((value,index)=>value===b.imageOffset[index]);}
function compareOffset(a:readonly number[],b:readonly number[]){return a[0]-b[0]||a[1]-b[1]||a[2]-b[2];}

function copyText(value: string) {
  const operation = navigator.clipboard?.writeText(value);
  if (operation) void operation.catch(() => undefined);
}
