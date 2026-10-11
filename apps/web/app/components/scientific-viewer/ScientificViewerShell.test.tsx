import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ScientificViewerShell } from "./ScientificViewerShell";
import { resolveScientificViewer } from "./scientificViewerRegistry";

const descriptor = resolveScientificViewer({ objectType: "analysis.rdf" });

describe("Agent2 Phase 9 ScientificViewerShell", () => {
  it("keeps scientific content primary and progressively discloses technical detail", () => {
    render(<ScientificViewerShell title="LiFePO4 RDF" descriptor={resolveScientificViewer({ objectType: "analysis.rdf" })} versionLabel="版本 1" exactVersionId="version-exact-1" relevance="STALE" metadata={{ formula: "LiFePO4", site_count: 28 }} limitations={["峰位来自已验证结果，不由 Viewer 推导。"]} primaryActionHref="/projects/project/research"><div>RDF scientific plot</div></ScientificViewerShell>);
    expect(screen.getByRole("heading", { name: "LiFePO4 RDF" })).toBeInTheDocument();
    expect(screen.getByText("RDF scientific plot")).toBeInTheDocument();
    expect(screen.getByText("历史数据版本")).toBeInTheDocument();
    expect(screen.getByText("精确版本")).toBeInTheDocument();
    expect(screen.getByText("version-exact-1")).toBeInTheDocument();
    expect(screen.getByText("峰位来自已验证结果，不由 Viewer 推导。")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "研究此数据" })).toHaveAttribute("href", "/projects/project/research");
    const sourceDetails = screen.getByText("查看数据详情").closest("details");
    expect(sourceDetails).not.toHaveAttribute("open");
    expect(screen.getByRole("button", { name: "导出元数据摘要" })).not.toBeVisible();
    fireEvent.click(screen.getByText("查看数据详情"));
    expect(sourceDetails).toHaveAttribute("open");
    expect(screen.getByRole("button", { name: "导出元数据摘要" })).toBeInTheDocument();
    expect(screen.getByText("来源标识与查看器").closest("details")).not.toHaveAttribute("open");
    const viewer = screen.getByRole("heading", { name: "LiFePO4 RDF" }).closest("article");
    expect(viewer).toHaveAttribute("aria-labelledby");
    expect(viewer?.getAttribute("aria-labelledby")).toBe(screen.getByRole("heading", { name: "LiFePO4 RDF" }).id);
  });

  it("discloses metadata beyond the compact first-page summary", () => {
    const metadata = Object.fromEntries(
      Array.from({ length: 18 }, (_, index) => [`field_${index + 1}`, `value-${index + 1}`]),
    );
    render(
      <ScientificViewerShell
        title="Large metadata viewer"
        descriptor={descriptor}
        versionLabel="版本 2"
        metadata={metadata}
      >
        <div />
      </ScientificViewerShell>,
    );

    fireEvent.click(screen.getByText("查看数据详情"));
    const additionalSummary = screen.getByText("查看其余 2 项元数据");
    const additionalDetails = additionalSummary.closest("details");
    expect(additionalDetails).not.toHaveAttribute("open");
    fireEvent.click(additionalSummary);
    expect(additionalDetails).toHaveAttribute("open");
    expect(screen.getByText("Field 17")).toBeInTheDocument();
    expect(screen.getByText("value-18")).toBeInTheDocument();
  });

  it("presents readable properties without merging conflicting counts or losing source identifiers", () => {
    const { rerender } = render(<ScientificViewerShell title="Materials" descriptor={descriptor} versionLabel="版本 1" metadata={{ columns: ["material", "value"], nRows: 2, row_count: 2, detectedFormat: "csv", dataset_id: "exact-dataset" }}><div /></ScientificViewerShell>);
    fireEvent.click(screen.getByText("查看数据详情"));
    expect(screen.getByText("material、value")).toBeVisible();
    expect(screen.getAllByText("行数")).toHaveLength(1);
    expect(screen.getByText("文件格式")).toBeVisible();
    expect(screen.getByText("exact-dataset")).not.toBeVisible();
    fireEvent.click(screen.getByText("来源标识与查看器"));
    expect(screen.getByText("exact-dataset")).toBeVisible();
    rerender(<ScientificViewerShell title="Materials" descriptor={descriptor} versionLabel="版本 1" metadata={{ nRows: 2, row_count: 3 }}><div /></ScientificViewerShell>);
    expect(screen.getAllByText("行数")).toHaveLength(2);
    expect(screen.getByText("2")).toBeVisible();
    expect(screen.getByText("3")).toBeVisible();
  });
});

it("gives repeated viewer limitation sections unique accessible ids", () => {
  const { container } = render(
    <>
      <ScientificViewerShell title="A" descriptor={descriptor} versionLabel="版本 1" limitations={["A limitation"]}><div /></ScientificViewerShell>
      <ScientificViewerShell title="B" descriptor={descriptor} versionLabel="版本 1" limitations={["B limitation"]}><div /></ScientificViewerShell>
    </>,
  );
  const headings = [...container.querySelectorAll("h3")];
  expect(headings).toHaveLength(2);
  expect(new Set(headings.map((heading) => heading.id)).size).toBe(2);
  headings.forEach((heading) => expect(heading.parentElement).toHaveAttribute("aria-labelledby", heading.id));
});
