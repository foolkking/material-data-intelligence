import { act, renderHook } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { applyAnswerFrame, useResearchAnswerStream } from "./use-research-answer-stream";

const delta = (revision = 1, text = "第一段", response = "response-1", turn = "turn-1") => ({ turn_id: turn, response_id: response, revision, text });

class Source extends EventTarget {
  static instances: Source[] = [];
  onopen: (() => void) | null = null;
  onerror: (() => void) | null = null;
  close = vi.fn();
  constructor(readonly url: string, readonly options: unknown) { super(); Source.instances.push(this); }
  emit(kind: string, value: unknown) { this.dispatchEvent(new MessageEvent(kind, { data: JSON.stringify(value) })); }
}
afterEach(() => { vi.unstubAllGlobals(); Source.instances = []; });

it("appends exact text once and uses the authoritative completion without duplicate tails", () => {
  let state = applyAnswerFrame(null, "turn-1", "answer.delta", delta());
  state = applyAnswerFrame(state, "turn-1", "answer.delta", delta());
  state = applyAnswerFrame(state, "turn-1", "answer.delta", delta(2, "\n\n**第二段**"));
  expect(state?.text).toBe("第一段\n\n**第二段**");
  state = applyAnswerFrame(state, "turn-1", "answer.completed", { turn_id: "turn-1", message_id: "saved-message", text: "验证后的完整回答", status: "ANSWERED" });
  expect(state).toMatchObject({ text: "验证后的完整回答", phase: "completed", messageId: "saved-message" });
  expect(applyAnswerFrame(state, "turn-1", "answer.delta", delta(3, "late"))).toBe(state);
  expect(applyAnswerFrame(state, "turn-1", "answer.reset", delta())).toBe(state);
});

it("isolates attempts and clears failed drafts before a replacement", () => {
  const first = applyAnswerFrame(null, "turn-1", "answer.delta", delta());
  expect(applyAnswerFrame(first, "turn-1", "answer.reset", { turn_id: "turn-1", response_id: "response-1" })).toBeNull();
  const next = applyAnswerFrame(first, "turn-1", "answer.delta", delta(1, "新尝试", "response-2"));
  expect(next?.text).toBe("新尝试");
  expect(applyAnswerFrame(next, "turn-1", "answer.stopped", { turn_id: "turn-1", status: "FAILED" })).toBeNull();
});

it.each([
  delta(2), delta(1, "foreign", "response", "other-turn"), delta(1, "x".repeat(32_001)),
  { turn_id: "turn-1", response_id: "r", revision: 0, text: "bad" },
])("rejects missing, foreign and malformed deltas", value => {
  expect(() => applyAnswerFrame(null, "turn-1", "answer.delta", value)).toThrow();
});

it("keeps partial text during reconnect and ignores replayed EventSource frames", () => {
  vi.stubGlobal("EventSource", Source);
  const settled = vi.fn();
  const { result, unmount } = renderHook(() => useResearchAnswerStream("turn-1", "ORCHESTRATING", settled));
  const source = Source.instances[0];
  expect(source.options).toEqual({ withCredentials: true });
  act(() => source.emit("answer.delta", delta()));
  act(() => source.onerror?.());
  expect(result.current).toMatchObject({ text: "第一段", phase: "reconnecting" });
  act(() => { source.onopen?.(); source.emit("answer.delta", delta()); source.emit("answer.delta", delta(2, "继续")); });
  expect(result.current).toMatchObject({ text: "第一段继续", phase: "streaming" });
  act(() => source.emit("answer.completed", { turn_id: "turn-1", message_id: "saved", text: "第一段继续", status: "ANSWERED" }));
  expect(settled).toHaveBeenCalledTimes(1);
  expect(source.close).toHaveBeenCalled();
  unmount();
});

it("closes branch streams and rejects late callbacks from a replaced connection", () => {
  vi.stubGlobal("EventSource", Source);
  const settled = vi.fn();
  const { result, rerender } = renderHook(({ turn, status }) => useResearchAnswerStream(turn, status, settled), { initialProps: { turn: "turn-1", status: "ORCHESTRATING" } });
  const old = Source.instances[0];
  act(() => old.emit("answer.delta", delta(2)));
  const repaired = Source.instances[1];
  act(() => repaired.emit("answer.delta", delta(1, "新连接")));
  act(() => old.emit("answer.delta", delta(2, "迟到")));
  expect(result.current?.text).toBe("新连接");
  rerender({ turn: "turn-2", status: "ORCHESTRATING" });
  expect(repaired.close).toHaveBeenCalled();
  act(() => repaired.emit("answer.delta", delta(2, "错误分支")));
  expect(result.current).toBeNull();
  const current = Source.instances[2];
  act(() => current.emit("answer.delta", delta(1, "第二个分支", "response-2", "turn-2")));
  rerender({ turn: "turn-2", status: "CANCELED" });
  expect(result.current).toBeNull();
  expect(current.close).toHaveBeenCalled();
});

it.each(["COMPLETED", "PARTIAL"])("keeps the scientific stream until saved text arrives after %s progress", status => {
  vi.stubGlobal("EventSource", Source);
  const settled = vi.fn();
  const { result, rerender } = renderHook(({ phase }) => useResearchAnswerStream("turn-1", phase, settled), { initialProps: { phase: "INTERPRETING" } });
  const source = Source.instances[0];
  act(() => source.emit("answer.delta", { ...delta(1, "## 分析结果\n\n第一峰为 2.5 Å。"), response_kind: "SCIENTIFIC_INTERPRETATION" }));
  rerender({ phase: status });
  expect(source.close).not.toHaveBeenCalled();
  expect(Source.instances).toHaveLength(1);
  act(() => source.emit("answer.completed", { turn_id: "turn-1", message_id: "saved-science", text: "## RDF 解读\n\n第一峰为 2.5 Å。\n\n### 限制\n\n- 仅当前版本。", status }));
  expect(result.current).toMatchObject({ phase: "completed", messageId: "saved-science", scientific: true });
  expect(result.current?.text).toContain("### 限制");
  expect(settled).toHaveBeenCalledOnce();
  expect(source.close).toHaveBeenCalledOnce();
});

it("identifies a saved scientific answer when reconnecting after completion", () => {
  const state = applyAnswerFrame(null, "turn-1", "answer.completed", { turn_id: "turn-1", message_id: "saved", text: "## 结果", status: "COMPLETED", response_kind: "SCIENTIFIC_INTERPRETATION" });
  expect(state).toMatchObject({ phase: "completed", scientific: true });
});
