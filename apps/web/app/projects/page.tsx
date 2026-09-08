import { ProjectsPage } from "../../features/projects/ProductPages";

export default async function ProjectsRoute({ searchParams }: { searchParams: Promise<{ manage?: string }> }) {
  const params = await searchParams;
  return <ProjectsPage manageProjectId={params.manage || ""} />;
}
