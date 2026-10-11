import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Agent2ScientificPresentation as Presentation } from "./Agent2ScientificPresentation";

import { useSessionMemory } from "../../features/research/use-session-memory";
import type { Agent2SessionMemory } from "../lib/agent2-memory-api";

function Agent2ScientificPresentation(props: React.ComponentProps<typeof Presentation>) {
  const context = useSessionMemory(props.projectId, props.sessionId, props.canModify !== false);
  return <Presentation {...props} context={context} />;
}
const memory: Agent2SessionMemory = { project_id: "project-1", session_id: "session-1", version: 1, pinned_result_refs: [], pinned_object_refs: [], session_constraints: [] };

const mocks = vi.hoisted(() => ({
  createAgent2ResearchTurn: vi.fn(),
  createAgent2AdmissionKey: vi.fn(() => "m4-01-test-admission-key"),
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
vi.mock("../lib/agent2-memory-api", async (importOriginal) => ({
  ...await importOriginal<typeof import("../lib/agent2-memory-api")>(),
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
  it("does not describe a not-yet-generated interpretation as a transport failure", async () => {
    mocks.getAgent2ResearchTurnResult.mockResolvedValue(result);
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(Object.assign(new Error("not ready"),{code:"SCIENTIFIC_RESULT_NOT_READY"}));
    render(<Agent2ScientificPresentation projectId="project-1" turnId="turn-1" />);
    await screen.findByText("结果解读尚未生成，已完成的科学结果仍可查看。");
    expect(screen.queryByText("结果解读暂时无法读取，分析结果仍可查看。")).toBeNull();
    expect(screen.getByRole("button",{name:"检查解读状态"})).toBeTruthy();
  });
  beforeEach(() => {
    mocks.createAgent2ResearchTurn.mockReset();
    mocks.getAgent2ResearchTurnResult.mockReset();
    mocks.getAgent2ResearchTurnInterpretation.mockReset();
    mocks.getAgent2SessionMemory.mockReset();
    mocks.pinAgent2Object.mockReset();
    mocks.pinAgent2Result.mockReset();
    mocks.unpinAgent2Object.mockReset();
    mocks.unpinAgent2Result.mockReset();
    mocks.getAgent2SessionMemory.mockResolvedValue(memory);
    mocks.push.mockReset();
  });

  it("offers local result recovery without claiming an unread result is saved", async () => {
    mocks.getAgent2ResearchTurnResult.mockRejectedValueOnce(new Error("offline")).mockResolvedValue(result);
    mocks.getAgent2ResearchTurnInterpretation.mockResolvedValue({ interpretation_id: "interpretation-1", research_turn_id: "turn-1", status: "VALID", message: "这是一条已保存的结果解读。" });
    render(<Agent2ScientificPresentation turnId="turn-1" projectId="project-1" sessionId="session-1" />);
    fireEvent.click(await screen.findByRole("button", { name: "重新读取分析结果" }));
    expect(await screen.findByText("这是一条已保存的结果解读。")).toBeInTheDocument();
    expect(screen.queryByText(/科学结果已保存/)).toBeNull();
    expect(mocks.getAgent2ResearchTurnResult).toHaveBeenCalledTimes(2);
    expect(mocks.getAgent2ResearchTurnInterpretation).toHaveBeenCalledTimes(1);
    expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  });

  it("keeps committed output links usable when result projection failed and rejects unrelated links", async () => {
    mocks.getAgent2ResearchTurnResult.mockRejectedValue(new Error("result snapshot absent"));
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(new Error("interpretation absent"));
    const output = { output_key: "output-1", step_id: "step_1", artifact_id: "artifact-1", display_label: "理论 XRD 原始数据", preview_available: false, available_at: "2026-10-04", content_url: "/api/planner/jobs/job-1/artifacts/artifact-1/content" };
    const progress = { contract_version: "1.0" as const, turn_id: "turn-1", status: "FAILED" as const, steps: [], active_step_ids: [], completed_step_count: 1, total_step_count: 1, result_projection_pending: false, warnings: [], incremental_outputs: [output, { ...output, output_key: "unsafe", display_label: "不可信外链", content_url: "https://untrusted.invalid/file" }] };
    const view = render(<Agent2ScientificPresentation turnId="turn-1" projectId="project-1" progress={progress} />);
    await screen.findByRole("button", { name: "重新读取分析结果" });
    expect(screen.getByRole("link", { name: "理论 XRD 原始数据" })).toHaveAttribute("href", output.content_url);
    expect(screen.queryByRole("link", { name: "不可信外链" })).toBeNull();
    expect(screen.queryByRole("heading", { name: "关键发现" })).toBeNull();
    view.rerender(<Agent2ScientificPresentation turnId="turn-2" projectId="project-1" progress={progress} />);
    expect(screen.queryByRole("link", { name: "理论 XRD 原始数据" })).toBeNull();
    expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  });

  it("retains the scientific presentation while recovering only its interpretation", async () => {
    mocks.getAgent2ResearchTurnResult.mockResolvedValue(result);
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValueOnce(new Error("offline"))
      .mockResolvedValue({ interpretation_id: "interpretation-1", research_turn_id: "turn-1", status: "VALID", message: "重新读取到的结果解读。" });
    render(<Agent2ScientificPresentation turnId="turn-1" projectId="project-1" sessionId="session-1" />);
    const retry = await screen.findByRole("button", { name: "重新读取结果解读" });
    const presentation = document.querySelector(".agent2-scientific-presentation");
    fireEvent.click(retry);
    expect(await screen.findByText("重新读取到的结果解读。")).toBeInTheDocument();
    expect(document.querySelector(".agent2-scientific-presentation")).toBe(presentation);
    expect(mocks.getAgent2ResearchTurnResult).toHaveBeenCalledTimes(1);
    expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  });

  it("delegates result research to the current workspace submission settings", async () => {
    mocks.getAgent2ResearchTurnResult.mockResolvedValue(result);
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(new Error("not ready"));
    const run = vi.fn().mockResolvedValue(undefined);
    render(<Agent2ScientificPresentation turnId="turn-1" projectId="project-1" sessionId="session-1" onRun={run} />);
    fireEvent.click(await screen.findByText("更多操作"));
    fireEvent.click(screen.getByRole("button", { name: /重新解释/ }));
    await waitFor(() => expect(run).toHaveBeenCalledWith("reinterpret", result));
    await waitFor(() => expect(screen.getByRole("button", { name: "重新研究（新运行）" })).toBeEnabled());
    fireEvent.click(screen.getByRole("button", { name: "重新研究（新运行）" }));
    await waitFor(() => expect(run).toHaveBeenCalledWith("rerun", result));
    expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  });

  it("returns Continue and Edit to the workspace composer without submitting a canned message", async () => {
    mocks.getAgent2ResearchTurnResult.mockResolvedValue(result);
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(new Error("not ready"));
    const onContinue = vi.fn(), onEdit = vi.fn();
    render(<Agent2ScientificPresentation turnId="turn-1" projectId="project-1" sessionId="session-1" onContinue={onContinue} onEdit={onEdit} />);
    fireEvent.click(await screen.findByRole("button", { name: "继续研究" }));
    fireEvent.click(screen.getByRole("button", { name: "编辑问题" }));
    expect(onContinue).toHaveBeenCalledOnce(); expect(onEdit).toHaveBeenCalledOnce();
    expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  });

  it("prevents parallel result submissions and does not leak a late error into another Turn", async () => {
    mocks.getAgent2ResearchTurnResult.mockImplementation(async (id) => ({ ...result, research_turn_id: id }));
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(new Error("not ready"));
    let fail!: (reason: unknown) => void;
    const run = vi.fn(() => new Promise<void>((_, reject) => { fail = reject; }));
    const view = render(<Agent2ScientificPresentation turnId="turn-1" projectId="project-1" sessionId="session-1" onRun={run} />);
    fireEvent.click(await screen.findByText("更多操作"));
    fireEvent.click(screen.getByRole("button", { name: /重新解释/ }));
    expect(screen.getByRole("button", { name: "重新研究（新运行）" })).toBeDisabled();
    view.rerender(<Agent2ScientificPresentation turnId="turn-2" projectId="project-1" sessionId="session-1" onRun={run} />);
    await waitFor(() => expect(screen.getByRole("button", { name: /重新解释/ })).toBeEnabled());
    fail(new Error("old failure"));
    await waitFor(() => expect(screen.queryByText("old failure")).toBeNull());
    expect(run).toHaveBeenCalledOnce();
  });

  it("omits mutation controls for a read-only result", async () => {
    mocks.getAgent2ResearchTurnResult.mockResolvedValue(result);
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(new Error("not ready"));
    render(<Agent2ScientificPresentation turnId="turn-1" projectId="project-1" sessionId="session-1" canModify={false} />);
    await screen.findByText("结果解读暂时无法读取，分析结果仍可查看。");
    expect(screen.queryByText("更多操作")).toBeNull();
    expect(mocks.createAgent2ResearchTurn).not.toHaveBeenCalled();
  });

  it("pins and unpins the exact result through session memory controls", async () => {
    mocks.getAgent2ResearchTurnResult.mockResolvedValue(result);
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(new Error("not ready"));
    mocks.pinAgent2Result.mockResolvedValue({ ...memory, version: 2, pinned_result_refs: ["snapshot-1"] });
    mocks.unpinAgent2Result.mockResolvedValue({ ...memory, version: 3, pinned_result_refs: [] });

    render(<Agent2ScientificPresentation turnId="turn-1" projectId="project-1" sessionId="session-1" />);
    fireEvent.click(await screen.findByText("更多操作"));
    const pin = await screen.findByRole("button", { name: "将结果加入本会话上下文" });
    fireEvent.click(pin);
    await waitFor(() => expect(mocks.pinAgent2Result).toHaveBeenCalledWith("project-1", "session-1", "snapshot-1", { signal: expect.any(AbortSignal) }));
    const unpin = await screen.findByRole("button", { name: "从本会话上下文移除结果" });
    fireEvent.click(unpin);
    await waitFor(() => expect(mocks.unpinAgent2Result).toHaveBeenCalledWith("project-1", "session-1", "snapshot-1", { signal: expect.any(AbortSignal) }));
  });

  it("pins and unpins exact source versions through session memory controls", async () => {
    const source = { object_id: "object-1", version_id: "version-1", project_id: "project-1", object_type: "structure.crystal", display_name: "Structure" };
    mocks.getAgent2ResearchTurnResult.mockResolvedValue({ ...result, source_object_refs: [source] });
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(new Error("not ready"));
    mocks.pinAgent2Object.mockResolvedValue({ ...memory, version: 2, pinned_object_refs: [source] });
    mocks.unpinAgent2Object.mockResolvedValue({ ...memory, version: 3 });

    render(<Agent2ScientificPresentation turnId="turn-1" projectId="project-1" sessionId="session-1" />);
    fireEvent.click(await screen.findByText("更多操作"));
    fireEvent.click(await screen.findByRole("button", { name: "将来源版本加入本会话上下文" }));
    await waitFor(() => expect(mocks.pinAgent2Object).toHaveBeenCalledWith("project-1", "session-1", expect.objectContaining({
      object_id: source.object_id,
      version_id: source.version_id,
    }), { signal: expect.any(AbortSignal) }));
    fireEvent.click(await screen.findByRole("button", { name: "从本会话上下文移除来源版本" }));
    await waitFor(() => expect(mocks.unpinAgent2Object).toHaveBeenCalledWith("project-1", "session-1", expect.objectContaining({
      object_id: source.object_id,
      version_id: source.version_id,
    }), { signal: expect.any(AbortSignal) }));
  });

  it("shares context with another entry point without an independent memory read", async () => {
    mocks.getAgent2ResearchTurnResult.mockResolvedValue(result);
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(new Error("not ready"));
    mocks.pinAgent2Result.mockResolvedValue({ ...memory, version: 2, pinned_result_refs: ["snapshot-1"] });
    mocks.unpinAgent2Result.mockResolvedValue({ ...memory, version: 3 });
    function Harness() {
      const context = useSessionMemory("project-1", "session-1", true);
      return <><button onClick={() => void context.setResultPinned("snapshot-1", false)} disabled={!context.canUpdate}>移除同一结果</button>
        <Presentation turnId="turn-1" projectId="project-1" sessionId="session-1" context={context} /></>;
    }
    render(<Harness />);
    fireEvent.click(await screen.findByText("更多操作"));
    fireEvent.click(await screen.findByRole("button", { name: "将结果加入本会话上下文" }));
    expect(await screen.findByRole("button", { name: "从本会话上下文移除结果" })).toBeEnabled();
    fireEvent.click(screen.getByRole("button", { name: "移除同一结果" }));
    expect(await screen.findByRole("button", { name: "将结果加入本会话上下文" })).toBeEnabled();
    expect(mocks.getAgent2SessionMemory).toHaveBeenCalledOnce();
  });

  it("does not offer a mutation while the saved context is unknown", async () => {
    let resolveMemory!: (value: Agent2SessionMemory) => void;
    mocks.getAgent2SessionMemory.mockImplementation(() => new Promise((resolve) => { resolveMemory = resolve; }));
    mocks.getAgent2ResearchTurnResult.mockResolvedValue(result);
    mocks.getAgent2ResearchTurnInterpretation.mockRejectedValue(new Error("not ready"));
    render(<Agent2ScientificPresentation turnId="turn-1" projectId="project-1" sessionId="session-1" />);
    fireEvent.click(await screen.findByText("更多操作"));
    const pin = screen.getByRole("button", { name: "将结果加入本会话上下文" });
    expect(pin).toBeDisabled();
    fireEvent.click(pin); expect(mocks.pinAgent2Result).not.toHaveBeenCalled();
    await act(async () => resolveMemory({ ...memory, version: 2, pinned_result_refs: ["snapshot-1"] }));
    expect(await screen.findByRole("button", { name: "从本会话上下文移除结果" })).toBeEnabled();
  });
});
