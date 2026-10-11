"use client";

import { useEffect, useRef, useState } from "react";
import { discoverUserModels, getUserModels, modelIdentity, personalConnections, saveUserConnection, saveUserModelSelection, type UserModelConnection, type UserModelSettings, type ModelProtocol } from "../../app/lib/user-models-api";
import styles from "./ModelSettings.module.css";

type ConnectionDraft = { label: string; baseUrl: string; protocol: ModelProtocol; apiKey: string; selected: string[]; query: string; connectionOpen: boolean; editedConnection: boolean; editedSelection: boolean };

export function ModelSettingsDialog({ open, onClose, fallbackFocus }: {
  open: boolean; onClose: () => void;
  fallbackFocus?: HTMLElement | null;
  /** Compatibility prop: this surface always owns personal settings. */
  canManage?: boolean;
}) {
  const [settings, setSettings] = useState<UserModelSettings | null>(null);
  const [accountSettings, setAccountSettings] = useState<UserModelSettings | null>(null);
  const [newConnection, setNewConnection] = useState<UserModelConnection | null>(null);
  const [connectionId, setConnectionId] = useState("personal");
  const connectionIdRef = useRef("personal");
  const drafts = useRef(new Map<string, ConnectionDraft>());
  const [label, setLabel] = useState("我的模型服务");
  const [baseUrl, setBaseUrl] = useState("");
  const [protocol, setProtocol] = useState<ModelProtocol>("openai_chat_json");
  const [apiKey, setApiKey] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [query, setQuery] = useState("");
  const [connectionOpen, setConnectionOpen] = useState(false);
  const [busy, setBusy] = useState<"load" | "connection" | "discover" | "selection" | null>(null);
  const [error, setError] = useState("");
  const [errorAction, setErrorAction] = useState<"load" | "discover">("load");
  const [notice, setNotice] = useState("");
  const [unconfirmed, setUnconfirmed] = useState<Set<string>>(() => new Set());
  const dialogRef = useRef<HTMLElement>(null);
  const connectionHeadingRef = useRef<HTMLHeadingElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const generation = useRef(0);
  const requestBusy = useRef(false);
  const readController = useRef<AbortController | null>(null);
  const fallbackFocusRef = useRef(fallbackFocus);
  fallbackFocusRef.current = fallbackFocus;
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;
  function scopedSettings(next: UserModelSettings, id: string): UserModelSettings {
    const connection = personalConnections(next).find((item) => item.connectionId === id) || (newConnection?.connectionId === id ? newConnection : null);
    if (!connection) throw new Error("所选连接暂时无法读取，请重新读取配置。");
    return { ...connection, catalog: [...connection.catalog, ...next.catalog.filter((item) => item.provider.startsWith("platform:"))] };
  }
  function accept(next: UserModelSettings, preserveSelection = false) {
    const scoped = scopedSettings(next, connectionIdRef.current);
    setAccountSettings(next);
    setSettings(scoped);
    setSelected((current) => preserveSelection
      ? current.filter((id) => scoped.catalog.some((item) => item.provider === scoped.provider && modelIdentity(item) === id))
      : scoped.selected.filter((item) => item.provider === scoped.provider).map(modelIdentity));
    return scoped;
  }
  function switchConnection(id: string, created?: UserModelConnection) {
    if (!accountSettings || requestBusy.current || id === connectionIdRef.current) return;
    const savedChoices = settings?.selected.map(modelIdentity) || [];
    drafts.current.set(connectionIdRef.current, { label, baseUrl, protocol, apiKey, selected, query, connectionOpen,
      editedConnection: Boolean(settings && (settings.label !== label || settings.baseUrl !== baseUrl || settings.protocol !== protocol || apiKey)),
      editedSelection: selected.length !== savedChoices.length || selected.some((key) => !savedChoices.includes(key)),
    });
    const next = created || scopedSettings(accountSettings, id);
    connectionIdRef.current = id; setConnectionId(id);
    setSettings(next); setError(""); setNotice("");
    const draft = drafts.current.get(id);
    setLabel(draft?.editedConnection ? draft.label : next.label); setBaseUrl(draft?.editedConnection ? draft.baseUrl : next.baseUrl);
    setProtocol(draft?.editedConnection ? draft.protocol : next.protocol); setApiKey(draft?.apiKey ?? "");
    setSelected(draft?.editedSelection ? draft.selected.filter((key) => next.catalog.some((item) => modelIdentity(item) === key)) : next.selected.map(modelIdentity));
    setQuery(draft?.query ?? ""); setConnectionOpen(draft?.connectionOpen ?? !next.secretConfigured);
  }
  function addConnection() {
    if (newConnection) { switchConnection(newConnection.connectionId); return; }
    const id = crypto.randomUUID();
    const next: UserModelConnection = { connectionId: id, provider: `personal:${id}`, label: "新连接", baseUrl: "", protocol: "openai_chat_json", secretConfigured: false, catalog: [], selected: [], revision: 0 };
    setNewConnection(next); switchConnection(id, next);
  }
  async function load(preserveDraft = false) {
    const current = ++generation.current;
    readController.current?.abort();
    const controller = new AbortController();
    readController.current = controller;
    requestBusy.current = true;
    setBusy("load"); setError(""); setNotice(""); setErrorAction("load");
    try {
      const next = await getUserModels({ signal: controller.signal });
      if (current !== generation.current) return;
      const scoped = scopedSettings(next, connectionIdRef.current);
      const removed = preserveDraft ? selected.filter((id) => !scoped.catalog.some((item) => item.provider === scoped.provider && modelIdentity(item) === id)).length : 0;
      accept(next, preserveDraft);
      if (unconfirmed.has(connectionIdRef.current)) requestAnimationFrame(() => {
        if (current === generation.current) connectionHeadingRef.current?.focus();
      });
      setUnconfirmed((pending) => { const updated = new Set(pending); updated.delete(connectionIdRef.current); return updated; });
      if (!preserveDraft) {
        setLabel(scoped.label || "我的模型服务"); setBaseUrl(scoped.baseUrl); setProtocol(scoped.protocol);
        setConnectionOpen(!scoped.secretConfigured && !scoped.catalog.some((item) => item.provider.startsWith("platform:")));
      } else setNotice(removed ? `配置已更新，${removed} 个已选模型已不再可用，其余编辑仍保留。请核对后保存。` : "配置已更新，你正在编辑的内容仍保留。请核对后保存。");
    } catch (reason) { if (current === generation.current) setError(reason instanceof Error ? reason.message : "模型设置读取失败"); }
    finally { if (current === generation.current) { setBusy(null); requestBusy.current = false; } }
  }
  useEffect(() => {
    if (!open) return;
    connectionIdRef.current = "personal"; setConnectionId("personal"); drafts.current.clear();
    setAccountSettings(null); setNewConnection(null);
    setUnconfirmed(new Set());
    setSettings(null); setApiKey(""); setNotice(""); setQuery(""); void load();
    const previousBodyOverflow = document.body.style.overflow;
    const previousRootOverflow = document.documentElement.style.overflow;
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden";
    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const frame = requestAnimationFrame(() => closeRef.current?.focus());
    const keydown = (event: KeyboardEvent) => {
      if (event.key === "Escape") { event.preventDefault(); onCloseRef.current(); }
      if (event.key !== "Tab" || !dialogRef.current) return;
      const elements = Array.from(dialogRef.current.querySelectorAll<HTMLElement>('button:not([disabled]), input:not([disabled]), select:not([disabled]), summary, a[href], [tabindex="0"]')).filter((element) => element.getClientRects().length > 0);
      const first = elements[0], last = elements[elements.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    };
    document.addEventListener("keydown", keydown);
    return () => {
      generation.current++; requestBusy.current = false; readController.current?.abort(); cancelAnimationFrame(frame); document.removeEventListener("keydown", keydown);
      document.body.style.overflow = previousBodyOverflow;
      document.documentElement.style.overflow = previousRootOverflow;
      setApiKey("");
      drafts.current.clear();
      (previous?.isConnected && previous !== document.body ? previous : fallbackFocusRef.current)?.focus();
    };
  }, [open]);
  async function run(kind: "connection" | "discover" | "selection") {
    if (!settings || requestBusy.current || unconfirmed.has(connectionIdRef.current)) return;
    requestBusy.current = true;
    const current = generation.current;
    const targetId = connectionIdRef.current;
    const scope = targetId === "personal" ? undefined : targetId;
    setBusy(kind); setError(""); setNotice(""); setErrorAction(kind === "discover" ? "discover" : "load");
    try {
      const next = kind === "connection"
        ? await saveUserConnection({ label, baseUrl, protocol, apiKey: apiKey || undefined, revision: settings.revision, ...(scope ? { connectionId: scope } : {}) })
        : kind === "discover" ? await discoverUserModels(scope)
          : scope ? await saveUserModelSelection(settings.catalog.filter((item) => item.provider === settings.provider && selected.includes(modelIdentity(item))), settings.revision, scope)
            : await saveUserModelSelection(settings.catalog.filter((item) => item.provider === settings.provider && selected.includes(modelIdentity(item))), settings.revision);
      if (current !== generation.current || targetId !== connectionIdRef.current) return;
      if ((next.connectionId || "personal") !== targetId) throw new Error("返回的连接不匹配，请重新读取配置确认保存状态。");
      const scoped = accept(next, kind !== "selection");
      if (kind === "connection") {
        setApiKey(""); setBaseUrl(scoped.baseUrl); setLabel(scoped.label); setProtocol(scoped.protocol); setConnectionOpen(false); setNotice("连接已保存。现在可以获取模型列表。");
        drafts.current.delete(targetId); if (newConnection?.connectionId === targetId) setNewConnection(null);
      }
      const personalCount = scoped.catalog.filter((item) => item.provider === scoped.provider).length;
      if (kind === "discover") {
        const warnings = (next.warnings || []).join(" ");
        setError(warnings);
        setNotice(warnings
          ? personalCount ? `下方保留上次获取的 ${personalCount} 个模型，本次未能更新。` : ""
          : personalCount ? `已获取 ${personalCount} 个模型，请勾选要使用的模型。` : "未获取到个人模型。请检查连接后重试。");
      }
      const selectedCount = scoped.selected.filter((item) => item.provider === scoped.provider).length;
      if (kind === "selection") setNotice(selectedCount ? `已保存 ${selectedCount} 个模型，可在研究中选择。` : "已清空个人模型选择。");
      window.dispatchEvent(new CustomEvent("mdi:models-changed"));
    } catch (reason) { if (current === generation.current) {
      setError(reason instanceof Error ? reason.message : "操作未完成，请重试。");
      if (kind !== "discover") setUnconfirmed((pending) => new Set(pending).add(targetId));
    } }
    finally { if (current === generation.current) { setBusy(null); requestBusy.current = false; } }
  }
  if (!open) return null;
  const dirtyConnection = Boolean(settings && (settings.baseUrl !== baseUrl || settings.label !== label || settings.protocol !== protocol || apiKey));
  const connections = accountSettings ? personalConnections(accountSettings) : [];
  const connectionChoices = newConnection && !connections.some((item) => item.connectionId === newConnection.connectionId) ? [...connections, newConnection] : connections;
  const personalModels = settings?.catalog.filter((item) => item.provider === settings.provider) || [];
  const platformModels = accountSettings?.catalog.filter((item) => item.provider.startsWith("platform:")) || [];
  const filtered = personalModels.filter((item) => `${item.model} ${item.label || ""}`.toLowerCase().includes(query.toLowerCase()));
  const savedSelected = settings?.selected.filter((item) => item.provider === settings.provider).map(modelIdentity) || [];
  const dirtySelection = selected.length !== savedSelected.length || selected.some((id) => !savedSelected.includes(id));
  const needsConfirmation = unconfirmed.has(connectionId);
  return <div className={styles.backdrop} onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <section ref={dialogRef} className={styles.dialog} role="dialog" aria-modal="true" aria-labelledby="model-settings-title" aria-describedby="model-settings-description">
      <header className={styles.header}><div><h2 id="model-settings-title">模型设置</h2><p id="model-settings-description">选择研究中可用的模型，或连接自己的模型服务。</p></div><button ref={closeRef} type="button" className="product-icon-action" aria-label="关闭模型设置" onClick={onClose}>×</button></header>
      <div className={styles.body} aria-busy={Boolean(busy)}>
        {busy === "load" && <p role="status">正在读取你的模型设置…</p>}
        {(error || needsConfirmation) && <div className={styles.error} role="alert">{error}{needsConfirmation && <p>上次保存状态尚未确认，请重新读取此连接的配置后再保存。当前编辑会保留。</p>}<button type="button" onClick={() => void (errorAction === "discover" && !needsConfirmation ? run("discover") : load(Boolean(settings)))} disabled={Boolean(busy) || (errorAction === "discover" && !needsConfirmation && dirtyConnection)}>{errorAction === "discover" && !needsConfirmation ? "重新获取模型列表" : "重新读取配置"}</button></div>}
        {notice && <p className={styles.notice} role="status">{notice}</p>}
        {settings && <>
          {accountSettings?.connections && <div className={styles.connectionPicker}>
            <label>已保存的连接<select value={connectionId} disabled={Boolean(busy)} onChange={(event) => switchConnection(event.target.value)}>
              {connectionChoices.map((item) => <option key={item.connectionId} value={item.connectionId}>{item.label || "我的模型服务"}{item.revision === 0 ? "（未保存）" : ""}</option>)}
            </select></label>
            <button type="button" className="product-secondary-action" disabled={Boolean(busy) || newConnection?.connectionId === connectionId} onClick={addConnection}>{newConnection ? "继续新增连接" : "新增连接"}</button>
          </div>}
          {platformModels.length > 0 && <section className={styles.platform} aria-labelledby="platform-models-title">
            <div className={styles.sectionHeading}><h3 id="platform-models-title">平台提供</h3><span>可直接使用</span></div>
            <p className={styles.hint}>无需配置，可直接在研究中选择。</p>
            <ul className={styles.models}>{platformModels.map((item) => <li className={styles.platformRow} key={modelIdentity(item)}><span><strong>{item.label || item.model}</strong>{item.label && item.label !== item.model ? <small>{item.model}</small> : null}</span></li>)}</ul>
          </section>}
          <div className={styles.connectionSummary}>
            <div><h3 ref={connectionHeadingRef} tabIndex={-1}>{settings.secretConfigured ? settings.label || "我的模型服务" : "连接自己的模型"}</h3><p>{dirtyConnection ? "连接有未保存的修改" : settings.secretConfigured ? "连接已保存，仅供你的账户使用" : "使用服务商提供的地址和密钥连接"}</p></div>
            <button type="button" className="product-secondary-action" aria-expanded={connectionOpen} aria-controls="model-connection" onClick={() => setConnectionOpen((value) => !value)}>{connectionOpen ? "收起连接" : settings.secretConfigured ? "编辑连接" : "添加连接"}</button>
          </div>
          {connectionOpen && <form id="model-connection" className={styles.connection} onInvalid={(event) => { const details = (event.target as HTMLElement).closest("details"); if (details) details.open = true; }} onSubmit={(event) => { event.preventDefault(); void run("connection"); }}>
            <label>服务名称<input value={label} onChange={(event) => setLabel(event.target.value)} maxLength={120} required disabled={Boolean(busy)} /></label>
            <label>服务地址<input type="url" value={baseUrl} onChange={(event) => setBaseUrl(event.target.value)} placeholder="https://api.example.com/v1" autoComplete="off" spellCheck={false} required disabled={Boolean(busy)} /></label>
            <p className={styles.hint}>填写服务商提供的 API 地址（Base URL）。</p>
            <label>服务密钥（API Key）<input type="password" value={apiKey} onChange={(event) => setApiKey(event.target.value)} placeholder={settings.secretConfigured ? "留空保留已保存的密钥" : "输入服务商提供的密钥"} autoComplete="off" required={!settings.secretConfigured || settings.baseUrl !== baseUrl} disabled={Boolean(busy)} /></label>
            <p className={styles.hint}>{settings.secretConfigured ? "密钥已保存，不会在页面中显示。更换服务地址时需重新填写。" : "密钥仅供你的账户使用，保存后不再显示。"}</p>
            <details className={styles.advanced}><summary>高级设置</summary><div>
              <label>请求协议<select value={protocol} onChange={(event) => setProtocol(event.target.value as ModelProtocol)} disabled={Boolean(busy)}>
                <option value="openai_chat_json">OpenAI Chat Completions · JSON 模式</option>
                <option value="openai_chat">OpenAI Chat Completions · 普通文本</option>
                <option value="openai_responses">OpenAI Responses</option>
                <option value="anthropic">Anthropic Messages</option>
              </select></label>
              <p className={styles.hint}>按服务商文档选择。不支持 JSON 模式时，可改用普通文本模式。</p>
            </div></details>
            <div className={styles.actions}><button type="submit" className="product-secondary-action" disabled={Boolean(busy) || needsConfirmation || !dirtyConnection}>{busy === "connection" ? "正在保存…" : "保存连接"}</button></div>
          </form>}
          <section className={styles.directory} aria-labelledby="model-directory-title">
            <div className={styles.sectionHeading}><h3 id="model-directory-title">选择模型</h3><button type="button" className="product-secondary-action" disabled={Boolean(busy) || needsConfirmation || dirtyConnection || !settings.secretConfigured} onClick={() => void run("discover")}>{busy === "discover" ? "正在获取…" : "获取模型列表"}</button></div>
            <p className={styles.hint}>{dirtyConnection ? "请先保存连接，再获取列表或保存模型选择。" : "勾选常用模型并保存，研究时就能选择它们。"}</p>
            {personalModels.length > 0 ? <>
              <label className={styles.search}>搜索模型<input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="按模型名称搜索" /></label>
              <div className={styles.selectionBar}><span>{query ? `${filtered.length} / ${personalModels.length} 个模型` : `${personalModels.length} 个模型`}</span><button type="button" disabled={Boolean(busy) || !filtered.length} onClick={() => setSelected(Array.from(new Set([...selected, ...filtered.map(modelIdentity)])))}>全选当前结果</button><button type="button" disabled={Boolean(busy) || !selected.length} onClick={() => setSelected([])}>清除全部选择</button></div>
              <ul className={styles.models}>{filtered.map((item) => {
                const id = modelIdentity(item);
                return <li key={id}><label><input type="checkbox" checked={selected.includes(id)} disabled={Boolean(busy)} onChange={(event) => setSelected((current) => event.target.checked ? [...current, id] : current.filter((value) => value !== id))} /><span><strong>{item.model}</strong></span></label></li>;
              })}</ul>
              {!filtered.length && <p className={styles.hint}>没有匹配的模型，试试其他名称。</p>}
            </> : <div className={styles.empty}>保存个人连接后，点击“获取模型列表”选择模型。</div>}
          </section>
        </>}
      </div>
      <footer className={styles.footer}><span>{settings ? `已选 ${selected.length} 个个人模型${dirtySelection ? " · 未保存" : ""}` : ""}</span><div><button type="button" className="product-secondary-action" onClick={onClose}>{dirtySelection || dirtyConnection ? "取消" : "完成"}</button><button type="button" className="product-primary-action" disabled={!settings || Boolean(busy) || needsConfirmation || dirtyConnection || !dirtySelection} onClick={() => void run("selection")}>{busy === "selection" ? "正在保存…" : "保存模型选择"}</button></div></footer>
    </section>
  </div>;
}
