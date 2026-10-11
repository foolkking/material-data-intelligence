import "@testing-library/jest-dom/vitest";
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { usePhononPlot, type PhononPlotlyLoader } from "./use-phonon-plot";

const plot = (value = 1) => ({ ok: true as const, data: [{ x: [0, 1], y: [-value, value] }], layout: { yaxis: { title: "THz" } } });
function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>(done => { resolve = done; });
  return { promise, resolve };
}
function Preview({ spec, loader }: { spec: ReturnType<typeof plot>; loader: PhononPlotlyLoader }) {
  const state = usePhononPlot(spec, loader);
  return <><div data-testid="canvas" ref={state.hostRef} /><output data-testid="phase">{state.phase}</output><output data-testid="export">{state.exportState}</output><button onClick={state.retry}>retry</button><button disabled={!state.canExport} onClick={() => state.downloadPng("phonon")}>export</button></>;
}
const settle = async () => { await act(async () => { await Promise.resolve(); }); };
beforeEach(() => vi.useFakeTimers());
afterEach(() => { cleanup(); vi.useRealTimers(); vi.restoreAllMocks(); });

describe("phonon plot ownership", () => {
  it("bounds module loading and ignores a module that arrives after recovery", async () => {
    const late = deferred<{ newPlot: ReturnType<typeof vi.fn>; purge: ReturnType<typeof vi.fn> }>();
    const oldApi = { newPlot: vi.fn(), purge: vi.fn() };
    const newApi = { newPlot: vi.fn().mockResolvedValue(undefined), purge: vi.fn() };
    const loader = vi.fn().mockReturnValueOnce(late.promise).mockResolvedValue(newApi);
    render(<Preview spec={plot()} loader={loader} />);
    await settle();
    await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
    expect(screen.getByTestId("phase")).toHaveTextContent("timeout");
    expect(screen.getByTestId("canvas")).toBeEmptyDOMElement();
    fireEvent.click(screen.getByText("retry")); await settle();
    expect(screen.getByTestId("phase")).toHaveTextContent("rendered");
    late.resolve(oldApi); await settle();
    expect(oldApi.newPlot).not.toHaveBeenCalled();
    expect(newApi.newPlot).toHaveBeenCalledTimes(1);
  });

  it("detaches a stalled render before retry and purges late mutation only on its old target", async () => {
    const late = deferred<void>();
    const purge = vi.fn();
    const newPlot = vi.fn().mockImplementationOnce(async (host: HTMLElement) => { await late.promise; host.textContent = "late geometry"; }).mockImplementation(async (host: HTMLElement) => { host.textContent = "current geometry"; });
    render(<Preview spec={plot()} loader={vi.fn().mockResolvedValue({ newPlot, purge })} />); await settle();
    const old = newPlot.mock.calls[0][0];
    await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
    expect(old.isConnected).toBe(false);
    fireEvent.click(screen.getByText("retry")); await settle();
    const current = newPlot.mock.calls[1][0];
    expect(current).not.toBe(old);
    late.resolve(); await settle();
    expect(screen.getByTestId("canvas")).toHaveTextContent("current geometry");
    expect(purge).toHaveBeenCalledWith(old);
    expect(purge.mock.calls.some(([target]) => target === current)).toBe(false);
    expect(screen.getByTestId("phase")).toHaveTextContent("rendered");
  });

  it.each(["module", "render", "sync render"])("recovers from %s failure", async failure => {
    const newPlot = vi.fn().mockResolvedValue(undefined);
    const api = { newPlot, purge: vi.fn() };
    const loader = vi.fn().mockResolvedValue(api);
    if (failure === "module") loader.mockRejectedValueOnce(new Error("chunk unavailable"));
    else if (failure === "render") newPlot.mockRejectedValueOnce(new Error("render rejected"));
    else newPlot.mockImplementationOnce(() => { throw new Error("render threw"); });
    render(<Preview spec={plot()} loader={loader} />); await settle();
    expect(screen.getByTestId("phase")).toHaveTextContent("error");
    fireEvent.click(screen.getByText("retry")); await settle();
    expect(screen.getByTestId("phase")).toHaveTextContent("rendered");
  });

  it("isolates source replacement, Plotly mutations and unmount cleanup", async () => {
    const late = deferred<void>();
    const purge = vi.fn();
    const newPlot = vi.fn().mockImplementationOnce(() => late.promise).mockImplementation(async (_host, data, layout) => { data[0].y[0] = 999; layout.yaxis.title = "mutated"; });
    const loader = vi.fn().mockResolvedValue({ newPlot, purge });
    const first = plot(), second = plot(3);
    const view = render(<Preview spec={first} loader={loader} />); await settle();
    const old = newPlot.mock.calls[0][0];
    view.rerender(<Preview spec={second} loader={loader} />); await settle();
    const current = newPlot.mock.calls[1][0];
    expect(old.isConnected).toBe(false);
    expect(second.data[0].y).toEqual([-3, 3]);
    expect(second.layout.yaxis.title).toBe("THz");
    late.resolve(); await settle();
    expect(purge.mock.calls.some(([target]) => target === current)).toBe(false);
    view.unmount();
    expect(purge.mock.calls.some(([target]) => target === current)).toBe(true);
    expect(vi.getTimerCount()).toBe(0);
  });

  it("prevents duplicate PNG exports, bounds waiting and ignores late export completion", async () => {
    const late = deferred<void>();
    const downloadImage = vi.fn().mockReturnValueOnce(late.promise).mockRejectedValueOnce(new Error("download failed")).mockResolvedValue(undefined);
    const loader = vi.fn().mockResolvedValue({ newPlot: vi.fn().mockResolvedValue(undefined), purge: vi.fn(), downloadImage });
    render(<Preview spec={plot()} loader={loader} />); await settle();
    fireEvent.click(screen.getByText("export")); fireEvent.click(screen.getByText("export")); await settle();
    expect(downloadImage).toHaveBeenCalledTimes(1);
    expect(downloadImage).toHaveBeenCalledWith(expect.any(HTMLElement), expect.objectContaining({width: 800, height: 500, scale: 2}));
    await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
    expect(screen.getByTestId("export")).toHaveTextContent("failed");
    fireEvent.click(screen.getByText("export")); await settle();
    expect(screen.getByTestId("export")).toHaveTextContent("failed");
    late.resolve(); await settle();
    expect(screen.getByTestId("export")).toHaveTextContent("failed");
    fireEvent.click(screen.getByText("export")); await settle();
    expect(screen.getByTestId("export")).toHaveTextContent("idle");
    expect(downloadImage).toHaveBeenCalledTimes(3);
  });

  it("does not carry an export failure into a replacement source", async () => {
    const late = deferred<void>();
    const loader = vi.fn().mockResolvedValue({ newPlot: vi.fn().mockResolvedValue(undefined), purge: vi.fn(), downloadImage: vi.fn().mockReturnValue(late.promise) });
    const view = render(<Preview spec={plot()} loader={loader} />); await settle();
    fireEvent.click(screen.getByText("export")); await settle();
    view.rerender(<Preview spec={plot(2)} loader={loader} />); await settle();
    late.resolve(); await settle();
    expect(screen.getByTestId("export")).toHaveTextContent("idle");
    expect(screen.getByTestId("phase")).toHaveTextContent("rendered");
  });
});
