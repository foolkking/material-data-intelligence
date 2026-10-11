import { invalidateProjectHistory } from "./planner-api";

const API_BASE = (process.env.NEXT_PUBLIC_MDI_API_BASE_URL || (typeof window === "undefined" ? "http://127.0.0.1:8000" : "/api")).replace(/\/$/, "");

// API_BASE is `/api` in the browser (where the Next proxy strips one prefix)
// but may be a fully-qualified backend URL in SSR/runtime tooling. Preserve
// the canonical backend route in both cases without changing the proxy
// contract for `/api/*` FastAPI routers.
const apiUrl = (path: string) =>
  `${API_BASE}${/^https?:\/\//u.test(API_BASE) && API_BASE.endsWith("/api") && path.startsWith("/api/")
    ? path.slice(4)
    : path}`;

export type ScientificObjectSummary = {
  id: string;
  project_id: string;
  kind: string;
  object_type: string;
  display_name: string;
  lifecycle_status: string;
  current_version_id: string | null;
};

export type ScientificObjectDependencyImpact = {
  entity: "scientific_object";
  entityId: string;
  displayName: string;
  canDelete: false;
  dependencyCount: number;
  dependencies: Array<{ kind: string; label: string; count: number; href?: string }>;
  retentionPolicy?: {
    schemaVersion: string;
    automaticPurge: "ENABLED" | "DISABLED";
    referencedProvenance: string;
    unreferencedTrash: string;
    manualPurge: "SERVER_ZERO_DEPENDENCY_ONLY" | "NOT_SUPPORTED_FOR_ENTITY";
    manualPurgeRequiresZeroDependencies: boolean;
  };
  impact: {
    removedFromActiveDiscovery: boolean;
    historicalProvenanceProtected: boolean;
    historicalResearchRemainsAccessible: boolean;
    scientificSnapshotMutated: false;
  };
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
  viewer_scene?: unknown;
  viewer_scene_issue?: string | null;
  canonical_metadata: Record<string, unknown>;
  source_resource_refs: Array<Record<string, unknown>>;
  content_hash: string;
  semantic_hash: string;
  payload_bytes: number | null;
  omitted_item_count: number;
  limitations: string[];
};

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(apiUrl(path), { credentials: "include", signal });
  if (!response.ok) throw new Error(`Scientific viewer request failed (${response.status})`);
  return response.json() as Promise<T>;
}

export const listScientificObjects = (
  projectId: string,
  signal?: AbortSignal,
  lifecycleStatus?: "ACTIVE" | "ARCHIVED" | "TRASHED",
  cursor?: string,
) => request<{ items: ScientificObjectSummary[]; next_cursor: string | null }>(
  `/api/projects/${encodeURIComponent(projectId)}/scientific-objects?limit=100${lifecycleStatus ? `&lifecycle_status=${lifecycleStatus}` : ""}${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ""}`,
  signal,
);

export const getScientificObjectSummary = (objectId: string, signal?: AbortSignal) =>
  request<ScientificObjectSummary>(`/api/scientific-objects/${encodeURIComponent(objectId)}`, signal);

export const getScientificViewerProjection = (objectId: string, versionId: string, signal?: AbortSignal) => request<ScientificViewerProjection>(`/api/scientific-objects/${encodeURIComponent(objectId)}/versions/${encodeURIComponent(versionId)}/viewer`, signal);

export const updateScientificObject = (
  objectId: string,
  changes: { display_name?: string; archived?: boolean; lifecycle?: "ACTIVE" | "ARCHIVED" | "TRASHED" },
  signal?: AbortSignal,
) => fetch(apiUrl(`/api/scientific-objects/${encodeURIComponent(objectId)}`), {
  method: "PATCH",
  credentials: "include",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(changes),
  signal,
}).then(async (response) => {
  if (!response.ok) throw Object.assign(new Error("Scientific object update failed"), { status: response.status });
  const result = await response.json() as ScientificObjectSummary;
  invalidateProjectHistory(result.project_id);
  return result;
});

export const bulkUpdateScientificObjects = (
  projectId: string,
  objectIds: string[],
  lifecycle: "ACTIVE" | "ARCHIVED" | "TRASHED",
  signal?: AbortSignal,
) =>
  fetch(
    apiUrl(`/api/projects/${encodeURIComponent(projectId)}/scientific-objects/bulk`),
    {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ object_ids: objectIds, lifecycle }),
      signal,
    },
  ).then(async (response) => {
    if (!response.ok)
      throw Object.assign(new Error("Scientific object bulk update failed"), { status: response.status });
    const result = await response.json() as {
      project_id: string;
      lifecycle: "ACTIVE" | "ARCHIVED" | "TRASHED";
      count: number;
      items: ScientificObjectSummary[];
    };
    invalidateProjectHistory(projectId);
    return result;
  });

export const getScientificObjectDependencyImpact = (objectId: string, signal?: AbortSignal) =>
  request<ScientificObjectDependencyImpact>(
    `/api/scientific-objects/${encodeURIComponent(objectId)}/dependency-impact`,
    signal,
  );

export type ScientificDatasetQuery = {
  filters?: Array<{ column: string; operator: "eq" | "gt" | "gte" | "lt" | "lte" | "in"; value: unknown }>;
  sort_by?: string;
  descending?: boolean;
  columns?: string[];
  limit?: number;
};

export const queryScientificDataset = (objectId: string, versionId: string, query: ScientificDatasetQuery) =>
  fetch(apiUrl(`/api/scientific-objects/${encodeURIComponent(objectId)}/versions/${encodeURIComponent(versionId)}/query`), {
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
