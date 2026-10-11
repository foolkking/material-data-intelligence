import type { ResearchSession } from "./product-api";

type CreationInput = { title: string; datasetId?: string; creationKey: string };
const pending = new Map<string, string>();
const storageWriteFailures = new Set<string>();
const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function save(key: string, value: string | null) {
  if (value) pending.set(key, value);
  else pending.delete(key);
  try {
    if (value) window.sessionStorage.setItem(key, value);
    else window.sessionStorage.removeItem(key);
    storageWriteFailures.delete(key);
  } catch { storageWriteFailures.add(key); }
}

function readKey(key: string) {
  let value = pending.get(key);
  if (!storageWriteFailures.has(key)) {
    try { value = window.sessionStorage.getItem(key) || undefined; } catch { /* Retain this page's identity. */ }
  }
  return value && uuidPattern.test(value) ? value : undefined;
}

function storageKey(projectId: string, datasetId: string | undefined, recoveryScope: string) {
  return `mdi:research-session-creation:${JSON.stringify([projectId, datasetId || null, recoveryScope])}`;
}

export function hasPendingResearchSessionCreation(projectId: string, datasetId: string | undefined, recoveryScope: string) {
  return Boolean(readKey(storageKey(projectId, datasetId, recoveryScope)));
}

function creationKey(key: string) {
  const value = readKey(key) || globalThis.crypto.randomUUID();
  save(key, value);
  return value;
}

/** A receipt is cleared only after the owning composer has adopted the session. */
export function acknowledgeResearchSessionCreation(receipt: string | undefined) {
  if (!receipt) return;
  for (const [key, value] of pending) if (value === receipt) save(key, null);
}

export class ResearchSessionCreationError extends Error {
  constructor(readonly status?: number) {
    const recovery = status === 401 ? "登录已过期，请重新登录后再次发送。"
      : status === 403 ? "当前账号无法创建或确认此对话，请检查访问权限后再次发送。"
      : status === 404 ? "所选项目或数据已不可访问，请检查所选数据后再次发送。"
      : status === 422 ? "创建对话的请求内容未通过校验，请检查所选数据和问题后再次发送。"
      : "暂时无法确认新对话是否已创建，请重新连接后再次发送。";
    super(`${recovery}输入已保留；重试会核对同一次创建请求。`);
    this.name = "ResearchSessionCreationError";
  }
}

export async function recoverResearchSessionCreation(
  projectId: string,
  title: string,
  datasetId: string | undefined,
  recoveryScope: string,
  send: (input: CreationInput, signal: AbortSignal) => Promise<ResearchSession>,
): Promise<ResearchSession> {
  const key = storageKey(projectId, datasetId, recoveryScope);
  const receipt = creationKey(key);
  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout> | undefined;
  try {
    const session = await Promise.race([
      send({ title, ...(datasetId ? { datasetId } : {}), creationKey: receipt }, controller.signal),
      new Promise<never>((_, reject) => {
        timer = setTimeout(() => { controller.abort(); reject(new ResearchSessionCreationError()); }, 10_000);
      }),
    ]);
    if (!session || typeof session.id !== "string" || !session.id.trim() ||
        (session.projectId || session.project_id) !== projectId ||
        (session.projectId && session.project_id && session.projectId !== session.project_id) ||
        session.creationKey !== receipt || typeof session.title !== "string" ||
        !["active", "archived", "trashed"].includes(session.status)) {
      throw new ResearchSessionCreationError();
    }
    return session;
  } catch (reason) {
    if (reason instanceof ResearchSessionCreationError) throw reason;
    throw new ResearchSessionCreationError((reason as { status?: number } | null)?.status);
  } finally {
    clearTimeout(timer);
    controller.abort();
  }
}
