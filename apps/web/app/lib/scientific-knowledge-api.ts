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
  if (!response.ok) {
    let message = `文献服务暂时不可用 (${response.status})`;
    try {
      const body = (await response.json()) as {
        detail?: string | { message?: string };
      };
      if (typeof body.detail === "string") message = body.detail;
      else if (body.detail?.message) message = body.detail.message;
    } catch {
      // Keep a bounded user-facing error.
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export function listTurnLiteratureEvidence(turnId: string) {
  return knowledgeRequest<{
    turnId: string;
    literatureEvidence: LiteratureEvidenceRow[];
  }>(
    `/api/research/turns/${encodeURIComponent(turnId)}/scientific-literature`,
  );
}

export function searchScientificLiterature(
  projectId: string,
  turnId: string,
  question: string,
) {
  return knowledgeRequest<{
    candidates: LiteratureCandidate[];
    cacheStatus?: string;
    scientificResultAuthority: false;
    qualificationAuthority: false;
  }>(
    `/api/projects/${encodeURIComponent(projectId)}/scientific-literature/search`,
    {
      method: "POST",
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
) {
  const snapshot =
    candidate.snapshots.find((item) => Boolean(item.abstract)) ||
    candidate.snapshots[0];
  const abstract = snapshot?.abstract?.trim();
  return knowledgeRequest<LiteratureEvidenceRow>(
    `/api/projects/${encodeURIComponent(projectId)}/scientific-literature/evidence`,
    {
      method: "POST",
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
