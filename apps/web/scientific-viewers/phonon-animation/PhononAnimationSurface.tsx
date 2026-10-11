"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import type { PeriodicSiteRef, RenderVector3, ViewerRendererEngine, ViewerRendererEngineFactory, ViewerRendererSnapshot } from "../viewer-scene/viewerSceneRendererTypes";
import { supportsManagedWebGL } from "../viewer-scene/viewerWebglCapability";
import { mapPhononAnimationFrame, validatePhononAnimationForViewer, type MappedPhononAnimation } from "./phononAnimationMapper";
import styles from "./PhononAnimationSurface.module.css";

const defaultEngineFactory:ViewerRendererEngineFactory=async(args)=>(await import("../viewer-scene/viewerSceneRendererEngine")).createThreeViewerEngine(args);
export type PhononAnimationSurfaceProps=Readonly<{payload:unknown;capabilityOverride?:boolean;reducedMotionOverride?:boolean;engineFactory?:ViewerRendererEngineFactory}>;

export function PhononAnimationSurface({payload,capabilityOverride,reducedMotionOverride,engineFactory=defaultEngineFactory}:PhononAnimationSurfaceProps){
  const validation=useMemo(()=>validatePhononAnimationForViewer(payload),[payload]);const animation=validation.ok?validation.package:null;
  const playback=animation?.playback as Record<string,any>|undefined;const display=animation?.display as Record<string,any>|undefined;
  const [phase,setPhase]=useState(()=>Number(playback?.initial_phase_radians??0));const [playing,setPlaying]=useState(false);const playingRef=useRef(false);playingRef.current=playing;
  const [speed,setSpeed]=useState(()=>Number(playback?.cycles_per_second??.5));const [scale,setScale]=useState(()=>Number(display?.display_scale??.15));
  const [showVectors,setShowVectors]=useState(()=>Boolean(display?.show_vectors??true));const [showTrails,setShowTrails]=useState(()=>Boolean(display?.show_trails??false));const [showBonds,setShowBonds]=useState(()=>Boolean(display?.show_bonds??true));const [showCell,setShowCell]=useState(()=>Boolean(display?.show_unit_cell??true));
  const [selected,setSelected]=useState<PeriodicSiteRef|null>(null);const [snapshot,setSnapshot]=useState<ViewerRendererSnapshot|null>(null);const [fallback,setFallback]=useState<string|null>(null);const [announcement,setAnnouncement]=useState("声子图正在准备。");const [attempt,setAttempt]=useState(0);
  const [reducedDetected,setReducedDetected]=useState(false);const reducedMotion=reducedMotionOverride??reducedDetected;
  const hostRef=useRef<HTMLDivElement>(null);const engineRef=useRef<ViewerRendererEngine|null>(null);const frameRef=useRef<number|null>(null);const lastTimeRef=useRef<number|null>(null);const disposedRef=useRef(false);const trailsRef=useRef<Map<string,RenderVector3[]>>(new Map());
  const mapped=useMemo(()=>animation?mapPhononAnimationFrame(animation,phase,scale):null,[animation,phase,scale]);const mappedRef=useRef<MappedPhononAnimation|null>(mapped);mappedRef.current=mapped;
  const stop=useCallback((message?:string)=>{playingRef.current=false;setPlaying(false);if(frameRef.current!==null){cancelAnimationFrame(frameRef.current);frameRef.current=null;}lastTimeRef.current=null;if(message)setAnnouncement(message);},[]);
  const onPick=useCallback((ref:PeriodicSiteRef|null)=>{if(playingRef.current)stop("已暂停播放，可查看所选原子。");setSelected(ref);},[stop]);

  useEffect(()=>{const query=window.matchMedia?.("(prefers-reduced-motion: reduce)");const update=()=>setReducedDetected(Boolean(query?.matches));update();query?.addEventListener?.("change",update);return()=>query?.removeEventListener?.("change",update);},[]);
  useEffect(()=>{if(reducedMotion&&playing)stop("已启用减少动态效果，播放已暂停。");},[playing,reducedMotion,stop]);
  useEffect(()=>{const visibility=()=>{if(document.hidden)stop("页面隐藏，播放已暂停。");};document.addEventListener("visibilitychange",visibility);return()=>document.removeEventListener("visibilitychange",visibility);},[stop]);

  useEffect(()=>{disposedRef.current=false;stop();engineRef.current?.dispose();engineRef.current=null;setSnapshot(null);setFallback(null);setSelected(null);trailsRef.current.clear();if(!animation||!mapped)return()=>{disposedRef.current=true;};const supported=capabilityOverride??supportsManagedWebGL();const host=hostRef.current;if(!supported||!host){setFallback(supported?"PHONON_ANIMATION_INITIALIZATION_FAILED":"PHONON_ANIMATION_WEBGL_UNSUPPORTED");return()=>{disposedRef.current=true;};}let cancelled=false;void engineFactory({container:host,scene:mapped.scene,pixelRatioCap:2,antialias:true,performanceTier:"interactive",onContextLost:()=>{stop();engineRef.current?.dispose();engineRef.current=null;setFallback("PHONON_ANIMATION_CONTEXT_LOST");setAnnouncement("图形上下文已丢失，播放已停止；原始数据仍可查看。");},onSitePick:onPick,onViewChange:()=>setSnapshot(engineRef.current?.snapshot()??null)}).then((engine)=>{if(cancelled){engine.dispose();return;}engineRef.current=engine;engine.setCellVisible(showCell);engine.setSupercellBoundaryVisible(true);engine.setLatticeAxesVisible(Boolean(display?.show_axes));engine.setBondsVisible(showBonds);engine.setDisplacementVectors(showVectors?mapped.vectors:[]);setSnapshot(engine.snapshot());setAnnouncement("声子模式已加载，播放已暂停。");}).catch(()=>{if(!cancelled)setFallback("PHONON_ANIMATION_INITIALIZATION_FAILED");});return()=>{cancelled=true;disposedRef.current=true;stop();engineRef.current?.dispose();engineRef.current=null;trailsRef.current.clear();};},[animation?.mode?.mode?.mode_id,attempt,capabilityOverride,engineFactory,onPick,stop]);

  useEffect(()=>{const engine=engineRef.current;if(!engine||!mapped)return;try{engine.updateDynamicScene(mapped.scene);engine.setBondsVisible(showBonds);engine.setCellVisible(showCell);engine.setDisplacementVectors(showVectors?mapped.vectors:[]);if(showTrails){mapped.scene.atoms.forEach((atom)=>{const key=atom.id;const path=trailsRef.current.get(key)??[];path.push(atom.position);if(path.length>Number(display?.trail_length??12))path.shift();trailsRef.current.set(key,path);});engine.setDisplacementTrails([...trailsRef.current.values()]);}else{trailsRef.current.clear();engine.setDisplacementTrails([]);}engine.setSelection(selected ? [selected] : []);setSnapshot(engine.snapshot());}catch{stop();setFallback("PHONON_ANIMATION_FRAME_UPDATE_FAILED");}},[mapped,selected,showBonds,showCell,showTrails,showVectors,display?.trail_length,stop]);

  useEffect(()=>{if(!playing||reducedMotion)return;const tick=(time:number)=>{if(disposedRef.current||!playingRef.current)return;const previous=lastTimeRef.current??time;lastTimeRef.current=time;const delta=Math.min(time-previous,100);setPhase((value)=>(value+delta/1000*speed*2*Math.PI)%(2*Math.PI));frameRef.current=requestAnimationFrame(tick);};frameRef.current=requestAnimationFrame(tick);return()=>{if(frameRef.current!==null){cancelAnimationFrame(frameRef.current);frameRef.current=null;}lastTimeRef.current=null;};},[playing,reducedMotion,speed]);

  if(!validation.ok)return <Fallback code={validation.errors[0]??"PHONON_ANIMATION_ARTIFACT_INVALID"} payload={payload}/>;if(!animation||!mapped)return <Fallback code="PHONON_ANIMATION_ARTIFACT_INVALID" payload={payload}/>;if(fallback)return <Fallback code={fallback} payload={payload} retry={()=>{setFallback(null);setAttempt((value)=>value+1);}}/>;
  const mode=animation.mode.mode as Record<string,any>;const imaginary=Boolean(animation.mode.provenance.imaginary_mode);const selectedAtom=selected?mapped.scene.atoms.find((atom)=>atom.siteIndex===selected.siteIndex&&atom.ref.imageOffset.every((value,index)=>value===selected.imageOffset[index])):null;const displacement=selectedAtom?[selectedAtom.position[0]-selectedAtom.canonicalPosition[0],selectedAtom.position[1]-selectedAtom.canonicalPosition[1],selectedAtom.position[2]-selectedAtom.canonicalPosition[2]]:null;
  const togglePlay=()=>{if(playing){stop("声子动画已暂停。");return;}if(reducedMotion){setAnnouncement("已启用减少动态效果，请调节相位查看静态构型。");return;}setSelected(null);setPlaying(true);setAnnouncement("声子动画播放中，显示幅度仅用于示意。");};
  const ready = snapshot !== null;
  return <section className={`viewer-renderer-surface phonon-animation-surface ${styles.surface}`} data-testid="phonon-animation-viewer" aria-label="声子振动查看器" tabIndex={0}>
    <header className={styles.heading}>
      <div><h3>声子振动</h3><p>q 点 {mode.qpoint_index} · 分支 {mode.branch_index} · {mode.frequency} {mode.frequency_unit === "terahertz" ? "THz" : mode.frequency_unit}</p></div>
      <span data-testid="phonon-animation-state">{!ready ? "正在加载" : playing ? "播放中" : "已暂停"}</span>
    </header>
    {imaginary ? <p className={styles.warning} data-testid="phonon-imaginary-warning">虚频模式：画面仅示意不稳定方向，不代表稳定的时间振动。</p> : null}
    {mode.degeneracy ? <p className={styles.warning} data-testid="phonon-degenerate-warning">显示的是源数据给出的简并基组，简并子空间内的基组选择并不唯一。</p> : null}
    {reducedMotion ? <p className={styles.note} data-testid="phonon-reduced-motion">已启用减少动态效果，可调节相位查看静态构型。</p> : null}
    <div className={styles.playback}>
      <button type="button" className="product-primary-action" disabled={!ready} aria-label={playing ? "暂停声子动画" : "播放声子动画"} onClick={togglePlay}>{playing ? "暂停" : "播放"}</button>
      <label className={styles.phase}>相位<input data-testid="phonon-phase-slider" disabled={!ready} type="range" min={0} max={2 * Math.PI} step={.01} value={phase} aria-valuetext={`${phase.toFixed(2)} 弧度`} onChange={event => { stop(); setPhase(Number(event.target.value)); }} /></label>
      <output data-testid="phonon-phase-value">{phase.toFixed(3)} rad</output>
      <button type="button" className="product-secondary-action" disabled={!ready} onClick={() => { stop(); setPhase(0); }}>重置相位</button>
      <button type="button" className="product-secondary-action" disabled={!ready} onClick={() => engineRef.current?.resetCamera()}>适配画面</button>
    </div>
    <p className={styles.note} data-testid="phonon-display-scale-warning">显示幅度仅用于示意，不代表实测振幅。</p>
    <div ref={hostRef} className={`viewer-renderer-canvas-host ${styles.canvas}`} data-testid="phonon-animation-canvas-host" aria-label="声子振动三维画面" aria-busy={!ready}>
      {!ready ? <span className={styles.loading} role="status">正在加载声子图…</span> : null}
    </div>
    <details className={styles.details}><summary>显示与播放设置</summary>
      <div className={styles.settings}>
        <label>播放速度 <span><input data-testid="phonon-speed" disabled={!ready} type="range" min={.05} max={2} step={.05} value={speed} aria-valuetext={`每秒 ${speed.toFixed(2)} 次循环`} onChange={event => setSpeed(Number(event.target.value))} /><output>{speed.toFixed(2)} 次/秒</output></span></label>
        <label>显示幅度（Å）<span><input data-testid="phonon-display-scale" disabled={!ready} type="range" min={.01} max={1} step={.01} value={scale} aria-valuetext={`${scale.toFixed(2)} 埃，仅用于示意`} onChange={event => setScale(Number(event.target.value))} /><output>{scale.toFixed(2)}</output></span></label>
        <div className={styles.toggles} role="group" aria-label="显示内容">
          <label><input type="checkbox" disabled={!ready} checked={showVectors} onChange={event => setShowVectors(event.target.checked)} />位移向量</label>
          <label><input type="checkbox" disabled={!ready} checked={showTrails} onChange={event => setShowTrails(event.target.checked)} />运动轨迹</label>
          <label><input type="checkbox" disabled={!ready} checked={showBonds} onChange={event => setShowBonds(event.target.checked)} />化学键</label>
          <label><input type="checkbox" disabled={!ready} checked={showCell} onChange={event => setShowCell(event.target.checked)} />晶胞</label>
        </div>
      </div>
    </details>
    {selectedAtom && displacement ? <section className={styles.inspector} data-testid="phonon-animation-inspector" aria-label="所选原子">
      <header><strong data-testid="phonon-selected-atom">{selectedAtom.species} · 原子 {selectedAtom.siteIndex} · 周期位置 [{selectedAtom.ref.imageOffset.join(", ")}]</strong><button type="button" className="product-secondary-action" onClick={() => setSelected(null)}>清除选择</button></header>
      <dl data-testid="phonon-selected-displacement"><dt>参考位置（Å）</dt><dd>[{selectedAtom.canonicalPosition.map(fmt).join(", ")}]</dd><dt>当前位置（Å）</dt><dd>[{selectedAtom.position.map(fmt).join(", ")}]</dd><dt>示意位移（Å）</dt><dd>[{displacement.map(fmt).join(", ")}]</dd></dl>
    </section> : null}
    <details className={styles.details}><summary>模式数据</summary><dl className={styles.metadata}><dt>q 点坐标</dt><dd>[{mode.qpoint_coordinates.join(", ")}]</dd><dt>超胞</dt><dd>{animation.supercell.repeat.join(" × ")}</dd><dt>模式标识</dt><dd>{mode.mode_id}</dd></dl></details>
    <pre hidden data-testid="phonon-animation-metrics">{JSON.stringify({modeId:mode.mode_id,phase,scale,playing,reducedMotion,supercell:animation.supercell.repeat,atomCount:mapped.scene.atoms.length,vectorCount:showVectors?mapped.vectors.length:0,trailPaths:showTrails?trailsRef.current.size:0,canvasCount:snapshot?.canvasCount??0,contextCount:snapshot?1:0,activeLoops:frameRef.current===null?0:1,drawCalls:snapshot?.metrics.drawCalls??0,mapMs:mapped.mapMs})}</pre><p className="sr-only" aria-live="polite" data-testid="phonon-animation-live-region">{announcement}</p>
  </section>;
}
function Fallback({code,payload,retry}:{code:string;payload:unknown;retry?:()=>void}){return <section className="viewer-renderer-fallback" data-testid="phonon-animation-fallback" role="status"><h3>声子动画暂不可用</h3><code>{code}</code><p>图形加载或播放已停止，原始结果仍可查看。</p>{retry?<button type="button" onClick={retry}>重试查看器</button>:null}<details><summary>模式数据摘要</summary><pre>{JSON.stringify(summary(payload),null,2)}</pre></details></section>;}
function summary(payload:unknown){if(!payload||typeof payload!=="object"||Array.isArray(payload))return{schema_version:null};const value=payload as Record<string,any>;return{schema_version:value.schema_version??null,mode_id:value.mode?.mode?.mode_id??null,full_json_available_in_preview:true};}
function fmt(value:number){return Math.abs(value)<.0001&&value!==0?value.toExponential(3):value.toFixed(4);}
