const API_BASE = (
  process.env.NEXT_PUBLIC_MDI_API_BASE_URL ||
  (typeof window === "undefined" ? "http://127.0.0.1:8000" : "/api")
).replace(/\/$/, "");

export type LiteratureSnapshot = {
  snapshot_id: string;
  provider: "OPENALEX" | "CROSSREF" | "USER_UPLOAD";
  title: string;
  authors: string[];
  venue?: string | null;
  publication_date?: string | null;
  publication_status: string;
  doi?: string | null;
  arxiv_id?: string | null;
  abstract?: string | null;
  access_status: string;
  source_url?: string | null;
  retrieved_at: string;
};

export type LiteratureCandidate = {
  candidate_id: string;
  work: {
    work_id: string;
    canonical_key: string;
    doi?: string | null;
    arxiv_id?: string | null;
  };
  snapshots: LiteratureSnapshot[];
  possible_duplicate_of: string[];
};

export type LiteratureEvidenceRow = {
  id: string;
  project_id?: string;
  research_turn_id?: string;
  title?: string;
  citation?: string;
  publication_status?: string;
  source_url?: string | null;
  doi?: string | null;
  arxiv_id?: string | null;
  scope: string;
  support_type: string;
  purpose: string;
  passage?: string | null;
  snapshot_id: string;
  work_id: string;
  selected_at: string;
};

export type LiteratureEvidenceSelection = Omit<LiteratureEvidenceRow, "id"> & { evidence_id: string; project_id: string; research_turn_id: string };

/** Match the current server's LiteratureSearchCandidate.preferred_snapshot. */
export function preferredLiteratureSnapshot(candidate: LiteratureCandidate) {
  return [...candidate.snapshots].sort((left, right) =>
    Number(left.publication_status === "RETRACTED") - Number(right.publication_status === "RETRACTED") ||
    Number(left.provider !== "CROSSREF") - Number(right.provider !== "CROSSREF") ||
    Math.floor(Date.parse(right.retrieved_at) / 1000) - Math.floor(Date.parse(left.retrieved_at) / 1000),
  )[0];
}

export class KnowledgeRequestError extends Error {
  constructor(readonly status: number) {
    super(`文献请求暂时未能完成 (${status})`);
  }
}

async function knowledgeRequest<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  if (response.status === 401 && typeof window !== "undefined") window.dispatchEvent(new CustomEvent("mdi:session-expired"));
  if (!response.ok) throw new KnowledgeRequestError(response.status);
  return response.json() as Promise<T>;
}

export function listTurnLiteratureEvidence(turnId: string, options: Readonly<{ signal?: AbortSignal }> = {}) {
  return knowledgeRequest<{
    turnId: string;
    literatureEvidence: LiteratureEvidenceRow[];
  }>(
    `/api/research/turns/${encodeURIComponent(turnId)}/scientific-literature`,
    options,
  );
}

export function searchScientificLiterature(
  projectId: string,
  turnId: string,
  question: string,
  options: Readonly<{ signal?: AbortSignal }> = {},
) {
  return knowledgeRequest<{
    candidates: LiteratureCandidate[];
    cacheStatus?: string;
    scientificResultAuthority: false;
    qualificationAuthority: false;
    search?: { project_id?: string; research_turn_id?: string };
  }>(
    `/api/projects/${encodeURIComponent(projectId)}/scientific-literature/search`,
    {
      method: "POST",
      signal: options.signal,
      body: JSON.stringify({
        research_turn_id: turnId,
        query: {
          purpose: "BACKGROUND",
          scientific_question: question,
          search_terms: [question],
          maximum_results: 8,
          provider_scope: ["OPENALEX", "CROSSREF"],
          use_external_scientific_knowledge: true,
        },
      }),
    },
  );
}

export function selectLiteratureEvidence(
  projectId: string,
  turnId: string,
  candidate: LiteratureCandidate,
  options: Readonly<{ signal?: AbortSignal }> = {},
) {
  const snapshot = preferredLiteratureSnapshot(candidate);
  const abstract = snapshot?.abstract?.trim();
  return knowledgeRequest<LiteratureEvidenceSelection>(
    `/api/projects/${encodeURIComponent(projectId)}/scientific-literature/evidence`,
    {
      method: "POST",
      signal: options.signal,
      body: JSON.stringify({
        candidate_id: candidate.candidate_id,
        research_turn_id: turnId,
        purpose: "BACKGROUND",
        scope: abstract ? "ABSTRACT_ONLY" : "METADATA_ONLY",
        support_type: "BACKGROUND",
        passage: abstract || null,
      }),
    },
  );
}
