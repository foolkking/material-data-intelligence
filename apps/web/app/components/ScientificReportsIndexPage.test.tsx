import { render, screen } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  getProjectHistory: vi.fn(),
  listScientificReports: vi.fn(),
}));

vi.mock("next/link", () => ({
  default: ({ children, href, ...props }: { children: React.ReactNode; href: string }) => <a href={href} {...props}>{children}</a>,
}));
vi.mock("../lib/planner-api", () => ({ getProjectHistory: mocks.getProjectHistory }));
vi.mock("../lib/scientific-report-api", () => ({ listScientificReports: mocks.listScientificReports }));
vi.mock("./ProductShell", () => ({
  ProductShell: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  RequireProductAuth: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

import { ScientificReportsIndexPage } from "./ScientificReportsIndexPage";

beforeEach(() => {
  vi.clearAllMocks();
  mocks.listScientificReports.mockResolvedValue({ items: [] });
});

it("labels modern and legacy history bindings without changing report routes", async () => {
  mocks.getProjectHistory.mockResolvedValue({
    project: { projectId: "project-1", name: "研究项目" },
    datasets: [],
    analyses: [
      {
        jobId: "job-modern",
        status: "completed",
        userQuestion: "现代研究",
        toolIds: ["structure.rdf"],
        artifactTypes: [],
        stepCount: 1,
        artifactCount: 1,
        reportCount: 1,
        researchContextKind: "RESEARCH_TURN",
      },
      {
        jobId: "job-legacy",
        status: "completed",
        userQuestion: "兼容运行",
        toolIds: ["structure.rdf"],
        artifactTypes: [],
        stepCount: 1,
        artifactCount: 1,
        reportCount: 1,
        researchContextKind: "LEGACY_SESSION_RUN",
      },
    ],
  });

  render(<ScientificReportsIndexPage projectId="project-1" />);

  expect(await screen.findByText("可恢复研究会话")).toBeInTheDocument();
  expect(screen.getByText("兼容历史运行")).toBeInTheDocument();
  expect(screen.getAllByRole("link", { name: /静态结构径向分布函数.*阅读旧版/ }).find(
    (link) => link.getAttribute("href")?.endsWith("job-legacy"),
  )).toHaveAttribute("href", "/projects/project-1/reports/job-legacy");
});
