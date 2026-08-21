import { ProjectDataPage } from "../../../components/ProductPages";

export default async function ProjectDataRoute({
  params,
  searchParams,
}: {
  params: Promise<{ projectId: string }>;
  searchParams: Promise<{ dataset?: string }>;
}) {
  const [{ projectId }, query] = await Promise.all([params, searchParams]);
  return <ProjectDataPage projectId={projectId} initialDatasetId={query.dataset || ""} />;
}
