import { VIEWER_EXPORT_LIMITS, VIEWER_EXPORT_PRESETS, type ViewerExportBackground, type ViewerExportFormat, type ViewerExportRequest } from "./viewerSceneExport";

export function ViewerExportPanel({request,busy,status,bundleReady,onChange,onExport,onDownload}:Readonly<{request:ViewerExportRequest;busy:boolean;status:string;bundleReady:boolean;onChange:(request:ViewerExportRequest)=>void;onExport:()=>void;onDownload:(kind:"png"|"json"|"markdown"|"manifest")=>void}>){
  const effective=request.width*request.height*request.pixelRatio*request.pixelRatio;
  const update=<K extends keyof ViewerExportRequest>(key:K,value:ViewerExportRequest[K])=>onChange(Object.freeze({...request,[key]:value}));
  const presetLabel: Record<string, string> = { web: "网页", presentation: "演示", square: "方形", publication: "出版" };
  return <fieldset className="viewer-export-panel" aria-label="科学导出控制">
    <legend>科学导出</legend>
    <div className="viewer-export-grid">
      <label>格式<select data-testid="viewer-export-format" value={request.format} onChange={(event)=>update("format",event.target.value as ViewerExportFormat)}><option value="png">PNG 图片</option><option value="json">查看状态 JSON</option><option value="markdown">科学 Markdown</option></select></label>
      <label>宽度<input data-testid="viewer-export-width" type="number" min={VIEWER_EXPORT_LIMITS.minWidth} max={VIEWER_EXPORT_LIMITS.maxWidth} step="1" value={request.width} onChange={(event)=>update("width",Number(event.target.value))}/></label>
      <label>高度<input data-testid="viewer-export-height" type="number" min={VIEWER_EXPORT_LIMITS.minHeight} max={VIEWER_EXPORT_LIMITS.maxHeight} step="1" value={request.height} onChange={(event)=>update("height",Number(event.target.value))}/></label>
      <label>像素比<select data-testid="viewer-export-pixel-ratio" value={request.pixelRatio} onChange={(event)=>update("pixelRatio",Number(event.target.value) as 1|2)}><option value="1">1x</option><option value="2">2x</option></select></label>
      <label>背景<select data-testid="viewer-export-background" value={request.background} onChange={(event)=>update("background",event.target.value as ViewerExportBackground)}><option value="light">浅色</option><option value="dark">深色</option><option value="transparent">透明</option></select></label>
    </div>
    <div className="viewer-export-presets" aria-label="导出尺寸预设">{Object.entries(VIEWER_EXPORT_PRESETS).map(([name,size])=><button type="button" className="compact secondary" key={name} onClick={()=>onChange(Object.freeze({...request,width:size[0],height:size[1],pixelRatio:1}))}>{presetLabel[name] || name}</button>)}</div>
    <div className="viewer-export-options">
      <label><input type="checkbox" checked={request.includeCell} onChange={(event)=>update("includeCell",event.target.checked)}/>晶胞边界</label>
      <label><input type="checkbox" checked={request.includeAxes} onChange={(event)=>update("includeAxes",event.target.checked)}/>晶格轴</label>
      <label><input type="checkbox" checked={request.includeBonds} onChange={(event)=>update("includeBonds",event.target.checked)}/>键合</label>
      <label><input type="checkbox" checked={request.includeMeasurements} onChange={(event)=>update("includeMeasurements",event.target.checked)}/>测量标记</label>
      <label><input type="checkbox" checked={request.includeInspectorSummary} onChange={(event)=>update("includeInspectorSummary",event.target.checked)}/>已选位点摘要</label>
    </div>
    <output data-testid="viewer-export-estimate">{request.width} × {request.height}，像素比 {request.pixelRatio}×；有效像素 {effective.toLocaleString()}；{request.background === "light" ? "浅色" : request.background === "dark" ? "深色" : "透明"}背景。</output>
    <button type="button" className="compact secondary" data-testid="viewer-scene-export-png" onClick={onExport} disabled={busy}>{busy?"正在导出……":`导出 ${request.format}`}</button>
    <div className="viewer-export-downloads" aria-label="已准备的导出文件">
      <button type="button" className="compact secondary" disabled={!bundleReady||busy} onClick={()=>onDownload("png")}>下载 PNG</button>
      <button type="button" className="compact secondary" disabled={!bundleReady||busy} onClick={()=>onDownload("json")}>下载导出 JSON</button>
      <button type="button" className="compact secondary" disabled={!bundleReady||busy} onClick={()=>onDownload("markdown")}>下载导出 Markdown</button>
      <button type="button" className="compact secondary" data-testid="viewer-export-manifest" disabled={!bundleReady||busy} onClick={()=>onDownload("manifest")}>下载导出清单</button>
    </div>
    <output role="status" aria-live="polite" data-testid="viewer-export-status">{status}</output>
  </fieldset>;
}
