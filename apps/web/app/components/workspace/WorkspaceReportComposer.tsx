"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import type { ScientificWorkspace } from "../../lib/workspace-api";
import {
  downloadReportComposition,
  finalizeReportComposition,
  getReportComposition,
  getReportCompositionRecipe,
  getReportCompositionSources,
  listReportCompositions,
  previewReportComposition,
  ReportCompositionApiError,
  type RecipeReplayManifest,
  type ReportCompositionPreview,
  type ReportCompositionRequest,
  type ReportCompositionSnapshot,
  type ReportHistoryItem,
  type ReportSourceInventory,
  type ReportSourceReference,
  type ReportSourceRole,
} from "../../lib/report-composition-api";

type ComposerView = "COMPOSE" | "PREVIEW" | "HISTORY";
type SourceFilter = "ALL" | "FIGURES" | "TABLES" | "FINDINGS" | "EVIDENCE" | "PROVENANCE";

const FILTER_ROLE: Record<Exclude<SourceFilter, "ALL">, ReportSourceRole> = {
  FIGURES: "REPORT_FIGURE_SOURCE",
  TABLES: "REPORT_TABLE_SOURCE",
  FINDINGS: "REPORT_FINDING_SOURCE",
  EVIDENCE: "REPORT_EVIDENCE_SOURCE",
  PROVENANCE: "REPORT_PROVENANCE_SOURCE",
};

export function WorkspaceReportComposer({ workspace, onDraftDirtyChange }: { workspace: ScientificWorkspace; onDraftDirtyChange?: (dirty: boolean) => void }) {
  const [inventory, setInventory] = useState<ReportSourceInventory | null>(null);
  const [history, setHistory] = useState<ReportHistoryItem[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [captions, setCaptions] = useState<Record<string, string>>({});
  const [title, setTitle] = useState(`${workspace.title} report`);
  const [filter, setFilter] = useState<SourceFilter>("ALL");
  const [view, setView] = useState<ComposerView>("COMPOSE");
  const [preview, setPreview] = useState<ReportCompositionPreview | null>(null);
  const [detail, setDetail] = useState<ReportCompositionSnapshot | Record<string, unknown> | null>(null);
  const [recipe, setRecipe] = useState<RecipeReplayManifest | null>(null);
  const [activeReportId, setActiveReportId] = useState<string | null>(null);
  const [mobileSourcesOpen, setMobileSourcesOpen] = useState(false);
  const [state, setState] = useState<"LOADING" | "READY" | "PREVIEWING" | "FINALIZING" | "FAILED">("LOADING");
  const [message, setMessage] = useState("Loading report source inventory");
  const requestRef = useRef<AbortController | null>(null);
  const submissionSequence = useRef(0);
  const mobileSourceTriggerRef = useRef<HTMLButtonElement | null>(null);
  const mobileSourceCloseRef = useRef<HTMLButtonElement | null>(null);
  const [savedDraftSignature, setSavedDraftSignature] = useState(() => JSON.stringify({ title: `${workspace.title} report`, selectedIds: [], captions: {} }));

  const refreshHistory = useCallback(async (signal?: AbortSignal) => {
    const result = await listReportCompositions(workspace.workspaceId, signal);
    setHistory(result.items);
  }, [workspace.workspaceId]);

  useEffect(() => {
    const controller = new AbortController();
    setState("LOADING");
    Promise.all([
      getReportCompositionSources(workspace.workspaceId, controller.signal),
      listReportCompositions(workspace.workspaceId, controller.signal),
    ]).then(([sources, records]) => {
      if (controller.signal.aborted) return;
      if (sources.workspaceId !== workspace.workspaceId || sources.workspaceRevision !== workspace.revision) {
        throw new Error("REPORT_SOURCE_SCOPE_MISMATCH");
      }
      setInventory(sources);
      setHistory(records.items);
      setState("READY");
      setMessage(`${sources.sourceCount} exact sources; ${sources.mandatoryDisclosureCount} mandatory disclosures`);
    }).catch((error: unknown) => {
      if (!controller.signal.aborted) {
        setState("FAILED");
        setMessage(safeErrorMessage(error));
      }
    });
    return () => controller.abort();
  }, [workspace.revision, workspace.workspaceId]);

  useEffect(() => () => requestRef.current?.abort(), []);

  useEffect(() => {
    if (!mobileSourcesOpen) return;
    mobileSourceCloseRef.current?.focus();
    const close = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      setMobileSourcesOpen(false);
      mobileSourceTriggerRef.current?.focus();
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [mobileSourcesOpen]);

  const selectedSources = useMemo(() => {
    const sourceById = new Map((inventory?.sources || []).map((source) => [source.sourceId, source]));
    return selectedIds.flatMap((id) => sourceById.get(id) ? [sourceById.get(id)!] : []);
  }, [inventory, selectedIds]);

  const visibleSources = useMemo(() => (inventory?.sources || []).filter((source) => {
    if (filter === "ALL") return true;
    return source.role === FILTER_ROLE[filter];
  }), [filter, inventory]);

  const draftSignature = useMemo(() => JSON.stringify({ title, selectedIds, captions }), [captions, selectedIds, title]);
  const draftDirty = draftSignature !== savedDraftSignature;

  useEffect(() => {
    onDraftDirtyChange?.(draftDirty);
    const warn = (event: BeforeUnloadEvent) => {
      if (!draftDirty) return;
      event.preventDefault();
      event.returnValue = "";
    };
    window.addEventListener("beforeunload", warn);
    return () => {
      window.removeEventListener("beforeunload", warn);
      onDraftDirtyChange?.(false);
    };
  }, [draftDirty, onDraftDirtyChange]);

  const requestPayload = useCallback((): ReportCompositionRequest => {
    const panels: string[] = [];
    const artifacts: string[] = [];
    const claims: string[] = [];
    const evidence: string[] = [];
    for (const source of selectedSources) {
      if (source.sourceKind === "WORKSPACE_PANEL") panels.push(source.sourceId);
      if (source.sourceKind === "ARTIFACT") artifacts.push(source.sourceId);
      if (source.sourceKind === "SCIENTIFIC_CLAIM") claims.push(source.sourceId);
      if (source.sourceKind === "EVIDENCE_ITEM") evidence.push(source.sourceId);
    }
    return {
      schemaVersion: "1.0",
      workspaceId: workspace.workspaceId,
      expectedWorkspaceRevision: workspace.revision,
      title,
      selectedPanelIds: panels,
      selectedArtifactIds: artifacts,
      selectedClaimIds: claims,
      selectedEvidenceItemIds: evidence,
      itemOrder: selectedSources.map((source) => source.sourceId),
      captions: selectedSources.flatMap((source) => captions[source.sourceId] ? [{ sourceId: source.sourceId, text: captions[source.sourceId] }] : []),
      exportFormats: ["json", "markdown"],
    };
  }, [captions, selectedSources, title, workspace.revision, workspace.workspaceId]);

  const invalidatePreview = () => {
    setPreview(null);
    setDetail(null);
    setRecipe(null);
    setActiveReportId(null);
    submissionSequence.current += 1;
  };

  const addSource = (source: ReportSourceReference) => {
    if (!isSelectable(source) || selectedIds.includes(source.sourceId)) return;
    setSelectedIds((current) => [...current, source.sourceId]);
    invalidatePreview();
  };

  const removeSource = (sourceId: string) => {
    setSelectedIds((current) => current.filter((id) => id !== sourceId));
    setCaptions((current) => {
      const next = { ...current };
      delete next[sourceId];
      return next;
    });
    invalidatePreview();
  };

  const moveSource = (sourceId: string, offset: -1 | 1) => {
    setSelectedIds((current) => {
      const from = current.indexOf(sourceId);
      const to = from + offset;
      if (from < 0 || to < 0 || to >= current.length) return current;
      const next = [...current];
      [next[from], next[to]] = [next[to], next[from]];
      return next;
    });
    invalidatePreview();
  };

  const runPreview = async () => {
    requestRef.current?.abort();
    const controller = new AbortController();
    requestRef.current = controller;
    setState("PREVIEWING");
    setMessage("Validating deterministic preview");
    try {
      const result = await previewReportComposition(workspace.workspaceId, requestPayload(), controller.signal);
      if (controller.signal.aborted) return;
      setPreview(result);
      setView("PREVIEW");
      setState("READY");
      setMessage(`${result.predictedOutcome}; preview writes: 0`);
    } catch (error: unknown) {
      if (!controller.signal.aborted) {
        setState("FAILED");
        setMessage(safeErrorMessage(error));
      }
    }
  };

  const finalize = async () => {
    requestRef.current?.abort();
    const controller = new AbortController();
    requestRef.current = controller;
    setState("FINALIZING");
    setMessage("Persisting immutable Report and Recipe pair");
    try {
      const key = `m5-${workspace.workspaceId}-${workspace.revision}-${submissionSequence.current}`;
      const result = await finalizeReportComposition(workspace.workspaceId, requestPayload(), key, controller.signal);
      if (controller.signal.aborted) return;
      await refreshHistory(controller.signal);
      setActiveReportId(result.reportId);
      setSavedDraftSignature(draftSignature);
      setState("READY");
      setMessage(`${result.outcome}; ${result.idempotentReplay ? "idempotent replay" : "immutable pair saved"}`);
      await openHistory(result.reportId);
    } catch (error: unknown) {
      if (!controller.signal.aborted) {
        setState("FAILED");
        setMessage(safeErrorMessage(error));
      }
    }
  };

  const openHistory = async (reportId: string, existingSignal?: AbortSignal) => {
    if (!existingSignal) requestRef.current?.abort();
    const controller = existingSignal ? null : new AbortController();
    const signal = existingSignal || controller!.signal;
    if (controller) requestRef.current = controller;
    setState("LOADING");
    setMessage("Loading immutable Report and Recipe");
    try {
      const reportResult = await getReportComposition(workspace.workspaceId, reportId, signal);
      let recipeResult: RecipeReplayManifest | null = null;
      if (!reportResult.legacyReadOnly) {
        recipeResult = (await getReportCompositionRecipe(workspace.workspaceId, reportId, signal)).recipe;
      }
      if (signal.aborted) return;
      setDetail(reportResult.report);
      setRecipe(recipeResult);
      setActiveReportId(reportId);
      setView("HISTORY");
      setState("READY");
      setMessage(reportResult.legacyReadOnly ? "Legacy Report is read-only" : "Immutable Report and exact Recipe loaded");
    } catch (error: unknown) {
      if (!signal.aborted) {
        setState("FAILED");
        setMessage(safeErrorMessage(error));
      }
    }
  };

  const download = async (reportId: string, format: "json" | "markdown") => {
    requestRef.current?.abort();
    const controller = new AbortController();
    requestRef.current = controller;
    try {
      const result = await downloadReportComposition(workspace.workspaceId, reportId, format, controller.signal);
      const objectUrl = URL.createObjectURL(result.blob);
      const anchor = document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = result.filename;
      anchor.click();
      URL.revokeObjectURL(objectUrl);
      setMessage(`${format.toUpperCase()} export ready${result.exportHash ? ` (${result.exportHash.slice(0, 12)})` : ""}`);
    } catch (error: unknown) {
      if (!controller.signal.aborted) setMessage(safeErrorMessage(error));
    }
  };

  return <section className="workspace-report-composer" data-testid="workspace-report-composer" aria-labelledby="workspace-report-composer-title">
    <header className="workspace-report-heading">
      <div><h3 id="workspace-report-composer-title">Scientific report composition</h3><p>{inventory ? `${inventory.sourceCount} sources / ${inventory.mandatoryDisclosureCount} mandatory` : "Metadata inventory pending"}</p></div>
      <span className="workspace-report-integrity">Workspace revision {workspace.revision}</span>
    </header>

    <div className="workspace-report-tabs" role="tablist" aria-label="Report composition views">
      {(["COMPOSE", "PREVIEW", "HISTORY"] as ComposerView[]).map((item) => <button key={item} type="button" role="tab" aria-selected={view === item} onClick={() => setView(item)}>{item.charAt(0) + item.slice(1).toLowerCase()}</button>)}
    </div>
    <p className={`workspace-report-status tone-${state === "FAILED" ? "danger" : "muted"}`} role={state === "FAILED" ? "alert" : "status"}>{message}</p>
    <p className="workspace-report-draft-notice" role="note">
      {draftDirty ? "Unsaved report draft. " : "Report draft is session-only. "}
      Draft is not saved until Finalize. Refreshing or closing this page discards the unfinalized draft.
    </p>

    {view === "COMPOSE" ? <div className="workspace-report-compose-grid">
      {mobileSourcesOpen ? <div className="workspace-report-mobile-backdrop" onMouseDown={(event) => { if (event.currentTarget === event.target) { setMobileSourcesOpen(false); mobileSourceTriggerRef.current?.focus(); } }} /> : null}
      <section className={`workspace-report-source-picker ${mobileSourcesOpen ? "mobile-open" : "mobile-closed"}`} aria-labelledby="report-source-title" role={mobileSourcesOpen ? "dialog" : undefined} aria-modal={mobileSourcesOpen ? true : undefined} onKeyDown={trapDialogFocus}>
        <div className="workspace-report-section-heading"><h4 id="report-source-title">Source inventory</h4><span>Metadata only</span><button ref={mobileSourceCloseRef} type="button" className="secondary workspace-report-mobile-close" aria-label="Close source picker" onClick={() => { setMobileSourcesOpen(false); mobileSourceTriggerRef.current?.focus(); }}>Close</button></div>
        <div className="workspace-report-filters" aria-label="Source filters">
          {(["ALL", "FIGURES", "TABLES", "FINDINGS", "EVIDENCE", "PROVENANCE"] as SourceFilter[]).map((item) => <button key={item} type="button" className={filter === item ? "active" : ""} aria-pressed={filter === item} onClick={() => setFilter(item)}>{item.charAt(0) + item.slice(1).toLowerCase()}</button>)}
        </div>
        <ul className="workspace-report-source-list">
          {visibleSources.map((source) => <li key={source.sourceId}>
            <div><strong>{source.role.replace("REPORT_", "").replace("_SOURCE", "").replaceAll("_", " ")}</strong><span>{source.contract ? `${source.contract}@${source.contractVersion || "unknown"}` : source.sourceKind}</span><small>{source.fallback || source.reason || source.sourceId}</small></div>
            <button type="button" className="secondary" disabled={!isSelectable(source) || selectedIds.includes(source.sourceId)} onClick={() => addSource(source)} aria-label={`Add ${source.sourceId} to report`}>{selectedIds.includes(source.sourceId) ? "Added" : "Add"}</button>
          </li>)}
        </ul>
      </section>

      <section className="workspace-report-draft" aria-labelledby="report-draft-title">
        <div className="workspace-report-section-heading"><h4 id="report-draft-title">Draft composition</h4><span>{selectedIds.length} selected</span></div>
        <button ref={mobileSourceTriggerRef} type="button" className="secondary workspace-report-mobile-source-trigger" onClick={() => setMobileSourcesOpen(true)}>Choose sources</button>
        <label>Report title<input value={title} maxLength={256} onChange={(event) => { setTitle(event.target.value); invalidatePreview(); }} /></label>
        <ul className="workspace-report-selected-list">
          {selectedSources.map((source, index) => <li key={source.sourceId}>
            <div><strong>{source.sourceKind}</strong><span>{source.sourceId}</span></div>
            <label>Caption<input value={captions[source.sourceId] || ""} maxLength={2048} onChange={(event) => { setCaptions((current) => ({ ...current, [source.sourceId]: event.target.value })); invalidatePreview(); }} /></label>
            <div className="workspace-report-order-actions"><button type="button" className="secondary" aria-label={`Move ${source.sourceId} up`} disabled={index === 0} onClick={() => moveSource(source.sourceId, -1)}>Up</button><button type="button" className="secondary" aria-label={`Move ${source.sourceId} down`} disabled={index === selectedSources.length - 1} onClick={() => moveSource(source.sourceId, 1)}>Down</button><button type="button" className="secondary" aria-label={`Remove ${source.sourceId} from report`} onClick={() => removeSource(source.sourceId)}>Remove</button></div>
          </li>)}
        </ul>
        <section className="workspace-report-mandatory" aria-labelledby="report-mandatory-title"><h5 id="report-mandatory-title">Mandatory disclosures</h5>{inventory?.mandatoryDisclosures.length ? <ul>{inventory.mandatoryDisclosures.map((item) => <li key={item.sourceId}>{item.fallback || item.reason || item.sourceId}</li>)}</ul> : <p>No mandatory disclosures.</p>}</section>
        <div className="workspace-report-actions"><button type="button" onClick={() => void runPreview()} disabled={!title.trim() || state === "PREVIEWING" || state === "FINALIZING"}>Preview report</button></div>
      </section>
    </div> : null}

    {view === "PREVIEW" ? <section className="workspace-report-preview" aria-labelledby="report-preview-title">
      <div className="workspace-report-section-heading"><h4 id="report-preview-title">Deterministic preview</h4><span>{preview?.predictedOutcome || "Not generated"}</span></div>
      {preview ? <><p className="workspace-report-no-write" role="status">Preview is not persisted. Report writes 0; Recipe writes 0; Job creation 0.</p><ReportSections report={preview.report} /><RecipeSummary recipe={preview.recipe} /><div className="workspace-report-actions"><button type="button" onClick={() => void finalize()} disabled={workspace.readOnly || state === "FINALIZING"}>Finalize report</button></div></> : <p>Generate a preview from the current draft.</p>}
    </section> : null}

    {view === "HISTORY" ? <section className="workspace-report-history" aria-labelledby="report-history-title">
      <div className="workspace-report-section-heading"><h4 id="report-history-title">Immutable history</h4><span>{history.length} snapshot(s)</span></div>
      <ul>{history.map((item) => <li key={item.reportId} className={activeReportId === item.reportId ? "active" : ""}><div><strong>{item.title}</strong><span>{item.outcome || "LEGACY_READ_ONLY"} / {item.version}</span><small>{item.reportId}</small></div><button type="button" className="secondary" onClick={() => void openHistory(item.reportId)}>Open</button></li>)}</ul>
      {detail ? <div className="workspace-report-detail"><h4>Report detail</h4>{isReportSnapshot(detail) ? <ReportSections report={detail} /> : <pre>{JSON.stringify(detail, null, 2)}</pre>}{recipe ? <RecipeSummary recipe={recipe} /> : <p>Recipe unavailable for this legacy Report.</p>}{activeReportId && recipe ? <div className="workspace-report-actions"><button type="button" className="secondary" onClick={() => void download(activeReportId, "json")}>Download canonical JSON</button><button type="button" className="secondary" onClick={() => void download(activeReportId, "markdown")}>Download Markdown</button></div> : null}</div> : null}
    </section> : null}
  </section>;
}

function ReportSections({ report }: { report: ReportCompositionSnapshot }) {
  return <article className="workspace-report-document"><header><span>{report.outcome}</span><h4>{report.title}</h4><p>{report.analysisGoal}</p></header>{report.sections.map((section) => <section key={section.sectionId} aria-labelledby={`report-section-${section.sectionId}`}><h5 id={`report-section-${section.sectionId}`}>{section.title}</h5><span>{section.status}</span>{section.items.length ? <ul>{section.items.map((item, index) => <li key={`${section.sectionId}-${index}`}>{item}</li>)}</ul> : <p>Typed empty or unavailable.</p>}</section>)}</article>;
}

function RecipeSummary({ recipe }: { recipe: RecipeReplayManifest }) {
  return <details className="workspace-recipe-summary"><summary>Exact non-executable Recipe</summary><dl><div><dt>Plan</dt><dd>{recipe.analysisPlanId} / {recipe.planSchemaVersion}</dd></div><div><dt>Dependency model</dt><dd>{recipe.dependencyModel}</dd></div><div><dt>Steps</dt><dd>{recipe.steps.length}</dd></div><div><dt>Execution authorized</dt><dd>No</dd></div><div><dt>Automatic replay</dt><dd>No</dd></div><div><dt>Recipe hash</dt><dd>{recipe.recipeHash}</dd></div></dl></details>;
}

function isSelectable(source: ReportSourceReference): boolean {
  return ["ELIGIBLE", "METADATA_ONLY"].includes(source.state) && ["WORKSPACE_PANEL", "ARTIFACT", "SCIENTIFIC_CLAIM", "EVIDENCE_ITEM"].includes(source.sourceKind) && source.role !== "REPORT_UNSUPPORTED";
}

function isReportSnapshot(value: ReportCompositionSnapshot | Record<string, unknown>): value is ReportCompositionSnapshot {
  return value.schemaVersion === "1.0" && Array.isArray(value.sections) && typeof value.reportHash === "string";
}

function safeErrorMessage(error: unknown): string {
  if (error instanceof ReportCompositionApiError) return `${error.code}: ${error.message}`;
  if (error instanceof Error && error.message === "REPORT_SOURCE_SCOPE_MISMATCH") return "REPORT_SOURCE_SCOPE_MISMATCH";
  return "Report composition is unavailable.";
}

function trapDialogFocus(event: React.KeyboardEvent<HTMLElement>) {
  if (event.key !== "Tab") return;
  const controls = Array.from(event.currentTarget.querySelectorAll<HTMLElement>("button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex='-1'])"));
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
