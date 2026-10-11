"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { POLYHEDRON_VIEWS, projectSavedPolyhedron, type PolyhedronFace, type PolyhedronVertex, type PolyhedronView } from "./localEnvironmentProjection";
import styles from "./LocalEnvironmentPolyhedra.module.css";

export function LocalEnvironmentPolyhedronView({ vertices, faces, selectedVertexId, selectedFaceId }: Readonly<{
  vertices: readonly PolyhedronVertex[];
  faces: readonly PolyhedronFace[];
  selectedVertexId?: string;
  selectedFaceId?: string;
}>) {
  const canvas = useRef<HTMLDivElement>(null);
  const drag = useRef<{ x: number; y: number; view: PolyhedronView; pointerId: number } | null>(null);
  const [size, setSize] = useState({ width: 640, height: 400 });
  const [view, setView] = useState<PolyhedronView>(POLYHEDRON_VIEWS.spatial);
  const [preset, setPreset] = useState<keyof typeof POLYHEDRON_VIEWS | null>("spatial");
  const [zoom, setZoom] = useState(1);
  useEffect(() => {
    const element = canvas.current;
    if (!element) return;
    const resize = () => {
      const { width, height } = element.getBoundingClientRect();
      if (width > 0 && height > 0) setSize((current) => current.width === width && current.height === height ? current : { width, height });
    };
    resize();
    if (typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(resize);
    observer.observe(element);
    return () => observer.disconnect();
  }, []);
  const projection = useMemo(() => projectSavedPolyhedron(vertices, faces, size.width, size.height, view, zoom), [vertices, faces, size, view, zoom]);
  const zoomBy = (delta: number) => setZoom((current) => Math.min(3, Math.max(.5, current + delta)));
  const reset = () => { setView(POLYHEDRON_VIEWS.spatial); setPreset("spatial"); setZoom(1); };
  return <figure className={styles.figure} aria-label="配位多面体">
    <div className={styles.toolbar}>
      <div className={styles.viewOptions} role="group" aria-label="投影视角">
        {([['spatial', '立体'], ['xy', 'XY'], ['xz', 'XZ'], ['yz', 'YZ']] as const).map(([key, label]) =>
          <button key={key} type="button" aria-pressed={preset === key} onClick={() => { setView(POLYHEDRON_VIEWS[key]); setPreset(key); setZoom(1); }}>{label}</button>)}
      </div>
      <div className={styles.zoom} role="group" aria-label="缩放视图">
        <button type="button" aria-label="缩小多面体" onClick={() => zoomBy(-.25)} disabled={zoom <= .5}>−</button>
        <button type="button" onClick={reset}>适配</button>
        <button type="button" aria-label="放大多面体" onClick={() => zoomBy(.25)} disabled={zoom >= 3}>＋</button>
      </div>
    </div>
    <div ref={canvas} className={styles.canvas} tabIndex={0} role="group" aria-label="多面体视图，方向键旋转，Home 适配"
      onKeyDown={(event) => {
        if (event.key === "Home") { event.preventDefault(); reset(); }
        else if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key)) {
          event.preventDefault(); setPreset(null);
          setView((current) => ({ yaw: current.yaw + (event.key === "ArrowLeft" ? -.18 : event.key === "ArrowRight" ? .18 : 0), pitch: current.pitch + (event.key === "ArrowUp" ? .18 : event.key === "ArrowDown" ? -.18 : 0) }));
        } else if (event.key === "+" || event.key === "=") { event.preventDefault(); zoomBy(.25); }
        else if (event.key === "-") { event.preventDefault(); zoomBy(-.25); }
      }}
      onPointerDown={(event) => {
        if (event.button !== 0) return;
        drag.current = { x: event.clientX, y: event.clientY, view, pointerId: event.pointerId };
        event.currentTarget.setPointerCapture(event.pointerId);
        event.currentTarget.focus({ preventScroll: true });
      }}
      onPointerMove={(event) => {
        const start = drag.current;
        if (!start || start.pointerId !== event.pointerId) return;
        setPreset(null);
        setView({ yaw: start.view.yaw + (event.clientX - start.x) * .008, pitch: start.view.pitch + (event.clientY - start.y) * .008 });
      }}
      onPointerUp={() => { drag.current = null; }} onPointerCancel={() => { drag.current = null; }} onLostPointerCapture={() => { drag.current = null; }}>
      <svg viewBox={`0 0 ${size.width} ${size.height}`} role="img" aria-label={`配位多面体，${vertices.length} 个近邻顶点，${faces.length} 个已保存三角面`}>
        {projection.polygons.map((face) => <polygon key={face.faceIdentity} className={styles.face} data-selected={selectedFaceId === face.faceIdentity}
          points={face.points.map((point) => `${point.x},${point.y}`).join(" ")} />)}
        {projection.points.map((point) => <line key={point.vertexIdentity} className={styles.relation} x1={projection.center.x} y1={projection.center.y} x2={point.x} y2={point.y} />)}
        {[...projection.points].sort((left, right) => left.depth - right.depth).map((point) => <g key={point.vertexIdentity}>
          <circle data-vertex-id={point.vertexIdentity} className={styles.vertex} data-selected={selectedVertexId === point.vertexIdentity} cx={point.x} cy={point.y} r={selectedVertexId === point.vertexIdentity ? 8 : 6} />
          {vertices.length <= 12 || selectedVertexId === point.vertexIdentity ? <text className={styles.pointLabel} x={point.x + 10} y={point.y - 9}>{point.index + 1}</text> : null}
        </g>)}
        <circle className={styles.center} cx={projection.center.x} cy={projection.center.y} r="8" />
        <text className={styles.pointLabel} x={projection.center.x + 12} y={projection.center.y + 20}>中心</text>
        <g transform={`translate(44 ${size.height - 44})`} aria-hidden="true">
          {projection.axes.map((axis) => <g key={axis.label}><line className={styles.axis} x1="0" y1="0" x2={axis.x} y2={axis.y} /><text className={styles.axisLabel} x={axis.x * 1.35} y={axis.y * 1.35 + 4} textAnchor="middle">{axis.label}</text></g>)}
        </g>
      </svg>
    </div>
    <figcaption className={styles.caption}><span>{vertices.length} 个近邻 · {faces.length} 个三角面</span><span>等比例正交投影</span></figcaption>
  </figure>;
}
