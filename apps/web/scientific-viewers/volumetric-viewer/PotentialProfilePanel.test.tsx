import "@testing-library/jest-dom/vitest";
import { useState } from "react";
import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import type { PotentialProfile } from "./electrostaticPotentialProduct";
import { PotentialProfilePanel } from "./PotentialProfilePanel";

function profile(count = 32): PotentialProfile {
  return { profileId: "profile", profileHash: "hash", fieldHash: "field", axis: "lattice_axis_0", formulaId: "POTENTIAL_PLANAR_AVERAGE_V1", gauge: "source_native", unit: "electronvolt", points: Array.from({ length: count }, (_, index) => ({ index, fractional: index / count, pathLengthAngstrom: index / 4, sourceValue: index / count, displayedValue: index / count, planeSampleCount: 1024 })) };
}
function Surface({ value = profile() }: { value?: PotentialProfile }) {
  const [selected, select] = useState<number | null>(null);
  return <PotentialProfilePanel profile={value} selectedIndex={selected} onSelect={select} />;
}

it("selects the visible plane on direct click without requiring a previous hover", () => {
  render(<Surface />);
  fireEvent.click(screen.getByRole("button", { name: "放大剖面" }));
  const chart = screen.getByRole("img");
  vi.spyOn(chart, "getBoundingClientRect").mockReturnValue({ left: 100, width: 640 } as DOMRect);
  fireEvent.click(chart, { clientX: 164 });
  expect(screen.getByTestId("potential-profile-selection")).toHaveTextContent("平面 8 · 分数坐标 0.250000");
  fireEvent.click(screen.getByRole("button", { name: "右移" }));
  fireEvent.click(chart, { clientX: 164 });
  expect(screen.getByTestId("potential-profile-selection")).toHaveTextContent("平面 12 · 分数坐标 0.375000");
});

it("keeps keyboard selection within the zoomed range and retains it through a gauge change", () => {
  const value = profile();
  const view = render(<Surface value={value} />);
  fireEvent.click(screen.getByRole("button", { name: "放大剖面" }));
  fireEvent.keyDown(screen.getByRole("img"), { key: "Home" });
  expect(screen.getByTestId("potential-profile-selection")).toHaveTextContent("平面 8");
  fireEvent.keyDown(screen.getByRole("img"), { key: "ArrowRight" });
  expect(screen.getByTestId("potential-profile-selection")).toHaveTextContent("平面 9");
  view.rerender(<Surface value={{ ...value, gauge: "cell_average_zero", points: value.points.map(point => ({ ...point, displayedValue: point.sourceValue - .5 })) }} />);
  expect(screen.getByTestId("potential-profile-selection")).toHaveTextContent("平面 9");
  expect(screen.getByTestId("potential-profile-selection")).toHaveTextContent("显示值 -0.21875 eV");
  fireEvent.keyDown(screen.getByRole("img"), { key: "End" });
  expect(screen.getByTestId("potential-profile-selection")).toHaveTextContent("平面 24");
});

it("paginates the full exact source table independently of the chart window", () => {
  render(<Surface value={profile(96)} />);
  fireEvent.click(screen.getByText("剖面数值 · 96 点"));
  const table = screen.getByRole("region", { name: "剖面数值表" });
  expect(within(table).getAllByRole("row")).toHaveLength(33);
  fireEvent.click(screen.getByRole("button", { name: "下一页" }));
  fireEvent.click(screen.getByRole("button", { name: "下一页" }));
  fireEvent.click(screen.getByRole("button", { name: "显示平面 65" }));
  expect(screen.getByTestId("potential-profile-selection")).toHaveTextContent("平面 65");
  expect(screen.getByRole("button", { name: "显示平面 65" })).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByRole("button", { name: "下一页" })).toBeDisabled();
});
