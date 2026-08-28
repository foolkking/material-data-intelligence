import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Agent2ScientificPresentation } from "./Agent2ScientificPresentation";

const mocks = vi.hoisted(() => ({
  createAgent2ResearchTurn: vi.fn(),
  getAgent2ResearchTurnResult: vi.fn(),
  getAgent2ResearchTurnInterpretation: vi.fn(),
  push: vi.fn(),
}));

vi.mock("../lib/agent2-research-api", () => mocks);
vi.mock("next/navigation", () => ({ useRouter: () => ({ push: mocks.push }) }));

const result = {
  result_id: "result-1",
  research_turn_id: "turn-1",
  research_question: "Inspect the structure",
  execution_status: "SUCCESS",
  relevance_status: "CURRENT",
  source_object_refs: [],
  facts: [],
  figures: [],
  tables: [],
  evidence: [],
  artifacts: [],
  scientific_selections: [],
};

describe("Agent2ScientificPresentation", () => {
  beforeEach(() => {
    mocks.createAgent2ResearchTurn.mockReset();
    mocks.getAgent2ResearchTurnResult.mockReset();
    mocks.getAgent2ResearchTurnInterpretation.mockReset();
    mocks.push.mockReset();
  });

  it("creates an explicit interpretation turn without rerunning scientific work", async () => {
    mocks.getAgent2ResearchTurnResult.mockResolvedValue(result);
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(new Error("not ready"));
    mocks.createAgent2ResearchTurn.mockResolvedValue({ turn_id: "turn-reinterpret-1" });

    render(<Agent2ScientificPresentation turnId="turn-1" projectId="project-1" sessionId="session-1" />);
    fireEvent.click(await screen.findByRole("button", { name: /重新解释/ }));

    await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith(
      "project-1",
      "session-1",
      expect.objectContaining({
        reply_to_turn_id: "turn-1",
        ui_context: expect.objectContaining({ explicit_result_ids: ["result-1"] }),
      }),
    ));
    expect(mocks.push).toHaveBeenCalledWith("/projects/project-1/research/session-1?turn=turn-reinterpret-1");
  });

  it("creates a continuation turn with an explicit reusable result", async () => {
    mocks.getAgent2ResearchTurnResult.mockResolvedValue({ ...result, source_object_refs: [{ object_id: "object-1", version_id: "version-1", project_id: "project-1", object_type: "structure.crystal" }] });
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(new Error("not ready"));
    mocks.createAgent2ResearchTurn.mockResolvedValue({ turn_id: "turn-continue-1" });

    render(<Agent2ScientificPresentation turnId="turn-1" projectId="project-1" sessionId="session-1" />);
    fireEvent.click(await screen.findByRole("button", { name: "继续研究" }));

    await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith(
      "project-1",
      "session-1",
      expect.objectContaining({
        reply_to_turn_id: "turn-1",
        ui_context: expect.objectContaining({ explicit_result_ids: ["result-1"] }),
      }),
    ));
    expect(mocks.push).toHaveBeenCalledWith("/projects/project-1/research/session-1?turn=turn-continue-1");
  });

  it("routes editing to an immutable branch composer", async () => {
    mocks.getAgent2ResearchTurnResult.mockResolvedValue(result);
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(new Error("not ready"));

    render(<Agent2ScientificPresentation turnId="turn-1" projectId="project-1" sessionId="session-1" />);
    fireEvent.click(await screen.findByRole("button", { name: "编辑问题" }));

    expect(mocks.push).toHaveBeenCalledWith("/projects/project-1/research/session-1?turn=turn-1&edit=turn-1");
  });

  it("creates a new rerun without claiming result reuse", async () => {
    mocks.getAgent2ResearchTurnResult.mockResolvedValue(result);
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(new Error("not ready"));
    mocks.createAgent2ResearchTurn.mockResolvedValue({ turn_id: "turn-rerun-1" });

    render(<Agent2ScientificPresentation turnId="turn-1" projectId="project-1" sessionId="session-1" />);
    fireEvent.click(await screen.findByRole("button", { name: "重新研究（新运行）" }));

    await waitFor(() => expect(mocks.createAgent2ResearchTurn).toHaveBeenCalledWith(
      "project-1",
      "session-1",
      expect.objectContaining({
        reply_to_turn_id: "turn-1",
        ui_context: expect.objectContaining({ explicit_result_ids: [] }),
      }),
    ));
    expect(mocks.push).toHaveBeenCalledWith("/projects/project-1/research/session-1?turn=turn-rerun-1");
  });
});
