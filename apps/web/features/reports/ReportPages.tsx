"use client";

import { ProductLink as Link, useProductRouter } from "../../app/components/ProductNavigation";
import React, {
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type KeyboardEvent as ReactKeyboardEvent,
} from "react";
import {
  admitDatasetResource,
  archiveProjectRun,
  createPlannerJob,
  createPlannerJobInterpretation,
  getPlannerInterpretationEvidence,
  getPlannerJob,
  getPlannerJobArtifacts,
  getPlannerJobEvents,
  getPlannerJobInterpretations,
  getPlannerProviderStatus,
  listPlannerProviders,
  getDataset,
  getDatasetProfile,
  getDatasetSourceResources,
  promoteDatasetTable,
  getProjectHistory,
  restoreProjectRun,
  type Artifact,
  type GroundedScientificInterpretation,
  type ScientificEvidenceItem,
  type InterpretationEvidenceResponse,
  type JobEvent,
  type PlannerJobCreateResult,
  type PlannerJobDetail,
  type ProjectHistory,
  type ProviderOption,
  type ProviderStatus,
} from "../../app/lib/planner-api";
import {
  bulkUpdateResearchSessions,
  createResearchAssistantProjection,
  createResearchMessage,
  createResearchSession,
  getResearchSession,
  listResearchSessions,
  resolveResearchScope,
  updateResearchSession,
  type ResearchMessage,
  type ResearchSession,
  type ResearchSessionBulkAction,
  type ScopeResolution,
} from "../../app/lib/product-api";
import { ProductShell, RequireProductAuth } from "../../app/components/ProductShell";
import { ManagedObjectRow, ProductModal } from "../../app/components/ObjectManagement";
import { LazyScientificResultViewer } from "../../app/components/LazyScientificViewers";
import {
  projectScientificArtifacts,
  scientificResultTitle,
  type ProjectedScientificArtifact,
} from "../../app/lib/scientific-result-projection";
import { formatScientificNarrativeNumbers } from "../../app/lib/scientific-presentation";
import { Agent2ScientificPresentation } from "../../app/components/Agent2ScientificPresentation";
import {
  getReportComposition,
  listReportCompositions,
  type ReportEditorialProjection,
} from "../../app/lib/report-composition-api";
import { researchRunTitle } from "../../app/lib/research-display";
import {
  cancelAgent2Execution,
  getAgent2ExecutionProgress,
  type Agent2ProgressView,
} from "../../app/lib/agent2-execution-api";
import { ResearchExecutionActivity } from "../../app/components/ResearchExecutionActivity";
import {
  getAgent2SessionMemory,
  unpinAgent2Object,
  unpinAgent2Result,
  type Agent2SessionMemory,
} from "../../app/lib/agent2-memory-api";
import { ScientificReportAction } from "../../app/components/ScientificReportAction";
import {
  Agent2ReadError,
  createAgent2ResearchTurn,
  dispatchAgent2ResearchTurn,
  getAgent2ContextManifest,
  getAgent2ResearchTurn,
  getAgent2ResearchTurnResult,
  listAgent2ResearchTurns,
  type Agent2ScientificObjectRef,
  type Agent2ScientificSelection,
  type Agent2ContextManifest,
  type Agent2ContextManifestItem,
  type Agent2ContextManifestRecord,
  type Agent2ResearchTurnResult,
  type Agent2TurnDetail,
  type Agent2TurnResponse,
} from "../../app/lib/agent2-research-api";
import { decodeWorkspaceSelectionUrl } from "../../app/components/workspace/workspace-selection-contract";
import {
  apiSemanticLocator,
  scientificSelectionFromWorkspace,
  selectionToResearchObjectRef,
} from "../../app/components/scientific-viewer/scientificSelection";
import { resolveScientificViewer } from "../../app/components/scientific-viewer/scientificViewerRegistry";
import { RESEARCH_CANCELLING_POLL_INTERVAL_MS } from "../../app/lib/research-status";
import {
  beginResearchPerformanceAttempt,
  bindResearchPerformanceTurn,
  recordResearchFirstTruthfulProgress,
  scheduleResearchSubmitAcknowledgement,
  type ResearchPerformanceSample,
} from "../../app/lib/research-performance";
import { projectRoleAllows } from "../../app/lib/project-permissions";
import { artifactLabel, displayEvidenceValue, evidenceLabel, formatPercent, groundedEvidenceNarrative, researchRunHref, researchSessionReferencesRun, userFacingClaims, userFacingLimitations } from "../research/ResearchPages";


export function ReportsPage({ projectId }: { projectId: string }) {
  const [history, setHistory] = useState<ProjectHistory | null>(null);
  const [loadState, setLoadState] = useState<"loading" | "ready" | "error">(
    "loading",
  );
  const [reloadKey, setReloadKey] = useState(0);
  useEffect(() => {
    let active = true;
    setLoadState("loading");
    void getProjectHistory(projectId)
      .then((value) => {
        if (active) {
          setHistory(value);
          setLoadState("ready");
        }
      })
      .catch(() => {
        if (active) setLoadState("error");
      });
    return () => {
      active = false;
    };
  }, [projectId, reloadKey]);
  const reports =
    history?.analyses.filter(
      (item) =>
        item.visibleInReports !== false &&
        (item.reportCount > 0 ||
          ["completed", "succeeded", "success"].includes(
            item.status.toLowerCase(),
          )),
    ) || [];
  return (
    <RequireProductAuth>
      <ProductShell projectId={projectId}>
        <section className="document-page">
          <header className="product-page-heading">
            <p className="product-kicker">报告</p>
            <h1>分析报告</h1>
            <p>这个项目中的分析报告，保留研究目标、方法、结果和依据。</p>
          </header>
          <div className="report-list">
            {loadState === "loading" ? (
              <div className="product-loading" role="status" aria-live="polite">
                正在加载项目报告…
              </div>
            ) : loadState === "error" ? (
              <div className="product-state" role="alert">
                <h2>报告列表暂时无法加载</h2>
                <p>已生成的报告没有丢失，请检查服务连接后重试。</p>
                <button
                  type="button"
                  className="product-primary-action"
                  onClick={() => setReloadKey((value) => value + 1)}
                >
                  重新加载
                </button>
              </div>
            ) : (
              <>
                {reports.map((run) => {
                  const dataset = history?.datasets.find(
                    (item) => item.datasetId === run.datasetId,
                  );
                  return (
                    <Link
                      className="report-list-row"
                      key={run.jobId}
                      href={"/projects/" + projectId + "/reports/" + run.jobId}
                    >
                      <div>
                        <span className="product-kicker">分析报告</span>
                        <h2>{researchRunTitle(run)}</h2>
                        <p>
                          {dataset?.name || "项目数据"} · {run.artifactCount}{" "}
                          个结果 · {run.stepCount} 个步骤
                        </p>
                      </div>
                      <span>阅读报告 →</span>
                    </Link>
                  );
                })}
                {reports.length === 0 && (
                  <div className="product-state">
                    <h2>还没有分析报告</h2>
                    <p>完成一次研究后，分析报告会出现在这里。</p>
                  </div>
                )}
              </>
            )}
          </div>
        </section>
      </ProductShell>
    </RequireProductAuth>
  );
}

export function ReportReaderPage({
  projectId,
  reportId,
}: {
  projectId: string;
  reportId: string;
}) {
  const [history, setHistory] = useState<ProjectHistory | null>(null);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [interpretation, setInterpretation] =
    useState<GroundedScientificInterpretation | null>(null);
  const [runDetail, setRunDetail] = useState<PlannerJobDetail | null>(null);
  const [reportEvidence, setReportEvidence] =
    useState<InterpretationEvidenceResponse | null>(null);
  const [editorial, setEditorial] = useState<ReportEditorialProjection | null>(
    null,
  );
  const [loadState, setLoadState] = useState<"loading" | "ready" | "error">(
    "loading",
  );
  useEffect(() => {
    void getProjectHistory(projectId).then(setHistory);
  }, [projectId]);
  useEffect(() => {
    const controller = new AbortController();
    setLoadState("loading");
    void Promise.allSettled([
      getPlannerJobArtifacts(reportId),
      getPlannerJobInterpretations(reportId),
      getPlannerJob(reportId),
    ])
      .then(([artifactResult, interpretationResult, detailResult]) => {
        if (controller.signal.aborted) return;
        setArtifacts(
          artifactResult.status === "fulfilled" ? artifactResult.value : [],
        );
        const nextInterpretation =
          interpretationResult.status === "fulfilled"
            ? interpretationResult.value.interpretations?.at(-1) || null
            : null;
        setInterpretation(nextInterpretation);
        setRunDetail(
          detailResult.status === "fulfilled" ? detailResult.value : null,
        );
        if (nextInterpretation)
          void getPlannerInterpretationEvidence(
            nextInterpretation.interpretationId,
          )
            .then(setReportEvidence)
            .catch(() => setReportEvidence(null));
        setLoadState(
          artifactResult.status === "fulfilled" ||
            interpretationResult.status === "fulfilled" ||
            detailResult.status === "fulfilled"
            ? "ready"
            : "error",
        );
      })
      .catch(() => {
        if (!controller.signal.aborted) setLoadState("error");
      });
    return () => controller.abort();
  }, [reportId]);
  const report = history?.analyses.find((item) => item.jobId === reportId);
  useEffect(() => {
    if (!report?.workspaceId) {
      setEditorial(null);
      return;
    }
    const controller = new AbortController();
    void listReportCompositions(report.workspaceId, controller.signal)
      .then((value) =>
        value.items.find((item) => item.sourceJobId === reportId),
      )
      .then((item) =>
        item
          ? getReportComposition(
              report.workspaceId!,
              item.reportId,
              controller.signal,
            )
          : null,
      )
      .then((detail) => {
        if (!controller.signal.aborted)
          setEditorial(detail?.editorialProjection || null);
      })
      .catch(() => {
        if (!controller.signal.aborted) setEditorial(null);
      });
    return () => controller.abort();
  }, [report?.workspaceId, reportId]);
  const reportArtifacts = projectScientificArtifacts(artifacts);
  const researchQuestion =
    editorial?.researchQuestion ||
    report?.userQuestion ||
    runDetail?.analysisPlan?.goal ||
    "本次研究围绕项目中的材料数据展开。";
  const reportTitle =
    editorial?.reportTitle ||
    scientificResultTitle(researchQuestion, artifacts, interpretation);
  const claims = userFacingClaims(interpretation);
  const limitations = userFacingLimitations(interpretation);
  const narrative = groundedEvidenceNarrative(reportEvidence);
  const primaryArtifact =
    reportArtifacts.find((item) => item.resultRole === "PRIMARY_FIGURE") ||
    reportArtifacts.find((item) => item.resultRole === "PRIMARY_TABLE") ||
    reportArtifacts[0];
  const supportingArtifacts = reportArtifacts.filter(
    (item) => item !== primaryArtifact,
  );
  const reportLimitations = editorial?.limitations?.length
    ? editorial.limitations
    : limitations;
  const canManageReport = projectRoleAllows(history?.project?.role, "write");
  const [archiveBusy, setArchiveBusy] = useState(false);
  const toggleArchive = async () => {
    setArchiveBusy(true);
    try {
      if (report?.archived) await restoreProjectRun(projectId, reportId);
      else await archiveProjectRun(projectId, reportId);
      setHistory((current) =>
        current
          ? {
              ...current,
              analyses: current.analyses.map((item) =>
                item.jobId === reportId
                  ? {
                      ...item,
                      archived: !item.archived,
                      visibleInReports: item.archived,
                    }
                  : item,
              ),
            }
          : current,
      );
    } finally {
      setArchiveBusy(false);
    }
  };
  return (
    <RequireProductAuth>
      <ProductShell projectId={projectId}>
        <article className="report-reader">
          <Link href={`/projects/${projectId}/reports`} className="back-link">
            ← 返回报告
          </Link>
          <div className="report-reader-actions">
            <p className="product-kicker">分析报告 · 单次运行</p>
            <div className="workbench-heading-actions">
              {report?.datasetId ? (
                <Link
                  className="product-secondary-action"
                  href={`/projects/${projectId}/data?dataset=${report.datasetId}`}
                >
                  查看数据
                </Link>
              ) : null}
              <Link
                className="product-secondary-action"
                href={researchRunHref(
                  projectId,
                  reportId,
                  [],
                  report?.researchSessionId,
                  report?.researchTurnId,
                )}
              >
                返回研究
              </Link>
              {canManageReport ? (
                <button
                  type="button"
                  className="product-secondary-action"
                  onClick={() => void toggleArchive()}
                  disabled={archiveBusy || !report}
                >
                  {report?.archived ? "恢复到报告列表" : "归档此报告"}
                </button>
              ) : null}
            </div>
          </div>
          <h1>{reportTitle}</h1>
          <p className="report-meta">
            {report?.archived ? "已归档 · " : ""}
            {history?.datasets.find(
              (item) => item.datasetId === report?.datasetId,
            )?.name || "项目数据"}{" "}
            · {reportArtifacts.length || report?.artifactCount || 0} 个输出 ·{" "}
            {report?.stepCount || runDetail?.analysisPlan?.steps?.length || 0}{" "}
            个步骤
          </p>
          <hr />
          <section
            className="report-primary-result"
            aria-labelledby="report-primary-result-title"
          >
            <h2 id="report-primary-result-title">主要结果</h2>
            {loadState === "loading" ? (
              <p className="product-loading" role="status">
                正在加载运行结果…
              </p>
            ) : loadState === "error" ? (
              <p className="product-form-error" role="alert">
                运行结果暂时无法读取，历史摘要仍然可用。
              </p>
            ) : primaryArtifact ? (
              <ReportArtifactFigure
                artifact={primaryArtifact}
                projectId={projectId}
                datasetId={report?.datasetId}
                reportId={reportId}
                artifacts={artifacts}
              />
            ) : (
              <div className="product-state">
                <h3>本次运行没有可展示的结果</h3>
                <p>保留运行记录和限制信息。</p>
              </div>
            )}
          </section>
          <section
            className="report-conclusion"
            aria-labelledby="report-conclusion-title"
          >
            <h2 id="report-conclusion-title">主要结论</h2>
            <p>
              {editorial?.summary ||
                claims[0]?.renderedText ||
                narrative.finding ||
                "本次报告汇总已验证的科学输出、依据和限制。"}
            </p>
            {claims.length ? (
              <ul className="report-findings">
                {claims.map((claim) => (
                  <li key={claim.claimId}>
                    <strong>发现</strong>
                    <p>{claim.renderedText}</p>
                  </li>
                ))}
              </ul>
            ) : null}
          </section>
          <section
            className="report-limitations"
            aria-labelledby="report-limitations-title"
          >
            <h2 id="report-limitations-title">限制</h2>
            {reportLimitations.length ? (
              <ul>
                {reportLimitations.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : (
              <p>
                {narrative.limitation ||
                  "报告结论仅适用于本次运行选择的数据和经过验证的工具步骤。"}
              </p>
            )}
          </section>
          {supportingArtifacts.length ? (
            <details className="report-supporting-results">
              <summary>支持性结果 · {supportingArtifacts.length} 项</summary>
              <div className="report-artifact-list">
                {supportingArtifacts.map((artifact) => (
                  <ReportArtifactFigure
                    key={artifact.artifactId || artifact.id}
                    artifact={artifact}
                    projectId={projectId}
                    datasetId={report?.datasetId}
                    reportId={reportId}
                    artifacts={artifacts}
                  />
                ))}
              </div>
            </details>
          ) : null}
          <h2>研究问题</h2>
          <p>{researchQuestion}</p>
          <h2>方法与依据</h2>
          <p>
            {editorial?.methodSummary?.join("；") ||
              "分析方案、来源数据、输出与可复现信息由运行记录提供。"}
          </p>
          {reportEvidence?.evidenceItems?.length ? (
            <details>
              <summary>依据 · {reportEvidence.evidenceItems.length} 项</summary>
              <ul>
                {reportEvidence.evidenceItems.map((item) => (
                  <li key={item.evidenceItemId}>
                    {evidenceLabel(item.semanticRole)}：
                    {displayEvidenceValue(item.displayValue)}
                  </li>
                ))}
              </ul>
            </details>
          ) : null}
          {interpretation ? (
            <details>
              <summary>来源与过程</summary>
              <p>结论来自已完成的科学解释，依据已与本次运行绑定。</p>
            </details>
          ) : null}
          <details>
            <summary>复现信息</summary>
            <p>
              此报告对应单次分析运行；复现信息由运行方案和来源资源绑定提供，不自动重新执行。
            </p>
          </details>
        </article>
      </ProductShell>
    </RequireProductAuth>
  );
}

function ReportArtifactFigure({
  artifact,
  projectId,
  datasetId,
  reportId,
  artifacts,
}: {
  artifact: ReturnType<typeof projectScientificArtifacts>[number];
  projectId: string;
  datasetId?: string;
  reportId: string;
  artifacts: Artifact[];
}) {
  return (
    <section
      className={`report-figure result-role-${artifact.resultRole.toLowerCase()}`}
    >
      <span>
        {artifact.resultRole === "PRIMARY_FIGURE" ||
        artifact.resultRole === "PRIMARY_TABLE"
          ? "主要结果"
          : artifactLabel(artifact.type)}
      </span>
      <strong>{artifact.resultTitle}</strong>
      <LazyScientificResultViewer
        projectId={projectId}
        datasetId={datasetId}
        jobId={reportId}
        selected={artifact}
        artifacts={artifacts}
      />
      <p>
        {artifact.resultRole === "PRIMARY_FIGURE" ||
        artifact.resultRole === "PRIMARY_TABLE"
          ? "图表、表格和单位来自本次运行的已验证输出。"
          : "支持性科学输出，供结果复核使用。"}
      </p>
    </section>
  );
}

