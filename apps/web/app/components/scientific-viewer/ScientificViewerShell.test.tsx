import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ScientificViewerShell } from "./ScientificViewerShell";
import { resolveScientificViewer } from "./scientificViewerRegistry";

describe("Agent2 Phase 9 ScientificViewerShell", () => {
  it("keeps scientific content primary and progressively discloses technical detail", () => {
    render(<ScientificViewerShell title="LiFePO4 RDF" descriptor={resolveScientificViewer({ objectType: "analysis.rdf" })} versionLabel="版本 1" relevance="STALE" metadata={{ formula: "LiFePO4", site_count: 28 }} limitations={["峰位来自已验证结果，不由 Viewer 推导。"]} primaryActionHref="/projects/project/research"><div>RDF scientific plot</div></ScientificViewerShell>);
    expect(screen.getByRole("heading", { name: "LiFePO4 RDF" })).toBeInTheDocument();
    expect(screen.getByText("RDF scientific plot")).toBeInTheDocument();
    expect(screen.getByText("历史数据版本")).toBeInTheDocument();
    expect(screen.getByText("峰位来自已验证结果，不由 Viewer 推导。")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "研究此数据" })).toHaveAttribute("href", "/projects/project/research");
    expect(screen.getByText("技术详情").closest("details")).not.toHaveAttribute("open");
  });
});
