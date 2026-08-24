import { ScientificReportRoute } from "../../../../components/ScientificReportRoute";
export default async function ReportReaderRoute({ params }: { params: Promise<{ projectId: string; reportId: string }> }) { const { projectId, reportId } = await params; return <ScientificReportRoute projectId={projectId} reportId={reportId} />; }
