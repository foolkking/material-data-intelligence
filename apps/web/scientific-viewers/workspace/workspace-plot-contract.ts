export type WorkspacePlotRecord = Record<string, unknown>;

export function normalizedPlotFigure(content: unknown): WorkspacePlotRecord | null {
  const root = record(content);
  if (!root) return null;
  const figure = record(root.figure) ?? record(root.plotlyFigure) ?? root;
  if (Array.isArray(figure.data)) return figure;

  const series = Array.isArray(root.series) ? root.series : null;
  const chartType = typeof root.chart_type === "string" ? root.chart_type.toLowerCase() : "";
  if (!series?.length || !["line", "scatter", "bar"].includes(chartType)) return null;

  const sharedX = scalarArray(record(root.x_axis)?.values);
  const data = series.flatMap((value, index) => {
    const item = record(value);
    const x = scalarArray(item?.x) ?? sharedX;
    const y = scalarArray(item?.y);
    if (!x || !y || x.length !== y.length || !x.length) return [];
    return [{
      type: chartType === "bar" ? "bar" : "scatter",
      mode: chartType === "line" ? "lines" : chartType === "scatter" ? "markers" : undefined,
      name: typeof item?.name === "string" ? item.name : `Series ${index + 1}`,
      x,
      y,
    }];
  });
  if (!data.length) return null;

  return {
    data,
    layout: {
      title: { text: typeof root.title === "string" ? root.title : "" },
      xaxis: { title: { text: axisLabel(root.x_axis) } },
      yaxis: { title: { text: axisLabel(root.y_axis) } },
    },
  };
}

function axisLabel(value: unknown): string {
  const axis = record(value);
  return typeof axis?.label === "string" ? axis.label : "";
}

function record(value: unknown): WorkspacePlotRecord | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? value as WorkspacePlotRecord
    : null;
}

function scalarArray(value: unknown): Array<number | string | null> | null {
  return Array.isArray(value) && value.every((item) =>
    item === null || (typeof item === "number" && Number.isFinite(item)) || typeof item === "string")
    ? value as Array<number | string | null>
    : null;
}
