import { redirect } from "next/navigation";

export default async function DatasetPage({ params }: { params: Promise<{ projectId: string; datasetId: string }> }) {
  const resolved = await params;
  redirect(
    `/projects/${encodeURIComponent(resolved.projectId)}/data?dataset=${encodeURIComponent(resolved.datasetId)}`,
  );
}
