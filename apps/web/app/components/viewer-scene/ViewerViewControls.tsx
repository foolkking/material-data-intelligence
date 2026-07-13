import { VIEWER_CLIP_AXES, type CameraPreset, type ViewerCellDisplayState, type ViewerClipAxis, type ViewerClipState } from "./viewerSceneViewState";

export function ViewerViewControls({ clip, bounds, display, preset, latticeLengths, onClipEnabled, onPlaneEnabled, onPosition, onResetClip, onDisplay, onPreset, onDownload }: Readonly<{
  clip: ViewerClipState;
  bounds: Readonly<Record<ViewerClipAxis, readonly [number, number]>>;
  display: ViewerCellDisplayState;
  preset: CameraPreset;
  latticeLengths: readonly [number, number, number];
  onClipEnabled: (enabled: boolean) => void;
  onPlaneEnabled: (axis: ViewerClipAxis, enabled: boolean) => void;
  onPosition: (axis: ViewerClipAxis, position: number) => void;
  onResetClip: () => void;
  onDisplay: (kind: keyof ViewerCellDisplayState, visible: boolean) => void;
  onPreset: (preset: CameraPreset) => void;
  onDownload: () => void;
}>) {
  const active = clip.enabled ? clip.planes.filter((plane) => plane.enabled) : [];
  return <fieldset className="viewer-view-controls" aria-label="Clipping, cell, and camera controls">
    <legend>View controls</legend>
    <div className="viewer-view-control-groups">
      <section aria-label="Axis-aligned clipping">
        <div className="viewer-control-heading"><strong>Clipping</strong><button type="button" className={`compact ${clip.enabled ? "active" : "secondary"}`} data-testid="viewer-clipping-enabled" aria-pressed={clip.enabled} onClick={() => onClipEnabled(!clip.enabled)}>{clip.enabled ? "Disable clipping" : "Enable clipping"}</button><button type="button" className="compact secondary" data-testid="viewer-clipping-reset" onClick={onResetClip}>Reset clipping</button></div>
        {VIEWER_CLIP_AXES.map((axis, index) => {
          const plane = clip.planes[index]; const [min,max] = bounds[axis]; const step = Math.max((max-min)/100, 0.001);
          return <div className="viewer-clip-row" key={axis}>
            <label><input type="checkbox" data-testid={`viewer-clip-${axis}-enabled`} checked={plane.enabled} onChange={(event)=>onPlaneEnabled(axis,event.target.checked)} />{axis.toUpperCase()} plane</label>
            <input aria-label={`${axis.toUpperCase()} clipping position`} data-testid={`viewer-clip-${axis}-slider`} type="range" min={min} max={max} step={step} value={plane.position} onChange={(event)=>onPosition(axis,Number(event.target.value))} />
            <input aria-label={`${axis.toUpperCase()} clipping position in angstrom`} data-testid={`viewer-clip-${axis}-position`} type="number" min={min} max={max} step={step} value={plane.position} onChange={(event)=>onPosition(axis,Number(event.target.value))} />
          </div>;
        })}
        <output role="status" aria-live="polite" data-testid="viewer-clipping-status">{active.length ? `Clipping enabled: ${active.map((plane)=>`${plane.axis.toUpperCase()} at ${plane.position.toFixed(3)} angstrom`).join("; ")}.` : "Clipping disabled."}</output>
      </section>
      <section aria-label="Cell and lattice display">
        <strong>Cell and lattice</strong>
        <div className="viewer-display-toggles">
          <button type="button" className={`compact ${display.unitCell ? "active" : "secondary"}`} data-testid="viewer-scene-renderer-toggle-cell" aria-pressed={display.unitCell} onClick={()=>onDisplay("unitCell",!display.unitCell)}>Unit cell</button>
          <button type="button" className={`compact ${display.supercellBoundary ? "active" : "secondary"}`} data-testid="viewer-scene-renderer-toggle-supercell-boundary" aria-pressed={display.supercellBoundary} onClick={()=>onDisplay("supercellBoundary",!display.supercellBoundary)}>Supercell boundary</button>
          <button type="button" className={`compact ${display.latticeAxes ? "active" : "secondary"}`} data-testid="viewer-lattice-axes" aria-pressed={display.latticeAxes} onClick={()=>onDisplay("latticeAxes",!display.latticeAxes)}>Lattice axes</button>
        </div>
        <dl className="mini-grid viewer-lattice-vector-summary">{(["a","b","c"] as const).map((axis,index)=><div key={axis}><dt>{axis} vector</dt><dd>{latticeLengths[index].toFixed(3)} angstrom</dd></div>)}</dl>
      </section>
      <section aria-label="Camera presets">
        <strong>Camera</strong>
        <div className="viewer-camera-presets">{(["default","top","front","side","isometric"] as const).map((value)=><button type="button" key={value} className={`compact ${preset===value ? "active" : "secondary"}`} data-testid={`viewer-camera-${value}`} aria-pressed={preset===value} onClick={()=>onPreset(value)}>{value[0].toUpperCase()+value.slice(1)}</button>)}</div>
        <output role="status" aria-live="polite" data-testid="viewer-camera-status">Camera preset: {preset}.</output>
        <button type="button" className="compact secondary" data-testid="viewer-view-state-download" onClick={onDownload}>Download view state</button>
      </section>
    </div>
  </fieldset>;
}
