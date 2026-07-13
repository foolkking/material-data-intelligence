import { PERIODIC_DERIVED_CAPS, type SupercellEstimate, type SupercellRepeat } from "./viewerSceneSupercell";

export function ViewerSupercellControls({ draft, applied, estimate, onDraft, onApply, onReset, onPreset, onDownload }: Readonly<{ draft: readonly string[]; applied: SupercellRepeat; estimate: SupercellEstimate; onDraft: (axis: number, value: string) => void; onApply: () => void; onReset: () => void; onPreset: (value: SupercellRepeat) => void; onDownload: () => void }>) {
  return <fieldset className="viewer-supercell-controls" aria-label="Bounded supercell controls">
    <legend>Renderer-local supercell</legend>
    <div className="viewer-supercell-axis-inputs">{([0,1,2] as const).map((axis) => <label key={axis}>{["A axis", "B axis", "C axis"][axis]}<input data-testid={`viewer-supercell-${["x","y","z"][axis]}`} inputMode="numeric" type="number" min="1" max="3" step="1" value={draft[axis]} aria-invalid={estimate.error ? true : undefined} onChange={(event) => onDraft(axis, event.target.value)} /></label>)}</div>
    <div className="viewer-supercell-presets" aria-label="Supercell presets">{([[1,1,1],[2,1,1],[2,2,1],[2,2,2],[3,3,3]] as const).map((preset) => <button key={preset.join("x")} type="button" className="compact secondary" onClick={() => onPreset(preset)}>{preset.join(" x ")}</button>)}</div>
    <div className="viewer-supercell-actions"><button type="button" className="compact secondary" data-testid="viewer-supercell-apply" onClick={onApply} disabled={estimate.mode === "refused"}>Apply</button><button type="button" className="compact secondary" data-testid="viewer-supercell-reset" onClick={onReset}>Reset 1 x 1 x 1</button><button type="button" className="compact secondary" data-testid="viewer-supercell-download" onClick={onDownload}>Download view state</button></div>
    <output role="status" aria-live="polite" data-testid="viewer-supercell-estimate">Draft {draft.join(" by ")}: {estimate.totalCells} cells, {estimate.displayedAtoms} atoms, {estimate.displayedBonds} bonds, {estimate.mode}.</output>
    <output data-testid="viewer-supercell-status">Applied {applied.join(" by ")}{estimate.error ? `; ${estimate.error}: requested ${estimate.displayedAtoms} sites and ${estimate.displayedBonds} bonds; limits are ${PERIODIC_DERIVED_CAPS.maxDisplayedSites} sites and ${PERIODIC_DERIVED_CAPS.maxDisplayedBonds} bonds.` : ""}</output>
  </fieldset>;
}
