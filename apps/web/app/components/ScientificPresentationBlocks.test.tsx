import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ScientificPresentationBlocks } from "./ScientificPresentationBlocks";

const mocks = vi.hoisted(() => ({
  getPlannerInterpretationEvidence: vi.fn(),
}));

vi.mock("../lib/planner-api", () => ({
  getPlannerInterpretationEvidence: mocks.getPlannerInterpretationEvidence,
}));

vi.mock("./ScientificViewerAdapter", () => ({
  ScientificResultViewer: ({ jobId, selected }: { jobId: string; selected: { artifactId?: string; id?: string } }) => (
    <div data-testid="inline-scientific-result-viewer">
      {jobId} · {selected.artifactId || selected.id}
    </div>
  ),
}));

const presentation = {
  schemaVersion: "1.0" as const,
  exactSourceRefs: [{ objectId: "object-1", versionId: "version-2", objectType: "structure.crystal", displayName: "Silicon" }],
  blocks: [{
    id: "evidence-1",
    type: "evidence_reference" as const,
    title: "证据",
    label: "band_gap = 2.5",
    source: {
      resultId: "result-1",
      interpretationId: "interpretation-1",
      evidenceId: "evidence-1",
      artifactId: "artifact-1",
      jobId: "job-1",
      toolCallId: "call-1",
      objectId: "object-1",
      versionId: "version-2",
    },
  }],
};

describe("ScientificPresentationBlocks evidence inspector", () => {
  it("renders bounded metric precision while retaining the exact source value", () => {
    render(<ScientificPresentationBlocks presentation={{
      schemaVersion: "1.0",
      exactSourceRefs: [],
      blocks: [{
        id: "metric-rmse",
        type: "metric",
        title: "RMSE",
        value: "0.21602468994692867",
        source: { resultId: "result-1", factId: "fact-rmse" },
      }],
    }} />);
    const value = screen.getByText("0.2160247");
    expect(value).toHaveAttribute("data-exact-value", "0.21602468994692867");
    expect(value).toHaveAttribute("title", "精确值：0.21602468994692867");
    expect(screen.getByText("精确值 0.21602468994692867")).toHaveClass("sr-only");
  });

  it("renders canonical system limitations in product language without changing their scientific meaning", () => {
    render(<ScientificPresentationBlocks presentation={{
      schemaVersion: "1.0",
      exactSourceRefs: [],
      blocks: [{
        id: "limitation-1",
        type: "limitation",
        text: "The current DOS Artifact does not provide eigenvectors or animation authority.",
        source: {},
      }],
    }} />);
    expect(screen.getByText("当前声子态密度 Artifact 不包含特征向量，因此不提供模式动画依据。")).toBeInTheDocument();
  });

  it("assigns unique accessible heading ids to repeated presentation instances", () => {
    const { container } = render(
      <>
        <ScientificPresentationBlocks presentation={presentation} projectId="project-1" />
        <ScientificPresentationBlocks presentation={presentation} projectId="project-1" />
      </>,
    );
    const sections = [...container.querySelectorAll<HTMLElement>("section.scientific-presentation")];
    const ids = sections.map((section) => section.getAttribute("aria-labelledby"));
    expect(ids).toHaveLength(2);
    expect(ids[0]).toBeTruthy();
    expect(ids[0]).not.toBe(ids[1]);
    expect(ids.every((id) => id && document.getElementById(id)?.tagName === "H3")).toBe(true);
  });

  it("opens a bounded exact source chain without exposing raw infrastructure details", async () => {
    mocks.getPlannerInterpretationEvidence.mockResolvedValue({
      interpretationId: "interpretation-1",
      bundleId: "bundle-1",
      bundleHash: "a".repeat(64),
      jobId: "job-1",
      planId: "plan-1",
      evidenceItems: [{
        schemaVersion: "1.0",
        evidenceItemId: "evidence-1",
        semanticRole: "band_gap",
        evidenceKind: "SCALAR",
        subjectId: "mat-2",
        displayValue: "2.5",
        unit: "eV",
        sourceArtifactId: "artifact-1",
        sourceArtifactChecksum: "b".repeat(64),
        artifactContract: "dataset.table",
        artifactContractVersion: "1.0",
        sourceToolId: "data.materials_explorer",
        sourceToolVersion: "1.0",
        fieldLocator: { fieldId: "band_gap", entityId: "mat-2" },
        warnings: [],
        limitations: [],
      }],
      sourceArtifactIds: ["artifact-1"],
      sourceObjectRefs: [{ objectId: "object-1", versionId: "version-2", objectType: "dataset", displayName: "Dataset" }],
      artifacts: [{ artifactId: "artifact-1", jobId: "job-1", contentHash: "c".repeat(64) }],
      toolCalls: [{ id: "call-1", toolId: "data.materials_explorer", status: "completed" }],
      bundleWarnings: [],
      bundleLimitations: [],
    });

    const user = userEvent.setup();
    render(<ScientificPresentationBlocks presentation={presentation} projectId="project-1" instanceId="turn-1" />);
    await user.click(screen.getByRole("button", { name: "检查证据链" }));

    expect(await screen.findByRole("region", { name: "证据链 evidence-1" })).toHaveTextContent("version-2");
    expect(screen.getByRole("region", { name: "证据链 evidence-1" })).toHaveTextContent("data.materials_explorer");
    expect(screen.getByRole("region", { name: "证据链 evidence-1" })).toHaveTextContent("band_gap · 2.5 eV");
    expect(screen.getByRole("region", { name: "证据链 evidence-1" })).not.toHaveTextContent("redis://");
    expect(screen.getByRole("link", { name: "打开权威 Artifact" })).toHaveAttribute("href", "/api/planner/jobs/job-1/artifacts/artifact-1/content");
    await waitFor(() => expect(mocks.getPlannerInterpretationEvidence).toHaveBeenCalledWith("interpretation-1"));
  });

  it("opens one persisted Figure or Table through the existing scientific renderer without leaving Research", async () => {
    const user = userEvent.setup();
    render(<ScientificPresentationBlocks
      projectId="project-1"
      instanceId="turn-figure"
      presentation={{
        schemaVersion: "1.0",
        exactSourceRefs: [{ objectId: "object-1", versionId: "version-2" }],
        blocks: [{
          id: "figure-1",
          type: "figure",
          title: "配位数直方图",
          artifactId: "artifact-plot",
          source: {
            jobId: "job-1",
            artifactId: "artifact-plot",
            objectId: "object-1",
            versionId: "version-2",
          },
        }],
      }}
      artifactCatalog={[{
        artifactId: "artifact-plot",
        jobId: "job-1",
        type: "plotly_json",
        name: "coordination_hist_plot.json",
      }]}
    />);

    expect(screen.queryByTestId("inline-scientific-result-viewer")).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "在页内查看" }));
    expect(screen.getByRole("region", { name: "图形：配位数直方图" })).toBeInTheDocument();
    expect(screen.getByTestId("inline-scientific-result-viewer")).toHaveTextContent("job-1 · artifact-plot");
    expect(screen.getByRole("link", { name: "打开原始 Artifact" })).toHaveAttribute(
      "href",
      "/api/planner/jobs/job-1/artifacts/artifact-plot/content",
    );
    await user.click(screen.getByRole("button", { name: "关闭预览" }));
    expect(screen.queryByTestId("inline-scientific-result-viewer")).not.toBeInTheDocument();
  });
});
