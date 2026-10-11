"use client";

import { useEffect, useRef, useState } from "react";
import type { PotentialProfile } from "./electrostaticPotentialProduct";
import { PROFILE_HEIGHT, potentialUnit, profileChart, profileNumber, profilePointAt, type ProfileWindow } from "./potential-profile-view";
import styles from "./VolumetricSurface.module.css";

type Props = { profile: PotentialProfile | null; selectedIndex: number | null; onSelect: (index: number | null) => void };
const PAGE_SIZE = 32;

export function PotentialProfilePanel({ profile, selectedIndex, onSelect }: Props) {
  const [window, setWindow] = useState<ProfileWindow>([0, 1]);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [page, setPage] = useState(0);
  const [width, setWidth] = useState(640);
  const host = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const element = host.current;
    if (!element) return;
    const resize = () => { const next = element.getBoundingClientRect().width; if (next > 0) setWidth(next); };
    resize();
    if (typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(resize);
    observer.observe(element);
    return () => observer.disconnect();
  }, []);
  const points = profile?.points ?? [];
  const chart = profileChart(points, window, width);
  const selected = points.find(point => point.index === selectedIndex);
  const inspected = points.find(point => point.index === hoveredIndex) ?? selected;
  const unit = potentialUnit(profile?.unit ?? "");
  const shifted = profile?.gauge !== "source_native";
  const pageCount = Math.max(1, Math.ceil(points.length / PAGE_SIZE));
  const currentPage = Math.min(page, pageCount - 1);
  useEffect(() => {
    if (!selected) return;
    setWindow(current => selected.fractional >= current[0] && selected.fractional <= current[1] ? current : [0, 1]);
    setPage(Math.floor(points.indexOf(selected) / PAGE_SIZE));
  }, [selectedIndex, profile?.fieldHash, profile?.axis]);

  function choose(index: number | null) { setHoveredIndex(null); onSelect(index); }
  function zoom() {
    if (chart.plotted.length <= 2) return;
    const center = selected && selected.fractional >= window[0] && selected.fractional <= window[1]
      ? selected.fractional : chart.plotted[Math.floor(chart.plotted.length / 2)].point.fractional;
    const span = (window[1] - window[0]) / 2;
    const start = Math.max(0, Math.min(1 - span, center - span / 2));
    setHoveredIndex(null); setWindow([start, start + span]);
  }
  function pan(direction: -1 | 1) {
    const span = window[1] - window[0];
    const start = Math.max(0, Math.min(1 - span, window[0] + direction * span / 4));
    setHoveredIndex(null); setWindow([start, start + span]);
  }

  return <section className={styles.profile} aria-label="势能平面平均剖面" data-testid="potential-profile-panel">
    <div className="viewer-renderer-toolbar"><strong>平面平均势</strong><div className="viewer-renderer-controls">
      <button type="button" onClick={zoom} disabled={chart.plotted.length <= 2}>放大剖面</button>
      <button type="button" onClick={() => pan(-1)} disabled={window[0] === 0}>左移</button>
      <button type="button" onClick={() => pan(1)} disabled={window[1] === 1}>右移</button>
      <button type="button" onClick={() => { setWindow([0, 1]); setHoveredIndex(null); }}>完整范围</button>
      <button type="button" onClick={() => choose(null)} disabled={selectedIndex === null}>清除平面</button>
    </div></div>
    {!profile ? <p role="status">正在计算平面平均势…</p> : null}
    <div ref={host} className={styles.profileChart}>
      <svg data-testid="potential-profile-chart" viewBox={`0 0 ${width} ${PROFILE_HEIGHT}`} height={PROFILE_HEIGHT}
        role="img" aria-label={`晶格轴 ${profile?.axis.slice(-1) ?? ""} 的平面平均势，单位 ${unit}；方向键选择平面，Home 和 End 跳到可见区间端点。`}
        tabIndex={0} onKeyDown={event => {
          if (!["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key) || !chart.plotted.length) return;
          event.preventDefault();
          const current = chart.plotted.findIndex(item => item.point.index === selectedIndex);
          const next = event.key === "Home" ? 0 : event.key === "End" ? chart.plotted.length - 1
            : current === -1 ? event.key === "ArrowLeft" ? chart.plotted.length - 1 : 0
              : Math.max(0, Math.min(chart.plotted.length - 1, current + (event.key === "ArrowRight" ? 1 : -1)));
          choose(chart.plotted[next].point.index);
        }} onPointerMove={event => setHoveredIndex(profilePointAt(chart, event.clientX, event.currentTarget.getBoundingClientRect())?.index ?? null)}
        onPointerLeave={() => setHoveredIndex(null)}
        onClick={event => { const point = profilePointAt(chart, event.clientX, event.currentTarget.getBoundingClientRect()); if (point) choose(point.index); }}>
        <text x={chart.left} y={15}>平均势（{unit}）</text>
        {chart.yTicks.map((tick, index) => <g key={index}><line x1={chart.left} x2={chart.right} y1={tick.position} y2={tick.position} /><text x={chart.left - 8} y={tick.position + 4} textAnchor="end">{profileNumber(tick.value)}</text></g>)}
        {chart.xTicks.map((tick, index) => <g key={index}><line x1={tick.position} x2={tick.position} y1={chart.bottom} y2={chart.bottom + 4} /><text x={tick.position} y={chart.bottom + 19} textAnchor={index === chart.xTicks.length - 1 ? "end" : "middle"}>{profileNumber(tick.value)}</text></g>)}
        <text x={(chart.left + chart.right) / 2} y={235} textAnchor="middle">沿晶格轴的路径长度（Å）</text>
        <polyline points={chart.plotted.map(item => `${item.x},${item.y}`).join(" ")} />
        {inspected && chart.plotted.some(item => item.point.index === inspected.index) ? <g className={styles.profileMarker}><line x1={chart.x(inspected.fractional)} x2={chart.x(inspected.fractional)} y1={chart.top} y2={chart.bottom} /><circle cx={chart.x(inspected.fractional)} cy={chart.y(inspected.displayedValue)} r={4} /></g> : null}
      </svg>
    </div>
    {inspected ? <p role="status" aria-live="polite" data-testid="potential-profile-selection">平面 {inspected.index} · 分数坐标 {inspected.fractional.toFixed(6)} · 路径 {inspected.pathLengthAngstrom.toFixed(6)} Å · 源值 {inspected.sourceValue} {unit}{shifted ? ` · 显示值 ${inspected.displayedValue} ${unit}` : ""}</p> : null}
    <div className={styles.details}>
      <details><summary>剖面数值 · {points.length} 点</summary>
        <div className={styles.profileTable} role="region" aria-label="剖面数值表" tabIndex={0}>
          <table><thead><tr><th>平面</th><th>分数坐标</th><th>路径（Å）</th><th>源值（{unit}）</th>{shifted ? <th>显示值（{unit}）</th> : null}<th>三维视图</th></tr></thead>
            <tbody>{points.slice(currentPage * PAGE_SIZE, (currentPage + 1) * PAGE_SIZE).map(point => <tr key={point.index} aria-selected={selectedIndex === point.index}><td>{point.index}</td><td>{point.fractional.toFixed(6)}</td><td>{point.pathLengthAngstrom.toFixed(6)}</td><td>{point.sourceValue}</td>{shifted ? <td>{point.displayedValue}</td> : null}<td><button type="button" aria-pressed={selectedIndex === point.index} onClick={() => choose(point.index)}>显示平面 {point.index}</button></td></tr>)}</tbody>
          </table>
        </div>
        {pageCount > 1 ? <nav className="viewer-renderer-controls" aria-label="剖面数值分页"><button type="button" disabled={currentPage === 0} onClick={() => setPage(value => value - 1)}>上一页</button><span>第 {currentPage + 1} / {pageCount} 页</span><button type="button" disabled={currentPage + 1 === pageCount} onClick={() => setPage(value => value + 1)}>下一页</button></nav> : null}
      </details>
      <details><summary>剖面方法与来源</summary><p>对另外两个晶格轴上的网格点取算术平均，未做平滑。路径长度沿晶格轴计算，并非切面法向距离。</p><dl className="mini-grid" data-testid="potential-profile-identity"><dt>方法</dt><dd>{profile?.formulaId ?? "等待中"}</dd><dt>字段校验值</dt><dd>{profile?.fieldHash ?? "等待中"}</dd><dt>剖面标识</dt><dd>{profile?.profileHash ?? "等待中"}</dd><dt>分数坐标范围</dt><dd>{window[0].toFixed(3)}–{window[1].toFixed(3)}</dd></dl></details>
    </div>
  </section>;
}
