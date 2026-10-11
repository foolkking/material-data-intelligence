import React from "react";
import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { useClampedTitle } from "./use-clamped-title";

function Example({ title = "很长的材料样品实验记录名称" }: { title?: string }) {
  const name = useClampedTitle(title, true);
  return <><a href="#sample" {...name.events}><strong ref={name.titleRef}>{title}</strong></a>{name.tooltip}</>;
}
afterEach(() => vi.useRealTimers());
const clip = (element: Element) => {
  Object.defineProperty(element, "clientHeight", { configurable: true, value: 40 });
  Object.defineProperty(element, "scrollHeight", { configurable: true, value: 80 });
};

it("reveals only truncated names on keyboard focus and dismisses with Escape or blur", () => {
  render(<Example />);
  const link = screen.getByRole("link");
  fireEvent.focus(link);
  expect(screen.queryByRole("tooltip")).toBeNull();
  clip(link.firstElementChild!);
  fireEvent.focus(link);
  const tooltip = screen.getByRole("tooltip");
  expect(tooltip).toHaveTextContent(link.textContent!);
  expect(tooltip.parentElement).toBe(document.body);
  expect(link).toHaveAttribute("aria-describedby", tooltip.id);
  fireEvent.keyDown(document, { key: "Escape" });
  expect(screen.queryByRole("tooltip")).toBeNull();
  fireEvent.blur(link);
  fireEvent.focus(link);
  expect(screen.getByRole("tooltip")).toBeInTheDocument();
  fireEvent.blur(link);
  expect(screen.queryByRole("tooltip")).toBeNull();
});

it("lets the pointer enter the full name and removes stale popups after a name change", () => {
  vi.useFakeTimers();
  const { rerender, unmount } = render(<Example />);
  const link = screen.getByRole("link");
  clip(link.firstElementChild!);
  fireEvent.pointerEnter(link, { pointerType: "mouse" });
  act(() => vi.advanceTimersByTime(250));
  const tooltip = screen.getByRole("tooltip");
  fireEvent.pointerLeave(link);
  fireEvent.pointerEnter(tooltip);
  act(() => vi.advanceTimersByTime(200));
  expect(screen.getByRole("tooltip")).toBe(tooltip);
  rerender(<Example title="另一份数据" />);
  expect(screen.queryByRole("tooltip")).toBeNull();
  fireEvent.pointerEnter(screen.getByRole("link"));
  unmount();
  act(() => vi.runAllTimers());
  expect(screen.queryByRole("tooltip")).toBeNull();
});

it("dismisses the full name before the surrounding panel and keeps popup clicks inside it", () => {
  const outerEscape = vi.fn();
  const outerPointer = vi.fn();
  document.addEventListener("keydown", outerEscape);
  document.addEventListener("pointerdown", outerPointer);
  try {
    render(<Example />);
    const link = screen.getByRole("link");
    clip(link.firstElementChild!);
    fireEvent.focus(link);
    fireEvent.pointerDown(screen.getByRole("tooltip"));
    expect(outerPointer).not.toHaveBeenCalled();
    expect(screen.getByRole("tooltip")).toBeInTheDocument();
    fireEvent.keyDown(link, { key: "Escape" });
    expect(screen.queryByRole("tooltip")).toBeNull();
    expect(outerEscape).not.toHaveBeenCalled();
    fireEvent.keyDown(link, { key: "Escape" });
    expect(outerEscape).toHaveBeenCalledTimes(1);
  } finally {
    document.removeEventListener("keydown", outerEscape);
    document.removeEventListener("pointerdown", outerPointer);
  }
});
