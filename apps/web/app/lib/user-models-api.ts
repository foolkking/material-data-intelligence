export type UserModel = { provider: string; model: string; label?: string };
export type ModelProtocol = "openai_chat_json" | "openai_chat" | "openai_responses" | "anthropic";
export type UserModelSettings = {
  label: string; baseUrl: string; secretConfigured: boolean;
  protocol: ModelProtocol;
  catalog: UserModel[]; selected: UserModel[]; revision: number; warnings?: string[];
  connectionId?: string; provider?: string; connections?: UserModelConnection[];
};
export type UserModelConnection = Omit<UserModelSettings, "connections" | "warnings" | "connectionId" | "provider"> & { connectionId: string; provider: string };
export function personalConnections(settings: UserModelSettings): UserModelConnection[] {
  return settings.connections || [{ ...settings, connectionId: "personal", provider: "personal",
    catalog: settings.catalog.filter((item) => item.provider === "personal"),
    selected: settings.selected.filter((item) => item.provider === "personal") }];
}
const API_BASE = (process.env.NEXT_PUBLIC_MDI_API_BASE_URL || "/api").replace(/\/$/, "");
async function request(path: string, init?: RequestInit): Promise<UserModelSettings> {
  const controller = new AbortController();
  const isRead = !init?.method || init.method === "GET";
  const timer = setTimeout(() => controller.abort(), isRead ? 10_000 : 35_000);
  const abort = () => controller.abort();
  init?.signal?.addEventListener("abort", abort, { once: true });
  if (init?.signal?.aborted) controller.abort();
  try {
    const response = await fetch(`${API_BASE}/account/models${path}`, {
      ...init, signal: controller.signal, credentials: "include", headers: { "Content-Type": "application/json" },
    });
    if (response.status === 401) window.dispatchEvent(new CustomEvent("mdi:session-expired"));
    const body = await response.json().catch(() => null);
    if (controller.signal.aborted) throw new Error("Model request aborted");
    if (!response.ok) throw new Error(typeof body?.detail === "string" ? body.detail : isRead ? "模型设置暂时无法读取，请重试。" : "模型设置暂时无法保存，请刷新配置后重试。");
    return body;
  } catch (error) {
    if (controller.signal.aborted) throw new Error(isRead ? "读取模型超时，请重试。" : "连接超时，请重新读取配置确认保存状态后重试。");
    throw error;
  } finally { clearTimeout(timer); init?.signal?.removeEventListener("abort", abort); }
}
export const getUserModels = (options: { signal?: AbortSignal } = {}) => request("", options);
export const saveUserConnection = (input: { label: string; baseUrl: string; apiKey?: string; revision: number; protocol: ModelProtocol; connectionId?: string }) => request("/connection", { method: "PUT", body: JSON.stringify(input) });
export const discoverUserModels = (connectionId?: string) => request("/discover", { method: "POST", ...(connectionId ? { body: JSON.stringify({ connectionId }) } : {}) });
export const saveUserModelSelection = (selected: UserModel[], revision: number, connectionId?: string) => request("/selection", { method: "PUT", body: JSON.stringify({ selected: selected.map(({ provider, model }) => ({ provider, model })), revision, ...(connectionId ? { connectionId } : {}) }) });
export const modelIdentity = (model: UserModel) => JSON.stringify([model.provider, model.model]);
