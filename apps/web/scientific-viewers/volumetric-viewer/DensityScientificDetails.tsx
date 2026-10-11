"use client";

import type {ChargeSpinDensityProduct} from "./chargeSpinDensityProduct";
import type {ElfOrbitalProduct} from "./elfOrbitalProduct";
import type {ValidatedVolumetricBundle, ValidatedVolumetricField} from "./volumetricViewerTypes";
import {densityFieldName, densityIntegralMeaning, densityUnit, densityWarning, rangeStatus} from "./density-display";
import styles from "./VolumetricSurface.module.css";

type Props = {bundle: ValidatedVolumetricBundle; field: ValidatedVolumetricField; charge: ChargeSpinDensityProduct | null; orbital: ElfOrbitalProduct | null};
const number = (value: number) => Number(value.toPrecision(6)).toString();

export function DensityScientificDetails({bundle, field, charge, orbital}: Props) {
  const elf = orbital?.kind === "elf";
  const special = orbital && orbital.status !== "unavailable" && orbital.sourceFieldId === field.fieldId ? orbital : null;
  const density = !special && charge && charge.status !== "unavailable" && Object.values(charge.modeFieldIds).includes(field.fieldId) ? charge : null;
  if (!special && !density) return null;
  const warnings = [...new Set([...(special?.warnings ?? density?.warnings ?? []), ...field.warnings])];
  const identityWarning = "ORBITAL_SOURCE_IDENTITY_UNAVAILABLE";
  const storageWarning = "VOLUME_COMPRESSION_RATIO_FALLBACK_RAW";
  const visibleWarnings = warnings.filter(warning => warning !== identityWarning && warning !== storageWarning);
  const range = special?.rangeValidation;
  return <section className={`${styles.scientificPanel} ${styles.densityDetails}`} aria-label={special ? elf ? "ELF 数据详情" : "部分电荷密度详情" : "电荷与自旋密度详情"} data-testid={special ? "elf-orbital-product" : "charge-spin-density-product"}>
    {visibleWarnings.length ? <ul className="warning" role="status">{visibleWarnings.map(warning => <li key={warning}>{densityWarning(warning)}</li>)}</ul> : null}
    {special ? <details className={styles.scientificDetails}><summary>统计与数值校验</summary>
      <dl className={styles.scientificProperties} data-testid="elf-orbital-statistics">
        <dt>最小值</dt><dd>{number(field.minimum)} {densityUnit(field.unit)}</dd><dt>最大值</dt><dd>{number(field.maximum)} {densityUnit(field.unit)}</dd>
        <dt>均值</dt><dd>{number(field.mean)} {densityUnit(field.unit)}</dd><dt>标准差</dt><dd>{number(field.standardDeviation)} {densityUnit(field.unit)}</dd><dt>均方根</dt><dd>{number(field.rms)} {densityUnit(field.unit)}</dd>
        <dt>整胞积分</dt><dd>{special.integral === null ? "未提供" : `${number(special.integral)} ${densityUnit(special.integralUnit ?? "")}`}</dd>
        <dt>数值范围</dt><dd data-testid="elf-orbital-range-status">{rangeStatus(range?.status)}</dd>
        <dt>{elf ? "低于 0／高于 1 的点数" : "负值点数"}</dt><dd>{range ? elf ? `${range.belowZeroCount} / ${range.aboveOneCount}` : range.negativeCount : "校验中"}</dd>
        {range ? <><dt>容差</dt><dd>{range.tolerance}</dd><dt>校验规则</dt><dd>{range.tolerancePolicy}</dd></> : null}
      </dl>
      <p>{elf ? "整胞 ELF 体积分不代表电子数或电子盆布居。" : field.integralSemantics === "electron_count" ? "积分按源数据解释为整胞电子数，不自动代表占据数或单轨道概率。" : field.normalizationSemantics === "normalized_to_unit_integral" ? "源数据声明单位积分归一化，不据此推断占据数。" : "积分来自整胞源网格，不作占据数或概率解释。"}</p>
    </details> : null}
    {density ? <details className={styles.scientificDetails}><summary>整胞积分</summary>
      <div className={styles.densityTable} role="region" aria-label="整胞积分表" tabIndex={0}><table data-testid="charge-spin-integrals"><thead><tr><th>字段</th><th>积分</th><th>单位</th><th>含义</th></tr></thead><tbody>{density.integralRows.map(row => <tr key={row.fieldId} aria-selected={row.fieldId === field.fieldId}><th scope="row">{densityFieldName(bundle.fields.find(item => item.field.fieldId === row.fieldId)!.field)}</th><td>{number(row.value)}</td><td>{densityUnit(row.unit)}</td><td>{densityIntegralMeaning(row.interpretation)}</td></tr>)}</tbody></table></div>
      <p>源网格的整胞积分不等同于原子电荷或等值面内的电子数。</p>
    </details> : null}
    <details className={styles.scientificDetails}><summary>来源与科学适用范围</summary>
      <dl className={styles.scientificProperties}><dt>物理量</dt><dd>{field.quantity}</dd><dt>原始字段名</dt><dd>{field.fieldName}</dd><dt>单位</dt><dd>{densityUnit(field.unit)}</dd><dt>源格式</dt><dd>{bundle.sourceFormat}</dd><dt>解析器</dt><dd>{field.provenance.producer} {field.provenance.producerVersion}</dd><dt>字段标识</dt><dd>{field.fieldId}</dd><dt>字段校验值</dt><dd>{field.contentHash}</dd><dt>源文件校验值</dt><dd>{bundle.sourceSha256}</dd><dt>归一化</dt><dd>{densityIntegralMeaning(field.normalizationSemantics)}</dd><dt>积分含义</dt><dd>{densityIntegralMeaning(field.integralSemantics)}</dd>
      {special?.identity ? <><dt>轨道身份</dt><dd data-testid="orbital-identity-completeness">{special.identity.completeness === "PARTIAL" ? "部分信息" : special.identity.completeness === "FULL" ? "完整" : "未提供"}</dd><dt>自旋通道</dt><dd>{special.identity.spinChannel ?? "未提供"}</dd><dt>能带／k 点／占据数</dt><dd>源数据未提供</dd></> : null}
      {density?.formulaIds.length ? <><dt>推导公式</dt><dd data-testid="charge-spin-formulas">{density.formulaIds.join("、")}</dd></> : null}</dl>
      {warnings.includes(storageWarning) ? <p>{densityWarning(storageWarning)}</p> : null}
      {special ? <p data-testid={elf ? "elf-interpretation-boundary" : "orbital-interpretation-boundary"}>{elf ? "ELF 等值面不自动判定化学键、孤对电子、电子盆或原子壳层。" : "此视图仅表示源定义的部分电荷密度，不推断单轨道、HOMO/LUMO、占据数、概率、成键或轨道成分。"}未计算等值面包围的电子数或概率。</p> : null}
      <p>显示使用源数值，未裁值、平滑或重新归一化。</p>
    </details>
  </section>;
}
