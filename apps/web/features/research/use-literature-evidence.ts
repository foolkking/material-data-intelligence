"use client";

import { useEffect, useRef, useState } from "react";
import { KnowledgeRequestError, listTurnLiteratureEvidence, preferredLiteratureSnapshot, searchScientificLiterature, selectLiteratureEvidence, type LiteratureCandidate, type LiteratureEvidenceRow } from "../../app/lib/scientific-knowledge-api";
import { readSessionRequest } from "./session-management";

export function useLiteratureEvidence(projectId: string, turnId: string) {
  const [used, setUsed] = useState<LiteratureEvidenceRow[]>([]);
  const [candidates, setCandidates] = useState<LiteratureCandidate[]>([]);
  const [question, setQuestion] = useState("");
  const [searchedQuestion, setSearchedQuestion] = useState("");
  const [readState, setReadState] = useState<"loading" | "ready" | "error">("loading");
  const [operation, setOperation] = useState<"search" | "select" | null>(null);
  const [pendingCandidateId, setPendingCandidateId] = useState<string | null>(null);
  const [unconfirmed, setUnconfirmed] = useState(false);
  const [error, setError] = useState("");
  const owner = useRef<AbortController | null>(null);
  const readOwner = useRef<AbortController | null>(null);
  const operationPending = useRef(false);
  const unresolvedSelection = useRef<LiteratureCandidate | null>(null);
  const usedRef = useRef(used);
  const alreadyUsed = (candidate: LiteratureCandidate) => usedRef.current.some((item) => item.work_id === candidate.work.work_id && item.snapshot_id === preferredLiteratureSnapshot(candidate)?.snapshot_id);

  async function refreshUsed() {
    const scope = owner.current;
    if (!scope || scope.signal.aborted) return;
    readOwner.current?.abort();
    const request = new AbortController(); readOwner.current = request;
    setReadState("loading");
    try {
      const response = await readSessionRequest((signal) => listTurnLiteratureEvidence(turnId, { signal }), request.signal);
      if (scope.signal.aborted || readOwner.current !== request) return;
      if (response?.turnId !== turnId || !Array.isArray(response.literatureEvidence) || response.literatureEvidence.some((item) => !item.id || !item.work_id || !item.snapshot_id || (item.project_id && item.project_id !== projectId) || (item.research_turn_id && item.research_turn_id !== turnId))) throw new Error("Literature scope mismatch");
      usedRef.current = response.literatureEvidence;
      setUsed(response.literatureEvidence); setReadState("ready");
      if (unresolvedSelection.current) {
        setError(alreadyUsed(unresolvedSelection.current) ? "" : "尚未确认文献已加入；已重新读取记录，可再次尝试。");
        unresolvedSelection.current = null; setUnconfirmed(false);
      }
    } catch {
      if (!scope.signal.aborted && readOwner.current === request) setReadState("error");
    } finally { if (readOwner.current === request) readOwner.current = null; }
  }

  useEffect(() => {
    const controller = new AbortController(); owner.current = controller;
    void refreshUsed();
    return () => { controller.abort(); readOwner.current?.abort(); };
  }, [projectId, turnId]);

  async function runSearch() {
    const value = question.trim(), scope = owner.current;
    if (!value || !scope || scope.signal.aborted || operationPending.current || unresolvedSelection.current) return;
    operationPending.current = true; setOperation("search"); setError("");
    try {
      const response = await readSessionRequest((signal) => searchScientificLiterature(projectId, turnId, value, { signal }), scope.signal);
      if (scope.signal.aborted) return;
      // Cached public metadata can originate from another Turn in this project.
      if (!Array.isArray(response?.candidates) || (response.search?.project_id && response.search.project_id !== projectId) || (response.cacheStatus !== "REUSED_FRESH_PUBLIC_METADATA" && response.search?.research_turn_id && response.search.research_turn_id !== turnId) || response.candidates.some((candidate) =>
        !candidate.candidate_id || !candidate.work?.work_id || !Array.isArray(candidate.snapshots) || !candidate.snapshots.length || candidate.snapshots.some((snapshot) => !snapshot.snapshot_id || !snapshot.title || !Array.isArray(snapshot.authors) || !Number.isFinite(Date.parse(snapshot.retrieved_at))))) throw new Error("Literature search content invalid");
      setCandidates(response.candidates); setSearchedQuestion(value);
    } catch {
      if (!scope.signal.aborted) setError(candidates.length ? "文献检索暂未完成，已保留检索词和先前结果，请重试。" : "文献检索暂未完成，已保留检索词，请重试。");
    } finally {
      if (!scope.signal.aborted) { operationPending.current = false; setOperation(null); }
    }
  }

  async function useCandidate(candidate: LiteratureCandidate) {
    const scope = owner.current, snapshot = preferredLiteratureSnapshot(candidate);
    if (!scope || scope.signal.aborted || readState !== "ready" || operationPending.current || unresolvedSelection.current || alreadyUsed(candidate) || !snapshot || ["RETRACTED", "WITHDRAWN"].includes(snapshot.publication_status)) return;
    operationPending.current = true; setOperation("select"); setPendingCandidateId(candidate.candidate_id); setError("");
    // Old directory reads cannot settle a selection submitted after they began.
    readOwner.current?.abort(); readOwner.current = null;
    try {
      const response = await readSessionRequest((signal) => selectLiteratureEvidence(projectId, turnId, candidate, { signal }), scope.signal);
      if (scope.signal.aborted) return;
      if (!response?.evidence_id || response.project_id !== projectId || response.research_turn_id !== turnId || response.work_id !== candidate.work.work_id || response.snapshot_id !== snapshot.snapshot_id) {
        // A changed source requires a fresh search before offering another save.
        setCandidates((current) => current.filter((item) => item.candidate_id !== candidate.candidate_id));
        setSearchedQuestion("");
        throw new Error("Literature selection mismatch");
      }
      unresolvedSelection.current = candidate; setUnconfirmed(true);
      setError("文献加入请求已收到，正在更新已用文献。");
    } catch (reason) {
      if (scope.signal.aborted) return;
      const rejected = reason instanceof KnowledgeRequestError && [400, 401, 403, 404, 409, 422].includes(reason.status);
      if (!rejected) { unresolvedSelection.current = candidate; setUnconfirmed(true); }
      setError(rejected ? "文献未能加入，请检查来源后重试。" : "加入结果尚未确认，请重新读取已用文献。");
    } finally {
      if (!scope.signal.aborted) {
        operationPending.current = false; setOperation(null); setPendingCandidateId(null);
        void refreshUsed();
      }
    }
  }

  return { used, candidates, question, setQuestion, searchedQuestion, readState, operation, pendingCandidateId, unconfirmed, error, refreshUsed, runSearch, useCandidate, alreadyUsed };
}
