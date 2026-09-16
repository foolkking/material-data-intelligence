import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";

import { LiteratureEvidencePanel } from "../../features/research/LiteratureEvidencePanel";

const mocks = vi.hoisted(() => ({
  list: vi.fn(),
  search: vi.fn(),
  select: vi.fn(),
}));

vi.mock("../lib/scientific-knowledge-api", () => ({
  listTurnLiteratureEvidence: mocks.list,
  searchScientificLiterature: mocks.search,
  selectLiteratureEvidence: mocks.select,
}));

beforeEach(() => {
  mocks.list.mockReset();
  mocks.search.mockReset();
  mocks.select.mockReset();
  mocks.list.mockResolvedValue({ turnId: "turn-1", literatureEvidence: [] });
});

it("keeps external search explicit and distinguishes literature from computed results", async () => {
  render(<LiteratureEvidencePanel projectId="project-1" turnId="turn-1" />);
  expect(
    screen.getByText("不同于“根据你的数据计算”"),
  ).toBeInTheDocument();
  expect(mocks.search).not.toHaveBeenCalled();
  fireEvent.click(screen.getByText("搜索科学文献"));
  expect(screen.getByLabelText("要检索的科学问题")).toBeInTheDocument();
});

it("shows evidence scope and blocks ordinary use of a retracted candidate", async () => {
  mocks.search.mockResolvedValue({
    candidates: [
      {
        candidate_id: "candidate-1",
        work: { work_id: "work-1", canonical_key: "doi:10.1/test" },
        possible_duplicate_of: [],
        snapshots: [
          {
            snapshot_id: "snapshot-1",
            provider: "CROSSREF",
            title: "Retracted diffusion result",
            authors: ["A Researcher"],
            publication_status: "RETRACTED",
            access_status: "METADATA_ONLY",
            source_url: "https://doi.org/10.1/test",
            retrieved_at: "2026-09-11T00:00:00Z",
          },
        ],
      },
    ],
  });
  render(<LiteratureEvidencePanel projectId="project-1" turnId="turn-1" />);
  fireEvent.click(screen.getByText("搜索科学文献"));
  fireEvent.change(screen.getByLabelText("要检索的科学问题"), {
    target: { value: "diffusion evidence" },
  });
  fireEvent.click(screen.getByRole("button", { name: "搜索文献" }));
  await waitFor(() =>
    expect(screen.getByText("Retracted diffusion result")).toBeInTheDocument(),
  );
  expect(
    screen.getByRole("button", { name: "撤稿来源不可作为普通支持" }),
  ).toBeDisabled();
});

it("shows the exact cited source for evidence already used in research", async () => {
  mocks.list.mockResolvedValue({
    turnId: "turn-1",
    literatureEvidence: [
      {
        id: "evidence-1",
        title: "Reference diffusion measurement",
        citation:
          "A. Researcher. (2025). Reference diffusion measurement. Journal. doi:10.5555/example",
        publication_status: "PEER_REVIEWED_ARTICLE",
        source_url: "https://doi.org/10.5555/example",
        scope: "ABSTRACT_ONLY",
        support_type: "SUPPORTING",
        purpose: "REFERENCE_VALUE",
        passage: "The diffusion coefficient is 1.2 cm^2/s.",
        snapshot_id: "snapshot-1",
        work_id: "work-1",
        selected_at: "2026-09-11T00:00:00Z",
      },
    ],
  });
  render(<LiteratureEvidencePanel projectId="project-1" turnId="turn-1" />);
  expect(
    await screen.findByText("Reference diffusion measurement"),
  ).toBeInTheDocument();
  expect(screen.getByText(/doi:10.5555\/example/)).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "打开来源" })).toHaveAttribute(
    "href",
    "https://doi.org/10.5555/example",
  );
});
