import { ProjectDataPage } from "../../../../features/data/DataPages";

export default async function ProjectDataRoute({
  params,
  searchParams,
}: {
  params: Promise<{ projectId: string }>;
  searchParams: Promise<{
    dataset?: string;
    object?: string;
    version?: string;
    tableQuery?: string;
    tableSort?: string;
    tableRow?: string;
    selection?: string;
  }>;
}) {
  const [{ projectId }, query] = await Promise.all([params, searchParams]);
  return <ProjectDataPage projectId={projectId} initialDatasetId={query.dataset || ""} initialObjectId={query.object || ""} initialObjectVersionId={query.version || ""} />;
}
