import { formatMeasurement, type ViewerMeasurementEvaluation, type ViewerMeasurementResult } from "./viewerSceneMeasurements";
import { selectionLimit, type ViewerSelectionMode } from "./viewerSceneSelection";

export function ViewerMeasurementPanel({ mode, selected, evaluation, history, onMode, onClear }: {
  readonly mode: ViewerSelectionMode;
  readonly selected: readonly number[];
  readonly evaluation: ViewerMeasurementEvaluation | null;
  readonly history: readonly ViewerMeasurementResult[];
  readonly onMode: (mode: ViewerSelectionMode) => void;
  readonly onClear: () => void;
}) {
  return (
    <section className="viewer-measurement-panel" aria-label="Structure measurements">
      <div className="viewer-measurement-modes" data-testid="viewer-measurement-mode">
        {(["inspect", "distance", "angle", "dihedral"] as const).map((value) => <button key={value} type="button" className={`compact ${mode === value ? "active" : "secondary"}`} aria-pressed={mode === value} onClick={() => onMode(value)}>{value === "inspect" ? "Select" : value[0].toUpperCase() + value.slice(1)}</button>)}
        <button type="button" className="compact secondary" data-testid="viewer-measurement-clear" onClick={onClear}>Clear</button>
      </div>
      <p data-testid="viewer-measurement-selection">Selected sites: {selected.length ? selected.map((site, index) => `${String.fromCharCode(65 + index)}=${site}`).join(", ") : "none"} ({selected.length}/{selectionLimit(mode)})</p>
      <p>Measurement uses positions represented in the current canonical viewer scene.</p>
      {evaluation?.ok ? <output data-testid="viewer-measurement-result">{evaluation.result.kind}: {formatMeasurement(evaluation.result.value)} {evaluation.result.unit === "angstrom" ? "Å" : "°"}</output> : null}
      {evaluation && !evaluation.ok ? <p className="notice" data-testid="viewer-measurement-result">Measurement unavailable: {evaluation.error.toLowerCase().replaceAll("_", " ")}.</p> : null}
      {history.length ? <ol className="viewer-measurement-history" aria-label="Measurement history">{history.map((item, index) => <li key={`${item.kind}-${item.siteIndices.join("-")}-${index}`}>{item.kind} {item.siteIndices.join("–")}: {formatMeasurement(item.value)} {item.unit === "angstrom" ? "Å" : "°"}</li>)}</ol> : null}
    </section>
  );
}
