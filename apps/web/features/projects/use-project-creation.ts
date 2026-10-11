"use client";

import { useEffect, useRef, useState } from "react";
import { createProject, listProjects, updateProject, type ProjectSummary } from "../../app/lib/planner-api";
import { getAuthUser } from "../../app/lib/product-api";
import { projectRoleAllows } from "../../app/lib/project-permissions";
import { validateProject, validateProjectDirectory } from "./project-operations";
import { trashRequest } from "./trash-operations";

type Draft = {
  name: string;
  description: string;
  mode: "draft" | "unconfirmed" | "created";
  submittedName: string;
  project: ProjectSummary | null;
  origin: "created" | "matched";
  descriptionSaved: boolean;
  needsRead: boolean;
};
const blank = (): Draft => ({ name: "", description: "", mode: "draft", submittedName: "", project: null, origin: "created", descriptionSaved: false, needsRead: false });
const memory = new Map<string, Draft>();
export const projectCreationDraftKey = (userId: string) => `mdi:project-creation:${encodeURIComponent(userId)}`;
function restore(key: string): Draft {
  try {
    const value = memory.get(key) || JSON.parse(window.sessionStorage.getItem(key) || "null");
    if (!value || typeof value.name !== "string" || value.name.length > 160 || typeof value.description !== "string" || value.description.length > 2000 ||
        !["draft", "unconfirmed", "created"].includes(value.mode) || typeof value.submittedName !== "string" ||
        (value.mode !== "draft" && !value.submittedName.trim())) return blank();
    if (value.project) validateProject(value.project);
    if (value.mode === "created" && !value.project) return blank();
    if (value.mode !== "created" && value.project) return blank();
    return { ...blank(), ...value, needsRead: value.mode !== "draft" };
  } catch { return memory.get(key) ? { ...memory.get(key)!, needsRead: memory.get(key)!.mode !== "draft" } : blank(); }
}
function store(key: string, value: Draft | null) {
  try {
    if (value) window.sessionStorage.setItem(key, JSON.stringify(value)); else window.sessionStorage.removeItem(key);
    memory.delete(key);
  } catch { if (value) memory.set(key, value); else memory.delete(key); }
}

export function useProjectCreation(onProject: (project: ProjectSummary) => void) {
  const [draft, setDraft] = useState<Draft>(blank);
  const current = useRef(draft);
  const storageKey = useRef("");
  const owner = useRef<AbortController | null>(null);
  const [authAttempt, setAuthAttempt] = useState(0);
  const [ready, setReady] = useState(false);
  const [authError, setAuthError] = useState(false);
  const [busy, setBusy] = useState<"creating" | "description" | "checking" | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [matches, setMatches] = useState<ProjectSummary[]>([]);
  const [retryAllowed, setRetryAllowed] = useState(false);
  const publish = (value: Draft) => {
    current.current = value; setDraft(value);
    if (storageKey.current) store(storageKey.current, value);
  };
  useEffect(() => {
    const controller = new AbortController();
    setReady(false); setAuthError(false); storageKey.current = "";
    setMatches([]); setRetryAllowed(false); setError(""); setNotice(""); setBusy(null);
    void trashRequest((signal) => getAuthUser({ signal }), controller.signal).then((user) => {
      if (controller.signal.aborted) return;
      if (!user?.id) throw new Error("Account identity unavailable");
      storageKey.current = projectCreationDraftKey(user.id);
      const restored = restore(storageKey.current); current.current = restored; setDraft(restored); setReady(true);
    }).catch(() => { if (!controller.signal.aborted) setAuthError(true); });
    const expired = () => { controller.abort(); owner.current?.abort(); owner.current = null; storageKey.current = ""; setReady(false); setAuthError(true); current.current = blank(); setDraft(current.current); setMatches([]); setRetryAllowed(false); };
    window.addEventListener("mdi:session-expired", expired);
    return () => { controller.abort(); owner.current?.abort(); owner.current = null; window.removeEventListener("mdi:session-expired", expired); };
  }, [authAttempt]);

  function begin(kind: NonNullable<typeof busy>) {
    if (!ready || owner.current) return null;
    const controller = new AbortController(); owner.current = controller; setBusy(kind); setError(""); setNotice("");
    return controller;
  }
  const owns = (controller: AbortController) => owner.current === controller && !controller.signal.aborted;
  function finish(controller: AbortController) {
    controller.abort();
    if (owner.current === controller) { owner.current = null; setBusy(null); }
  }
  async function writeDescription(controller: AbortController) {
    const source = current.current;
    if (!source.project || !projectRoleAllows(source.project.role, "write")) return;
    const id = source.project.id;
    const description = source.description.trim();
    publish({ ...source, needsRead: true }); setBusy("description");
    const next = validateProject(await trashRequest((signal) => updateProject(id, { description }, signal), controller.signal), id, { description });
    if (!owns(controller)) return;
    publish({ ...current.current, project: next, descriptionSaved: true, needsRead: false }); onProject(next);
  }
  function failWrite(reason: unknown) {
    const status = (reason as { status?: number } | null)?.status;
    const rejected = status !== undefined && [400, 401, 403, 404, 409, 422].includes(status);
    if (current.current.project) {
      publish({ ...current.current, needsRead: !rejected });
      setError(rejected ? "项目已创建，研究说明未保存。请检查内容或权限后重试。" : "项目已创建，研究说明的保存结果尚未确认。请先核对项目。");
    } else if (rejected && status !== 409) {
      publish({ ...current.current, mode: "draft", submittedName: "", needsRead: false });
      setError("项目未创建，请检查名称或权限后重试。");
    } else {
      setRetryAllowed(false);
      setError(status === 409 ? "已有同名项目，请核对项目列表。" : "创建结果尚未确认。草稿已保留，请先核对项目列表。");
    }
  }
  async function submit() {
    const source = current.current;
    if (source.project || !source.name.trim() || (source.mode === "unconfirmed" && !retryAllowed)) return;
    const controller = begin("creating"); if (!controller) return;
    const name = source.mode === "unconfirmed" ? source.submittedName : source.name.trim();
    publish({ ...source, name, submittedName: name, mode: "unconfirmed", needsRead: true }); setRetryAllowed(false); setMatches([]);
    try {
      const project = validateProject(await trashRequest((signal) => createProject(name, signal), controller.signal), undefined, { name });
      if (!owns(controller)) return;
      publish({ ...current.current, project, mode: "created", origin: "created", needsRead: false, descriptionSaved: !source.description.trim() });
      onProject(project);
      if (source.description.trim() && owns(controller)) await writeDescription(controller);
    } catch (reason) { if (owns(controller)) failWrite(reason); }
    finally { finish(controller); }
  }
  async function saveDescription() {
    if (!current.current.project || current.current.needsRead || current.current.descriptionSaved) return;
    const controller = begin("description"); if (!controller) return;
    try { await writeDescription(controller); }
    catch (reason) { if (owns(controller)) failWrite(reason); }
    finally { finish(controller); }
  }
  async function recheck() {
    const controller = begin("checking"); if (!controller) return;
    setRetryAllowed(false); setMatches([]);
    try {
      const items = validateProjectDirectory(await trashRequest((signal) => listProjects({ forceRefresh: true, signal }), controller.signal));
      if (!owns(controller)) return;
      const source = current.current;
      if (source.project) {
        const project = items.find((item) => item.id === source.project!.id);
        if (!project) throw new Error("Created project unavailable");
        publish({ ...source, project, needsRead: false, descriptionSaved: !source.description.trim() || (project.description || "").trim() === source.description.trim() }); onProject(project);
        setNotice("已核对项目，可继续处理。");
      } else {
        const found = items.filter((project) => project.name === source.submittedName);
        setMatches(found); setRetryAllowed(found.length === 0);
        setNotice(found.length ? "找到同名项目，请确认是否继续使用。" : `暂未找到“${source.submittedName}”。可再次核对，或用原名称重试。`);
      }
    } catch { if (owns(controller)) setError("暂时无法核对项目，草稿已保留。请重试。"); }
    finally { finish(controller); }
  }
  function useExisting(id: string) {
    if (owner.current || !ready) return;
    const project = matches.find((item) => item.id === id); if (!project) return;
    publish({ ...current.current, project, mode: "created", origin: "matched", needsRead: false, descriptionSaved: !current.current.description.trim() || (project.description || "").trim() === current.current.description.trim() });
    setMatches([]); setError(""); setNotice(""); onProject(project);
  }
  function dismiss() {
    owner.current?.abort(); owner.current = null; setBusy(null);
    if (current.current.project && current.current.descriptionSaved && !current.current.needsRead && storageKey.current) store(storageKey.current, null);
  }
  return { ...draft, ready, authError, busy, error, notice, matches, retryAllowed, submit, recheck, saveDescription, useExisting, dismiss,
    retryAuth: () => setAuthAttempt((value) => value + 1),
    setName: (name: string) => { if (ready && !owner.current && current.current.mode === "draft") publish({ ...current.current, name }); },
    setDescription: (description: string) => { if (ready && !owner.current) publish({ ...current.current, description, descriptionSaved: false }); },
  };
}
