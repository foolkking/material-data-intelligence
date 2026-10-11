/** Display-only terminology shared by Research, report readers and exports.
 * Never apply this to source payloads, identifiers, filenames or user questions.
 * Unknown terms and all numeric/unit spellings are retained verbatim.
 */
const NARRATIVE_TERMS: Readonly<Record<string, string>> = {
  "immutable ScientificResultSnapshot": "不可变的科学结果快照",
  "validated Interpretation": "已验证的解读",
  "exact source versions": "精确来源版本",
  "exact source version": "精确来源版本",
  statistics_authority: "统计依据",
  computed_from_payload: "由保存的场数据计算",
  source_declared: "由源数据声明",
  integral_semantics: "积分含义",
  normalization_semantics: "归一化方式",
  electron_count: "电子数",
  not_physically_interpreted: "未指定物理量解释",
  source_native: "沿用源数据的归一化",
  source_defined: "由源数据定义",
  normalized_to_unit_integral: "归一化至单位积分",
  normalized_to_electron_count: "按电子数归一化",
  normalized_to_charge: "按电荷归一化",
  not_normalized: "未归一化",
  orbital_density: "轨道密度",
  electron_localization_function: "电子局域函数（ELF）",
  real_space_cartesian: "实空间笛卡尔坐标",
  ScientificResultSnapshot: "科学结果快照",
  ScientificResult: "科学结果",
  undefined_constant_target: "未定义（目标值为常量）",
  INSUFFICIENT_DURATION: "拟合窗口时长不足",
  INSUFFICIENT_POINTS: "拟合点数不足",
  INSUFFICIENT_ORIGIN_COVERAGE: "时间原点覆盖不足",
  NON_POSITIVE_SLOPE: "拟合斜率非正",
  POOR_LINEAR_FIT: "线性拟合质量不足",
  INSUFFICIENT_MSD_SIGNAL: "均方位移信号不足",
  BALLISTIC_LIKE_WINDOW: "所选窗口呈类弹道行为",
  NON_DIFFUSIVE_WINDOW: "所选窗口未满足扩散判据",
  DIFFUSIVE_WINDOW_ACCEPTED: "所选窗口满足扩散判据",
};

const TOKEN_CHARACTERS = "[A-Za-z0-9_./:@?&=#%+~\\\\-]";
const TERM_PATTERN = new RegExp(
  `(?<!${TOKEN_CHARACTERS})(?:${Object.keys(NARRATIVE_TERMS).join("|")})(?!${TOKEN_CHARACTERS})`,
  "gu",
);

export function scientificNarrativeText(value: string): string {
  // Quoted code and URI/path spans are provenance, even when a component is a
  // known term. Transform only the surrounding narrative.
  return value.split(/(`+[^`\n]*`+|[A-Za-z][A-Za-z0-9+.-]*:\/\/[^\s<>"'，。；（）]+|(?:[A-Za-z]:\\|[A-Za-z0-9_.-]+[\/\\]|\/)[^\s<>"'，。；（）]+)/gu)
    .map((part, index) => index % 2 ? part : translateNarrative(part)).join("");
}

function translateNarrative(value: string): string {
  return value
    // Omit only an exact machine-label echo after its equivalent explanation.
    .replace(/轨道密度\s*[（(]orbital_density[）)]/gu, "轨道密度")
    .replace(/(未(?:被)?赋予物理(?:意义|含义))\s*[（(]not_physically_interpreted[）)]/gu, "$1")
    .replace(/((?:由|从)(?:存储|保存|已保存)的(?:数值场|网格值|场数据)计算(?:得出)?)\s*[（(](?:statistics_authority\s*=\s*)?computed_from_payload[）)]/gu, "$1")
    .replace(/归一化语义为\s*source_native(?![A-Za-z0-9_./:@-])/gu, "归一化沿用源数据")
    .replace(/积分语义为\s*electron_count(?![A-Za-z0-9_./:@?&=#%+~\\-])/gu, "积分表示电子数")
    .replace(/量类型为\s*orbital_density(?![A-Za-z0-9_./:@?&=#%+~\\-])/gu, "物理量为轨道密度")
    .replace(/端点策略为\s*excluded(?![A-Za-z0-9_./:@-])/gu, "网格不包含终点")
    .replace(/端点策略为\s*included(?![A-Za-z0-9_./:@-])/gu, "网格包含终点")
    .replace(TERM_PATTERN, term => NARRATIVE_TERMS[term])
    .replaceAll("。；", "；")
    .replaceAll("；。", "。")
    .replaceAll("。。", "。");
}
