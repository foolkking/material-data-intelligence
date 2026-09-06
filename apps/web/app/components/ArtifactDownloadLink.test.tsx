import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import {
  artifactDownloadHref,
  ArtifactDownloadLink,
  isTrustedArtifactDownloadHref,
  sanitizeArtifactDownloadName,
} from "./ArtifactDownloadLink";

describe("ArtifactDownloadLink", () => {
  it("downloads trusted persisted Artifact content through the same-origin route", () => {
    render(
      <ArtifactDownloadLink
        href="/api/planner/jobs/job-1/artifacts/artifact-1/content"
        downloadName="figure.json"
      >
        下载权威 Artifact
      </ArtifactDownloadLink>,
    );

    const link = screen.getByRole("link", { name: "下载权威 Artifact" });
    expect(link).toHaveAttribute(
      "href",
      "/api/planner/jobs/job-1/artifacts/artifact-1/content?download=true",
    );
    expect(link).toHaveAttribute("download", "figure.json");
    expect(link).toHaveAttribute("rel", "noopener");
    expect(link).not.toHaveAttribute("target");
  });

  it("fails closed for non-Artifact routes", () => {
    const { container } = render(
      <ArtifactDownloadLink href="/projects/project-1/research">
        不受信任下载
      </ArtifactDownloadLink>,
    );

    expect(container).toBeEmptyDOMElement();
    expect(isTrustedArtifactDownloadHref("https://example.com/artifact")).toBe(false);
  });

  it("bounds download filenames without allowing path separators or control characters", () => {
    expect(sanitizeArtifactDownloadName("../figure\n.json")).toBe("-figure.json");
    expect(sanitizeArtifactDownloadName("  report.json  ")).toBe("report.json");
    expect(sanitizeArtifactDownloadName(`${"a".repeat(200)}.json`)).toHaveLength(120);
    expect(sanitizeArtifactDownloadName("..")).toBeUndefined();
    expect(
      artifactDownloadHref(
        "/api/planner/jobs/job-1/artifacts/artifact-1/content?preview=1",
      ),
    ).toBe(
      "/api/planner/jobs/job-1/artifacts/artifact-1/content?preview=1&download=true",
    );
  });
});
