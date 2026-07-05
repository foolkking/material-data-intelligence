"use client";

import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";

import { createTranslator, type Locale, type MessageKey } from "../lib/i18n";
import {
  type AnalysisPlan,
  type Artifact,
  type DataProfileSummary,
  type DatasetOption,
  type JobEvent,
  type JobResult,
  type PlannerApiError,
  type PlannerJobCreateResult,
  type PlannerJobDetail,
  type ProviderOption,
  type ProviderResolveResult,
  type ProviderStatus,
  type ProviderTestResult,
  type RuntimeHealth,
  type SecretSummary,
  type ToolCall,
  type ValidationError,
  createDatasetProfile,
  createPlannerJob,
  createSecret,
  deleteSecret,
  getDatasetProfile,
  getPlannerJob,
  getPlannerJobArtifacts,
  getPlannerJobEvents,
  getPlannerJobEventsStreamUrl,
  getPlannerJobResult,
  getPlannerJobToolCalls,
  getPlannerProviderStatus,
  getRuntimeHealth,
  listDatasets,
  listPlannerProviders,
  listSecrets,
  loadDemoDataset,
  resolvePlannerProvider,
  testPlannerProvider,
  uploadDataset
} from "../lib/planner-api";

type MainWorkspaceTab = "agent_process" | "conversation_plan" | "results_export";
type ProviderPreset = "openai" | "deepseek" | "custom";
type ChunkKind = "user_request" | "plan_preview" | "validation_result" | "run_status" | "result_reference";

type WorkspaceSnapshot = {
  job?: PlannerJobDetail;
  events: JobEvent[];
  toolCalls: ToolCall[];
  artifacts: Artifact[];
  result?: JobResult;
};

type ConversationChunk = {
  id: string;
  kind: ChunkKind;
  title: string;
  summary: string;
  status: "idle" | "running" | "success" | "warning" | "error";
  relatedStepId?: string;
  relatedArtifactIds: string[];
};

const examplePromptKeys: MessageKey[] = ["examplePromptMetrics", "examplePromptElements", "examplePromptOutliers", "examplePromptStructure"];

const presetDefaults: Record<ProviderPreset, { baseUrl: string; model: string }> = {
  openai: { baseUrl: "https://api.openai.com/v1", model: "gpt-4o" },
  deepseek: { baseUrl: "https://api.deepseek.com/v1", model: "deepseek-chat" },
  custom: { baseUrl: "", model: "" }
};

export function PlannerWorkbench() {
  const [locale, setLocale] = useState<Locale>("zh-CN");
  const t = useMemo(() => createTranslator(locale), [locale]);
  const examplePrompts = useMemo(() => examplePromptKeys.map((key) => t(key)), [t]);

  const [developerMode, setDeveloperMode] = useState(false);
  const [activeMainTab, setActiveMainTab] = useState<MainWorkspaceTab>("conversation_plan");
  const [selectedChunkId, setSelectedChunkId] = useState<string>("");
  const [selectedResultArtifactId, setSelectedResultArtifactId] = useState<string>("");
  const [datasetDialogOpen, setDatasetDialogOpen] = useState(false);
  const [modelDialogOpen, setModelDialogOpen] = useState(false);
  const [leftPanelWidth, setLeftPanelWidth] = useState(332);
  const [leftPanelCollapsed, setLeftPanelCollapsed] = useState(false);

  const [projectId, setProjectId] = useState("project_local");
  const [datasetId, setDatasetId] = useState("");
  const [profileId, setProfileId] = useState("");
  const [datasets, setDatasets] = useState<DatasetOption[]>([]);
  const [profile, setProfile] = useState<DataProfileSummary | null>(null);
  const [dataMessage, setDataMessage] = useState(t("emptyDataset"));
  const [dataBusy, setDataBusy] = useState(false);

  const [providerMode, setProviderMode] = useState<"mock" | "openai_compatible">("mock");
  const [providerPreset, setProviderPreset] = useState<ProviderPreset>("deepseek");
  const [providerOptions, setProviderOptions] = useState<ProviderOption[]>([]);
  const [providerStatus, setProviderStatus] = useState<ProviderStatus | null>(null);
  const [providerResolution, setProviderResolution] = useState<ProviderResolveResult | null>(null);
  const [providerResult, setProviderResult] = useState<ProviderTestResult | null>(null);
  const [baseUrl, setBaseUrl] = useState(presetDefaults.deepseek.baseUrl);
  const [model, setModel] = useState(presetDefaults.deepseek.model);
  const [temperature, setTemperature] = useState(0.1);
  const [maxTokens, setMaxTokens] = useState(1024);
  const [timeoutSeconds, setTimeoutSeconds] = useState(60);
  const [secretAlias, setSecretAlias] = useState("Demo LLM Key");
  const [apiKey, setApiKey] = useState("");
  const [secrets, setSecrets] = useState<SecretSummary[]>([]);
  const [selectedSecretId, setSelectedSecretId] = useState("");

  const [prompt, setPrompt] = useState(() => createTranslator("zh-CN")("examplePromptMetrics"));
  const [createdResult, setCreatedResult] = useState<PlannerJobCreateResult | null>(null);
  const [snapshot, setSnapshot] = useState<WorkspaceSnapshot>({ events: [], toolCalls: [], artifacts: [] });
  const [validationFailure, setValidationFailure] = useState<ValidationError[] | null>(null);
  const [submitError, setSubmitError] = useState<PlannerApiError | Error | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [health, setHealth] = useState<RuntimeHealth | null>(null);
  const [timelineMode, setTimelineMode] = useState<"sse" | "polling" | "idle">("idle");
  const eventSourceRef = useRef<EventSource | null>(null);

  const plan = createdResult?.plan || snapshot.job?.analysisPlan || null;
  const jobId = createdResult?.job_id || snapshot.job?.jobId || snapshot.job?.id || "";
  const planId = createdResult?.plan_id || snapshot.job?.planId || snapshot.result?.planId || "";
  const planHash = createdResult?.plan_hash || snapshot.job?.planHash || snapshot.result?.planHash || "";
  const jobStatus = snapshot.job?.status || (jobId ? "queued" : "");
  const isTerminal = ["completed", "failed", "cancelled"].includes(String(jobStatus));
  const selectedDataset = datasets.find((dataset) => (dataset.datasetId || dataset.id) === datasetId);
  const providerLabel =
    providerMode === "mock"
      ? t("mockPlanner")
      : providerResolution?.willUseLiveProvider
        ? `Live LLM / ${providerResolution.model || model || t("notConfigured")}`
        : `${providerPreset} / ${model || t("notConfigured")} / ${providerResolution?.status || t("notConfigured")}`;
  const chunks = useMemo(
    () =>
      buildConversationChunks({
        t,
        prompt,
        plan,
        createdResult,
        validationFailure,
        jobId,
        jobStatus,
        artifacts: snapshot.artifacts
      }),
    [t, prompt, plan, createdResult, validationFailure, jobId, jobStatus, snapshot.artifacts]
  );
  const selectedChunk = chunks.find((chunk) => chunk.id === selectedChunkId);
  const selectedArtifact = snapshot.artifacts.find((artifact) => (artifact.artifactId || artifact.id) === selectedResultArtifactId);

  useEffect(() => {
    setDataMessage(t("emptyDataset"));
  }, [t]);

  useEffect(() => {
    void loadInitialState();
    return () => {
      eventSourceRef.current?.close();
    };
  }, []);

  useEffect(() => {
    void refreshProviderResolution();
  }, [providerMode, baseUrl, model, selectedSecretId, temperature, maxTokens, timeoutSeconds]);

  useEffect(() => {
    if (!jobId || timelineMode !== "polling" || isTerminal) {
      return;
    }
    const interval = window.setInterval(() => {
      void refreshSnapshot(jobId);
    }, 2500);
    return () => window.clearInterval(interval);
  }, [jobId, timelineMode, isTerminal]);

  async function loadInitialState() {
    const [healthResult, datasetResult, providersResult, statusResult, secretsResult] = await Promise.allSettled([
      getRuntimeHealth(),
      listDatasets(),
      listPlannerProviders(),
      getPlannerProviderStatus(),
      listSecrets()
    ]);
    if (healthResult.status === "fulfilled") setHealth(healthResult.value);
    if (datasetResult.status === "fulfilled") setDatasets(datasetResult.value);
    if (providersResult.status === "fulfilled") setProviderOptions(providersResult.value.providers);
    if (statusResult.status === "fulfilled") setProviderStatus(statusResult.value);
    if (secretsResult.status === "fulfilled") {
      setSecrets(secretsResult.value);
      setSelectedSecretId(secretsResult.value[0]?.id || "");
    }
  }

  async function refreshDatasets() {
    const next = await listDatasets();
    setDatasets(next);
    return next;
  }

  async function selectDataset(nextId: string) {
    setDatasetId(nextId);
    if (!nextId) {
      setProfile(null);
      setProfileId("");
      setDataMessage(t("manualFallback"));
      return;
    }
    setDataBusy(true);
    try {
      const nextProfile = await getDatasetProfile(nextId);
      setProfile(nextProfile);
      setProfileId(nextProfile.profileId || nextId);
      setDataMessage(t("datasetProfileLoaded"));
    } catch {
      setProfile(null);
      setDataMessage(t("profileNotReady"));
    } finally {
      setDataBusy(false);
    }
  }

  async function handleLoadDemo() {
    setDataBusy(true);
    try {
      const demo = await loadDemoDataset();
      const nextDatasetId = demo.datasetId || demo.id;
      setDatasetId(nextDatasetId);
      setProjectId(demo.projectId || "project_local");
      setProfile(demo.profile);
      setProfileId(demo.profile.profileId || nextDatasetId);
      setPrompt(examplePrompts[0]);
      setProviderMode("mock");
      setDataMessage(t("demoLoaded"));
      await refreshDatasets();
      setDatasetDialogOpen(false);
    } catch (error) {
      setSubmitError(error as Error);
    } finally {
      setDataBusy(false);
    }
  }

  async function handleGenerateProfile() {
    if (!datasetId) {
      setDataMessage(t("emptyDataset"));
      return;
    }
    setDataBusy(true);
    try {
      const nextProfile = await createDatasetProfile(datasetId);
      setProfile(nextProfile);
      setProfileId(nextProfile.profileId || datasetId);
      setDataMessage(t("profileGenerated"));
    } catch (error) {
      setSubmitError(error as Error);
    } finally {
      setDataBusy(false);
    }
  }

  async function handleUploadFile(file: File | null) {
    if (!file) return;
    setDataBusy(true);
    try {
      const content = await file.text();
      const uploaded = await uploadDataset({
        projectId,
        datasetName: file.name.replace(/\.[^.]+$/, "") || file.name,
        files: [{ fileName: file.name, content }]
      });
      const nextDatasetId = uploaded.datasetId || uploaded.id;
      setDatasetId(nextDatasetId);
      if (uploaded.profile) {
        setProfile(uploaded.profile);
        setProfileId(uploaded.profile.profileId || nextDatasetId);
      }
      setDataMessage(t("uploadCompleted"));
      await refreshDatasets();
      setDatasetDialogOpen(false);
    } catch (error) {
      setSubmitError(error as Error);
    } finally {
      setDataBusy(false);
    }
  }

  async function handleSaveSecret() {
    if (!apiKey.trim()) return;
    const saved = await createSecret({
      provider: providerPreset,
      alias: secretAlias || `${providerPreset} API Key`,
      value: apiKey.trim()
    });
    setApiKey("");
    const nextSecrets = await listSecrets();
    setSecrets(nextSecrets);
    setSelectedSecretId(saved.id);
  }

  async function handleDeleteSecret() {
    if (!selectedSecretId) return;
    await deleteSecret(selectedSecretId);
    const nextSecrets = await listSecrets();
    setSecrets(nextSecrets);
    setSelectedSecretId(nextSecrets[0]?.id || "");
  }

  async function handleProviderTest() {
    setProviderResult(null);
    const result = await testPlannerProvider({
      provider: providerMode,
      baseUrl: providerMode === "openai_compatible" ? baseUrl : undefined,
      model: providerMode === "openai_compatible" ? model : undefined,
      secretId: providerMode === "openai_compatible" ? selectedSecretId : undefined,
      temperature,
      maxTokens,
      timeoutSeconds
    });
    setProviderResult(result);
  }

  async function refreshProviderResolution() {
    try {
      const result = await resolvePlannerProvider({
        provider: providerMode,
        baseUrl: providerMode === "openai_compatible" ? baseUrl : undefined,
        model: providerMode === "openai_compatible" ? model : undefined,
        secretId: providerMode === "openai_compatible" ? selectedSecretId : undefined,
        temperature,
        maxTokens,
        timeoutSeconds
      });
      setProviderResolution(result);
    } catch {
      setProviderResolution(null);
    }
  }

  async function handleSubmit() {
    setSubmitting(true);
    setSubmitError(null);
    setValidationFailure(null);
    setCreatedResult(null);
    setActiveMainTab("conversation_plan");
    if (!datasetId) {
      setSubmitting(false);
      setSubmitError(new Error(t("emptyDataset")));
      return;
    }
    try {
      const result = await createPlannerJob({
        userPrompt: prompt,
        projectId,
        datasetId,
        profileId: profileId || datasetId,
        enqueue: true,
        provider: providerMode,
        baseUrl: providerMode === "openai_compatible" ? baseUrl : undefined,
        model: providerMode === "openai_compatible" ? model : undefined,
        secretId: providerMode === "openai_compatible" ? selectedSecretId : undefined,
        temperature,
        maxTokens,
        timeoutSeconds
      });
      setCreatedResult(result);
      setSelectedChunkId(result.ok ? "plan_preview" : "validation_result");
      if (!result.ok) {
        setValidationFailure(result.validation_errors || []);
        setTimelineMode("idle");
        return;
      }
      const nextJobId = result.job_id || "";
      if (nextJobId) {
        const nextSnapshot = await refreshSnapshot(nextJobId);
        startEventSource(nextJobId, maxSeq(nextSnapshot.events));
      }
    } catch (error) {
      setSubmitError(error as Error);
    } finally {
      setSubmitting(false);
    }
  }

  async function refreshSnapshot(nextJobId: string): Promise<WorkspaceSnapshot> {
    const [job, events, toolCalls, artifacts, result] = await Promise.all([
      getPlannerJob(nextJobId),
      getPlannerJobEvents(nextJobId),
      getPlannerJobToolCalls(nextJobId),
      getPlannerJobArtifacts(nextJobId),
      getPlannerJobResult(nextJobId)
    ]);
    const nextSnapshot = { job, events, toolCalls, artifacts, result };
    setSnapshot(nextSnapshot);
    if (artifacts[0] && !selectedResultArtifactId) {
      setSelectedResultArtifactId(artifacts[0].artifactId || artifacts[0].id || "");
    }
    return nextSnapshot;
  }

  function startEventSource(nextJobId: string, afterSeq: number) {
    eventSourceRef.current?.close();
    const source = new EventSource(getPlannerJobEventsStreamUrl(nextJobId, afterSeq));
    eventSourceRef.current = source;
    setTimelineMode("sse");
    const handleEvent = (event: MessageEvent) => {
      const parsed = safeEvent(event.data);
      if (!parsed) return;
      setSnapshot((current) => {
        if (current.events.some((item) => item.id === parsed.id || item.seq === parsed.seq)) return current;
        return { ...current, events: [...current.events, parsed] };
      });
      if (parsed.eventType === "artifact.ready" && typeof parsed.payload?.artifactId === "string") {
        setSelectedResultArtifactId(parsed.payload.artifactId);
      }
      if (parsed.eventType === "job.completed" || parsed.eventType === "job.failed") {
        void refreshSnapshot(nextJobId);
      }
    };
    source.onmessage = handleEvent;
    [
      "plan.generated",
      "plan.persisted",
      "job.queued",
      "plan.loaded",
      "data.loaded",
      "tool.started",
      "tool.completed",
      "artifact.ready",
      "job.completed",
      "job.failed"
    ].forEach((type) => source.addEventListener(type, handleEvent));
    source.onerror = () => {
      source.close();
      setTimelineMode("polling");
    };
  }

  function handlePresetChange(next: ProviderPreset) {
    setProviderPreset(next);
    setBaseUrl(presetDefaults[next].baseUrl);
    setModel(presetDefaults[next].model);
  }

  function startResize(event: React.MouseEvent<HTMLButtonElement>) {
    event.preventDefault();
    const startX = event.clientX;
    const startWidth = leftPanelWidth;
    const onMove = (moveEvent: MouseEvent) => {
      setLeftPanelWidth(Math.min(520, Math.max(240, startWidth + moveEvent.clientX - startX)));
    };
    const onUp = () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  }

  return (
    <main
      className="planner-shell phase9c"
      data-testid="planner-workbench"
      aria-label="Analysis Planner workspace"
      data-phase1-shell-labels="Validated Plan Preview; Plan Provenance; Agent Timeline; Tool Calls; Artifact Gallery; Report / Recipe Summary; No deterministic fallback used"
    >
      <GlobalContextBar
        t={t}
        locale={locale}
        setLocale={setLocale}
        developerMode={developerMode}
        setDeveloperMode={setDeveloperMode}
        datasetLabel={selectedDataset?.name || datasetId || t("emptyDataset")}
        profileLabel={profileId || t("profileNotReady")}
        providerLabel={providerLabel}
        jobLabel={jobId ? `${jobId} · ${statusLabel(jobStatus, t)}` : t("emptyJob")}
        onOpenDataset={() => setDatasetDialogOpen(true)}
        onOpenModel={() => setModelDialogOpen(true)}
      />

      <section
        className={`phase9c-body ${leftPanelCollapsed ? "left-collapsed" : ""}`}
        style={{ gridTemplateColumns: leftPanelCollapsed ? "44px minmax(0, 1fr)" : `${leftPanelWidth}px 8px minmax(0, 1fr)` }}
      >
        <DataContextShell
          t={t}
          collapsed={leftPanelCollapsed}
          onToggle={() => setLeftPanelCollapsed((value) => !value)}
          profile={profile}
          profileId={profileId}
          datasetId={datasetId}
          dataset={selectedDataset}
          dataMessage={dataMessage}
          busy={dataBusy}
        />
        {!leftPanelCollapsed ? <button type="button" className="resize-handle" aria-label={t("resizeDataContext")} onMouseDown={startResize} /> : null}
        <MainWorkspaceTabs
          t={t}
          activeTab={activeMainTab}
          onTabChange={setActiveMainTab}
          agentTab={
            <AgentProcessTab
              t={t}
              events={snapshot.events}
              mode={timelineMode}
              planId={planId}
              planHash={planHash}
              health={health}
              providerStatus={providerStatus}
            />
          }
          conversationTab={
            <ConversationPlanTab
              t={t}
              prompt={prompt}
              setPrompt={setPrompt}
              examples={examplePrompts}
              providerLabel={providerLabel}
              datasetLabel={selectedDataset?.name || datasetId || t("emptyDataset")}
              submitting={submitting}
              onSubmit={handleSubmit}
              submitError={submitError}
              validationFailure={validationFailure}
              plan={plan}
              planId={planId}
              planHash={planHash}
              developerMode={developerMode}
              chunks={chunks}
              selectedChunkId={selectedChunkId}
              onSelectChunk={(chunk) => {
                setSelectedChunkId(chunk.id);
                setSelectedResultArtifactId(chunk.relatedArtifactIds[0] || selectedResultArtifactId);
              }}
              jobId={jobId}
              jobStatus={jobStatus}
              enqueued={createdResult?.enqueued}
            />
          }
          resultsTab={
            <ResultsExportTab
              t={t}
              selectedChunk={selectedChunk}
              selectedArtifact={selectedArtifact}
              artifacts={snapshot.artifacts}
              result={snapshot.result}
              job={snapshot.job}
              toolCalls={snapshot.toolCalls}
              datasetId={datasetId}
              profileId={profileId}
              planId={planId}
              planHash={planHash}
              developerMode={developerMode}
            />
          }
        />
      </section>

      {datasetDialogOpen ? (
        <DatasetCommandDialog
          t={t}
          projectId={projectId}
          setProjectId={setProjectId}
          datasetId={datasetId}
          setDatasetId={setDatasetId}
          profileId={profileId}
          setProfileId={setProfileId}
          datasets={datasets}
          profile={profile}
          dataMessage={dataMessage}
          busy={dataBusy}
          onDatasetSelect={selectDataset}
          onLoadDemo={handleLoadDemo}
          onGenerateProfile={handleGenerateProfile}
          onUploadFile={handleUploadFile}
          onClose={() => setDatasetDialogOpen(false)}
        />
      ) : null}

      {modelDialogOpen ? (
        <ModelProviderDialog
          t={t}
          providerMode={providerMode}
          setProviderMode={setProviderMode}
          providerPreset={providerPreset}
          onPresetChange={handlePresetChange}
          providerOptions={providerOptions}
          providerStatus={providerStatus}
          providerResolution={providerResolution}
          providerResult={providerResult}
          baseUrl={baseUrl}
          setBaseUrl={setBaseUrl}
          model={model}
          setModel={setModel}
          temperature={temperature}
          setTemperature={setTemperature}
          maxTokens={maxTokens}
          setMaxTokens={setMaxTokens}
          timeoutSeconds={timeoutSeconds}
          setTimeoutSeconds={setTimeoutSeconds}
          secretAlias={secretAlias}
          setSecretAlias={setSecretAlias}
          apiKey={apiKey}
          setApiKey={setApiKey}
          secrets={secrets}
          selectedSecretId={selectedSecretId}
          setSelectedSecretId={setSelectedSecretId}
          onSaveSecret={handleSaveSecret}
          onDeleteSecret={handleDeleteSecret}
          onTestProvider={handleProviderTest}
          onClose={() => setModelDialogOpen(false)}
        />
      ) : null}
    </main>
  );
}

function GlobalContextBar(props: {
  t: ReturnType<typeof createTranslator>;
  locale: Locale;
  setLocale: (locale: Locale) => void;
  developerMode: boolean;
  setDeveloperMode: (value: boolean) => void;
  datasetLabel: string;
  profileLabel: string;
  providerLabel: string;
  jobLabel: string;
  onOpenDataset: () => void;
  onOpenModel: () => void;
}) {
  const { t } = props;
  return (
    <header className="global-context-bar" data-testid="global-context-bar">
      <div className="brand-block">
        <span className="eyebrow">Material Data Intelligence</span>
        <h1>{t("title")}</h1>
      </div>
      <button type="button" className="context-button" onClick={props.onOpenDataset}>
        <span>{t("currentDataset")}</span>
        <strong>{props.datasetLabel}</strong>
        <small>{props.profileLabel}</small>
      </button>
      <button type="button" className="context-button" onClick={props.onOpenModel}>
        <span>{t("modelStatus")}</span>
        <strong>{props.providerLabel}</strong>
        <small>{t("providerDialogHint")}</small>
      </button>
      <div className="job-pill">
        <span>{t("currentJob")}</span>
        <strong>{props.jobLabel}</strong>
      </div>
      <div className="top-settings" aria-label={t("settings")}>
        <LanguageToggle locale={props.locale} setLocale={props.setLocale} t={t} />
        <button type="button" className="icon-button" aria-label={t("theme")}>
          ◐
        </button>
        <button type="button" className="icon-button" aria-label={t("userSettings")}>
          ⚙
        </button>
        <button type="button" className="icon-button" aria-label={t("help")}>
          ?
        </button>
        <label className="developer-toggle">
          <input type="checkbox" checked={props.developerMode} onChange={(event) => props.setDeveloperMode(event.target.checked)} />
          <span>{props.developerMode ? t("developerMode") : t("userMode")}</span>
        </label>
      </div>
    </header>
  );
}

function LanguageToggle({ locale, setLocale, t }: { locale: Locale; setLocale: (locale: Locale) => void; t: ReturnType<typeof createTranslator> }) {
  return (
    <div className="segmented" aria-label="Language">
      <button type="button" className={locale === "zh-CN" ? "active" : ""} onClick={() => setLocale("zh-CN")}>
        {t("languageChinese")}
      </button>
      <button type="button" className={locale === "en-US" ? "active" : ""} onClick={() => setLocale("en-US")}>
        {t("languageEnglish")}
      </button>
    </div>
  );
}

function DataContextShell(props: {
  t: ReturnType<typeof createTranslator>;
  collapsed: boolean;
  onToggle: () => void;
  profile: DataProfileSummary | null;
  profileId: string;
  datasetId: string;
  dataset?: DatasetOption;
  dataMessage: string;
  busy: boolean;
}) {
  const { t } = props;
  if (props.collapsed) {
    return (
      <aside className="data-context-collapsed" data-testid="data-context-viewer">
        <button type="button" className="collapse-button" onClick={props.onToggle} aria-label={t("expandDataContext")}>
          ›
        </button>
      </aside>
    );
  }
  return (
    <aside className="data-context-viewer" data-testid="data-context-viewer">
      <div className="section-heading">
        <h2>{t("dataContextViewer")}</h2>
        <button type="button" className="secondary compact" onClick={props.onToggle}>
          {t("collapse")}
        </button>
      </div>
      <p className="selector-status">{props.busy ? t("loadingDataContext") : props.dataMessage}</p>
      <dl className="mini-grid">
        <Field label={t("datasetId")} value={props.datasetId || t("emptyDataset")} />
        <Field label={t("profileId")} value={props.profileId || t("profileNotReady")} />
        <Field label={t("datasetType")} value={datasetKind(props.profile, t)} />
        <Field label={t("datasetStatus")} value={props.dataset?.status || props.profile?.status || t("unknown")} />
      </dl>
      <FormatAdaptiveProfile t={t} profile={props.profile} />
    </aside>
  );
}

function FormatAdaptiveProfile({ t, profile }: { t: ReturnType<typeof createTranslator>; profile: DataProfileSummary | null }) {
  if (!profile) {
    return <p className="empty-state">{t("emptyDataset")}</p>;
  }
  const columns = profile.tableSummary?.columns || [];
  const numericColumns = columns.filter((column) => column.dtype === "number").map((column) => column.name).filter(Boolean);
  const categoricalColumns = columns.filter((column) => column.dtype !== "number").map((column) => column.name).filter(Boolean);
  const formulaColumns = columns.filter((column) => column.inferredRole === "formula").map((column) => column.name).filter(Boolean);
  if (profile.tableSummary) {
    return (
      <section className="format-profile" data-format="table" data-testid="profile-summary">
        <h3>{t("tableData")}</h3>
        <dl className="mini-grid">
          <Field label={t("rowCount")} value={String(profile.tableSummary.nRows ?? 0)} />
          <Field label={t("columnCount")} value={String(profile.tableSummary.nColumns ?? columns.length)} />
          <Field label={t("numericColumns")} value={numericColumns.join(", ") || t("notConfigured")} />
          <Field label={t("categoricalColumns")} value={categoricalColumns.join(", ") || t("notConfigured")} />
          <Field label={t("formulaColumns")} value={formulaColumns.join(", ") || t("notConfigured")} />
          <Field label={t("fieldRoles")} value={columns.map((column) => `${column.name}:${column.inferredRole || "field"}`).join(", ")} />
        </dl>
        <div className="table-preview">
          {columns.slice(0, 8).map((column) => (
            <span key={column.name}>{column.name}</span>
          ))}
        </div>
      </section>
    );
  }
  if (profile.structureSummary?.nStructures) {
    return (
      <section className="format-profile" data-format="structure">
        <h3>{t("structureData")}</h3>
        <dl className="mini-grid">
          <Field label={t("structureCount")} value={String(profile.structureSummary.nStructures)} />
          <Field label={t("elements")} value={profile.structureSummary.elements?.join(", ") || t("notConfigured")} />
          <Field label={t("formulaCount")} value={String(profile.structureSummary.formulaStats?.total ?? 0)} />
          <Field label={t("uniqueFormulaCount")} value={String(profile.structureSummary.formulaStats?.uniqueCount ?? 0)} />
        </dl>
      </section>
    );
  }
  if (profile.objects?.length) {
    return (
      <section className="format-profile" data-format="archive">
        <h3>{t("archiveData")}</h3>
        <div className="list-stack">
          {profile.objects.map((object, index) => (
            <div className="list-row" key={`${object.objectType}-${index}`}>
              <strong>{object.objectType || t("unknown")}</strong>
              <span>{object.count ?? 0}</span>
            </div>
          ))}
        </div>
      </section>
    );
  }
  return (
    <section className="format-profile" data-format="unsupported">
      <h3>{t("unsupportedData")}</h3>
      <p>{t("unsupportedDataHint")}</p>
    </section>
  );
}

function DatasetCommandDialog(props: {
  t: ReturnType<typeof createTranslator>;
  projectId: string;
  setProjectId: (value: string) => void;
  datasetId: string;
  setDatasetId: (value: string) => void;
  profileId: string;
  setProfileId: (value: string) => void;
  datasets: DatasetOption[];
  profile: DataProfileSummary | null;
  dataMessage: string;
  busy: boolean;
  onDatasetSelect: (datasetId: string) => Promise<void>;
  onLoadDemo: () => Promise<void>;
  onGenerateProfile: () => Promise<void>;
  onUploadFile: (file: File | null) => Promise<void>;
  onClose: () => void;
}) {
  const { t } = props;
  return (
    <div className="dialog-backdrop" role="presentation">
      <section className="dialog-panel" role="dialog" aria-modal="true" aria-label={t("datasetDialogTitle")}>
        <DialogHeader title={t("datasetDialogTitle")} onClose={props.onClose} />
        <div className="dialog-grid">
          <div className="panel compact-panel">
            <label>
              {t("projectId")}
              <input value={props.projectId} onChange={(event) => props.setProjectId(event.target.value)} />
            </label>
            <label>
              {t("datasetSelector")}
              <select aria-label={t("datasetSelector")} value={props.datasetId} onChange={(event) => void props.onDatasetSelect(event.target.value)}>
                <option value="">{t("manualFallback")}</option>
                {props.datasets.map((dataset) => (
                  <option value={dataset.datasetId || dataset.id} key={dataset.datasetId || dataset.id}>
                    {dataset.name || dataset.datasetId || dataset.id}
                  </option>
                ))}
              </select>
            </label>
            <label>
              {t("datasetId")}
              <input aria-label={t("datasetId")} value={props.datasetId} onChange={(event) => props.setDatasetId(event.target.value)} />
            </label>
            <label>
              {t("profileId")}
              <input aria-label={t("profileId")} value={props.profileId} onChange={(event) => props.setProfileId(event.target.value)} />
            </label>
            <div className="button-row">
              <button type="button" onClick={props.onLoadDemo} disabled={props.busy}>
                {t("loadDemo")}
              </button>
              <button type="button" className="secondary" onClick={props.onGenerateProfile} disabled={props.busy}>
                {t("generateProfile")}
              </button>
              <label className="file-button">
                {t("uploadDataset")}
                <input type="file" onChange={(event) => void props.onUploadFile(event.currentTarget.files?.[0] || null)} />
              </label>
            </div>
            <p className="selector-status">{props.dataMessage}</p>
          </div>
          <div className="panel compact-panel">
            <PanelHeading title={t("profileSummary")} badge={props.profile?.profileId || t("profileNotReady")} />
            <FormatAdaptiveProfile t={t} profile={props.profile} />
          </div>
        </div>
      </section>
    </div>
  );
}

function ModelProviderDialog(props: {
  t: ReturnType<typeof createTranslator>;
  providerMode: "mock" | "openai_compatible";
  setProviderMode: (value: "mock" | "openai_compatible") => void;
  providerPreset: ProviderPreset;
  onPresetChange: (value: ProviderPreset) => void;
  providerOptions: ProviderOption[];
  providerStatus: ProviderStatus | null;
  providerResolution: ProviderResolveResult | null;
  providerResult: ProviderTestResult | null;
  baseUrl: string;
  setBaseUrl: (value: string) => void;
  model: string;
  setModel: (value: string) => void;
  temperature: number;
  setTemperature: (value: number) => void;
  maxTokens: number;
  setMaxTokens: (value: number) => void;
  timeoutSeconds: number;
  setTimeoutSeconds: (value: number) => void;
  secretAlias: string;
  setSecretAlias: (value: string) => void;
  apiKey: string;
  setApiKey: (value: string) => void;
  secrets: SecretSummary[];
  selectedSecretId: string;
  setSelectedSecretId: (value: string) => void;
  onSaveSecret: () => Promise<void>;
  onDeleteSecret: () => Promise<void>;
  onTestProvider: () => Promise<void>;
  onClose: () => void;
}) {
  const { t } = props;
  return (
    <div className="dialog-backdrop" role="presentation">
      <section className="dialog-panel" role="dialog" aria-modal="true" aria-label={t("modelDialogTitle")}>
        <DialogHeader title={t("modelDialogTitle")} onClose={props.onClose} />
        <div className="dialog-grid">
          <div className="panel compact-panel">
            <label>
              {t("providerMode")}
              <select aria-label={t("providerMode")} value={props.providerMode} onChange={(event) => props.setProviderMode(event.target.value as "mock" | "openai_compatible")}>
                <option value="mock">{t("mockPlanner")}</option>
                <option value="openai_compatible">{t("openaiCompatible")}</option>
              </select>
            </label>
            <label>
              {t("preset")}
              <select value={props.providerPreset} onChange={(event) => props.onPresetChange(event.target.value as ProviderPreset)}>
                <option value="openai">OpenAI</option>
                <option value="deepseek">DeepSeek</option>
                <option value="custom">{t("customOpenAI")}</option>
              </select>
            </label>
            <label>
              {t("baseUrl")}
              <input value={props.baseUrl} onChange={(event) => props.setBaseUrl(event.target.value)} />
            </label>
            <label>
              {t("model")}
              <input value={props.model} onChange={(event) => props.setModel(event.target.value)} />
            </label>
            <div className="triple-grid">
              <label>
                {t("temperature")}
                <input type="number" step="0.1" value={props.temperature} onChange={(event) => props.setTemperature(Number(event.target.value))} />
              </label>
              <label>
                {t("maxTokens")}
                <input type="number" value={props.maxTokens} onChange={(event) => props.setMaxTokens(Number(event.target.value))} />
              </label>
              <label>
                {t("timeout")}
                <input type="number" value={props.timeoutSeconds} onChange={(event) => props.setTimeoutSeconds(Number(event.target.value))} />
              </label>
            </div>
            <p className="selector-status">{props.providerResolution?.message || t("emptyProvider")}</p>
            <small>
              Default service provider: {props.providerStatus?.provider || "unknown"} / {props.providerStatus?.status || "unknown"}
            </small>
          </div>
          <div className="panel compact-panel">
            <PanelHeading title={t("savedSecret")} badge={t("providerNotice")} />
            <label>
              {t("secretAlias")}
              <input value={props.secretAlias} onChange={(event) => props.setSecretAlias(event.target.value)} />
            </label>
            <label>
              {t("apiKey")}
              <input aria-label={t("apiKey")} type="password" value={props.apiKey} onChange={(event) => props.setApiKey(event.target.value)} />
            </label>
            <label>
              {t("savedSecret")}
              <select value={props.selectedSecretId} onChange={(event) => props.setSelectedSecretId(event.target.value)}>
                <option value="">{t("notConfigured")}</option>
                {props.secrets.map((secret) => (
                  <option value={secret.id} key={secret.id}>
                    {secret.alias || secret.id} · {secret.maskedPreview || "********"}
                  </option>
                ))}
              </select>
            </label>
            <div className="button-row">
              <button type="button" onClick={props.onSaveSecret}>
                {t("saveSecret")}
              </button>
              <button type="button" className="secondary" onClick={props.onDeleteSecret}>
                {t("deleteSecret")}
              </button>
              <button type="button" className="secondary" onClick={props.onTestProvider}>
                {t("testConnection")}
              </button>
            </div>
            {props.providerResult ? (
              <div className={props.providerResult.ok ? "success-card" : "error-card"} data-testid="provider-test-result">
                <strong>{props.providerResult.message}</strong>
                {props.providerResult.safeDetails ? <small>{props.providerResult.safeDetails}</small> : null}
              </div>
            ) : null}
            {props.providerOptions.length ? <small>{props.providerOptions.map((provider) => provider.label).join(" / ")}</small> : null}
          </div>
        </div>
      </section>
    </div>
  );
}

function DialogHeader({ title, onClose }: { title: string; onClose: () => void }) {
  return (
    <div className="dialog-header">
      <h2>{title}</h2>
      <button type="button" className="secondary compact" onClick={onClose}>
        ×
      </button>
    </div>
  );
}

function MainWorkspaceTabs(props: {
  t: ReturnType<typeof createTranslator>;
  activeTab: MainWorkspaceTab;
  onTabChange: (tab: MainWorkspaceTab) => void;
  agentTab: ReactNode;
  conversationTab: ReactNode;
  resultsTab: ReactNode;
}) {
  const tabs: Array<[MainWorkspaceTab, string]> = [
    ["agent_process", props.t("agentProcessTab")],
    ["conversation_plan", props.t("conversationPlanTab")],
    ["results_export", props.t("resultsExportTab")]
  ];
  return (
    <section className="main-workspace" data-testid="main-workspace">
      <nav className="main-tab-list" aria-label={props.t("mainWorkspaceTabs")}>
        {tabs.map(([id, label]) => (
          <button key={id} type="button" className={props.activeTab === id ? "active" : ""} onClick={() => props.onTabChange(id)}>
            {label}
          </button>
        ))}
      </nav>
      <div className="main-tab-surface" data-active-tab={props.activeTab}>
        {props.activeTab === "agent_process" ? props.agentTab : null}
        {props.activeTab === "conversation_plan" ? props.conversationTab : null}
        {props.activeTab === "results_export" ? props.resultsTab : null}
      </div>
    </section>
  );
}

function AgentProcessTab(props: {
  t: ReturnType<typeof createTranslator>;
  events: JobEvent[];
  mode: "sse" | "polling" | "idle";
  planId: string;
  planHash: string;
  health: RuntimeHealth | null;
  providerStatus: ProviderStatus | null;
}) {
  const { t } = props;
  return (
    <div className="tab-grid agent-process-tab" data-testid="agent-process-tab">
      <section className="panel">
        <PanelHeading title={t("agentProcessTab")} badge={props.mode === "sse" ? t("ssePath") : props.mode === "polling" ? t("pollingFallback") : t("emptyTimeline")} />
        {!props.events.length ? <p className="empty-state">{t("emptyTimeline")}</p> : null}
        <ol className="timeline-list">
          {props.events.map((event) => (
            <li key={event.id || event.seq} className={`timeline-item ${event.eventType === "plan.loaded" ? "important" : ""}`}>
              <time>{formatTime(event.createdAt)}</time>
              <span>{timelineLabel(event.eventType, t)}</span>
              <strong>{event.status}</strong>
              <p>{event.message}</p>
              <details>
                <summary>{t("safePayload")}</summary>
                <pre>{JSON.stringify(redactPayload(event), null, 2)}</pre>
              </details>
            </li>
          ))}
        </ol>
      </section>
      <section className="panel">
        <PanelHeading title={t("provenance")} badge={props.planId || t("emptyProvenance")} />
        <dl className="mini-grid">
          <Field label="job.plan_id" value={props.planId || t("emptyProvenance")} />
          <Field label="planHash" value={props.planHash || t("emptyProvenance")} />
          <Field label="binding" value="jobs.plan_id -> analysis_plans.id" />
          <Field label="source" value="persisted_analysis_plan" />
        </dl>
        <div className="provenance-flags">
          <span>{t("loadedPersistedPlan")}</span>
          <span>{t("toolRegistryAdapter")}</span>
          <span>{t("noFallback")}</span>
        </div>
      </section>
      <SystemHealthPanel t={t} health={props.health} providerStatus={props.providerStatus} />
    </div>
  );
}

function ConversationPlanTab(props: {
  t: ReturnType<typeof createTranslator>;
  prompt: string;
  setPrompt: (value: string) => void;
  examples: string[];
  providerLabel: string;
  datasetLabel: string;
  submitting: boolean;
  onSubmit: () => Promise<void>;
  submitError: PlannerApiError | Error | null;
  validationFailure: ValidationError[] | null;
  plan: AnalysisPlan | null;
  planId: string;
  planHash: string;
  developerMode: boolean;
  chunks: ConversationChunk[];
  selectedChunkId: string;
  onSelectChunk: (chunk: ConversationChunk) => void;
  jobId: string;
  jobStatus: string;
  enqueued?: boolean;
}) {
  const { t } = props;
  return (
    <div className="conversation-plan-tab" data-testid="conversation-plan-tab">
      <section className="panel prompt-panel" data-testid="planner-form">
        <PanelHeading title={t("promptTitle")} badge={props.providerLabel} />
        <textarea aria-label={t("promptTitle")} value={props.prompt} onChange={(event) => props.setPrompt(event.target.value)} placeholder={t("promptPlaceholder")} />
        <div className="prompt-examples">
          {props.examples.map((example) => (
            <button key={example} type="button" className="secondary" onClick={() => props.setPrompt(example)}>
              {t("examplePrompt")}
            </button>
          ))}
        </div>
        <p className="subtle">
          {props.providerLabel} · {props.datasetLabel}
        </p>
        <button type="button" onClick={props.onSubmit} disabled={props.submitting}>
          {props.submitting ? t("submitting") : t("createAndRun")}
        </button>
      </section>
      {props.submitError ? <ErrorExplainer t={t} error={props.submitError} /> : null}
      {props.validationFailure ? <ValidationResultPanel t={t} errors={props.validationFailure} /> : null}
      <section className="chunk-list-panel" data-testid="conversation-chunks">
        <PanelHeading title={t("conversationChunks")} badge={String(props.chunks.length)} />
        <div className="chunk-list">
          {props.chunks.map((chunk) => (
            <button
              key={chunk.id}
              type="button"
              className={`conversation-chunk ${props.selectedChunkId === chunk.id ? "selected" : ""} status-${chunk.status}`}
              onClick={() => props.onSelectChunk(chunk)}
            >
              <span>{chunkLabel(chunk.kind, t)}</span>
              <strong>{chunk.title}</strong>
              <small>{chunk.summary}</small>
            </button>
          ))}
        </div>
      </section>
      <PlanPreviewPanel t={t} plan={props.plan} planId={props.planId} planHash={props.planHash} developerMode={props.developerMode} />
      <RunControls t={t} jobId={props.jobId} planId={props.planId} planHash={props.planHash} enqueued={props.enqueued} status={props.jobStatus} onRun={props.onSubmit} submitting={props.submitting} />
    </div>
  );
}

function ResultsExportTab(props: {
  t: ReturnType<typeof createTranslator>;
  selectedChunk?: ConversationChunk;
  selectedArtifact?: Artifact;
  artifacts: Artifact[];
  result?: JobResult;
  job?: PlannerJobDetail;
  toolCalls: ToolCall[];
  datasetId: string;
  profileId: string;
  planId: string;
  planHash: string;
  developerMode: boolean;
}) {
  const { t } = props;
  if (!props.selectedChunk) {
    return (
      <section className="panel" data-testid="results-export-tab">
        <PanelHeading title={t("resultsExportTab")} badge={t("emptyResultSelection")} />
        <p className="empty-state">{t("emptyResultSelection")}</p>
      </section>
    );
  }
  const hasResults = Boolean(props.result || props.artifacts.length || props.toolCalls.length);
  return (
    <div className="results-export-tab" data-testid="results-export-tab">
      <section className="panel selected-result-header">
        <PanelHeading title={t("selectedResultContext")} badge={props.selectedChunk.title} />
        <dl className="mini-grid">
          <Field label="chunk" value={props.selectedChunk.id} />
          <Field label="jobId" value={props.result?.jobId || props.job?.jobId || t("emptyJob")} />
          <Field label="planId" value={props.planId || t("emptyProvenance")} />
          <Field label="planHash" value={props.planHash || t("emptyProvenance")} />
        </dl>
      </section>
      {!hasResults ? (
        <section className="panel">
          <p className="empty-state">{t("emptyResultsForChunk")}</p>
        </section>
      ) : null}
      <ReportRecipeSummaryPanel t={t} result={props.result} artifacts={props.artifacts} datasetId={props.datasetId} profileId={props.profileId} planId={props.planId} planHash={props.planHash} />
      <MaterialResultRenderer t={t} artifacts={props.artifacts} />
      <MetricsResultRenderer t={t} artifact={props.artifacts.find((artifact) => artifact.type === "metrics_json")} />
      <TableSummaryRenderer t={t} artifact={props.artifacts.find(isTableSummaryArtifact)} />
      <ArtifactGallery t={t} artifacts={props.artifacts} developerMode={props.developerMode} selectedArtifact={props.selectedArtifact} />
      <ToolCallList t={t} toolCalls={props.toolCalls} developerMode={props.developerMode} />
      <ExportControls t={t} artifacts={props.artifacts} />
    </div>
  );
}

function PlanPreviewPanel({ t, plan, planId, planHash, developerMode }: { t: ReturnType<typeof createTranslator>; plan: AnalysisPlan | null; planId: string; planHash: string; developerMode: boolean }) {
  const steps = plan?.steps || [];
  return (
    <section className="panel" data-testid="plan-preview-panel">
      <PanelHeading title={t("planPreview")} badge={steps.length ? `${steps.length} steps` : t("emptyPlan")} />
      {!steps.length ? <p className="empty-state">{t("emptyPlan")}</p> : null}
      <div className="step-list">
        {steps.map((step, index) => (
          <article key={step.stepId} className="step-row">
            <div>
              <strong>
                {t("step")} {index + 1}: {step.purpose || step.reason || step.stepId}
              </strong>
              <span>{toolDisplayName(step.toolId, t)}</span>
            </div>
            <p>
              {t("inputCurrentTable")} · {t("output")}: {step.output?.artifactTypes?.join(", ") || "artifact"}
            </p>
            {developerMode ? (
              <dl className="mini-grid">
                <Field label="stepId" value={step.stepId} />
                <Field label="toolId" value={step.toolId} />
                <Field label="params" value={JSON.stringify(step.params || {})} />
                <Field label="inputRefs" value={JSON.stringify(step.inputRefs || [])} />
              </dl>
            ) : null}
          </article>
        ))}
      </div>
      {developerMode ? (
        <details className="raw-json">
          <summary>raw AnalysisPlan JSON</summary>
          <pre>{JSON.stringify({ planId, planHash, plan }, null, 2)}</pre>
        </details>
      ) : null}
    </section>
  );
}

function ValidationResultPanel({ t, errors }: { t: ReturnType<typeof createTranslator>; errors: ValidationError[] }) {
  return (
    <section className="validation-failure" data-testid="validation-failure">
      <h2>{t("validationFailed")}</h2>
      <ul>
        <li>{t("noPlanSaved")}</li>
        <li>{t("noJobCreated")}</li>
        <li>{t("nothingEnqueued")}</li>
        <li>{t("fixAndRetry")}</li>
      </ul>
      <div className="list-stack">
        {errors.map((error, index) => (
          <div className="list-row" key={`${error.code || "error"}-${index}`}>
            <strong>{error.code || "VALIDATION_ERROR"}</strong>
            <small>{error.message || JSON.stringify(error.detail || error.details || {})}</small>
          </div>
        ))}
      </div>
    </section>
  );
}

function RunControls(props: { t: ReturnType<typeof createTranslator>; jobId: string; planId: string; planHash: string; enqueued?: boolean; status: string; submitting: boolean; onRun: () => Promise<void> }) {
  const { t } = props;
  return (
    <section className="panel" data-testid="run-controls">
      <PanelHeading title={t("runControls")} badge={statusLabel(props.status, t)} />
      <dl className="mini-grid">
        <Field label="jobId" value={props.jobId || t("emptyJob")} />
        <Field label="planId" value={props.planId || t("emptyProvenance")} />
        <Field label="planHash" value={props.planHash || t("emptyProvenance")} />
        <Field label="enqueued" value={String(Boolean(props.enqueued))} />
      </dl>
      <button type="button" onClick={props.onRun} disabled={props.submitting}>
        {props.submitting ? t("submitting") : t("createAndRun")}
      </button>
    </section>
  );
}

function SystemHealthPanel({ t, health, providerStatus }: { t: ReturnType<typeof createTranslator>; health: RuntimeHealth | null; providerStatus: ProviderStatus | null }) {
  const entries = health
    ? [
        [t("apiService"), health.api],
        [t("database"), health.database],
        [t("redisQueue"), health.redis],
        [t("artifactStorage"), health.artifactStorage],
        ["Worker", health.worker],
        ["LLM Provider", health.llmProvider]
      ]
    : [];
  return (
    <section className="panel" data-testid="system-health-panel">
      <PanelHeading title={t("systemStatus")} badge={providerStatus?.status || t("unknown")} />
      {!entries.length ? <p className="empty-state">{t("emptyHealth")}</p> : null}
      <div className="health-list">
        {entries.map(([label, item]) => (
          <div className="health-row" key={label as string}>
            <strong>{label as string}</strong>
            <span>{statusText((item as { status?: string }).status, t)}</span>
            {(item as { reason?: string }).reason ? <small>{(item as { reason?: string }).reason}</small> : null}
          </div>
        ))}
      </div>
    </section>
  );
}

function MaterialResultRenderer({ t, artifacts }: { t: ReturnType<typeof createTranslator>; artifacts: Artifact[] }) {
  const structureArtifact = artifacts.find((artifact) => String(artifact.type).includes("matterviz") || String(artifact.type).includes("structure"));
  return (
    <section className="panel" data-testid="material-result-renderer">
      <PanelHeading title={t("materialResult")} badge={structureArtifact?.name || t("emptyMaterialResult")} />
      <p className="empty-state">{structureArtifact ? t("materialResultReady") : t("emptyMaterialResult")}</p>
    </section>
  );
}

function MetricsResultRenderer({ t, artifact }: { t: ReturnType<typeof createTranslator>; artifact?: Artifact }) {
  return (
    <section className="panel" data-testid="metrics-result-renderer">
      <PanelHeading title={t("metricsResult")} badge={artifact?.name || t("emptyMetrics")} />
      <p className="empty-state">{artifact ? t("metricsResultReady") : t("emptyMetrics")}</p>
    </section>
  );
}

function TableSummaryRenderer({ t, artifact }: { t: ReturnType<typeof createTranslator>; artifact?: Artifact }) {
  return (
    <section className="panel" data-testid="table-summary-renderer">
      <PanelHeading title={t("tableSummaryResult")} badge={artifact?.name || t("emptyTableSummary")} />
      <p className="empty-state">{artifact ? t("tableSummaryReady") : t("emptyTableSummary")}</p>
    </section>
  );
}

function ArtifactGallery({ t, artifacts, developerMode, selectedArtifact }: { t: ReturnType<typeof createTranslator>; artifacts: Artifact[]; developerMode: boolean; selectedArtifact?: Artifact }) {
  const groups = groupArtifacts(artifacts, t);
  return (
    <section className="panel" data-testid="artifacts-panel">
      <PanelHeading title={t("artifacts")} badge={selectedArtifact?.name || `${artifacts.length}`} />
      {!artifacts.length ? <p className="empty-state">{t("emptyArtifacts")}</p> : null}
      {groups.map((group) => (
        <div key={group.label} className="artifact-group">
          <h3>{group.label}</h3>
          <div className="artifact-grid">
            {group.items.map((artifact) => (
              <article className="artifact-card" key={artifact.artifactId || artifact.id}>
                <strong>{artifact.name || artifact.artifactId || artifact.id}</strong>
                <span>{artifact.type}</span>
                <small>{artifact.toolCallId || "system"}</small>
                <div className="button-row">
                  <button type="button" className="secondary">
                    {t("preview")}
                  </button>
                  <button type="button" className="secondary">
                    {t("download")}
                  </button>
                </div>
                {developerMode ? (
                  <dl className="mini-grid">
                    <Field label="artifactId" value={artifact.artifactId || artifact.id || ""} />
                    <Field label="planId" value={artifact.planId || ""} />
                    <Field label="planHash" value={artifact.planHash || ""} />
                    <Field label="storage URI" value={artifact.storageKey || ""} />
                  </dl>
                ) : null}
              </article>
            ))}
          </div>
        </div>
      ))}
    </section>
  );
}

function ReportRecipeSummaryPanel(props: { t: ReturnType<typeof createTranslator>; result?: JobResult; artifacts: Artifact[]; datasetId: string; profileId: string; planId: string; planHash: string }) {
  const reportArtifacts = props.artifacts.filter((artifact) => ["summary_md", "report_md", "report_html"].includes(String(artifact.type)));
  const recipeArtifacts = props.artifacts.filter((artifact) => artifact.type === "recipe_json");
  return (
    <section className="panel" data-testid="report-recipe-panel">
      <PanelHeading title={props.t("reportRecipe")} badge={props.t("systemGeneratedSummary")} />
      <div className="summary-box">
        <h3>{props.t("reportSummaryTitle")}</h3>
        <p>{props.result?.summary || props.t("emptyReport")}</p>
        <ul>
          <li>{props.t("reportDidWhat")}</li>
          <li>
            {props.t("reportGeneratedPrefix")} {props.artifacts.length} {props.t("artifactCountUnit")}, {props.result?.toolCallCount ?? 0} {props.t("toolCallCountUnit")}.
          </li>
          <li>{props.t("reportKeyMetrics")}</li>
          <li>{props.t("reportNotes")}</li>
        </ul>
      </div>
      <div className="summary-box">
        <h3>{props.t("recipeTitle")}</h3>
        <dl className="mini-grid">
          <Field label="Dataset" value={props.datasetId || props.t("emptyDataset")} />
          <Field label="Profile" value={props.profileId || props.t("emptyDataset")} />
          <Field label="AnalysisPlan" value={props.planId || props.t("emptyProvenance")} />
          <Field label="planHash" value={props.planHash || props.t("emptyProvenance")} />
          <Field label="Reports" value={reportArtifacts.map((artifact) => artifact.name).join(", ") || props.t("emptyReport")} />
          <Field label="Recipes" value={recipeArtifacts.map((artifact) => artifact.name).join(", ") || props.t("emptyReport")} />
        </dl>
      </div>
    </section>
  );
}

function ToolCallList({ t, toolCalls, developerMode }: { t: ReturnType<typeof createTranslator>; toolCalls: ToolCall[]; developerMode: boolean }) {
  return (
    <section className="panel" data-testid="toolcalls-panel">
      <PanelHeading title={t("toolCalls")} badge={`${toolCalls.length}`} />
      {!toolCalls.length ? <p className="empty-state">{t("emptyToolCalls")}</p> : null}
      <div className="list-stack">
        {toolCalls.map((toolCall) => (
          <article key={toolCall.id} className="list-row">
            <div>
              <strong>{toolCall.toolId}</strong>
              <span>{toolCall.status}</span>
            </div>
            <dl className="mini-grid">
              <Field label="stepId" value={toolCall.stepId || ""} />
              <Field label="planId" value={toolCall.planId || ""} />
              <Field label="planHash" value={toolCall.planHash || ""} />
              <Field label="input" value={toolCall.inputSummary || ""} />
            </dl>
            {developerMode ? <pre>{JSON.stringify(toolCall, null, 2)}</pre> : null}
          </article>
        ))}
      </div>
    </section>
  );
}

function ExportControls({ t, artifacts }: { t: ReturnType<typeof createTranslator>; artifacts: Artifact[] }) {
  return (
    <section className="panel" data-testid="export-controls">
      <PanelHeading title={t("exportControls")} badge={`${artifacts.length}`} />
      <div className="button-row">
        <button type="button" className="secondary">
          {t("exportReport")}
        </button>
        <button type="button" className="secondary">
          {t("downloadArtifacts")}
        </button>
      </div>
    </section>
  );
}

function ErrorExplainer({ t, error }: { t: ReturnType<typeof createTranslator>; error: PlannerApiError | Error }) {
  const apiError = error as PlannerApiError;
  const suggestions = apiError.suggestions?.length ? apiError.suggestions : [t("suggestionDataset"), t("suggestionDemo"), t("suggestionProfile"), t("suggestionProvider")];
  return (
    <section className="error-explainer" data-testid="error-explainer">
      <h2>{t("errorTitle")}</h2>
      <div>
        <strong>{t("possibleReasons")}：</strong>
        <ol>
          <li>{t("reasonDataset")}</li>
          <li>{t("reasonProfile")}</li>
          <li>{t("reasonProvider")}</li>
          <li>{t("reasonApi")}</li>
        </ol>
      </div>
      <p>
        <strong>{t("details")}：</strong>
        {error.message}
      </p>
      {apiError.safeDetails ? <p>{apiError.safeDetails}</p> : null}
      <div>
        <strong>{t("suggestions")}：</strong>
        <ul>
          {suggestions.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}

function PanelHeading({ title, badge }: { title: string; badge?: string }) {
  return (
    <div className="section-heading">
      <h2>{title}</h2>
      {badge ? <span>{badge}</span> : null}
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}

function buildConversationChunks(input: {
  t: ReturnType<typeof createTranslator>;
  prompt: string;
  plan: AnalysisPlan | null;
  createdResult: PlannerJobCreateResult | null;
  validationFailure: ValidationError[] | null;
  jobId: string;
  jobStatus: string;
  artifacts: Artifact[];
}): ConversationChunk[] {
  const chunks: ConversationChunk[] = [
    {
      id: "user_request",
      kind: "user_request",
      title: input.t("userRequestChunk"),
      summary: input.prompt,
      status: "idle",
      relatedArtifactIds: []
    }
  ];
  if (input.plan?.steps?.length) {
    chunks.push({
      id: "plan_preview",
      kind: "plan_preview",
      title: input.t("planPreview"),
      summary: `${input.plan.steps.length} step(s): ${input.plan.steps.map((step) => step.toolId).join(", ")}`,
      status: "success",
      relatedStepId: input.plan.steps[0]?.stepId,
      relatedArtifactIds: input.artifacts.map((artifact) => artifact.artifactId || artifact.id || "").filter(Boolean)
    });
  }
  if (input.validationFailure) {
    chunks.push({
      id: "validation_result",
      kind: "validation_result",
      title: input.t("validationFailed"),
      summary: input.validationFailure.map((error) => error.code || error.message).join(", "),
      status: "error",
      relatedArtifactIds: []
    });
  }
  if (input.createdResult?.ok) {
    chunks.push({
      id: "run_status",
      kind: "run_status",
      title: input.t("runControls"),
      summary: `${input.jobId || input.t("emptyJob")} · ${input.jobStatus || input.t("queued")}`,
      status: input.jobStatus === "completed" ? "success" : "running",
      relatedArtifactIds: input.artifacts.map((artifact) => artifact.artifactId || artifact.id || "").filter(Boolean)
    });
  }
  if (input.artifacts.length) {
    chunks.push({
      id: "result_reference",
      kind: "result_reference",
      title: input.t("resultsExportTab"),
      summary: `${input.artifacts.length} ${input.t("artifactCountUnit")}`,
      status: "success",
      relatedArtifactIds: input.artifacts.map((artifact) => artifact.artifactId || artifact.id || "").filter(Boolean)
    });
  }
  return chunks;
}

function maxSeq(events: JobEvent[]) {
  return events.reduce((max, event) => Math.max(max, Number(event.seq || 0)), 0);
}

function safeEvent(value: string): JobEvent | null {
  try {
    return JSON.parse(value) as JobEvent;
  } catch {
    return null;
  }
}

function redactPayload(event: JobEvent) {
  return {
    ...event,
    payload: event.payload ? redactObject(event.payload) : {}
  };
}

function redactObject(value: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(value).map(([key, entry]) => {
      if (/key|secret|token|authorization/i.test(key)) {
        return [key, "[redacted]"];
      }
      return [key, entry];
    })
  );
}

function formatTime(value?: string) {
  return value ? new Date(value).toLocaleTimeString() : "";
}

function timelineLabel(type: string | undefined, t: ReturnType<typeof createTranslator>) {
  const labels: Record<string, MessageKey> = {
    "plan.generated": "timelinePlanGenerated",
    "plan.persisted": "timelinePlanPersisted",
    "job.queued": "timelineJobQueued",
    "plan.loaded": "timelinePlanLoaded",
    "data.loaded": "timelineDataLoaded",
    "tool.started": "timelineToolStarted",
    "tool.completed": "timelineToolCompleted",
    "artifact.ready": "timelineArtifactReady",
    "job.completed": "timelineJobCompleted",
    "job.failed": "timelineJobFailed"
  };
  const key = labels[type || ""];
  return key ? t(key) : type || "event";
}

function chunkLabel(type: ChunkKind, t: ReturnType<typeof createTranslator>) {
  const labels: Record<ChunkKind, MessageKey> = {
    user_request: "userRequestChunk",
    plan_preview: "planPreviewChunk",
    validation_result: "validationChunk",
    run_status: "runChunk",
    result_reference: "resultChunk"
  };
  return t(labels[type]);
}

function statusLabel(status: string | undefined, t: ReturnType<typeof createTranslator>) {
  if (!status) return t("unknown");
  if (status === "completed") return t("completed");
  if (status === "queued") return t("queued");
  if (status === "running") return t("running");
  if (status === "failed") return t("failed");
  return status;
}

function statusText(status: string | undefined, t: ReturnType<typeof createTranslator>) {
  if (status === "ok") return t("ok");
  if (status === "ready") return t("ready");
  if (status === "unknown") return t("unknown");
  return status || t("unknown");
}

function toolDisplayName(toolId: string, t: ReturnType<typeof createTranslator>) {
  if (toolId === "ml.basic_metrics") return t("toolBasicMetrics");
  if (toolId === "table.numeric_summary") return t("toolNumericSummary");
  if (toolId === "table.distribution_summary") return "Distribution summary";
  if (toolId === "viz.scatter") return "Scatter plot";
  if (toolId === "viz.histogram") return "Histogram";
  if (toolId === "viz.correlation") return "Correlation matrix";
  if (toolId === "composition.summary") return "Composition summary";
  if (toolId === "composition.ptable_heatmap") return t("toolElementHeatmap");
  if (toolId === "structure.viewer_3d") return t("toolStructureViewer");
  return toolId;
}

function datasetKind(profile: DataProfileSummary | null, t: ReturnType<typeof createTranslator>) {
  if (!profile) return t("unknown");
  if (profile.tableSummary) return t("tableData");
  if (profile.structureSummary?.nStructures) return t("structureData");
  if (profile.objects?.length) return t("archiveData");
  return profile.datasetType || t("unknown");
}

function groupArtifacts(artifacts: Artifact[], t: ReturnType<typeof createTranslator>) {
  const groups: Record<string, Artifact[]> = {
    [t("charts")]: [],
    [t("jsonMetrics")]: [],
    [t("tables")]: [],
    [t("structures")]: [],
    [t("reports")]: [],
    [t("other")]: []
  };
  for (const artifact of artifacts) {
    const type = String(artifact.type || "");
    if (type.includes("plot") || type.includes("plotly") || type.includes("figure") || type.includes("png") || type.includes("svg")) groups[t("charts")].push(artifact);
    else if (type === "metrics_json") groups[t("jsonMetrics")].push(artifact);
    else if (isTableSummaryArtifact(artifact)) groups[t("tables")].push(artifact);
    else if (type.includes("structure") || type.includes("matterviz")) groups[t("structures")].push(artifact);
    else if (type.includes("summary") || type.includes("report") || type.includes("recipe")) groups[t("reports")].push(artifact);
    else groups[t("other")].push(artifact);
  }
  return Object.entries(groups)
    .filter(([, items]) => items.length)
    .map(([label, items]) => ({ label, items }));
}

function isTableSummaryArtifact(artifact: Artifact) {
  const type = String(artifact.type || "");
  const name = String(artifact.name || "");
  return type === "table_json" || name.includes("distribution_summary") || name.includes("numeric_summary") || name.includes("correlation_matrix") || name.includes("composition_summary");
}
