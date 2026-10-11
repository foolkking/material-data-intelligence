"use client";

import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import { buildResearchHref } from "../../app/lib/research-navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  getWorkspace,
  patchWorkspace,
  type WorkspaceApiError,
  type WorkspacePanel,
  type WorkspaceSelectionContext,
  type WorkspaceSnapshot,
} from "../../app/lib/workspace-api";
import {
  getPlannerInterpretationEvidence,
  getPlannerJobInterpretations,
  type GroundedScientificInterpretation,
  type InterpretationEvidenceResponse,
  type ScientificClaim,
  type ScientificEvidenceItem,
} from "../../app/lib/planner-api";
import {
  WORKSPACE_EXPERIENCE_NAVIGATION_GROUPS,
  compactIdentity,
  firstPanelForKind,
  orderedVisiblePanels,
  panelForRequestedId,
  panelStateCopy,
  panelStateTone,
  workspaceGoalSummary,
  workspaceStatusCopy,
  workspaceStatusTone,
} from "./workspace-shell-model";
import {
  decodeWorkspaceSelectionUrl,
  encodeWorkspaceSelectionUrl,
  WorkspaceSelectionError,
} from "../../shared/workspace/workspace-selection-contract";
import {
  artifactSelectionFromPanel,
  claimSelection,
  evidenceItemSelection,
  evidenceSourceArtifactSelection,
  resolvePanelSelection,
  type WorkspaceSelectionDelivery,
  WorkspaceSelectionStore,
} from "../../shared/workspace/workspace-selection-runtime";
import { WorkspaceArtifactGallery } from "./WorkspaceArtifactGallery";
import { WorkspaceReportComposer } from "./WorkspaceReportComposer";
import {
  durableDraftFromWorkspace,
  workspaceDraftIsDirty,
  workspaceNeedsObservation,
  workspacePatchForDraft,
  type WorkspaceDurableDraft,
} from "./workspace-recovery-model";

type LoadState = "LOADING" | "READY" | "NOT_FOUND" | "ERROR";
type SaveState = "SAVED" | "DIRTY" | "SAVING" | "CONFLICT" | "CAP_EXCEEDED" | "ERROR";

export function ScientificWorkspaceShell({ workspaceId }: { workspaceId: string }) {
  const [snapshot, setSnapshot] = useState<WorkspaceSnapshot | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("LOADING");
  const [loadMessage, setLoadMessage] = useState("Loading Workspace metadata");
  const [activePanelId, setActivePanelId] = useState<string | null>(null);
  const [invalidPanelId, setInvalidPanelId] = useState<string | null>(null);
  const [dataRailOpen, setDataRailOpen] = useState(true);
  const [mobileContextOpen, setMobileContextOpen] = useState(false);
  const [inspectorOpen, setInspectorOpen] = useState(false);
  const [etag, setEtag] = useState<string | null>(null);
  const [selection, setSelection] = useState<WorkspaceSelectionContext | null>(null);
  const [selectionOriginPanelId, setSelectionOriginPanelId] = useState<string | null>(null);
  const [selectionMessage, setSelectionMessage] = useState("No canonical selection is active.");
  const [deliveries, setDeliveries] = useState<Record<string, WorkspaceSelectionDelivery>>({});
  const [pinState, setPinState] = useState<"IDLE" | "SAVING" | "SAVED" | "CONFLICT" | "ERROR">("IDLE");
  const [durableBase, setDurableBase] = useState<WorkspaceDurableDraft | null>(null);
  const [durableDraft, setDurableDraft] = useState<WorkspaceDurableDraft | null>(null);
  const [saveState, setSaveState] = useState<SaveState>("SAVED");
  const [saveMessage, setSaveMessage] = useState("Workspace is saved.");
  const [conflictSnapshot, setConflictSnapshot] = useState<WorkspaceSnapshot | null>(null);
  const [conflictEtag, setConflictEtag] = useState<string | null>(null);
  const [reportDraftDirty, setReportDraftDirty] = useState(false);
  const [recoveryNotice, setRecoveryNotice] = useState<string | null>(null);
  const [recoveryError, setRecoveryError] = useState<string | null>(null);
  const inspectorCloseRef = useRef<HTMLButtonElement | null>(null);
  const inspectorTriggerRef = useRef<HTMLButtonElement | null>(null);
  const contextCloseRef = useRef<HTMLButtonElement | null>(null);
  const contextTriggerRef = useRef<HTMLButtonElement | null>(null);
  const saveAlertRef = useRef<HTMLParagraphElement | null>(null);
  const requestIdRef = useRef(0);
  const selectionStoreRef = useRef<WorkspaceSelectionStore | null>(null);
  const saveControllerRef = useRef<AbortController | null>(null);
  const revalidateControllerRef = useRef<AbortController | null>(null);
  const revalidateNowRef = useRef<() => void>(() => undefined);

  const workspaceDirty = Boolean(durableDraft && durableBase && workspaceDraftIsDirty(durableDraft, durableBase));
  const workspaceTitleValid = Boolean(durableDraft?.title.trim());
  const workspaceDirtyRef = useRef(workspaceDirty);
  workspaceDirtyRef.current = workspaceDirty;

  useEffect(() => {
    if (!workspaceDirty && saveState === "DIRTY") {
      setSaveState("SAVED");
      setSaveMessage("Workspace is saved.");
    }
  }, [saveState, workspaceDirty]);

  const applyUrlState = useCallback((nextSnapshot: WorkspaceSnapshot) => {
    const requested = new URLSearchParams(window.location.search).get("panel");
    const selected = panelForRequestedId(nextSnapshot, requested);
    setInvalidPanelId(requested && !selected ? requested : null);
    setActivePanelId(selected?.panelId || null);
    const token = new URLSearchParams(window.location.search).get("selection");
    if (!token) {
      setSelectionOriginPanelId(null);
      try {
        const pinned = nextSnapshot.workspace.pinnedSelection;
        if (pinned) new WorkspaceSelectionStore(nextSnapshot.workspace, pinned);
        setSelection(pinned);
        setSelectionMessage(pinned ? "Restored the explicitly pinned canonical selection." : "No canonical selection is active.");
      } catch {
        setSelection(null);
        setSelectionMessage("Pinned selection is stale and was not restored.");
      }
      return;
    }
    try {
      const decoded = decodeWorkspaceSelectionUrl(token);
      new WorkspaceSelectionStore(nextSnapshot.workspace, decoded);
      setSelection(decoded);
      setSelectionOriginPanelId(null);
      setSelectionMessage("Restored canonical selection from the exact URL token.");
    } catch (error) {
      const code = error instanceof WorkspaceSelectionError ? error.code : boundedErrorMessage(String(error));
      setSelection(null);
      setSelectionOriginPanelId(null);
      setSelectionMessage(`Selection URL rejected: ${code}`);
    }
  }, []);

  const load = useCallback(() => {
    const controller = new AbortController();
    const requestId = ++requestIdRef.current;
    setLoadState("LOADING");
    setLoadMessage("Loading Workspace metadata");
    void getWorkspace(workspaceId, { signal: controller.signal })
      .then((response) => {
        if (requestId !== requestIdRef.current || !response.data) return;
        setSnapshot(response.data);
        setEtag(response.etag);
        const base = durableDraftFromWorkspace(response.data.workspace);
        setDurableBase(base);
        setDurableDraft(base);
        setSaveState("SAVED");
        setSaveMessage("Workspace is saved.");
        setConflictSnapshot(null);
        setConflictEtag(null);
        applyUrlState(response.data);
        setLoadState("READY");
      })
      .catch((error: WorkspaceApiError | Error) => {
        if (controller.signal.aborted || requestId !== requestIdRef.current) return;
        const status = "status" in error ? error.status : 0;
        setLoadState(status === 404 ? "NOT_FOUND" : "ERROR");
        setLoadMessage(status === 404 ? "Workspace not found" : boundedErrorMessage(error.message));
      });
    return () => controller.abort();
  }, [applyUrlState, workspaceId]);

  useEffect(() => load(), [load]);

  useEffect(() => () => {
    saveControllerRef.current?.abort();
    revalidateControllerRef.current?.abort();
  }, []);

  useEffect(() => {
    const onPopState = () => {
      if (snapshot) applyUrlState(snapshot);
    };
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, [applyUrlState, snapshot]);

  useEffect(() => {
    if (!snapshot || !etag || !workspaceNeedsObservation(snapshot)) return;
    let disposed = false;
    const revalidate = () => {
      if (disposed || document.visibilityState === "hidden") return;
      revalidateControllerRef.current?.abort();
      const controller = new AbortController();
      revalidateControllerRef.current = controller;
      void getWorkspace(workspaceId, { etag, signal: controller.signal }).then((response) => {
        if (disposed || controller.signal.aborted || !response.data) return;
        setRecoveryError(null);
        const next = response.data;
        if (workspaceDirtyRef.current && durableBase && next.workspace.revision !== snapshot.workspace.revision) {
          setConflictSnapshot(next);
          setConflictEtag(response.etag);
          setSaveState("CONFLICT");
          setSaveMessage(`Server revision ${next.workspace.revision} changed while local edits remain based on revision ${snapshot.workspace.revision}.`);
          return;
        }
        const previousArtifacts = snapshot.workspace.artifactCount;
        setSnapshot(next);
        setEtag(response.etag);
        if (!workspaceDirtyRef.current) {
          const base = durableDraftFromWorkspace(next.workspace);
          setDurableBase(base);
          setDurableDraft(base);
        }
        if (!workspaceNeedsObservation(next)) setRecoveryNotice("Job reached a terminal persisted state.");
        else if (next.workspace.artifactCount > previousArtifacts) setRecoveryNotice("A persisted Artifact became available.");
      }).catch((error: WorkspaceApiError | Error) => {
        if (disposed || controller.signal.aborted) return;
        setRecoveryError(`Recovery revalidation failed. ${boundedErrorMessage(error.message)} Previously validated panels remain available.`);
      });
    };
    revalidateNowRef.current = revalidate;
    const timer = window.setInterval(revalidate, 4000);
    const onVisibility = () => { if (document.visibilityState === "visible") revalidate(); };
    document.addEventListener("visibilitychange", onVisibility);
    return () => {
      disposed = true;
      window.clearInterval(timer);
      document.removeEventListener("visibilitychange", onVisibility);
      revalidateControllerRef.current?.abort();
      revalidateNowRef.current = () => undefined;
    };
  }, [durableBase, etag, snapshot, workspaceId]);

  useEffect(() => {
    const warn = (event: BeforeUnloadEvent) => {
      if (!workspaceDirty && !reportDraftDirty) return;
      event.preventDefault();
      event.returnValue = "";
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [reportDraftDirty, workspaceDirty]);

  useEffect(() => {
    if (!snapshot) return;
    const store = new WorkspaceSelectionStore(snapshot.workspace);
    selectionStoreRef.current = store;
    setDeliveries({});
    const unsubscribe = snapshot.panels.map((panel) => store.subscribe(panel, (delivery) => {
      setDeliveries((current) => ({ ...current, [panel.panelId]: delivery }));
    }));
    if (selection) store.set(selection);
    return () => {
      unsubscribe.forEach((dispose) => dispose());
      if (selectionStoreRef.current === store) selectionStoreRef.current = null;
    };
  }, [snapshot]);

  useEffect(() => {
    const store = selectionStoreRef.current;
    if (!store) return;
    try {
      if (selection) store.set(selection);
      else store.clear();
    } catch (error) {
      setSelection(null);
      setSelectionMessage(`Selection rejected: ${boundedErrorMessage(String(error))}`);
    }
  }, [selection]);

  useEffect(() => {
    if (!inspectorOpen) return;
    inspectorCloseRef.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setInspectorOpen(false);
        inspectorTriggerRef.current?.focus();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [inspectorOpen]);

  useEffect(() => {
    if (!mobileContextOpen) return;
    contextCloseRef.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setMobileContextOpen(false);
        contextTriggerRef.current?.focus();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [mobileContextOpen]);

  const visiblePanels = useMemo(() => (snapshot ? orderedVisiblePanels(snapshot) : []), [snapshot]);
  const activePanel = visiblePanels.find((panel) => panel.panelId === activePanelId) || null;

  const selectPanel = useCallback((panel: WorkspacePanel) => {
    if (reportDraftDirty && activePanel?.panelKind === "REPORT" && panel.panelId !== activePanel.panelId
      && !window.confirm("Leave Report and discard the unfinalized session draft?")) return;
    const next = new URL(window.location.href);
    next.searchParams.set("panel", panel.panelId);
    window.history.pushState({ panelId: panel.panelId }, "", next);
    setInvalidPanelId(null);
    setActivePanelId(panel.panelId);
    setDurableDraft((current) => current ? Object.freeze({ ...current, activePanelId: panel.panelId }) : current);
    setSaveState((current) => current === "CAP_EXCEEDED" || current === "CONFLICT" ? current : "DIRTY");
    setSaveMessage("Unsaved Workspace changes.");
    setMobileContextOpen(false);
  }, [activePanel, reportDraftDirty]);

  const saveWorkspace = useCallback(() => {
    if (!snapshot || !etag || !durableBase || !durableDraft || snapshot.workspace.readOnly || saveState === "SAVING") return;
    const patch = workspacePatchForDraft(durableDraft, durableBase);
    if (!patch) {
      setSaveState("SAVED");
      setSaveMessage("No durable changes to save.");
      return;
    }
    saveControllerRef.current?.abort();
    const controller = new AbortController();
    saveControllerRef.current = controller;
    setSaveState("SAVING");
    setSaveMessage("Saving Workspace.");
    void patchWorkspace(snapshot.workspace.workspaceId, etag, patch, controller.signal).then((response) => {
      if (controller.signal.aborted || !response.data) return;
      const base = durableDraftFromWorkspace(response.data.workspace);
      setSnapshot(response.data);
      setEtag(response.etag);
      setDurableBase(base);
      setDurableDraft(base);
      setConflictSnapshot(null);
      setConflictEtag(null);
      setSaveState("SAVED");
      setSaveMessage(`Workspace saved at revision ${response.data.workspace.revision}.`);
    }).catch((error: WorkspaceApiError | Error) => {
      if (controller.signal.aborted) return;
      const code = "detail" in error ? error.detail?.code : null;
      if (("status" in error && error.status === 412) || code === "REVISION_MISMATCH") {
        setSaveState("CONFLICT");
        setSaveMessage(`Revision conflict. Local edits from revision ${snapshot.workspace.revision} are preserved while the current server revision is loaded.`);
        void getWorkspace(snapshot.workspace.workspaceId, { signal: controller.signal }).then((latest) => {
          if (!controller.signal.aborted && latest.data) {
            setConflictSnapshot(latest.data);
            setConflictEtag(latest.etag);
          }
        }).catch(() => undefined);
      } else if (code === "REVISION_CAP_EXCEEDED") {
        setSaveState("CAP_EXCEEDED");
        setSaveMessage("Layout revision cap reached. Unsaved edits are preserved; the Workspace remains readable.");
      } else {
        setSaveState("ERROR");
        setSaveMessage(`Save failed. ${boundedErrorMessage(error.message)} Local edits are preserved.`);
      }
      window.setTimeout(() => saveAlertRef.current?.focus(), 0);
    });
  }, [durableBase, durableDraft, etag, saveState, snapshot]);

  const reloadServerVersion = useCallback(() => {
    if (!conflictSnapshot || !window.confirm("Discard local Workspace edits and reload the current server revision?")) return;
    const base = durableDraftFromWorkspace(conflictSnapshot.workspace);
    setSnapshot(conflictSnapshot);
    setDurableBase(base);
    setDurableDraft(base);
    setEtag(conflictEtag);
    setConflictSnapshot(null);
    setConflictEtag(null);
    setSaveState("SAVED");
    setSaveMessage(`Server revision ${conflictSnapshot.workspace.revision} loaded. Local edits were discarded by explicit confirmation.`);
    applyUrlState(conflictSnapshot);
  }, [applyUrlState, conflictEtag, conflictSnapshot]);

  const activateSelection = useCallback((nextSelection: WorkspaceSelectionContext, originPanelId: string) => {
    try {
      selectionStoreRef.current?.set(nextSelection, originPanelId);
      setSelection(nextSelection);
      setSelectionOriginPanelId(originPanelId);
      setSelectionMessage(`Selected exact ${nextSelection.primary?.kind || "identity"}.`);
      setPinState("IDLE");
      const next = new URL(window.location.href);
      next.searchParams.set("selection", encodeWorkspaceSelectionUrl(nextSelection));
      window.history.pushState({ panelId: activePanelId, selection: true }, "", next);
    } catch (error) {
      setSelectionMessage(`Selection rejected: ${boundedErrorMessage(String(error))}`);
    }
  }, [activePanelId]);

  const navigateArtifactReference = useCallback((nextSelection: WorkspaceSelectionContext, destination: "EVIDENCE" | "PROVENANCE", originPanelId: string) => {
    if (!snapshot) return;
    activateSelection(nextSelection, originPanelId);
    const preferredKinds = destination === "EVIDENCE" ? ["EVIDENCE", "FINDINGS"] : ["PROVENANCE"];
    const target = preferredKinds
      .map((kind) => visiblePanels.find((panel) => panel.panelKind === kind
        && resolvePanelSelection(panel, nextSelection, snapshot.workspace).compatibility === "EXACT"))
      .find((panel): panel is WorkspacePanel => panel !== undefined);
    if (!target) {
      setSelectionMessage(`Exact ${destination.toLowerCase()} reference is unavailable for this Artifact.`);
      return;
    }
    selectPanel(target);
  }, [activateSelection, selectPanel, snapshot, visiblePanels]);

  const clearSelection = useCallback(() => {
    selectionStoreRef.current?.clear(activePanelId);
    setSelection(null);
    setSelectionOriginPanelId(null);
    setSelectionMessage("Canonical selection cleared.");
    setPinState("IDLE");
    const next = new URL(window.location.href);
    next.searchParams.delete("selection");
    window.history.pushState({ panelId: activePanelId }, "", next);
  }, [activePanelId]);

  const pinSelection = useCallback(() => {
    if (!snapshot || !selection || !etag || snapshot.workspace.readOnly) return;
    setPinState("SAVING");
    void patchWorkspace(snapshot.workspace.workspaceId, etag, { pinnedSelection: selection })
      .then((response) => {
        if (!response.data) throw new Error("Workspace PATCH returned no snapshot.");
        setSnapshot(response.data);
        setEtag(response.etag);
        setPinState("SAVED");
      })
      .catch((error: WorkspaceApiError | Error) => {
        setPinState("status" in error && error.status === 412 ? "CONFLICT" : "ERROR");
      });
  }, [etag, selection, snapshot]);

  const copySelectionLink = useCallback(() => {
    if (!selection) return;
    if (!navigator.clipboard) {
      setSelectionMessage("Selection link copy is unavailable.");
      return;
    }
    const next = new URL(window.location.href);
    next.searchParams.set("selection", encodeWorkspaceSelectionUrl(selection));
    void navigator.clipboard.writeText(next.toString()).then(
      () => setSelectionMessage("Canonical selection link copied."),
      () => setSelectionMessage("Selection link copy is unavailable."),
    );
  }, [selection]);

  if (loadState === "LOADING") return <WorkspaceLoadState title="Loading Workspace" message={loadMessage} />;
  if (loadState === "NOT_FOUND") return <WorkspaceLoadState
    title="Workspace not found"
    message="The exact Workspace ID is unavailable. No scientific source or historical result was changed."
    actionHref="/projects"
    actionLabel="查看项目"
    secondaryActionHref="/console"
    secondaryActionLabel="返回控制台"
  />;
  if (loadState === "ERROR" || !snapshot) return <WorkspaceLoadState title="Workspace unavailable" message={loadMessage} actionLabel="Retry" onAction={load} />;

  const workspace = snapshot.workspace;
  const researchHref = buildResearchHref({
    projectId: workspace.projectId,
    jobId: workspace.sourceJobId,
    researchTurnId: snapshot.sourceSummary.researchTurnId,
    researchSessionId: snapshot.sourceSummary.researchSessionId,
  });
  return (
    <main className="scientific-workspace" data-testid="scientific-workspace-shell">
      <a className="skip-link" href="#workspace-primary-content">Skip to active scientific result</a>
      <header className="workspace-header">
        <div className="workspace-header-title">
          <Link className="workspace-back-link" href={researchHref} aria-label="返回项目研究" onClick={(event) => {
            if ((workspaceDirty || reportDraftDirty) && !window.confirm("Leave Workspace and discard unsaved changes?")) event.preventDefault();
          }}>← 返回项目研究</Link>
          <span className="eyebrow">Scientific Workspace 1.0</span>
          <h1>{workspace.title}</h1>
          <p>{workspaceGoalSummary(workspace)} · Job {compactIdentity(workspace.sourceJobId)}</p>
        </div>
        <div className="workspace-header-status" role="status" aria-live="polite">
          <span className={`workspace-status tone-${workspaceStatusTone(workspace.projectedStatus)}`}>{workspace.projectedStatus}</span>
          <span>{workspaceStatusCopy(workspace.projectedStatus)}</span>
          <small>Plan {workspace.planSchemaVersion || "legacy"} · revision {workspace.revision}</small>
        </div>
        <div className="workspace-header-actions">
          <button ref={contextTriggerRef} type="button" className="secondary workspace-mobile-only" onClick={() => setMobileContextOpen(true)} aria-label="Open data context" aria-haspopup="dialog" aria-expanded={mobileContextOpen}>Context</button>
          <button ref={inspectorTriggerRef} type="button" className="secondary" onClick={() => setInspectorOpen(true)} aria-haspopup="dialog" aria-expanded={inspectorOpen}>Inspector</button>
        </div>
      </header>

      <section className="workspace-save-bar" aria-label="Workspace save controls">
        <label htmlFor="workspace-title-input"><span>Workspace title</span><input id="workspace-title-input" value={durableDraft?.title || ""} maxLength={256} disabled={workspace.readOnly || saveState === "SAVING"} onChange={(event) => {
          const title = event.currentTarget.value;
          setDurableDraft((current) => current ? Object.freeze({ ...current, title }) : current);
          setSaveState((current) => current === "CAP_EXCEEDED" || current === "CONFLICT" ? current : "DIRTY");
          setSaveMessage("Unsaved Workspace changes.");
        }} /></label>
        <div className="workspace-save-actions">
          <span className={`workspace-save-state tone-${saveState === "ERROR" || saveState === "CONFLICT" || saveState === "CAP_EXCEEDED" ? "danger" : workspaceDirty ? "warning" : "success"}`}>{workspaceDirty ? "Unsaved changes" : "Saved"}</span>
          <button type="button" onClick={saveWorkspace} disabled={workspace.readOnly || !workspaceDirty || !workspaceTitleValid || saveState === "SAVING" || saveState === "CAP_EXCEEDED"}>{saveState === "SAVING" ? "Saving" : "Save"}</button>
        </div>
        <p ref={saveAlertRef} tabIndex={saveState === "CONFLICT" || saveState === "CAP_EXCEEDED" || saveState === "ERROR" ? -1 : undefined} className="workspace-save-message" role={saveState === "CONFLICT" || saveState === "CAP_EXCEEDED" || saveState === "ERROR" ? "alert" : "status"} aria-live="polite">{saveMessage}</p>
        {!workspaceTitleValid ? <p className="workspace-cap-note" role="alert">Workspace title is required.</p> : null}
        {saveState === "CONFLICT" ? <div className="workspace-conflict-actions"><span>Local base revision {workspace.revision}; server revision {conflictSnapshot?.workspace.revision ?? "loading"}.</span><button type="button" className="secondary" disabled={!conflictSnapshot || !conflictEtag} onClick={reloadServerVersion}>Reload server version</button><button type="button" className="secondary" onClick={saveWorkspace}>Retry save</button></div> : null}
        {saveState === "CAP_EXCEEDED" ? <p className="workspace-cap-note">Revision history remains intact. Results, provenance, and Report history stay read-only and available.</p> : null}
      </section>

      <details className="workspace-guide">
        <summary>Workspace guide</summary>
        <p>Use Data, Plan, Execution, Results, Findings, Evidence, Provenance, and Report to inspect exact persisted analysis records. Pin an exact selection explicitly; use Save for allowed Workspace fields and Finalize for an immutable Report and Recipe.</p>
      </details>

      {recoveryError ? <section className="workspace-recovery-alert" role="alert"><span>{recoveryError}</span><button type="button" className="secondary" onClick={() => revalidateNowRef.current()}>Retry recovery check</button></section> : null}
      {!recoveryError && recoveryNotice ? <p className="workspace-recovery-notice" role="status" aria-live="polite">{recoveryNotice}</p> : null}

      <section className="workspace-selection-banner" role="status" aria-live="polite" data-testid="workspace-selection-status">
        <strong>Canonical selection</strong><span>{selectionMessage}</span>
        {selection?.primary ? <code>{selection.primary.kind}</code> : null}
      </section>

      {workspace.readOnly || !["COMPLETE", "READY"].includes(workspace.projectedStatus) ? (
        <section className="workspace-state-banner" role="status" aria-label="Workspace source state">
          <strong>{workspace.projectedStatus}</strong>
          <span>{workspaceStatusCopy(workspace.projectedStatus)}. Exact historical bindings are preserved.</span>
        </section>
      ) : null}

      {invalidPanelId ? (
        <section className="workspace-inline-error" role="alert" data-testid="workspace-invalid-panel">
          <strong>Unknown panel deep link</strong>
          <span>`{invalidPanelId}` is not a visible panel in this Workspace. No substitute was selected.</span>
        </section>
      ) : null}

      <div className={`workspace-layout ${dataRailOpen ? "" : "data-rail-collapsed"}`}>
        <aside className="workspace-data-rail" aria-label="Data context">
          <div className="workspace-rail-heading">
            <h2>Data context</h2>
            <button type="button" className="workspace-icon-button" aria-label={dataRailOpen ? "Collapse data context" : "Expand data context"} onClick={() => setDataRailOpen((value) => !value)}>{dataRailOpen ? "<" : ">"}</button>
          </div>
          {dataRailOpen ? <WorkspaceDataContext snapshot={snapshot} /> : null}
        </aside>

        <nav className="workspace-navigation" aria-label="Workspace sections">
          <div className="workspace-navigation-heading"><span className="eyebrow">Scientific result</span><h2>Workspace</h2><p>Read results first; inspect exact records when needed.</p></div>
          {WORKSPACE_EXPERIENCE_NAVIGATION_GROUPS.map((group) => <section key={group.id} className={`workspace-navigation-group${group.advanced ? " advanced" : ""}`} aria-label={group.label}>
            {group.items.length > 1 || group.advanced ? <h3>{group.label}</h3> : null}
            <ul>{group.items.map((item) => {
              const panel = firstPanelForKind(snapshot, item.panelKind);
              const current = panel?.panelId === activePanelId;
              return <li key={item.id}><button type="button" className={current ? "active" : ""} disabled={!panel} aria-current={current ? "page" : undefined} onClick={() => panel && selectPanel(panel)}><span>{item.label}</span><small>{panel ? panel.state : "Unavailable"}</small></button></li>;
            })}</ul>
          </section>)}
        </nav>

        <section id="workspace-primary-content" tabIndex={-1} className="workspace-main-panel" aria-labelledby="workspace-active-panel-title">
          {activePanel ? <WorkspacePanelSurface panel={activePanel} workspace={workspace} snapshot={snapshot} delivery={deliveries[activePanel.panelId] || null} onReportDraftDirtyChange={setReportDraftDirty} onActivateSelection={(nextSelection, panelId) => activateSelection(nextSelection, panelId)} onNavigateArtifactReference={(nextSelection, destination, panelId) => navigateArtifactReference(nextSelection, destination, panelId)} onSelectArtifact={(panel) => {
            const nextSelection = artifactSelectionFromPanel(panel, workspace);
            if (nextSelection) activateSelection(nextSelection, panel.panelId);
          }} /> : <WorkspaceEmptyState panelCount={visiblePanels.length} />}
        </section>
      </div>

      {mobileContextOpen ? (
        <div className="workspace-mobile-drawer" role="dialog" aria-modal="true" aria-label="Data context drawer" onKeyDown={trapDialogFocus}>
          <div className="workspace-drawer-header"><h2>Data context</h2><button ref={contextCloseRef} type="button" className="workspace-icon-button" aria-label="Close data context" onClick={() => { setMobileContextOpen(false); contextTriggerRef.current?.focus(); }}>X</button></div>
          <WorkspaceDataContext snapshot={snapshot} />
          <div className="workspace-mobile-panel-switcher"><h3>Panels</h3>{visiblePanels.map((panel) => <button key={panel.panelId} type="button" className="secondary" onClick={() => selectPanel(panel)}>{panel.title}</button>)}</div>
        </div>
      ) : null}

      {inspectorOpen ? (
        <div className="workspace-inspector-backdrop" onMouseDown={(event) => event.currentTarget === event.target && setInspectorOpen(false)}>
          <aside className="workspace-inspector" role="dialog" aria-modal="true" aria-labelledby="workspace-inspector-title" onKeyDown={trapDialogFocus}>
            <div className="workspace-drawer-header"><h2 id="workspace-inspector-title">Context inspector</h2><button ref={inspectorCloseRef} type="button" className="workspace-icon-button" aria-label="Close inspector" onClick={() => { setInspectorOpen(false); inspectorTriggerRef.current?.focus(); }}>X</button></div>
            <p className="subtle">Meaning first, with exact scientific identity and source records available below.</p>
            <WorkspaceSelectionInspector selection={selection} originPanelId={selectionOriginPanelId} deliveries={deliveries} panels={visiblePanels} activePanel={activePanel} pinState={pinState} readOnly={workspace.readOnly} onClear={clearSelection} onCopy={copySelectionLink} onPin={pinSelection} onSelectPanel={selectPanel} />
          </aside>
        </div>
      ) : null}
    </main>
  );
}

function WorkspacePanelSurface({ panel, workspace, snapshot, delivery, onReportDraftDirtyChange, onActivateSelection, onNavigateArtifactReference, onSelectArtifact }: { panel: WorkspacePanel; workspace: WorkspaceSnapshot["workspace"]; snapshot: WorkspaceSnapshot; delivery: WorkspaceSelectionDelivery | null; onReportDraftDirtyChange: (dirty: boolean) => void; onActivateSelection: (selection: WorkspaceSelectionContext, panelId: string) => void; onNavigateArtifactReference: (selection: WorkspaceSelectionContext, destination: "EVIDENCE" | "PROVENANCE", panelId: string) => void; onSelectArtifact: (panel: WorkspacePanel) => void }) {
  const selectableArtifact = artifactSelectionFromPanel(panel, workspace);
  return (
    <article className="workspace-panel-surface" data-testid={`workspace-panel-${panel.panelKind.toLowerCase()}`}>
      <header className="workspace-panel-header">
        <div><span className="eyebrow">{panel.panelKind.replaceAll("_", " ")}</span><h2 id="workspace-active-panel-title">{panel.title}</h2></div>
        <span className={`workspace-status tone-${panelStateTone(panel.state)}`}>{panel.state}</span>
      </header>
      <p className="workspace-panel-state-copy">{panelStateCopy(panel.state)}</p>
      {panel.panelKind === "SCIENTIFIC_RESULT" ? <WorkspaceResultSummary panel={panel} workspace={workspace} delivery={delivery} /> : null}
      {panel.state === "PARTIAL" || panel.state === "BLOCKED_BY_DEPENDENCY" ? <div className="workspace-panel-warning" role="status">This panel reflects only successful source branches. Failed or blocked outputs are not presented as complete.</div> : null}
      {panel.unsupportedReason ? <div className="workspace-panel-warning" role="alert"><strong>Unsupported source contract</strong><span>{panel.unsupportedReason}</span></div> : null}
      {panel.panelKind === "OVERVIEW" ? <WorkspaceOverview snapshot={snapshot} /> : null}
      {panel.panelKind === "PLAN" ? <WorkspacePlanSummary snapshot={snapshot} /> : null}
      {panel.panelKind === "EXECUTION" ? <WorkspaceExecutionSummary snapshot={snapshot} /> : null}
      {["FINDINGS", "EVIDENCE", "PROVENANCE"].includes(panel.panelKind) ? <WorkspaceReferenceSummary panel={panel} workspace={workspace} snapshot={snapshot} delivery={delivery} onSelection={(selection) => onActivateSelection(selection, panel.panelId)} /> : null}
      {panel.panelKind === "REPORT" ? <WorkspaceReportComposer workspace={workspace} onDraftDirtyChange={onReportDraftDirtyChange} /> : null}
      {panel.panelKind === "SCIENTIFIC_RESULT" ? <WorkspaceArtifactGallery workspace={workspace} panel={panel} delivery={delivery} onSelection={(selection) => onActivateSelection(selection, panel.panelId)} onNavigateReference={(selection, destination) => onNavigateArtifactReference(selection, destination, panel.panelId)} /> : null}
      {selectableArtifact ? <button type="button" className="secondary workspace-selection-command" onClick={() => onSelectArtifact(panel)} data-testid={`workspace-select-artifact-${panel.panelId}`}>Select exact artifact</button> : null}
      <details className="workspace-scientific-details"><summary>Scientific details</summary><dl className="workspace-metadata-grid">
        <Metadata label="Renderer contract" value={panel.rendererContract} />
        <Metadata label="Panel ID" value={compactIdentity(panel.panelId, 32)} />
        <Metadata label="Source references" value={String(panel.sourceRefs.length)} />
        <Metadata label="Evidence links" value={String(panel.evidenceRefs.length)} />
        <Metadata label="Provenance links" value={String(panel.provenanceRefs.length)} />
        <Metadata label="Plan schema" value={workspace.planSchemaVersion || "Legacy"} />
      </dl><div className={`workspace-selection-delivery tone-${delivery?.compatibility === "EXACT" ? "success" : "muted"}`} role="status" aria-label="Panel selection compatibility"><strong>Selection compatibility</strong><span>{delivery ? `${delivery.compatibility}: ${delivery.reason}` : "NOT_APPLICABLE: no selection runtime delivery yet."}</span></div></details>
      <details className="workspace-audit-json"><summary>Developer details</summary><pre>{JSON.stringify({ panel, sourceSummary: snapshot.sourceSummary }, null, 2)}</pre></details>
    </article>
  );
}

function WorkspaceResultSummary({ panel, workspace, delivery }: { panel: WorkspacePanel; workspace: WorkspaceSnapshot["workspace"]; delivery: WorkspaceSelectionDelivery | null }) {
  return <section className="workspace-result-summary" aria-label="Scientific result summary">
    <div><span className="eyebrow">Scientific result</span><h3>Persisted result ready for inspection</h3><p>Choose a result to load its validated payload. Artifact identity, provenance and selection remain exact.</p></div>
    <dl><Metadata label="Artifacts" value={String(workspace.artifactCount)} /><Metadata label="Source records" value={String(panel.sourceRefs.length)} /><Metadata label="Selection" value={delivery?.compatibility === "EXACT" ? "Exact compatible" : "Available when applicable"} /></dl>
  </section>;
}

function WorkspaceOverview({ snapshot }: { snapshot: WorkspaceSnapshot }) {
  return <section className="workspace-summary-band" aria-label="Workspace overview"><h3>Source overview</h3><dl className="workspace-metadata-grid"><Metadata label="Job status" value={snapshot.sourceSummary.jobStatus || "Unknown"} /><Metadata label="Tool calls" value={String(snapshot.sourceSummary.toolCallCount)} /><Metadata label="Artifacts" value={String(snapshot.sourceSummary.artifactCount)} /><Metadata label="Interpretations" value={String(snapshot.sourceSummary.interpretationCount)} /></dl></section>;
}

function WorkspacePlanSummary({ snapshot }: { snapshot: WorkspaceSnapshot }) {
  return <section className="workspace-summary-band"><h3>Persisted plan</h3><p>Schema {snapshot.sourceSummary.analysisPlanSchemaVersion || "legacy"}; plan identity {compactIdentity(snapshot.workspace.planId)}.</p><p className="subtle">Step dependencies remain owned by the persisted plan and execution records.</p></section>;
}

function WorkspaceExecutionSummary({ snapshot }: { snapshot: WorkspaceSnapshot }) {
  return <section className="workspace-summary-band"><h3>Execution projection</h3><dl className="workspace-metadata-grid"><Metadata label="Job" value={snapshot.sourceSummary.jobStatus || "Unknown"} /><Metadata label="Dependency outcome" value={snapshot.sourceSummary.dependencyOutcome || "Independent or unavailable"} /><Metadata label="Tool calls" value={String(snapshot.sourceSummary.toolCallCount)} /><Metadata label="Artifacts retained" value={String(snapshot.sourceSummary.artifactCount)} /></dl></section>;
}

function WorkspaceReferenceSummary({ panel, workspace, snapshot, delivery, onSelection }: { panel: WorkspacePanel; workspace: WorkspaceSnapshot["workspace"]; snapshot: WorkspaceSnapshot; delivery: WorkspaceSelectionDelivery | null; onSelection: (selection: WorkspaceSelectionContext) => void }) {
  const labels: Record<string, string> = { FINDINGS: "Grounded interpretation", EVIDENCE: "Scientific evidence", PROVENANCE: "Source lineage" };
  const [interpretation, setInterpretation] = useState<GroundedScientificInterpretation | null>(null);
  const [evidence, setEvidence] = useState<InterpretationEvidenceResponse | null>(null);
  const [loadState, setLoadState] = useState<"IDLE" | "LOADING" | "READY" | "EMPTY" | "FAILED">("IDLE");
  const [evidencePage, setEvidencePage] = useState(0);
  const readsInterpretation = panel.panelKind === "FINDINGS" || panel.panelKind === "EVIDENCE" || panel.panelKind === "PROVENANCE";

  useEffect(() => {
    if (!readsInterpretation) return;
    const controller = new AbortController();
    setLoadState("LOADING");
    setEvidencePage(0);
    void getPlannerJobInterpretations(workspace.sourceJobId, { signal: controller.signal }).then(async (records) => {
      const latest = records.interpretations.at(-1) ?? null;
      if (!latest) {
        setLoadState("EMPTY");
        return;
      }
      const projectedEvidence = await getPlannerInterpretationEvidence(latest.interpretationId, { signal: controller.signal });
      if (controller.signal.aborted) return;
      if (latest.sourceJobId !== workspace.sourceJobId || projectedEvidence.interpretationId !== latest.interpretationId || projectedEvidence.bundleId !== latest.sourceBundleId || projectedEvidence.bundleHash !== latest.sourceBundleHash) {
        throw new Error("WORKSPACE_INTERPRETATION_SCOPE_MISMATCH");
      }
      setInterpretation(latest);
      setEvidence(projectedEvidence);
      setLoadState("READY");
    }).catch(() => {
      if (!controller.signal.aborted) setLoadState("FAILED");
    });
    return () => controller.abort();
  }, [panel.panelId, readsInterpretation, workspace.sourceJobId]);

  const pageSize = 32;
  const evidenceItems = evidence?.evidenceItems ?? [];
  const pageCount = Math.max(1, Math.ceil(evidenceItems.length / pageSize));
  const visibleEvidence = evidenceItems.slice(evidencePage * pageSize, (evidencePage + 1) * pageSize);
  const selected = delivery?.context?.primary;
  const selectedClaim = selected?.kind === "CLAIM" ? interpretation?.claims.find((claim) => claim.claimId === selected.claimId) : null;
  const selectedEvidence = selected?.kind === "EVIDENCE_ITEM" ? evidenceItems.find((item) => item.evidenceItemId === selected.evidenceItemId) : null;
  return <section className="workspace-summary-band workspace-trust-path"><h3>{labels[panel.panelKind]}</h3><p>Follow persisted claims to exact evidence, source Artifacts, Tool versions, inputs and lineage. Presentation does not generate or rank scientific conclusions.</p><dl className="workspace-metadata-grid"><Metadata label="Interpretations" value={String(snapshot.sourceSummary.interpretationCount)} /><Metadata label="Reports" value={String(snapshot.sourceSummary.reportCount)} /><Metadata label="Recipes" value={String(snapshot.sourceSummary.recipeCount)} /><Metadata label="Metadata only" value="Yes" /></dl>
    {readsInterpretation && loadState === "LOADING" ? <p role="status">Loading persisted grounded references.</p> : null}
    {readsInterpretation && loadState === "EMPTY" ? <p role="status">No persisted grounded interpretation is available.</p> : null}
    {readsInterpretation && loadState === "FAILED" ? <p role="alert">Grounded references are unavailable or failed exact source validation.</p> : null}
    {interpretation ? <InterpretationDisclosure interpretation={interpretation} evidence={evidence} /> : null}
    {panel.panelKind === "FINDINGS" && interpretation && evidence ? <FindingTrustPath interpretation={interpretation} evidence={evidence} workspace={workspace} selected={selected} onSelection={onSelection} /> : null}
    {panel.panelKind === "EVIDENCE" && interpretation && evidence ? <div className="workspace-grounded-reference-list" data-testid="workspace-grounded-evidence"><div className="workspace-reference-pagination"><h4>Evidence</h4><span>Showing {evidenceItems.length ? evidencePage * pageSize + 1 : 0}-{Math.min((evidencePage + 1) * pageSize, evidenceItems.length)} of {evidenceItems.length}</span></div>{visibleEvidence.map((item) => <EvidenceCard key={item.evidenceItemId} item={item} roles={evidenceRoles(interpretation.claims, item.evidenceItemId)} selected={selected?.kind === "EVIDENCE_ITEM" && selected.evidenceItemId === item.evidenceItemId} onSelect={() => onSelection(evidenceItemSelection(workspace, interpretation, evidence, item))} onSource={() => onSelection(evidenceSourceArtifactSelection(workspace, interpretation, evidence, item))} />)}{pageCount > 1 ? <div className="workspace-selection-actions"><button type="button" className="secondary" disabled={evidencePage === 0} onClick={() => setEvidencePage((value) => value - 1)}>Previous evidence</button><button type="button" className="secondary" disabled={evidencePage + 1 >= pageCount} onClick={() => setEvidencePage((value) => value + 1)}>Next evidence</button></div> : null}</div> : null}
    {panel.panelKind === "PROVENANCE" && interpretation && evidence ? <ProvenanceTrustPath workspace={workspace} panel={panel} interpretation={interpretation} evidence={evidence} selected={selected} selectedClaim={selectedClaim || null} selectedEvidence={selectedEvidence || null} /> : null}
  </section>;
}

const CLAIM_LABELS: Record<ScientificClaim["claimType"], string> = {
  OBSERVATION: "Observation", COMPARISON: "Comparison", ANOMALY: "Anomaly", WARNING: "Warning",
  LIMITATION: "Scientific limitation", RECOMMENDATION: "Recommendation", NO_SUPPORTED_CONCLUSION: "No supported conclusion",
};

const QUALIFICATION_COPY: Record<ScientificClaim["confidenceClass"], string> = {
  DIRECT: "Directly supported by the persisted evidence listed below.",
  QUALIFIED: "Supported with stated qualifications; inspect limiting evidence before reuse.",
  LIMITED: "Limited conclusion. The persisted limitations materially bound this statement.",
};

function InterpretationDisclosure({ interpretation, evidence }: { interpretation: GroundedScientificInterpretation; evidence: InterpretationEvidenceResponse | null }) {
  const warnings = [...interpretation.globalWarnings, ...(evidence?.bundleWarnings ?? [])];
  const limitations = [...interpretation.globalLimitations, ...(evidence?.bundleLimitations ?? [])];
  return <div className="workspace-interpretation-disclosure" aria-label="Interpretation scope">
    <span className={`workspace-status tone-${interpretation.completeness === "COMPLETE" ? "success" : interpretation.completeness === "PARTIAL" ? "warning" : "muted"}`}>{interpretation.completeness}</span>
    <p>{interpretation.completeness === "COMPLETE" ? "Persisted grounded interpretation is complete for its supported evidence scope." : interpretation.completeness === "PARTIAL" ? "Only the successful persisted evidence scope supports these claims." : "No supported scientific conclusion is available from this evidence scope."}</p>
    {warnings.length ? <div className="workspace-trust-warning" role="status"><strong>Warnings</strong><ul>{warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul></div> : null}
    {limitations.length ? <div className="workspace-trust-limitation" role="note"><strong>Scientific limitations</strong><ul>{limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul></div> : null}
  </div>;
}

function FindingTrustPath({ interpretation, evidence, workspace, selected, onSelection }: { interpretation: GroundedScientificInterpretation; evidence: InterpretationEvidenceResponse; workspace: WorkspaceSnapshot["workspace"]; selected: WorkspaceSelectionContext["primary"] | undefined; onSelection: (selection: WorkspaceSelectionContext) => void }) {
  const evidenceById = new Map(evidence.evidenceItems.map((item) => [item.evidenceItemId, item]));
  const orderedClaims = [...interpretation.claims].sort((left, right) => left.displayOrder - right.displayOrder || left.claimId.localeCompare(right.claimId));
  return <div className="workspace-grounded-reference-list" data-testid="workspace-grounded-claims"><div className="workspace-reference-pagination"><h4>Findings</h4><span>{orderedClaims.length} persisted claim(s)</span></div>
    {orderedClaims.length === 0 ? <p role="status">No supported scientific conclusion was generated from the available persisted evidence.</p> : orderedClaims.map((claim) => <article className={`workspace-finding-card finding-${claim.claimType.toLowerCase()}`} key={claim.claimId}>
      <header><div><span className="workspace-finding-type">{CLAIM_LABELS[claim.claimType]}</span><h5>{claim.renderedText}</h5></div><span className={`workspace-status tone-${claim.confidenceClass === "DIRECT" ? "success" : claim.confidenceClass === "QUALIFIED" ? "warning" : "danger"}`}>{claim.confidenceClass}</span></header>
      <p>{QUALIFICATION_COPY[claim.confidenceClass]}</p>
      {claim.qualifiers.length ? <ul className="workspace-qualifier-list">{claim.qualifiers.map((qualifier) => <li key={qualifier}>{qualifier}</li>)}</ul> : null}
      <FindingEvidenceGroup role="Supporting" ids={claim.supportingEvidenceIds} evidenceById={evidenceById} onSelect={(item) => onSelection(evidenceItemSelection(workspace, interpretation, evidence, item))} />
      <FindingEvidenceGroup role="Limiting" ids={claim.limitingEvidenceIds} evidenceById={evidenceById} onSelect={(item) => onSelection(evidenceItemSelection(workspace, interpretation, evidence, item))} />
      <FindingEvidenceGroup role="Contradicting" ids={claim.contradictingEvidenceIds} evidenceById={evidenceById} onSelect={(item) => onSelection(evidenceItemSelection(workspace, interpretation, evidence, item))} />
      <button type="button" className="secondary" aria-pressed={selected?.kind === "CLAIM" && selected.claimId === claim.claimId} onClick={() => onSelection(claimSelection(workspace, interpretation, claim))}>Inspect exact claim</button>
    </article>)}
    {interpretation.recommendations.length ? <section className="workspace-recommendation-list" aria-label="Non-executable recommendations"><h4>Recommendations</h4>{interpretation.recommendations.map((recommendation) => <article key={recommendation.recommendationId}><strong>{recommendation.suggestedGoalCategory}</strong><p>{recommendation.limitation}</p><small>Advisory only. No plan, job, queue or execution is authorized.</small></article>)}</section> : null}
  </div>;
}

function FindingEvidenceGroup({ role, ids, evidenceById, onSelect }: { role: "Supporting" | "Limiting" | "Contradicting"; ids: string[]; evidenceById: Map<string, ScientificEvidenceItem>; onSelect: (item: ScientificEvidenceItem) => void }) {
  if (!ids.length) return null;
  return <section className={`workspace-finding-evidence role-${role.toLowerCase()}`} aria-label={`${role} evidence`}><strong>{role} evidence</strong><ul>{ids.map((id) => {
    const item = evidenceById.get(id);
    return <li key={id}>{item ? <button type="button" className="quiet" onClick={() => onSelect(item)}><span>{item.semanticRole}</span><small>{item.displayValue}{item.unit ? ` ${item.unit}` : ""}</small></button> : <span role="alert">Exact evidence {compactIdentity(id)} is unavailable.</span>}</li>;
  })}</ul></section>;
}

function evidenceRoles(claims: ScientificClaim[], evidenceItemId: string): Array<"SUPPORTING" | "LIMITING" | "CONTRADICTING"> {
  const roles = new Set<"SUPPORTING" | "LIMITING" | "CONTRADICTING">();
  for (const claim of claims) {
    if (claim.supportingEvidenceIds.includes(evidenceItemId)) roles.add("SUPPORTING");
    if (claim.limitingEvidenceIds.includes(evidenceItemId)) roles.add("LIMITING");
    if (claim.contradictingEvidenceIds.includes(evidenceItemId)) roles.add("CONTRADICTING");
  }
  return [...roles];
}

function EvidenceCard({ item, roles, selected, onSelect, onSource }: { item: ScientificEvidenceItem; roles: string[]; selected: boolean; onSelect: () => void; onSource: () => void }) {
  return <article className="workspace-evidence-card"><header><div><span className="workspace-evidence-kind">{item.evidenceKind}</span><h5>{item.semanticRole}</h5></div><div className="workspace-evidence-roles">{roles.length ? roles.map((role) => <span key={role}>{role}</span>) : <span>SUBJECT</span>}</div></header>
    <p className="workspace-evidence-value">{item.displayValue}{item.unit ? ` ${item.unit}` : ""}</p>
    {item.warnings.length ? <div className="workspace-trust-warning"><strong>Warning</strong><span>{item.warnings.join("; ")}</span></div> : null}
    {item.limitations.length ? <div className="workspace-trust-limitation"><strong>Limitation</strong><span>{item.limitations.join("; ")}</span></div> : null}
    <p className="subtle">Persisted in {item.artifactContract}@{item.artifactContractVersion}; produced by {item.sourceToolId}@{item.sourceToolVersion}.</p>
    <div className="workspace-selection-actions"><button type="button" className="secondary" aria-pressed={selected} onClick={onSelect}>Inspect exact evidence</button><button type="button" className="secondary" onClick={onSource}>Select source Artifact</button></div>
    <details><summary>Scientific details</summary><dl className="workspace-metadata-grid"><Metadata label="Evidence ID" value={item.evidenceItemId} /><Metadata label="Artifact" value={item.sourceArtifactId} /><Metadata label="Checksum" value={compactIdentity(item.sourceArtifactChecksum, 32)} /><Metadata label="Field" value={item.fieldLocator.fieldId} /></dl></details>
  </article>;
}

function ProvenanceTrustPath({ workspace, panel, interpretation, evidence, selected, selectedClaim, selectedEvidence }: { workspace: WorkspaceSnapshot["workspace"]; panel: WorkspacePanel; interpretation: GroundedScientificInterpretation; evidence: InterpretationEvidenceResponse; selected: WorkspaceSelectionContext["primary"] | undefined; selectedClaim: ScientificClaim | null; selectedEvidence: ScientificEvidenceItem | null }) {
  const artifactId = selectedEvidence?.sourceArtifactId || (selected?.kind === "ARTIFACT" ? selected.artifactId : null);
  const checksum = selectedEvidence?.sourceArtifactChecksum || (selected?.kind === "ARTIFACT" ? selected.artifactChecksum : null);
  return <div className="workspace-provenance-trust-path" data-testid="workspace-artifact-lineage"><h4>Exact provenance chain</h4><ol>
    <li><strong>Finding</strong><span>{selectedClaim ? `${CLAIM_LABELS[selectedClaim.claimType]} (${selectedClaim.claimId})` : selected?.kind === "CLAIM" ? selected.claimId : "Choose a persisted claim for claim-level traceability."}</span></li>
    <li><strong>Evidence</strong><span>{selectedEvidence ? `${selectedEvidence.semanticRole} (${selectedEvidence.evidenceItemId})` : selected?.kind === "EVIDENCE_ITEM" ? selected.evidenceItemId : `${evidence.evidenceItems.length} item(s) in exact bundle`}</span></li>
    <li><strong>Artifact</strong><span>{artifactId || evidence.sourceArtifactIds.join(", ") || "No supported source Artifact"}</span>{checksum ? <code>{checksum}</code> : null}</li>
    <li><strong>Tool / version</strong><span>{selectedEvidence ? `${selectedEvidence.sourceToolId}@${selectedEvidence.sourceToolVersion}` : "Available after selecting exact evidence."}</span></li>
    <li><strong>Plan / Job</strong><span>Plan {interpretation.sourcePlanId} ({workspace.planSchemaVersion || "legacy"}); Job {workspace.sourceJobId}</span></li>
    <li><strong>Input identity</strong><span>Dataset {workspace.datasetId}@{workspace.datasetVersion || "unknown"}; source scope {compactIdentity(workspace.sourceReferenceHash, 28)}</span></li>
  </ol><details><summary>Lineage and developer details</summary><dl className="workspace-metadata-grid"><Metadata label="Interpretation" value={interpretation.interpretationId} /><Metadata label="Interpretation hash" value={compactIdentity(interpretation.interpretationHash, 32)} /><Metadata label="Evidence bundle" value={evidence.bundleId} /><Metadata label="Bundle hash" value={compactIdentity(evidence.bundleHash, 32)} /><Metadata label="Plan hash" value={compactIdentity(interpretation.sourcePlanHash, 32)} /><Metadata label="Plan dependency semantics" value={workspace.planSchemaVersion === "0.2" ? "Typed Artifact dependency bindings" : "Independent/sequential 0.1 semantics"} /><Metadata label="Panel provenance refs" value={String(panel.provenanceRefs.length)} /></dl></details></div>;
}

function WorkspaceDataContext({ snapshot }: { snapshot: WorkspaceSnapshot }) {
  const workspace = snapshot.workspace;
  return <dl className="workspace-data-list"><Metadata label="Project" value={compactIdentity(workspace.projectId, 28)} /><Metadata label="Dataset" value={compactIdentity(workspace.datasetId, 28)} /><Metadata label="Dataset version" value={workspace.datasetVersion || "Unavailable"} /><Metadata label="Profile" value={compactIdentity(workspace.profileId, 28)} /><Metadata label="Profile hash" value={compactIdentity(workspace.profileSemanticHash, 24)} /><Metadata label="Plan" value={compactIdentity(workspace.planId, 28)} /><Metadata label="Job" value={compactIdentity(workspace.sourceJobId, 28)} /><Metadata label="Artifacts" value={String(workspace.artifactCount)} /></dl>;
}

function WorkspaceSourceList({ panel }: { panel: WorkspacePanel }) {
  if (!panel.sourceRefs.length) return <p className="empty-state">This panel has no source references.</p>;
  return <ul className="workspace-source-list">{panel.sourceRefs.map((source) => <li key={`${source.kind}-${source.sourceId}`}><strong>{source.kind}</strong><span>{compactIdentity(source.sourceId, 36)}</span><small>{source.contract ? `${source.contract} ${source.contractVersion || ""}` : "Exact repository reference"}</small></li>)}</ul>;
}

function WorkspaceSelectionInspector({ selection, originPanelId, deliveries, panels, activePanel, pinState, readOnly, onClear, onCopy, onPin, onSelectPanel }: { selection: WorkspaceSelectionContext | null; originPanelId: string | null; deliveries: Record<string, WorkspaceSelectionDelivery>; panels: WorkspacePanel[]; activePanel: WorkspacePanel | null; pinState: "IDLE" | "SAVING" | "SAVED" | "CONFLICT" | "ERROR"; readOnly: boolean; onClear: () => void; onCopy: () => void; onPin: () => void; onSelectPanel: (panel: WorkspacePanel) => void }) {
  const primary = selection?.primary || null;
  const originPanel = panels.find((panel) => panel.panelId === originPanelId);
  const facts = primary ? Object.entries(primary).filter(([key, value]) => !["selectionSchemaVersion", "sourceScopeHash", "projectId", "kind"].includes(key) && value !== null) : [];
  return <section className="workspace-selection-inspector" aria-label="Canonical selection inspector">
    <section className="workspace-inspector-layer" aria-labelledby="inspector-summary-heading"><h3 id="inspector-summary-heading">Summary</h3>
    {primary ? <><p><strong>{primary.kind.replaceAll("_", " ")}</strong> selected from {originPanel?.title || "an exact URL or pinned state"}.</p>
      <div className="workspace-selection-actions"><button type="button" className="secondary" onClick={onClear}>Clear selection</button><button type="button" className="secondary" onClick={onCopy}>Copy selection link</button><button type="button" onClick={onPin} disabled={readOnly || pinState === "SAVING"}>{pinState === "SAVING" ? "Pinning" : "Pin selection"}</button></div>
      <p className="subtle" role="status">Pin state: {pinState}. Pinning is explicit; it never executes a tool, plan, or job.</p>
    </> : <p className="empty-state">No canonical selection is active. Source metadata remains read-only.</p>}
    </section>
    <details className="workspace-inspector-layer"><summary>Scientific details</summary>{primary ? <dl className="workspace-metadata-grid"><Metadata label="Kind" value={primary.kind} /><Metadata label="Origin panel" value={originPanel ? `${originPanel.title} (${originPanel.panelId})` : "URL or explicitly pinned state"} />{facts.map(([key, value]) => <Metadata key={key} label={key} value={String(value)} />)}</dl> : <p>No exact scientific object is selected.</p>}
    <h4>Compatible panels</h4>
    <ul className="workspace-selection-subscriptions">{panels.map((panel) => {
      const delivery = deliveries[panel.panelId];
      return <li key={panel.panelId}><div><strong>{panel.title}</strong><span>{delivery?.compatibility || "NOT_APPLICABLE"}</span><small>{delivery?.reason || "Awaiting selection runtime."}</small></div>{delivery?.compatibility === "EXACT" ? <button type="button" className="secondary" onClick={() => onSelectPanel(panel)}>Open panel</button> : null}</li>;
    })}</ul></details>
    <details className="workspace-inspector-layer"><summary>Provenance</summary>{primary ? <dl className="workspace-metadata-grid"><Metadata label="Project" value={compactIdentity(primary.projectId, 28)} /><Metadata label="Source scope" value={compactIdentity(primary.sourceScopeHash, 24)} /></dl> : null}{activePanel ? <WorkspaceSourceList panel={activePanel} /> : <p>No active panel.</p>}</details>
    <details className="workspace-inspector-layer"><summary>Developer details</summary><pre>{JSON.stringify({ selection, activePanelId: activePanel?.panelId || null }, null, 2)}</pre></details>
  </section>;
}

function WorkspaceEmptyState({ panelCount }: { panelCount: number }) {
  return <div className="workspace-empty-state" role="status"><h2>No active panel</h2><p>{panelCount ? "Choose an available Workspace section." : "This Workspace has no visible panel descriptors."}</p></div>;
}

function WorkspaceLoadState({
  title,
  message,
  actionHref,
  actionLabel,
  secondaryActionHref,
  secondaryActionLabel,
  onAction,
}: {
  title: string;
  message: string;
  actionHref?: string;
  actionLabel?: string;
  secondaryActionHref?: string;
  secondaryActionLabel?: string;
  onAction?: () => void;
}) {
  return <main className="workspace-route-state"><section role="status"><span className="eyebrow">Scientific Workspace</span><h1>{title}</h1><p>{message}</p><div className="workspace-route-actions">{onAction ? <button type="button" className="product-primary-action" onClick={onAction}>{actionLabel || "Retry"}</button> : null}{actionHref ? <Link className="product-primary-action" href={actionHref}>{actionLabel || "继续"}</Link> : null}{secondaryActionHref ? <Link className="product-secondary-action" href={secondaryActionHref}>{secondaryActionLabel || "返回"}</Link> : null}</div></section></main>;
}

function Metadata({ label, value }: { label: string; value: string }) {
  return <div><dt>{label}</dt><dd>{value}</dd></div>;
}

function boundedErrorMessage(value: string): string {
  const safe = value.replace(/[\r\n\t]+/g, " ").slice(0, 240);
  return safe || "Workspace metadata could not be loaded.";
}

function trapDialogFocus(event: React.KeyboardEvent<HTMLElement>) {
  if (event.key !== "Tab") return;
  const controls = Array.from(event.currentTarget.querySelectorAll<HTMLElement>("button:not([disabled]), input:not([disabled]), [href], [tabindex]:not([tabindex='-1'])"));
  if (!controls.length) return;
  const first = controls[0];
  const last = controls[controls.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}
