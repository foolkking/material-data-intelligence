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
    expect(screen.getByText("技术详情").closest("details")).not.toHaveAttribute("open");
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

    const additionalSummary = screen.getByText("查看其余 2 项元数据");
    const additionalDetails = additionalSummary.closest("details");
    expect(additionalDetails).not.toHaveAttribute("open");
    fireEvent.click(additionalSummary);
    expect(additionalDetails).toHaveAttribute("open");
    expect(screen.getByText("Field 17")).toBeInTheDocument();
    expect(screen.getByText("value-18")).toBeInTheDocument();
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
