import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Agent2ScientificPresentation } from "./Agent2ScientificPresentation";

const mocks = vi.hoisted(() => ({
  createAgent2ResearchTurn: vi.fn(),
  getAgent2ResearchTurnResult: vi.fn(),
  getAgent2ResearchTurnInterpretation: vi.fn(),
  getAgent2SessionMemory: vi.fn(),
  pinAgent2Object: vi.fn(),
  pinAgent2Result: vi.fn(),
  unpinAgent2Object: vi.fn(),
  unpinAgent2Result: vi.fn(),
  push: vi.fn(),
}));

vi.mock("../lib/agent2-research-api", () => mocks);
vi.mock("../lib/agent2-memory-api", () => ({
  getAgent2SessionMemory: mocks.getAgent2SessionMemory,
  pinAgent2Object: mocks.pinAgent2Object,
  pinAgent2Result: mocks.pinAgent2Result,
  unpinAgent2Object: mocks.unpinAgent2Object,
  unpinAgent2Result: mocks.unpinAgent2Result,
}));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push: mocks.push }) }));

const result = {
  result_id: "result-1",
  result_snapshot_id: "snapshot-1",
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
    mocks.getAgent2SessionMemory.mockReset();
    mocks.pinAgent2Object.mockReset();
    mocks.pinAgent2Result.mockReset();
    mocks.unpinAgent2Object.mockReset();
    mocks.unpinAgent2Result.mockReset();
    mocks.getAgent2SessionMemory.mockResolvedValue({ pinned_result_refs: [], pinned_object_refs: [] });
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
        ui_context: expect.objectContaining({ explicit_result_ids: ["snapshot-1"] }),
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
        ui_context: expect.objectContaining({ explicit_result_ids: ["snapshot-1"] }),
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

  it("pins and unpins the exact result through session memory controls", async () => {
    mocks.getAgent2ResearchTurnResult.mockResolvedValue(result);
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(new Error("not ready"));
    mocks.pinAgent2Result.mockResolvedValue({ pinned_result_refs: ["snapshot-1"] });
    mocks.unpinAgent2Result.mockResolvedValue({ pinned_result_refs: [] });

    render(<Agent2ScientificPresentation turnId="turn-1" projectId="project-1" sessionId="session-1" />);
    const pin = await screen.findByRole("button", { name: "将结果加入本会话上下文" });
    fireEvent.click(pin);
    await waitFor(() => expect(mocks.pinAgent2Result).toHaveBeenCalledWith("project-1", "session-1", "snapshot-1"));
    const unpin = await screen.findByRole("button", { name: "从本会话上下文移除结果" });
    fireEvent.click(unpin);
    await waitFor(() => expect(mocks.unpinAgent2Result).toHaveBeenCalledWith("project-1", "session-1", "snapshot-1"));
  });

  it("pins and unpins exact source versions through session memory controls", async () => {
    const source = { object_id: "object-1", version_id: "version-1", project_id: "project-1", object_type: "structure.crystal", display_name: "Structure" };
    mocks.getAgent2ResearchTurnResult.mockResolvedValue({ ...result, source_object_refs: [source] });
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(new Error("not ready"));
    mocks.pinAgent2Object.mockResolvedValue({ pinned_result_refs: [], pinned_object_refs: [source] });
    mocks.unpinAgent2Object.mockResolvedValue({ pinned_result_refs: [], pinned_object_refs: [] });

    render(<Agent2ScientificPresentation turnId="turn-1" projectId="project-1" sessionId="session-1" />);
    fireEvent.click(await screen.findByRole("button", { name: "将来源版本加入本会话上下文" }));
    await waitFor(() => expect(mocks.pinAgent2Object).toHaveBeenCalledWith("project-1", "session-1", expect.objectContaining({
      object_id: source.object_id,
      version_id: source.version_id,
    })));
    fireEvent.click(await screen.findByRole("button", { name: "从本会话上下文移除来源版本" }));
    await waitFor(() => expect(mocks.unpinAgent2Object).toHaveBeenCalledWith("project-1", "session-1", expect.objectContaining({
      object_id: source.object_id,
      version_id: source.version_id,
    })));
  });

  it("keeps presentation pin controls synchronized with parent session memory", async () => {
    const source = {
      object_id: "object-1",
      version_id: "version-1",
      project_id: "project-1",
      object_type: "structure.crystal",
      display_name: "Structure",
    };
    mocks.getAgent2ResearchTurnResult.mockResolvedValue({
      ...result,
      source_object_refs: [source],
    });
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(
      new Error("not ready"),
    );
    const onSessionMemoryChange = vi.fn();
    const { rerender } = render(
      <Agent2ScientificPresentation
        turnId="turn-1"
        projectId="project-1"
        sessionId="session-1"
        sessionMemory={{
          session_id: "session-1",
          project_id: "project-1",
          pinned_result_refs: [],
          pinned_object_refs: [source],
          session_constraints: [],
          version: 1,
        }}
        onSessionMemoryChange={onSessionMemoryChange}
      />,
    );

    expect(
      await screen.findByRole("button", { name: "从本会话上下文移除来源版本" }),
    ).toBeInTheDocument();

    rerender(
      <Agent2ScientificPresentation
        turnId="turn-1"
        projectId="project-1"
        sessionId="session-1"
        sessionMemory={{
          session_id: "session-1",
          project_id: "project-1",
          pinned_result_refs: [],
          pinned_object_refs: [],
          session_constraints: [],
          version: 2,
        }}
        onSessionMemoryChange={onSessionMemoryChange}
      />,
    );

    expect(
      await screen.findByRole("button", { name: "将来源版本加入本会话上下文" }),
    ).toBeInTheDocument();
    expect(mocks.getAgent2SessionMemory).not.toHaveBeenCalled();
  });

  it("does not let a stale session-memory read undo a completed pin", async () => {
    let resolveMemory: ((value: { pinned_result_refs: string[] }) => void) | undefined;
    mocks.getAgent2SessionMemory.mockImplementation(
      () => new Promise((resolve) => { resolveMemory = resolve; }),
    );
    mocks.getAgent2ResearchTurnResult.mockResolvedValue(result);
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(new Error("not ready"));
    mocks.pinAgent2Result.mockResolvedValue({ pinned_result_refs: ["snapshot-1"] });

    render(<Agent2ScientificPresentation turnId="turn-1" projectId="project-1" sessionId="session-1" />);
    const pin = await screen.findByRole("button", { name: "将结果加入本会话上下文" });
    fireEvent.click(pin);
    const unpin = await screen.findByRole("button", { name: "从本会话上下文移除结果" });

    resolveMemory?.({ pinned_result_refs: [] });
    await waitFor(() => expect(screen.getByRole("button", { name: "从本会话上下文移除结果" })).toBeInTheDocument());
  });
});
