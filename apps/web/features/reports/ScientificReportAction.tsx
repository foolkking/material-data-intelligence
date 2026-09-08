"use client";

import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import { useEffect, useState } from "react";

import {
  getScientificReportStatusForTurn,
  requestScientificReport,
} from "../../app/lib/scientific-report-api";

export function ScientificReportAction({ projectId, turnId, canGenerate }: { projectId: string; turnId: string; canGenerate: boolean }) {
  const [reportId, setReportId] = useState<string | null>(null);
  const [status, setStatus] = useState<"checking" | "idle" | "requesting" | "composing" | "ready" | "error">("checking");
  const [pollRevision, setPollRevision] = useState(0);

  useEffect(() => {
    let active = true;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let attempts = 0;
    const refresh = () => {
      void getScientificReportStatusForTurn(turnId).then((value) => {
        if (!active) return;
        if (value.status === "READY" && value.report_id) {
          setReportId(value.report_id);
          setStatus("ready");
          return;
        }
        if (value.status === "FAILED") {
          setStatus("error");
          return;
        }
        if (value.status === "REQUESTED" || value.status === "COMPOSING") {
          setStatus("composing");
          if (attempts < 80) {
            attempts += 1;
            timer = setTimeout(refresh, 1500);
          } else {
            setStatus("error");
          }
          return;
        }
        setStatus("idle");
      }).catch(() => {
        if (!active) return;
        setStatus("error");
      });
    };
    refresh();
    return () => {
      active = false;
      if (timer) clearTimeout(timer);
    };
  }, [pollRevision, turnId]);

  async function generate() {
    setStatus("requesting");
    try {
      await requestScientificReport(turnId);
      setStatus("composing");
      setPollRevision((value) => value + 1);
    } catch {
      setStatus("error");
    }
  }

  return <section className="research-report-action" aria-label="科学报告">
    <div>
      <strong>{status === "ready" ? "分析报告已生成" : status === "composing" || status === "requesting" ? "正在整理分析报告" : "生成科学报告"}</strong>
      <p>{status === "ready" ? "报告已作为可追溯的科学记录保存。" : status === "error" ? "科学结果仍然有效，报告整理暂时未完成。" : "将已验证结果和解释整理为持久报告，不会重新计算。"}</p>
    </div>
    {status === "ready" && reportId
      ? <Link className="product-primary-action" href={`/projects/${projectId}/reports/${reportId}`}>打开报告</Link>
      : canGenerate && !["requesting", "composing", "checking"].includes(status)
        ? <button type="button" className="product-secondary-action" onClick={() => void generate()}>{status === "error" ? "重试生成" : "生成报告"}</button>
        : <span className="research-report-action-status" role="status" aria-live="polite">{status === "checking" ? "正在检查报告…" : status === "requesting" || status === "composing" ? "处理中…" : ""}</span>}
  </section>;
}
