export const PROJECT_ROLES = [
  "owner",
  "admin",
  "researcher",
  "viewer",
] as const;

export type ProjectRole = (typeof PROJECT_ROLES)[number];

export type ProjectCapability =
  | "read"
  | "export"
  | "write"
  | "archive"
  | "research"
  | "purge";

const PROJECT_ROLE_CAPABILITIES: Record<
  ProjectRole,
  ReadonlySet<ProjectCapability>
> = {
  owner: new Set(["read", "export", "write", "archive", "research", "purge"]),
  admin: new Set(["read", "export", "write", "archive", "research"]),
  researcher: new Set(["read", "export", "write", "archive", "research"]),
  viewer: new Set(["read", "export"]),
};

export function isProjectRole(role: string | null | undefined): role is ProjectRole {
  return PROJECT_ROLES.includes(role as ProjectRole);
}

export function projectRoleAllows(
  role: string | null | undefined,
  capability: ProjectCapability,
): boolean {
  return isProjectRole(role) && PROJECT_ROLE_CAPABILITIES[role].has(capability);
}

export function projectRoleCapabilities(
  role: string | null | undefined,
): ReadonlySet<ProjectCapability> {
  return isProjectRole(role)
    ? PROJECT_ROLE_CAPABILITIES[role]
    : new Set<ProjectCapability>();
}
