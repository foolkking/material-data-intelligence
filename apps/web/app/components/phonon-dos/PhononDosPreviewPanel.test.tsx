import "@testing-library/jest-dom/vitest";

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it, vi } from "vitest";

import { mapPhononDosPlot, PhononDosPreviewPanel } from "./PhononDosPreviewPanel";

const root = resolve(__dirname, "../../../../..");
const dos = JSON.parse(readFileSync(resolve(root, "docs/phase10h/fixtures/phonon_contract/projected_dos.json"), "utf8"));
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
  it("validates DOS, renders total and selected projection, and purges", async () => {
    const newPlot = vi.fn().mockResolvedValue(undefined);
    const purge = vi.fn();
    const view = render(<PhononDosPreviewPanel artifacts={artifacts()} plotlyLoader={async () => ({ newPlot, purge })} />);
    expect(screen.getByTestId("phonon-dos-schema")).toHaveTextContent("phase10h.phonon_dos.v1");
    expect(screen.getByTestId("phonon-dos-summary")).toHaveTextContent("complete");
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(1));
    expect(newPlot.mock.calls[0][1]).toHaveLength(1);
    fireEvent.change(screen.getByTestId("phonon-dos-projection-selector"), { target: { value: "0" } });
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(2));
    expect(newPlot.mock.calls[1][1]).toHaveLength(2);
    expect(screen.getByTestId("phonon-dos-live-status")).toHaveTextContent("2 visible series");
    view.unmount();
    expect(purge).toHaveBeenCalled();
  });

  it("keeps accessible table, negative classification, and JSON fallback", async () => {
    render(<PhononDosPreviewPanel artifacts={artifacts()} plotlyLoader={async () => ({ newPlot: vi.fn().mockResolvedValue(undefined), purge: vi.fn() })} />);
    fireEvent.click(screen.getByRole("tab", { name: "DOS table" }));
    expect(screen.getByRole("table", { name: "Phonon density of states samples" })).toBeInTheDocument();
    expect(screen.getAllByText("imaginary").length).toBeGreaterThan(0);
    fireEvent.click(screen.getByRole("tab", { name: "Canonical JSON" }));
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
    await waitFor(() => expect(screen.getByTestId("phonon-dos-plot-fallback")).toHaveTextContent("PHONON_DOS_PLOT_LOAD_FAILED"));
    expect(screen.getByRole("tab", { name: "Canonical JSON" })).toBeEnabled();
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
