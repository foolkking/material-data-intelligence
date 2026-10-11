import { afterEach, expect, it, vi } from "vitest";
import { listTurnLiteratureEvidence, preferredLiteratureSnapshot, searchScientificLiterature, selectLiteratureEvidence, type LiteratureCandidate } from "./scientific-knowledge-api";

const snapshot = { snapshot_id: "crossref", provider: "CROSSREF" as const, title: "Metadata title", authors: [], publication_status: "PEER_REVIEWED_ARTICLE", access_status: "METADATA_ONLY", retrieved_at: "2026-09-30T12:00:00Z" };
const candidate: LiteratureCandidate = { candidate_id: "candidate", work: { work_id: "work", canonical_key: "doi:example" }, possible_duplicate_of: [], snapshots: [{ ...snapshot, snapshot_id: "openalex", provider: "OPENALEX", abstract: "Other provider's abstract", retrieved_at: "2026-09-30T13:00:00Z" }, snapshot] };
afterEach(() => vi.unstubAllGlobals());

it("uses the same immutable snapshot as the current server, without borrowing another provider's abstract", async () => {
  const fetcher = vi.fn().mockResolvedValue(new Response("{}")); vi.stubGlobal("fetch", fetcher);
  expect(preferredLiteratureSnapshot(candidate).snapshot_id).toBe("crossref");
  await selectLiteratureEvidence("project", "turn", candidate);
  expect(JSON.parse(fetcher.mock.calls[0][1].body)).toMatchObject({ research_turn_id: "turn", candidate_id: "candidate", scope: "METADATA_ONLY", passage: null });
  expect(candidate.snapshots[0].snapshot_id).toBe("openalex");
});
it("matches server preference for non-retracted sources, provider priority and newest retrieval", () => {
  expect(preferredLiteratureSnapshot({ ...candidate, snapshots: [{ ...snapshot, publication_status: "RETRACTED" }, candidate.snapshots[0]] }).snapshot_id).toBe("openalex");
  expect(preferredLiteratureSnapshot({ ...candidate, snapshots: [snapshot, { ...snapshot, snapshot_id: "latest", retrieved_at: "2026-10-01T12:00:00Z" }] }).snapshot_id).toBe("latest");
});
it("keeps request cancellation out of the external query payload", async () => {
  const fetcher = vi.fn().mockImplementation(() => Promise.resolve(new Response("{}"))); vi.stubGlobal("fetch", fetcher);
  const controller = new AbortController();
  await listTurnLiteratureEvidence("turn", { signal: controller.signal });
  await searchScientificLiterature("project", "turn", "diffusion", { signal: controller.signal });
  await selectLiteratureEvidence("project", "turn", candidate, { signal: controller.signal });
  expect(fetcher.mock.calls.every(([, request]) => request.signal === controller.signal)).toBe(true);
  expect(JSON.parse(fetcher.mock.calls[1][1].body).query.scientific_question).toBe("diffusion");
  expect(fetcher.mock.calls[1][1].body).not.toContain("signal");
});
it("reports session expiry without rendering raw provider error content", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("private upstream detail", { status: 401 })));
  const expired = vi.fn(); window.addEventListener("mdi:session-expired", expired);
  try { await expect(listTurnLiteratureEvidence("turn")).rejects.toMatchObject({ status: 401, message: "文献请求暂时未能完成 (401)" }); expect(expired).toHaveBeenCalledOnce(); }
  finally { window.removeEventListener("mdi:session-expired", expired); }
});
