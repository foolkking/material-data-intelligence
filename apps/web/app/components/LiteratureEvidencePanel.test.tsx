import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";

import { LiteratureEvidencePanel } from "../../features/research/LiteratureEvidencePanel";

const mocks = vi.hoisted(() => ({
  list: vi.fn(),
  search: vi.fn(),
  select: vi.fn(),
}));

vi.mock("../lib/scientific-knowledge-api", async (original) => ({
  ...await original<typeof import("../lib/scientific-knowledge-api")>(),
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
    screen.getByText("参考文献"),
  ).toBeInTheDocument();
  expect(mocks.search).not.toHaveBeenCalled();
  fireEvent.click(screen.getByText("参考文献"));
  fireEvent.click(screen.getByText("搜索科学文献"));
  expect(screen.getByLabelText("要检索的科学问题")).toBeInTheDocument();
});

it("shows a failed read as unknown and restores the explicit empty state only after recovery", async () => {
  mocks.list.mockRejectedValueOnce(new Error("offline")).mockResolvedValue({ turnId: "turn-1", literatureEvidence: [] });
  render(<LiteratureEvidencePanel projectId="project-1" turnId="turn-1" />);
  fireEvent.click(screen.getByText("参考文献"));
  const retry = await screen.findByRole("button", { name: "重新读取已用文献" });
  expect(screen.queryByText("本次研究尚未引用文献。")).toBeNull();
  fireEvent.click(retry);
  expect(await screen.findByText("本次研究尚未引用文献。")).toBeInTheDocument();
  expect(mocks.search).not.toHaveBeenCalled();
});

it("clears the old panel scope and ignores late search results after navigation", async () => {
  mocks.list.mockImplementation(async (turnId: string) => ({ turnId, literatureEvidence: [] }));
  let finish!: (value: unknown) => void;
  mocks.search.mockReturnValueOnce(new Promise((resolve) => { finish = resolve; }));
  const view = render(<LiteratureEvidencePanel projectId="project-1" turnId="turn-1" />);
  fireEvent.click(screen.getByText("参考文献")); fireEvent.click(screen.getByText("搜索科学文献"));
  fireEvent.change(screen.getByLabelText("要检索的科学问题"), { target: { value: "previous query" } });
  fireEvent.click(screen.getByRole("button", { name: "搜索文献" }));
  view.rerender(<LiteratureEvidencePanel projectId="project-1" turnId="turn-2" />);
  fireEvent.click(screen.getByText("参考文献")); fireEvent.click(screen.getByText("搜索科学文献"));
  expect(screen.getByLabelText("要检索的科学问题")).toHaveValue("");
  await act(async () => { finish({ candidates: [{ candidate_id: "foreign" }] }); });
  expect(screen.queryByText(/previous query/)).toBeNull();
  expect(mocks.search.mock.calls[0][3].signal.aborted).toBe(true);
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
  fireEvent.click(screen.getByText("参考文献"));
  fireEvent.click(screen.getByText("搜索科学文献"));
  fireEvent.change(screen.getByLabelText("要检索的科学问题"), {
    target: { value: "diffusion evidence" },
  });
  fireEvent.click(screen.getByRole("button", { name: "搜索文献" }));
  await waitFor(() =>
    expect(screen.getByText("Retracted diffusion result")).toBeInTheDocument(),
  );
  expect(
    screen.getByRole("button", { name: "撤稿或撤回来源不可作为普通支持" }),
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
  fireEvent.click(screen.getByText(/参考文献/));
  expect(screen.getByRole("link", { name: "打开来源" })).toHaveAttribute(
    "href",
    "https://doi.org/10.5555/example",
  );
});
