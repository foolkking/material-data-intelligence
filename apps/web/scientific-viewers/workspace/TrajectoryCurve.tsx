"use client";

import { useEffect, useRef, useState } from "react";
import styles from "./TrajectoryAnalytics.module.css";

export type TrajectorySeries = { label: string; values: number[] };
const COLORS = ["#08756c", "#b34c39", "#355b99", "#755398"];
const number = (value: number) => Number(value.toPrecision(4)).toString();

/** Scale saved coordinates only. No fitting, smoothing or scientific resampling. */
export function TrajectoryCurve({ x, series, xLabel, yLabel, label }: {
  x: number[]; series: TrajectorySeries[]; xLabel: string; yLabel: string; label: string;
}) {
  const host = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(640);
  useEffect(() => {
    const element = host.current;
    if (!element) return;
    const resize = () => { if (element.clientWidth > 0) setWidth(Math.max(220, element.clientWidth)); };
    resize();
    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(resize);
    observer?.observe(element);
    return () => observer?.disconnect();
  }, []);
  const xmin = Math.min(...x), xmax = Math.max(...x);
  let ymin = Infinity, ymax = -Infinity;
  for (const curve of series) for (const value of curve.values) { ymin = Math.min(ymin, value); ymax = Math.max(ymax, value); }
  const left = width < 420 ? 62 : 72, right = width - 16, top = 32, bottom = 272;
  const domainX = xmin === xmax ? [xmin - 1, xmax + 1] : [xmin, xmax];
  const domainY = ymin === ymax ? [ymin - 1, ymax + 1] : [Math.min(0, ymin), ymax];
  const sx = (value: number) => left + (value - domainX[0]) / (domainX[1] - domainX[0]) * (right - left);
  const sy = (value: number) => bottom - (value - domainY[0]) / (domainY[1] - domainY[0]) * (bottom - top);
  const ticks = (domain: number[], count: number) => Array.from({ length: count }, (_, i) => domain[0] + (domain[1] - domain[0]) * i / (count - 1));
  return <div ref={host} className={styles.curve}>
    <svg viewBox={`0 0 ${width} 328`} role="img" aria-label={label}>
      <title>{label}</title>
      <text x={left} y={16}>{yLabel}</text>
      {ticks(domainY, 5).map(value => <g key={value}>
        <line x1={left} x2={right} y1={sy(value)} y2={sy(value)} className={styles.grid} />
        <text x={left - 8} y={sy(value) + 4} textAnchor="end">{number(value)}</text>
      </g>)}
      {ticks(domainX, width < 420 ? 3 : 5).map((value, i, values) => <g key={value}>
        <line x1={sx(value)} x2={sx(value)} y1={bottom} y2={bottom + 5} className={styles.axis} />
        <text x={sx(value)} y={bottom + 22} textAnchor={i === 0 ? "start" : i === values.length - 1 ? "end" : "middle"}>{number(value)}</text>
      </g>)}
      <path d={`M${left} ${top}V${bottom}H${right}`} fill="none" stroke="currentColor" className={styles.axis} />
      {series.map((curve, index) => x.length === 1
        ? <circle key={curve.label} cx={sx(x[0])} cy={sy(curve.values[0])} r={3} fill={COLORS[index % COLORS.length]}><title>{curve.label}</title></circle>
        : <polyline key={curve.label} fill="none" stroke={COLORS[index % COLORS.length]} strokeWidth={index === 0 ? 2 : 1.6}
          strokeDasharray={index === 0 ? undefined : index === 1 ? "6 3" : index === 2 ? "2 3" : "8 3 2 3"}
          strokeLinejoin="round" data-point-count={x.length}
          points={x.map((value, i) => `${sx(value)},${sy(curve.values[i])}`).join(" ")}><title>{curve.label}</title></polyline>)}
      <text x={(left + right) / 2} y={316} textAnchor="middle">{xLabel}</text>
    </svg>
    <ul className={styles.legend} aria-label="曲线图例">{series.map((curve, i) => <li key={curve.label}>
      <span aria-hidden="true" style={{ borderColor: COLORS[i % COLORS.length], borderTopStyle: i ? "dashed" : "solid" }} />{curve.label}
    </li>)}</ul>
  </div>;
}
