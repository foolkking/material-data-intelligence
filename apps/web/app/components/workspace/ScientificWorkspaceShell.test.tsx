import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getWorkspace } from "../../lib/workspace-api";
import { ScientificWorkspaceShell } from "./ScientificWorkspaceShell";
import { workspaceSnapshotFixture } from "./workspace-test-fixture";

vi.mock("../../lib/workspace-api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../lib/workspace-api")>();
  return { ...actual, getWorkspace: vi.fn() };
});

const getWorkspaceMock = vi.mocked(getWorkspace);

beforeEach(() => {
  window.history.replaceState({}, "", "/workspaces/workspace_demo");
  getWorkspaceMock.mockReset();
  getWorkspaceMock.mockResolvedValue({ data: workspaceSnapshotFixture(), status: 200, etag: "etag", idempotentReplay: null });
});

describe("Phase 10M-2 ScientificWorkspaceShell", () => {
  it("loads metadata-first and renders the sealed shell with one active panel", async () => {
    render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    expect(screen.getByRole("heading", { name: "Loading Workspace" })).not.toBeNull();
    expect(await screen.findByTestId("scientific-workspace-shell")).not.toBeNull();
    expect(screen.getByRole("navigation", { name: "Workspace sections" })).not.toBeNull();
    expect(screen.getByRole("heading", { name: "Analysis overview" })).not.toBeNull();
    expect(screen.getAllByRole("button").filter((button) => button.getAttribute("aria-current") === "page")).toHaveLength(1);
    expect(getWorkspaceMock).toHaveBeenCalledWith("workspace_demo", expect.objectContaining({ signal: expect.any(AbortSignal) }));
  });

  it("uses exact panel deep links and restores browser history", async () => {
    window.history.replaceState({}, "", "/workspaces/workspace_demo?panel=panel_data");
    const user = userEvent.setup();
    render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    expect(await screen.findByRole("heading", { name: "Dataset context" })).not.toBeNull();
    await user.click(screen.getByRole("button", { name: /Results/ }));
    expect(screen.getByRole("heading", { name: "Scientific results" })).not.toBeNull();
    expect(window.location.search).toBe("?panel=panel_results");
    window.history.back();
    window.dispatchEvent(new PopStateEvent("popstate"));
    await waitFor(() => expect(screen.getByRole("heading", { name: "Dataset context" })).not.toBeNull());
  });

  it("reports an unknown panel without choosing a substitute", async () => {
    window.history.replaceState({}, "", "/workspaces/workspace_demo?panel=panel_invented");
    render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    const alert = await screen.findByTestId("workspace-invalid-panel");
    expect(alert.textContent).toContain("panel_invented");
    expect(screen.getByRole("heading", { name: "No active panel" })).not.toBeNull();
  });

  it.each(["RUNNING", "PARTIAL_RESULTS", "FAILED", "STALE", "LEGACY_READ_ONLY"] as const)("projects %s as a typed Workspace state", async (status) => {
    getWorkspaceMock.mockResolvedValue({ data: workspaceSnapshotFixture(status), status: 200, etag: "etag", idempotentReplay: null });
    render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    expect((await screen.findAllByText(status)).length).toBeGreaterThan(0);
    expect(screen.getByRole("status", { name: "Workspace source state" }).textContent).toContain("Exact historical bindings are preserved");
  });

  it("renders unsupported content as inert text", async () => {
    const snapshot = workspaceSnapshotFixture();
    snapshot.panels[0].state = "CONTRACT_UNSUPPORTED";
    snapshot.panels[0].unsupportedReason = '<script>window.__workspaceInjected=true</script><iframe src="https://example.invalid">';
    getWorkspaceMock.mockResolvedValue({ data: snapshot, status: 200, etag: "etag", idempotentReplay: null });
    const { container } = render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    expect(await screen.findByText(snapshot.panels[0].unsupportedReason)).not.toBeNull();
    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelector("iframe")).toBeNull();
  });

  it("opens the inspector, moves focus, and closes with Escape", async () => {
    const user = userEvent.setup();
    render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    await screen.findByTestId("scientific-workspace-shell");
    await user.click(screen.getByRole("button", { name: "Inspector" }));
    const dialog = screen.getByRole("dialog", { name: "Context inspector" });
    const close = within(dialog).getByRole("button", { name: "Close inspector" });
    expect(close).toHaveFocus();
    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog", { name: "Context inspector" })).toBeNull();
    expect(screen.getByRole("button", { name: "Inspector" })).toHaveFocus();
  });

  it("opens the bounded mobile context drawer and switches one active panel", async () => {
    const user = userEvent.setup();
    render(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    await screen.findByTestId("scientific-workspace-shell");
    await user.click(screen.getByRole("button", { name: "Open data context" }));
    const drawer = screen.getByRole("dialog", { name: "Data context drawer" });
    await user.click(within(drawer).getByRole("button", { name: "Scientific results" }));
    expect(screen.queryByRole("dialog", { name: "Data context drawer" })).toBeNull();
    expect(screen.getByRole("heading", { name: "Scientific results" })).not.toBeNull();
  });

  it("aborts stale metadata requests when the route identity changes", async () => {
    let firstSignal: AbortSignal | undefined;
    getWorkspaceMock
      .mockImplementationOnce((_workspaceId, options) => {
        firstSignal = options?.signal;
        return new Promise(() => undefined);
      })
      .mockResolvedValueOnce({ data: workspaceSnapshotFixture(), status: 200, etag: "etag", idempotentReplay: null });
    const { rerender } = render(<ScientificWorkspaceShell workspaceId="workspace_old" />);
    await waitFor(() => expect(firstSignal).toBeDefined());
    rerender(<ScientificWorkspaceShell workspaceId="workspace_demo" />);
    await screen.findByTestId("scientific-workspace-shell");
    expect(firstSignal?.aborted).toBe(true);
  });

  it("renders typed not-found and bounded error states", async () => {
    getWorkspaceMock.mockRejectedValueOnce(Object.assign(new Error("missing"), { status: 404 }));
    const { rerender } = render(<ScientificWorkspaceShell workspaceId="missing" />);
    expect(await screen.findByRole("heading", { name: "Workspace not found" })).not.toBeNull();
    getWorkspaceMock.mockRejectedValueOnce(new Error("private\nstack\tmessage"));
    rerender(<ScientificWorkspaceShell workspaceId="error" />);
    expect(await screen.findByRole("heading", { name: "Workspace unavailable" })).not.toBeNull();
    expect(screen.getByText("private stack message")).not.toBeNull();
  });
});
