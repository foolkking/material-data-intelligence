"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { supportsManagedWebGL } from "../viewer-scene/viewerWebglCapability";
import styles from "./BrillouinZoneSurface.module.css";
import { BrillouinZoneLabels } from "./BrillouinZoneLabels";
import { BZ_RENDERER_CAPS, mapBrillouinZoneArtifacts, type BZArtifactBundle } from "./brillouinZoneMapper";
import type { BZCameraPreset, BZExportRequest, BZProjection, BZRendererEngine, BZRendererEngineFactory, BZRendererSnapshot, BZRendererState, BZSelection, BZVisibility } from "./brillouinZoneTypes";

export type BrillouinZoneSurfaceProps = Readonly<{
  bundle: BZArtifactBundle;
  capabilityOverride?: boolean;
  engineFactory?: BZRendererEngineFactory;
  summary?: string;
  recipe?: unknown;
  externalSelection?: BZSelection | null;
  onSelection?: (selection: BZSelection | null) => void;
}>;

const DEFAULT_VISIBILITY: BZVisibility = Object.freeze({faces:true,edges:true,vertices:false,axes:true,points:true,labels:true,path:true});
const DEFAULT_EXPORT: BZExportRequest = Object.freeze({width:1600,height:1200,pixelRatio:1,background:"light"});

const defaultEngineFactory: BZRendererEngineFactory = async (args) => {
  let timer: ReturnType<typeof setTimeout> | undefined;
  try {
    const module = await Promise.race([
      import("./brillouinZoneEngine"),
      new Promise<never>((_, reject) => { timer=setTimeout(()=>reject(new Error("BZ_RENDERER_CHUNK_TIMEOUT")),15_000); }),
    ]);
    return module.createBrillouinZoneEngine(args);
  } catch {
    throw new Error("BZ_RENDERER_CHUNK_LOAD_FAILED");
  } finally { if(timer)clearTimeout(timer); }
};

export function BrillouinZoneSurface({bundle,capabilityOverride,engineFactory=defaultEngineFactory,summary,recipe,externalSelection,onSelection:selectionListener}:BrillouinZoneSurfaceProps) {
  const mapping=useMemo(()=>mapBrillouinZoneArtifacts(bundle),[bundle]);
  const containerRef=useRef<HTMLDivElement>(null);
  const engineRef=useRef<BZRendererEngine|null>(null);
  const generationRef=useRef(0);
  const [state,setState]=useState<BZRendererState>(mapping.ok?"ready":mapping.code==="BZ_RENDERER_RESOURCE_LIMIT"?"over_cap":"invalid");
  const [attempt,setAttempt]=useState(0);
  const [visibility,setVisibility]=useState<BZVisibility>(DEFAULT_VISIBILITY);
  const [opacity,setOpacity]=useState(.28);
  const [projection,setProjection]=useState<BZProjection>("perspective");
  const [preset,setPreset]=useState<BZCameraPreset>("isometric");
  const [variantId,setVariantId]=useState<string|null>(mapping.ok?mapping.scene.selectedVariantId:null);
  const [selection,setSelection]=useState<BZSelection|null>(null);
  const [snapshot,setSnapshot]=useState<BZRendererSnapshot|null>(null);
  const [exportRequest,setExportRequest]=useState<BZExportRequest>(DEFAULT_EXPORT);
  const [exportState,setExportState]=useState("");
  const [exporting,setExporting]=useState(false);
  const exportingRef=useRef<BZRendererEngine|null>(null);
  const [announcement,setAnnouncement]=useState("布里渊区查看器已就绪。");
  const selectionRef=useRef(selection);selectionRef.current=selection;

  const refreshSnapshot=useCallback(()=>{const engine=engineRef.current;if(engine)setSnapshot(engine.snapshot());},[]);
  const onSelection=useCallback((next:BZSelection|null)=>{setSelection(next);setAnnouncement(next?`已选择${next.kind === "point" ? "点" : next.kind === "face" ? "面" : next.kind === "vertex" ? "顶点" : "路径段"} ${next.id}。`:"已清除选择。");selectionListener?.(next);},[selectionListener]);
  const onViewChange=useCallback(()=>{setExportState("");queueMicrotask(refreshSnapshot);},[refreshSnapshot]);

  useEffect(()=>{
    exportingRef.current=null;setExporting(false);setExportState("");
    setSelection(null);setSnapshot(null);setVisibility(DEFAULT_VISIBILITY);setOpacity(.28);setProjection("perspective");setPreset("isometric");setVariantId(mapping.ok?mapping.scene.selectedVariantId:null);setState(mapping.ok?"ready":mapping.code==="BZ_RENDERER_RESOURCE_LIMIT"?"over_cap":"invalid");
  },[bundle,mapping]);

  useEffect(()=>{
    if(!mapping.ok)return;
    const supported=capabilityOverride??supportsManagedWebGL();
    if(!supported){setState("unsupported");return;}
    const container=containerRef.current;if(!container)return;
    let cancelled=false;const generation=++generationRef.current;setState("initializing");
    void engineFactory({container,scene:mapping.scene,visibility,opacity,projection,variantId,mappingMs:mapping.mappingMs,artifactBytes:mapping.artifactBytes,onSelection,onContextLost:()=>{setState("context_lost");queueMicrotask(()=>{engineRef.current?.dispose();engineRef.current=null;});},onViewChange}).then((engine)=>{
      if(cancelled||generation!==generationRef.current){engine.dispose();return;}
      engineRef.current=engine;engine.setSelection(selectionRef.current);setSnapshot(engine.snapshot());setState("rendered");setAnnouncement(`已渲染 ${mapping.scene.faces.length} 个面、${mapping.scene.edges.length} 条边和 ${mapping.scene.points.length} 个高对称点。`);
    }).catch(()=>{if(!cancelled)setState("renderer_failed");});
    return()=>{cancelled=true;if(generation===generationRef.current)generationRef.current+=1;const engine=engineRef.current;engineRef.current=null;if(engine)try{engine.dispose();}catch{/* detached surfaces dispose best-effort */}};
  },[attempt,capabilityOverride,engineFactory,mapping,onSelection,onViewChange]);

  useEffect(()=>{engineRef.current?.setSelection(selection);refreshSnapshot();},[refreshSnapshot,selection]);
  useEffect(()=>{if(externalSelection!==undefined)setSelection(externalSelection);},[externalSelection]);
  const updateVisibility=(key:keyof BZVisibility)=>{const next=Object.freeze({...visibility,[key]:!visibility[key]});setVisibility(next);engineRef.current?.setVisibility(next);if(selection&&((selection.kind==="point"&&!next.points)||(selection.kind==="vertex"&&!next.vertices)||(selection.kind==="face"&&!next.faces)||((selection.kind==="segment"||selection.kind==="reciprocal_sample")&&!next.path)))setSelection(null);refreshSnapshot();};
  const updateProjection=(next:BZProjection)=>{setProjection(next);engineRef.current?.setProjection(next);refreshSnapshot();};
  const updatePreset=(next:BZCameraPreset)=>{setPreset(next);engineRef.current?.setCameraPreset(next);refreshSnapshot();};
  const updateVariant=(next:string)=>{setVariantId(next||null);setSelection(null);engineRef.current?.setVariant(next||null);refreshSnapshot();};
  const reset=()=>{setPreset("isometric");engineRef.current?.resetCamera();refreshSnapshot();};
  const exportPng=async()=>{
    const engine=engineRef.current;if(!engine||exportingRef.current===engine)return;
    exportingRef.current=engine;setExporting(true);setExportState("");
    try {
      const blob=await engine.exportPng(exportRequest);
      if(engineRef.current!==engine)return;
      downloadBlob(blob,safeFilename(`${mapping.ok?mapping.scene.packageId:"brillouin-zone"}-brillouin-zone.png`));
      setExportState("图片已生成，下载已开始。");
    } catch(error) {
      if(engineRef.current!==engine)return;
      setExportState(error instanceof Error&&error.message==="BZ_EXPORT_LABELS_DO_NOT_FIT"?"标签过密，请调整视角或隐藏标签后重试。":"图片导出失败，请重试。");
    } finally {
      if(exportingRef.current===engine){exportingRef.current=null;setExporting(false);}
    }
  };
  const selected=mapping.ok&&selection?selectionDetails(mapping.scene,selection):null;
  const labels=mapping.ok&&visibility.labels&&snapshot?snapshot.pointScreenPositions.slice(0,BZ_RENDERER_CAPS.visibleLabels):[];
  const onKeyDown=(event:React.KeyboardEvent<HTMLElement>)=>{
    if(event.defaultPrevented||event.altKey||event.ctrlKey||event.metaKey)return;
    const target=event.target;
    if(target instanceof HTMLElement&&target.closest("input, select, textarea, button, a, summary, [contenteditable]:not([contenteditable='false'])"))return;
    const actions:Record<string,Parameters<BZRendererEngine["keyboardCamera"]>[0]>={ArrowLeft:"rotate_left",ArrowRight:"rotate_right",ArrowUp:"rotate_up",ArrowDown:"rotate_down","+":"zoom_in","=":"zoom_in","-":"zoom_out"};
    if(actions[event.key]){event.preventDefault();engineRef.current?.keyboardCamera(actions[event.key]);refreshSnapshot();}
    if(event.key.toLowerCase()==="r"){event.preventDefault();reset();}
  };

  return <section className={`brillouin-zone-surface ${styles.surface}`} data-testid="brillouin-zone-renderer-surface" aria-label="第一布里渊区查看器" tabIndex={0} onKeyDown={onKeyDown}>
    <output className="sr-only" aria-live="polite" data-testid="brillouin-zone-live-region">{announcement}</output>
    <div className="brillouin-zone-heading"><div><h3>三维布里渊区</h3><p>已验证的倒易笛卡尔几何（Å⁻¹），采用物理学 2π 约定</p></div><code data-testid="brillouin-zone-renderer-state">{state}</code></div>
    {!mapping.ok?<Fallback code={mapping.code} text="规范化倒易空间数据在 WebGL 初始化前未通过校验。" errors={mapping.errors}/>:null}
    {mapping.ok&&state==="unsupported"?<Fallback code="BZ_RENDERER_UNSUPPORTED" text="当前环境不支持 WebGL；科学数据表和结构化数据仍可查看。"/>:null}
    {mapping.ok&&state==="over_cap"?<Fallback code="BZ_RENDERER_RESOURCE_LIMIT" text="已验证场景超过图形资源预算，未渲染不完整几何。"/>:null}
    {mapping.ok&&state==="context_lost"?<Fallback code="BZ_RENDERER_CONTEXT_LOST" text="图形上下文已丢失，过期 GPU 资源已释放。" action="重新初始化查看器" onAction={()=>setAttempt((value)=>value+1)}/>:null}
    {mapping.ok&&state==="renderer_failed"?<Fallback code="BZ_RENDERER_INITIALIZATION_FAILED" text="本地查看器无法初始化；结构化数据和文本视图仍可查看。" action="重试查看器" onAction={()=>setAttempt((value)=>value+1)}/>:null}
    {mapping.ok&&(state==="ready"||state==="initializing")?<div className="viewer-renderer-loading" role="status">正在加载本地三维查看器…</div>:null}
    {mapping.ok?<>
      <div className={`brillouin-zone-controls ${styles.controls}`} aria-label="布里渊区显示控制">
        <div className={styles.visibility} role="group" aria-label="显示内容">
        {(["faces","edges","vertices","axes","points","labels","path"] as const).map((key)=><button key={key} type="button" aria-pressed={visibility[key]} className={visibility[key]?"active":"secondary"} onClick={()=>updateVisibility(key)}>{({faces:"面",edges:"边",vertices:"顶点",axes:"坐标轴",points:"高对称点",labels:"标签",path:"路径"} as const)[key]}</button>)}
        </div>
        <label>面透明度 <input data-testid="brillouin-zone-opacity" type="range" min="0.08" max="0.65" step="0.01" value={opacity} aria-valuetext={`${Math.round(opacity*100)}%`} onChange={(event)=>{const value=Number(event.target.value);setOpacity(value);engineRef.current?.setOpacity(value);refreshSnapshot();}}/></label>
        <label>投影 <select data-testid="brillouin-zone-projection" value={projection} onChange={(event)=>updateProjection(event.target.value as BZProjection)}><option value="perspective">透视</option><option value="orthographic">正交</option></select></label>
        <label>视角 <select data-testid="brillouin-zone-camera-preset" value={preset} onChange={(event)=>updatePreset(event.target.value as BZCameraPreset)}><option value="isometric">等轴测</option><option value="b1">+b1</option><option value="b2">+b2</option><option value="b3">+b3</option></select></label>
        {mapping.scene.variants.length?<label>路径变体 <select data-testid="brillouin-zone-path-variant" value={variantId??""} onChange={(event)=>updateVariant(event.target.value)}>{mapping.scene.variants.map((item)=><option key={item.id} value={item.id}>{item.description}</option>)}</select></label>:null}
        <button type="button" className="product-secondary-action" data-testid="brillouin-zone-reset" onClick={reset}>适配视图</button>
      </div>
      <div className="brillouin-zone-stage">
        <div className="viewer-renderer-canvas-host" ref={containerRef} data-testid="brillouin-zone-canvas-host"/>
        <BrillouinZoneLabels points={labels.filter(position => position.visible !== false).flatMap(position => { const point = mapping.scene.points.find(item => item.id === position.id); return point ? [{ ...position, text: point.displayLabel }] : []; })} selectedId={selection?.kind === "point" ? selection.id : undefined} onSelect={id => onSelection({kind:"point",id})} />
      </div>
      <div className="brillouin-zone-export-controls" aria-label="本地图片导出控制">
        <label>背景 <select value={exportRequest.background} onChange={(event)=>setExportRequest(Object.freeze({...exportRequest,background:event.target.value as BZExportRequest["background"]}))}><option value="light">浅色</option><option value="dark">深色</option><option value="transparent">透明</option></select></label>
        <label>分辨率 <select value={`${exportRequest.width}x${exportRequest.height}`} onChange={(event)=>{const [width,height]=event.target.value.split("x").map(Number);setExportRequest(Object.freeze({...exportRequest,width,height}));}}><option value="1600x1200">1600 × 1200</option><option value="2400x1800">2400 × 1800</option></select></label>
        <label>像素倍率 <select value={exportRequest.pixelRatio} onChange={(event)=>setExportRequest(Object.freeze({...exportRequest,pixelRatio:Number(event.target.value) as 1|2}))}><option value="1">1×</option><option value="2">2×</option></select></label>
        <button type="button" data-testid="brillouin-zone-export-png" disabled={state!=="rendered"||exporting} onClick={()=>void exportPng()}>{exporting?"正在导出…":"导出当前视图"}</button><output data-testid="brillouin-zone-export-status">{exportState}</output>
      </div>
      <dl className="mini-grid brillouin-zone-summary" data-testid="brillouin-zone-summary"><div><dt>顶点</dt><dd>{mapping.scene.vertices.length}</dd></div><div><dt>边</dt><dd>{mapping.scene.edges.length}</dd></div><div><dt>面</dt><dd>{mapping.scene.faces.length}</dd></div><div><dt>三角形</dt><dd>{mapping.scene.faces.reduce((sum,item)=>sum+item.triangleVertexIndices.length/3,0)}</dd></div><div><dt>高对称点</dt><dd>{mapping.scene.points.length}</dd></div><div><dt>路径段</dt><dd>{mapping.scene.segments.length}</dd></div><div><dt>体积</dt><dd>{mapping.scene.volume.toFixed(6)} Å⁻³</dd></div><div><dt>视觉比例</dt><dd>{mapping.scene.visualScale.toFixed(6)}（统一）</dd></div></dl>
      {mapping.warnings.length?<ul className="warning-list">{mapping.warnings.map((warning)=><li key={warning}>{warning}</li>)}</ul>:null}
      <BZInspector details={selected} onClear={()=>onSelection(null)}/>
      <BZTextTables scene={mapping.scene} onSelect={onSelection}/>
      <div className="viewer-artifact-downloads"><button type="button" onClick={()=>downloadBlob(jsonBlob(bundle.zone),"brillouin_zone.json")}>下载布里渊区数据</button><button type="button" onClick={()=>downloadBlob(jsonBlob(bundle.reciprocal),"reciprocal_lattice.json")}>下载倒易晶格</button>{bundle.kpath?<button type="button" onClick={()=>downloadBlob(jsonBlob(bundle.kpath),"kpath.json")}>下载 k 路径</button>:null}<button type="button" onClick={()=>downloadBlob(jsonBlob(bundle.manifest),"brillouin_zone_manifest.json")}>下载数据清单</button>{summary?<button type="button" onClick={()=>downloadBlob(new Blob([summary],{type:"text/markdown"}),"summary.md")}>下载摘要</button>:null}{recipe?<button type="button" onClick={()=>downloadBlob(jsonBlob(recipe),"recipe.json")}>下载复现信息</button>:null}</div>
      <output aria-hidden="true" className="sr-only" data-testid="brillouin-zone-renderer-metrics">{snapshot?JSON.stringify(snapshot.metrics):"metrics pending"}</output>
      <output aria-hidden="true" className="sr-only" data-testid="brillouin-zone-renderer-snapshot">{snapshot?JSON.stringify(snapshot):"snapshot pending"}</output>
    </>:null}
  </section>;
}

function BZInspector({details,onClear}:{details:ReturnType<typeof selectionDetails>|null;onClear:()=>void}) { return <section className="brillouin-zone-inspector" data-testid="brillouin-zone-inspector" aria-label="倒易空间检查器"><div><h4>倒易空间检查器</h4>{details?<button type="button" onClick={onClear}>清除选择</button>:null}</div>{details?<><strong data-testid="brillouin-zone-selection-id">{details.title}</strong><dl className="mini-grid">{details.rows.map(([label,value])=><div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl></>:<p>选择高对称点、面、顶点或路径段。规范化标识会在相机视角变化时保持稳定。</p>}</section>; }
function BZTextTables({scene,onSelect}:{scene:Extract<ReturnType<typeof mapBrillouinZoneArtifacts>,{ok:true}>["scene"];onSelect:(selection:BZSelection)=>void}) { return <div className="brillouin-zone-tables"><div className="compact-table-wrap"><table className="compact-table"><caption>规范化倒易坐标中的高对称点</caption><thead><tr><th>标签</th><th>点标识</th><th>分数坐标</th><th>笛卡尔坐标（Å⁻¹）</th></tr></thead><tbody>{scene.points.map((point)=><tr key={point.id}><td><button type="button" onClick={()=>onSelect({kind:"point",id:point.id})}>{point.displayLabel}</button></td><td><code>{point.id}</code></td><td>{formatVector(point.fractional)}</td><td>{formatVector(point.cartesian)}</td></tr>)}</tbody></table></div><div className="compact-table-wrap"><table className="compact-table"><caption>当前规范化路径变体；不连续处不会推断路径段</caption><thead><tr><th>顺序</th><th>路径段标识</th><th>端点</th><th>长度（Å⁻¹）</th></tr></thead><tbody>{scene.segments.filter((item)=>item.variantId===scene.selectedVariantId).map((segment)=><tr key={segment.id}><td>{segment.orderIndex}</td><td><button type="button" onClick={()=>onSelect({kind:"segment",id:segment.id,variantId:segment.variantId})}>{segment.id}</button></td><td>{segment.startLabelKey} → {segment.endLabelKey}</td><td>{segment.length.toFixed(6)}</td></tr>)}</tbody></table></div></div>; }
function Fallback({code,text,errors=[],action,onAction}:{code:string;text:string;errors?:readonly string[];action?:string;onAction?:()=>void}) { return <div className="viewer-renderer-fallback" data-testid="brillouin-zone-renderer-fallback" role="alert"><strong>{text}</strong><code>{code}</code>{errors.length?<ul>{errors.map((error)=><li key={error}>{error}</li>)}</ul>:null}{action?<button type="button" onClick={onAction}>{action}</button>:null}<p>JSON, summary, recipe, reciprocal matrix, topology counts, high-symmetry points, and path tables remain available outside the graphics surface.</p></div>; }
function selectionDetails(scene:Extract<ReturnType<typeof mapBrillouinZoneArtifacts>,{ok:true}>["scene"],selection:BZSelection) { if(selection.kind==="point"){const item=scene.points.find((value)=>value.id===selection.id);return item?{title:`点 ${item.displayLabel} · ${item.id}`,rows:[["别名",item.aliases.join(", ")||"无"],["分数坐标",formatVector(item.fractional)],["笛卡尔坐标",`${formatVector(item.cartesian)} Å⁻¹`],["来源",scene.provider.name],["约定",scene.provider.pathConvention],["关联路径段",item.incidentSegmentIds.join(", ")||"无"],["时间反演",String(scene.provider.timeReversal)]] as [string,string][]}:null;}if(selection.kind==="face"){const item=scene.faces.find((value)=>value.id===selection.id);return item?{title:`面 ${item.id}`,rows:[["顶点",item.vertexIds.join(", ")],["边",item.edgeIds.join(", ")],["面积",`${item.area.toFixed(6)} Å⁻²`],["质心",formatVector(item.centroid)],["外法向",formatVector(item.outwardNormal)],["生成 hkl",item.generatorHkl.join(", ")],["平面偏移",item.planeOffset.toFixed(6)]] as [string,string][]}:null;}if(selection.kind==="vertex"){const item=scene.vertices.find((value)=>value.id===selection.id);return item?{title:`顶点 ${item.id}`,rows:[["笛卡尔坐标",`${formatVector(item.cartesian)} Å⁻¹`],["分数坐标",formatVector(item.fractional)],["关联面",item.incidentFaceIds.join(", ")]] as [string,string][]}:null;}if(selection.kind==="reciprocal_sample")return{title:`关联样本 ${selection.id}`,rows:[["笛卡尔坐标",`${formatVector(selection.cartesian)} Å⁻¹`],["路径段",selection.segmentId],["来源","已验证的能带—布里渊区关联模型"]] as [string,string][]};const item=scene.segments.find((value)=>value.id===selection.id&&value.variantId===selection.variantId);return item?{title:`路径段 ${item.id}`,rows:[["变体",item.variantId],["端点",`${item.startLabelKey} → ${item.endLabelKey}`],["点标识",`${item.startPointId} → ${item.endPointId}`],["长度",`${item.length.toFixed(6)} Å⁻¹`],["顺序",String(item.orderIndex)],["前后不连续",`${item.discontinuityBefore}/${item.discontinuityAfter}`]] as [string,string][]}:null; }
function formatVector(value:readonly number[]){return `[${value.map((item)=>item.toFixed(6)).join(", ")}]`;}
function jsonBlob(value:unknown){return new Blob([JSON.stringify(value,null,2)+"\n"],{type:"application/json"});}
function safeFilename(value:string){return value.replace(/[^A-Za-z0-9_.-]+/g,"-").replace(/^-+|-+$/g,"").slice(0,160)||"brillouin-zone.png";}
function downloadBlob(blob:Blob,name:string){const url=URL.createObjectURL(blob);const anchor=document.createElement("a");anchor.href=url;anchor.download=safeFilename(name);anchor.click();setTimeout(()=>URL.revokeObjectURL(url),0);}
