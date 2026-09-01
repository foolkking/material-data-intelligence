import { describe, expect, it } from "vitest";

import { buildResearchHref } from "./research-navigation";

describe("buildResearchHref", () => {
  it("prefers the authoritative session and turn over run and workspace projections", () => {
    expect(buildResearchHref({
      projectId: "project one",
      researchSessionId: "session/one",
      researchTurnId: "turn one",
      jobId: "job-one",
      workspaceId: "workspace-one",
    })).toBe(
      "/projects/project%20one/research/session%2Fone?turn=turn%20one",
    );
  });

  it("uses the project run route with an exact turn when no session is available", () => {
    expect(buildResearchHref({
      projectId: "project-1",
      jobId: "job-1",
      researchTurnId: "turn-1",
      workspaceId: "workspace-1",
    })).toBe("/projects/project-1/research?run=job-1&turn=turn-1");
  });

  it("uses the project run route without guessing a turn", () => {
    expect(buildResearchHref({
      projectId: "project-1",
      jobId: "job-1",
      workspaceId: "workspace-1",
    })).toBe("/projects/project-1/research?run=job-1");
  });

  it("keeps legacy workspace bookmarks as a bounded compatibility fallback", () => {
    expect(buildResearchHref({
      workspaceId: "legacy workspace",
    })).toBe("/workspaces/legacy%20workspace");
  });

  it("falls back to the project Research entry when no run identity exists", () => {
    expect(buildResearchHref({
      projectId: "project-1",
    })).toBe("/projects/project-1/research");
  });
});
