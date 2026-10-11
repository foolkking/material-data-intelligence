import type { Artifact } from "./planner-api";
import type { PersistedScientificInterpretation } from "./scientific-presentation";
import { readExecutionResponse, validateExecutionIdentity } from "./agent2-execution-api";

const API_BASE = (process.env.NEXT_PUBLIC_MDI_API_BASE_URL || (typeof window === "undefined" ? "http://127.0.0.1:8000" : "/api")).replace(/\/$/, "");

export type Agent2ScientificObjectRef = { object_id: string; version_id: string; project_id: string; object_type: string; display_name?: string; version_no?: number | null };
export type Agent2ScientificSelection = { contract_version: "1.0"; object_ref: Agent2ScientificObjectRef; viewer_id: string; selection_type: string; semantic_locator: Record<string, string | number>; display_label: string; evidence_locator?: Record<string, string | number> | null };
export type Agent2TurnResponse = { turn_id: string; id?: string; research_session_id: string; project_id: string; sequence_no: number; parent_turn_id?: string | null; status: string; user_message: { id: string; role: string; content: string }; message_ids?: string[]; created_at: string; idempotent_replay?: boolean };
export type Agent2TurnListItem = {
  id: string;
  research_session_id: string;
  project_id: string;
  sequence_no: number;
  parent_turn_id?: string | null;
  status: string;
  messages: Array<{
    id: string;
    role: string;
    content: string;
    created_at: string;
  }>;
  created_at: string;
};
type Agent2TurnDetailItem = Agent2TurnListItem & {
  context?: {
    scope?: Agent2ScientificObjectRef[];
    selection?: Agent2ScientificObjectRef[];
    scientific_selection?: Agent2ScientificSelection[];
  } | null;
};
export type Agent2ContextManifestItem = {
  item_id: string;
  kind: string;
  authority_class: string;
  context_role?: "EVIDENCE" | "CONTINUITY" | "SUBJECT" | "CONSTRAINT" | "PREFERENCE";
  support_eligible?: boolean;
  server_side_source_identity: string;
  provider_opaque_ref: string;
  exact_object_id?: string | null;
  exact_object_version_id?: string | null;
  result_ref?: string | null;
  inclusion_reason: string;
  selection_mode: string;
  authorization_checked: boolean;
  content_fingerprint: string;
  representation_type?: string;
  representation_version?: string;
  serialized_representation?: unknown;
  lineage_refs?: string[];
  estimated_tokens: number;
  source_class?: string;
  freshness?: string;
  epistemic_status?: string;
  was_compacted: boolean;
  was_truncated: boolean;
  superseded_state: string;
};
export type Agent2ContextManifest = {
  context_manifest_id: string;
  operation: string;
  project_id: string;
  research_session_id: string;
  research_turn_id: string;
  policy_version: string;
  input_state?: "PROSPECTIVE" | "ACTUAL";
  invocation_role?: string | null;
  prompt_template_version?: string | null;
  serialized_input_version?: string | null;
  serialized_input?: Record<string, unknown> | null;
  serialized_input_fingerprint?: string | null;
  included_items: Agent2ContextManifestItem[];
  excluded_items: string[];
  excluded_item_details?: Array<{
    item_id: string;
    reason: string;
    detail: string;
  }>;
  estimated_input_tokens: number;
  input_budget: number;
  reserved_output_tokens: number;
  repair_margin: number;
  compaction_state: string;
  truncation_state: string;
  context_fingerprint: string;
  created_at: string;
};
export type Agent2ContextManifestRecord = {
  operation: string;
  manifest: Agent2ContextManifest;
  event_id?: string | null;
  sequence_no?: number | null;
};
export type Agent2TurnDetail = Agent2TurnResponse & {
  context?: {
    scope: Agent2ScientificObjectRef[];
    selection: Agent2ScientificObjectRef[];
    scientific_selection: Agent2ScientificSelection[];
  } | null;
};
export type Agent2ScientificFact = {
  fact_id: string;
  predicate: string;
  subject_ref: string;
  value: unknown;
  unit?: string | null;
  source: { tool_call_id?: string | null; artifact_id?: string | null; artifact_locator?: string | null; scientific_object_ref?: Agent2ScientificObjectRef | null };
};
export type Agent2ScientificEvidence = {
  evidence_id: string;
  evidence_type: string;
  artifact_id?: string | null;
  tool_call_id?: string | null;
  artifact_locator?: string | null;
  scientific_object_refs?: Agent2ScientificObjectRef[];
  supports_fact_refs?: string[];
  supports_result_item_refs?: string[];
};
export type Agent2ScientificResultItem = {
  id: string;
  result_type: string;
  role: string;
  title: string;
  artifact_ids: string[];
  scientific_object_refs: Agent2ScientificObjectRef[];
  fact_refs: string[];
  evidence_refs: string[];
  viewer_binding?: string | null;
};
export type Agent2ResearchTurnResult = {
  result_id: string;
  /** Persisted snapshot identity used by context/memory APIs. */
  result_snapshot_id?: string;
  /** Turn addressed by this authorized result view. */
  research_turn_id: string;
  /** Original owner of the immutable scientific result, including reused results. */
  source_research_turn_id?: string;
  research_question: string;
  execution_status: string;
  relevance_status: "CURRENT" | "STALE" | "SOURCE_MISSING" | "INVALIDATED";
  source_object_refs: Agent2ScientificObjectRef[];
  result_items: Agent2ScientificResultItem[];
  input_provenance?: Record<string, unknown> | null;
  facts: Agent2ScientificFact[];
  figures: Array<{ figure_id: string; artifact_ids: string[]; title?: string | null }>;
  tables: Array<{ table_id: string; artifact_ids: string[]; title?: string | null }>;
  evidence: Agent2ScientificEvidence[];
  artifacts: Artifact[];
  /** Exact recorded calls belonging to the result snapshot's execution. */
  tool_call_ids?: string[];
  scientific_selections: Agent2ScientificSelection[];
};
export type Agent2ResearchTurnInterpretation = {
  interpretation_id: string;
  research_turn_id: string;
  status: "VALID" | "REJECTED" | "PENDING" | string;
  title?: string | null;
  message?: string | null;
  execution_status?: string | null;
  interpretation?: PersistedScientificInterpretation | null;
};

function notifySessionExpired(response: Response): void {
  if (response.status === 401 && typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent("mdi:session-expired"));
  }
}

export class Agent2ReadError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(status: number, code?: string) {
    super(`科学呈现暂时无法读取 (${status})`);
    this.name = "Agent2ReadError";
    this.status = status;
    this.code = code;
  }
}

export function createAgent2AdmissionKey(): string {
  if (typeof globalThis.crypto?.randomUUID === "function") {
    return globalThis.crypto.randomUUID();
  }
  return `mdi-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 14)}`;
}

const RESEARCH_TURN_ADMISSION_RETRY_DELAYS_MS = [250, 750] as const;
// Admission only persists/enqueues the Turn; scientific execution is async.
// Match the existing task-feed connection deadline, not a Tool/provider timeout.
const RESEARCH_TURN_ADMISSION_TIMEOUT_MS = 10_000;

export class Agent2AdmissionUnconfirmedError extends Error {
  readonly rejectionStatus?: number;

  constructor(rejectionStatus?: number) {
    const reason = rejectionStatus === 401 ? "登录已过期；" : rejectionStatus === 403 ? "当前账号无法确认该研究；"
      : rejectionStatus === 429 ? "当前请求暂受限制；" : rejectionStatus ? "重试未能确认原请求；" : "研究请求的响应中断，";
    super(`${reason}无法确认本次提交状态。原输入已保留；再次发送相同问题与设置会核对原请求，也可重新打开当前研究查看进度。`);
    this.name = "Agent2AdmissionUnconfirmedError";
    this.rejectionStatus = rejectionStatus;
  }
}

async function readAdmissionResponse(url: string, request: RequestInit) {
  const controller = new AbortController();
  let response: Response | undefined;
  let timeout: ReturnType<typeof globalThis.setTimeout> | undefined;
  try {
    return await Promise.race([
      (async () => {
        response = await fetch(url, { ...request, signal: controller.signal });
        notifySessionExpired(response);
        const body: unknown = await response.json().catch((reason: unknown) => {
          if (response?.ok) throw reason;
          return null;
        });
        return { response, body };
      })(),
      new Promise<never>((_resolve, reject) => {
        timeout = globalThis.setTimeout(() => {
          controller.abort();
          reject(new Error("Admission response deadline exceeded"));
        }, RESEARCH_TURN_ADMISSION_TIMEOUT_MS);
      }),
    ]);
  } catch (reason) {
    // Rejection headers are sufficient to report a definitive client error,
    // even if the optional explanatory body cannot be read before the deadline.
    if (response && !response.ok) return { response, body: null };
    throw reason;
  } finally {
    globalThis.clearTimeout(timeout);
  }
}

async function readAgent2<T>(path: string, options: Readonly<{ signal?: AbortSignal }> = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { credentials: "include", signal: options.signal });
  notifySessionExpired(response);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const code = response.status === 409 && body?.detail?.code === "SCIENTIFIC_RESULT_NOT_READY"
      ? "SCIENTIFIC_RESULT_NOT_READY" : undefined;
    throw new Agent2ReadError(response.status, code);
  }
  return response.json() as Promise<T>;
}

export type Agent2TurnInput = {
  message: string;
  requested_action?: "INTERPRET_RESULT";
  ui_context: { active_object_refs: Agent2ScientificObjectRef[]; selection_refs: Agent2ScientificObjectRef[]; scientific_selections: Agent2ScientificSelection[]; explicit_object_refs: Agent2ScientificObjectRef[]; explicit_result_ids: string[]; explicit_finding_refs: string[] };
  reply_to_turn_id?: string;
  autonomy_mode?: "STANDARD" | "BOUNDED_AUTONOMOUS";
  admission_key?: string;
  model_selection?: { provider: string; model: string; thinking_mode: "quick" | "standard" | "deep" };
};

const admissionRecoveryMemory = new Map<string, Record<string, string>>();
const admissionStorageWriteFailures = new Set<string>();

function admissionFingerprint(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(admissionFingerprint).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.entries(value).filter(([, item]) => item !== undefined).sort(([a], [b]) => a.localeCompare(b)).map(([key, item]) => `${JSON.stringify(key)}:${admissionFingerprint(item)}`).join(",")}}`;
  }
  return JSON.stringify(value) ?? "null";
}

function readPendingAdmissions(storageKey: string): Record<string, string> {
  if (admissionStorageWriteFailures.has(storageKey)) {
    return { ...admissionRecoveryMemory.get(storageKey) };
  }
  try {
    const parsed: unknown = JSON.parse(window.sessionStorage.getItem(storageKey) || "{}");
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return {};
    return Object.fromEntries(Object.entries(parsed).filter(([, key]) => typeof key === "string" && key.trim()));
  } catch {
    return { ...admissionRecoveryMemory.get(storageKey) };
  }
}

function writePendingAdmissions(storageKey: string, pending: Record<string, string>) {
  if (Object.keys(pending).length) admissionRecoveryMemory.set(storageKey, pending);
  else admissionRecoveryMemory.delete(storageKey);
  try {
    if (Object.keys(pending).length) window.sessionStorage.setItem(storageKey, JSON.stringify(pending));
    else window.sessionStorage.removeItem(storageKey);
    admissionStorageWriteFailures.delete(storageKey);
  } catch {
    admissionStorageWriteFailures.add(storageKey);
    // Keep retries safe in this page when session storage is unavailable.
  }
}

export async function createAgent2ResearchTurn(projectId: string, sessionId: string, input: Agent2TurnInput): Promise<Agent2TurnResponse> {
  // Retain unresolved admissions across manual retries and page reloads. The
  // fingerprint includes the exact message, scope, parent and model settings;
  // editing any of them starts a separate request. Only verified acceptance
  // removes an identity so a later intentional repeat can create a new Turn.
  const storageKey = `mdi:research-admissions:${encodeURIComponent(projectId)}:${encodeURIComponent(sessionId)}`;
  const { admission_key: suppliedKey, ...bodyInput } = input;
  // Read models add a human-facing version number. The request contract uses
  // the immutable version ID; never echo display enrichment into strict refs.
  const inputRef = ({ version_no: _displayVersion, ...ref }: Agent2ScientificObjectRef) => ref;
  const context = bodyInput.ui_context;
  const requestBody = { ...bodyInput, ui_context: {
    ...context,
    active_object_refs: context.active_object_refs.map(inputRef),
    selection_refs: context.selection_refs.map(inputRef),
    explicit_object_refs: context.explicit_object_refs.map(inputRef),
    scientific_selections: context.scientific_selections.map(selection => ({ ...selection, object_ref: inputRef(selection.object_ref) })),
  } };
  const fingerprint = admissionFingerprint(requestBody);
  const pending = readPendingAdmissions(storageKey);
  let admissionUncertain = Boolean(pending[fingerprint]);
  const admissionKey = pending[fingerprint] || suppliedKey || createAgent2AdmissionKey();
  pending[fingerprint] = admissionKey;
  writePendingAdmissions(storageKey, pending);
  const forgetAdmission = () => {
    const current = readPendingAdmissions(storageKey);
    if (current[fingerprint] === admissionKey) delete current[fingerprint];
    writePendingAdmissions(storageKey, current);
  };
  const requestInput = {
    ...requestBody,
    admission_key: admissionKey,
  };
  const request = {
    method: "POST",
    credentials: "include" as const,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(requestInput),
  };
  for (let attempt = 0; ; attempt += 1) {
    let response: Response;
    let body: unknown;
    try {
      ({ response, body } = await readAdmissionResponse(
        `${API_BASE}/api/projects/${encodeURIComponent(projectId)}/research/sessions/${encodeURIComponent(sessionId)}/turns`,
        request,
      ));
    } catch {
      admissionUncertain = true;
      if (attempt >= RESEARCH_TURN_ADMISSION_RETRY_DELAYS_MS.length) {
        throw new Agent2AdmissionUnconfirmedError();
      }
      await new Promise((resolve) =>
        globalThis.setTimeout(resolve, RESEARCH_TURN_ADMISSION_RETRY_DELAYS_MS[attempt]),
      );
      continue;
    }
    if (response.ok) {
      try {
        const accepted = body as Agent2TurnResponse | null;
        if (!accepted || typeof accepted.turn_id !== "string" || !accepted.turn_id.trim()) {
          throw new Error("Admission response is missing the durable Turn identity");
        }
        if ((accepted.project_id && accepted.project_id !== projectId) ||
            (accepted.research_session_id && accepted.research_session_id !== sessionId) ||
            (input.reply_to_turn_id && accepted.parent_turn_id && accepted.parent_turn_id !== input.reply_to_turn_id)) {
          throw new Error("Admission response does not match the submitted research scope");
        }
        forgetAdmission();
        return accepted;
      } catch {
        admissionUncertain = true;
        if (attempt >= RESEARCH_TURN_ADMISSION_RETRY_DELAYS_MS.length) {
          throw new Agent2AdmissionUnconfirmedError();
        }
        await new Promise((resolve) =>
          globalThis.setTimeout(resolve, RESEARCH_TURN_ADMISSION_RETRY_DELAYS_MS[attempt]),
        );
        continue;
      }
    }
    if (response.status >= 500) {
      admissionUncertain = true;
      if (attempt >= RESEARCH_TURN_ADMISSION_RETRY_DELAYS_MS.length) {
        throw new Agent2AdmissionUnconfirmedError();
      }
      await new Promise((resolve) =>
        globalThis.setTimeout(resolve, RESEARCH_TURN_ADMISSION_RETRY_DELAYS_MS[attempt]),
      );
      continue;
    }
    // A later denial describes this attempt only. An earlier interrupted
    // attempt may already own a durable Turn, including across login/reload.
    // Keep that identity until acceptance is verified, instead of duplicating
    // scientific work when the user restores access and sends again.
    if (admissionUncertain) throw new Agent2AdmissionUnconfirmedError(response.status);
    // Also retain a first observed denial: transport retries can happen below
    // fetch, and reusing an unaccepted key remains safe after access is restored.
    let detail = `研究请求失败 (${response.status})`;
    const rejection = body as { detail?: string | { summary?: string } | unknown[] } | null;
    if (typeof rejection?.detail === "string") detail = rejection.detail;
    else if (Array.isArray(rejection?.detail)) detail = "研究请求的参数未通过校验。问题已保留，请检查来源和模型设置后重试。";
    else if (rejection?.detail?.summary) detail = rejection.detail.summary;
    throw new Error(detail);
  }
}

export async function listAgent2ResearchTurns(projectId: string, sessionId: string, options: Readonly<{ signal?: AbortSignal }> = {}): Promise<Agent2TurnResponse[]> {
  const path = `/api/projects/${encodeURIComponent(projectId)}/research/sessions/${encodeURIComponent(sessionId)}/turns`;
  const turns: Agent2TurnResponse[] = [];
  let cursor: number | undefined;
  do {
    options.signal?.throwIfAborted();
    const response = await readAgent2<{ items?: Agent2TurnListItem[]; next_cursor?: number | null }>(
      `${path}${cursor === undefined ? "" : `?cursor=${cursor}`}`, options,
    );
    options.signal?.throwIfAborted();
    if (!Array.isArray(response?.items)) throw new Error("Research turn directory unavailable");
    const next = response.next_cursor;
    if (next !== undefined && next !== null && (!Number.isSafeInteger(next) || next <= (cursor ?? 0) ||
        !response.items.length || next !== response.items.at(-1)?.sequence_no)) {
      throw new Error("Research turn directory unavailable");
    }
    turns.push(...response.items.map(normalizeAgent2TurnListItem));
    cursor = next ?? undefined;
  } while (cursor !== undefined);
  // Publish only a complete directory. The caller retains its last successful
  // read if any page fails, and its single deadline covers the entire traversal.
  return turns;
}

export function normalizeAgent2TurnListItem(
  item: Agent2TurnListItem,
): Agent2TurnResponse {
  const userMessage = item.messages.find(
    (message) => message.role.toUpperCase() === "USER",
  );
  if (!userMessage) {
    throw new Error(`ResearchTurn ${item.id} 缺少权威用户消息`);
  }
  return {
    turn_id: item.id,
    id: item.id,
    research_session_id: item.research_session_id,
    project_id: item.project_id,
    sequence_no: item.sequence_no,
    parent_turn_id: item.parent_turn_id || null,
    status: item.status,
    message_ids: item.messages.map((message) => message.id),
    user_message: {
      id: userMessage.id,
      role: "user",
      content: userMessage.content,
    },
    created_at: item.created_at,
  };
}

export function normalizeAgent2TurnDetail(
  item: Agent2TurnDetailItem,
): Agent2TurnDetail {
  const normalized = normalizeAgent2TurnListItem(item);
  return {
    ...normalized,
    context: item.context
      ? {
          scope: item.context.scope || [],
          selection: item.context.selection || [],
          scientific_selection: item.context.scientific_selection || [],
        }
      : null,
  };
}

export async function dispatchAgent2ResearchTurn(turnId: string, options: Readonly<{ signal?: AbortSignal }> = {}): Promise<{ turn_id: string; status: string; queued: boolean }> {
  const value = await readExecutionResponse<{ turn_id: string; status: string; queued: boolean }>(`/api/research/turns/${encodeURIComponent(turnId)}/dispatch`, "dispatch", options.signal);
  validateExecutionIdentity(value, turnId);
  if (typeof value.queued !== "boolean") throw new Error("执行排队结果尚未确认，请重新读取研究状态。");
  return value;
}

export const getAgent2ResearchTurnResult = (turnId: string, options: Readonly<{ signal?: AbortSignal }> = {}) =>
  readAgent2<Agent2ResearchTurnResult>(`/api/research/turns/${encodeURIComponent(turnId)}/result`, options);

export async function getAgent2ResearchTurn(
  turnId: string,
  options: Readonly<{ signal?: AbortSignal }> = {},
): Promise<Agent2TurnDetail> {
  const item = await readAgent2<Agent2TurnDetailItem>(
    `/api/research/turns/${encodeURIComponent(turnId)}`, options,
  );
  return normalizeAgent2TurnDetail(item);
}

export type Agent2ContextResultSource = {
  result_snapshot_id: string;
  project_id: string;
  research_session_id: string;
  research_turn_id: string;
  result_items?: Array<Pick<Agent2ScientificResultItem, "id" | "title" | "result_type" | "scientific_object_refs">>;
};
export type Agent2ContextManifestResponse = { turn_id: string; manifest: Agent2ContextManifest; manifests?: Agent2ContextManifestRecord[]; result_sources?: Agent2ContextResultSource[] };
export const getAgent2ContextManifest = (turnId: string, options: Readonly<{ signal?: AbortSignal }> = {}) =>
  readAgent2<Agent2ContextManifestResponse>(`/api/research/turns/${encodeURIComponent(turnId)}/context-manifest`, options);

export const getAgent2ResearchTurnInterpretation = (turnId: string, options: Readonly<{ signal?: AbortSignal }> = {}) =>
  readAgent2<Agent2ResearchTurnInterpretation>(`/api/research/turns/${encodeURIComponent(turnId)}/interpretation`, options);
