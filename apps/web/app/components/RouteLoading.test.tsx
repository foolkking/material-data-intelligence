import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { RouteLoading } from "./RouteLoading";

describe("RouteLoading", () => {
  it("preserves the research workbench shape during client navigation", () => {
    render(<RouteLoading embedded section="研究工作台" variant="research" />);

    const loading = screen.getByRole("region", { name: "研究工作台正在加载" });
    expect(loading).toHaveClass("route-loading-workbench");
    expect(screen.getByRole("status")).toHaveTextContent(
      "正在保留当前科学上下文并打开研究工作台",
    );
  });

  it("keeps the bounded document fallback for non-workbench routes", () => {
    render(<RouteLoading section="科学报告" />);

    expect(screen.getByRole("status")).toHaveTextContent(
      "正在保留当前研究上下文",
    );
  });

  it("keeps the same spatial shell for overview and report transitions", () => {
    const { rerender } = render(
      <RouteLoading embedded section="项目研究" variant="overview" />,
    );
    expect(screen.getByRole("region", { name: "项目研究正在加载" })).toHaveClass(
      "route-loading-workbench",
    );
    expect(document.querySelector(".route-loading-workbench-context")).toBeInTheDocument();

    rerender(<RouteLoading embedded section="科学报告" variant="reports" />);
    expect(screen.getByRole("region", { name: "科学报告正在加载" })).toHaveClass(
      "route-loading-workbench",
    );
    expect(document.querySelector(".route-loading-workbench-main")).toBeInTheDocument();
  });
});
