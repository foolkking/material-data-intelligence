"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { createTranslator, type Locale } from "../lib/i18n";
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
  testPlannerProvider,
  uploadDataset
} from "../lib/planner-api";

type TabId = "overview" | "artifacts" | "report" | "toolcalls" | "audit";

type WorkspaceSnapshot = {
  job?: PlannerJobDetail;
  events: JobEvent[];
  toolCalls: ToolCall[];
  artifacts: Artifact[];
  result?: JobResult;
};

type ProviderPreset = "openai" | "deepseek" | "custom";

const examplePrompts = [
  "请计算 y_true 和 y_pred 的基础误差指标，并生成报告摘要。",
  "请统计材料组成中的元素分布。",
  "请找出预测误差最大的样本。",
  "请基于当前结构数据生成 3D 可视化。"
];

const presetDefaults: Record<ProviderPreset, { baseUrl: string; model: string }> = {
  openai: { baseUrl: "https://api.openai.com/v1", model: "gpt-4o" },
  deepseek: { baseUrl: "https://api.deepseek.com/v1", model: "deepseek-chat" },
  custom: { baseUrl: "", model: "" }
};

export function PlannerWorkbench() {
  const [locale, setLocale] = useState<Locale>("zh-CN");
  const t = useMemo(() => createTranslator(locale), [locale]);
  const [developerMode, setDeveloperMode] = useState(false);
  const [activeTab, setActiveTab] = useState<TabId>("overview");

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

  const [prompt, setPrompt] = useState(examplePrompts[0]);
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
    if (healthResult.status === "fulfilled") {
      setHealth(healthResult.value);
    }
    if (datasetResult.status === "fulfilled") {
      setDatasets(datasetResult.value);
    }
    if (providersResult.status === "fulfilled") {
      setProviderOptions(providersResult.value.providers);
    }
    if (statusResult.status === "fulfilled") {
      setProviderStatus(statusResult.value);
    }
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
      setDataMessage(locale === "zh-CN" ? "已从后端加载 Dataset/Profile" : "Dataset/profile loaded from API");
    } catch (error) {
      setProfile(null);
      setDataMessage(locale === "zh-CN" ? "Profile 尚未生成，可手动输入或点击生成。" : "Profile is not ready. Use manual fallback or generate it.");
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
      setDataMessage(locale === "zh-CN" ? "已加载服务端 Demo 数据。" : "Backend demo dataset loaded.");
      await refreshDatasets();
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
      setDataMessage(locale === "zh-CN" ? "Profile 已生成。" : "Profile generated.");
    } catch (error) {
      setSubmitError(error as Error);
    } finally {
      setDataBusy(false);
    }
  }

  async function handleUploadFile(file: File | null) {
    if (!file) {
      return;
    }
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
      setDataMessage(locale === "zh-CN" ? "上传完成并生成 Profile。" : "Upload completed and Profile generated.");
      await refreshDatasets();
    } catch (error) {
      setSubmitError(error as Error);
    } finally {
      setDataBusy(false);
    }
  }

  async function handleSaveSecret() {
    if (!apiKey.trim()) {
      return;
    }
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
    if (!selectedSecretId) {
      return;
    }
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

  async function handleSubmit() {
    setSubmitting(true);
    setSubmitError(null);
    setValidationFailure(null);
    setCreatedResult(null);
    if (!datasetId) {
      setSubmitting(false);
      setSubmitError(new Error(t("emptyDataset")));
      return;
    }
    try {
      const payload = {
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
      };
      const result = await createPlannerJob(payload);
      setCreatedResult(result);
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
    return nextSnapshot;
  }

  function startEventSource(nextJobId: string, afterSeq: number) {
    eventSourceRef.current?.close();
    const source = new EventSource(getPlannerJobEventsStreamUrl(nextJobId, afterSeq));
    eventSourceRef.current = source;
    setTimelineMode("sse");
    const handleEvent = (event: MessageEvent) => {
      const parsed = safeEvent(event.data);
      if (!parsed) {
        return;
      }
      setSnapshot((current) => {
        if (current.events.some((item) => item.id === parsed.id || item.seq === parsed.seq)) {
          return current;
        }
        return { ...current, events: [...current.events, parsed] };
      });
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

  const providerLabel = providerMode === "mock" ? t("mockPlanner") : `${providerPreset} / ${model || t("notConfigured")}`;
  const selectedDataset = datasets.find((dataset) => (dataset.datasetId || dataset.id) === datasetId);

  return (
    <main
      className="planner-shell phase9b"
      data-product="Analysis Planner"
      data-acceptance="Validated Plan Preview; Plan Provenance; Agent Timeline; Tool Calls; Artifact Gallery; Report / Recipe Summary; No deterministic fallback used"
      data-testid="planner-workbench"
    >
      <header className="planner-topbar">
        <div>
          <p className="eyebrow">Material Data Intelligence</p>
          <h1>{t("title")}</h1>
          <p className="subtle">{t("subtitle")}</p>
        </div>
        <LanguageToggle locale={locale} setLocale={setLocale} t={t} />
        <label className="switch-row">
          <input type="checkbox" checked={developerMode} onChange={(event) => setDeveloperMode(event.target.checked)} />
          <span>{developerMode ? t("developerMode") : t("userMode")}</span>
        </label>
      </header>

      <section className="status-strip" aria-label={t("systemStatus")}>
        <Metric label={t("systemStatus")} value={health ? health.api.status || t("unknown") : t("emptyHealth")} />
        <Metric label={t("modelStatus")} value={providerLabel} />
        <Metric label={t("currentDataset")} value={selectedDataset?.name || datasetId || t("emptyDataset")} />
        <Metric label={t("currentJob")} value={jobId ? `${jobId} · ${statusLabel(jobStatus, t)}` : t("emptyJob")} status={jobStatus} />
      </section>

      <section className="workspace-layout">
        <aside className="control-column">
          <DataContextPanel
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
          />
          <DemoWorkflowPanel t={t} onLoadDemo={handleLoadDemo} onUsePrompt={() => setPrompt(examplePrompts[0])} onUseMock={() => setProviderMode("mock")} onRun={handleSubmit} />
          <LLMProviderSettingsPanel
            t={t}
            providerMode={providerMode}
            setProviderMode={setProviderMode}
            providerPreset={providerPreset}
            onPresetChange={handlePresetChange}
            providerOptions={providerOptions}
            providerStatus={providerStatus}
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
          />
        </aside>

        <section className="main-column">
          <PromptComposer
            t={t}
            prompt={prompt}
            setPrompt={setPrompt}
            examples={examplePrompts}
            providerLabel={providerLabel}
            datasetLabel={selectedDataset?.name || datasetId || t("emptyDataset")}
            submitting={submitting}
            onSubmit={handleSubmit}
          />
          {submitError ? <ErrorExplainer t={t} error={submitError} /> : null}
          {validationFailure ? <ValidationResultPanel t={t} errors={validationFailure} /> : null}
          <PlanPreviewPanel t={t} plan={plan} planId={planId} planHash={planHash} developerMode={developerMode} />
          <RunControls t={t} jobId={jobId} planId={planId} planHash={planHash} enqueued={createdResult?.enqueued} status={jobStatus} onRun={handleSubmit} submitting={submitting} />
        </section>

        <aside className="status-column">
          <SystemHealthPanel t={t} health={health} providerStatus={providerStatus} />
          <PlanProvenancePanel t={t} job={snapshot.job} result={snapshot.result} planId={planId} planHash={planHash} />
          <TimelinePanel t={t} events={snapshot.events} mode={timelineMode} />
        </aside>
      </section>

      <section className="result-tabs">
        <nav className="tab-list" aria-label="Result tabs">
          {[
            ["overview", t("resultOverview")],
            ["artifacts", t("artifacts")],
            ["report", t("reportRecipe")],
            ["toolcalls", t("toolCalls")],
            ["audit", t("developerAudit")]
          ].map(([id, label]) => (
            <button key={id} type="button" className={activeTab === id ? "active" : ""} onClick={() => setActiveTab(id as TabId)}>
              {label}
            </button>
          ))}
        </nav>
        <div className="tab-surface">
          {activeTab === "overview" ? <ResultOverviewPanel t={t} result={snapshot.result} job={snapshot.job} /> : null}
          {activeTab === "artifacts" ? <ArtifactGallery t={t} artifacts={snapshot.artifacts} developerMode={developerMode} /> : null}
          {activeTab === "report" ? <ReportRecipeSummaryPanel t={t} result={snapshot.result} artifacts={snapshot.artifacts} datasetId={datasetId} profileId={profileId} planId={planId} planHash={planHash} /> : null}
          {activeTab === "toolcalls" ? <ToolCallList t={t} toolCalls={snapshot.toolCalls} developerMode={developerMode} /> : null}
          {activeTab === "audit" ? (
            <DeveloperAuditPanel
              t={t}
              developerMode={developerMode}
              job={snapshot.job}
              events={snapshot.events}
              plan={plan}
              result={createdResult}
              toolCalls={snapshot.toolCalls}
              artifacts={snapshot.artifacts}
            />
          ) : null}
        </div>
      </section>
    </main>
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

function DataContextPanel(props: {
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
}) {
  const { t } = props;
  return (
    <section className="panel" data-testid="data-context-panel">
      <PanelHeading title={t("dataContext")} badge={props.busy ? t("running") : t("ready")} />
      <button type="button" onClick={props.onLoadDemo}>
        {t("loadDemo")}
      </button>
      <label>
        {t("datasetSelector")}
        <select
          aria-label={t("datasetSelector")}
          value={props.datasetId || "__manual"}
          onChange={(event) => {
            if (event.target.value === "__manual") {
              props.setDatasetId("");
              return;
            }
            void props.onDatasetSelect(event.target.value);
          }}
        >
          <option value="__manual">{t("manualFallback")}</option>
          {props.datasets.map((dataset) => {
            const value = dataset.datasetId || dataset.id;
            return (
              <option key={value} value={value}>
                {dataset.name || value} ({dataset.status || t("unknown")})
              </option>
            );
          })}
        </select>
      </label>
      <label>
        {t("projectId")}
        <input aria-label={t("projectId")} value={props.projectId} onChange={(event) => props.setProjectId(event.target.value)} />
      </label>
      <label>
        {t("datasetId")}
        <input aria-label={t("datasetId")} value={props.datasetId} onChange={(event) => props.setDatasetId(event.target.value)} placeholder="dataset_demo" />
      </label>
      <label>
        {t("profileId")}
        <input aria-label={t("profileId")} value={props.profileId} onChange={(event) => props.setProfileId(event.target.value)} placeholder="profile_demo" />
      </label>
      <div className="button-row">
        <button type="button" onClick={props.onGenerateProfile} disabled={!props.datasetId}>
          {t("generateProfile")}
        </button>
        <label className="file-button">
          {t("uploadDataset")}
          <input aria-label={t("uploadDataset")} type="file" onChange={(event) => void props.onUploadFile(event.target.files?.[0] || null)} />
        </label>
      </div>
      <p className="selector-status">{props.dataMessage}</p>
      <ProfileSummary t={t} profile={props.profile} />
    </section>
  );
}

function ProfileSummary({ t, profile }: { t: ReturnType<typeof createTranslator>; profile: DataProfileSummary | null }) {
  if (!profile) {
    return <p className="empty-state">{t("emptyDataset")}</p>;
  }
  const columns = profile.tableSummary?.columns || [];
  const roles = columns.filter((column) => column.inferredRole).map((column) => `${column.inferredRole}:${column.name}`);
  return (
    <div className="profile-summary" data-testid="profile-summary">
      <strong>{t("profileSummary")}</strong>
      <dl className="mini-grid">
        <Field label="Type" value={profile.datasetType || t("unknown")} />
        <Field label="Rows" value={String(profile.tableSummary?.nRows ?? 0)} />
        <Field label="Fields" value={String(profile.tableSummary?.nColumns ?? columns.length)} />
        <Field label="Columns" value={columns.map((column) => column.name).filter(Boolean).join(", ") || t("unknown")} />
        <Field label="Roles" value={roles.join(", ") || t("unknown")} />
        <Field label="Structures" value={String(profile.structureSummary?.nStructures ?? 0)} />
      </dl>
    </div>
  );
}

function DemoWorkflowPanel({ t, onLoadDemo, onUsePrompt, onUseMock, onRun }: { t: ReturnType<typeof createTranslator>; onLoadDemo: () => Promise<void>; onUsePrompt: () => void; onUseMock: () => void; onRun: () => Promise<void> }) {
  return (
    <section className="panel" data-testid="demo-workflow-panel">
      <PanelHeading title={t("demoWorkflow")} badge="Demo" />
      <ol className="workflow-list">
        <li>
          <button type="button" onClick={onLoadDemo}>
            {t("demoStepData")}
          </button>
        </li>
        <li>
          <button type="button" onClick={onUsePrompt}>
            {t("demoStepPrompt")}
          </button>
        </li>
        <li>
          <button type="button" onClick={onUseMock}>
            {t("demoStepMock")}
          </button>
        </li>
        <li>
          <button type="button" onClick={onRun}>
            {t("demoStepRun")}
          </button>
        </li>
        <li>{t("demoStepResult")}</li>
      </ol>
    </section>
  );
}

function LLMProviderSettingsPanel(props: {
  t: ReturnType<typeof createTranslator>;
  providerMode: "mock" | "openai_compatible";
  setProviderMode: (value: "mock" | "openai_compatible") => void;
  providerPreset: ProviderPreset;
  onPresetChange: (value: ProviderPreset) => void;
  providerOptions: ProviderOption[];
  providerStatus: ProviderStatus | null;
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
}) {
  const { t } = props;
  return (
    <section className="panel" data-testid="provider-settings-panel">
      <PanelHeading title={t("providerSettings")} badge={props.providerMode === "mock" ? "Mock" : "LLM"} />
      <label>
        {t("providerMode")}
        <select aria-label={t("providerMode")} value={props.providerMode} onChange={(event) => props.setProviderMode(event.target.value as "mock" | "openai_compatible")}>
          <option value="mock">{t("mockPlanner")}</option>
          <option value="openai_compatible">{t("openaiCompatible")}</option>
        </select>
      </label>
      <label>
        {t("preset")}
        <select aria-label={t("preset")} value={props.providerPreset} onChange={(event) => props.onPresetChange(event.target.value as ProviderPreset)}>
          <option value="openai">OpenAI</option>
          <option value="deepseek">DeepSeek</option>
          <option value="custom">自定义 OpenAI-compatible</option>
        </select>
      </label>
      <label>
        {t("baseUrl")}
        <input aria-label={t("baseUrl")} value={props.baseUrl} onChange={(event) => props.setBaseUrl(event.target.value)} />
      </label>
      <label>
        {t("model")}
        <input aria-label={t("model")} value={props.model} onChange={(event) => props.setModel(event.target.value)} />
      </label>
      <div className="triple-grid">
        <label>
          {t("temperature")}
          <input aria-label={t("temperature")} type="number" step="0.1" value={props.temperature} onChange={(event) => props.setTemperature(Number(event.target.value))} />
        </label>
        <label>
          {t("maxTokens")}
          <input aria-label={t("maxTokens")} type="number" value={props.maxTokens} onChange={(event) => props.setMaxTokens(Number(event.target.value))} />
        </label>
        <label>
          {t("timeout")}
          <input aria-label={t("timeout")} type="number" value={props.timeoutSeconds} onChange={(event) => props.setTimeoutSeconds(Number(event.target.value))} />
        </label>
      </div>
      <label>
        {t("secretAlias")}
        <input aria-label={t("secretAlias")} value={props.secretAlias} onChange={(event) => props.setSecretAlias(event.target.value)} />
      </label>
      <label>
        {t("apiKey")}
        <input aria-label={t("apiKey")} type="password" value={props.apiKey} onChange={(event) => props.setApiKey(event.target.value)} autoComplete="off" />
      </label>
      <div className="button-row">
        <button type="button" onClick={props.onSaveSecret} disabled={!props.apiKey.trim()}>
          {t("saveSecret")}
        </button>
        <button type="button" className="secondary" onClick={props.onDeleteSecret} disabled={!props.selectedSecretId}>
          {t("deleteSecret")}
        </button>
      </div>
      <label>
        {t("savedSecret")}
        <select aria-label={t("savedSecret")} value={props.selectedSecretId} onChange={(event) => props.setSelectedSecretId(event.target.value)}>
          <option value="">{t("notConfigured")}</option>
          {props.secrets.map((secret) => (
            <option key={secret.id} value={secret.id}>
              {secret.alias || secret.provider} · {secret.maskedPreview || "••••"}
            </option>
          ))}
        </select>
      </label>
      <button type="button" onClick={props.onTestProvider}>
        {t("testConnection")}
      </button>
      <p className="subtle">{t("providerNotice")}</p>
      <p className="selector-status">{props.providerStatus?.message || t("emptyProvider")}</p>
      {props.providerResult ? (
        <div className={props.providerResult.ok ? "success-card" : "error-card"} data-testid="provider-test-result">
          <strong>{props.providerResult.message}</strong>
          {props.providerResult.safeDetails ? <small>{props.providerResult.safeDetails}</small> : null}
        </div>
      ) : null}
      {props.providerOptions.length ? <small>{props.providerOptions.map((provider) => provider.label).join(" / ")}</small> : null}
    </section>
  );
}

function PromptComposer(props: {
  t: ReturnType<typeof createTranslator>;
  prompt: string;
  setPrompt: (value: string) => void;
  examples: string[];
  providerLabel: string;
  datasetLabel: string;
  submitting: boolean;
  onSubmit: () => Promise<void>;
}) {
  const { t } = props;
  return (
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
              <strong>步骤 {index + 1}：{step.purpose || step.reason || step.stepId}</strong>
              <span>{toolDisplayName(step.toolId)}</span>
            </div>
            <p>输入：当前数据表 · 输出：{step.output?.artifactTypes?.join(", ") || "artifact"}</p>
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
        ["API 服务", health.api],
        ["数据库", health.database],
        ["Redis 队列", health.redis],
        ["Artifact 存储", health.artifactStorage],
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

function PlanProvenancePanel({ t, job, result, planId, planHash }: { t: ReturnType<typeof createTranslator>; job?: PlannerJobDetail; result?: JobResult; planId: string; planHash: string }) {
  const provenance = job?.provenance || result?.provenance;
  return (
    <section className="panel" data-testid="provenance-panel">
      <PanelHeading title={t("provenance")} badge={planId || t("emptyProvenance")} />
      {!planId ? <p className="empty-state">{t("emptyProvenance")}</p> : null}
      {planId ? (
        <>
          <dl className="mini-grid">
            <Field label="job.plan_id" value={planId} />
            <Field label="planHash" value={planHash} />
            <Field label="binding" value={provenance?.binding || "jobs.plan_id -> analysis_plans.id"} />
            <Field label="source" value={provenance?.loadedFrom || "persisted_analysis_plan"} />
          </dl>
          <div className="provenance-flags">
            <span>{t("loadedPersistedPlan")}</span>
            <span>{t("toolRegistryAdapter")}</span>
            <span>{t("noFallback")}</span>
          </div>
        </>
      ) : null}
    </section>
  );
}

function TimelinePanel({ t, events, mode }: { t: ReturnType<typeof createTranslator>; events: JobEvent[]; mode: "sse" | "polling" | "idle" }) {
  return (
    <section className="panel" data-testid="job-timeline">
      <PanelHeading title={t("timeline")} badge={mode === "sse" ? t("ssePath") : mode === "polling" ? t("pollingFallback") : t("emptyTimeline")} />
      {!events.length ? <p className="empty-state">{t("emptyTimeline")}</p> : null}
      <ol className="timeline-list">
        {events.map((event) => (
          <li key={event.id || event.seq} className={`timeline-item ${event.eventType === "plan.loaded" ? "important" : ""}`}>
            <time>{formatTime(event.createdAt)}</time>
            <span>{timelineLabel(event.eventType)}</span>
            <strong>{event.status}</strong>
            <p>{event.message}</p>
            <details>
              <summary>raw JSON</summary>
              <pre>{JSON.stringify(event, null, 2)}</pre>
            </details>
          </li>
        ))}
      </ol>
    </section>
  );
}

function ResultOverviewPanel({ t, result, job }: { t: ReturnType<typeof createTranslator>; result?: JobResult; job?: PlannerJobDetail }) {
  return (
    <section className="panel" data-testid="result-overview-panel">
      <PanelHeading title={t("resultOverview")} badge={statusLabel(result?.status || job?.status || "", t)} />
      <p className="result-summary">{result?.summary || t("emptyReport")}</p>
      <dl className="mini-grid">
        <Field label="ToolCalls" value={String(result?.toolCallCount ?? job?.toolCallCount ?? 0)} />
        <Field label="Artifacts" value={String(result?.artifactCount ?? job?.artifactCount ?? 0)} />
        <Field label="planId" value={result?.planId || job?.planId || t("emptyProvenance")} />
        <Field label="planHash" value={result?.planHash || job?.planHash || t("emptyProvenance")} />
      </dl>
    </section>
  );
}

function ArtifactGallery({ t, artifacts, developerMode }: { t: ReturnType<typeof createTranslator>; artifacts: Artifact[]; developerMode: boolean }) {
  const groups = groupArtifacts(artifacts, t);
  return (
    <section className="panel" data-testid="artifacts-panel">
      <PanelHeading title={t("artifacts")} badge={`${artifacts.length}`} />
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
                  <button type="button" className="secondary">预览</button>
                  <button type="button" className="secondary">下载</button>
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
        <h3>报告摘要</h3>
        <p>{props.result?.summary || props.t("emptyReport")}</p>
        <ul>
          <li>本次分析做了什么：执行 persisted AnalysisPlan 绑定的工具步骤。</li>
          <li>生成了哪些结果：{props.artifacts.length} 个 Artifact，{props.result?.toolCallCount ?? 0} 个 ToolCall。</li>
          <li>关键指标：由 metrics_json / report artifact 提供。</li>
          <li>异常/注意事项：真实 LLM 报告未启用时显示系统生成摘要。</li>
        </ul>
      </div>
      <div className="summary-box">
        <h3>复现配方</h3>
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

function DeveloperAuditPanel(props: { t: ReturnType<typeof createTranslator>; developerMode: boolean; job?: PlannerJobDetail; events: JobEvent[]; plan: AnalysisPlan | null; result: PlannerJobCreateResult | null; toolCalls: ToolCall[]; artifacts: Artifact[] }) {
  return (
    <section className="panel" data-testid="developer-audit-panel">
      <PanelHeading title={props.t("developerAudit")} badge={props.developerMode ? "open" : "closed"} />
      {!props.developerMode ? <p className="empty-state">打开开发者模式后显示 raw events、AnalysisPlan JSON 和 provenance chain。</p> : null}
      {props.developerMode ? (
        <pre>
          {JSON.stringify(
            {
              jobId: props.job?.jobId || props.result?.job_id,
              planId: props.job?.planId || props.result?.plan_id,
              planHash: props.job?.planHash || props.result?.plan_hash,
              events: props.events,
              analysisPlan: props.plan,
              toolCalls: props.toolCalls,
              artifacts: props.artifacts,
              apiResponse: props.result
            },
            null,
            2
          )}
        </pre>
      ) : null}
    </section>
  );
}

function ErrorExplainer({ t, error }: { t: ReturnType<typeof createTranslator>; error: PlannerApiError | Error }) {
  const apiError = error as PlannerApiError;
  const suggestions = apiError.suggestions?.length
    ? apiError.suggestions
    : [t("suggestionDataset"), t("suggestionDemo"), t("suggestionProfile"), t("suggestionProvider")];
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
        <ul>{suggestions.map((item) => <li key={item}>{item}</li>)}</ul>
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

function Metric({ label, value, status }: { label: string; value: string; status?: string }) {
  return (
    <div className={`metric ${status ? `status-${status}` : ""}`}>
      <span>{label}</span>
      <strong>{value}</strong>
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

function formatTime(value?: string) {
  return value ? new Date(value).toLocaleTimeString() : "";
}

function timelineLabel(type?: string) {
  const labels: Record<string, string> = {
    "plan.generated": "分析计划已生成",
    "plan.persisted": "分析计划已保存",
    "job.queued": "任务已入队",
    "plan.loaded": "Worker 已加载分析计划",
    "tool.started": "工具开始执行",
    "tool.completed": "工具执行完成",
    "artifact.ready": "结果产物已生成",
    "job.completed": "任务完成",
    "job.failed": "任务失败"
  };
  return labels[type || ""] || type || "event";
}

function statusLabel(status: string | undefined, t: ReturnType<typeof createTranslator>) {
  if (!status) {
    return t("unknown");
  }
  if (status === "completed") {
    return t("completed");
  }
  if (status === "queued") {
    return t("queued");
  }
  if (status === "running") {
    return t("running");
  }
  if (status === "failed") {
    return t("failed");
  }
  return status;
}

function statusText(status: string | undefined, t: ReturnType<typeof createTranslator>) {
  if (status === "ok") {
    return t("ok");
  }
  if (status === "ready") {
    return t("ready");
  }
  if (status === "unknown") {
    return t("unknown");
  }
  return status || t("unknown");
}

function toolDisplayName(toolId: string) {
  if (toolId === "ml.basic_metrics") {
    return "基础指标计算";
  }
  if (toolId === "composition.ptable_heatmap") {
    return "元素分布热图";
  }
  if (toolId === "structure.viewer_3d") {
    return "3D 结构查看器";
  }
  return toolId;
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
    if (type.includes("plot") || type.includes("figure") || type.includes("png") || type.includes("svg")) {
      groups[t("charts")].push(artifact);
    } else if (type === "metrics_json") {
      groups[t("jsonMetrics")].push(artifact);
    } else if (type.includes("table")) {
      groups[t("tables")].push(artifact);
    } else if (type.includes("structure") || type.includes("matterviz")) {
      groups[t("structures")].push(artifact);
    } else if (type.includes("report") || type.includes("summary") || type.includes("recipe")) {
      groups[t("reports")].push(artifact);
    } else {
      groups[t("other")].push(artifact);
    }
  }
  return Object.entries(groups)
    .filter(([, items]) => items.length)
    .map(([label, items]) => ({ label, items }));
}
