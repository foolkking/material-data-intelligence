export const TABLE_STAT_LABELS: Record<string, string> = {
  column: "变量", count: "有效样本", missing: "缺失", missing_rate: "缺失比例",
  mean: "均值", std: "标准差", min: "最小值", p25: "下四分位数", median: "中位数",
  p75: "上四分位数", max: "最大值", unique_count: "不同值数",
};
const labels: Record<string, string> = {
  "composition.stoichiometry": "化学计量数", "composition.atomic_fraction": "原子分数", "composition.atomic_percent": "原子百分比",
  "inline.minimum": "最小值", "inline.maximum": "最大值", "inline.mean": "均值", "inline.first": "首行数值", "inline.last": "末行数值",
  "calculation.sampled_min": "采样最小值", "calculation.sampled_max": "采样最大值",
  "calculation.start_value": "起点函数值", "calculation.end_value": "终点函数值",
  "reference.element.atomic_number": "原子序数", "reference.element.covalent_radius": "参考共价半径",
  "table.row_count": "数据行数", "table.column_count": "数据列数",
  "correlation.method": "相关方法", "correlation.pair_count": "变量对数",
  "correlation.valid_pair_count": "有效变量对", "correlation.missing_pair_count": "缺失变量对",
  "correlation.minimum_sample_count": "最低共同样本设置", "correlation.left_column": "变量 A",
  "correlation.right_column": "变量 B", "correlation.coefficient": "相关系数",
  "table.category.column": "变量", "table.category.value": "类别", "table.category.count": "样本数",
  "histogram.column": "变量", "histogram.count": "有效样本", "histogram.bins": "分箱设置",
  "histogram.input_count": "输入行数", "histogram.excluded_count": "排除行数",
  "scatter.x_column": "横轴变量", "scatter.y_column": "纵轴变量", "scatter.point_count": "绘制点数",
  "scatter.input_count": "输入行数", "scatter.valid_point_count": "有效点数", "scatter.excluded_count": "排除行数", "scatter.omitted_point_count": "未绘制点数",
  "scatter.x_min": "横轴最小值", "scatter.x_max": "横轴最大值",
  "scatter.y_min": "纵轴最小值", "scatter.y_max": "纵轴最大值",
};

export function tableMetricTitle(predicate: string): string | undefined {
  const match = predicate.match(/^(?:table\.(?:numeric|categorical)|histogram)\.(.+)$/u);
  return labels[predicate] || (match ? TABLE_STAT_LABELS[match[1]] : undefined);
}

type Fact = { factId: string; predicate: string; subjectRef: string; value: unknown;
  source?: { artifactId?: string | null; scientificObjectRef?: { objectId: string; versionId: string } | null } };

/** A measurement label may borrow a name only from its exact saved subject. */
export function tableFactLabels(facts: readonly Fact[]): Map<string, string> {
  const groups = new Map<string, Fact[]>(), ids = new Set<string>(), duplicates = new Set<string>();
  for (const fact of facts) { if (ids.has(fact.factId)) duplicates.add(fact.factId); ids.add(fact.factId); }
  for (const fact of facts) {
    if (!fact.source?.artifactId || !fact.subjectRef || duplicates.has(fact.factId)) continue;
    const source = fact.source.scientificObjectRef;
    const key = JSON.stringify([fact.source.artifactId, fact.subjectRef, source?.objectId, source?.versionId]);
    groups.set(key, [...(groups.get(key) || []), fact]);
  }
  const result = new Map<string, string>();
  for (const group of groups.values()) {
    if (new Set(group.map(f => f.predicate)).size !== group.length) continue;
    const name = (predicate: string) => {
      const value = group.find(f => f.predicate === predicate)?.value;
      return typeof value === "string" && value.trim() ? value : null;
    };
    const left = name("correlation.left_column"), right = name("correlation.right_column");
    const column = name("table.numeric.column") || name("table.categorical.column") || name("histogram.column") || name("inline.column");
    const element = name("reference.element.symbol") || name("composition.element");
    const expression = name("calculation.function");
    for (const fact of group) {
      const title = tableMetricTitle(fact.predicate);
      if (!title) continue;
      if (element && (fact.predicate.startsWith("reference.element.") || fact.predicate.startsWith("composition."))) result.set(fact.factId, `${element} · ${title}`);
      else if (expression && fact.predicate.startsWith("calculation.")) result.set(fact.factId, `${expression} · ${title}`);
      else if (fact.predicate === "correlation.coefficient" && left && right) result.set(fact.factId, `${left} ↔ ${right} · ${title}`);
      else if (column && !fact.predicate.endsWith(".column")) result.set(fact.factId, `${column} · ${title}`);
    }
  }
  return result;
}
