import React, { useRef } from "react";
import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { useConversationScroll } from "./use-conversation-scroll";

type Size = { content: number; height: number; width: number; top: number; question: number };
const size = (): Size => ({ content: 1000, height: 400, width: 600, top: 0, question: 360 });
const rect = (top: number, height: number) => ({ top, bottom: top + height, height, left: 0, right: 600, width: 600, x: 0, y: top, toJSON: () => ({}) });
let observers: Array<() => void>;
let frames: Map<number, FrameRequestCallback>;

beforeEach(() => {
  observers = [];
  frames = new Map();
  let frameId = 0;
  vi.spyOn(window, "requestAnimationFrame").mockImplementation(callback => { frames.set(++frameId, callback); return frameId; });
  vi.spyOn(window, "cancelAnimationFrame").mockImplementation(id => { frames.delete(id); });
  vi.stubGlobal("ResizeObserver", class {
    constructor(callback: () => void) { observers.push(callback); }
    observe() {}
    disconnect() {}
  });
});
afterEach(() => { window.getSelection()?.removeAllRanges(); vi.restoreAllMocks(); vi.unstubAllGlobals(); });

function flushFrames() {
  act(() => { const pending = [...frames.values()]; frames.clear(); pending.forEach(callback => callback(0)); });
}
function resize() { act(() => observers.at(-1)?.()); }

function Conversation({ dimensions, scope = "project/session/turn-1", text, answerId = "response-1", streaming = false, answerPending = false, question = null, ready = true }: {
  dimensions: Size; scope?: string; text?: string; answerId?: string; streaming?: boolean; answerPending?: boolean; question?: string | null; ready?: boolean;
}) {
  const viewportRef = useRef<HTMLDivElement | null>(null);
  const scroll = useConversationScroll({ scope, viewportRef, focusMessageId: question, answerId, answerText: text, streaming, answerPending, ready });
  return <>
    <p>其它面板文字</p>
    {ready ? <>
      <div role="region" aria-label="对话内容" tabIndex={0} ref={element => {
        viewportRef.current = element;
        if (!element) return;
        Object.defineProperties(element, {
          scrollHeight: { configurable: true, get: () => dimensions.content },
          clientHeight: { configurable: true, get: () => dimensions.height },
          clientWidth: { configurable: true, get: () => dimensions.width },
          scrollTop: { configurable: true, get: () => dimensions.top, set: value => { dimensions.top = Math.max(0, Math.min(value, dimensions.content - dimensions.height)); } },
        });
        element.getBoundingClientRect = () => rect(100, dimensions.height);
      }}>
        <div ref={scroll.contentRef} role="log" aria-label="研究对话">
          {question ? <p data-message-id={question} ref={element => {
            if (element) element.getBoundingClientRect = () => rect(100 + dimensions.question - dimensions.top, 80);
          }}>当前问题</p> : null}
          <p>{text || "历史回答"}</p>
        </div>
      </div>
      {scroll.showJump ? <button ref={scroll.jumpButtonRef} onClick={scroll.jumpToLatest}>回到对话底部</button> : null}
    </> : <p>正在加载</p>}
  </>;
}

it("follows growing Markdown and its final saved replacement without following later history expansion", () => {
  const dimensions = size();
  const view = render(<Conversation dimensions={dimensions} text="第一段" streaming />);
  expect(dimensions.top).toBe(600);
  expect(screen.queryByRole("button", { name: "回到对话底部" })).toBeNull();
  dimensions.content = 1500;
  view.rerender(<Conversation dimensions={dimensions} text="第一段\n\n第二段" streaming />);
  expect(dimensions.top).toBe(1100);
  dimensions.content = 1600;
  view.rerender(<Conversation dimensions={dimensions} text="完整回答" />);
  expect(dimensions.top).toBe(1200);
  dimensions.content = 1650;
  view.rerender(<Conversation dimensions={dimensions} text="完整回答" answerId="saved-message" />);
  expect(dimensions.top).toBe(1250);
  dimensions.content = 2000;
  resize();
  expect(dimensions.top).toBe(1250);
  expect(screen.getByRole("button", { name: "回到对话底部" })).toBeVisible();
});

it("follows an accepted answer that completes before its first public text delta", () => {
  const dimensions = { ...size(), content: 200 };
  const view = render(<Conversation dimensions={dimensions} answerPending />);
  dimensions.content = 1000;
  view.rerender(<Conversation dimensions={dimensions} text="已完成的回答" answerId="saved-message" />);
  expect(dimensions.top).toBe(600);
  expect(screen.queryByRole("button", { name: "回到对话底部" })).toBeNull();
});

it("keeps manual reading through deltas and completion, then resumes with keyboard focus in the conversation", () => {
  const dimensions = size();
  const view = render(<Conversation dimensions={dimensions} text="第一段" streaming />);
  const viewport = screen.getByRole("region", { name: "对话内容" });
  viewport.scrollTop = 120;
  fireEvent.scroll(viewport);
  dimensions.content = 1600;
  view.rerender(<Conversation dimensions={dimensions} text="第二段" streaming />);
  expect(dimensions.top).toBe(120);
  view.rerender(<Conversation dimensions={dimensions} text="已保存的回答" />);
  expect(dimensions.top).toBe(120);
  const jump = screen.getByRole("button", { name: "回到对话底部" });
  jump.focus();
  fireEvent.click(jump);
  expect(dimensions.top).toBe(1200);
  expect(viewport).toHaveFocus();
  expect(screen.queryByRole("button", { name: "回到对话底部" })).toBeNull();
  dimensions.content = 1700;
  view.rerender(<Conversation dimensions={dimensions} text="已保存的回答及来源" answerId="saved-message" />);
  expect(dimensions.top).toBe(1300);
});

it.each(["project/session/turn-2", "project/other-session/turn-1", "other-project/session/turn-1"])("resets paused following in a new scope: %s", scope => {
  const dimensions = size();
  const view = render(<Conversation dimensions={dimensions} text="回答" streaming />);
  const viewport = screen.getByRole("region", { name: "对话内容" });
  viewport.scrollTop = 80;
  fireEvent.scroll(viewport);
  const staleResize = observers.at(-1)!;
  dimensions.content = 1200;
  view.rerender(<Conversation dimensions={dimensions} scope={scope} text="新分支" streaming />);
  expect(dimensions.top).toBe(800);
  viewport.scrollTop = 100;
  fireEvent.scroll(viewport);
  dimensions.content = 1500;
  act(staleResize);
  expect(dimensions.top).toBe(100);
});

it("centers a historical question without mistaking that scroll for a request to pause a new answer", () => {
  const dimensions = size();
  const view = render(<Conversation dimensions={dimensions} question="question-1" text="已保存回答" />);
  flushFrames();
  expect(dimensions.top).toBe(200);
  fireEvent.scroll(screen.getByRole("region", { name: "对话内容" }));
  view.rerender(<Conversation dimensions={dimensions} question="question-1" text="正在生成" streaming />);
  expect(dimensions.top).toBe(600);
});

it("does not follow the initial layout of a restored answer as if it were streaming", () => {
  const dimensions = { ...size(), content: 200 };
  const view = render(<Conversation dimensions={dimensions} />);
  dimensions.content = 1400;
  dimensions.height = 420;
  resize();
  expect(dimensions.top).toBe(0);
  view.rerender(<Conversation dimensions={dimensions} text="已保存的回答" question="question-1" />);
  flushFrames();
  expect(dimensions.top).toBe(190);
  const jump = screen.getByRole("button", { name: "回到对话底部" });
  fireEvent.click(jump);
  view.rerender(<Conversation dimensions={dimensions} text="已保存的回答" question="late-question" />);
  flushFrames();
  expect(dimensions.top).toBe(980);
  dimensions.height = 300;
  resize();
  expect(dimensions.top).toBe(1100);
});

it("does not let a delayed branch directory pull a streamed answer back to its question", () => {
  const dimensions = size();
  const view = render(<Conversation dimensions={dimensions} text="正在生成" streaming />);
  view.rerender(<Conversation dimensions={dimensions} question="late-question" text="正在生成" streaming />);
  flushFrames();
  expect(dimensions.top).toBe(600);
});

it("does not center a late question after the reader has moved", () => {
  const dimensions = size();
  const view = render(<Conversation dimensions={dimensions} text="保存的回答" />);
  const viewport = screen.getByRole("region", { name: "对话内容" });
  viewport.scrollTop = 120;
  fireEvent.scroll(viewport);
  view.rerender(<Conversation dimensions={dimensions} question="late-question" text="保存的回答" />);
  flushFrames();
  expect(dimensions.top).toBe(120);
});

it("pauses while selecting answer text and resumes only when the reader returns to the bottom", () => {
  const dimensions = size();
  const view = render(<Conversation dimensions={dimensions} text="可选择的研究回答" streaming />);
  const selection = window.getSelection()!;
  const range = document.createRange();
  range.selectNodeContents(screen.getByText("可选择的研究回答"));
  selection.addRange(range);
  fireEvent(document, new Event("selectionchange"));
  dimensions.content = 1400;
  view.rerender(<Conversation dimensions={dimensions} text="可选择的研究回答及后续段落" streaming />);
  expect(dimensions.top).toBe(600);
  selection.removeAllRanges();
  dimensions.content = 1500;
  view.rerender(<Conversation dimensions={dimensions} text="最后一段" streaming />);
  expect(dimensions.top).toBe(600);
  fireEvent.click(screen.getByRole("button", { name: "回到对话底部" }));
  expect(dimensions.top).toBe(1100);
  dimensions.content = 1600;
  view.rerender(<Conversation dimensions={dimensions} text="完整回答" />);
  expect(dimensions.top).toBe(1200);
});

it("does not stop following when text is selected outside the conversation", () => {
  const dimensions = size();
  const view = render(<Conversation dimensions={dimensions} text="第一段" streaming />);
  const range = document.createRange();
  range.selectNodeContents(screen.getByText("其它面板文字"));
  window.getSelection()!.addRange(range);
  fireEvent(document, new Event("selectionchange"));
  dimensions.content = 1300;
  view.rerender(<Conversation dimensions={dimensions} text="后续段落" streaming />);
  expect(dimensions.top).toBe(900);
});

it("handles Markdown reflow and viewport resize while preserving manual reading", () => {
  const dimensions = size();
  render(<Conversation dimensions={dimensions} text="表格与公式" streaming />);
  dimensions.content = 1200;
  resize();
  expect(dimensions.top).toBe(800);
  dimensions.height = 300;
  resize();
  expect(dimensions.top).toBe(900);
  const viewport = screen.getByRole("region", { name: "对话内容" });
  viewport.scrollTop = 100;
  fireEvent.scroll(viewport);
  dimensions.content = 1600;
  dimensions.width = 320;
  resize();
  expect(dimensions.top).toBe(100);
});

it("installs scrolling when the page finishes loading and hides the jump control when content fits", () => {
  const dimensions = size();
  const view = render(<Conversation dimensions={dimensions} ready={false} />);
  view.rerender(<Conversation dimensions={dimensions} text="第一段" streaming />);
  expect(dimensions.top).toBe(600);
  const viewport = screen.getByRole("region", { name: "对话内容" });
  viewport.scrollTop = 80;
  fireEvent.scroll(viewport);
  dimensions.content = 1400;
  view.rerender(<Conversation dimensions={dimensions} text="后续段落" streaming />);
  expect(dimensions.top).toBe(80);
  screen.getByRole("button", { name: "回到对话底部" }).focus();
  dimensions.content = 200;
  dimensions.top = 0;
  resize();
  expect(screen.queryByRole("button", { name: "回到对话底部" })).toBeNull();
  expect(viewport).toHaveFocus();
});

it.each(["wheel", "keyboard"])("respects %s reading intent before content overflows", intent => {
  const dimensions = { ...size(), content: 200 };
  const view = render(<Conversation dimensions={dimensions} text="第一段" streaming />);
  const viewport = screen.getByRole("region", { name: "对话内容" });
  if (intent === "wheel") fireEvent.wheel(viewport, { deltaY: -100 });
  else fireEvent.keyDown(viewport, { key: "PageUp" });
  dimensions.content = 1500;
  view.rerender(<Conversation dimensions={dimensions} text="完整长回答" streaming />);
  expect(dimensions.top).toBe(0);
  expect(screen.getByRole("button", { name: "回到对话底部" })).toBeVisible();
});
