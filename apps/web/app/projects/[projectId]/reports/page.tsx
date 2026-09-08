import { ScientificReportsIndexPage } from "../../../../features/reports/ScientificReportsIndexPage";
export default async function ReportsRoute({ params }: { params: Promise<{ projectId: string }> }) { const { projectId } = await params; return <ScientificReportsIndexPage projectId={projectId} />; }
