import { ResearchPage } from "../../../components/ResearchPages";
type ResearchQuery = { run?: string | string[]; turn?: string | string[]; object?: string | string[]; version?: string | string[]; type?: string | string[]; name?: string | string[]; selection?: string | string[]; selectionLabel?: string | string[] };
const first = (value?: string | string[]) => Array.isArray(value) ? value[0] : value;
export default async function ProjectResearchRoute({ params, searchParams }: { params: Promise<{ projectId: string }>; searchParams?: Promise<ResearchQuery> }) {
  const { projectId } = await params;
  const query = searchParams ? await searchParams : {};
  return <ResearchPage projectId={projectId} runId={first(query.run)} agent2TurnId={first(query.turn)} viewerContext={{ objectId: first(query.object), versionId: first(query.version), objectType: first(query.type), displayName: first(query.name), selectionToken: first(query.selection), selectionLabel: first(query.selectionLabel) }} />;
}
