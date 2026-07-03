"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  AnalysisPlan,
  AnalysisPlanRecord,
  Artifact,
  JobEvent,
  JobResult,
  PlannerApiError,
  PlannerJobCreateResult,
  PlannerJobDetail,
  ToolCall,
  ValidationError,
  createPlannerJob,
  getAnalysisPlan,
  getPlannerJob,
  getPlannerJobArtifacts,
  getPlannerJobEvents,
  getPlannerJobResult,
  getPlannerJobToolCalls
} from "../lib/planner-api";

type Snapshot = {
  job: PlannerJobDetail | null;
  analysisPlan: AnalysisPlanRecord | null;
  events: JobEvent[];
  toolCalls: ToolCall[];
  artifacts: Artifact[];
  result: JobResult | null;
};

const terminalStatuses = new Set(["completed", "failed", "cancelled"]);

const emptySnapshot: Snapshot = {
  job: null,
  analysisPlan: null,
  events: [],
  toolCalls: [],
  artifacts: [],
  result: null
};

export function PlannerWorkbench() {
  const [projectId, setProjectId] = useState("project_local");
  const [datasetId, setDatasetId] = useState("dataset_demo");
  const [profileId, setProfileId] = useState("profile_demo");
  const [userPrompt, setUserPrompt] = useState("Compute basic metrics for y_true vs y_pred.");
  const [enqueue, setEnqueue] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [shouldPoll, setShouldPoll] = useState(false);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [currentPlanId, setCurrentPlanId] = useState<string | null>(null);
  const [createResult, setCreateResult] = useState<PlannerJobCreateResult | null>(null);
  const [snapshot, setSnapshot] = useState<Snapshot>(emptySnapshot);
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>([]);
  const [apiError, setApiError] = useState<string | null>(null);

  const activePlan = useMemo<AnalysisPlan | null>(() => {
    return snapshot.analysisPlan?.analysisPlan || snapshot.job?.analysisPlan || createResult?.plan || null;
  }, [createResult, snapshot.analysisPlan, snapshot.job]);
  const planId = snapshot.job?.planId || snapshot.analysisPlan?.planId || createResult?.plan_id || currentPlanId;
  const planHash = snapshot.job?.planHash || snapshot.analysisPlan?.planHash || createResult?.plan_hash || null;
  const jobId = snapshot.job?.jobId || createResult?.job_id || currentJobId;
  const planLoadedEvent = snapshot.events.find((event) => event.eventType === "plan.loaded");
  const status = snapshot.job?.status || (createResult?.enqueued ? "queued" : createResult?.ok ? "created" : "unknown");
  const terminal = terminalStatuses.has(status);

  async function refreshSnapshot(jobIdValue: string, planIdValue: string | null, fallbackPlan?: AnalysisPlan | null) {
    setRefreshing(true);
    try {
      const [job, events, toolCalls, artifacts, result, analysisPlan] = await Promise.all([
        getPlannerJob(jobIdValue),
        getPlannerJobEvents(jobIdValue),
        getPlannerJobToolCalls(jobIdValue),
        getPlannerJobArtifacts(jobIdValue),
        getPlannerJobResult(jobIdValue),
        planIdValue ? getAnalysisPlan(planIdValue) : Promise.resolve(null)
      ]);
      setSnapshot({
        job: fallbackPlan && !job.analysisPlan ? { ...job, analysisPlan: fallbackPlan } : job,
        analysisPlan,
        events,
        toolCalls,
        artifacts,
        result
      });
    } catch (error) {
      setApiError(error instanceof PlannerApiError ? error.message : "Unable to load planner job state.");
    } finally {
      setRefreshing(false);
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setApiError(null);
    setValidationErrors([]);
    setCreateResult(null);
    setSnapshot(emptySnapshot);
    setCurrentJobId(null);
    setCurrentPlanId(null);
    setShouldPoll(false);
    try {
      const created = await createPlannerJob({
        projectId,
        datasetId,
        profileId,
        userPrompt,
        enqueue
      });
      setCreateResult(created);
      if (!created.ok) {
        setValidationErrors(created.validation_errors || []);
        return;
      }
      const createdJobId = created.job_id || null;
      const createdPlanId = created.plan_id || null;
      setCurrentJobId(createdJobId);
      setCurrentPlanId(createdPlanId);
      setShouldPoll(Boolean(created.enqueued));
      if (createdJobId) {
        await refreshSnapshot(createdJobId, createdPlanId, created.plan || null);
      }
    } catch (error) {
      setApiError(error instanceof PlannerApiError ? error.message : "Unable to create planner job.");
    } finally {
      setSubmitting(false);
    }
  }

  useEffect(() => {
    if (!currentJobId || !shouldPoll || terminal) {
      return;
    }
    const interval = window.setInterval(() => {
      void refreshSnapshot(currentJobId, currentPlanId);
    }, 2500);
    return () => window.clearInterval(interval);
  }, [currentJobId, currentPlanId, shouldPoll, terminal]);

  return (
    <main className="planner-shell">
      <section className="planner-create" aria-label="Create planner job">
        <header className="workspace-header">
          <p className="eyebrow">Planner</p>
          <h1>Analysis Planner</h1>
          <p className="subtle">Natural language request to persisted AnalysisPlan job.</p>
        </header>

        <form className="planner-form" data-testid="planner-form" onSubmit={onSubmit}>
          <label>
            Project ID
            <input value={projectId} onChange={(event) => setProjectId(event.target.value)} required />
          </label>
          <label>
            Dataset ID
            <input value={datasetId} onChange={(event) => setDatasetId(event.target.value)} required />
          </label>
          <label>
            Profile ID
            <input value={profileId} onChange={(event) => setProfileId(event.target.value)} />
          </label>
          <label>
            Analysis intent
            <textarea value={userPrompt} onChange={(event) => setUserPrompt(event.target.value)} required rows={5} />
          </label>
          <label className="toggle-row">
            <input type="checkbox" checked={enqueue} onChange={(event) => setEnqueue(event.target.checked)} />
            Enqueue job
          </label>
          <button type="submit" disabled={submitting}>
            {submitting ? "Submitting" : enqueue ? "Create and enqueue" : "Create planned job"}
          </button>
        </form>

        {apiError ? <p className="alert error">{apiError}</p> : null}
        {createResult && !createResult.ok ? <ValidationFailure errors={validationErrors} /> : null}
      </section>

      <section className="planner-workspace" aria-label="Planner job workspace">
        <section className="summary-strip" aria-label="Planner job summary">
          <Metric label="Job" value={display(jobId)} />
          <Metric label="Plan" value={display(planId)} />
          <Metric label="Plan hash" value={display(planHash)} />
          <Metric label="Status" value={display(status)} tone={status} />
          <Metric label="Enqueued" value={createResult?.enqueued ? "true" : createResult?.ok ? "false" : "Not available yet"} />
        </section>

        <section className="work-grid">
          <PlanPreview plan={activePlan} planId={planId} planHash={planHash} validationStatus={snapshot.job?.validationStatus} />
          <PlanProvenance
            job={snapshot.job}
            analysisPlan={snapshot.analysisPlan}
            planLoadedEvent={planLoadedEvent}
            toolCalls={snapshot.toolCalls}
            artifacts={snapshot.artifacts}
            result={snapshot.result}
          />
          <JobStatusPanel job={snapshot.job} result={snapshot.result} refreshing={refreshing} />
          <JobTimeline events={snapshot.events} />
          <ToolCallsPanel toolCalls={snapshot.toolCalls} />
          <ArtifactsResultPanel artifacts={snapshot.artifacts} result={snapshot.result} />
        </section>
      </section>
    </main>
  );
}

function ValidationFailure({ errors }: { errors: ValidationError[] }) {
  return (
    <section className="validation-failure" data-testid="validation-failure" aria-live="polite">
      <h2>Plan validation failed</h2>
      <ul>
        <li>No AnalysisPlan was saved</li>
        <li>No Job was created</li>
        <li>Nothing was enqueued</li>
        <li>Please fix the request and try again</li>
      </ul>
      {errors.length ? (
        <div className="validation-errors">
          {errors.map((error, index) => (
            <div className="list-row" key={`${error.code || "error"}-${index}`}>
              <strong>{display(error.code || error.field || "VALIDATION_ERROR")}</strong>
              <span>{display(error.message)}</span>
              <small>{formatDetail(error.detail || error.details)}</small>
            </div>
          ))}
        </div>
      ) : (
        <p className="subtle">No field-level details were returned.</p>
      )}
    </section>
  );
}

function PlanPreview({
  plan,
  planId,
  planHash,
  validationStatus
}: {
  plan: AnalysisPlan | null;
  planId?: string | null;
  planHash?: string | null;
  validationStatus?: string | null;
}) {
  const steps = plan?.steps || [];
  return (
    <section className="surface plan-preview" data-testid="plan-preview" aria-label="Validated plan preview">
      <div className="section-heading">
        <h2>Validated Plan Preview</h2>
        <span>{steps.length ? `${steps.length} step(s)` : "Not available yet"}</span>
      </div>
      <dl className="detail-grid">
        <div>
          <dt>planId</dt>
          <dd>{display(planId)}</dd>
        </div>
        <div>
          <dt>planHash</dt>
          <dd>{display(planHash)}</dd>
        </div>
        <div>
          <dt>validation</dt>
          <dd>{display(validationStatus || "validated")}</dd>
        </div>
        <div>
          <dt>datasetId</dt>
          <dd>{display(plan?.datasetId)}</dd>
        </div>
      </dl>
      <div className="step-list">
        {steps.length ? (
          steps.map((step) => (
            <article className="step-row" key={step.stepId}>
              <div>
                <strong>{step.stepId}</strong>
                <span>{step.toolId}</span>
              </div>
              <p>{display(step.purpose || step.reason)}</p>
              <small>{paramsSummary(step.params)}</small>
            </article>
          ))
        ) : (
          <p className="empty-state">Not available yet</p>
        )}
      </div>
    </section>
  );
}

function PlanProvenance({
  job,
  analysisPlan,
  planLoadedEvent,
  toolCalls,
  artifacts,
  result
}: {
  job: PlannerJobDetail | null;
  analysisPlan: AnalysisPlanRecord | null;
  planLoadedEvent?: JobEvent;
  toolCalls: ToolCall[];
  artifacts: Artifact[];
  result: JobResult | null;
}) {
  const firstToolCall = toolCalls[0];
  const firstArtifact = artifacts[0];
  const hasPlanBinding = Boolean(job?.planId || analysisPlan?.planId || analysisPlan?.id);
  return (
    <section className="surface provenance-panel" data-testid="provenance-panel" aria-label="Plan provenance">
      <div className="section-heading">
        <h2>Plan Provenance</h2>
        <span>{job?.provenance?.loadedFrom === "persisted_analysis_plan" ? "persisted" : "Not available yet"}</span>
      </div>
      <dl className="detail-grid">
        <div>
          <dt>job.plan_id</dt>
          <dd>{display(job?.planId)}</dd>
        </div>
        <div>
          <dt>analysisPlan.id</dt>
          <dd>{display(analysisPlan?.planId || analysisPlan?.id)}</dd>
        </div>
        <div>
          <dt>analysisPlan.planHash</dt>
          <dd>{display(analysisPlan?.planHash || job?.planHash)}</dd>
        </div>
        <div>
          <dt>ToolCall.planId / planHash</dt>
          <dd>{display(joinPair(firstToolCall?.planId, firstToolCall?.planHash))}</dd>
        </div>
        <div>
          <dt>Artifact.planId / planHash</dt>
          <dd>{display(joinPair(firstArtifact?.planId, firstArtifact?.planHash))}</dd>
        </div>
        <div>
          <dt>Result.planId / planHash</dt>
          <dd>{display(joinPair(result?.planId, result?.planHash))}</dd>
        </div>
      </dl>
      <div className="provenance-flags">
        {hasPlanBinding ? (
          <>
            <span>Loaded from persisted AnalysisPlan</span>
            <span>Executed through Tool Registry + Adapter</span>
            <span>No deterministic fallback used</span>
          </>
        ) : (
          <span>Not available yet</span>
        )}
      </div>
      <div className="event-highlight">
        <strong>{display(planLoadedEvent?.eventType)}</strong>
        <span>{display(planLoadedEvent?.createdAt)}</span>
        <small>
          planId {display(planLoadedEvent?.payload?.planId)} · planHash {display(planLoadedEvent?.payload?.planHash)}
        </small>
      </div>
    </section>
  );
}

function JobStatusPanel({ job, result, refreshing }: { job: PlannerJobDetail | null; result: JobResult | null; refreshing: boolean }) {
  return (
    <section className="surface status-panel" aria-label="Job run status">
      <div className="section-heading">
        <h2>Job Status</h2>
        <span>{refreshing ? "refreshing" : display(job?.status)}</span>
      </div>
      <dl className="detail-grid">
        <div>
          <dt>jobId</dt>
          <dd>{display(job?.jobId)}</dd>
        </div>
        <div>
          <dt>job.plan_id</dt>
          <dd>{display(job?.planId)}</dd>
        </div>
        <div>
          <dt>ToolCalls</dt>
          <dd>{display(job?.toolCallCount)}</dd>
        </div>
        <div>
          <dt>Artifacts</dt>
          <dd>{display(job?.artifactCount)}</dd>
        </div>
      </dl>
      <p className="result-summary">{display(result?.summary)}</p>
    </section>
  );
}

function JobTimeline({ events }: { events: JobEvent[] }) {
  return (
    <section className="surface timeline-panel" aria-label="Agent timeline">
      <div className="section-heading">
        <h2>Agent Timeline</h2>
        <span>{events.length ? `${events.length} event(s)` : "Not available yet"}</span>
      </div>
      <ol className="timeline-list" data-testid="job-timeline">
        {events.length ? (
          events.map((event) => (
            <li className={event.eventType === "plan.loaded" ? "timeline-item important" : "timeline-item"} key={event.id || `${event.seq}-${event.eventType}`}>
              <span>{event.eventType}</span>
              <strong>{event.status}</strong>
              <p>{event.message}</p>
              <small>{display(event.createdAt)}</small>
            </li>
          ))
        ) : (
          <li className="empty-state">Not available yet</li>
        )}
      </ol>
    </section>
  );
}

function ToolCallsPanel({ toolCalls }: { toolCalls: ToolCall[] }) {
  return (
    <section className="surface toolcalls-panel" data-testid="toolcalls-panel" aria-label="Tool calls">
      <div className="section-heading">
        <h2>Tool Calls</h2>
        <span>{toolCalls.length ? `${toolCalls.length} call(s)` : "Not available yet"}</span>
      </div>
      <div className="list-stack">
        {toolCalls.length ? (
          toolCalls.map((toolCall) => (
            <article className="list-row" key={toolCall.id || `${toolCall.stepId}-${toolCall.toolId}`}>
              <div>
                <strong>{display(toolCall.toolId)}</strong>
                <span>{display(toolCall.stepId)}</span>
              </div>
              <dl className="inline-details">
                <div>
                  <dt>Status</dt>
                  <dd>{display(toolCall.status)}</dd>
                </div>
                <div>
                  <dt>planId</dt>
                  <dd>{display(toolCall.planId)}</dd>
                </div>
                <div>
                  <dt>planHash</dt>
                  <dd>{display(toolCall.planHash)}</dd>
                </div>
              </dl>
              <small>{display(toolCall.inputSummary)} · {display(toolCall.outputSummary)}</small>
            </article>
          ))
        ) : (
          <p className="empty-state">Not available yet</p>
        )}
      </div>
    </section>
  );
}

function ArtifactsResultPanel({ artifacts, result }: { artifacts: Artifact[]; result: JobResult | null }) {
  return (
    <section className="surface artifacts-panel" data-testid="artifacts-panel" aria-label="Artifacts and result">
      <div className="section-heading">
        <h2>Artifacts / Result</h2>
        <span>{artifacts.length ? `${artifacts.length} artifact(s)` : "Not available yet"}</span>
      </div>
      <div className="list-stack">
        {artifacts.length ? (
          artifacts.map((artifact) => (
            <article className="list-row" key={artifact.artifactId || artifact.id}>
              <div>
                <strong>{display(artifact.name || artifact.artifactId || artifact.id)}</strong>
                <span>{display(artifact.type)}</span>
              </div>
              <dl className="inline-details">
                <div>
                  <dt>storage</dt>
                  <dd>{display(artifact.storageProvider)}</dd>
                </div>
                <div>
                  <dt>planId</dt>
                  <dd>{display(artifact.planId)}</dd>
                </div>
                <div>
                  <dt>planHash</dt>
                  <dd>{display(artifact.planHash)}</dd>
                </div>
              </dl>
              <small>{display(artifact.storageKey)}</small>
            </article>
          ))
        ) : (
          <p className="empty-state">Not available yet</p>
        )}
      </div>
      <div className="result-box">
        <strong>Result summary</strong>
        <p>{display(result?.summary)}</p>
        <small>
          planId {display(result?.planId)} · planHash {display(result?.planHash)}
        </small>
      </div>
    </section>
  );
}

function Metric({ label, value, tone }: { label: string; value: string; tone?: string }) {
  return (
    <div className={`metric ${tone ? `status-${tone}` : ""}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function display(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "Not available yet";
  }
  if (typeof value === "number") {
    return Number.isFinite(value) ? String(value) : "Not available yet";
  }
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  return String(value);
}

function paramsSummary(params: Record<string, unknown> | undefined): string {
  if (!params || !Object.keys(params).length) {
    return "No params";
  }
  return `Params: ${Object.keys(params).sort().join(", ")}`;
}

function formatDetail(value: unknown): string {
  if (!value) {
    return "";
  }
  if (typeof value === "string") {
    return value;
  }
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

function joinPair(first: string | null | undefined, second: string | null | undefined): string | null {
  if (!first && !second) {
    return null;
  }
  return `${display(first)} / ${display(second)}`;
}
