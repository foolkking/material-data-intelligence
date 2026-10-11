import type { PotentialProfilePoint } from "./electrostaticPotentialProduct";

export type ProfileWindow = readonly [number, number];
export const PROFILE_HEIGHT = 240;

export function profileChart(points: readonly PotentialProfilePoint[], window: ProfileWindow, width: number) {
  const visible = points.filter(point => point.fractional >= window[0] && point.fractional <= window[1]);
  const left = 64, right = Math.max(left + 1, width - 16), top = 24, bottom = 192;
  const values = visible.map(point => point.displayedValue);
  const minimum = values.length ? Math.min(...values) : 0;
  const maximum = values.length ? Math.max(...values) : 1;
  const padding = maximum === minimum ? Math.max(Math.abs(minimum) * 0.05, 1e-6) : (maximum - minimum) * 0.08;
  const low = minimum - padding, high = maximum + padding;
  const x = (fraction: number) => left + (fraction - window[0]) / Math.max(window[1] - window[0], Number.EPSILON) * (right - left);
  const y = (value: number) => bottom - (value - low) / (high - low) * (bottom - top);
  const plotted = visible.map(point => ({ point, x: x(point.fractional), y: y(point.displayedValue) }));
  const tickCount = width < 480 ? 3 : 5;
  const last = points[points.length - 1];
  const pathScale = last?.fractional ? last.pathLengthAngstrom / last.fractional : 0;
  return {
    width, left, right, top, bottom, plotted, x, y,
    xTicks: Array.from({ length: tickCount }, (_, index) => {
      const fraction = window[0] + index / (tickCount - 1) * (window[1] - window[0]);
      return { position: x(fraction), value: fraction * pathScale };
    }),
    yTicks: [low, (low + high) / 2, high].map(value => ({ position: y(value), value })),
  };
}

export function profilePointAt(chart: ReturnType<typeof profileChart>, clientX: number, bounds: { left: number; width: number }) {
  if (!Number.isFinite(clientX) || bounds.width <= 0 || !chart.plotted.length) return null;
  const position = (clientX - bounds.left) / bounds.width * chart.width;
  return chart.plotted.reduce((nearest, item) => Math.abs(item.x - position) < Math.abs(nearest.x - position) ? item : nearest).point;
}

export function profileNumber(value: number) {
  return Number(value.toPrecision(5)).toString();
}

export function potentialUnit(unit: string) {
  return ({ electronvolt: "eV", volt: "V", hartree: "Ha", "hartree/elementary_charge": "Ha/e" } as Record<string, string>)[unit] ?? unit;
}

export function potentialWarning(warning: string) {
  return ({
    "Potential zero is source-defined unless the source reference says otherwise.": "势的零点按源数据参考系解释。",
    "Absolute potential is not available from this product.": "此视图不提供绝对势。",
    "Vacuum level has not been detected.": "未识别真空能级。",
    "Work function has not been calculated.": "未计算功函数。",
    "Cross-calculation comparison requires explicit alignment.": "比较不同计算前，需要明确对齐参考系。",
    "LOCPOT component semantics depend on the source and parser definition.": "LOCPOT 的势分量含义取决于源文件及解析定义。",
    "The source reference is unknown; reference-dependent claims are disabled.": "源参考系未知，无法得出依赖参考系的结论。",
  } as Record<string, string>)[warning] ?? warning;
}
