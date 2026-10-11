import React from "react";
import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { useDataNavigator } from "./use-data-navigator";

let available = 1000;
function Example() {
  const navigator = useDataNavigator();
  return <section ref={navigator.workbenchRef} style={navigator.style} data-testid="workbench" data-collapsed={navigator.collapsed}>
    <button onClick={() => navigator.setCollapsed((value) => !value)}>目录</button>
    <div {...navigator.separatorProps} />
    <input aria-label="查看器搜索" defaultValue="SiO2" />
  </section>;
}
beforeEach(() => {
  localStorage.clear();
  available = 1000;
  vi.spyOn(HTMLElement.prototype, "clientWidth", "get").mockImplementation(() => available);
});
afterEach(() => vi.restoreAllMocks());

it("bounds keyboard resizing and restores the preferred width after a smaller viewport", () => {
  localStorage.setItem("mdi:data-directory-width", "460");
  render(<Example />);
  const divider = screen.getByRole("separator");
  expect(divider).toHaveAttribute("aria-valuenow", "460");
  available = 760;
  fireEvent(window, new Event("resize"));
  expect(divider).toHaveAttribute("aria-valuemax", "332");
  expect(divider).toHaveAttribute("aria-valuenow", "332");
  expect(localStorage.getItem("mdi:data-directory-width")).toBe("460");
  available = 1000;
  fireEvent(window, new Event("resize"));
  expect(divider).toHaveAttribute("aria-valuenow", "460");
  fireEvent.keyDown(divider, { key: "Home" });
  expect(divider).toHaveAttribute("aria-valuenow", "220");
  fireEvent.keyDown(divider, { key: "ArrowRight" });
  expect(divider).toHaveAttribute("aria-valuenow", "236");
  expect(localStorage.getItem("mdi:data-directory-width")).toBe("236");
  fireEvent.keyDown(divider, { key: "End" });
  expect(divider).toHaveAttribute("aria-valuenow", "480");
  fireEvent.doubleClick(divider);
  expect(divider).toHaveAttribute("aria-valuenow", "264");
});

it("keeps the viewer mounted across collapse and expansion and tolerates unusable storage", () => {
  localStorage.setItem("mdi:data-directory-width", "NaN");
  render(<Example />);
  const viewer = screen.getByRole("textbox");
  fireEvent.change(viewer, { target: { value: "CaO" } });
  fireEvent.click(screen.getByRole("button"));
  expect(screen.getByTestId("workbench")).toHaveAttribute("data-collapsed", "true");
  fireEvent.click(screen.getByRole("button"));
  expect(screen.getByRole("textbox")).toBe(viewer);
  expect(viewer).toHaveValue("CaO");
  vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => { throw new Error("storage disabled"); });
  fireEvent.keyDown(screen.getByRole("separator"), { key: "ArrowRight" });
  expect(screen.getByRole("separator")).toHaveAttribute("aria-valuenow", "280");
});

it("cancels a captured drag without persisting it, and persists only a completed drag", () => {
  render(<Example />);
  const divider = screen.getByRole("separator");
  let captured = false;
  divider.setPointerCapture = () => { captured = true; };
  divider.hasPointerCapture = () => captured;
  divider.releasePointerCapture = () => { captured = false; };
  const pointer = (type: string, x: number) => {
    const event = new Event(type, { bubbles: true });
    Object.assign(event, { pointerId: 1, button: 0, clientX: x });
    fireEvent(divider, event);
  };
  pointer("pointerdown", 300);
  pointer("pointermove", 410);
  expect(divider).toHaveAttribute("aria-valuenow", "374");
  fireEvent.keyDown(window, { key: "Escape" });
  expect(divider).toHaveAttribute("aria-valuenow", "264");
  expect(captured).toBe(false);
  expect(localStorage.getItem("mdi:data-directory-width")).toBeNull();
  pointer("pointerdown", 300);
  pointer("pointermove", 380);
  pointer("pointerup", 380);
  expect(localStorage.getItem("mdi:data-directory-width")).toBe("344");
  act(() => { available = 700; window.dispatchEvent(new Event("resize")); });
  expect(divider).toHaveAttribute("aria-valuenow", "272");
});
