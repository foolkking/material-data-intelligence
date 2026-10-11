import { useCallback, useLayoutEffect, useRef, useState, type RefObject } from "react";

const BOTTOM_THRESHOLD = 64;

function hasConversationSelection(container: HTMLElement) {
  const selection = window.getSelection();
  return Boolean(selection?.toString() &&
    (container.contains(selection.anchorNode) || container.contains(selection.focusNode)));
}

export function useConversationScroll({
  scope, viewportRef, focusMessageId, answerId, answerText, streaming, answerPending = false, ready = true,
}: {
  scope: string;
  viewportRef: RefObject<HTMLDivElement | null>;
  focusMessageId: string | null;
  answerId?: string;
  answerText?: string;
  streaming: boolean;
  answerPending?: boolean;
  ready?: boolean;
}) {
  const contentRef = useRef<HTMLDivElement | null>(null);
  const jumpButtonRef = useRef<HTMLButtonElement | null>(null);
  const [showJump, setShowJump] = useState(false);
  const follow = useRef(true);
  const hasLiveAnswer = useRef(false);
  const streamActive = useRef(false);
  const userMoved = useRef(false);
  const atBottom = useRef(true);
  const expectedScrollTop = useRef<number | null>(null);

  const measure = useCallback(() => {
    const container = viewportRef.current;
    const visible = Boolean(container && container.clientHeight > 0);
    atBottom.current = Boolean(container &&
      container.scrollHeight - container.clientHeight - container.scrollTop <= BOTTOM_THRESHOLD);
    const next = visible && !atBottom.current;
    if (!next && visible && document.activeElement === jumpButtonRef.current) {
      container?.focus({ preventScroll: true });
    }
    setShowJump(next);
  }, [viewportRef]);

  const scrollToBottom = useCallback(() => {
    const container = viewportRef.current;
    if (!container || container.clientHeight <= 0) return;
    container.scrollTop = Math.max(0, container.scrollHeight - container.clientHeight);
    expectedScrollTop.current = container.scrollTop;
    measure();
  }, [measure, viewportRef]);

  useLayoutEffect(() => {
    follow.current = true;
    hasLiveAnswer.current = false;
    userMoved.current = false;
    expectedScrollTop.current = viewportRef.current?.scrollTop ?? null;
  }, [scope, viewportRef]);

  useLayoutEffect(() => {
    streamActive.current = streaming;
    if (streaming || answerPending) hasLiveAnswer.current = true;
    if (!ready) return;
    const container = viewportRef.current;
    if (container && hasConversationSelection(container)) follow.current = false;
    // Keep following the final saved replacement, but never jump on a
    // completed answer's initial replay or on unrelated history updates.
    if (hasLiveAnswer.current && follow.current) scrollToBottom();
    measure();
  }, [scope, answerId, answerText, streaming, answerPending, ready, measure, scrollToBottom, viewportRef]);

  useLayoutEffect(() => {
    if (!ready || !focusMessageId) return;
    const frame = window.requestAnimationFrame(() => {
      if (hasLiveAnswer.current || userMoved.current) return;
      const container = viewportRef.current;
      const message = Array.from(container?.querySelectorAll<HTMLElement>("[data-message-id]") || [])
        .find(element => element.dataset.messageId === focusMessageId);
      if (!container || !message || container.clientHeight <= 0) return;
      const containerRect = container.getBoundingClientRect();
      const messageRect = message.getBoundingClientRect();
      container.scrollTop = Math.max(0, container.scrollTop + messageRect.top - containerRect.top -
        Math.max(16, (container.clientHeight - messageRect.height) / 2));
      // This is branch navigation, not a request to pause a new answer.
      expectedScrollTop.current = container.scrollTop;
      measure();
    });
    return () => window.cancelAnimationFrame(frame);
  }, [scope, focusMessageId, ready, measure, viewportRef]);

  useLayoutEffect(() => {
    const container = viewportRef.current;
    if (!ready || !container) return;
    let active = true;
    let width = container.clientWidth;
    let height = container.clientHeight;
    const pause = () => { follow.current = false; userMoved.current = true; };
    const onScroll = () => {
      const expected = expectedScrollTop.current;
      expectedScrollTop.current = null;
      measure();
      if (expected !== null && Math.abs(container.scrollTop - expected) <= 1) return;
      follow.current = atBottom.current && !hasConversationSelection(container);
      userMoved.current = true;
    };
    const onWheel = (event: WheelEvent) => { if (event.deltaY < 0) pause(); };
    const onKeyDown = (event: KeyboardEvent) => {
      const target = event.target;
      if (target instanceof HTMLElement && target.closest("input, textarea, select, [contenteditable=true]")) return;
      if (["ArrowUp", "PageUp", "Home"].includes(event.key)) pause();
    };
    const onSelection = () => { if (hasConversationSelection(container)) pause(); };
    const onResize = () => {
      if (!active) return;
      const resized = width !== container.clientWidth || height !== container.clientHeight;
      width = container.clientWidth;
      height = container.clientHeight;
      if (follow.current && !hasConversationSelection(container) &&
          (streamActive.current || (resized && atBottom.current && (hasLiveAnswer.current || userMoved.current)))) scrollToBottom();
      else measure();
    };
    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(onResize);
    observer?.observe(container);
    if (contentRef.current) observer?.observe(contentRef.current);
    container.addEventListener("scroll", onScroll, { passive: true });
    container.addEventListener("wheel", onWheel, { passive: true });
    container.addEventListener("keydown", onKeyDown);
    document.addEventListener("selectionchange", onSelection);
    measure();
    return () => {
      active = false;
      observer?.disconnect();
      container.removeEventListener("scroll", onScroll);
      container.removeEventListener("wheel", onWheel);
      container.removeEventListener("keydown", onKeyDown);
      document.removeEventListener("selectionchange", onSelection);
    };
  }, [scope, ready, measure, scrollToBottom, viewportRef]);

  const jumpToLatest = useCallback(() => {
    const container = viewportRef.current;
    if (!container) return;
    if (hasConversationSelection(container)) window.getSelection()?.removeAllRanges();
    follow.current = true;
    userMoved.current = true;
    container.focus({ preventScroll: true });
    scrollToBottom();
  }, [scrollToBottom, viewportRef]);

  return { contentRef, jumpButtonRef, showJump, jumpToLatest };
}
