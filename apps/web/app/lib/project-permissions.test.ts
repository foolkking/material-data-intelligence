import { describe, expect, it } from "vitest";

import {
  PROJECT_ROLES,
  projectRoleAllows,
  projectRoleCapabilities,
  type ProjectCapability,
} from "./project-permissions";

const expected: Record<(typeof PROJECT_ROLES)[number], ProjectCapability[]> = {
  owner: ["read", "export", "write", "archive", "research", "purge"],
  admin: ["read", "export", "write", "archive", "research"],
  researcher: ["read", "export", "write", "archive", "research"],
  viewer: ["read", "export"],
};

describe("project role capability contract", () => {
  for (const role of PROJECT_ROLES) {
    it(`${role} exposes only its authorized product actions`, () => {
      expect([...projectRoleCapabilities(role)]).toEqual(expected[role]);
      for (const capability of [
        "read",
        "export",
        "write",
        "archive",
        "research",
        "purge",
      ] satisfies ProjectCapability[]) {
        expect(projectRoleAllows(role, capability)).toBe(
          expected[role].includes(capability),
        );
      }
    });
  }

  it("does not treat platform administration or missing roles as project membership", () => {
    expect(projectRoleCapabilities("PLATFORM_ADMIN")).toEqual(new Set());
    expect(projectRoleCapabilities(undefined)).toEqual(new Set());
    expect(projectRoleAllows("PLATFORM_ADMIN", "write")).toBe(false);
    expect(projectRoleAllows(null, "read")).toBe(false);
  });
});
