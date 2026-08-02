"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { supportsManagedWebGL } from "../viewer-scene/viewerWebglCapability";
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
  const [exportState,setExportState]=useState("No PNG prepared.");
  const [announcement,setAnnouncement]=useState("Brillouin zone renderer ready.");
  const selectionRef=useRef(selection);selectionRef.current=selection;

  const refreshSnapshot=useCallback(()=>{const engine=engineRef.current;if(engine)setSnapshot(engine.snapshot());},[]);
  const onSelection=useCallback((next:BZSelection|null)=>{setSelection(next);setAnnouncement(next?`Selected ${next.kind} ${next.id}.`:"Selection cleared.");selectionListener?.(next);},[selectionListener]);
  const onViewChange=useCallback(()=>{setExportState("View changed; export again for a current PNG.");queueMicrotask(refreshSnapshot);},[refreshSnapshot]);

  useEffect(()=>{
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
      engineRef.current=engine;engine.setSelection(selectionRef.current);setSnapshot(engine.snapshot());setState("rendered");setAnnouncement(`Rendered ${mapping.scene.faces.length} faces, ${mapping.scene.edges.length} edges, and ${mapping.scene.points.length} high-symmetry points.`);
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
  const exportPng=async()=>{const engine=engineRef.current;if(!engine)return;try{setExportState("Preparing deterministic PNG...");engine.setCameraPreset("isometric");setPreset("isometric");const blob=await engine.exportPng(exportRequest);downloadBlob(blob,safeFilename(`${mapping.ok?mapping.scene.packageId:"brillouin-zone"}-brillouin-zone.png`));setExportState(`PNG exported locally (${blob.size} bytes).`);refreshSnapshot();}catch{setExportState("PNG export failed within the bounded local renderer.");}};
  const selected=mapping.ok&&selection?selectionDetails(mapping.scene,selection):null;
  const labels=mapping.ok&&visibility.labels&&snapshot?snapshot.pointScreenPositions.slice(0,BZ_RENDERER_CAPS.visibleLabels):[];
  const onKeyDown=(event:React.KeyboardEvent<HTMLElement>)=>{const actions:Record<string,Parameters<BZRendererEngine["keyboardCamera"]>[0]>={ArrowLeft:"rotate_left",ArrowRight:"rotate_right",ArrowUp:"rotate_up",ArrowDown:"rotate_down","+":"zoom_in","=":"zoom_in","-":"zoom_out"};if(actions[event.key]){event.preventDefault();engineRef.current?.keyboardCamera(actions[event.key]);refreshSnapshot();}if(event.key.toLowerCase()==="r"){event.preventDefault();reset();}};

  return <section className="brillouin-zone-surface" data-testid="brillouin-zone-renderer-surface" aria-label="First Brillouin zone viewer" tabIndex={0} onKeyDown={onKeyDown}>
    <output className="sr-only" aria-live="polite" data-testid="brillouin-zone-live-region">{announcement}</output>
    <div className="brillouin-zone-heading"><div><h3>3D Brillouin Zone</h3><p>Validated reciprocal Cartesian geometry in Å⁻¹ · physics 2π convention</p></div><code data-testid="brillouin-zone-renderer-state">{state}</code></div>
    {!mapping.ok?<Fallback code={mapping.code} text="The canonical reciprocal-space artifacts failed validation before WebGL initialization." errors={mapping.errors}/>:null}
    {mapping.ok&&state==="unsupported"?<Fallback code="BZ_RENDERER_UNSUPPORTED" text="WebGL is unavailable. Scientific tables and JSON remain available."/>:null}
    {mapping.ok&&state==="over_cap"?<Fallback code="BZ_RENDERER_RESOURCE_LIMIT" text="The validated scene exceeds the application-owned graphics budget. No partial geometry was rendered."/>:null}
    {mapping.ok&&state==="context_lost"?<Fallback code="BZ_RENDERER_CONTEXT_LOST" text="The graphics context was lost and stale GPU resources were released." action="Reinitialize renderer" onAction={()=>setAttempt((value)=>value+1)}/>:null}
    {mapping.ok&&state==="renderer_failed"?<Fallback code="BZ_RENDERER_INITIALIZATION_FAILED" text="The local renderer module could not initialize. JSON and text views remain available." action="Retry renderer" onAction={()=>setAttempt((value)=>value+1)}/>:null}
    {mapping.ok&&(state==="ready"||state==="initializing")?<div className="viewer-renderer-loading" role="status">Loading the local Three.js renderer...</div>:null}
    {mapping.ok?<>
      <div className="brillouin-zone-controls" aria-label="Brillouin zone display controls">
        {(["faces","edges","vertices","axes","points","labels","path"] as const).map((key)=><button key={key} type="button" aria-pressed={visibility[key]} className={visibility[key]?"active":"secondary"} onClick={()=>updateVisibility(key)}>{key}</button>)}
        <label>Face opacity <input data-testid="brillouin-zone-opacity" type="range" min="0.08" max="0.65" step="0.01" value={opacity} aria-valuetext={`${Math.round(opacity*100)} percent`} onChange={(event)=>{const value=Number(event.target.value);setOpacity(value);engineRef.current?.setOpacity(value);refreshSnapshot();}}/></label>
        <label>Projection <select data-testid="brillouin-zone-projection" value={projection} onChange={(event)=>updateProjection(event.target.value as BZProjection)}><option value="perspective">Perspective</option><option value="orthographic">Orthographic</option></select></label>
        <label>Camera <select data-testid="brillouin-zone-camera-preset" value={preset} onChange={(event)=>updatePreset(event.target.value as BZCameraPreset)}><option value="isometric">Isometric</option><option value="b1">+b1</option><option value="b2">+b2</option><option value="b3">+b3</option></select></label>
        {mapping.scene.variants.length?<label>Path variant <select data-testid="brillouin-zone-path-variant" value={variantId??""} onChange={(event)=>updateVariant(event.target.value)}>{mapping.scene.variants.map((item)=><option key={item.id} value={item.id}>{item.description}</option>)}</select></label>:null}
        <button type="button" onClick={()=>engineRef.current?.fit()}>Fit</button><button type="button" data-testid="brillouin-zone-reset" onClick={reset}>Reset</button>
      </div>
      <div className="brillouin-zone-stage">
        <div className="viewer-renderer-canvas-host" ref={containerRef} data-testid="brillouin-zone-canvas-host"/>
        {labels.map((position)=>{const point=mapping.scene.points.find((item)=>item.id===position.id);return point?<button type="button" className="brillouin-zone-label" key={point.id} style={{left:position.x,top:position.y}} onClick={()=>onSelection({kind:"point",id:point.id})}>{point.displayLabel}</button>:null;})}
      </div>
      <div className="brillouin-zone-export-controls" aria-label="Local PNG export controls">
        <label>Background <select value={exportRequest.background} onChange={(event)=>setExportRequest(Object.freeze({...exportRequest,background:event.target.value as BZExportRequest["background"]}))}><option value="light">Light</option><option value="dark">Dark</option><option value="transparent">Transparent</option></select></label>
        <label>Resolution <select value={`${exportRequest.width}x${exportRequest.height}`} onChange={(event)=>{const [width,height]=event.target.value.split("x").map(Number);setExportRequest(Object.freeze({...exportRequest,width,height}));}}><option value="1600x1200">1600 × 1200</option><option value="2400x1800">2400 × 1800</option></select></label>
        <label>Pixel ratio <select value={exportRequest.pixelRatio} onChange={(event)=>setExportRequest(Object.freeze({...exportRequest,pixelRatio:Number(event.target.value) as 1|2}))}><option value="1">1×</option><option value="2">2×</option></select></label>
        <button type="button" data-testid="brillouin-zone-export-png" disabled={state!=="rendered"} onClick={()=>void exportPng()}>Export fixed-camera PNG</button><output data-testid="brillouin-zone-export-status">{exportState}</output>
      </div>
      <dl className="mini-grid brillouin-zone-summary" data-testid="brillouin-zone-summary"><div><dt>vertices</dt><dd>{mapping.scene.vertices.length}</dd></div><div><dt>edges</dt><dd>{mapping.scene.edges.length}</dd></div><div><dt>faces</dt><dd>{mapping.scene.faces.length}</dd></div><div><dt>triangles</dt><dd>{mapping.scene.faces.reduce((sum,item)=>sum+item.triangleVertexIndices.length/3,0)}</dd></div><div><dt>points</dt><dd>{mapping.scene.points.length}</dd></div><div><dt>segments</dt><dd>{mapping.scene.segments.length}</dd></div><div><dt>volume</dt><dd>{mapping.scene.volume.toFixed(6)} Å⁻³</dd></div><div><dt>visual scale</dt><dd>{mapping.scene.visualScale.toFixed(6)} uniform</dd></div></dl>
      {mapping.warnings.length?<ul className="warning-list">{mapping.warnings.map((warning)=><li key={warning}>{warning}</li>)}</ul>:null}
      <BZInspector details={selected} onClear={()=>onSelection(null)}/>
      <BZTextTables scene={mapping.scene} onSelect={onSelection}/>
      <div className="viewer-artifact-downloads"><button type="button" onClick={()=>downloadBlob(jsonBlob(bundle.zone),"brillouin_zone.json")}>Download BZ JSON</button><button type="button" onClick={()=>downloadBlob(jsonBlob(bundle.reciprocal),"reciprocal_lattice.json")}>Download reciprocal lattice</button>{bundle.kpath?<button type="button" onClick={()=>downloadBlob(jsonBlob(bundle.kpath),"kpath.json")}>Download k-path</button>:null}<button type="button" onClick={()=>downloadBlob(jsonBlob(bundle.manifest),"brillouin_zone_manifest.json")}>Download manifest</button>{summary?<button type="button" onClick={()=>downloadBlob(new Blob([summary],{type:"text/markdown"}),"summary.md")}>Download summary</button>:null}{recipe?<button type="button" onClick={()=>downloadBlob(jsonBlob(recipe),"recipe.json")}>Download recipe</button>:null}</div>
      <output className="sr-only" data-testid="brillouin-zone-renderer-metrics">{snapshot?JSON.stringify(snapshot.metrics):"metrics pending"}</output>
      <output className="sr-only" data-testid="brillouin-zone-renderer-snapshot">{snapshot?JSON.stringify(snapshot):"snapshot pending"}</output>
    </>:null}
  </section>;
}

function BZInspector({details,onClear}:{details:ReturnType<typeof selectionDetails>|null;onClear:()=>void}) { return <section className="brillouin-zone-inspector" data-testid="brillouin-zone-inspector" aria-label="Reciprocal-space inspector"><div><h4>Reciprocal-space inspector</h4>{details?<button type="button" onClick={onClear}>Clear selection</button>:null}</div>{details?<><strong data-testid="brillouin-zone-selection-id">{details.title}</strong><dl className="mini-grid">{details.rows.map(([label,value])=><div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl></>:<p>Select a high-symmetry point, face, vertex, or path segment. Canonical IDs remain stable across camera changes.</p>}</section>; }
function BZTextTables({scene,onSelect}:{scene:Extract<ReturnType<typeof mapBrillouinZoneArtifacts>,{ok:true}>["scene"];onSelect:(selection:BZSelection)=>void}) { return <div className="brillouin-zone-tables"><div className="compact-table-wrap"><table className="compact-table"><caption>High-symmetry points in canonical reciprocal coordinates</caption><thead><tr><th>Label</th><th>Point ID</th><th>Fractional</th><th>Cartesian Å⁻¹</th></tr></thead><tbody>{scene.points.map((point)=><tr key={point.id}><td><button type="button" onClick={()=>onSelect({kind:"point",id:point.id})}>{point.displayLabel}</button></td><td><code>{point.id}</code></td><td>{formatVector(point.fractional)}</td><td>{formatVector(point.cartesian)}</td></tr>)}</tbody></table></div><div className="compact-table-wrap"><table className="compact-table"><caption>Selected canonical path variant; discontinuities are not rendered as inferred segments</caption><thead><tr><th>Order</th><th>Segment ID</th><th>Endpoints</th><th>Length Å⁻¹</th></tr></thead><tbody>{scene.segments.filter((item)=>item.variantId===scene.selectedVariantId).map((segment)=><tr key={segment.id}><td>{segment.orderIndex}</td><td><button type="button" onClick={()=>onSelect({kind:"segment",id:segment.id,variantId:segment.variantId})}>{segment.id}</button></td><td>{segment.startLabelKey} → {segment.endLabelKey}</td><td>{segment.length.toFixed(6)}</td></tr>)}</tbody></table></div></div>; }
function Fallback({code,text,errors=[],action,onAction}:{code:string;text:string;errors?:readonly string[];action?:string;onAction?:()=>void}) { return <div className="viewer-renderer-fallback" data-testid="brillouin-zone-renderer-fallback" role="alert"><strong>{text}</strong><code>{code}</code>{errors.length?<ul>{errors.map((error)=><li key={error}>{error}</li>)}</ul>:null}{action?<button type="button" onClick={onAction}>{action}</button>:null}<p>JSON, summary, recipe, reciprocal matrix, topology counts, high-symmetry points, and path tables remain available outside the graphics surface.</p></div>; }
function selectionDetails(scene:Extract<ReturnType<typeof mapBrillouinZoneArtifacts>,{ok:true}>["scene"],selection:BZSelection) { if(selection.kind==="point"){const item=scene.points.find((value)=>value.id===selection.id);return item?{title:`Point ${item.displayLabel} · ${item.id}`,rows:[["aliases",item.aliases.join(", ")||"none"],["fractional",formatVector(item.fractional)],["Cartesian",`${formatVector(item.cartesian)} Å⁻¹`],["provider",scene.provider.name],["convention",scene.provider.pathConvention],["incident segments",item.incidentSegmentIds.join(", ")||"none"],["time reversal",String(scene.provider.timeReversal)]] as [string,string][]}:null;}if(selection.kind==="face"){const item=scene.faces.find((value)=>value.id===selection.id);return item?{title:`Face ${item.id}`,rows:[["vertices",item.vertexIds.join(", ")],["edges",item.edgeIds.join(", ")],["area",`${item.area.toFixed(6)} Å⁻²`],["centroid",formatVector(item.centroid)],["outward normal",formatVector(item.outwardNormal)],["generator hkl",item.generatorHkl.join(", ")],["plane offset",item.planeOffset.toFixed(6)]] as [string,string][]}:null;}if(selection.kind==="vertex"){const item=scene.vertices.find((value)=>value.id===selection.id);return item?{title:`Vertex ${item.id}`,rows:[["Cartesian",`${formatVector(item.cartesian)} Å⁻¹`],["fractional",formatVector(item.fractional)],["incident faces",item.incidentFaceIds.join(", ")]] as [string,string][]}:null;}if(selection.kind==="reciprocal_sample")return{title:`Linked sample ${selection.id}`,rows:[["Cartesian",`${formatVector(selection.cartesian)} Å⁻¹`],["path segment",selection.segmentId],["source","validated Band-BZ link model"]] as [string,string][]};const item=scene.segments.find((value)=>value.id===selection.id&&value.variantId===selection.variantId);return item?{title:`Segment ${item.id}`,rows:[["variant",item.variantId],["endpoints",`${item.startLabelKey} → ${item.endLabelKey}`],["point IDs",`${item.startPointId} → ${item.endPointId}`],["length",`${item.length.toFixed(6)} Å⁻¹`],["order",String(item.orderIndex)],["break before/after",`${item.discontinuityBefore}/${item.discontinuityAfter}`]] as [string,string][]}:null; }
function formatVector(value:readonly number[]){return `[${value.map((item)=>item.toFixed(6)).join(", ")}]`;}
function jsonBlob(value:unknown){return new Blob([JSON.stringify(value,null,2)+"\n"],{type:"application/json"});}
function safeFilename(value:string){return value.replace(/[^A-Za-z0-9_.-]+/g,"-").replace(/^-+|-+$/g,"").slice(0,160)||"brillouin-zone.png";}
function downloadBlob(blob:Blob,name:string){const url=URL.createObjectURL(blob);const anchor=document.createElement("a");anchor.href=url;anchor.download=safeFilename(name);anchor.click();setTimeout(()=>URL.revokeObjectURL(url),0);}
