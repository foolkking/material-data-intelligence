"use client";

import { useEffect, useRef, useState } from "react";
import { configurePlannerProvider, getPlannerProviderStatus, listPlannerProviders, listProviderModels, removePlannerProvider, testPlannerProvider, updatePlannerProviderModels, type ProviderOption, type ProviderStatus, type ProviderTestResult } from "../lib/planner-api";

type DialogState = "loading" | "ready" | "error";

export function ModelSettingsDialog({
  open,
  onClose,
  canManage = false,
}: {
  open: boolean;
  onClose: () => void;
  canManage?: boolean;
}) {
  const [status, setStatus] = useState<ProviderStatus | null>(null);
  const [providers, setProviders] = useState<ProviderOption[]>([]);
  const [state, setState] = useState<DialogState>("loading");
  const [error, setError] = useState("");
  const [provider, setProvider] = useState("custom-compatible");
  const [label, setLabel] = useState("兼容模型服务");
  const [baseUrl, setBaseUrl] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [models, setModels] = useState<string[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [modelsState, setModelsState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<ProviderTestResult | null>(null);
  const dialogRef = useRef<HTMLElement | null>(null);
  const closeRef = useRef<HTMLButtonElement | null>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  async function refresh() {
    const [nextStatus, nextProviders] = await Promise.all([getPlannerProviderStatus(), listPlannerProviders()]);
    setStatus(nextStatus);
    const visible = (nextProviders.providers || []).filter((item) => !item.developerOnly);
    setProviders(visible);
    const active = visible.find((item) => item.provider === nextStatus.provider);
    if (active) {
      setProvider(active.provider);
      setLabel(active.label);
      setBaseUrl(active.baseUrl || "");
      setModels(active.models || active.allowedModels || nextStatus.allowedModels || []);
      setSelectedModels(active.models || active.allowedModels || nextStatus.allowedModels || []);
    } else {
      setProvider("custom-compatible");
      setLabel("兼容模型服务");
      setBaseUrl("");
      setModels([]);
      setSelectedModels([]);
    }
  }

  useEffect(() => {
    if (!open) return;
    let active = true;
    setState("loading"); setError(""); setTestResult(null);
    void refresh().then(() => { if (active) setState("ready"); }).catch((reason) => {
      if (!active) return;
      setError(reason instanceof Error ? reason.message : "模型服务暂时无法读取"); setState("error");
    });
    return () => { active = false; };
  }, [open]);

  useEffect(() => {
    if (!open) return;
    previousFocusRef.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const frame = window.requestAnimationFrame(() => closeRef.current?.focus());
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") { event.preventDefault(); onClose(); return; }
      if (event.key !== "Tab" || !dialogRef.current) return;
      const focusable = Array.from(dialogRef.current.querySelectorAll<HTMLElement>('button:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'));
      if (!focusable.length) return;
      const first = focusable[0]; const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => { window.cancelAnimationFrame(frame); document.removeEventListener("keydown", onKeyDown); window.setTimeout(() => previousFocusRef.current?.focus(), 0); };
  }, [open, onClose]);

  async function saveConnection(event: React.FormEvent) {
    event.preventDefault();
    if (!apiKey.trim()) { setError("请输入 API Key。已保存的密钥不会再次显示；替换时需要重新输入。"); return; }
    setSaving(true); setError(""); setTestResult(null);
    try {
      await configurePlannerProvider({ provider, label, kind: "openai_compatible", baseUrl, apiKey });
      setApiKey("");
      await refresh();
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Provider 保存失败"); }
    finally { setSaving(false); }
  }

  async function refreshModels() {
    if (!provider) return;
    setModelsState("loading"); setError("");
    try {
      const result = await listProviderModels(provider);
      setModels(result.models || []); setSelectedModels(result.models || []); setModelsState(result.ok ? "ready" : "error");
      if (!result.ok && result.message) setError(result.message);
    } catch (reason) { setModelsState("error"); setError(reason instanceof Error ? reason.message : "模型目录读取失败"); }
  }

  async function saveModelGroup() {
    if (!savedConnection || !selectedModels.length) return;
    setSaving(true); setError("");
    try {
      await updatePlannerProviderModels(provider, selectedModels, selectedModels[0]);
      setModels(selectedModels);
      await refresh();
    } catch (reason) { setError(reason instanceof Error ? reason.message : "模型组保存失败"); }
    finally { setSaving(false); }
  }

  async function runConnectionTest() {
    if (!provider) return;
    setTesting(true); setTestResult(null);
    try { setTestResult(await testPlannerProvider({ provider, model: models[0] })); }
    catch (reason) { setTestResult({ ok: false, message: reason instanceof Error ? reason.message : "连接测试失败" }); }
    finally { setTesting(false); }
  }

  async function deleteConnection() {
    setSaving(true); setError("");
    try { await removePlannerProvider(provider); setApiKey(""); setModels([]); setBaseUrl(""); await refresh(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "无法删除 Provider 配置"); }
    finally { setSaving(false); }
  }

  if (!open) return null;
  const activeProvider = providers.find((item) => item.provider === status?.provider) || providers.find((item) => item.provider === provider);
  // Keep the server-managed environment connection separate from a user-added
  // connection.  A ready system provider must not look like a deletable form
  // entry, otherwise the dialog implies that the browser owns its credential.
  const savedConnection = providers.find((item) => item.provider === provider && item.secretConfigured);
  const systemReady = Boolean(status?.ok && status.status === "ready" && status.configurationSource === "server_environment");
  const configured = Boolean(savedConnection);

  return <div className="model-settings-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <section ref={dialogRef} className="model-settings-dialog" role="dialog" aria-modal="true" aria-labelledby="model-settings-title" aria-describedby="model-settings-description">
      <header className="model-settings-dialog-header"><div><p className="product-kicker">研究助手</p><h2 id="model-settings-title">模型服务</h2><p id="model-settings-description">{canManage ? "管理平台使用的兼容模型服务。密钥仅在保存时发送给服务端，之后不会再次显示。" : "查看当前研究助手使用的服务状态。平台连接与密钥由管理员统一维护。"}</p></div><button ref={closeRef} type="button" className="product-icon-action" aria-label="关闭模型设置" onClick={onClose}>×</button></header>
      <div className="model-settings-dialog-body">
        {state === "loading" && <div className="model-settings-loading" role="status">正在读取模型服务…</div>}
        {state === "error" && <div className="product-state" role="alert"><h3>模型服务暂时无法读取</h3><p>{error}</p></div>}
        {state === "ready" && <>
          <section className="model-provider-summary"><div className="model-provider-identity"><span className="model-provider-mark" aria-hidden="true">◎</span><div><span>当前服务</span><h3>{activeProvider?.label || status?.provider || "尚未配置"}</h3><p>{configured ? "已保存服务端连接；对话时可以选择模型和思考深度。" : systemReady ? "系统已配置服务端模型；连接密钥由服务端维护。" : "尚未保存可用连接。"}</p></div></div><span className={configured || systemReady ? "model-status ready" : "model-status unavailable"}>{configured ? "已保存" : systemReady ? "系统托管" : "未配置"}</span></section>
          {!canManage ? <section className="model-settings-policy" aria-label="模型服务管理权限"><strong>平台托管配置</strong><p>你可以查看服务状态并验证连接，但不能在浏览器中替换或删除平台模型配置。如需变更，请联系平台管理员。</p></section> : null}
          {canManage ? <form className="provider-connection-form" onSubmit={saveConnection}>
            <div className="provider-form-grid"><label>Provider 标识<input value={provider} onChange={(event) => setProvider(event.target.value.toLowerCase())} placeholder="例如 openai-compatible" autoComplete="off" required /></label><label>显示名称<input value={label} onChange={(event) => setLabel(event.target.value)} placeholder="例如 OpenAI 兼容服务" required /></label></div>
            <label>Base URL<input type="url" value={baseUrl} onChange={(event) => setBaseUrl(event.target.value)} placeholder="https://api.example.com/v1" autoComplete="url" required /></label>
            <label>API Key<input type="password" value={apiKey} onChange={(event) => setApiKey(event.target.value)} placeholder={configured ? "输入新密钥以替换现有配置" : "仅保存时显示"} autoComplete="new-password" required /></label>
            <p className="product-form-hint">支持 OpenAI-compatible 的 <code>/chat/completions</code> 与 <code>/models</code>。保存后密钥立即从输入框清除，界面只保留“已保存”状态；需要修改时重新输入，或删除后重新添加。</p>
            {error && <p className="product-form-error" role="alert">{error}</p>}
            <div className="model-settings-actions"><button type="submit" className="product-primary-action" disabled={saving}>{saving ? "正在保存…" : configured ? "替换并保存密钥" : "保存 Provider"}</button>{configured && <button type="button" className="product-secondary-action" disabled={saving} onClick={() => void deleteConnection()}>删除连接</button>}</div>
          </form> : null}
          <section className="provider-model-directory" aria-labelledby="provider-model-directory-title"><div><p className="product-kicker">模型目录</p><h3 id="provider-model-directory-title">{canManage ? "从 Provider 读取模型" : "可用模型与连接状态"}</h3><p>{canManage ? "先读取 Provider 返回的全部模型，默认全部加入模型组；取消选择后，对话页只显示保留的模型。" : "当前列表来自服务端授权配置。测试连接不会展示或下载平台密钥。"}</p></div><div className="product-row-actions">{canManage ? <button type="button" className="product-secondary-action" onClick={() => void refreshModels()} disabled={!configured || modelsState === "loading"}>{modelsState === "loading" ? "正在读取…" : "刷新模型"}</button> : null}<button type="button" className="product-secondary-action" onClick={() => void runConnectionTest()} disabled={!(configured || systemReady) || testing}>{testing ? "正在测试…" : "测试连接"}</button></div>{models.length ? <>{canManage ? <ul className="provider-model-list">{models.map((model) => <li key={model}><label><input type="checkbox" checked={selectedModels.includes(model)} onChange={(event) => setSelectedModels((current) => event.target.checked ? Array.from(new Set([...current, model])) : current.filter((item) => item !== model))} /> <span>{model}</span></label></li>)}</ul> : <ul className="provider-model-list provider-model-list-readonly">{models.map((model) => <li key={model}><span>{model}</span></li>)}</ul>}{canManage ? <button type="button" className="product-secondary-action" onClick={() => void saveModelGroup()} disabled={!configured || !selectedModels.length || saving}>保存模型组</button> : null}</> : <p className="product-form-hint">{canManage ? <>保存连接后可读取 <code>/models</code>。如果 Provider 不提供目录，需要先配置默认模型，之后可在对话中选择已知模型名。</> : "当前服务未公开可浏览的模型目录；研究对话仍会使用服务端允许的默认模型。"}</p>}{testResult && <p className={testResult.ok ? "model-test-result success" : "model-test-result failure"} role={testResult.ok ? "status" : "alert"}>{testResult.ok ? `连接成功${testResult.latencyMs ? ` · ${testResult.latencyMs} ms` : ""}` : testResult.message || "连接测试失败"}</p>}</section>
          <details className="model-settings-details"><summary>安全与协议说明</summary><p>连接信息由服务端维护。浏览器不保存 API Key，研究问题、Artifact、Report 与导出内容也不包含 Key。当前通用适配器采用 OpenAI-compatible 协议；其他 Provider 协议需显式增加服务端适配器。</p>{savedConnection?.configurationSource === "process_only" && <p className="product-form-hint">当前 API 未设置稳定的加密密钥；本地连接会在 API 进程重启后清除。部署时请设置 <code>MDI_PROVIDER_ENCRYPTION_KEY</code>。</p>}<dl><div><dt>模型目录</dt><dd><code>GET /planner/providers/{"{provider}"}/models</code></dd></div><div><dt>保存连接</dt><dd><code>POST /planner/providers/configure</code></dd></div><div><dt>模型组</dt><dd><code>PATCH /planner/providers/{"{provider}"}/models</code></dd></div><div><dt>移除连接</dt><dd><code>DELETE /planner/providers/{"{provider}"}</code></dd></div></dl></details>
        </>}
      </div>
      <footer className="model-settings-dialog-footer"><span>{canManage ? "具体模型与思考深度在研究对话中选择" : "平台配置只读；研究选择仍受服务端权限与策略约束"}</span><button type="button" className="product-secondary-action" onClick={onClose}>完成</button></footer>
    </section>
  </div>;
}
