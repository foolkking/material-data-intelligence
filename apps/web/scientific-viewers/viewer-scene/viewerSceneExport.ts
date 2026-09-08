import type { ViewerMeasurementResult } from "./viewerSceneMeasurements";
import type { PeriodicSiteRef, ValidatedRenderScene, ViewerRendererSnapshot } from "./viewerSceneRendererTypes";
import type { CameraPreset, ViewerClipState } from "./viewerSceneViewState";

export const VIEWER_EXPORT_LIMITS = Object.freeze({ minWidth:256, minHeight:256, maxWidth:4096, maxHeight:4096, maxPixels:16_777_216, maxPixelRatio:2, maxEstimatedBytes:67_108_864, maxConcurrent:1 });
export const VIEWER_EXPORT_PRESETS = Object.freeze({ web:[1200,900], presentation:[1600,900], square:[1600,1600], publication:[2400,1800] } as const);
export type ViewerExportFormat = "png" | "json" | "markdown";
export type ViewerExportBackground = "transparent" | "light" | "dark";
export type ViewerExportRequest = Readonly<{ format:ViewerExportFormat; width:number; height:number; pixelRatio:1|2; background:ViewerExportBackground; includeCell:boolean; includeAxes:boolean; includeBonds:boolean; includeMeasurements:boolean; includeInspectorSummary:boolean }>;
export type ViewerExportMeasurement = Readonly<{ result:ViewerMeasurementResult; refs:readonly PeriodicSiteRef[] }>;

export const DEFAULT_VIEWER_EXPORT_REQUEST:ViewerExportRequest=Object.freeze({format:"png",width:1600,height:1200,pixelRatio:1,background:"light",includeCell:true,includeAxes:true,includeBonds:true,includeMeasurements:true,includeInspectorSummary:false});

export function validateViewerExportRequest(value:unknown):ViewerExportRequest{
  if(!record(value))throw new Error("VIEWER_EXPORT_REQUEST_INVALID");
  const keys=Object.keys(value).sort();const allowed=["background","format","height","includeAxes","includeBonds","includeCell","includeInspectorSummary","includeMeasurements","pixelRatio","width"].sort();
  if(keys.join()!==allowed.join()||!["png","json","markdown"].includes(String(value.format))||!["transparent","light","dark"].includes(String(value.background))||![1,2].includes(Number(value.pixelRatio)))throw new Error("VIEWER_EXPORT_REQUEST_INVALID");
  for(const key of ["includeCell","includeAxes","includeBonds","includeMeasurements","includeInspectorSummary"] as const)if(typeof value[key]!=="boolean")throw new Error("VIEWER_EXPORT_REQUEST_INVALID");
  assertViewerExportDimensions(Number(value.width),Number(value.height),Number(value.pixelRatio));
  return Object.freeze({format:value.format as ViewerExportFormat,width:Number(value.width),height:Number(value.height),pixelRatio:Number(value.pixelRatio) as 1|2,background:value.background as ViewerExportBackground,includeCell:value.includeCell as boolean,includeAxes:value.includeAxes as boolean,includeBonds:value.includeBonds as boolean,includeMeasurements:value.includeMeasurements as boolean,includeInspectorSummary:value.includeInspectorSummary as boolean});
}

export function sanitizeViewerFilename(value:string,suffix="structure-viewer.png"){
  const safeSuffix=/^(?:structure-viewer\.png|viewer-export-state\.json|viewer-export-summary\.md|viewer-export-manifest\.json)$/.test(suffix)?suffix:"structure-viewer.png";
  const stem=value.normalize("NFKD").replace(/[\u0000-\u001f\u007f\\/]+/g,"-").replace(/[^a-zA-Z0-9._-]+/g,"-").replace(/^[._-]+|[._-]+$/g,"").slice(0,80)||"structure";
  return `${stem}-${safeSuffix}`;
}

export function assertViewerExportDimensions(width:number,height:number,pixelRatio=1){
  const effectiveWidth=width*pixelRatio,effectiveHeight=height*pixelRatio,pixels=effectiveWidth*effectiveHeight;
  if(!Number.isInteger(width)||!Number.isInteger(height)||![1,2].includes(pixelRatio)||width<VIEWER_EXPORT_LIMITS.minWidth||height<VIEWER_EXPORT_LIMITS.minHeight||effectiveWidth>VIEWER_EXPORT_LIMITS.maxWidth||effectiveHeight>VIEWER_EXPORT_LIMITS.maxHeight)throw new Error("VIEWER_EXPORT_INVALID_SIZE");
  if(!Number.isSafeInteger(pixels)||pixels>VIEWER_EXPORT_LIMITS.maxPixels||pixels*4>VIEWER_EXPORT_LIMITS.maxEstimatedBytes)throw new Error("VIEWER_EXPORT_PIXEL_BUDGET_EXCEEDED");
}

export function buildViewerExportState(args:Readonly<{scene:ValidatedRenderScene;snapshot:ViewerRendererSnapshot;request:ViewerExportRequest;clip:ViewerClipState;cameraPreset:CameraPreset;showCell:boolean;showSupercellBoundary:boolean;showAxes:boolean;showBonds:boolean;measurements:readonly ViewerExportMeasurement[];inspectorSummary?:Readonly<{siteIndex:number;imageOffset:readonly[number,number,number];species:string;displayedCartesian:readonly[number,number,number]}>}>){
  const request=validateViewerExportRequest(args.request);const measurements=Object.freeze(args.measurements.slice(-20).map((item)=>Object.freeze({kind:item.result.kind,value:round(item.result.value),unit:item.result.unit,site_indices:Object.freeze([...item.result.siteIndices]),periodic_refs:Object.freeze(item.refs.map((ref)=>Object.freeze({site_index:ref.siteIndex,image_offset:Object.freeze([...ref.imageOffset])})))})));
  const inspector=request.includeInspectorSummary&&args.inspectorSummary?Object.freeze({site_index:args.inspectorSummary.siteIndex,image_offset:Object.freeze([...args.inspectorSummary.imageOffset]),species:plain(args.inspectorSummary.species),displayed_cartesian:Object.freeze(args.inspectorSummary.displayedCartesian.map(round))}):null;
  return Object.freeze({schema_version:"phase10f26.viewer_export_state.v1" as const,scene:Object.freeze({schema_version:args.scene.schemaVersion,resource_id:args.scene.source.resourceId,formula:args.scene.formula}),viewer_state:Object.freeze({supercell_expansion:Object.freeze([...args.scene.supercellRepeat]),camera_preset:args.cameraPreset,camera_position:args.snapshot.cameraPosition,camera_target:args.snapshot.cameraTarget,camera_up:args.snapshot.cameraUp,camera_zoom:args.snapshot.cameraZoom,clipping:args.clip,show_unit_cell:args.showCell,show_supercell_boundary:args.showSupercellBoundary,show_axes:args.showAxes,show_bonds:args.showBonds}),measurements,inspector_summary:inspector,export_request:request,deterministic:true,policy:Object.freeze({screenshot_is_scientific_data:false,structure_mutated:false,topology_mutated:false,periodic_identity:"site_index@[image_offset]"}),security:Object.freeze({contains_javascript:false,contains_html:false,external_urls:Object.freeze([])})});
}

export function buildViewerExportMarkdown(scene:ValidatedRenderScene,state:ReturnType<typeof buildViewerExportState>){
  const cross=scene.bonds.filter((bond)=>bond.fromRef.imageOffset.some((value,index)=>value!==bond.toRef.imageOffset[index])).length;const self=scene.bonds.filter((bond)=>bond.fromSiteIndex===bond.toSiteIndex&&bond.fromRef.imageOffset.some((value,index)=>value!==bond.toRef.imageOffset[index])).length;
  const inspector=state.inspector_summary?`- Selected site: ${state.inspector_summary.site_index}@[${state.inspector_summary.image_offset.join(",")}]; ${state.inspector_summary.species}; displayed Cartesian [${state.inspector_summary.displayed_cartesian.join(", ")}] angstrom`:"- Selected site: not included";
  const lines=["# Scientific Structure Viewer Export","",`- Formula: ${plain(scene.formula)}`,`- Scene schema: ${scene.schemaVersion}`,`- Lattice vectors (angstrom): ${scene.lattice.matrix.map((row)=>`[${row.map(round).join(", ")}]`).join("; ")}`,`- Canonical sites: ${scene.atoms.filter((atom)=>atom.ref.imageOffset.every((value)=>value===0)).length}`,`- Canonical bonds: ${scene.bonds.length}`,`- Cross-boundary bonds: ${cross}`,`- Self-periodic bonds: ${self}`,`- Supercell expansion: ${scene.supercellRepeat.join(" x ")}`,`- Displayed atoms: ${scene.atoms.length}`,`- Displayed bonds: ${scene.bonds.length}`,`- Camera: ${state.viewer_state.camera_preset}; position [${state.viewer_state.camera_position.join(", ")}]; target [${state.viewer_state.camera_target.join(", ")}]`,`- Clipping: ${state.viewer_state.clipping.enabled?state.viewer_state.clipping.planes.filter((plane)=>plane.enabled).map((plane)=>`${plane.axis} <= ${round(plane.position)} angstrom`).join("; ")||"enabled with no planes":"disabled"}`,`- Export: ${state.export_request.width} x ${state.export_request.height}; pixel ratio ${state.export_request.pixelRatio}; ${state.export_request.background} background`,inspector,"","## Measurements",...(state.measurements.length?state.measurements.map((item)=>`- ${item.kind}: ${item.value} ${item.unit}; ${item.periodic_refs.map((ref)=>`${ref.site_index}@[${ref.image_offset.join(",")}]`).join(" -> ")}`):["- None"]),"","## Provenance and limitations",`- Source resource identity: ${plain(scene.source.resourceId)}`,"- Periodic bonds are emitted scene topology and are not authoritative chemistry or bond order.","- The PNG is a rendered view, not a structure data source.","- No structure or topology mutation occurred.","- No JavaScript, HTML, external URL, remote asset, or renderer bundle is included."];
  return `${lines.join("\n")}\n`;
}

export async function buildViewerExportManifest(artifacts:readonly Readonly<{name:string;mediaType:"image/png"|"application/json"|"text/markdown";blob:Blob}>[]){
  const expected=["viewer.png","viewer_export_state.json","viewer_export_summary.md"];
  if(artifacts.length!==3||artifacts.map((item)=>item.name).join()!==expected.join())throw new Error("VIEWER_EXPORT_MANIFEST_INVALID");
  return Object.freeze({schema_version:"phase10f26.viewer_export_manifest.v1" as const,artifacts:Object.freeze(await Promise.all(artifacts.map(async(item)=>Object.freeze({name:item.name,media_type:item.mediaType,size_bytes:item.blob.size,sha256:await sha256Blob(item.blob)})))),renderer_included:false,javascript_included:false,external_assets:Object.freeze([]),deterministic_order:true});
}

export async function sha256Blob(blob: Blob) {
  const bytes = typeof blob.arrayBuffer === "function"
    ? await blob.arrayBuffer()
    : await readBlobWithFileReader(blob);
  const digestInput = new Uint8Array(bytes.byteLength);
  digestInput.set(new Uint8Array(bytes));
  const hash = await crypto.subtle.digest("SHA-256", digestInput);
  return [...new Uint8Array(hash)].map((value) => value.toString(16).padStart(2, "0")).join("");
}
export function downloadLocalBlob(blob:Blob,filename:string){const url=URL.createObjectURL(blob);const anchor=document.createElement("a");anchor.href=url;anchor.download=filename;anchor.rel="noopener";anchor.click();queueMicrotask(()=>URL.revokeObjectURL(url));}
export function jsonBlob(payload:unknown){return new Blob([`${JSON.stringify(payload,null,2)}\n`],{type:"application/json"});}
export function markdownBlob(value:string){return new Blob([value],{type:"text/markdown"});}
function record(value:unknown):value is Record<string,unknown>{return Boolean(value)&&typeof value==="object"&&!Array.isArray(value);}
function round(value:number){if(!Number.isFinite(value))throw new Error("VIEWER_EXPORT_NON_FINITE");return Number(value.toFixed(6));}
function plain(value:string){return value.replace(/[\u0000-\u001f\u007f<>]/g," ").replace(/\s+/g," ").trim().slice(0,160)||"unknown";}

function readBlobWithFileReader(blob: Blob) {
  return new Promise<ArrayBuffer>((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error("VIEWER_EXPORT_HASH_READ_FAILED"));
    reader.onload = () => reader.result instanceof ArrayBuffer
      ? resolve(reader.result)
      : reject(new Error("VIEWER_EXPORT_HASH_READ_FAILED"));
    reader.readAsArrayBuffer(blob);
  });
}
