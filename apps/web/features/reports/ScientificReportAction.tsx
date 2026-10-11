"use client";

import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import { useEffect, useRef, useState } from "react";
import { readSessionRequest } from "../research/session-management";
import { getScientificReportStatusForTurn, requestScientificReport } from "../../app/lib/scientific-report-api";

type Props = { projectId: string; turnId: string; canGenerate: boolean };
type Status = "checking" | "idle" | "requesting" | "composing" | "ready" | "failed" | "unconfirmed";

function reportFailureMessage(code: string | null): string {
  const messages: Record<string, string> = {
    REPORT_QUEUE_TIMEOUT: "报告等待处理超时，可重试生成。",
    REPORT_STAGE_TIMEOUT: "报告生成中断或超时，可重试生成。",
    REPORT_PROVIDER_TIMEOUT: "模型服务响应超时，可稍后重试生成。",
    REPORT_PROVIDER_RATE_LIMITED: "模型服务请求过于频繁，请稍后重试生成。",
    REPORT_PROVIDER_AUTH_FAILED: "模型服务认证失败，请检查所用连接的密钥和访问权限。",
    REPORT_PROVIDER_REQUEST_REJECTED: "模型服务拒绝了报告请求，请检查所用模型和连接设置。",
    REPORT_PROVIDER_OUTPUT_TRUNCATED: "模型返回的报告不完整，可重试生成。",
    REPORT_PROVIDER_INVALID_RESPONSE: "模型返回的报告格式无效，可重试生成。",
    REPORT_SCHEMA_INVALID: "模型返回的报告格式未通过校验，可重试生成。",
    REPORT_EXTERNAL_UNAVAILABLE: "模型服务暂时不可用，请稍后重试生成。",
    REPORT_GROUNDING_FAILED: "报告内容未通过科学依据校验，未保存为正式报告。可重试生成。",
  };
  return `${messages[code || ""] || "报告生成失败，暂未获得可用报告。可重试生成。"} 已保存的科学结果仍可查看。`;
}

export function ScientificReportAction(props: Props) {
  return <ReportAction key={`${props.projectId}:${props.turnId}`} {...props} />;
}

function ReportAction({ projectId, turnId, canGenerate }: Props) {
  const [reportId, setReportId] = useState<string | null>(null);
  const [status, setStatus] = useState<Status>("checking");
  const [pollRevision, setPollRevision] = useState(0);
  const owner = useRef<AbortController | null>(null);
  const [error, setError] = useState("");

  useEffect(() => () => { owner.current?.abort(); }, []);
  useEffect(() => {
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    let attempts = 0;
    async function refresh() {
      try {
        const value = await readSessionRequest((signal) => getScientificReportStatusForTurn(turnId, signal), controller.signal);
        if (controller.signal.aborted) return;
        if (value.research_turn_id !== turnId || !["READY", "FAILED", "REQUESTED", "COMPOSING", "NOT_REQUESTED"].includes(value.status) || (value.status === "READY" && !value.report_id)) throw new Error("Report identity or status mismatch");
        setError("");
        if (value.status === "READY") {
          setReportId(value.report_id); setStatus("ready"); return;
        }
        if (value.status === "FAILED") { setError(reportFailureMessage(value.error_code)); setStatus("failed"); return; }
        if (value.status === "REQUESTED" || value.status === "COMPOSING") {
          setStatus("composing");
          if (attempts++ < 80) timer = setTimeout(() => void refresh(), 1500);
          else { setStatus("unconfirmed"); setError("报告仍在整理中，可重新读取进度。科学结果仍可查看。"); }
          return;
        }
        setStatus("idle");
      } catch {
        if (controller.signal.aborted) return;
        setStatus("unconfirmed");
        setError("暂时无法确认报告状态，请重新读取。科学结果仍可查看。");
      }
    }
    void refresh();
    return () => { controller.abort(); clearTimeout(timer); };
  }, [pollRevision, turnId]);

  async function generate() {
    if (owner.current || !canGenerate || !["idle", "failed"].includes(status)) return;
    const controller = new AbortController(); owner.current = controller;
    setStatus("requesting"); setError("");
    try {
      const value = await readSessionRequest((signal) => requestScientificReport(turnId, signal), controller.signal);
      if (controller.signal.aborted) return;
      if (!value.generation_id || !["REQUESTED", "COMPOSING", "READY"].includes(value.status)) throw new Error("Invalid report admission");
      setStatus("checking"); setPollRevision((value) => value + 1);
    } catch {
      if (controller.signal.aborted) return;
      setStatus("unconfirmed");
      setError("尚未确认报告生成请求的结果，请先重新读取状态，避免重复提交。");
    } finally { if (owner.current === controller) owner.current = null; }
  }

  if (status === "idle" && !canGenerate) return null;
  return <section className="research-report-action" aria-label="科学报告">
    {error ? <p role="status">{error}</p> : null}
    {status === "ready" && reportId
      ? <Link className="product-secondary-action" href={`/projects/${encodeURIComponent(projectId)}/reports/${encodeURIComponent(reportId)}`}>打开报告</Link>
      : status === "unconfirmed"
        ? <button type="button" className="product-secondary-action" onClick={() => { setStatus("checking"); setPollRevision((value) => value + 1); }}>重新读取报告状态</button>
        : canGenerate && ["idle", "failed"].includes(status)
          ? <button type="button" className="product-secondary-action" title="使用已保存的结果生成报告，不会重新计算。" onClick={() => void generate()}>{status === "failed" ? "重试生成" : "生成报告"}</button>
          : <span className="research-report-action-status" role="status" aria-live="polite">{status === "checking" ? "正在检查报告…" : status === "requesting" || status === "composing" ? "正在整理分析报告" : ""}</span>}
  </section>;
}
