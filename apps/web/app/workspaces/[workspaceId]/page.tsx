import { LegacyWorkspaceCompatibility } from "../../../features/compatibility/LegacyCompatibilityPages";

export default async function ScientificWorkspacePage({ params }: { params: Promise<{ workspaceId: string }> }) {
  const { workspaceId } = await params;
  return <LegacyWorkspaceCompatibility workspaceId={workspaceId} />;
}
