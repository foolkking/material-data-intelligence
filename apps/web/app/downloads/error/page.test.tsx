import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ReportDownloadError from "./page";

describe("report download recovery", () => {
  it("explains an expired login while preserving a bounded retry link", async () => {
    render(await ReportDownloadError({ searchParams: Promise.resolve({ reason: "auth", reportId: "agent2_report_exact", format: "markdown" }) }));
    expect(screen.getByRole("heading", { name: "报告下载未完成" })).toBeVisible();
    expect(screen.getByRole("alert")).toHaveTextContent("登录已过期");
    expect(screen.getByRole("link", { name: "重试下载" })).toHaveAttribute("href", "/downloads/scientific-reports/agent2_report_exact/markdown");
    expect(screen.getByText("原报告仍保留在原页面中。")).toBeVisible();
  });

  it("never echoes unknown errors or untrusted destinations", async () => {
    render(await ReportDownloadError({ searchParams: Promise.resolve({ reason: "private diagnostics", reportId: "https://external.test", format: "manifest" }) }));
    expect(screen.getByRole("alert")).toHaveTextContent("暂时无法读取完整报告");
    expect(screen.queryByRole("link", { name: "重试下载" })).toBeNull();
    expect(screen.queryByText(/private diagnostics|external\.test/)).toBeNull();
  });
});
