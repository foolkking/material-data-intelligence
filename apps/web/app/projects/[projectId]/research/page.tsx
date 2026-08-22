import { ResearchPage } from "../../../components/ResearchPages";
export default async function ProjectResearchRoute({ params, searchParams }: { params: Promise<{ projectId: string }>; searchParams?: Promise<{ run?: string | string[]; turn?: string | string[] }> }) {
  const { projectId } = await params;
  const query = searchParams ? await searchParams : {};
  const runId = Array.isArray(query.run) ? query.run[0] : query.run;
  const turnId = Array.isArray(query.turn) ? query.turn[0] : query.turn;
  return <ResearchPage projectId={projectId} runId={runId} agent2TurnId={turnId} />;
}
