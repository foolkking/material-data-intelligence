"use client";

import { useEffect, useRef, useState } from "react";
import { electronicNumber, electronicSpinLabel, type ElectronicPlotData } from "./electronic-plot";

const COLORS = ["#176b87", "#b42318", "#627d32", "#7a5ca8", "#a26a00", "#2f6f6d"];

export function ElectronicPlot({ data, kind, dosUnit }: { data: ElectronicPlotData; kind: "band" | "dos"; dosUnit?: string }) {
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
  const left = 58, right = width - 18, top = 32, bottom = 268;
  const scaleX = (value: number) => left + (value - data.xDomain[0]) / (data.xDomain[1] - data.xDomain[0]) * (right - left);
  const scaleY = (value: number) => bottom - (value - data.yDomain[0]) / (data.yDomain[1] - data.yDomain[0]) * (bottom - top);
  const ticks = (domain: [number, number], count = 5) => Array.from({ length: count }, (_, i) => domain[0] + (domain[1] - domain[0]) * i / (count - 1));
  const customTicks = data.ticks.length > 0 && data.ticks.length <= (width < 420 ? 4 : 8);
  const xTicks = customTicks ? data.ticks : ticks(data.xDomain, width < 420 ? 3 : 5).map(value => ({ value, label: electronicNumber(value) }));
  const color = (index: number) => kind === "band" ? data.curves[index].spin === "down" ? COLORS[1] : COLORS[0] : COLORS[index % COLORS.length];
  const legend = kind === "band" ? [...new Set(data.curves.map(curve => curve.spin))].map(spin => ({ label: electronicSpinLabel(spin), color: spin === "down" ? COLORS[1] : COLORS[0], dashed: spin === "down" })) : data.curves.map((curve, index) => ({ label: curve.label, color: color(index), dashed: curve.spin === "down" }));
  return <div ref={host} className="electronic-plot">
    <svg viewBox={`0 0 ${width} 324`} role="img" aria-label={kind === "band" ? "电子能带：倒易路径与能量" : "电子态密度：能量与态密度"} data-testid={`electronic-${kind}-plot`}>
      <title>{kind === "band" ? "电子能带，按源文件路径距离显示，断点不连线" : "电子态密度，按源文件能量坐标显示"}</title>
      <text x={left} y={16} className="electronic-axis-title">{kind === "band" ? "能量（eV）" : dosUnit || "态密度"}</text>
      {ticks(data.yDomain).map(value => <g key={value}><line x1={left} x2={right} y1={scaleY(value)} y2={scaleY(value)} className="electronic-grid-line" /><text x={left - 10} y={scaleY(value) + 4} textAnchor="end">{electronicNumber(value)}</text></g>)}
      {xTicks.map(({ value, label }, index) => <g key={`${value}:${label}`}><line x1={scaleX(value)} x2={scaleX(value)} y1={top} y2={bottom} className="electronic-grid-line" /><text x={scaleX(value)} y={bottom + 22} textAnchor={index === 0 ? "start" : index === xTicks.length - 1 ? "end" : "middle"}>{label}</text></g>)}
      <path d={`M${left} ${top}V${bottom}H${right}`} className="electronic-axis-line" />
      {data.curves.map((curve, index) => curve.segments.map((points, segment) => points.length === 1
        ? <circle key={`${curve.id}:${segment}`} cx={scaleX(points[0][0])} cy={scaleY(points[0][1])} r={2.5} fill={color(index)}><title>{curve.label}</title></circle>
        : <polyline key={`${curve.id}:${segment}`} fill="none" stroke={color(index)} strokeDasharray={curve.spin === "down" ? "5 4" : undefined} strokeWidth="1.6" strokeLinejoin="round" points={points.map(([x, y]) => `${scaleX(x)},${scaleY(y)}`).join(" ")}><title>{curve.label}</title></polyline>))}
      <text x={(left + right) / 2} y={314} textAnchor="middle" className="electronic-axis-title">{kind === "band" ? "倒易路径（源文件距离）" : "能量（eV）"}</text>
    </svg>
    <ul className="electronic-legend" aria-label="曲线图例">{legend.map((item, index) => <li key={`${item.label}:${index}`}><span aria-hidden="true" style={{ borderColor: item.color, borderTopStyle: item.dashed ? "dashed" : "solid" }} />{item.label}</li>)}</ul>
  </div>;
}
