import { ScientificWorkspaceShell } from "../../components/workspace/ScientificWorkspaceShell";

export default async function ScientificWorkspacePage({ params }: { params: Promise<{ workspaceId: string }> }) {
  const { workspaceId } = await params;
  return <ScientificWorkspaceShell workspaceId={workspaceId} />;
}
