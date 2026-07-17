import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

import type { BZCameraPreset, BZExportRequest, BZProjection, BZRendererEngine, BZRendererEngineFactory, BZRendererSnapshot, BZScene, BZSelection, BZVector3, BZVisibility } from "./brillouinZoneTypes";

export const createBrillouinZoneEngine: BZRendererEngineFactory = async (args) => {
  const started = now();
  const { container, scene } = args;
  const width = Math.max(container.clientWidth || 720, 320);
  const height = Math.max(container.clientHeight || 520, 280);
  let renderer: THREE.WebGLRenderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
  } catch {
    throw new Error("BZ_RENDERER_INITIALIZATION_FAILED");
  }
  renderer.domElement.dataset.testid = "brillouin-zone-renderer-canvas";
  renderer.domElement.setAttribute("aria-label", "Interactive first Brillouin zone renderer");
  renderer.domElement.setAttribute("role", "img");
  renderer.domElement.tabIndex = 0;
  renderer.domElement.style.touchAction = "pan-y";
  renderer.setPixelRatio(Math.min(Math.max(window.devicePixelRatio || 1, 1), isMobile() ? 1 : 2));
  renderer.setSize(width, height, false);
  renderer.setClearColor(0xf5f7f8, 1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  container.append(renderer.domElement);

  const threeScene = new THREE.Scene();
  const root = new THREE.Group();
  threeScene.add(root);
  const scaled = (value: BZVector3) => new THREE.Vector3(value[0] * scene.visualScale, value[1] * scene.visualScale, value[2] * scene.visualScale);
  const frame = cameraFrame(scene);
  let projection: BZProjection = args.projection;
  const perspective = new THREE.PerspectiveCamera(42, width / height, frame.near, frame.far);
  const orthographic = new THREE.OrthographicCamera(-frame.ortho * width / height, frame.ortho * width / height, frame.ortho, -frame.ortho, frame.near, frame.far);
  let camera: THREE.PerspectiveCamera | THREE.OrthographicCamera = projection === "perspective" ? perspective : orthographic;
  const initialTarget = new THREE.Vector3(0, 0, 0);
  let cameraPreset: BZCameraPreset = "isometric";
  const initialPosition = presetPosition(scene, cameraPreset, frame.distance);
  for (const item of [perspective, orthographic]) { item.position.copy(initialPosition); item.up.set(0, 0, 1); item.lookAt(initialTarget); item.updateProjectionMatrix(); }
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.copy(initialTarget);
  controls.enableDamping = false;
  controls.enablePan = true;
  controls.minDistance = Math.max(0.2, frame.radius * 0.35);
  controls.maxDistance = frame.distance * 10;

  let visibility = args.visibility;
  let opacity = boundedOpacity(args.opacity);
  let variantId = args.variantId;
  let selection: BZSelection | null = null;
  let disposed = false;
  let contextLost = false;
  let firstFrameMs = 0;
  let initializationMs = 0;

  const faceGeometry = faceBuffer(scene, scaled);
  const faceMaterial = new THREE.MeshBasicMaterial({ color: 0x62a6bb, transparent: true, opacity, side: THREE.DoubleSide, depthTest: true, depthWrite: false });
  const faces = new THREE.Mesh(faceGeometry.geometry, faceMaterial);
  faces.name = "canonical-bz-faces";
  faces.renderOrder = 2;
  root.add(faces);

  const edgeGeometry = lineBuffer(scene.edges.flatMap((edge) => edge.vertexIds.map((id) => scaled(scene.vertices.find((item) => item.id === id)!.cartesian))));
  const edgeMaterial = new THREE.LineBasicMaterial({ color: 0x123b47, transparent: false });
  const edges = new THREE.LineSegments(edgeGeometry, edgeMaterial);
  edges.name = "canonical-bz-edges";
  edges.renderOrder = 5;
  root.add(edges);

  const vertexGeometry = pointsBuffer(scene.vertices.map((vertex) => scaled(vertex.cartesian)));
  const vertexMaterial = new THREE.PointsMaterial({ color: 0x2f5964, size: 0.075, sizeAttenuation: true });
  const vertices = new THREE.Points(vertexGeometry, vertexMaterial);
  vertices.name = "canonical-bz-vertices";
  root.add(vertices);

  const axisGeometry = lineBuffer(scene.reciprocalMatrix.flatMap((axis) => [new THREE.Vector3(), scaled(axis)]));
  const axisMaterial = new THREE.LineBasicMaterial({ color: 0x24735d });
  const axes = new THREE.LineSegments(axisGeometry, axisMaterial);
  axes.name = "primitive-reciprocal-axes";
  axes.renderOrder = 4;
  root.add(axes);

  const pointGeometry = pointsBuffer(scene.points.map((point) => scaled(point.cartesian)));
  const pointMaterial = new THREE.PointsMaterial({ color: 0xb13f32, size: 0.13, sizeAttenuation: true, depthTest: false });
  const points = new THREE.Points(pointGeometry, pointMaterial);
  points.name = "high-symmetry-points";
  points.renderOrder = 10;
  root.add(points);

  let pathData = pathBuffer(scene, variantId, scaled);
  const pathMaterial = new THREE.LineBasicMaterial({ color: 0xd38a18, depthTest: false });
  const path = new THREE.LineSegments(pathData.geometry, pathMaterial);
  path.name = "high-symmetry-path";
  path.renderOrder = 9;
  root.add(path);

  let selectionGeometry = new THREE.BufferGeometry();
  const selectionMaterial = new THREE.LineBasicMaterial({ color: 0xe02154, depthTest: false });
  const selectionLines = new THREE.LineSegments(selectionGeometry, selectionMaterial);
  selectionLines.name = "bz-selection";
  selectionLines.renderOrder = 20;
  selectionLines.visible = false;
  root.add(selectionLines);
  const selectedPointGeometry = new THREE.SphereGeometry(0.11, 12, 8);
  const selectedPointMaterial = new THREE.MeshBasicMaterial({ color: 0xe02154, wireframe: true, depthTest: false });
  const selectedPoint = new THREE.Mesh(selectedPointGeometry, selectedPointMaterial);
  selectedPoint.renderOrder = 21;
  selectedPoint.visible = false;
  root.add(selectedPoint);

  const applyVisibility = () => {
    faces.visible = visibility.faces;
    edges.visible = visibility.edges;
    vertices.visible = visibility.vertices;
    axes.visible = visibility.axes;
    points.visible = visibility.points;
    path.visible = visibility.path && Boolean(variantId);
  };
  applyVisibility();

  const render = () => {
    if (disposed || contextLost || document.visibilityState === "hidden") return;
    camera.updateMatrixWorld();
    renderer.render(threeScene, camera);
    if (!firstFrameMs) firstFrameMs = elapsed(started);
  };
  const notifyView = () => { args.onViewChange(); render(); };
  controls.addEventListener("change", notifyView);

  const syncCamera = (next: THREE.PerspectiveCamera | THREE.OrthographicCamera) => {
    next.position.copy(camera.position);
    next.quaternion.copy(camera.quaternion);
    next.up.copy(camera.up);
    next.near = camera.near;
    next.far = camera.far;
    next.updateProjectionMatrix();
    camera = next;
    (controls as unknown as { object: THREE.Camera }).object = camera;
    controls.update();
  };
  const resetCamera = () => {
    cameraPreset = "isometric";
    const position = presetPosition(scene, cameraPreset, frame.distance);
    for (const item of [perspective, orthographic]) { item.position.copy(position); item.up.set(0,0,1); item.lookAt(initialTarget); item.zoom = 1; item.updateProjectionMatrix(); }
    camera = projection === "perspective" ? perspective : orthographic;
    (controls as unknown as { object: THREE.Camera }).object = camera;
    controls.target.copy(initialTarget);
    controls.update();
    notifyView();
  };
  const setCameraPreset = (preset: BZCameraPreset) => {
    cameraPreset = preset;
    camera.position.copy(presetPosition(scene, preset, frame.distance));
    camera.up.set(0,0,1);
    camera.lookAt(controls.target);
    camera.updateProjectionMatrix();
    controls.update();
    notifyView();
  };

  const updateSelection = (next: BZSelection | null) => {
    selection = next;
    selectionLines.visible = false;
    selectedPoint.visible = false;
    const segments: THREE.Vector3[] = [];
    if (next?.kind === "point") {
      const item = scene.points.find((point) => point.id === next.id);
      if (item) { selectedPoint.position.copy(scaled(item.cartesian)); selectedPoint.visible = true; }
    } else if (next?.kind === "vertex") {
      const item = scene.vertices.find((vertex) => vertex.id === next.id);
      if (item) { selectedPoint.position.copy(scaled(item.cartesian)); selectedPoint.visible = true; }
    } else if (next?.kind === "face") {
      const item = scene.faces.find((face) => face.id === next.id);
      if (item) for (let index = 0; index < item.vertexIds.length; index += 1) { segments.push(scaled(scene.vertices.find((vertex) => vertex.id === item.vertexIds[index])!.cartesian), scaled(scene.vertices.find((vertex) => vertex.id === item.vertexIds[(index+1)%item.vertexIds.length])!.cartesian)); }
    } else if (next?.kind === "segment") {
      const item = scene.segments.find((segment) => segment.id === next.id && segment.variantId === next.variantId);
      if (item) segments.push(scaled(item.start), scaled(item.end));
    } else if (next?.kind === "reciprocal_sample") {
      selectedPoint.position.copy(scaled(next.cartesian));
      selectedPoint.visible = true;
      const item = scene.segments.find((segment) => segment.id === next.segmentId);
      if (item) segments.push(scaled(item.start), scaled(item.end));
    }
    selectionGeometry.dispose();
    selectionGeometry = lineBuffer(segments);
    selectionLines.geometry = selectionGeometry;
    selectionLines.visible = segments.length > 0;
    render();
  };

  const raycaster = new THREE.Raycaster();
  raycaster.params.Points!.threshold = 0.14;
  raycaster.params.Line!.threshold = 0.08;
  const pointer = new THREE.Vector2();
  const pickAt = (clientX: number, clientY: number) => {
    if (disposed || contextLost) return;
    const bounds = renderer.domElement.getBoundingClientRect();
    pointer.set(((clientX-bounds.left)/bounds.width)*2-1,-((clientY-bounds.top)/bounds.height)*2+1);
    raycaster.setFromCamera(pointer, camera);
    if (points.visible) {
      const hit = raycaster.intersectObject(points, false)[0];
      if (hit?.index !== undefined && scene.points[hit.index]) return args.onSelection({kind:"point",id:scene.points[hit.index].id});
    }
    if (vertices.visible) {
      const hit = raycaster.intersectObject(vertices, false)[0];
      if (hit?.index !== undefined && scene.vertices[hit.index]) return args.onSelection({kind:"vertex",id:scene.vertices[hit.index].id});
    }
    if (path.visible) {
      const hit = raycaster.intersectObject(path, false)[0];
      if (typeof hit?.index === "number") { const id=pathData.segmentIds[Math.floor(hit.index/2)]; if(id)return args.onSelection({kind:"segment",id,variantId:variantId!}); }
    }
    if (faces.visible) {
      const hit = raycaster.intersectObject(faces, false)[0];
      if (typeof hit?.faceIndex === "number") { const id=faceGeometry.faceIds[hit.faceIndex]; if(id)return args.onSelection({kind:"face",id}); }
    }
    args.onSelection(null);
  };
  let pointerStart: { id:number;x:number;y:number } | null = null;
  const onPointerDown = (event: PointerEvent) => { if(event.button===0)pointerStart={id:event.pointerId,x:event.clientX,y:event.clientY}; };
  const onPointerUp = (event: PointerEvent) => { const start=pointerStart;pointerStart=null;if(start&&start.id===event.pointerId&&Math.hypot(event.clientX-start.x,event.clientY-start.y)<=5)pickAt(event.clientX,event.clientY); };
  const onPointerCancel = () => { pointerStart=null; };
  renderer.domElement.addEventListener("pointerdown",onPointerDown);
  renderer.domElement.addEventListener("pointerup",onPointerUp);
  renderer.domElement.addEventListener("pointercancel",onPointerCancel);
  const onLost = (event: Event) => { event.preventDefault(); if(contextLost||disposed)return;contextLost=true;args.onContextLost(); };
  renderer.domElement.addEventListener("webglcontextlost",onLost,false);

  const resize = () => {
    if(disposed)return;
    const nextWidth=Math.max(container.clientWidth||720,320);const nextHeight=Math.max(container.clientHeight||520,280);const aspect=nextWidth/nextHeight;
    perspective.aspect=aspect;
    orthographic.left=-frame.ortho*aspect;orthographic.right=frame.ortho*aspect;orthographic.top=frame.ortho;orthographic.bottom=-frame.ortho;
    perspective.updateProjectionMatrix();orthographic.updateProjectionMatrix();renderer.setSize(nextWidth,nextHeight,false);render();
  };
  const resizeObserver = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(resize);
  resizeObserver?.observe(container);

  const snapshot = (): BZRendererSnapshot => Object.freeze({
    state: contextLost ? "context_lost" : disposed ? "disposed" : "rendered",
    graphicsContext: renderer.capabilities.isWebGL2 ? "webgl2" : "webgl",
    rendererVersion: THREE.REVISION,
    projection,
    cameraPosition: vector(camera.position),
    cameraTarget: vector(controls.target),
    cameraUp: vector(camera.up),
    selection,
    pointScreenPositions: Object.freeze(scene.points.map((item)=>screenPosition(item.id,scaled(item.cartesian),camera,renderer.domElement))),
    faceScreenPositions: Object.freeze(scene.faces.map((item)=>screenPosition(item.id,scaled(item.centroid),camera,renderer.domElement))),
    metrics: Object.freeze({ artifactBytes:args.artifactBytes,vertexCount:scene.vertices.length,edgeCount:scene.edges.length,faceCount:scene.faces.length,triangleCount:scene.faces.reduce((sum,item)=>sum+item.triangleVertexIndices.length/3,0),pointCount:scene.points.length,pathSegmentCount:pathData.segmentIds.length,visibleLabelCount:visibility.labels?Math.min(scene.points.length,64):0,drawCalls:renderer.info.render.calls,geometries:renderer.info.memory.geometries,materials:8,textures:renderer.info.memory.textures,canvasCount:container.querySelectorAll("canvas").length,contextCount:1,mappingMs:args.mappingMs,initializationMs,firstFrameMs }),
  });

  const engine: BZRendererEngine = {
    resetCamera,
    fit: resetCamera,
    setCameraPreset,
    setProjection(next) { if(next===projection)return;projection=next;syncCamera(next==="perspective"?perspective:orthographic);notifyView(); },
    setVisibility(next) { visibility=next;applyVisibility();if(selection&&((selection.kind==="point"&&!next.points)||(selection.kind==="vertex"&&!next.vertices)||(selection.kind==="face"&&!next.faces)||((selection.kind==="segment"||selection.kind==="reciprocal_sample")&&!next.path)))args.onSelection(null);render(); },
    setOpacity(next) { opacity=boundedOpacity(next);faceMaterial.opacity=opacity;render(); },
    setVariant(next) { if(next===variantId)return;variantId=next;pathData.geometry.dispose();pathData=pathBuffer(scene,variantId,scaled);path.geometry=pathData.geometry;path.visible=visibility.path&&Boolean(variantId);if(selection?.kind==="segment"&&selection.variantId!==variantId)args.onSelection(null);render(); },
    setSelection: updateSelection,
    keyboardCamera(action) { const offset=camera.position.clone().sub(controls.target);const spherical=new THREE.Spherical().setFromVector3(offset);if(action.startsWith("rotate_")){const step=0.12;if(action==="rotate_left")spherical.theta-=step;if(action==="rotate_right")spherical.theta+=step;if(action==="rotate_up")spherical.phi=Math.max(0.1,spherical.phi-step);if(action==="rotate_down")spherical.phi=Math.min(Math.PI-0.1,spherical.phi+step);camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(spherical));}else if(action.startsWith("pan_")){const right=new THREE.Vector3().crossVectors(camera.getWorldDirection(new THREE.Vector3()),camera.up).normalize();const delta=action==="pan_left"?right.multiplyScalar(-frame.radius*.08):action==="pan_right"?right.multiplyScalar(frame.radius*.08):new THREE.Vector3();camera.position.add(delta);controls.target.add(delta);}else{const factor=action==="zoom_in"?.88:1.14;camera.position.copy(controls.target).add(offset.multiplyScalar(factor));}cameraPreset="isometric";controls.update();notifyView(); },
    async exportPng(request) { validateExport(request);if(disposed||contextLost)throw new Error("BZ_RENDERER_CONTEXT_UNAVAILABLE");const previousSize=renderer.getSize(new THREE.Vector2());const previousRatio=renderer.getPixelRatio();const previousColor=renderer.getClearColor(new THREE.Color()).clone();const previousAlpha=renderer.getClearAlpha();const previousAspect=perspective.aspect;try{renderer.setPixelRatio(request.pixelRatio);renderer.setSize(request.width,request.height,false);perspective.aspect=request.width/request.height;perspective.updateProjectionMatrix();const color=request.background==="dark"?0x101820:0xf5f7f8;renderer.setClearColor(color,request.background==="transparent"?0:1);render();return await new Promise<Blob>((resolve,reject)=>renderer.domElement.toBlob((blob)=>blob?resolve(blob):reject(new Error("BZ_EXPORT_FAILED")),"image/png"));}finally{renderer.setPixelRatio(previousRatio);renderer.setSize(previousSize.x,previousSize.y,false);renderer.setClearColor(previousColor,previousAlpha);perspective.aspect=previousAspect;perspective.updateProjectionMatrix();render();}},
    snapshot,
    dispose() { if(disposed)return;disposed=true;controls.removeEventListener("change",notifyView);controls.dispose();resizeObserver?.disconnect();renderer.domElement.removeEventListener("pointerdown",onPointerDown);renderer.domElement.removeEventListener("pointerup",onPointerUp);renderer.domElement.removeEventListener("pointercancel",onPointerCancel);renderer.domElement.removeEventListener("webglcontextlost",onLost);for(const geometry of [faceGeometry.geometry,edgeGeometry,vertexGeometry,axisGeometry,pointGeometry,pathData.geometry,selectionGeometry,selectedPointGeometry])geometry.dispose();for(const material of [faceMaterial,edgeMaterial,vertexMaterial,axisMaterial,pointMaterial,pathMaterial,selectionMaterial,selectedPointMaterial])material.dispose();threeScene.clear();renderer.dispose();renderer.forceContextLoss();if(renderer.domElement.parentElement===container)renderer.domElement.remove(); },
  };
  render();
  initializationMs=elapsed(started);
  return engine;
};

function faceBuffer(scene: BZScene, scaled:(value:BZVector3)=>THREE.Vector3) { const positions:number[]=[];const normals:number[]=[];const faceIds:string[]=[];for(const face of scene.faces)for(let index=0;index<face.triangleVertexIndices.length;index+=3){for(let offset=0;offset<3;offset+=1){const point=scaled(scene.vertices[face.triangleVertexIndices[index+offset]].cartesian);positions.push(point.x,point.y,point.z);normals.push(...face.outwardNormal);}faceIds.push(face.id);}const geometry=new THREE.BufferGeometry();geometry.setAttribute("position",new THREE.Float32BufferAttribute(positions,3));geometry.setAttribute("normal",new THREE.Float32BufferAttribute(normals,3));geometry.computeBoundingSphere();return{geometry,faceIds}; }
function lineBuffer(points:readonly THREE.Vector3[]){const geometry=new THREE.BufferGeometry();geometry.setAttribute("position",new THREE.Float32BufferAttribute(points.flatMap((point)=>[point.x,point.y,point.z]),3));geometry.computeBoundingSphere();return geometry;}
function pointsBuffer(points:readonly THREE.Vector3[]){return lineBuffer(points);}
function pathBuffer(scene:BZScene,variantId:string|null,scaled:(value:BZVector3)=>THREE.Vector3){const allowed=new Set(scene.variants.find((item)=>item.id===variantId)?.segmentIds??[]);const segments=scene.segments.filter((item)=>allowed.has(item.id));return{geometry:lineBuffer(segments.flatMap((item)=>[scaled(item.start),scaled(item.end)])),segmentIds:segments.map((item)=>item.id)};}
function cameraFrame(scene:BZScene){const points=scene.vertices.map((item)=>new THREE.Vector3(...item.cartesian).multiplyScalar(scene.visualScale));const box=new THREE.Box3().setFromPoints(points);const sphere=box.getBoundingSphere(new THREE.Sphere());const radius=Math.max(sphere.radius,1);return{radius,distance:radius*3.2,near:Math.max(radius/100,0.01),far:radius*50,ortho:radius*1.45};}
function presetPosition(scene:BZScene,preset:BZCameraPreset,distance:number){const matrix=scene.reciprocalMatrix.map((item)=>new THREE.Vector3(...item).normalize());const direction=preset==="b1"?matrix[0]:preset==="b2"?matrix[1]:preset==="b3"?matrix[2]:matrix[0].clone().add(matrix[1]).add(matrix[2]).normalize();if(direction.lengthSq()<1e-12)direction.set(1,1,1).normalize();return direction.multiplyScalar(distance);}
function screenPosition(id:string,point:THREE.Vector3,camera:THREE.Camera,canvas:HTMLCanvasElement){const projected=point.clone().project(camera);return Object.freeze({id,x:round((projected.x+1)*.5*canvas.clientWidth),y:round((1-projected.y)*.5*canvas.clientHeight)});}
function validateExport(value:BZExportRequest){if(!Number.isSafeInteger(value.width)||!Number.isSafeInteger(value.height)||value.width<256||value.height<256||value.width>4096||value.height>4096||![1,2].includes(value.pixelRatio)||value.width*value.height*value.pixelRatio*value.pixelRatio>16_777_216||!["light","dark","transparent"].includes(value.background))throw new Error("BZ_EXPORT_LIMIT_EXCEEDED");}
function boundedOpacity(value:number){if(!Number.isFinite(value))return .28;return Math.min(.65,Math.max(.08,value));}
function vector(value:THREE.Vector3):BZVector3{return Object.freeze([round(value.x),round(value.y),round(value.z)]);}
function round(value:number){return Math.round(value*1e6)/1e6;}
function isMobile(){return typeof window!=="undefined"&&window.matchMedia?.("(max-width: 760px)").matches;}
function now(){return typeof performance==="undefined"?Date.now():performance.now();}
function elapsed(started:number){return Math.max(0,now()-started);}
