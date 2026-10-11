import { fireEvent, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, it, vi } from "vitest";

import { BrillouinZoneLabels } from "./BrillouinZoneLabels";

afterEach(() => vi.restoreAllMocks());

function sizeCanvas(width = 320, height = 400) {
  vi.spyOn(HTMLElement.prototype, "clientWidth", "get").mockReturnValue(width);
  vi.spyOn(HTMLElement.prototype, "clientHeight", "get").mockReturnValue(height);
  vi.spyOn(HTMLElement.prototype, "offsetWidth", "get").mockReturnValue(44);
  vi.spyOn(HTMLElement.prototype, "offsetHeight", "get").mockReturnValue(44);
}

it("keeps coincident point identities independently selectable by keyboard", async () => {
  sizeCanvas();
  const select = vi.fn();
  render(<BrillouinZoneLabels points={[{ id: "gamma", text: "Γ", x: 160, y: 180 }, { id: "r", text: "R", x: 160, y: 180 }]} onSelect={select} />);
  const gamma = screen.getByRole("button", { name: "Γ" });
  const r = screen.getByRole("button", { name: "R" });
  expect(gamma.style.left + gamma.style.top).not.toBe(r.style.left + r.style.top);
  expect(gamma.tabIndex).toBe(0);
  expect(r.tabIndex).toBe(0);
  gamma.focus();
  await userEvent.keyboard("{Enter}");
  r.focus();
  await userEvent.keyboard("{Enter}");
  expect(select.mock.calls).toEqual([["gamma"], ["r"]]);
});

it("keeps focus on the same canonical point while the camera moves", () => {
  sizeCanvas();
  const select = vi.fn();
  const { rerender } = render(<BrillouinZoneLabels points={[{ id: "gamma", text: "Γ", x: 160, y: 180 }]} onSelect={select} />);
  const button = screen.getByRole("button", { name: "Γ" });
  button.focus();
  rerender(<BrillouinZoneLabels points={[{ id: "gamma", text: "Γ", x: 80, y: 100 }]} selectedId="gamma" onSelect={select} />);
  expect(document.activeElement).toBe(button);
  expect(button).toHaveAttribute("aria-pressed", "true");
});

it("makes unplaceable point labels available in a compact picker", () => {
  sizeCanvas(90, 90);
  const select = vi.fn();
  render(<BrillouinZoneLabels points={Array.from({ length: 8 }, (_, id) => ({ id: String(id), text: `P${id}`, x: 45, y: 45 }))} onSelect={select} />);
  const summary = screen.getByText(/更多高对称点/u);
  fireEvent.click(summary);
  const picker = summary.closest("details")!;
  const choices = within(picker).getAllByRole("button");
  fireEvent.click(choices[0]);
  expect(select).toHaveBeenCalledWith(choices[0].textContent!.slice(1));
});
