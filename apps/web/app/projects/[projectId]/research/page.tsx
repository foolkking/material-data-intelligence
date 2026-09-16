import { ResearchPage } from "../../../../features/research/ResearchPages";
type ResearchQuery = { dataset?: string | string[]; sample?: string | string[]; run?: string | string[]; turn?: string | string[]; edit?: string | string[]; retryOf?: string | string[]; retry?: string | string[]; new?: string | string[]; object?: string | string[]; version?: string | string[]; type?: string | string[]; name?: string | string[]; selection?: string | string[]; selectionLabel?: string | string[]; resultContext?: string | string[]; fromSearch?: string | string[] };
const first = (value?: string | string[]) => Array.isArray(value) ? value[0] : value;
export default async function ProjectResearchRoute({ params, searchParams }: { params: Promise<{ projectId: string }>; searchParams?: Promise<ResearchQuery> }) {
  const { projectId } = await params;
  const query = searchParams ? await searchParams : {};
  return <ResearchPage projectId={projectId} datasetId={first(query.dataset)} sampleRef={first(query.sample)} runId={first(query.run)} agent2TurnId={first(query.turn)} editTurnId={first(query.edit)} retryOfTurnId={first(query.retryOf)} retryRequested={first(query.retry) === "1"} fresh={first(query.new) === "1"} resultContextId={first(query.resultContext)} contextCandidateFromSearch={first(query.fromSearch) === "1"} viewerContext={{ objectId: first(query.object), versionId: first(query.version), objectType: first(query.type), displayName: first(query.name), selectionToken: first(query.selection), selectionLabel: first(query.selectionLabel) }} />;
}
