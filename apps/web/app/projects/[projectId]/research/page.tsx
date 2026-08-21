import { ResearchPage } from "../../../components/ResearchPages";
export default async function ProjectResearchRoute({ params, searchParams }: { params: Promise<{ projectId: string }>; searchParams?: Promise<{ run?: string | string[] }> }) {
  const { projectId } = await params;
  const query = searchParams ? await searchParams : {};
  const runId = Array.isArray(query.run) ? query.run[0] : query.run;
  return <ResearchPage projectId={projectId} runId={runId} />;
}
