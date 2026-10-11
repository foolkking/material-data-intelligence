"use client";

import { useLayoutEffect, useRef, useState } from "react";

import { layoutBrillouinZoneLabels } from "./brillouinZoneLabelLayout";
import styles from "./BrillouinZoneSurface.module.css";

type LabelPoint = Readonly<{ id: string; x: number; y: number; text: string }>;

export function BrillouinZoneLabels({ points, selectedId, onSelect }: {
  points: readonly LabelPoint[];
  selectedId?: string;
  onSelect: (id: string) => void;
}) {
  const rootRef = useRef<HTMLDivElement>(null);
  const buttonsRef = useRef(new Map<string, HTMLButtonElement>());
  const [measurements, setMeasurements] = useState({ width: 0, height: 0, labels: new Map<string, { width: number; height: number }>() });
  const contentKey = JSON.stringify(points.map(point => [point.id, point.text]));
  useLayoutEffect(() => {
    const root = rootRef.current;
    if (!root) return;
    const measure = () => {
      const labels = new Map([...buttonsRef.current].map(([id, element]) => [id, { width: element.offsetWidth, height: element.offsetHeight }]));
      setMeasurements({ width: root.clientWidth, height: root.clientHeight, labels });
    };
    measure();
    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(measure);
    observer?.observe(root);
    for (const button of buttonsRef.current.values()) observer?.observe(button);
    return () => observer?.disconnect();
  }, [contentKey]);

  const { placed, overflow } = layoutBrillouinZoneLabels(points.map(point => ({ ...point, width: measurements.labels.get(point.id)?.width || 44, height: measurements.labels.get(point.id)?.height || 44 })), measurements.width, measurements.height);
  const placements = new Map(placed.map(point => [point.id, point]));
  return <div ref={rootRef} className={styles.labelLayer} role="group" aria-label="图中高对称点">
    <svg className={styles.labelLeaders} aria-hidden="true">
      {placed.map(point => <g key={point.id}>
        <line x1={point.x} y1={point.y} x2={point.left + point.width / 2} y2={point.top + point.height / 2} />
        <circle cx={point.x} cy={point.y} r="2.5" />
      </g>)}
    </svg>
    {points.map(point => {
      const position = placements.get(point.id);
      return <button key={point.id} ref={element => { if (element) buttonsRef.current.set(point.id, element); else buttonsRef.current.delete(point.id); }}
        type="button" className={styles.pointLabel} title={point.text} aria-pressed={selectedId === point.id}
        aria-hidden={!position} tabIndex={position ? 0 : -1}
        style={{ left: position?.left ?? 0, top: position?.top ?? 0, visibility: position ? "visible" : "hidden" }}
        onClick={() => onSelect(point.id)}><span>{point.text}</span></button>;
    })}
    {overflow.length ? <details className={styles.labelOverflow}><summary>更多高对称点 · {overflow.length}</summary>
      <div>{points.filter(point => overflow.includes(point.id)).map(point => <button key={point.id} type="button" aria-pressed={selectedId === point.id} onClick={() => onSelect(point.id)}>{point.text}</button>)}</div>
    </details> : null}
  </div>;
}
