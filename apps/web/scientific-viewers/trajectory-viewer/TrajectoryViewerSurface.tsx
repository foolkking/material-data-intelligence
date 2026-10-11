"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { measureAngle, measureDihedral, measureDistance, formatMeasurement, type ViewerMeasurementEvaluation } from "../viewer-scene/viewerSceneMeasurements";
import type { ImageOffset, PeriodicSiteRef, ViewerRendererEngine, ViewerRendererEngineFactory, ViewerRendererSnapshot } from "../viewer-scene/viewerSceneRendererTypes";
import { supportsManagedWebGL } from "../viewer-scene/viewerWebglCapability";
import { initialViewerClipState } from "../viewer-scene/viewerSceneViewState";
import { TrajectoryFrameCache } from "./trajectoryFrameCache";
import { classifyTrajectoryViewer, mapTrajectoryFrame, validateTrajectoryForViewer } from "./trajectoryFrameMapper";
import { nextTrajectoryFrame, setTrajectoryPlaying, setTrajectorySpeed } from "./trajectoryViewerState";
import { TRAJECTORY_DEFAULT_REPEAT, TRAJECTORY_PLAYBACK_SPEEDS, type MappedTrajectoryFrame, type TrajectoryViewerState } from "./trajectoryViewerTypes";
import { trajectoryPoint, trajectoryPointIds, trajectoryPointLabel, type TrajectoryPoint } from "./trajectory-selection";

export type TrajectoryViewerProductIdentity="structure.trajectory_viewer"|"structure.trajectory_import"|"unknown";
export type TrajectoryViewerLaunchOptions=Readonly<{playbackSpeed:0.25|0.5|1|2|4;loop:boolean;supercell:ImageOffset;showCell:boolean;clipping:boolean;performanceMode:"auto";bondMode:"none"}>;
export type TrajectoryViewerSurfaceProps = Readonly<{payload:unknown;toolId?:TrajectoryViewerProductIdentity;initialOptions?:TrajectoryViewerLaunchOptions;capabilityOverride?:boolean;engineFactory?:ViewerRendererEngineFactory;mobileOverride?:boolean;selectedPoint?:TrajectoryPoint|null;onPointSelection?:(point:TrajectoryPoint|null)=>void}>;
const defaultEngineFactory:ViewerRendererEngineFactory=async(args)=>(await import("../viewer-scene/viewerSceneRendererEngine")).createThreeViewerEngine(args);
const DEFAULT_LAUNCH_OPTIONS:TrajectoryViewerLaunchOptions=Object.freeze({playbackSpeed:1,loop:false,supercell:TRAJECTORY_DEFAULT_REPEAT,showCell:true,clipping:false,performanceMode:"auto",bondMode:"none"});
const limits={inspect:1,distance:2,angle:3,dihedral:4} as const;
const SUPERCELL_OPTIONS = [1, 2, 3] as const;
type SelectionMode=keyof typeof limits;

export function TrajectoryViewerSurface({payload,toolId="unknown",initialOptions=DEFAULT_LAUNCH_OPTIONS,capabilityOverride,engineFactory=defaultEngineFactory,mobileOverride,selectedPoint,onPointSelection}:TrajectoryViewerSurfaceProps){
  const validation=useMemo(()=>validateTrajectoryForViewer(payload),[payload]);
  const trajectory=validation.ok?validation.trajectory:null;
  const [repeat,setRepeat]=useState<ImageOffset>(initialOptions.supercell);
  const [detectedMobile,setDetectedMobile]=useState(false);
  const mobile=mobileOverride??detectedMobile;
  const decision=useMemo(()=>trajectory?classifyTrajectoryViewer(trajectory,repeat,mobile):null,[trajectory,repeat,mobile]);
  const [viewerState,setViewerState]=useState<TrajectoryViewerState>(()=>Object.freeze({status:"idle",currentFrameIndex:0,requestedFrameIndex:0,frameCount:0,playbackSpeed:initialOptions.playbackSpeed,loop:initialOptions.loop,isBuffering:false,activeGeneration:0}));
  const stateRef=useRef(viewerState);stateRef.current=viewerState;
  const [mapped,setMapped]=useState<MappedTrajectoryFrame|null>(null);const mappedRef=useRef(mapped);mappedRef.current=mapped;
  const [selectionMode,setSelectionMode]=useState<SelectionMode>("inspect");
  const selectionModeRef=useRef<SelectionMode>(selectionMode);selectionModeRef.current=selectionMode;
  const [selectedRefs,setSelectedRefs]=useState<readonly PeriodicSiteRef[]>(Object.freeze([]));
  const [measurement,setMeasurement]=useState<ViewerMeasurementEvaluation|null>(null);
  const [snapshot,setSnapshot]=useState<ViewerRendererSnapshot|null>(null);
  const [announcement,setAnnouncement]=useState("Trajectory viewer idle.");
  const [fallbackCode,setFallbackCode]=useState<string|null>(null);
  const [attempt,setAttempt]=useState(0);
  const [showCell,setShowCell]=useState(initialOptions.showCell);
  const [clipEnabled,setClipEnabled]=useState(initialOptions.clipping);
  const clipEnabledRef=useRef(clipEnabled);clipEnabledRef.current=clipEnabled;
  const hostRef=useRef<HTMLDivElement>(null);const surfaceRef=useRef<HTMLElement>(null);const engineRef=useRef<ViewerRendererEngine|null>(null);
  const generationRef=useRef(0);const playbackTimerRef=useRef<ReturnType<typeof setTimeout>|null>(null);const disposedRef=useRef(false);
  const pendingFrameRef=useRef<{index:number;generation:number;manual:boolean}|null>(null);const mappingScheduledRef=useRef(false);const peakPendingRef=useRef(0);
  const cacheRef=useRef<TrajectoryFrameCache|null>(null);
  const trajectoryIdRef=useRef<string|null>(null);
  const rendererFailureRef=useRef<((code:string)=>void)|null>(null);
  const focusOnRecoveryRef=useRef(false);
  const externalIds = selectedPoint ? trajectoryPointIds(selectedPoint) : null;
  const externalPoint = useMemo(() => externalIds ? trajectoryPoint(payload, externalIds.frameId, externalIds.atomId)?.point ?? null : null, [payload, externalIds?.frameId, externalIds?.atomId]);
  const externalKey = externalPoint ? JSON.stringify(trajectoryPointIds(externalPoint)) : "";
  const appliedExternalRef = useRef<{key:string;engine:ViewerRendererEngine|null}>({key:"",engine:null});
  const requestedRepeatRef = useRef("");
  const [selectionRestoreWarning,setSelectionRestoreWarning]=useState(false);

  const stopPlayback=useCallback((message?:string)=>{if(playbackTimerRef.current){clearTimeout(playbackTimerRef.current);playbackTimerRef.current=null;}setViewerState((state)=>setTrajectoryPlaying(state,false));if(message)setAnnouncement(message);},[]);

  const commitMapped=useCallback((next:MappedTrajectoryFrame,index:number,generation:number,manual:boolean)=>{
    if(disposedRef.current||generation!==generationRef.current)return;
    try{engineRef.current?.updateDynamicScene(next.scene);if(clipEnabledRef.current)engineRef.current?.setClipState(Object.freeze({...initialViewerClipState(next.scene),enabled:true}));}catch{rendererFailureRef.current?.("TRAJECTORY_VIEWER_FRAME_LOAD_FAILED");return;}
    mappedRef.current=next;setMapped(next);setViewerState((state)=>generation!==state.activeGeneration?state:Object.freeze({...state,currentFrameIndex:index,requestedFrameIndex:index,isBuffering:false}));
    setMeasurement(null);setSelectedRefs((refs)=>selectionModeRef.current==="inspect"?refs:Object.freeze([]));setSnapshot(engineRef.current?.snapshot()??null);
    if(manual)setAnnouncement(`第 ${index+1} / ${trajectory?.frames.length ?? 0} 帧。`);
  },[stopPlayback,trajectory?.frames.length]);

  const seek=useCallback((index:number,manual=true)=>{
    if(!engineRef.current||!trajectory||!decision||decision.mode==="refused"||!Number.isSafeInteger(index)||index<0||index>=trajectory.frames.length)return;
    if(manual)stopPlayback();
    const generation=++generationRef.current;setViewerState((state)=>Object.freeze({...state,requestedFrameIndex:index,isBuffering:index!==state.currentFrameIndex,activeGeneration:generation}));
    pendingFrameRef.current={index,generation,manual};peakPendingRef.current=Math.max(peakPendingRef.current,1);if(mappingScheduledRef.current)return;mappingScheduledRef.current=true;
    queueMicrotask(()=>{mappingScheduledRef.current=false;const pending=pendingFrameRef.current;pendingFrameRef.current=null;if(!pending||pending.generation!==generationRef.current||disposedRef.current)return;try{const cache=cacheRef.current;const next=cache?.get(pending.index)??mapTrajectoryFrame(trajectory,pending.index,repeat);cache?.set(next,stateRef.current.currentFrameIndex);commitMapped(next,pending.index,pending.generation,pending.manual);}catch{if(pending.generation!==generationRef.current)return;rendererFailureRef.current?.("TRAJECTORY_VIEWER_FRAME_LOAD_FAILED");}});
  },[commitMapped,decision,repeat,stopPlayback,trajectory]);

  const onPick=useCallback((ref:PeriodicSiteRef|null)=>{
    if(stateRef.current.isBuffering){setAnnouncement("正在切换帧，请稍后选择原子。");return;}
    if(stateRef.current.status==="playing")stopPlayback("已暂停播放，可以查看所选原子。");
    if(!ref){setSelectedRefs(Object.freeze([]));setMeasurement(null);return;}
    setSelectedRefs((current)=>{const mode=selectionModeRef.current;if(mode==="inspect")return Object.freeze([ref]);const exists=current.some((item)=>item.siteIndex===ref.siteIndex&&item.imageOffset.every((value,index)=>value===ref.imageOffset[index]));if(exists)return current;const next=Object.freeze([...current,ref].slice(-limits[mode]));return next;});
  },[stopPlayback]);

  useEffect(() => {
    disposedRef.current = false; generationRef.current += 1; pendingFrameRef.current = null; mappingScheduledRef.current = false; peakPendingRef.current = 0;
    stopPlayback(); engineRef.current?.dispose(); engineRef.current = null;
    setSelectedRefs(Object.freeze([])); setMeasurement(null); setSnapshot(null); setFallbackCode(null);
    if (!trajectory || !decision) {
      setViewerState(state => Object.freeze({...state, status: "error", frameCount: 0}));
      return () => { disposedRef.current = true; };
    }
    const sameTrajectory = trajectoryIdRef.current === trajectory.trajectory_id;
    const initialIndex = sameTrajectory ? Math.min(stateRef.current.currentFrameIndex, trajectory.frames.length - 1) : 0;
    trajectoryIdRef.current = trajectory.trajectory_id;
    setViewerState(Object.freeze({status: decision.mode === "refused" ? "refused" : "loading", currentFrameIndex: initialIndex, requestedFrameIndex: initialIndex,
      frameCount: trajectory.frames.length, playbackSpeed: sameTrajectory ? stateRef.current.playbackSpeed : initialOptions.playbackSpeed,
      loop: sameTrajectory ? stateRef.current.loop : initialOptions.loop, isBuffering: true, activeGeneration: generationRef.current}));
    if (decision.mode === "refused") return () => { disposedRef.current = true; };
    if (focusOnRecoveryRef.current) { surfaceRef.current?.focus({preventScroll:true}); focusOnRecoveryRef.current = false; }
    cacheRef.current = new TrajectoryFrameCache(decision.cacheFrames, decision.cacheBytes, trajectory.trajectory_id);
    let first: MappedTrajectoryFrame;
    try { first = mapTrajectoryFrame(trajectory, initialIndex, repeat); cacheRef.current.set(first); setMapped(first); mappedRef.current = first; }
    catch { setFallbackCode("TRAJECTORY_VIEWER_FRAME_LOAD_FAILED"); return () => { disposedRef.current = true; cacheRef.current?.clear(); }; }
    const supported = capabilityOverride ?? supportsManagedWebGL(), host = hostRef.current;
    if (!supported || !host) {
      setFallbackCode(supported ? "TRAJECTORY_VIEWER_INITIALIZATION_FAILED" : "TRAJECTORY_VIEWER_UNSUPPORTED");
      return () => { disposedRef.current = true; cacheRef.current?.clear(); };
    }
    // A timed-out factory may still append a canvas; each attempt owns a detachable host.
    const canvasHost = document.createElement("div");
    canvasHost.style.width = "100%"; canvasHost.style.height = "100%";
    host.appendChild(canvasHost);
    let active = true, ownedEngine: ViewerRendererEngine | null = null;
    const dispose = () => {
      const engine = ownedEngine; ownedEngine = null;
      if (engineRef.current === engine) engineRef.current = null;
      canvasHost.remove(); engine?.dispose();
    };
    const fail = (code: string) => {
      if (!active) return;
      active = false; clearTimeout(timer); generationRef.current += 1; stopPlayback(); dispose();
      setFallbackCode(code); setSnapshot(null);
      setViewerState(state => Object.freeze({...state, status: code === "TRAJECTORY_VIEWER_CONTEXT_LOST" ? "context_lost" : "error", isBuffering: false}));
      setAnnouncement("轨迹画面暂时无法显示，当前帧和来源信息已保留。");
    };
    rendererFailureRef.current = fail;
    const timer = setTimeout(() => fail("TRAJECTORY_VIEWER_INITIALIZATION_TIMEOUT"), 10_000);
    setAnnouncement("正在加载轨迹画面。");
    void Promise.resolve().then(() => engineFactory({container: canvasHost, scene: first.scene,
      pixelRatioCap: decision.mode === "degraded" ? 1 : 2, antialias: decision.mode !== "degraded", performanceTier: decision.mode === "degraded" ? "degraded" : "interactive",
      onContextLost: () => fail("TRAJECTORY_VIEWER_CONTEXT_LOST"),
      onSitePick: ref => { if (active && engineRef.current) onPick(ref); },
      onViewChange: () => { if (active) setSnapshot(engineRef.current?.snapshot() ?? null); },
    })).then(engine => {
      if (!active) { engine.dispose(); return; }
      ownedEngine = engine; engineRef.current = engine;
      engine.setBondsVisible(false); engine.setCellVisible(showCell);
      if (clipEnabledRef.current) engine.setClipState(Object.freeze({...initialViewerClipState(first.scene), enabled: true}));
      clearTimeout(timer); setSnapshot(engine.snapshot());
      setViewerState(state => Object.freeze({...state, status: decision.mode === "degraded" ? "degraded" : "paused", isBuffering: false}));
      setAnnouncement(`已加载轨迹，停在第 ${initialIndex + 1} / ${trajectory.frames.length} 帧。`);
    }).catch(() => fail("TRAJECTORY_VIEWER_INITIALIZATION_FAILED"));
    return () => {
      active = false; clearTimeout(timer); if(rendererFailureRef.current === fail)rendererFailureRef.current = null; disposedRef.current = true; generationRef.current += 1;
      pendingFrameRef.current = null; mappingScheduledRef.current = false; stopPlayback(); cacheRef.current?.clear(); cacheRef.current = null; dispose();
    };
  }, [attempt, capabilityOverride, decision, engineFactory, initialOptions.loop, initialOptions.playbackSpeed, onPick, repeat, stopPlayback, trajectory]);

  useEffect(()=>{if(viewerState.status!=="playing"||!decision)return;const interval=1000/Math.min(decision.maxPlaybackFps,10*viewerState.playbackSpeed);playbackTimerRef.current=setTimeout(()=>{playbackTimerRef.current=null;const next=nextTrajectoryFrame(stateRef.current);if(next.ended){stopPlayback(`已播放到最后一帧（第 ${stateRef.current.currentFrameIndex+1} 帧）。`);return;}seek(next.index,false);},interval);return()=>{if(playbackTimerRef.current){clearTimeout(playbackTimerRef.current);playbackTimerRef.current=null;}};},[decision,seek,stopPlayback,viewerState.currentFrameIndex,viewerState.playbackSpeed,viewerState.status]);
  useEffect(()=>{if(mobileOverride!==undefined){setDetectedMobile(mobileOverride);return;}const update=()=>setDetectedMobile(Math.min(window.innerWidth,window.innerHeight)<=640||(typeof navigator!=="undefined"&&navigator.maxTouchPoints>0));update();window.addEventListener("resize",update);return()=>window.removeEventListener("resize",update);},[mobileOverride]);
  useEffect(()=>{const visibility=()=>{if(document.hidden)stopPlayback("离开页面后已暂停播放。");};document.addEventListener("visibilitychange",visibility);return()=>document.removeEventListener("visibilitychange",visibility);},[stopPlayback]);
  useEffect(()=>{engineRef.current?.setSelection(selectedRefs);setSnapshot(engineRef.current?.snapshot()??null);if(!mapped||selectionMode==="inspect"||selectedRefs.length!==limits[selectionMode]){setMeasurement(null);return;}const byRef=new Map(mapped.scene.atoms.map((atom)=>[`${atom.siteIndex}:${atom.ref.imageOffset.join(":")}`,atom.position] as const));const points=selectedRefs.map((ref)=>byRef.get(`${ref.siteIndex}:${ref.imageOffset.join(":")}`)).filter((point):point is readonly[number,number,number]=>Boolean(point));const ids=selectedRefs.map((ref)=>ref.siteIndex);if(points.length!==selectedRefs.length){setMeasurement(null);return;}setMeasurement(selectionMode==="distance"?measureDistance(ids as [number,number],points as [typeof points[0],typeof points[0]]):selectionMode==="angle"?measureAngle(ids as [number,number,number],points as [typeof points[0],typeof points[0],typeof points[0]]):measureDihedral(ids as [number,number,number,number],points as [typeof points[0],typeof points[0],typeof points[0],typeof points[0]]));},[mapped,selectedRefs,selectionMode]);

  useEffect(() => {
    if (selectedPoint === undefined || !trajectory || !snapshot || viewerState.status === "loading" || !engineRef.current) return;
    if (appliedExternalRef.current.key === externalKey && appliedExternalRef.current.engine === engineRef.current) return;
    if (!externalPoint) {
      if (appliedExternalRef.current.key) {setSelectedRefs(Object.freeze([]));setMeasurement(null);}
      appliedExternalRef.current={key:"",engine:engineRef.current};requestedRepeatRef.current="";setSelectionRestoreWarning(false);return;
    }
    const required = externalPoint.atom ? Math.max(...externalPoint.atom.imageOffset) + 1 : 1;
    const outside = Boolean(externalPoint.atom?.imageOffset.some((value,axis) => value >= repeat[axis]));
    if (outside && requestedRepeatRef.current !== externalKey && classifyTrajectoryViewer(trajectory,[required,required,required],mobile).mode !== "refused") {
      requestedRepeatRef.current=externalKey;stopPlayback();setRepeat(Object.freeze([required,required,required]));return;
    }
    appliedExternalRef.current={key:externalKey,engine:engineRef.current};setSelectionRestoreWarning(outside);
    selectionModeRef.current="inspect";setSelectionMode("inspect");setMeasurement(null);
    setSelectedRefs(externalPoint.atom && !outside ? Object.freeze([externalPoint.atom]) : Object.freeze([]));
    seek(externalPoint.frameIndex);
  }, [externalKey, externalPoint, selectedPoint, trajectory, snapshot, viewerState.status, repeat, mobile, seek, stopPlayback]);

  const setMode=(mode:SelectionMode)=>{setSelectionMode(mode);setSelectedRefs(Object.freeze([]));setMeasurement(null);setAnnouncement(`${({inspect:"检查",distance:"距离",angle:"角度",dihedral:"二面角"} as const)[mode]}模式已选择。`);};
  const togglePlay=()=>{if(!engineRef.current)return;if(viewerState.status==="playing"){stopPlayback(`已暂停在第 ${viewerState.currentFrameIndex+1} 帧。`);return;}setSelectedRefs(Object.freeze([]));setMeasurement(null);setViewerState((state)=>setTrajectoryPlaying(state,true));setAnnouncement("已开始播放；显示速度不代表物理时间尺度。");};
  const keyDown=(event:React.KeyboardEvent)=>{
    if(event.target!==event.currentTarget)return;
    const actions:Record<string,()=>void>={ArrowLeft:()=>seek(Math.max(0,stateRef.current.currentFrameIndex-1)),ArrowRight:()=>seek(Math.min(stateRef.current.frameCount-1,stateRef.current.currentFrameIndex+1)),Home:()=>seek(0),End:()=>seek(stateRef.current.frameCount-1)," ":togglePlay,
      n:()=>{const atoms=mappedRef.current?.scene.atoms;if(!atoms?.length)return;const last=selectedRefs.at(-1);const index=last?atoms.findIndex(atom=>atom.siteIndex===last.siteIndex&&atom.ref.imageOffset.every((value,axis)=>value===last.imageOffset[axis])):-1;onPick(atoms[(index+1)%atoms.length].ref);},
      Escape:()=>onPick(null)};
    const action=actions[event.key.length===1&&event.key!==" "?event.key.toLowerCase():event.key];if(action){event.preventDefault();action();}
  };

  if(!validation.ok)return <TrajectoryFallback title="轨迹数据无效" code={validation.errors[0]??"TRAJECTORY_VIEWER_ARTIFACT_INVALID"} payload={payload}/>;
  if(!trajectory||!decision)return <TrajectoryFallback title="轨迹数据无效" code="TRAJECTORY_VIEWER_ARTIFACT_INVALID" payload={payload}/>;
  if(decision.mode==="refused")return <TrajectoryFallback title="轨迹查看器数据量超出范围" code="TRAJECTORY_VIEWER_BUDGET_EXCEEDED" payload={payload} frameIndex={viewerState.currentFrameIndex}
    onReduceSupercell={repeat.some(value => value !== 1) && classifyTrajectoryViewer(trajectory, TRAJECTORY_DEFAULT_REPEAT, mobile).mode !== "refused" ? () => {focusOnRecoveryRef.current=true;setRepeat(TRAJECTORY_DEFAULT_REPEAT);} : undefined}/>;
  if(fallbackCode)return <TrajectoryFallback title="轨迹渲染器暂不可用" code={fallbackCode} payload={payload} frameIndex={viewerState.currentFrameIndex} onRetry={()=>{focusOnRecoveryRef.current=true;setFallbackCode(null);setAttempt((value)=>value+1);}}/>;
  const frame=mapped?.rawFrame;const selected=selectedRefs[0];const selectedAtom=selected&&mapped?.scene.atoms.find((atom)=>atom.siteIndex===selected.siteIndex&&atom.ref.imageOffset.every((value,index)=>value===selected.imageOffset[index]));const selectedVelocity=selected&&frame?.velocities?.[selected.siteIndex];const selectedForce=selected&&frame?.forces?.[selected.siteIndex];const cache=cacheRef.current?.snapshot();
  const ready = snapshot !== null && viewerState.status !== "loading";
  const timeUnit = trajectory.time.unit === "femtosecond" ? "fs" : trajectory.time.unit === "picosecond" ? "ps" : "";
  const kindLabel = {molecular_dynamics: "分子动力学", geometry_optimization: "结构优化", structure_sequence: "结构序列", unknown_static_sequence: "结构序列（类型未确定）"}[trajectory.kind];
  const supercellOptions = SUPERCELL_OPTIONS.map(size => ({size, unavailable: classifyTrajectoryViewer(trajectory, [size, size, size], mobile).mode === "refused"}));
  return <section ref={surfaceRef} className="viewer-renderer-surface trajectory-viewer-surface" data-testid="trajectory-viewer" aria-label="原子轨迹查看器" tabIndex={0} onKeyDown={keyDown}>
    <header className="trajectory-heading">
      <div><h2>原子轨迹</h2><p>{trajectory.atoms.count.toLocaleString("zh-CN")} 个原子 · {trajectory.frames.length.toLocaleString("zh-CN")} 帧 · {kindLabel}</p></div>
      <button type="button" className="product-secondary-action" disabled={!ready} onClick={() => engineRef.current?.fitCurrentScene()}>适配画面</button>
    </header>
    {trajectory.position_wrapping === "unknown" ? <p className="trajectory-reading-note" data-testid="trajectory-wrapping-warning">周期包裹状态未知，位置按源数据原样显示。</p> : null}
    {decision.mode === "degraded" ? <p className="trajectory-reading-note" data-testid="trajectory-degraded">数据量较大，已降低显示细节以保持播放流畅。</p> : null}
    <div ref={hostRef} className="viewer-renderer-canvas-host" data-testid="trajectory-canvas-host" aria-label="原子轨迹三维画面" aria-busy={!ready}>
      {!ready ? <span className="trajectory-loading" role="status">正在加载轨迹画面…</span> : null}
    </div>
    <div className="trajectory-playback-bar">
      <div className="trajectory-playback-actions">
        <button type="button" className="product-secondary-action" aria-label="上一帧" disabled={!ready || viewerState.currentFrameIndex === 0} onClick={() => seek(Math.max(0, viewerState.currentFrameIndex - 1))}>上一帧</button>
        <button type="button" className="product-primary-action" disabled={!ready} aria-label={viewerState.status === "playing" ? "暂停轨迹" : "播放轨迹"} onClick={togglePlay}>{viewerState.status === "playing" ? "暂停" : "播放"}</button>
        <button type="button" className="product-secondary-action" aria-label="下一帧" disabled={!ready || viewerState.currentFrameIndex === viewerState.frameCount - 1} onClick={() => seek(Math.min(viewerState.frameCount - 1, viewerState.currentFrameIndex + 1))}>下一帧</button>
      </div>
      <p className="trajectory-frame-status"><span>第 {viewerState.currentFrameIndex + 1} / {trajectory.frames.length} 帧</span>{frame?.time !== null && frame?.time !== undefined ? <span>{frame.time} {timeUnit}</span> : null}<span data-testid="trajectory-viewer-state">{!ready ? "正在加载" : viewerState.status === "playing" ? "播放中" : "已暂停"}</span></p>
    </div>
    <label className="trajectory-frame-control">帧 <input data-testid="trajectory-frame-slider" disabled={!ready} aria-valuetext={`第 ${viewerState.currentFrameIndex + 1} / ${trajectory.frames.length} 帧`} type="range" min={0} max={Math.max(0, trajectory.frames.length - 1)} value={viewerState.requestedFrameIndex} onChange={event => seek(Number(event.target.value))} /></label>
    <div className="trajectory-playback-options">
      <label>播放速度 <select disabled={!ready} data-testid="trajectory-playback-speed" value={viewerState.playbackSpeed} onChange={event => setViewerState(state => setTrajectorySpeed(state, Number(event.target.value)))}>{TRAJECTORY_PLAYBACK_SPEEDS.map(speed => <option key={speed} value={speed}>{speed} 倍</option>)}</select></label>
      <label className="trajectory-check"><input disabled={!ready} data-testid="trajectory-loop" type="checkbox" checked={viewerState.loop} onChange={event => setViewerState(state => Object.freeze({...state, loop: event.target.checked}))} />循环播放</label>
      <span>倍速仅改变回放速度。</span>
      {onPointSelection ? <button type="button" className="product-secondary-action" disabled={!ready || viewerState.isBuffering} onClick={() => {stopPlayback();onPointSelection({frameIndex:viewerState.currentFrameIndex,atom:null});}}>选择当前帧用于研究</button> : null}
    </div>
    {onPointSelection ? <p className="trajectory-reading-note">点击原子查看位置；聚焦查看器后按 N 逐个选择，Esc 清除检查。</p> : null}
    {externalPoint && onPointSelection ? <div className="trajectory-selected-summary" data-testid="trajectory-research-selection"><strong>已选 {trajectoryPointLabel(externalPoint)}</strong><button type="button" className="product-secondary-action" onClick={() => onPointSelection(null)}>清除研究选择</button></div> : null}
    {selectionRestoreWarning ? <p className="trajectory-reading-note" role="status">所选周期位置超出当前显示范围；研究选择仍保留，画面显示原始晶胞。</p> : null}
    {selectedAtom ? <div className="trajectory-selected-summary" aria-live="polite"><strong>{selectedAtom.species} · 原子 {selectedAtom.siteIndex + 1}</strong><span data-testid="trajectory-selected-atom">[{selectedAtom.position.map(formatNumber).join(", ")}] Å{selectedAtom.ref.imageOffset.some(value => value !== 0) ? ` · 周期位置 [${selectedAtom.ref.imageOffset.join(", ")}]` : ""}</span>{onPointSelection && selectionMode === "inspect" ? <button type="button" className="product-secondary-action" disabled={!ready || viewerState.isBuffering} onClick={() => {stopPlayback();onPointSelection({frameIndex:viewerState.currentFrameIndex,atom:selectedAtom.ref});}}>选择此原子用于研究</button> : null}</div> : null}
    {measurement ? <output className="trajectory-measurement" data-testid="trajectory-measurement">{measurement.ok ? `${formatMeasurement(measurement.result.value)} ${measurement.result.unit === "angstrom" ? "Å" : "°"} · 第 ${viewerState.currentFrameIndex + 1} 帧` : measurement.error}</output> : null}
    <details className="trajectory-details"><summary>测量与显示</summary>
      <div className="trajectory-options-grid">
        <fieldset disabled={!ready}><legend>测量当前帧</legend><div className="trajectory-mode-actions">{(["inspect", "distance", "angle", "dihedral"] as const).map(mode => <button type="button" className="product-secondary-action" key={mode} aria-pressed={selectionMode === mode} onClick={() => setMode(mode)}>{{inspect: "检查", distance: "距离", angle: "角度", dihedral: "二面角"}[mode]}</button>)}<button type="button" className="product-secondary-action" disabled={!selectedRefs.length} onClick={() => {setSelectedRefs(Object.freeze([])); setMeasurement(null);}}>清除选择</button></div><p className="trajectory-reading-note">{selectionMode === "inspect" ? "点击画面中的原子查看位置。" : `依次选择 ${limits[selectionMode]} 个原子，测量当前帧。切换帧后会清除测量。`}</p></fieldset>
        <fieldset disabled={!ready}><legend>显示设置</legend><label>超胞 <select data-testid="trajectory-supercell" value={repeat.join("x")} onChange={event => {const value=event.target.value.split("x").map(Number) as unknown as ImageOffset; if(classifyTrajectoryViewer(trajectory,value,mobile).mode === "refused")return; stopPlayback(); setRepeat(Object.freeze(value)); setSelectedRefs(Object.freeze([])); setMeasurement(null);}}>{supercellOptions.map(({size, unavailable}) => <option key={size} value={`${size}x${size}x${size}`} disabled={unavailable}>{size} × {size} × {size}{unavailable ? "（超出显示上限）" : ""}</option>)}</select></label>
          {supercellOptions.some(option => option.unavailable) ? <p className="trajectory-reading-note">较大的超胞超出当前设备显示上限，已停用。</p> : null}
          <div className="trajectory-display-toggles"><label className="trajectory-check"><input type="checkbox" checked={showCell} onChange={event => {setShowCell(event.target.checked); engineRef.current?.setCellVisible(event.target.checked);}} />晶胞</label><label className="trajectory-check"><input type="checkbox" checked={clipEnabled} onChange={event => {setClipEnabled(event.target.checked); if(mapped)engineRef.current?.setClipState(event.target.checked ? Object.freeze({...initialViewerClipState(mapped.scene), enabled:true}) : initialViewerClipState(mapped.scene));}} />裁剪</label></div>
        </fieldset>
      </div>
      {selectedVelocity ? <p data-testid="trajectory-selected-velocity">速度 [{selectedVelocity.map(formatNumber).join(", ")}] Å/飞秒</p> : null}
      {selectedForce ? <p data-testid="trajectory-selected-force">力 [{selectedForce.map(formatNumber).join(", ")}] eV/Å</p> : null}
    </details>
    <details className="trajectory-details"><summary>数据与来源</summary>
      <dl className="trajectory-source-properties"><dt>轨迹类型</dt><dd>{kindLabel}</dd><dt>晶格</dt><dd>{trajectory.lattice_mode === "fixed" ? "固定晶格" : "随帧变化"}</dd><dt>坐标</dt><dd>{trajectory.coordinate_mode === "cartesian" ? "笛卡尔坐标" : "分数坐标"}</dd><dt>周期包裹</dt><dd>{{wrapped:"已包裹", unwrapped:"未包裹，原子可能位于显示晶胞之外", unknown:"未确定"}[trajectory.position_wrapping]}</dd>
        {frame?.step !== null && frame?.step !== undefined ? <><dt>当前步数</dt><dd>{frame.step}</dd></> : null}
        {frame?.energy ? <><dt>{frame.energy.potential !== null ? "当前势能" : "当前总能量"}</dt><dd>{frame.energy.potential ?? frame.energy.total ?? "未提供"} eV</dd></> : null}
        {frame?.temperature !== null && frame?.temperature !== undefined ? <><dt>当前温度</dt><dd>{frame.temperature} K</dd></> : null}
      </dl>
      <p className="trajectory-reading-note" data-testid="trajectory-viewer-capability-truth">显示源数据中的原子位置；测量仅针对当前帧。动态键合、系综分析、编辑和视频导出暂不可用。</p>
      <details><summary>技术来源</summary><p data-testid="trajectory-viewer-product-identity">{toolId === "structure.trajectory_viewer" ? "正式轨迹查看器" : toolId === "structure.trajectory_import" ? "导入轨迹回放" : "已验证轨迹回放"}</p><p data-testid="trajectory-performance-tier">显示模式：{decision.mode === "degraded" ? "降低细节" : "标准"}</p><pre>{JSON.stringify(trajectoryFallbackSummary(payload), null, 2)}</pre></details>
    </details>
    <pre data-testid="trajectory-viewer-metrics" hidden>{JSON.stringify({trajectory:{id:trajectory.trajectory_id,schema:trajectory.schema_version,kind:trajectory.kind,frames:trajectory.frames.length,atoms:trajectory.atoms.count,coordinateMode:trajectory.coordinate_mode,wrapping:trajectory.position_wrapping,latticeMode:trajectory.lattice_mode},viewer:{toolId,currentFrame:viewerState.currentFrameIndex,requestedFrame:viewerState.requestedFrameIndex,status:viewerState.status,tier:decision.mode,speed:viewerState.playbackSpeed,loop:viewerState.loop,mobile,maxPlaybackFps:decision?.maxPlaybackFps,cache,pendingRequests:mappingScheduledRef.current?1:0,peakPendingRequests:peakPendingRef.current,maxPendingRequests:decision.maxPendingRequests,prefetchRequests:0,displayedInstances:decision?.displayedInstances,coordinateValues:decision.coordinateValues,activeLoops:playbackTimerRef.current?1:0,canvasCount:snapshot?.canvasCount??0,contextCount:snapshot?1:0,drawCalls:snapshot?.metrics.drawCalls??0,geometries:snapshot?.metrics.geometries??0,materials:snapshot?.metrics.materials??0,textures:snapshot?.metrics.textures??0,programs:snapshot?.metrics.programs??0},timing:{frameMapMs:mapped?.mapMs??0,gpuUpdateMs:snapshot?.metrics.lastDynamicUpdateMs??0}})}</pre>
    <p className="sr-only" aria-live="polite" data-testid="trajectory-live-region">{announcement}</p>
  </section>;
}

function TrajectoryFallback({title, code, payload, onRetry, onReduceSupercell, frameIndex}: {title: string; code: string; payload: unknown; onRetry?: () => void; onReduceSupercell?: () => void; frameIndex?: number}) {
  const message = code === "TRAJECTORY_VIEWER_INITIALIZATION_TIMEOUT" ? "加载超过 10 秒。可以重试，或展开来源信息查看数据概况。"
    : code === "TRAJECTORY_VIEWER_BUDGET_EXCEEDED" ? onReduceSupercell ? "当前超胞超出显示上限，可以恢复原始晶胞继续查看。" : "数据量超出当前交互显示范围，来源信息仍可查看。"
    : code === "TRAJECTORY_VIEWER_UNSUPPORTED" ? "浏览器暂不支持所需的三维显示。可以重试检测，或查看来源信息。"
    : onRetry ? "轨迹画面未能完成显示，可以重新加载。" : "轨迹格式或数值未通过检查，请核对来源文件。";
  return <section className="viewer-renderer-fallback" data-testid="trajectory-viewer-fallback" role="alert"><h3>{title}</h3><span data-testid="trajectory-viewer-state" hidden>{code === "TRAJECTORY_VIEWER_CONTEXT_LOST" ? "context_lost" : "error"}</span><p>{message}</p>
    {frameIndex !== undefined ? <p>当前停在第 {frameIndex + 1} 帧。</p> : null}
    {onRetry ? <button type="button" className="product-secondary-action" onClick={onRetry}>重试渲染器</button> : null}
    {onReduceSupercell ? <button type="button" className="product-secondary-action" onClick={onReduceSupercell}>恢复原始晶胞</button> : null}
    <details><summary>来源信息与技术详情</summary><code>{code}</code><pre>{JSON.stringify(trajectoryFallbackSummary(payload), null, 2)}</pre></details>
  </section>;
}
function trajectoryFallbackSummary(payload:unknown){if(!payload||typeof payload!=="object"||Array.isArray(payload))return Object.freeze({artifact:"unavailable"});const value=payload as Record<string,unknown>;const atoms=value.atoms&&typeof value.atoms==="object"&&!Array.isArray(value.atoms)?value.atoms as Record<string,unknown>:null;return Object.freeze({schema_version:typeof value.schema_version==="string"?value.schema_version:null,trajectory_id:typeof value.trajectory_id==="string"?value.trajectory_id:null,frame_count:Array.isArray(value.frames)?value.frames.length:null,atom_count:typeof atoms?.count==="number"?atoms.count:null,provenance:value.provenance??null});}
function formatNumber(value:number){return Math.abs(value)>=1000||Math.abs(value)<0.001&&value!==0?value.toExponential(4):value.toFixed(4);}
