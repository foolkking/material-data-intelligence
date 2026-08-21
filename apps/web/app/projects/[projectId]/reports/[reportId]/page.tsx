import { ReportReaderPage } from "../../../../components/ResearchPages";
export default async function ReportReaderRoute({ params }: { params: Promise<{ projectId: string; reportId: string }> }) { const { projectId, reportId } = await params; return <ReportReaderPage projectId={projectId} reportId={reportId} />; }
