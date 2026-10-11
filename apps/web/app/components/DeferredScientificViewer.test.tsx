import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { renderToString } from "react-dom/server";
import { afterEach, expect, it, vi } from "vitest";
import { createDeferredScientificViewer } from "../../scientific-viewers/DeferredScientificViewer";

afterEach(() => { vi.useRealTimers(); vi.restoreAllMocks(); });

it("defers viewer imports until client mount and caches code without caching source props", async () => {
  const load = vi.fn(async () => ({ default: ({ source }: { source: string }) => <p>Source {source}</p> }));
  const Viewer = createDeferredScientificViewer(load);
  expect(renderToString(<Viewer source="server" />)).toContain("正在打开科学查看器");
  expect(load).not.toHaveBeenCalled();
  const view = render(<><Viewer source="first" /><Viewer source="second" /></>);
  await screen.findByText("Source first");
  expect(screen.getByText("Source second")).toBeVisible();
  expect(load).toHaveBeenCalledOnce();
  view.unmount();
  render(<Viewer source="third" />);
  expect(await screen.findByText("Source third")).toBeVisible();
  expect(screen.queryByText("Source first")).not.toBeInTheDocument();
  expect(load).toHaveBeenCalledOnce();
});

it("retries a rejected component import locally while retaining sibling content", async () => {
  const load = vi.fn().mockRejectedValueOnce(new Error("private-raw-load-details"))
    .mockResolvedValue({ default: () => <p>Recovered plot</p> });
  const Viewer = createDeferredScientificViewer(load);
  render(<><h1>Saved report</h1><input aria-label="Filter" defaultValue="Fe" /><Viewer /></>);
  expect(await screen.findByRole("alert")).toHaveTextContent("查看器未能加载");
  expect(screen.getByRole("heading", { name: "Saved report" })).toBeVisible();
  expect(screen.queryByText(/private-raw/)).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "重试查看器" }));
  expect(await screen.findByText("Recovered plot")).toBeVisible();
  expect(screen.getByRole("textbox", { name: "Filter" })).toHaveValue("Fe");
  expect(load).toHaveBeenCalledTimes(2);
});

it("times out stalled imports and rejects a late obsolete component after retry", async () => {
  vi.useFakeTimers();
  let finish!: (value: unknown) => void;
  const load = vi.fn().mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }))
    .mockResolvedValue({ default: () => <p>Current component</p> });
  const Viewer = createDeferredScientificViewer(load);
  await act(async () => { render(<Viewer />); });
  await act(async () => { vi.advanceTimersByTime(10_000); });
  expect(screen.getByRole("alert")).toHaveTextContent("查看器加载超时");
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "重试查看器" })); });
  expect(screen.getByText("Current component")).toBeVisible();
  await act(async () => finish({ default: () => <p>Obsolete component</p> }));
  expect(screen.queryByText("Obsolete component")).not.toBeInTheDocument();
});

it("contains render exceptions and retries without re-importing successful code", async () => {
  vi.spyOn(console, "error").mockImplementation(() => undefined);
  let broken = true;
  const load = vi.fn(async () => ({ default: () => {
    if (broken) throw new Error("private-raw-render-details");
    return <p>Recovered viewer</p>;
  } }));
  const Viewer = createDeferredScientificViewer(load);
  render(<><p>Saved metrics</p><Viewer /></>);
  expect(await screen.findByRole("alert")).toHaveTextContent("查看器暂时无法显示");
  expect(screen.getByText("Saved metrics")).toBeVisible();
  expect(screen.queryByText(/private-raw/)).not.toBeInTheDocument();
  broken = false;
  fireEvent.click(screen.getByRole("button", { name: "重试查看器" }));
  expect(await screen.findByText("Recovered viewer")).toBeVisible();
  expect(load).toHaveBeenCalledOnce();
});

it("resets an error on exact source changes and renders the new props", async () => {
  vi.spyOn(console, "error").mockImplementation(() => undefined);
  const load = vi.fn(async () => ({ default: ({ source }: { source: string }) => {
    if (source === "broken-version") throw new Error("invalid view");
    return <p>{source}</p>;
  } }));
  const Viewer = createDeferredScientificViewer(load, { sourceKey: props => props.source });
  const view = render(<Viewer source="broken-version" />);
  await screen.findByRole("alert");
  view.rerender(<Viewer source="new-version" />);
  expect(await screen.findByText("new-version")).toBeVisible();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  expect(load).toHaveBeenCalledOnce();
});

it("keeps polling prop changes from restarting an in-flight import", async () => {
  let finish!: (value: { default: (props: { source: string }) => React.ReactNode }) => void;
  const load = vi.fn(() => new Promise<{ default: (props: { source: string }) => React.ReactNode }>(resolve => { finish = resolve; }));
  const Viewer = createDeferredScientificViewer(load);
  const view = render(<Viewer source="before" />);
  await waitFor(() => expect(load).toHaveBeenCalledOnce());
  view.rerender(<Viewer source="after" />);
  await act(async () => finish({ default: ({ source }) => <p>{source}</p> }));
  expect(screen.getByText("after")).toBeVisible();
  expect(load).toHaveBeenCalledOnce();
});

it("does not render a late import or a timeout after unmount", async () => {
  vi.useFakeTimers();
  let finish!: (value: unknown) => void;
  const load = vi.fn(() => new Promise<{ default: () => React.ReactNode }>(resolve => { finish = resolve as typeof finish; }));
  const Viewer = createDeferredScientificViewer(load);
  let view!: ReturnType<typeof render>;
  await act(async () => { view = render(<Viewer />); });
  view.unmount();
  await act(async () => { vi.advanceTimersByTime(10_000); finish({ default: () => <p>Late viewer</p> }); });
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  expect(screen.queryByText("Late viewer")).not.toBeInTheDocument();
});
