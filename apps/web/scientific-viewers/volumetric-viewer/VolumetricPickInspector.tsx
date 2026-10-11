import type { VolumetricSurfacePick } from "./volumetricViewerTypes";
import type { potentialSurfaceLayer } from "./electrostaticPotentialProduct";
import { densityUnit } from "./density-display";
import styles from "./VolumetricSurface.module.css";

export function VolumetricPickInspector({ pick, atom, layerNumber, unit, fieldHash, potentialLayer, onClear }: {
  pick: VolumetricSurfacePick | null;
  atom: number | null;
  layerNumber: number;
  unit: string;
  fieldHash?: string;
  potentialLayer: ReturnType<typeof potentialSurfaceLayer> | null;
  onClear: () => void;
}) {
  if (!pick && atom === null) return null;
  const value = potentialLayer?.sourceIsovalue ?? pick?.isovalue;
  const displayUnit = densityUnit(potentialLayer?.unit ?? unit);
  return <section className={styles.pickInspector} aria-label="当前选点" data-testid={pick ? "volumetric-surface-inspector" : "volumetric-atom-inspector"}>
    <div className={styles.pickSummary}>
      <strong>{pick ? `等值面${layerNumber > 0 ? ` ${layerNumber}` : ""}` : `结构位点 ${atom}`}</strong>
      {pick ? <span>{potentialLayer ? "源等值" : "等值"} {Number(value).toPrecision(6)} {displayUnit}</span> : null}
      {potentialLayer && potentialLayer.displayedIsovalue !== potentialLayer.sourceIsovalue ? <span>显示等值 {potentialLayer.displayedIsovalue.toPrecision(6)} {displayUnit}</span> : null}
      <button type="button" onClick={onClear}>清除选择</button>
    </div>
    {pick ? <>
      <p className={styles.pickCoordinates}>坐标（Å） {pick.cartesianPosition.map(value => value.toFixed(3)).join(", ")}</p>
      <details className={styles.pickDetails}><summary>精确数值与来源</summary><dl className={styles.scientificProperties}>
        <dt>{potentialLayer ? "源等值" : "等值"}</dt><dd>{value} {displayUnit}</dd>
        {potentialLayer ? <><dt>显示等值</dt><dd>{potentialLayer.displayedIsovalue} {displayUnit}</dd></> : null}
        <dt>笛卡尔坐标（Å）</dt><dd>{pick.cartesianPosition.join(", ")}</dd>
        <dt>表面编号</dt><dd>{pick.layerId}</dd>
        <dt>三角形编号</dt><dd>{pick.triangleIndex}</dd>
        <dt>字段编号</dt><dd>{pick.fieldId}</dd>
        {fieldHash ? <><dt>字段校验值</dt><dd>{fieldHash}</dd></> : null}
        <dt>网格校验值</dt><dd>{pick.meshHash}</dd>
      </dl></details>
    </> : null}
  </section>;
}
