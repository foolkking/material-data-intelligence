import { ProjectOverviewPage } from "../../components/ProductPages";
export default async function ProjectRoute({ params }: { params: Promise<{ projectId: string }> }) { const { projectId } = await params; return <ProjectOverviewPage projectId={projectId} />; }
