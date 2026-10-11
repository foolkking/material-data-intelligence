export const projectScienceNames: Readonly<Record<string, string>> = {
  "reference.periodic_table": "元素周期表", "reference.compare_elements": "元素参考性质比较",
  "reference.convert_units": "单位换算", "generation.function_curve": "函数曲线",
  "composition.from_formula": "化学式组成", "viz.inline_xy": "输入数据绘图",
  "generation.ideal_crystal": "理想晶格",
};

export const inputOriginNames: Readonly<Record<string, string>> = {
  PLATFORM_REFERENCE: "平台参考资料", USER_PARAMETERS: "输入参数",
  USER_TEXT_DATA: "输入表格", IDEAL_MODEL: "理想模型", MIXED: "多种输入来源",
};

export const projectParameterNames: Readonly<Record<string, string>> = {
  values: "原数值", from_unit: "原单位", to_unit: "目标单位", quantity: "物理量",
  x_min: "区间起点", x_max: "区间终点", point_count: "采样点数", functions: "函数",
  kind: "类型", coefficients: "系数（从常数项起）", amplitude: "幅值", offset: "纵向偏移",
  rate: "自变量系数", phase: "自变量偏移", center: "中心", sigma: "标准差参数",
  formula: "化学式", data_text: "原始输入表格", x_column: "横轴列（从零起）",
  y_columns: "纵轴列（从零起）", style: "绘图方式", prototype: "晶格原型", elements: "元素",
  lattice_a_angstrom: "单胞 a（Å）", lattice_c_angstrom: "单胞 c（Å）", repetitions: "晶胞重复数",
};

export const projectParameterValues: Readonly<Record<string, string>> = {
  polynomial: "多项式", sine: "正弦", cosine: "余弦", exponential: "指数", logarithm: "自然对数",
  gaussian: "高斯函数", value: "数值", temperature_difference: "温差", line: "折线", scatter: "散点",
  sc: "简单立方（SC）", bcc: "体心立方（BCC）", fcc: "面心立方（FCC）", diamond: "金刚石型",
  rocksalt: "岩盐型", cscl: "CsCl 型", hcp: "六方密排（HCP）",
};
