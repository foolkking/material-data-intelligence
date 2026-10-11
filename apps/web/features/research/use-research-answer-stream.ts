import { useEffect, useRef, useState } from "react";

const API_BASE = (process.env.NEXT_PUBLIC_MDI_API_BASE_URL || (typeof window === "undefined" ? "http://127.0.0.1:8000" : "/api")).replace(/\/$/, "");
export type ResearchAnswerDraft = {
  turnId: string;
  responseId: string;
  revision: number;
  text: string;
  phase: "streaming" | "reconnecting" | "completed";
  messageId?: string;
  scientific?: boolean;
};

export function applyAnswerFrame(current: ResearchAnswerDraft | null, turnId: string, kind: string, value: unknown): ResearchAnswerDraft | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("Invalid answer frame");
  const frame = value as Record<string, unknown>;
  if (frame.turn_id !== turnId) throw new Error("Answer belongs to another turn");
  if (current?.phase === "completed" && kind !== "answer.completed") return current;
  if (kind === "answer.reset") return current?.responseId === frame.response_id ? null : current;
  if (kind === "answer.stopped" || kind === "answer.unavailable") return null;
  if (kind === "answer.completed") {
    if (typeof frame.message_id !== "string" || !frame.message_id || typeof frame.text !== "string" || frame.text.length > 64_000 ||
        !["ANSWERED", "COMPLETED", "PARTIAL", "NEEDS_CLARIFICATION"].includes(String(frame.status))) throw new Error("Invalid completed answer");
    return { turnId, responseId: current?.responseId || frame.message_id, revision: current?.revision || 0, text: frame.text, phase: "completed", messageId: frame.message_id,
      scientific: frame.response_kind === "SCIENTIFIC_INTERPRETATION" || current?.scientific };
  }
  if (kind !== "answer.delta" || typeof frame.response_id !== "string" || !frame.response_id || frame.response_id.length > 128 ||
      !Number.isSafeInteger(frame.revision) || Number(frame.revision) < 1 || Number(frame.revision) > 129 || typeof frame.text !== "string") throw new Error("Invalid answer delta");
  if (current?.phase === "completed") return current;
  const prior = current?.responseId === frame.response_id ? current : null;
  if (prior && Number(frame.revision) <= prior.revision) return prior;
  if (Number(frame.revision) !== (prior?.revision || 0) + 1) throw new Error("Missing answer delta");
  const text = (prior?.text || "") + frame.text;
  if (text.length > 32_000) throw new Error("Answer exceeds display limit");
  return { turnId, responseId: frame.response_id, revision: Number(frame.revision), text, phase: "streaming",
    scientific: frame.response_kind === "SCIENTIFIC_INTERPRETATION" || prior?.scientific };
}

export function useResearchAnswerStream(turnId: string | null, status: string | undefined, onSettled: () => void) {
  const [draft, setDraft] = useState<ResearchAnswerDraft | null>(null);
  const settled = useRef(onSettled);
  settled.current = onSettled;
  const enabled = !status || ["RECEIVED", "RESOLVING_CONTEXT", "ORCHESTRATING", "INTERPRETING", "ANSWERED", "COMPLETED", "PARTIAL", "NEEDS_CLARIFICATION"].includes(status);
  useEffect(() => {
    if (!turnId || !enabled || typeof EventSource === "undefined") return;
    let active = true;
    let current: ResearchAnswerDraft | null = null;
    let source: EventSource;
    let repairs = 0;
    setDraft(null);
    function connect() {
      source = new EventSource(`${API_BASE}/api/research/turns/${encodeURIComponent(turnId!)}/answer-stream`, { withCredentials: true });
      const connection = source;
      let finished = false;
      for (const kind of ["answer.delta", "answer.reset", "answer.completed", "answer.stopped", "answer.unavailable"]) {
        source.addEventListener(kind, event => {
          if (!active || connection !== source || finished) return;
          try {
            current = applyAnswerFrame(current, turnId!, kind, JSON.parse((event as MessageEvent).data));
            setDraft(current);
            if (kind === "answer.completed" || kind === "answer.stopped") {
              finished = true;
              source.close();
              settled.current();
            } else if (kind === "answer.unavailable") {
              settled.current();
            }
          } catch {
            source.close();
            current = null;
            setDraft(null);
            if (++repairs <= 1) connect();
            else settled.current();
          }
        });
      }
      source.onopen = () => {
        if (active && connection === source && current?.phase === "reconnecting") {
          current = { ...current, phase: "streaming" };
          setDraft(current);
        }
      };
      source.onerror = () => {
        if (active && connection === source && current && current.phase !== "completed") {
          current = { ...current, phase: "reconnecting" };
          setDraft(current);
        }
      };
    }
    connect();
    return () => { active = false; source.close(); };
  }, [turnId, enabled]);
  const visible = enabled || ["COMPLETED", "PARTIAL"].includes(status || "");
  return visible && draft?.turnId === turnId ? draft : null;
}
