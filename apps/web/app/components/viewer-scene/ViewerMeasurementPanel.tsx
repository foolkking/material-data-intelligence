import { formatMeasurement, type ViewerMeasurementEvaluation, type ViewerMeasurementResult } from "./viewerSceneMeasurements";
import { selectionLimit, type ViewerSelectionMode } from "./viewerSceneSelection";
import type { PeriodicSiteRef } from "./viewerSceneRendererTypes";

export type PeriodicMeasurementMode = "displayed_positions" | "minimum_image";

export function ViewerMeasurementPanel({ mode, selected, coordinateMode, resolvedRefs, evaluation, history, onMode, onCoordinateMode, onUndo, onClear, onDownload }: {
  readonly mode: ViewerSelectionMode;
  readonly selected: readonly PeriodicSiteRef[];
  readonly coordinateMode: PeriodicMeasurementMode;
  readonly resolvedRefs: readonly PeriodicSiteRef[];
  readonly evaluation: ViewerMeasurementEvaluation | null;
  readonly history: readonly ViewerMeasurementResult[];
  readonly onMode: (mode: ViewerSelectionMode) => void;
  readonly onCoordinateMode: (mode: PeriodicMeasurementMode) => void;
  readonly onUndo: () => void;
  readonly onClear: () => void;
  readonly onDownload: () => void;
}) {
  return (
    <section className="viewer-measurement-panel" aria-label="结构测量">
      <div className="viewer-measurement-modes" data-testid="viewer-measurement-mode">
        {(["inspect", "distance", "angle", "dihedral"] as const).map((value) => <button key={value} type="button" className={`compact ${mode === value ? "active" : "secondary"}`} aria-pressed={mode === value} onClick={() => onMode(value)}>{({inspect:"选择",distance:"距离",angle:"角度",dihedral:"二面角"} as const)[value]}</button>)}
        <button type="button" className="compact secondary" data-testid="viewer-measurement-undo" onClick={onUndo} disabled={!selected.length}>撤销</button>
        <button type="button" className="compact secondary" data-testid="viewer-measurement-clear" onClick={onClear}>清除</button>
        <button type="button" className="compact secondary" data-testid="viewer-measurement-download" onClick={onDownload} disabled={!evaluation?.ok}>下载测量 JSON</button>
      </div>
      <div className="viewer-measurement-modes" aria-label="测量坐标模式">
        <button type="button" className={`compact ${coordinateMode === "displayed_positions" ? "active" : "secondary"}`} aria-pressed={coordinateMode === "displayed_positions"} onClick={() => onCoordinateMode("displayed_positions")}>显示坐标</button>
        <button type="button" className={`compact ${coordinateMode === "minimum_image" ? "active" : "secondary"}`} aria-pressed={coordinateMode === "minimum_image"} onClick={() => onCoordinateMode("minimum_image")}>最小周期像</button>
      </div>
      <p data-testid="viewer-measurement-selection">已选位点：{selected.length ? selected.map((site, index) => `${String.fromCharCode(65 + index)}=${formatRef(site)}`).join(", ") : "无"}（{selected.length}/{selectionLimit(mode)}）</p>
      <p>{coordinateMode === "displayed_positions" ? "测量使用当前结构场景中的显示坐标。" : "最小周期像测量使用受限的精确晶格搜索，并报告解析后的周期位置。"}</p>
      {resolvedRefs.length ? <p data-testid="viewer-periodic-measurement-offsets">解析后的周期位置：{resolvedRefs.map(formatRef).join("；")}</p> : null}
      {evaluation?.ok ? <output data-testid="viewer-measurement-result">{evaluation.result.kind}: {formatMeasurement(evaluation.result.value)} {evaluation.result.unit === "angstrom" ? "Å" : "°"}</output> : null}
      {evaluation && !evaluation.ok ? <p className="notice" data-testid="viewer-measurement-result">测量不可用：{evaluation.error.toLowerCase().replaceAll("_", " ")}。</p> : null}
      {history.length ? <ol className="viewer-measurement-history" aria-label="测量历史">{history.map((item, index) => <li key={`${item.kind}-${item.siteIndices.join("-")}-${index}`}>{({distance:"距离",angle:"角度",dihedral:"二面角"} as Record<string,string>)[item.kind] || item.kind} {item.siteIndices.join("–")}：{formatMeasurement(item.value)} {item.unit === "angstrom" ? "Å" : "°"}</li>)}</ol> : null}
    </section>
  );
}

function formatRef(ref: PeriodicSiteRef) { return `${ref.siteIndex}@[${ref.imageOffset.join(",")}]`; }
