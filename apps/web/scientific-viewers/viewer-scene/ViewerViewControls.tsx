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
  return <fieldset className="viewer-view-controls" aria-label="裁剪、晶胞和相机控制">
    <legend>视图控制</legend>
    <div className="viewer-view-control-groups">
      <section aria-label="轴向裁剪">
        <div className="viewer-control-heading"><strong>裁剪</strong><button type="button" className={`compact ${clip.enabled ? "active" : "secondary"}`} data-testid="viewer-clipping-enabled" aria-pressed={clip.enabled} onClick={() => onClipEnabled(!clip.enabled)}>{clip.enabled ? "停用裁剪" : "启用裁剪"}</button><button type="button" className="compact secondary" data-testid="viewer-clipping-reset" onClick={onResetClip}>重置裁剪</button></div>
        {VIEWER_CLIP_AXES.map((axis, index) => {
          const plane = clip.planes[index]; const [min,max] = bounds[axis]; const step = Math.max((max-min)/100, 0.001);
          return <div className="viewer-clip-row" key={axis}>
            <label><input type="checkbox" data-testid={`viewer-clip-${axis}-enabled`} checked={plane.enabled} onChange={(event)=>onPlaneEnabled(axis,event.target.checked)} />{axis.toUpperCase()} 平面</label>
            <input aria-label={`${axis.toUpperCase()} 裁剪位置`} data-testid={`viewer-clip-${axis}-slider`} type="range" min={min} max={max} step={step} value={plane.position} onChange={(event)=>onPosition(axis,Number(event.target.value))} />
            <input aria-label={`${axis.toUpperCase()} 裁剪位置（Å）`} data-testid={`viewer-clip-${axis}-position`} type="number" min={min} max={max} step={step} value={plane.position} onChange={(event)=>onPosition(axis,Number(event.target.value))} />
          </div>;
        })}
        <output role="status" aria-live="polite" data-testid="viewer-clipping-status">{active.length ? `裁剪已启用：${active.map((plane)=>`${plane.axis.toUpperCase()} 位于 ${plane.position.toFixed(3)} Å`).join("；")}。` : "裁剪已停用。"}</output>
      </section>
      <section aria-label="晶胞与晶格显示">
        <strong>晶胞与晶格</strong>
        <div className="viewer-display-toggles">
          <button type="button" className={`compact ${display.unitCell ? "active" : "secondary"}`} data-testid="viewer-scene-renderer-toggle-cell" aria-pressed={display.unitCell} onClick={()=>onDisplay("unitCell",!display.unitCell)}>晶胞</button>
          <button type="button" className={`compact ${display.supercellBoundary ? "active" : "secondary"}`} data-testid="viewer-scene-renderer-toggle-supercell-boundary" aria-pressed={display.supercellBoundary} onClick={()=>onDisplay("supercellBoundary",!display.supercellBoundary)}>超晶胞边界</button>
          <button type="button" className={`compact ${display.latticeAxes ? "active" : "secondary"}`} data-testid="viewer-lattice-axes" aria-pressed={display.latticeAxes} onClick={()=>onDisplay("latticeAxes",!display.latticeAxes)}>晶格轴</button>
        </div>
        <dl className="mini-grid viewer-lattice-vector-summary">{(["a","b","c"] as const).map((axis,index)=><div key={axis}><dt>{axis} 晶格矢量</dt><dd>{latticeLengths[index].toFixed(3)} Å</dd></div>)}</dl>
      </section>
      <section aria-label="相机预设">
        <strong>相机</strong>
        <div className="viewer-camera-presets">{(["default","top","front","side","isometric"] as const).map((value)=><button type="button" key={value} className={`compact ${preset===value ? "active" : "secondary"}`} data-testid={`viewer-camera-${value}`} aria-pressed={preset===value} onClick={()=>onPreset(value)}>{({default:"默认",top:"顶部",front:"前方",side:"侧面",isometric:"等轴"} as const)[value]}</button>)}</div>
        <output role="status" aria-live="polite" data-testid="viewer-camera-status">当前相机视角：{preset}。</output>
        <button type="button" className="compact secondary" data-testid="viewer-view-state-download" onClick={onDownload}>下载视图状态</button>
      </section>
    </div>
  </fieldset>;
}
