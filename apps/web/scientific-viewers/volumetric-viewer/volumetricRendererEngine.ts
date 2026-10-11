import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

import { cloneScientificExportCamera, copyScientificCameraView, createAtomSphereGeometry, fitScientificCamera, resizeScientificCamera, trackInitialCameraFit } from "../viewer-scene/scientificCamera";
import { captureScientificCanvas, createScientificPngExporter } from "../viewer-scene/scientificPngExport";
import { bindScientificPointerPick } from "../viewer-scene/scientificPointerPick";
import { displayedOverlayBonds, volumetricRenderBounds } from "./volumetricRenderGeometry";
import { captureOrbitControlsDisposer } from "../viewer-scene/orbitControlsLifecycle";
import type { IsosurfaceMesh, ValidatedVolumetricGrid, VolumeVector3, VolumetricRendererEngine, VolumetricRendererSnapshot, VolumetricStructureOverlay, VolumetricSurfacePick } from "./volumetricViewerTypes";
import { VolumetricViewerError } from "./volumetricViewerTypes";

export async function createVolumetricRendererEngine(args: Readonly<{
  container: HTMLElement;
  grid: ValidatedVolumetricGrid;
  fieldId: string;
  meshes: readonly IsosurfaceMesh[];
  overlay: VolumetricStructureOverlay | null;
  onSurfacePick?: (pick: VolumetricSurfacePick | null) => void;
  onAtomPick?: (siteIndex: number | null) => void;
  onContextLost: () => void;
}>): Promise<VolumetricRendererEngine> {
  const {container,grid,fieldId,meshes,overlay,onSurfacePick,onAtomPick,onContextLost}=args;
  if(typeof document==="undefined"||typeof window==="undefined")throw new VolumetricViewerError("VOLUME_VIEWER_WEBGL_UNSUPPORTED","Graphics are unavailable outside a browser.");
  let width=Math.max(1,container.clientWidth||720),height=Math.max(1,container.clientHeight||480);
  let renderer:THREE.WebGLRenderer;
  try{renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true,powerPreference:"high-performance"});}catch{throw new VolumetricViewerError("VOLUME_VIEWER_WEBGL_UNSUPPORTED","The browser could not initialize WebGL.");}
  renderer.setPixelRatio(Math.min(Math.max(window.devicePixelRatio||1,1),2));renderer.setSize(width,height,false);renderer.setClearColor(0xf3f6f7,1);renderer.localClippingEnabled=true;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.domElement.dataset.testid="volumetric-renderer-canvas";renderer.domElement.setAttribute("role","img");renderer.domElement.setAttribute("aria-label","交互式体数据等值面");renderer.domElement.tabIndex=-1;container.append(renderer.domElement);
  const scene=new THREE.Scene();const root=new THREE.Group();root.name="validated-volumetric-scene";scene.add(root);let projection:"perspective"|"orthographic"="perspective";const sphere=volumetricRenderBounds(grid,overlay,meshes);const direction=new THREE.Vector3(1.15,.9,.78);let camera:THREE.PerspectiveCamera|THREE.OrthographicCamera=new THREE.PerspectiveCamera(42,width/height);camera.up.set(0,0,1);fitScientificCamera(camera,sphere,width/height,direction);const controls=new OrbitControls(camera,renderer.domElement);const disposeControls=captureOrbitControlsDisposer(controls);controls.target.copy(sphere.center);controls.enableDamping=false;controls.enablePan=true;renderer.domElement.style.touchAction="pan-y";
  const surfaceMaterials:THREE.MeshStandardMaterial[]=[];const surfaceMeshes:THREE.Mesh[]=[];const colors=[0xe85d75,0x2f80ed,0x7b61ff,0x0b8f8f];
  for(const [index,mesh] of meshes.entries()){const geometry=new THREE.BufferGeometry();geometry.setAttribute("position",new THREE.BufferAttribute(mesh.positions,3));geometry.setAttribute("normal",new THREE.BufferAttribute(mesh.normals,3));geometry.setIndex(new THREE.BufferAttribute(mesh.indices,1));geometry.computeBoundingBox();geometry.computeBoundingSphere();const material=new THREE.MeshStandardMaterial({color:colors[index%colors.length],transparent:true,opacity:.62,side:THREE.DoubleSide,roughness:.38,metalness:.03,depthWrite:false});material.clippingPlanes=[];surfaceMaterials.push(material);const surface=new THREE.Mesh(geometry,material);surface.name=`isosurface-${mesh.layerId}`;surface.userData={fieldId,layerId:mesh.layerId,isovalue:mesh.isovalue,meshHash:mesh.meshHash};surfaceMeshes.push(surface);root.add(surface);}
  const overlayObjects:THREE.Object3D[]=[];let atomMeshes:THREE.InstancedMesh[]=[];let atomGeometry:THREE.SphereGeometry|null=null;const atomMaterials=new Map<string,THREE.MeshStandardMaterial>();
  if(overlay){atomGeometry=createAtomSphereGeometry(overlay.atoms.length);const groups=new Map<string,typeof overlay.atoms>();for(const atom of overlay.atoms)groups.set(atom.color,[...(groups.get(atom.color)||[]),atom]);for(const [color,atoms] of groups){const material=new THREE.MeshStandardMaterial({color,roughness:.4,metalness:.02});atomMaterials.set(color,material);const mesh=new THREE.InstancedMesh(atomGeometry,material,atoms.length);mesh.name=`volumetric-atoms-${color}`;const matrix=new THREE.Matrix4();for(const [index,atom] of atoms.entries()){matrix.compose(new THREE.Vector3(...atom.position),new THREE.Quaternion(),new THREE.Vector3(atom.radius,atom.radius,atom.radius));mesh.setMatrixAt(index,matrix);}mesh.instanceMatrix.needsUpdate=true;mesh.userData={siteIndices:atoms.map((atom)=>atom.siteIndex)};atomMeshes.push(mesh);root.add(mesh);overlayObjects.push(mesh);}}
  const displayedBonds=overlay?displayedOverlayBonds(overlay):[];
  let bondGeometry:THREE.BufferGeometry|null=null;let bondMaterial:THREE.LineBasicMaterial|null=null;let bondLines:THREE.LineSegments|null=null;if(displayedBonds.length){bondGeometry=lineGeometry(displayedBonds.flatMap((bond)=>[bond.start,bond.end]));bondMaterial=new THREE.LineBasicMaterial({color:0x536878,transparent:true,opacity:.7});bondLines=new THREE.LineSegments(bondGeometry,bondMaterial);bondLines.name="volumetric-structure-bonds";root.add(bondLines);overlayObjects.push(bondLines);}
  let cellGeometry:THREE.BufferGeometry|null=null;let cellMaterial:THREE.LineBasicMaterial|null=null;let cellLines:THREE.LineSegments|null=null;if(grid.periodic){const vectors:readonly[VolumeVector3,VolumeVector3,VolumeVector3]=overlay?.lattice??[scaleRow(grid.stepMatrix[0],grid.shape[0]),scaleRow(grid.stepMatrix[1],grid.shape[1]),scaleRow(grid.stepMatrix[2],grid.shape[2])];cellGeometry=lineGeometry(cellEdges(grid.origin,vectors));cellMaterial=new THREE.LineBasicMaterial({color:0x1f6f8b,transparent:true,opacity:.9});cellLines=new THREE.LineSegments(cellGeometry,cellMaterial);cellLines.name="volumetric-unit-cell";root.add(cellLines);}
  let profilePlaneGeometry:THREE.BufferGeometry|null=null;const profilePlaneMaterial=new THREE.MeshBasicMaterial({color:0x14839c,transparent:true,opacity:.18,side:THREE.DoubleSide,depthWrite:false});let profilePlane:THREE.Mesh|null=null;
  const ambient=new THREE.AmbientLight(0xffffff,1.35),key=new THREE.DirectionalLight(0xffffff,2.2);key.position.copy(camera.position);scene.add(ambient,key);let surfaceVisible=true,structureVisible=true,clippingEnabled=false,clipAxis:0|1|2=2,clipOffset=0,selected:VolumetricSurfacePick|null=null,disposed=false,contextLost=false;let clippingPlanes:THREE.Plane[]=[];
  const snapshot=():VolumetricRendererSnapshot=>Object.freeze({state:contextLost?"context_lost":disposed?"disposed":"rendered",canvasCount:container.querySelectorAll("canvas").length,contextCount:disposed?0:1,vertexCount:meshes.reduce((sum,mesh)=>sum+mesh.vertexCount,0),triangleCount:meshes.reduce((sum,mesh)=>sum+mesh.triangleCount,0),layerCount:meshes.length,drawCalls:renderer.info.render.calls,geometries:renderer.info.memory.geometries,materials:surfaceMaterials.length+atomMaterials.size+(bondMaterial?1:0)+(cellMaterial?1:0)+(profilePlane?1:0),cameraProjection:projection,clippingEnabled,surfaceVisible,structureVisible});
  const render=()=>{if(disposed||contextLost)return;renderer.render(scene,camera);publish();};
  controls.addEventListener("change",render);
  const publish=()=>{(window as unknown as {__mdiVolumetricRendererEvidence?:VolumetricRendererSnapshot}).__mdiVolumetricRendererEvidence=snapshot();};
  const applyClip=()=>{clippingPlanes=clippingEnabled?[new THREE.Plane(new THREE.Vector3(...axisVector(clipAxis)),clipOffset)]:[];for(const material of surfaceMaterials)material.clippingPlanes=clippingPlanes;};
  const applyFrame = (bounds: THREE.Sphere) => {
    fitScientificCamera(camera, bounds, width / height, direction);
    controls.target.copy(bounds.center);
    controls.update();
    render();
  };
  const resetCamera = () => applyFrame(sphere);
  const initialFit = trackInitialCameraFit(controls, resetCamera);
  const setProjection = (next: "perspective" | "orthographic") => {
    if (next === projection) return;
    const nextCamera = next === "perspective" ? new THREE.PerspectiveCamera(42) : new THREE.OrthographicCamera();
    copyScientificCameraView(camera, nextCamera, controls.target, width / height);
    camera = nextCamera;
    projection = next;
    (controls as unknown as { object: THREE.Camera }).object = camera;
    controls.update();
    render();
  };
  const fitSurface = () => { initialFit.markInteracted(); applyFrame(volumetricRenderBounds(grid, null, meshes)); };
  const fitStructure = () => { initialFit.markInteracted(); applyFrame(volumetricRenderBounds(grid, overlay)); };
  const pickAt = (clientX: number, clientY: number) => {
    if (disposed || contextLost) return;
    const bounds = renderer.domElement.getBoundingClientRect();
    if (!bounds.width || !bounds.height) return;
    const pointer = new THREE.Vector2(((clientX - bounds.left) / bounds.width) * 2 - 1, -((clientY - bounds.top) / bounds.height) * 2 + 1);
    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(pointer, camera);
    const visibleHit = (hit: THREE.Intersection) => hit.object.visible && clippingPlanes.every(plane => plane.distanceToPoint(hit.point) >= -1e-7);
    const atomHit = structureVisible ? raycaster.intersectObjects(atomMeshes, false).find(hit => hit.object.visible) : undefined;
    if (atomHit?.instanceId !== undefined) {
      const ids = Array.isArray(atomHit.object.userData.siteIndices) ? atomHit.object.userData.siteIndices : [];
      selected = null;
      onSurfacePick?.(null);
      onAtomPick?.(Number.isSafeInteger(ids[atomHit.instanceId]) ? ids[atomHit.instanceId] : null);
      return;
    }
    onAtomPick?.(null);
    const surfaceHit = surfaceVisible ? raycaster.intersectObjects(surfaceMeshes.filter(mesh => mesh.visible), false).find(visibleHit) : undefined;
    if (!surfaceHit || typeof surfaceHit.faceIndex !== "number") { selected = null; onSurfacePick?.(null); return; }
    const layer = surfaceHit.object.userData as { layerId: string; isovalue: number; meshHash: string };
    selected = Object.freeze({ fieldId, layerId: layer.layerId, isovalue: layer.isovalue, triangleIndex: surfaceHit.faceIndex,
      cartesianPosition: Object.freeze([surfaceHit.point.x, surfaceHit.point.y, surfaceHit.point.z]) as VolumeVector3,
      interpolatedFieldValue: layer.isovalue, meshHash: layer.meshHash });
    onSurfacePick?.(selected);
    render();
  };
  const disposePicking = bindScientificPointerPick(renderer.domElement, pickAt);
  const onLost=(event:Event)=>{event.preventDefault();contextLost=true;onContextLost();};renderer.domElement.addEventListener("webglcontextlost",onLost,false);const resize=()=>{if(disposed||!container.clientWidth||!container.clientHeight)return;width=container.clientWidth;height=container.clientHeight;resizeScientificCamera(camera,width/height);renderer.setSize(width,height,false);initialFit.resize();render();};const observer=typeof ResizeObserver==="function"?new ResizeObserver(resize):null;observer?.observe(container);window.addEventListener("resize",resize);applyClip();controls.update();render();
  const setProfilePlane=(axis:0|1|2,index:number|null)=>{profilePlaneGeometry?.dispose();profilePlaneGeometry=null;if(profilePlane){root.remove(profilePlane);profilePlane=null;}if(index===null){render();return;}if(!Number.isSafeInteger(index)||index<0||index>=grid.shape[axis]){render();return;}const other=([0,1,2] as const).filter((value)=>value!==axis);const base=add(grid.origin,scaleRow(grid.stepMatrix[axis],index));const u=scaleRow(grid.stepMatrix[other[0]],grid.shape[other[0]]),v=scaleRow(grid.stepMatrix[other[1]],grid.shape[other[1]]);const corners=[base,add(base,u),add(add(base,u),v),add(base,v)];profilePlaneGeometry=new THREE.BufferGeometry();profilePlaneGeometry.setAttribute("position",new THREE.Float32BufferAttribute(corners.flatMap((point)=>[...point]),3));profilePlaneGeometry.setIndex([0,1,2,0,2,3]);profilePlane=new THREE.Mesh(profilePlaneGeometry,profilePlaneMaterial);profilePlane.name=`potential-profile-plane-${axis}-${index}`;root.add(profilePlane);render();};
  const exportImage = createScientificPngExporter(([exportWidth,exportHeight,pixelRatio]:readonly [number,number,number]) => {
    if(!Number.isSafeInteger(exportWidth)||!Number.isSafeInteger(exportHeight)||exportWidth<256||exportHeight<256||exportWidth>4096||exportHeight>4096||![1,2].includes(pixelRatio)||exportWidth*exportHeight*pixelRatio*pixelRatio>16_777_216)throw new VolumetricViewerError("VOLUME_VIEWER_MESH_CAP_EXCEEDED","PNG export exceeds the bounded pixel budget.");
    if(disposed||contextLost)throw new Error("VIEWER_EXPORT_CONTEXT_UNAVAILABLE");
    const oldSize=renderer.getSize(new THREE.Vector2()),oldRatio=renderer.getPixelRatio();
    try {
      const exportCamera=cloneScientificExportCamera(camera,oldSize.x/oldSize.y,exportWidth/exportHeight);
      renderer.setPixelRatio(pixelRatio);renderer.setSize(exportWidth,exportHeight,false);
      renderer.render(scene,exportCamera);
      return captureScientificCanvas(renderer.domElement);
    } finally {
      renderer.setPixelRatio(oldRatio);renderer.setSize(oldSize.x,oldSize.y,false);render();
    }
  });
  const engine:VolumetricRendererEngine={setSurfaceVisible:(visible)=>{surfaceVisible=visible;surfaceMeshes.forEach((mesh)=>mesh.visible=visible);render();},setLayerVisible:(layerId,visible)=>{surfaceMeshes.filter((mesh)=>mesh.userData.layerId===layerId).forEach((mesh)=>mesh.visible=visible&&surfaceVisible);render();},setStructureVisible:(visible)=>{structureVisible=visible;overlayObjects.forEach((object)=>object.visible=visible);render();},setCellVisible:(visible)=>{if(cellLines)cellLines.visible=visible;render();},setOpacity:(opacity)=>{const bounded=Math.min(.9,Math.max(.1,Number.isFinite(opacity)?opacity:.62));surfaceMaterials.forEach((material)=>material.opacity=bounded);render();},setProjection, setClipping:(enabled,axis,offset)=>{clippingEnabled=enabled;clipAxis=axis;clipOffset=Number.isFinite(offset)?Math.max(-10000,Math.min(10000,offset)):0;applyClip();render();},resetCamera,fitSurface,fitStructure,setSelection:(pickValue)=>{selected=pickValue;render();},setProfilePlane,snapshot,render,exportPng:(width,height,ratio)=>exportImage([width,height,ratio]),dispose:()=>{if(disposed)return;disposed=true;observer?.disconnect();window.removeEventListener("resize",resize);disposePicking();renderer.domElement.removeEventListener("webglcontextlost",onLost);controls.removeEventListener("change",render);initialFit.dispose();disposeControls();surfaceMeshes.forEach((mesh)=>{mesh.geometry.dispose();(mesh.material as THREE.Material).dispose();root.remove(mesh);});atomGeometry?.dispose();atomMaterials.forEach((material)=>material.dispose());bondGeometry?.dispose();bondMaterial?.dispose();cellGeometry?.dispose();cellMaterial?.dispose();profilePlaneGeometry?.dispose();profilePlaneMaterial.dispose();renderer.forceContextLoss();renderer.dispose();renderer.domElement.remove();publish();}};
  return engine;
}

function lineGeometry(points:readonly VolumeVector3[]){const geometry=new THREE.BufferGeometry();geometry.setAttribute("position",new THREE.Float32BufferAttribute(points.flatMap((point)=>[...point]),3));return geometry;}
function cellEdges(origin:VolumeVector3,vectors:readonly[VolumeVector3,VolumeVector3,VolumeVector3]){const corners=[origin,add(origin,vectors[0]),add(add(origin,vectors[0]),vectors[1]),add(origin,vectors[1]),add(origin,vectors[2]),add(add(origin,vectors[0]),vectors[2]),add(add(add(origin,vectors[0]),vectors[1]),vectors[2]),add(add(origin,vectors[1]),vectors[2])];const edges=[[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]];return edges.flatMap(([a,b])=>[corners[a],corners[b]]);}
function add(a:VolumeVector3,b:VolumeVector3):VolumeVector3{return[a[0]+b[0],a[1]+b[1],a[2]+b[2]];}
function scaleRow(row:VolumeVector3,value:number):VolumeVector3{return[row[0]*value,row[1]*value,row[2]*value];}
function axisVector(axis:0|1|2):VolumeVector3{return axis===0?[1,0,0]:axis===1?[0,1,0]:[0,0,1];}
