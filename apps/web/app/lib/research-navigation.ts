export type ResearchNavigationIdentity = Readonly<{
  projectId?: string | null;
  jobId?: string | null;
  researchSessionId?: string | null;
  researchTurnId?: string | null;
  workspaceId?: string | null;
}>;

function present(value: string | null | undefined): string | null {
  const normalized = value?.trim();
  return normalized ? normalized : null;
}

export function buildResearchHref(
  identity: ResearchNavigationIdentity,
): string {
  const projectId = present(identity.projectId);
  const jobId = present(identity.jobId);
  const sessionId = present(identity.researchSessionId);
  const turnId = present(identity.researchTurnId);
  const workspaceId = present(identity.workspaceId);

  if (projectId && sessionId && turnId) {
    return `/projects/${encodeURIComponent(projectId)}/research/${encodeURIComponent(sessionId)}?turn=${encodeURIComponent(turnId)}`;
  }
  if (projectId && jobId) {
    const turnQuery = turnId
      ? `&turn=${encodeURIComponent(turnId)}`
      : "";
    return `/projects/${encodeURIComponent(projectId)}/research?run=${encodeURIComponent(jobId)}${turnQuery}`;
  }
  if (workspaceId) {
    return `/workspaces/${encodeURIComponent(workspaceId)}`;
  }
  if (projectId) {
    return `/projects/${encodeURIComponent(projectId)}/research`;
  }
  return "/projects";
}
