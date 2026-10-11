export function savedPeriodicTableFixture(log = false) {
  const cells = [{ symbol: "Cu", x: 10, y: 6, value: 1 }, { symbol: "Fe", x: 7, y: 6, value: 12 }, { symbol: "O", x: 15, y: 8, value: 12 }, { symbol: "Si", x: 13, y: 7, value: 3 }];
  const grid = () => Array.from({ length: 10 }, () => Array<number | null>(18).fill(null));
  const background = grid(), values = grid();
  for (const cell of cells) { background[cell.y][cell.x] = 1; values[cell.y][cell.x] = log ? Math.log10(cell.value) : cell.value; }
  const annotations = Array.from({ length: 180 }, (_, i) => {
    const x = i % 18, y = Math.floor(i / 18), cell = cells.find(cell => cell.x === x && cell.y === y);
    return { x, y, xref: "x", yref: "y", showarrow: false, text: cell ? `<span style='font-weight: bold;'>${cell.symbol}</span><br>${cell.value}` : "", font: { color: "#000000" } };
  });
  const bar = log ? { tickvals: [0, Math.log10(2), 1], ticktext: ["1", "2", "10"] } : {};
  return { artifactType: "composition.ptable_heatmap", countMode: "occurrence", log, elementValues: { Cu: 1, Fe: 12, O: 12, Si: 3 }, plotlyFigure: {
    data: [
      { type: "heatmap", z: background, colorscale: [[0, "darkgray"], [1, "darkgray"]], showscale: false, xgap: 4.5, ygap: 4.5 },
      { type: "heatmap", z: background, colorscale: [[0, "#eff"], [1, "#eff"]], showscale: false, xgap: 5, ygap: 5 },
      { type: "heatmap", z: values, colorscale: [[0, "#440154"], [1, "#fde725"]], showscale: true, xgap: 5, ygap: 5, zauto: false, zmin: log ? 0 : 1, zmax: log ? Math.log10(12) : 12, colorbar: bar },
    ], layout: { title: { text: "Periodic Table Heatmap" }, annotations } },
  };
}
