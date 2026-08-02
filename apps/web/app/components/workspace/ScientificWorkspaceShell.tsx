"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  getWorkspace,
  type WorkspaceApiError,
  type WorkspacePanel,
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
  const inspectorCloseRef = useRef<HTMLButtonElement | null>(null);
  const inspectorTriggerRef = useRef<HTMLButtonElement | null>(null);
  const requestIdRef = useRef(0);

  const applyUrlPanel = useCallback((nextSnapshot: WorkspaceSnapshot) => {
    const requested = new URLSearchParams(window.location.search).get("panel");
    const selected = panelForRequestedId(nextSnapshot, requested);
    setInvalidPanelId(requested && !selected ? requested : null);
    setActivePanelId(selected?.panelId || null);
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
        applyUrlPanel(response.data);
        setLoadState("READY");
      })
      .catch((error: WorkspaceApiError | Error) => {
        if (controller.signal.aborted || requestId !== requestIdRef.current) return;
        const status = "status" in error ? error.status : 0;
        setLoadState(status === 404 ? "NOT_FOUND" : "ERROR");
        setLoadMessage(status === 404 ? "Workspace not found" : boundedErrorMessage(error.message));
      });
    return () => controller.abort();
  }, [applyUrlPanel, workspaceId]);

  useEffect(() => load(), [load]);

  useEffect(() => {
    const onPopState = () => {
      if (snapshot) applyUrlPanel(snapshot);
    };
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, [applyUrlPanel, snapshot]);

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
          {activePanel ? <WorkspacePanelSurface panel={activePanel} workspace={workspace} snapshot={snapshot} /> : <WorkspaceEmptyState panelCount={visiblePanels.length} />}
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
            <p className="subtle">Exact source metadata for the active panel. Cross-panel selection is deferred to Phase 10M-3.</p>
            {activePanel ? <WorkspaceSourceList panel={activePanel} /> : <p>No active panel.</p>}
          </aside>
        </div>
      ) : null}
    </main>
  );
}

function WorkspacePanelSurface({ panel, workspace, snapshot }: { panel: WorkspacePanel; workspace: WorkspaceSnapshot["workspace"]; snapshot: WorkspaceSnapshot }) {
  return (
    <article className="workspace-panel-surface" data-testid={`workspace-panel-${panel.panelKind.toLowerCase()}`}>
      <header className="workspace-panel-header">
        <div><span className="eyebrow">{panel.panelKind.replaceAll("_", " ")}</span><h2 id="workspace-active-panel-title">{panel.title}</h2></div>
        <span className={`workspace-status tone-${panelStateTone(panel.state)}`}>{panel.state}</span>
      </header>
      <p className="workspace-panel-state-copy">{panelStateCopy(panel.state)}</p>
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
