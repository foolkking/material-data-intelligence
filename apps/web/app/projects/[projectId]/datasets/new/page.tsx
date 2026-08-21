import { DatasetUploadPage } from "../../../../components/ProductPages";

export default async function DatasetUploadRoute({ params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  return <DatasetUploadPage projectId={projectId} />;
}
