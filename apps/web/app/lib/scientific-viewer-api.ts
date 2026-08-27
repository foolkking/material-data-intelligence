const API_BASE = (process.env.NEXT_PUBLIC_MDI_API_BASE_URL || (typeof window === "undefined" ? "http://127.0.0.1:8000" : "/api")).replace(/\/$/, "");

export type ScientificObjectSummary = {
  id: string;
  project_id: string;
  kind: string;
  object_type: string;
  display_name: string;
  lifecycle_status: string;
  current_version_id: string | null;
};

export type ScientificViewerProjection = {
  contract_version: "1.0";
  project_id: string;
  object_id: string;
  version_id: string;
  object_type: string;
  object_schema_version: string;
  display_name: string;
  version_no: number;
  is_current_version: boolean;
  availability_status: string;
  viewer: {
    viewer_id: string;
    viewer_version: "1.0";
    renderer_key: string;
    support: "PROFESSIONAL" | "SUPPORTED" | "FALLBACK" | "NOT_CURRENTLY_SUPPORTED";
    interaction_capabilities: string[];
    selection_capabilities: string[];
    maximum_payload_bytes: number;
    fallback_policy: string;
  };
  payload_status: "READY" | "METADATA_ONLY" | "SOURCE_MISSING" | "INVALIDATED";
  payload: unknown;
  canonical_metadata: Record<string, unknown>;
  source_resource_refs: Array<Record<string, unknown>>;
  content_hash: string;
  semantic_hash: string;
  payload_bytes: number | null;
  omitted_item_count: number;
  limitations: string[];
};

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { credentials: "include", signal });
  if (!response.ok) throw new Error(`Scientific viewer request failed (${response.status})`);
  return response.json() as Promise<T>;
}

export const listScientificObjects = (
  projectId: string,
  signal?: AbortSignal,
  lifecycleStatus?: "ACTIVE" | "ARCHIVED",
) => request<{ items: ScientificObjectSummary[]; next_cursor: string | null }>(
  `/api/projects/${encodeURIComponent(projectId)}/scientific-objects?limit=100${lifecycleStatus ? `&lifecycle_status=${lifecycleStatus}` : ""}`,
  signal,
);

export const getScientificViewerProjection = (objectId: string, versionId: string, signal?: AbortSignal) => request<ScientificViewerProjection>(`/api/scientific-objects/${encodeURIComponent(objectId)}/versions/${encodeURIComponent(versionId)}/viewer`, signal);

export const updateScientificObject = (
  objectId: string,
  changes: { display_name?: string; archived?: boolean },
) => fetch(`${API_BASE}/api/scientific-objects/${encodeURIComponent(objectId)}`, {
  method: "PATCH",
  credentials: "include",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(changes),
}).then(async (response) => {
  if (!response.ok) throw new Error(`Scientific object update failed (${response.status})`);
  return response.json() as Promise<ScientificObjectSummary>;
});

export type ScientificDatasetQuery = {
  filters?: Array<{ column: string; operator: "eq" | "gt" | "gte" | "lt" | "lte" | "in"; value: unknown }>;
  sort_by?: string;
  descending?: boolean;
  columns?: string[];
  limit?: number;
};

export const queryScientificDataset = (objectId: string, versionId: string, query: ScientificDatasetQuery) =>
  fetch(`${API_BASE}/api/scientific-objects/${encodeURIComponent(objectId)}/versions/${encodeURIComponent(versionId)}/query`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(query),
  }).then(async (response) => {
    if (!response.ok) throw new Error(`Scientific dataset query failed (${response.status})`);
    return response.json() as Promise<{
      object_id: string;
      version_id: string;
      total_matching: number;
      limit: number;
      columns: string[];
      items: Array<Record<string, unknown> & { _stable_id: string }>;
    }>;
  });
