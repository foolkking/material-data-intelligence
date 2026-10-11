import "@testing-library/jest-dom/vitest";

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it, vi } from "vitest";

import { mapPhononBandPlot, phononAnimationHandoff, PhononBandPreviewPanel } from "./PhononBandPreviewPanel";
import { phononAnimationFixture } from "../phonon-animation/phononAnimationTestFixture";

const root = resolve(__dirname, "../../../../..");
const stable = JSON.parse(readFileSync(resolve(root, "tests/fixtures/phonon_contract/stable_band.json"), "utf8"));
const summary = JSON.parse(readFileSync(resolve(root, "tests/fixtures/phonon_contract/phonon_summary.json"), "utf8"));
const manifest = JSON.parse(readFileSync(resolve(root, "tests/fixtures/phonon_contract/phonon_manifest.json"), "utf8"));

function artifacts(payload: unknown = stable) {
  return [
    { id: "band", type: "phonon_band_json", name: "phonon_band.json", content: payload },
    { id: "summary", type: "phonon_summary_json", name: "phonon_summary.json", content: summary },
    { id: "manifest", type: "phonon_manifest_json", name: "phonon_manifest.json", content: manifest },
  ];
}

describe("PhononBandPreviewPanel", () => {
  it("selects an original q point and branch from the keyboard without remounting the plot", async () => {
    const newPlot = vi.fn().mockResolvedValue(undefined), select = vi.fn();
    const source = artifacts(), loader = async () => ({newPlot, purge: vi.fn()});
    const view = render(<PhononBandPreviewPanel artifacts={source} onPointSelection={select} plotlyLoader={loader} />);
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(1));
    fireEvent.click(screen.getByText("能带数值", {selector: "summary"}));
    fireEvent.click(screen.getByRole("button", {name: "选择 q 点 1、分支 2"}));
    expect(select).toHaveBeenLastCalledWith({qpointIndex: 1, branchIndex: 2});
    view.rerender(<PhononBandPreviewPanel artifacts={source} selectedPoint={{qpointIndex: 1, branchIndex: 2}} onPointSelection={select} plotlyLoader={loader} />);
    expect(screen.getByRole("button", {name: "选择 q 点 1、分支 2"})).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText("已选 q 点 1 · 分支 2")).toBeVisible();
    expect(newPlot).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByRole("button", {name: "清除选择"}));
    expect(select).toHaveBeenLastCalledWith(null);
  });
  it("retains both labels at a disconnected path boundary without joining curves", () => {
    const discontinuous = JSON.parse(readFileSync(resolve(root, "tests/fixtures/phonon_contract/discontinuous_band.json"), "utf8"));
    const mapped = mapPhononBandPlot(discontinuous);
    expect(mapped.ok).toBe(true);
    if (!mapped.ok) return;
    expect(mapped.layout.xaxis).toMatchObject({ ticktext: ["Γ", "X", "L｜Γ", "M"] });
    expect(mapped.data).toHaveLength(12);
    expect(mapped.data[0]).toMatchObject({ x: discontinuous.qpoints.slice(0, 3).map((point: { distance: number }) => point.distance), y: discontinuous.branches[0].frequencies.slice(0, 3) });
    expect(mapped.data[1]).toMatchObject({ x: discontinuous.qpoints.slice(3).map((point: { distance: number }) => point.distance), y: discontinuous.branches[0].frequencies.slice(3) });
  });
  it("renders the explicitly selected band instead of the first same-type sibling", async () => {
    const selectedPayload = structuredClone(stable);
    selectedPayload.branches[0].frequencies[1] = 1.125;
    const selected = { id: "selected-band", type: "phonon_band_json", content: selectedPayload };
    const newPlot = vi.fn().mockResolvedValue(undefined);
    render(<PhononBandPreviewPanel artifacts={[...artifacts(), selected]} selected={selected} plotlyLoader={async () => ({ newPlot, purge: vi.fn() })} />);
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(1));
    expect(newPlot.mock.calls[0][1][0].y).toEqual([0, 1.125, 1.5]);
    expect(screen.queryByTestId("phonon-band-animation-handoff")).not.toBeInTheDocument();
  });
  it("validates canonical data, renders local Plotly traces, and purges on unmount", async () => {
    const newPlot = vi.fn().mockResolvedValue(undefined);
    const purge = vi.fn();
    const view = render(<PhononBandPreviewPanel artifacts={artifacts()} plotlyLoader={async () => ({ newPlot, purge })} />);
    expect(screen.getByTestId("phonon-band-schema")).toHaveTextContent("phase10h.phonon_band.v1");
    expect(screen.getByTestId("phonon-band-summary")).toHaveTextContent("6");
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(1));
    const traces = newPlot.mock.calls[0][1] as Array<{ y: number[] }>;
    expect(traces).toHaveLength(6);
    expect(traces[0].y).toEqual([0, 1, 1.5]);
    expect(screen.getByTestId("phonon-band-live-status")).toHaveTextContent("已显示 6 条分支");
    view.unmount();
    expect(purge).toHaveBeenCalledTimes(1);
  });

  it("keeps accessible table and canonical JSON alongside the plot", async () => {
    const newPlot = vi.fn().mockResolvedValue(undefined);
    render(<PhononBandPreviewPanel artifacts={artifacts()} plotlyLoader={async () => ({ newPlot, purge: vi.fn() })} />);
    await waitFor(() => expect(newPlot).toHaveBeenCalledTimes(1));
    const target = newPlot.mock.calls[0][0];
    expect(screen.getByText("能带数值").closest("details")).not.toHaveAttribute("open");
    expect(screen.getByTestId("phonon-band-schema")).not.toBeVisible();
    fireEvent.click(screen.getByText("能带数值"));
    expect(screen.getByRole("table", { name: "声子能带采样数值" })).toBeVisible();
    expect(screen.getAllByRole("row")).toHaveLength(19);
    expect(screen.getByRole("columnheader", { name: "q 坐标" })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "类型" })).toBeInTheDocument();
    fireEvent.click(screen.getByText("数据与来源"));
    expect(screen.getByText("phonon_band.json")).toBeInTheDocument();
    expect(screen.getByText("phonon_manifest.json")).toBeInTheDocument();
    expect(newPlot).toHaveBeenCalledTimes(1);
    expect(target.isConnected).toBe(true);
  });

  it("rejects invalid or executable metadata before loading Plotly", () => {
    const loader = vi.fn();
    const invalid = structuredClone(stable);
    invalid.source.url = "javascript:alert(1)";
    render(<PhononBandPreviewPanel artifacts={artifacts(invalid)} plotlyLoader={loader} />);
    expect(screen.getByTestId("phonon-band-preview-invalid")).toHaveTextContent("PHONON_EXTERNAL_REFERENCE_FORBIDDEN");
    expect(loader).not.toHaveBeenCalled();
  });

  it("reports chunk-load failure without losing the canonical preview tabs", async () => {
    render(<PhononBandPreviewPanel artifacts={artifacts()} plotlyLoader={async () => { throw new Error("chunk missing"); }} />);
    await waitFor(() => expect(screen.getByTestId("phonon-band-plot-fallback")).toHaveTextContent("图表暂时无法显示"));
    expect(screen.getByRole("button", { name: "重新绘制图表" })).toBeEnabled();
    fireEvent.click(screen.getByText("数据与来源"));
    expect(screen.getByText("phonon_band.json")).toBeVisible();
  });

  it("refuses mappings that exceed the application-owned trace budget", () => {
    const mapped = mapPhononBandPlot({ qpoints: Array.from({ length: 2 }, (_, index) => ({ index, distance: index })), segments: Array.from({ length: 257 }, (_, index) => ({ segment_index: index, start_qpoint_index: 0, end_qpoint_index: 1 })), branches: Array.from({ length: 16 }, (_, branch_index) => ({ branch_index, frequencies: [0, 1] })) });
    expect(mapped.ok).toBe(false);
    if (!mapped.ok) expect(mapped.message).toContain("PHONON_BAND_PREVIEW_LIMIT_EXCEEDED");
  });

  it("enables handoff only for the exact band hash and mode identity",()=>{const animation=phononAnimationFixture();const hash=animation.source.band_sha256;const linked={id:"band",type:"phonon_band_json",name:"phonon_band.json",content:stable,sha256:hash};expect(phononAnimationHandoff(stable,linked,animation)).toMatchObject({ok:true,qpointIndex:1,branchIndex:3,modeId:animation.mode.mode.mode_id});expect(phononAnimationHandoff(stable,{...linked,sha256:"f".repeat(64)},animation)).toEqual({ok:false,code:"PHONON_ANIMATION_BAND_HASH_MISMATCH"});expect(phononAnimationHandoff(stable,linked,null)).toEqual({ok:false,code:"PHONON_ANIMATION_EIGENVECTOR_UNAVAILABLE"});});

  it("shows an enabled exact-mode handoff without frequency search",()=>{const animation=phononAnimationFixture();render(<><div data-testid="phonon-animation-preview-panel"/><PhononBandPreviewPanel artifacts={[...artifacts(),{id:"animation",type:"phonon_animation_json",name:"phonon_animation.json",content:animation}] .map((artifact)=>artifact.name==="phonon_band.json"?{...artifact,sha256:animation.source.band_sha256}:artifact)} plotlyLoader={async()=>({newPlot:vi.fn().mockResolvedValue(undefined),purge:vi.fn()})}/></>);expect(screen.getByTestId("phonon-band-animation-handoff")).toHaveTextContent("已关联 q 点");expect(screen.getByRole("button",{name:"查看振动动画"})).toBeEnabled();});
});
