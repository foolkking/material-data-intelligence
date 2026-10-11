import {
  isScientificReportDownload,
  reportDownloadErrors,
  scientificReportDownloadHref,
} from "../../lib/scientific-report-download";
import styles from "./page.module.css";

export const metadata = { title: "报告下载未完成 · Material Data Intelligence" };

export default async function ReportDownloadError({ searchParams }: {
  searchParams: Promise<{ reason?: string; reportId?: string; format?: string }>;
}) {
  const params = await searchParams;
  const reason = Object.hasOwn(reportDownloadErrors, params.reason || "")
    ? params.reason as keyof typeof reportDownloadErrors : "unavailable";
  const reportId = params.reportId || "";
  const format = params.format || "";
  return <main className={styles.page}>
    <section className={styles.message} aria-labelledby="report-download-error-title">
      <h1 id="report-download-error-title">报告下载未完成</h1>
      <p role="alert">{reportDownloadErrors[reason]}</p>
      <p>原报告仍保留在原页面中。</p>
      <div className="product-row-actions">
        {isScientificReportDownload(reportId, format)
          ? <a className="product-primary-action" href={scientificReportDownloadHref(reportId, format)}>重试下载</a> : null}
        <a className="product-secondary-action" href="/projects">打开项目列表</a>
      </div>
    </section>
  </main>;
}
