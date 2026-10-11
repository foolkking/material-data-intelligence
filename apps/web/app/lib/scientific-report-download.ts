export type ScientificReportDownloadFormat = "markdown" | "manifest" | "zip";

export function isScientificReportDownload(reportId: string, format: string): format is ScientificReportDownloadFormat {
  return /^agent2_report_[a-z0-9_-]{1,96}$/iu.test(reportId)
    && (format === "markdown" || format === "manifest" || format === "zip");
}

export function scientificReportDownloadHref(reportId: string, format: ScientificReportDownloadFormat) {
  return `/downloads/scientific-reports/${encodeURIComponent(reportId)}/${format}`;
}

export const reportDownloadErrors = {
  auth: "登录已过期。请返回报告页面重新登录，再重试下载。",
  forbidden: "当前账户没有这份报告的访问权限。请返回报告页面确认账户和项目权限。",
  missing: "这份报告暂时不可用。请返回报告列表确认报告是否仍可访问。",
  timeout: "读取报告超时。请稍后重试下载。",
  unavailable: "暂时无法读取完整报告。请稍后重试下载。",
  bundle_limit: "随附结果超出本次打包范围（最多 32 个原始结果文件、每个 8 MB、总计 32 MB）。可分别导出正文、复现清单，并在报告中下载原始结果。",
} as const;
