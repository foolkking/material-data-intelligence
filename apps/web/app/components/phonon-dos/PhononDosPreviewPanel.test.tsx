import "@testing-library/jest-dom/vitest";

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it, vi } from "vitest";

import { mapPhononDosPlot, PhononDosPreviewPanel } from "./PhononDosPreviewPanel";

const root = resolve(__dirname, "../../../../..");
const dos = JSON.parse(readFileSync(resolve(root, "tests/fixtures/phonon_contract/projected_dos.json"), "utf8"));
const summary = {
  schema_version: "phase10h2.phonon_dos_summary.v1",
  imaginary_region_integral: 0.5,
  projection_completeness: "complete",
};
const manifest = { schema_version: "phase10h2.phonon_dos_manifest.v1" };

function artifacts(payload: unknown = dos) {
  return [
    { id: "dos", type: "phonon_dos_json", name: "phonon_dos.json", content: payload },
    { id: "summary", type: "phonon_summary_json", name: "phonon_dos_summary.json", content: summary },
    { id: "manifest", type: "phonon_manifest_json", name: "phonon_manifest.json", content: manifest },
  ];
}

describe("PhononDosPreviewPanel", () => {
  it("selects total and projected values independently and restores without overriding later channel choices", async () => {
    const onPointSelection = vi.fn(), newPlot = vi.fn().mockResolvedValue(undefined);
    const loader = async () => ({newPlot, purge: vi.fn()});
    const items = artifacts();
    const view = render(<PhononDosPreviewPanel artifacts={items} selectedPoint={{frequencyIndex: 0, projectionIndex: 1}} onPointSelection={onPointSelection} plotlyLoader={loader} />);
    fireEvent.click(screen.getByText("态密度数值"));
    const choice = screen.getByRole("button", {name: "选择原子 1 (Si)频率点 0"});
    expect(choice).toHaveAttribute("aria-pressed", "true");
    fireEvent.click(choice);
    expect(onPointSelection).toHaveBeenLastCalledWith({frequencyIndex: 0, projectionIndex: 1});
    fireEvent.click(screen.getByRole("button", {name: "选择总态密度频率点 0"}));
    expect(onPointSelection).toHaveBeenLastCalledWith({frequencyIndex: 0, projectionIndex: null});
    expect(screen.getByText(/已选 原子 1/)).toHaveTextContent("-1.00000 THz");
    fireEvent.change(screen.getByTestId("phonon-dos-projection-selector"), {target: {value: "0"}});
    view.rerender(<PhononDosPreviewPanel artifacts={items} selectedPoint={{frequencyIndex: 0, projectionIndex: 1}} onPointSelection={onPointSelection} plotlyLoader={loader} />);
    expect(screen.getByTestId("phonon-dos-projection-selector")).toHaveValue("0");
    fireEvent.click(screen.getByRole("button", {name: "清除选择"}));
    expect(onPointSelection).toHaveBeenLastCalledWith(null);
    await waitFor(() => expect(newPlot).toHaveBeenCalled());
  });
  it("restores and selects samples beyond the first numeric page with original indices", async () => {
    const payload = structuredClone(dos);
    payload.frequencies = Array.from({length: 601}, (_, index) => -1 + index / 100);
    payload.total_dos = payload.frequencies.map(() => 1);
    payload.projected_dos.forEach((projection: {values: number[]}) => {projection.values = payload.frequencies.map(() => 0.5);});
    const onPointSelection = vi.fn();
    render(<PhononDosPreviewPanel artifacts={artifacts(payload)} selectedPoint={{frequencyIndex: 600, projectionIndex: null}} onPointSelection={onPointSelection} plotlyLoader={async () => ({newPlot: vi.fn().mockResolvedValue(undefined), purge: vi.fn()})} />);
    fireEvent.click(screen.getByText("态密度数值"));
    expect(screen.getByRole("button", {name: "下一页"})).toBeDisabled();
    fireEvent.click(screen.getByRole("button", {name: "选择总态密度频率点 600"}));
    expect(onPointSelection).toHaveBeenLastCalledWith({frequencyIndex: 600, projectionIndex: null});
    fireEvent.click(screen.getByRole("button", {name: "上一页"}));
    expect(screen.getByRole("button", {name: "选择总态密度频率点 300"})).toBeVisible();
    expect(screen.queryByRole("button", {name: "选择总态密度频率点 600"})).toBeNull();
  });
  it("does not expose source-selection controls in a read-only report", () => {
    render(<PhononDosPreviewPanel artifacts={artifacts()} plotlyLoader={async () => ({newPlot: vi.fn().mockResolvedValue(undefined), purge: vi.fn()})} />);
    fireEvent.click(screen.getByText("态密度数值"));
    expect(screen.queryByRole("button", {name: /选择总态密度/})).toBeNull();
  });
  it("keeps serialized artifact payloads stable while restoring a selected frequency", async () => {
    const newPlot = vi.fn().mockResolvedValue(undefined);
    render(<PhononDosPreviewPanel artifacts={artifacts(JSON.stringify(dos))} selectedPoint={{frequencyIndex: 0, projectionIndex: 1}} onPointSelection={vi.fn()} plotlyLoader={async () => ({newPlot, purge: vi.fn()})} />);
    fireEvent.click(screen.getByText("态密度数值"));
    expect(screen.getByRole("button", {name: "选择原子 1 (Si)频率点 0"})).toHaveAttribute("aria-pressed", "true");
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(1));
  });
  it("uses the selected DOS and does not fabricate missing summary values", async () => {
    const selectedPayload = structuredClone(dos);
    selectedPayload.total_dos[1] += 0.01;
    selectedPayload.total_dos[2] -= 0.01;
    const selected = { id: "selected-dos", type: "phonon_dos_json", content: selectedPayload };
    const newPlot = vi.fn().mockResolvedValue(undefined);
    render(<PhononDosPreviewPanel artifacts={[...artifacts(), selected].map(artifact => artifact.id === "summary" ? { ...artifact, content: {} } : artifact)} selected={selected} plotlyLoader={async () => ({ newPlot, purge: vi.fn() })} />);
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(1));
    expect(newPlot.mock.calls[0][1][0].y).toEqual(selectedPayload.total_dos);
    expect(screen.getByTestId("phonon-dos-summary")).not.toHaveTextContent("NaN");
    expect(screen.getByTestId("phonon-dos-summary")).toHaveTextContent("未提供");
  });
  it("validates DOS, renders total and selected projection, and purges", async () => {
    const newPlot = vi.fn().mockResolvedValue(undefined);
    const purge = vi.fn();
    const view = render(<PhononDosPreviewPanel artifacts={artifacts()} plotlyLoader={async () => ({ newPlot, purge })} />);
    expect(screen.getByTestId("phonon-dos-schema")).toHaveTextContent("phase10h.phonon_dos.v1");
    expect(screen.getByTestId("phonon-dos-summary")).toHaveTextContent("完整");
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(1));
    expect(newPlot.mock.calls[0][1]).toHaveLength(1);
    fireEvent.change(screen.getByTestId("phonon-dos-projection-selector"), { target: { value: "0" } });
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(2));
    expect(newPlot.mock.calls[1][1]).toHaveLength(2);
    expect(newPlot.mock.calls[1][2].legend).toMatchObject({ yanchor: "bottom" });
    expect(newPlot.mock.calls[1][2].legend.y).toBeGreaterThan(1);
    expect(screen.getByTestId("phonon-dos-live-status")).toHaveTextContent("2 条曲线");
    view.unmount();
    expect(purge).toHaveBeenCalled();
  });

  it("keeps accessible table, negative classification, and JSON fallback", async () => {
    render(<PhononDosPreviewPanel artifacts={artifacts()} plotlyLoader={async () => ({ newPlot: vi.fn().mockResolvedValue(undefined), purge: vi.fn() })} />);
    expect(screen.getByText("态密度数值").closest("details")).not.toHaveAttribute("open");
    expect(screen.getByTestId("phonon-dos-schema")).not.toBeVisible();
    fireEvent.click(screen.getByText("态密度数值"));
    expect(screen.getByRole("table", { name: "声子态密度采样数值" })).toBeVisible();
    expect(screen.getAllByText("虚频").length).toBeGreaterThan(0);
    fireEvent.click(screen.getByText("数据与来源"));
    expect(screen.getByText("phonon_dos.json")).toBeInTheDocument();
    expect(screen.getByText("phonon_dos_summary.json")).toBeInTheDocument();
  });

  it("rejects executable metadata before loading Plotly", () => {
    const loader = vi.fn();
    const invalid = structuredClone(dos);
    invalid.source.url = "javascript:alert(1)";
    render(<PhononDosPreviewPanel artifacts={artifacts(invalid)} plotlyLoader={loader} />);
    expect(screen.getByTestId("phonon-dos-preview-invalid")).toHaveTextContent("PHONON_EXTERNAL_REFERENCE_FORBIDDEN");
    expect(loader).not.toHaveBeenCalled();
  });

  it("reports lazy chunk failure while retaining JSON access", async () => {
    render(<PhononDosPreviewPanel artifacts={artifacts()} plotlyLoader={async () => { throw new Error("chunk missing"); }} />);
    await waitFor(() => expect(screen.getByTestId("phonon-dos-plot-fallback")).toHaveTextContent("图表暂时无法显示"));
    expect(screen.getByRole("button", { name: "重新绘制图表" })).toBeEnabled();
    fireEvent.click(screen.getByText("数据与来源"));
    expect(screen.getByText("phonon_dos.json")).toBeVisible();
  });

  it("shows a deterministic warning for a source-guaranteed projection sum mismatch", async () => {
    const mismatch = structuredClone(dos);
    mismatch.projected_dos[0].values[0] += 1;
    const newPlot = vi.fn().mockResolvedValue(undefined);
    render(<PhononDosPreviewPanel artifacts={artifacts(mismatch)} plotlyLoader={async () => ({ newPlot, purge: vi.fn() })} />);
    expect(screen.getByTestId("phonon-dos-warnings")).toHaveTextContent("PHONON_PROJECTED_DOS_SUM_MISMATCH");
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(1));
  });

  it("refuses an application-owned preview budget overflow", () => {
    const mapped = mapPhononDosPlot({ frequencies: Array.from({ length: 130_000 }, (_, index) => index), total_dos: Array.from({ length: 130_000 }, () => 1), projected_dos: [{ values: Array.from({ length: 130_000 }, () => 1), projection_type: "species", species: "Si" }] }, 0);
    expect(mapped.ok).toBe(false);
    if (!mapped.ok) expect(mapped.message).toContain("PHONON_DOS_PREVIEW_LIMIT_EXCEEDED");
  });
});
