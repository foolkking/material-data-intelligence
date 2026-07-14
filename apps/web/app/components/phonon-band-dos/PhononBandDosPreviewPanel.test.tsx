import "@testing-library/jest-dom/vitest";

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";

import { mapPhononBandDosPlot, PhononBandDosPreviewPanel } from "./PhononBandDosPreviewPanel";

const root = resolve(__dirname, "../../../../..");
const evidence = resolve(root, "docs/phase10h/evidence/phase10h3_combined_band_dos/artifacts");
const json = (name: string) => JSON.parse(readFileSync(resolve(evidence, name), "utf8"));
const payloads = {
  combined: json("phonon_band_dos.json"), summary: json("phonon_band_dos_summary.json"),
  report: json("phonon_band_dos_compatibility_report.json"), plot: json("phonon_band_dos_plot.json"),
  table: json("phonon_band_dos_table.json"), manifest: json("phonon_band_dos_manifest.json"),
};

function artifacts(combined: unknown = payloads.combined) {
  return [
    {id: "combined", type: "phonon_band_dos_json", name: "phonon_band_dos.json", content: combined},
    {id: "summary", type: "phonon_summary_json", name: "phonon_band_dos_summary.json", content: payloads.summary},
    {id: "report", type: "phonon_compatibility_json", name: "phonon_band_dos_compatibility_report.json", content: payloads.report},
    {id: "plot", type: "plotly_json", name: "phonon_band_dos_plot.json", content: payloads.plot},
    {id: "table", type: "table_json", name: "phonon_band_dos_table.json", content: payloads.table},
    {id: "manifest", type: "phonon_manifest_json", name: "phonon_band_dos_manifest.json", content: payloads.manifest},
  ];
}

afterEach(() => vi.restoreAllMocks());

describe("PhononBandDosPreviewPanel", () => {
  it("renders one shared-axis figure, selects projected DOS, exports PNG, and purges", async () => {
    const newPlot = vi.fn().mockResolvedValue(undefined);
    const purge = vi.fn();
    const downloadImage = vi.fn().mockResolvedValue(undefined);
    const view = render(<PhononBandDosPreviewPanel artifacts={artifacts()} plotlyLoader={async () => ({newPlot, purge, downloadImage})} />);
    expect(screen.getByTestId("phonon-band-dos-schema")).toHaveTextContent("phase10h.phonon_band_dos.v1");
    expect(screen.getByTestId("phonon-band-dos-summary")).toHaveTextContent("compatible");
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(1));
    const firstLayout = newPlot.mock.calls[0][2];
    expect(firstLayout.xaxis.domain).toEqual([0, 0.72]);
    expect(firstLayout.xaxis2.domain).toEqual([0.78, 1]);
    expect(firstLayout.yaxis.title.text).toBe("Frequency (THz)");
    expect(newPlot.mock.calls[0][1]).toHaveLength(7);
    fireEvent.change(screen.getByTestId("phonon-band-dos-projection-selector"), {target: {value: "atom:0"}});
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(2));
    expect(newPlot.mock.calls[1][1]).toHaveLength(8);
    expect(screen.getByTestId("phonon-band-dos-live-status")).toHaveTextContent("one shared frequency axis");
    fireEvent.click(screen.getByTestId("phonon-band-dos-download-png"));
    expect(downloadImage).toHaveBeenCalledWith(expect.any(HTMLElement), expect.objectContaining({format: "png", width: 1600, height: 1000}));
    view.unmount();
    expect(purge).toHaveBeenCalled();
  });

  it("keeps compatibility, bounded data, and JSON tabs keyboard accessible", async () => {
    render(<PhononBandDosPreviewPanel artifacts={artifacts()} plotlyLoader={async () => ({newPlot: vi.fn().mockResolvedValue(undefined), purge: vi.fn()})} />);
    fireEvent.click(screen.getByRole("tab", {name: "Compatibility"}));
    expect(screen.getByRole("table", {name: "Band and DOS compatibility checks"})).toBeInTheDocument();
    expect(screen.getByTestId("phonon-band-dos-compatibility-status")).toHaveTextContent("compatible");
    fireEvent.click(screen.getByRole("tab", {name: "Band data"}));
    expect(screen.getByRole("table", {name: "Combined display band samples"})).toBeInTheDocument();
    fireEvent.click(screen.getByRole("tab", {name: "DOS data"}));
    expect(screen.getByRole("table", {name: "Combined display DOS samples"})).toBeInTheDocument();
    fireEvent.click(screen.getByRole("tab", {name: "Artifact JSON"}));
    expect(screen.getByText("phonon_band_dos.json")).toBeInTheDocument();
    expect(screen.getByText("phonon_band_dos_manifest.json")).toBeInTheDocument();
  });

  it("rejects an invalid combined bundle before Plotly initialization", () => {
    const loader = vi.fn();
    const invalid = structuredClone(payloads.combined);
    invalid.tool_id = "phonon.eigenvector";
    render(<PhononBandDosPreviewPanel artifacts={artifacts(invalid)} plotlyLoader={loader} />);
    expect(screen.getByTestId("phonon-band-dos-preview-invalid")).toHaveTextContent("PHONON_BAND_DOS_SCHEMA_INVALID");
    expect(loader).not.toHaveBeenCalled();
  });

  it("reports lazy chunk failure, retries, and retains non-plot tabs", async () => {
    const newPlot = vi.fn().mockResolvedValue(undefined);
    const loader = vi.fn().mockRejectedValueOnce(new Error("chunk missing")).mockResolvedValue({newPlot, purge: vi.fn()});
    render(<PhononBandDosPreviewPanel artifacts={artifacts()} plotlyLoader={loader} />);
    await waitFor(() => expect(screen.getByTestId("phonon-band-dos-plot-fallback")).toHaveTextContent("PHONON_BAND_DOS_PLOT_LOAD_FAILED"));
    fireEvent.click(screen.getByRole("button", {name: "Retry plot"}));
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(1));
    expect(screen.getByRole("tab", {name: "Compatibility"})).toBeEnabled();
  });

  it("downloads combined JSON locally without a network request", () => {
    const createObjectURL = vi.fn().mockReturnValue("blob:combined");
    const revokeObjectURL = vi.fn();
    Object.defineProperty(URL, "createObjectURL", {value: createObjectURL, configurable: true});
    Object.defineProperty(URL, "revokeObjectURL", {value: revokeObjectURL, configurable: true});
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    render(<PhononBandDosPreviewPanel artifacts={artifacts()} plotlyLoader={async () => ({newPlot: vi.fn().mockResolvedValue(undefined), purge: vi.fn()})} />);
    fireEvent.click(screen.getByTestId("phonon-band-dos-download-json"));
    expect(createObjectURL).toHaveBeenCalledTimes(1);
    expect(click).toHaveBeenCalledTimes(1);
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:combined");
  });

  it("refuses application-owned plot budget and unknown projection identities", () => {
    const refused = structuredClone(payloads.plot);
    refused.display.mode = "refused";
    refused.display.reason = "PHONON_BAND_DOS_PLOT_BUDGET_EXCEEDED";
    expect(mapPhononBandDosPlot(refused).ok).toBe(false);
    const unknown = mapPhononBandDosPlot(payloads.plot, "species:Na");
    expect(unknown.ok).toBe(false);
  });
});
