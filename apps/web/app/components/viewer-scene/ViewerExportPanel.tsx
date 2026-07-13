import { VIEWER_EXPORT_LIMITS, VIEWER_EXPORT_PRESETS, type ViewerExportBackground, type ViewerExportFormat, type ViewerExportRequest } from "./viewerSceneExport";

export function ViewerExportPanel({request,busy,status,bundleReady,onChange,onExport,onDownload}:Readonly<{request:ViewerExportRequest;busy:boolean;status:string;bundleReady:boolean;onChange:(request:ViewerExportRequest)=>void;onExport:()=>void;onDownload:(kind:"png"|"json"|"markdown"|"manifest")=>void}>){
  const effective=request.width*request.height*request.pixelRatio*request.pixelRatio;
  const update=<K extends keyof ViewerExportRequest>(key:K,value:ViewerExportRequest[K])=>onChange(Object.freeze({...request,[key]:value}));
  return <fieldset className="viewer-export-panel" aria-label="Scientific export controls">
    <legend>Scientific export</legend>
    <div className="viewer-export-grid">
      <label>Format<select data-testid="viewer-export-format" value={request.format} onChange={(event)=>update("format",event.target.value as ViewerExportFormat)}><option value="png">PNG image</option><option value="json">Viewer state JSON</option><option value="markdown">Scientific Markdown</option></select></label>
      <label>Width<input data-testid="viewer-export-width" type="number" min={VIEWER_EXPORT_LIMITS.minWidth} max={VIEWER_EXPORT_LIMITS.maxWidth} step="1" value={request.width} onChange={(event)=>update("width",Number(event.target.value))}/></label>
      <label>Height<input data-testid="viewer-export-height" type="number" min={VIEWER_EXPORT_LIMITS.minHeight} max={VIEWER_EXPORT_LIMITS.maxHeight} step="1" value={request.height} onChange={(event)=>update("height",Number(event.target.value))}/></label>
      <label>Pixel ratio<select data-testid="viewer-export-pixel-ratio" value={request.pixelRatio} onChange={(event)=>update("pixelRatio",Number(event.target.value) as 1|2)}><option value="1">1x</option><option value="2">2x</option></select></label>
      <label>Background<select data-testid="viewer-export-background" value={request.background} onChange={(event)=>update("background",event.target.value as ViewerExportBackground)}><option value="light">Light</option><option value="dark">Dark</option><option value="transparent">Transparent</option></select></label>
    </div>
    <div className="viewer-export-presets" aria-label="Export size presets">{Object.entries(VIEWER_EXPORT_PRESETS).map(([name,size])=><button type="button" className="compact secondary" key={name} onClick={()=>onChange(Object.freeze({...request,width:size[0],height:size[1],pixelRatio:1}))}>{name}</button>)}</div>
    <div className="viewer-export-options">
      <label><input type="checkbox" checked={request.includeCell} onChange={(event)=>update("includeCell",event.target.checked)}/>Cell boundaries</label>
      <label><input type="checkbox" checked={request.includeAxes} onChange={(event)=>update("includeAxes",event.target.checked)}/>Lattice axes</label>
      <label><input type="checkbox" checked={request.includeBonds} onChange={(event)=>update("includeBonds",event.target.checked)}/>Bonds</label>
      <label><input type="checkbox" checked={request.includeMeasurements} onChange={(event)=>update("includeMeasurements",event.target.checked)}/>Measurement overlays</label>
      <label><input type="checkbox" checked={request.includeInspectorSummary} onChange={(event)=>update("includeInspectorSummary",event.target.checked)}/>Selected site summary</label>
    </div>
    <output data-testid="viewer-export-estimate">{request.width} x {request.height} at {request.pixelRatio}x; {effective.toLocaleString()} effective pixels; {request.background} background.</output>
    <button type="button" className="compact secondary" data-testid="viewer-scene-export-png" onClick={onExport} disabled={busy}>{busy?"Exporting...":`Export ${request.format}`}</button>
    <div className="viewer-export-downloads" aria-label="Prepared export artifacts">
      <button type="button" className="compact secondary" disabled={!bundleReady||busy} onClick={()=>onDownload("png")}>Download PNG</button>
      <button type="button" className="compact secondary" disabled={!bundleReady||busy} onClick={()=>onDownload("json")}>Download export JSON</button>
      <button type="button" className="compact secondary" disabled={!bundleReady||busy} onClick={()=>onDownload("markdown")}>Download export Markdown</button>
      <button type="button" className="compact secondary" data-testid="viewer-export-manifest" disabled={!bundleReady||busy} onClick={()=>onDownload("manifest")}>Download export manifest</button>
    </div>
    <output role="status" aria-live="polite" data-testid="viewer-export-status">{status}</output>
  </fieldset>;
}
