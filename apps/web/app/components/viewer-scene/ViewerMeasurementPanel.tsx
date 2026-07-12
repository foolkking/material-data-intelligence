import { formatMeasurement, type ViewerMeasurementEvaluation, type ViewerMeasurementResult } from "./viewerSceneMeasurements";
import { selectionLimit, type ViewerSelectionMode } from "./viewerSceneSelection";
import type { PeriodicSiteRef } from "./viewerSceneRendererTypes";

export type PeriodicMeasurementMode = "displayed_positions" | "minimum_image";

export function ViewerMeasurementPanel({ mode, selected, coordinateMode, resolvedRefs, evaluation, history, onMode, onCoordinateMode, onClear }: {
  readonly mode: ViewerSelectionMode;
  readonly selected: readonly PeriodicSiteRef[];
  readonly coordinateMode: PeriodicMeasurementMode;
  readonly resolvedRefs: readonly PeriodicSiteRef[];
  readonly evaluation: ViewerMeasurementEvaluation | null;
  readonly history: readonly ViewerMeasurementResult[];
  readonly onMode: (mode: ViewerSelectionMode) => void;
  readonly onCoordinateMode: (mode: PeriodicMeasurementMode) => void;
  readonly onClear: () => void;
}) {
  return (
    <section className="viewer-measurement-panel" aria-label="Structure measurements">
      <div className="viewer-measurement-modes" data-testid="viewer-measurement-mode">
        {(["inspect", "distance", "angle", "dihedral"] as const).map((value) => <button key={value} type="button" className={`compact ${mode === value ? "active" : "secondary"}`} aria-pressed={mode === value} onClick={() => onMode(value)}>{value === "inspect" ? "Select" : value[0].toUpperCase() + value.slice(1)}</button>)}
        <button type="button" className="compact secondary" data-testid="viewer-measurement-clear" onClick={onClear}>Clear</button>
      </div>
      <div className="viewer-measurement-modes" aria-label="Measurement coordinate mode">
        <button type="button" className={`compact ${coordinateMode === "displayed_positions" ? "active" : "secondary"}`} aria-pressed={coordinateMode === "displayed_positions"} onClick={() => onCoordinateMode("displayed_positions")}>Displayed positions</button>
        <button type="button" className={`compact ${coordinateMode === "minimum_image" ? "active" : "secondary"}`} aria-pressed={coordinateMode === "minimum_image"} onClick={() => onCoordinateMode("minimum_image")}>Minimum image (periodic)</button>
      </div>
      <p data-testid="viewer-measurement-selection">Selected sites: {selected.length ? selected.map((site, index) => `${String.fromCharCode(65 + index)}=${formatRef(site)}`).join(", ") : "none"} ({selected.length}/{selectionLimit(mode)})</p>
      <p>{coordinateMode === "displayed_positions" ? "Measurement uses displayed positions represented in the current viewer scene." : "Minimum-image measurement uses a bounded exact lattice search and reports the resolved periodic images."}</p>
      {resolvedRefs.length ? <p data-testid="viewer-periodic-measurement-offsets">Resolved images: {resolvedRefs.map(formatRef).join("; ")}</p> : null}
      {evaluation?.ok ? <output data-testid="viewer-measurement-result">{evaluation.result.kind}: {formatMeasurement(evaluation.result.value)} {evaluation.result.unit === "angstrom" ? "Å" : "°"}</output> : null}
      {evaluation && !evaluation.ok ? <p className="notice" data-testid="viewer-measurement-result">Measurement unavailable: {evaluation.error.toLowerCase().replaceAll("_", " ")}.</p> : null}
      {history.length ? <ol className="viewer-measurement-history" aria-label="Measurement history">{history.map((item, index) => <li key={`${item.kind}-${item.siteIndices.join("-")}-${index}`}>{item.kind} {item.siteIndices.join("–")}: {formatMeasurement(item.value)} {item.unit === "angstrom" ? "Å" : "°"}</li>)}</ol> : null}
    </section>
  );
}

function formatRef(ref: PeriodicSiteRef) { return `${ref.siteIndex}@[${ref.imageOffset.join(",")}]`; }
