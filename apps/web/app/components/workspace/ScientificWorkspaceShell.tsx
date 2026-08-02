"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  getWorkspace,
  patchWorkspace,
  type WorkspaceApiError,
  type WorkspacePanel,
  type WorkspaceSelectionContext,
  type WorkspaceSnapshot,
} from "../../lib/workspace-api";
import {
  WORKSPACE_NAVIGATION_GROUPS,
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
} from "./workspace-selection-contract";
import {
  artifactSelectionFromPanel,
  type WorkspaceSelectionDelivery,
  WorkspaceSelectionStore,
} from "./workspace-selection-runtime";

type LoadState = "LOADING" | "READY" | "NOT_FOUND" | "ERROR";

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
  const inspectorCloseRef = useRef<HTMLButtonElement | null>(null);
  const inspectorTriggerRef = useRef<HTMLButtonElement | null>(null);
  const requestIdRef = useRef(0);
  const selectionStoreRef = useRef<WorkspaceSelectionStore | null>(null);

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

  useEffect(() => {
    const onPopState = () => {
      if (snapshot) applyUrlState(snapshot);
    };
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, [applyUrlState, snapshot]);

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

  const visiblePanels = useMemo(() => (snapshot ? orderedVisiblePanels(snapshot) : []), [snapshot]);
  const activePanel = visiblePanels.find((panel) => panel.panelId === activePanelId) || null;

  const selectPanel = useCallback((panel: WorkspacePanel) => {
    const next = new URL(window.location.href);
    next.searchParams.set("panel", panel.panelId);
    window.history.pushState({ panelId: panel.panelId }, "", next);
    setInvalidPanelId(null);
    setActivePanelId(panel.panelId);
    setMobileContextOpen(false);
  }, []);

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
  if (loadState === "NOT_FOUND") return <WorkspaceLoadState title="Workspace not found" message="The exact Workspace ID is unavailable in this project." actionHref="/" />;
  if (loadState === "ERROR" || !snapshot) return <WorkspaceLoadState title="Workspace unavailable" message={loadMessage} actionLabel="Retry" onAction={load} />;

  const workspace = snapshot.workspace;
  return (
    <main className="scientific-workspace" data-testid="scientific-workspace-shell">
      <header className="workspace-header">
        <div className="workspace-header-title">
          <a className="workspace-back-link" href="/" aria-label="Back to PlannerWorkbench">Back to planner</a>
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
          <button type="button" className="secondary workspace-mobile-only" onClick={() => setMobileContextOpen(true)} aria-label="Open data context">Context</button>
          <button ref={inspectorTriggerRef} type="button" className="secondary" onClick={() => setInspectorOpen(true)} aria-haspopup="dialog">Inspector</button>
        </div>
      </header>

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
          <h2>Workspace</h2>
          <ul>
            {WORKSPACE_NAVIGATION_GROUPS.map((group) => {
              const panel = firstPanelForKind(snapshot, group.panelKind);
              const current = panel?.panelId === activePanelId;
              return <li key={group.id}><button type="button" className={current ? "active" : ""} disabled={!panel} aria-current={current ? "page" : undefined} onClick={() => panel && selectPanel(panel)}><span>{group.label}</span><small>{panel ? panel.state : "Unavailable"}</small></button></li>;
            })}
          </ul>
        </nav>

        <section className="workspace-main-panel" aria-labelledby="workspace-active-panel-title">
          {activePanel ? <WorkspacePanelSurface panel={activePanel} workspace={workspace} snapshot={snapshot} delivery={deliveries[activePanel.panelId] || null} onSelectArtifact={(panel) => {
            const nextSelection = artifactSelectionFromPanel(panel, workspace);
            if (nextSelection) activateSelection(nextSelection, panel.panelId);
          }} /> : <WorkspaceEmptyState panelCount={visiblePanels.length} />}
        </section>
      </div>

      {mobileContextOpen ? (
        <div className="workspace-mobile-drawer" role="dialog" aria-modal="true" aria-label="Data context drawer">
          <div className="workspace-drawer-header"><h2>Data context</h2><button type="button" className="workspace-icon-button" aria-label="Close data context" onClick={() => setMobileContextOpen(false)}>X</button></div>
          <WorkspaceDataContext snapshot={snapshot} />
          <div className="workspace-mobile-panel-switcher"><h3>Panels</h3>{visiblePanels.map((panel) => <button key={panel.panelId} type="button" className="secondary" onClick={() => selectPanel(panel)}>{panel.title}</button>)}</div>
        </div>
      ) : null}

      {inspectorOpen ? (
        <div className="workspace-inspector-backdrop" onMouseDown={(event) => event.currentTarget === event.target && setInspectorOpen(false)}>
          <aside className="workspace-inspector" role="dialog" aria-modal="true" aria-labelledby="workspace-inspector-title">
            <div className="workspace-drawer-header"><h2 id="workspace-inspector-title">Context inspector</h2><button ref={inspectorCloseRef} type="button" className="workspace-icon-button" aria-label="Close inspector" onClick={() => { setInspectorOpen(false); inspectorTriggerRef.current?.focus(); }}>X</button></div>
            <p className="subtle">Exact source metadata and canonical cross-panel selection state.</p>
            <WorkspaceSelectionInspector selection={selection} originPanelId={selectionOriginPanelId} deliveries={deliveries} panels={visiblePanels} pinState={pinState} readOnly={workspace.readOnly} onClear={clearSelection} onCopy={copySelectionLink} onPin={pinSelection} onSelectPanel={selectPanel} />
            {activePanel ? <WorkspaceSourceList panel={activePanel} /> : <p>No active panel.</p>}
          </aside>
        </div>
      ) : null}
    </main>
  );
}

function WorkspacePanelSurface({ panel, workspace, snapshot, delivery, onSelectArtifact }: { panel: WorkspacePanel; workspace: WorkspaceSnapshot["workspace"]; snapshot: WorkspaceSnapshot; delivery: WorkspaceSelectionDelivery | null; onSelectArtifact: (panel: WorkspacePanel) => void }) {
  const selectableArtifact = artifactSelectionFromPanel(panel, workspace);
  return (
    <article className="workspace-panel-surface" data-testid={`workspace-panel-${panel.panelKind.toLowerCase()}`}>
      <header className="workspace-panel-header">
        <div><span className="eyebrow">{panel.panelKind.replaceAll("_", " ")}</span><h2 id="workspace-active-panel-title">{panel.title}</h2></div>
        <span className={`workspace-status tone-${panelStateTone(panel.state)}`}>{panel.state}</span>
      </header>
      <p className="workspace-panel-state-copy">{panelStateCopy(panel.state)}</p>
      <div className={`workspace-selection-delivery tone-${delivery?.compatibility === "EXACT" ? "success" : "muted"}`} role="status" aria-label="Panel selection compatibility">
        <strong>Selection compatibility</strong><span>{delivery ? `${delivery.compatibility}: ${delivery.reason}` : "NOT_APPLICABLE: no selection runtime delivery yet."}</span>
      </div>
      {panel.state === "PARTIAL" || panel.state === "BLOCKED_BY_DEPENDENCY" ? <div className="workspace-panel-warning" role="status">This panel reflects only successful source branches. Failed or blocked outputs are not presented as complete.</div> : null}
      <dl className="workspace-metadata-grid">
        <Metadata label="Renderer contract" value={panel.rendererContract} />
        <Metadata label="Panel ID" value={compactIdentity(panel.panelId, 32)} />
        <Metadata label="Source references" value={String(panel.sourceRefs.length)} />
        <Metadata label="Evidence links" value={String(panel.evidenceRefs.length)} />
        <Metadata label="Provenance links" value={String(panel.provenanceRefs.length)} />
        <Metadata label="Plan schema" value={workspace.planSchemaVersion || "Legacy"} />
      </dl>
      {panel.unsupportedReason ? <div className="workspace-panel-warning" role="alert"><strong>Unsupported source contract</strong><span>{panel.unsupportedReason}</span></div> : null}
      {panel.panelKind === "OVERVIEW" ? <WorkspaceOverview snapshot={snapshot} /> : null}
      {panel.panelKind === "PLAN" ? <WorkspacePlanSummary snapshot={snapshot} /> : null}
      {panel.panelKind === "EXECUTION" ? <WorkspaceExecutionSummary snapshot={snapshot} /> : null}
      {["FINDINGS", "EVIDENCE", "PROVENANCE", "REPORT"].includes(panel.panelKind) ? <WorkspaceReferenceSummary panel={panel} snapshot={snapshot} /> : null}
      {panel.panelKind === "SCIENTIFIC_RESULT" ? <p className="workspace-deferred-note">Scientific payload rendering is deferred to the typed renderer registry in Phase 10M-4. Exact metadata remains available here.</p> : null}
      {selectableArtifact ? <button type="button" className="secondary workspace-selection-command" onClick={() => onSelectArtifact(panel)} data-testid={`workspace-select-artifact-${panel.panelId}`}>Select exact artifact</button> : null}
      <details className="workspace-audit-json"><summary>Audit JSON</summary><pre>{JSON.stringify({ panel, sourceSummary: snapshot.sourceSummary }, null, 2)}</pre></details>
    </article>
  );
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

function WorkspaceReferenceSummary({ panel, snapshot }: { panel: WorkspacePanel; snapshot: WorkspaceSnapshot }) {
  const labels: Record<string, string> = { FINDINGS: "Grounded interpretation", EVIDENCE: "Scientific evidence", PROVENANCE: "Source lineage", REPORT: "Report and recipe" };
  return <section className="workspace-summary-band"><h3>{labels[panel.panelKind]}</h3><p>Exact references are available from {panel.sourceRefs.length} source record(s).</p><dl className="workspace-metadata-grid"><Metadata label="Interpretations" value={String(snapshot.sourceSummary.interpretationCount)} /><Metadata label="Reports" value={String(snapshot.sourceSummary.reportCount)} /><Metadata label="Recipes" value={String(snapshot.sourceSummary.recipeCount)} /><Metadata label="Metadata only" value="Yes" /></dl>{panel.panelKind === "REPORT" ? <p className="workspace-deferred-note">Report and recipe composition remain read-only entry points until Phase 10M-5.</p> : null}</section>;
}

function WorkspaceDataContext({ snapshot }: { snapshot: WorkspaceSnapshot }) {
  const workspace = snapshot.workspace;
  return <dl className="workspace-data-list"><Metadata label="Project" value={compactIdentity(workspace.projectId, 28)} /><Metadata label="Dataset" value={compactIdentity(workspace.datasetId, 28)} /><Metadata label="Dataset version" value={workspace.datasetVersion || "Unavailable"} /><Metadata label="Profile" value={compactIdentity(workspace.profileId, 28)} /><Metadata label="Profile hash" value={compactIdentity(workspace.profileSemanticHash, 24)} /><Metadata label="Plan" value={compactIdentity(workspace.planId, 28)} /><Metadata label="Job" value={compactIdentity(workspace.sourceJobId, 28)} /><Metadata label="Artifacts" value={String(workspace.artifactCount)} /></dl>;
}

function WorkspaceSourceList({ panel }: { panel: WorkspacePanel }) {
  if (!panel.sourceRefs.length) return <p className="empty-state">This panel has no source references.</p>;
  return <ul className="workspace-source-list">{panel.sourceRefs.map((source) => <li key={`${source.kind}-${source.sourceId}`}><strong>{source.kind}</strong><span>{compactIdentity(source.sourceId, 36)}</span><small>{source.contract ? `${source.contract} ${source.contractVersion || ""}` : "Exact repository reference"}</small></li>)}</ul>;
}

function WorkspaceSelectionInspector({ selection, originPanelId, deliveries, panels, pinState, readOnly, onClear, onCopy, onPin, onSelectPanel }: { selection: WorkspaceSelectionContext | null; originPanelId: string | null; deliveries: Record<string, WorkspaceSelectionDelivery>; panels: WorkspacePanel[]; pinState: "IDLE" | "SAVING" | "SAVED" | "CONFLICT" | "ERROR"; readOnly: boolean; onClear: () => void; onCopy: () => void; onPin: () => void; onSelectPanel: (panel: WorkspacePanel) => void }) {
  const primary = selection?.primary || null;
  const originPanel = panels.find((panel) => panel.panelId === originPanelId);
  const facts = primary ? Object.entries(primary).filter(([key, value]) => !["selectionSchemaVersion", "sourceScopeHash", "projectId", "kind"].includes(key) && value !== null) : [];
  return <section className="workspace-selection-inspector" aria-label="Canonical selection inspector">
    <h3>Canonical selection</h3>
    {primary ? <><dl className="workspace-metadata-grid"><Metadata label="Kind" value={primary.kind} /><Metadata label="Origin panel" value={originPanel ? `${originPanel.title} (${originPanel.panelId})` : "URL or explicitly pinned state"} /><Metadata label="Project" value={compactIdentity(primary.projectId, 28)} /><Metadata label="Source scope" value={compactIdentity(primary.sourceScopeHash, 24)} />{facts.map(([key, value]) => <Metadata key={key} label={key} value={String(value)} />)}</dl>
      <div className="workspace-selection-actions"><button type="button" className="secondary" onClick={onClear}>Clear selection</button><button type="button" className="secondary" onClick={onCopy}>Copy selection link</button><button type="button" onClick={onPin} disabled={readOnly || pinState === "SAVING"}>{pinState === "SAVING" ? "Pinning" : "Pin selection"}</button></div>
      <p className="subtle" role="status">Pin state: {pinState}. Pinning is explicit; it never executes a tool, plan, or job.</p>
    </> : <p className="empty-state">No canonical selection is active. Source metadata remains read-only.</p>}
    <h3>Panel subscriptions</h3>
    <ul className="workspace-selection-subscriptions">{panels.map((panel) => {
      const delivery = deliveries[panel.panelId];
      return <li key={panel.panelId}><div><strong>{panel.title}</strong><span>{delivery?.compatibility || "NOT_APPLICABLE"}</span><small>{delivery?.reason || "Awaiting selection runtime."}</small></div>{delivery?.compatibility === "EXACT" ? <button type="button" className="secondary" onClick={() => onSelectPanel(panel)}>Open panel</button> : null}</li>;
    })}</ul>
  </section>;
}

function WorkspaceEmptyState({ panelCount }: { panelCount: number }) {
  return <div className="workspace-empty-state" role="status"><h2>No active panel</h2><p>{panelCount ? "Choose an available Workspace section." : "This Workspace has no visible panel descriptors."}</p></div>;
}

function WorkspaceLoadState({ title, message, actionHref, actionLabel, onAction }: { title: string; message: string; actionHref?: string; actionLabel?: string; onAction?: () => void }) {
  return <main className="workspace-route-state"><section role="status"><span className="eyebrow">Scientific Workspace</span><h1>{title}</h1><p>{message}</p>{actionHref ? <a href={actionHref}>Back to planner</a> : null}{onAction ? <button type="button" onClick={onAction}>{actionLabel || "Retry"}</button> : null}</section></main>;
}

function Metadata({ label, value }: { label: string; value: string }) {
  return <div><dt>{label}</dt><dd>{value}</dd></div>;
}

function boundedErrorMessage(value: string): string {
  const safe = value.replace(/[\r\n\t]+/g, " ").slice(0, 240);
  return safe || "Workspace metadata could not be loaded.";
}
