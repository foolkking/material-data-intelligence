import { DatasetWorkbenchPage } from "../../../../components/DatasetWorkbenchPage";

export default async function DatasetPage({ params }: { params: Promise<{ projectId: string; datasetId: string }> }) {
  const resolved = await params;
  return <DatasetWorkbenchPage projectId={resolved.projectId} datasetId={resolved.datasetId} />;
}
