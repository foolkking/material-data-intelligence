import { ReportsPage } from "../../../components/ResearchPages";
export default async function ReportsRoute({ params }: { params: Promise<{ projectId: string }> }) { const { projectId } = await params; return <ReportsPage projectId={projectId} />; }
