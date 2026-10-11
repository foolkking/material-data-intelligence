const PRESENTATION_LIMITATION_TRANSLATIONS: Readonly<Record<string, string>> = {
  "MSD series values remain referenced structured data; only exact lag-time boundaries are projected for downstream parameter authority.": "完整 MSD 序列保留在数值数据中；当前解读事实仅包含精确的滞后时间边界。",
  "MSD curves remain saved structured data. Scalar facts expose only saved endpoint values and origin counts; they do not establish linearity, isotropy, or a diffusive regime.": "完整 MSD 曲线保留在数值数据中；端点数值和时间原点数不能单独确定线性、各向同性或扩散状态。",
  "Fit statistics alone do not establish diffusion. A diffusion coefficient is available only when the saved diagnostic accepts the selected window; a rejected window must not be reported as a measured diffusion coefficient.": "拟合统计本身不能确定扩散；只有所选窗口通过诊断判据时，才提供该窗口的扩散系数。",
  "Source-defined partial density and its contours do not establish a single orbital, band, k-point, HOMO/LUMO, orbital character, or bonding identity. Such assignments require explicit supporting source metadata and analysis.": "部分电荷密度及其等值面不能确定单轨道、能带、K 点、HOMO/LUMO、轨道成分或成键身份；这些判断需要明确的源数据和额外分析。",
  "The saved full-cell partial-density integral retains its declared unit and normalization. An electron-count integral is not automatically a single-orbital occupancy or probability; no electron count or probability inside an isosurface has been computed.": "整胞部分密度积分保留源单位和归一化含义；电子数积分不自动代表单轨道占据数或概率，也未计算等值面内部的电子数或概率。",
  "ELF is dimensionless. Its saved full-cell spatial integral is a mathematical statistic in cubic angstroms; no electron-count or basin-population interpretation is assigned. This does not make the saved statistic unavailable or invalid.": "ELF 本身无量纲，保存的整胞体积分是以 Å³ 为单位的数学统计量，不能直接解释为电子数或盆布居；这不影响该数值本身的有效性。",
  "ELF isosurfaces and slices display the supplied scalar field. They do not establish bond, lone-pair, basin, shell, or topology classifications; those require additional scientific analysis.": "ELF 等值面和切片展示已有标量场；化学键、孤对电子、盆、壳层和拓扑分类需要额外分析。",
  "The result preserves validated volumetric metadata and does not claim renderer or arbitrary slice computation authority.": "结论以已保存的体数据记录为依据；渲染图形或查看切片本身不构成新的科学计算结果。",
  "Conclusions are limited to the saved volumetric field and statistics; rendered surfaces and slices do not independently establish physical properties.": "结论限于已保存的体数据和统计结果；不能仅凭等值面或切片推断材料的物理性质。",
  "Lattice and symmetry facts describe only the supplied validated structure and do not infer material properties.": "晶格与对称性信息仅描述所提供的已验证结构，不据此推断材料性质。",
  "The trajectory viewer product preserves validated trajectory data and launch metadata; it does not compute MSD, diffusion, RDF, or infer dynamic bonds.": "轨迹查看器保留已验证的轨迹数据和启动信息；不计算 MSD、扩散或 RDF，也不推断动态化学键。",
  "The result projector does not infer peaks or coordination shells from the RDF curve.": "不据 RDF 曲线推断峰位或配位壳层。",
  "结果投影仪不推断 RDF 曲线中的峰位或配位壳层。": "不据 RDF 曲线推断峰位或配位壳层。",
  "MSD series values remain referenced structured data and are not expanded into scalar facts.": "MSD 序列保留为可追溯的结构化数据，不会被展开或改写为额外标量事实。",
  "The current band Artifact does not provide eigenvectors or animation authority.": "当前声子能带 Artifact 不包含特征向量，因此不提供模式动画依据。",
  "The current DOS Artifact does not provide eigenvectors or animation authority.": "当前声子态密度 Artifact 不包含特征向量，因此不提供模式动画依据。",
  "The combined Artifact is a static band/DOS result and does not provide eigenvectors or animation authority.": "当前组合 Artifact 是静态声子能带/DOS 结果，不包含特征向量或动画依据。",
  "The result references the validated coordination Artifact and does not recompute neighbors.": "该结果引用已验证的配位 Artifact；呈现时不会重新计算近邻。",
  "RDF series remain bounded structured evidence; the projector does not detect peaks.": "RDF 序列保留为有界结构化证据；结果投影不会自行识别峰位。",
  "Band values are supplied electronic data; no DFT/GW calculation or interpolation is executed.": "能带数值来自已提供的权威电子结构数据；本次呈现不会执行 DFT/GW 计算或插值。",
  "Band energies and gap facts are derived only from the supplied sampled electronic data; the platform performs no DFT, GW correction, interpolation or projected-band analysis.": "能带能量与带隙事实仅来自已提供的采样电子数据；平台未执行 DFT、GW 修正、插值或投影能带分析。",
  "DOS values are supplied electronic data; no new electronic calculation is executed.": "DOS 数值来自已提供的权威电子结构数据；本次呈现不会执行新的电子结构计算。",
  "DOS values are supplied data. Partial or unknown projection coverage describes only provided channels; no total, electron count, bonding, magnetism or band character is inferred.": "DOS 数值来自已提供的数据。PARTIAL 或未知投影覆盖仅描述现有通道；不会据此推断总态密度、电子数、成键、磁性或能带性质。",
  "Composition-space projection is descriptive and does not establish material identity or causality.": "组成空间投影仅用于描述数据分布，不据此确立材料身份或因果关系。",
  "Only the bounded, profile-authorized dataset projection is included.": "当前结果仅包含通过语义 Profile 授权的有界 Dataset 投影。",
  "Diffusion is estimated only over the explicitly selected fit window and is not an unconditional long-time bulk diffusion coefficient.": "扩散系数仅在明确选择的拟合时间窗内估算，不代表无条件的长时间体相扩散系数。",
  "MSD uses Cartesian x/y/z axes and is not automatically crystallographic a/b/c diffusion.": "MSD 使用笛卡尔 x/y/z 轴，不会自动解释为晶体学 a/b/c 方向扩散。",
  "No center-of-mass drift correction is applied.": "本次结果未应用质心漂移校正。",
};

export function presentationLimitationText(text: string): string {
  return Object.hasOwn(PRESENTATION_LIMITATION_TRANSLATIONS, text) ? PRESENTATION_LIMITATION_TRANSLATIONS[text] : text;
}

// Reviewed, complete statements only. Do not infer equivalence from similar
// wording: a changed axis, negation, value or source qualifier can change scope.
const REPORT_LIMITATION_ALIASES: Readonly<Record<string, string>> = {
  "未应用质心漂移校正。": "No center-of-mass drift correction is applied.",
  "MSD使用笛卡尔x/y/z轴，非自动晶格a/b/c扩散。": "MSD uses Cartesian x/y/z axes and is not automatically crystallographic a/b/c diffusion.",
};

type ReportLimitation = { statement: string; source_refs: string[] };

export function reportLimitationPresentation(items: readonly ReportLimitation[]): ReportLimitation[] {
  const unique = new Map<string, ReportLimitation>();
  for (const item of items) {
    const original = item.statement.trim();
    const statement = presentationLimitationText(Object.hasOwn(REPORT_LIMITATION_ALIASES, original) ? REPORT_LIMITATION_ALIASES[original] : original);
    const existing = unique.get(statement);
    if (existing) {
      existing.source_refs = [...new Set([...existing.source_refs, ...item.source_refs])];
    } else {
      unique.set(statement, { statement, source_refs: [...new Set(item.source_refs)] });
    }
  }
  return [...unique.values()];
}
