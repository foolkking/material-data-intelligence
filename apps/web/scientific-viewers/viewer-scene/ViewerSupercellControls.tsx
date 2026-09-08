import { PERIODIC_DERIVED_CAPS, type SupercellEstimate, type SupercellRepeat } from "./viewerSceneSupercell";

export function ViewerSupercellControls({ draft, applied, estimate, onDraft, onApply, onReset, onPreset, onDownload }: Readonly<{ draft: readonly string[]; applied: SupercellRepeat; estimate: SupercellEstimate; onDraft: (axis: number, value: string) => void; onApply: () => void; onReset: () => void; onPreset: (value: SupercellRepeat) => void; onDownload: () => void }>) {
  return <fieldset className="viewer-supercell-controls" aria-label="受限超晶胞控制">
    <legend>超晶胞</legend>
    <div className="viewer-supercell-axis-inputs">{([0,1,2] as const).map((axis) => <label key={axis}>{["A 轴", "B 轴", "C 轴"][axis]}<input data-testid={`viewer-supercell-${["x","y","z"][axis]}`} inputMode="numeric" type="number" min="1" max="3" step="1" value={draft[axis]} aria-invalid={estimate.error ? true : undefined} onChange={(event) => onDraft(axis, event.target.value)} /></label>)}</div>
    <div className="viewer-supercell-presets" aria-label="超晶胞预设">{([[1,1,1],[2,1,1],[2,2,1],[2,2,2],[3,3,3]] as const).map((preset) => <button key={preset.join("x")} type="button" className="compact secondary" onClick={() => onPreset(preset)}>{preset.join(" × ")}</button>)}</div>
    <div className="viewer-supercell-actions"><button type="button" className="compact secondary" data-testid="viewer-supercell-apply" onClick={onApply} disabled={estimate.mode === "refused"}>应用</button><button type="button" className="compact secondary" data-testid="viewer-supercell-reset" onClick={onReset}>重置为 1 × 1 × 1</button><button type="button" className="compact secondary" data-testid="viewer-supercell-download" onClick={onDownload}>下载视图状态</button></div>
    <output role="status" aria-live="polite" data-testid="viewer-supercell-estimate">草稿 {draft.join(" × ")}：{estimate.totalCells} 个晶胞，{estimate.displayedAtoms} 个原子，{estimate.displayedBonds} 条键，模式：{estimate.mode}。</output>
    <output data-testid="viewer-supercell-status">已应用 {applied.join(" × ")}{estimate.error ? `；${estimate.error}：请求 ${estimate.displayedAtoms} 个位点和 ${estimate.displayedBonds} 条键，限制为 ${PERIODIC_DERIVED_CAPS.maxDisplayedSites} 个位点和 ${PERIODIC_DERIVED_CAPS.maxDisplayedBonds} 条键。` : ""}</output>
  </fieldset>;
}
