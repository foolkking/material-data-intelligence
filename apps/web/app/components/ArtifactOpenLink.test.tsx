import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import {
  ArtifactOpenLink,
  isTrustedArtifactContentHref,
} from "./ArtifactOpenLink";

describe("ArtifactOpenLink", () => {
  it("opens trusted persisted Artifact content through a native browser link", () => {
    render(
      <ArtifactOpenLink href="/api/planner/jobs/job-1/artifacts/artifact-1/content">
        打开权威 Artifact
      </ArtifactOpenLink>,
    );

    expect(screen.getByRole("link", { name: "打开权威 Artifact" })).toHaveAttribute(
      "href",
      "/api/planner/jobs/job-1/artifacts/artifact-1/content",
    );
    expect(screen.getByRole("link", { name: "打开权威 Artifact" })).toHaveAttribute(
      "target",
      "_blank",
    );
    expect(screen.getByRole("link", { name: "打开权威 Artifact" })).toHaveAttribute(
      "rel",
      "noopener noreferrer",
    );
  });

  it("fails closed for non-Artifact routes", () => {
    const { container } = render(
      <ArtifactOpenLink href="/projects/project-1/research">
        不受信任入口
      </ArtifactOpenLink>,
    );

    expect(container).toBeEmptyDOMElement();
    expect(isTrustedArtifactContentHref("https://example.com/artifact")).toBe(false);
  });
});
