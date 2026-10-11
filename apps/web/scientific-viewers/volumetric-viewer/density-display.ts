import type { ValidatedVolumetricField } from "./volumetricViewerTypes";

export function densityFieldName(field: Pick<ValidatedVolumetricField, "fieldName" | "quantity" | "spin">) {
  const channel = field.spin?.channel;
  if (channel === "spin_difference") return "自旋差";
  if (channel === "spin_up") return "自旋向上";
  if (channel === "spin_down") return "自旋向下";
  if (field.quantity === "electron_localization_function") return "电子局域函数（ELF）";
  if (field.quantity === "orbital_density" && field.fieldName === "total") return "部分电荷密度";
  if (field.quantity === "electron_density" && field.fieldName === "total") return "总电子密度";
  if (field.quantity === "charge_density") return "电荷密度";
  if (field.quantity === "local_potential") return "局域势";
  if (field.quantity === "electrostatic_potential") return "静电势";
  return field.fieldName;
}

export function densityUnit(unit: string) {
  return ({ dimensionless: "无量纲", "electron/angstrom^3": "电子/Å³", "bohr_magneton/angstrom^3": "μB/Å³", "elementary_charge/angstrom^3": "e/Å³", "angstrom^-3": "Å⁻³", "angstrom^3": "Å³", electron: "电子", elementary_charge: "e", bohr_magneton: "μB", electronvolt: "eV", volt: "V", hartree: "Ha", "hartree/elementary_charge": "Ha/e" } as Record<string, string>)[unit] ?? unit;
}

export function densityWarning(warning: string) {
  return ({
    VOLUME_COMPRESSION_RATIO_FALLBACK_RAW: "压缩率超过读取上限，已使用未压缩格式保存原数值。",
    VOLUME_VASP_AUGMENTATION_NOT_INCLUDED: "网格积分未包含全部增广贡献。",
    VOLUME_COLLINEAR_DERIVED_FIELDS_UNAVAILABLE: "自旋向上／向下的推导关系未完整验证。",
    VOLUME_ELECTRON_DENSITY_SIGNIFICANT_NEGATIVE: "电子密度含显著负值，请核对源数据。",
    VOLUME_ELECTRON_DENSITY_NUMERIC_NEGATIVE: "电子密度含数值精度范围内的负值。",
    VOLUME_NONCOLLINEAR_PRODUCT_DEFERRED: "暂不支持非共线磁化矢量的等值面。",
    ELF_NUMERIC_RANGE_TOLERANCE_WARNING: "ELF 略超出 0–1，偏差在数值容差内。",
    ELF_SOURCE_RANGE_ANOMALY: "ELF 超出 0–1，偏差超过数值容差，请核对源数据。",
    ORBITAL_DENSITY_NUMERIC_NEGATIVE_WARNING: "部分电荷密度含数值容差内的负值。",
    ORBITAL_DENSITY_SOURCE_RANGE_ANOMALY: "部分电荷密度含显著负值，请核对源数据。",
    ORBITAL_SOURCE_IDENTITY_UNAVAILABLE: "源数据未提供轨道、能带、k 点或占据数身份。",
  } as Record<string, string>)[warning] ?? warning;
}

export function densityIntegralMeaning(meaning: string) {
  return ({ electron_count: "整胞电子数", elementary_charge: "整胞电荷", magnetic_moment: "整胞磁矩", not_physically_interpreted: "未赋予物理含义", normalized_to_unit_integral: "源数据声明归一化至单位积分", source_native: "源数据归一化" } as Record<string, string>)[meaning] ?? meaning;
}

export function rangeStatus(status?: string) {
  return ({ VALID_RANGE: "范围正常", NUMERIC_TOLERANCE_WARNING: "容差内偏差", SOURCE_RANGE_ANOMALY: "源值范围异常", INVALID_NON_FINITE: "含无效数值" } as Record<string, string>)[status ?? ""] ?? "正在校验源值…";
}
