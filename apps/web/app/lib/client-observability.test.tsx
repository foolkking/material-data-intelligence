import { render, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ClientObservability } from "../components/ClientObservability";
import {
  boundedProductRoute,
  buildClientExceptionEvent,
  clientCorrelation,
} from "./client-observability";


afterEach(() => {
  vi.restoreAllMocks();
  window.history.replaceState({}, "", "/");
});

describe("client observability", () => {
  it("keeps only bounded route and scientific correlation identities", () => {
    const location = {
      pathname: "/projects/project-1/research/private/provider-payload",
      search:
        "?turnId=turn-1&jobId=job-1&contextManifestId=manifest-1&token=secret",
    } as Pick<Location, "pathname" | "search">;

    expect(boundedProductRoute(location.pathname)).toBe(
      "/projects/:projectId/research",
    );
    expect(clientCorrelation(location)).toEqual({
      projectId: "project-1",
      researchTurnId: "turn-1",
      jobId: "job-1",
      contextManifestId: "manifest-1",
    });
    const event = buildClientExceptionEvent({
      source: "unhandledrejection",
      releaseSha: "A".repeat(40),
      location,
      error: new Error(
        "password=LocalAcceptance C:\\Users\\private\\provider.json",
      ),
      clientEventId: "client-1",
    });
    const serialized = JSON.stringify(event);

    expect(event.releaseSha).toBe("a".repeat(40));
    expect(event.errorType).toBe("Error");
    expect(serialized).not.toContain("LocalAcceptance");
    expect(serialized).not.toContain("provider");
    expect(serialized).not.toContain("token");
    expect(serialized).not.toContain("Users");
  });

  it("captures an unhandled rejection once without serializing its reason", async () => {
    window.history.replaceState(
      {},
      "",
      "/projects/project-2/research?turnId=turn-2",
    );
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(new Response(null, { status: 202 }));
    render(<ClientObservability releaseSha={"b".repeat(40)} />);
    const rejection = new Event("unhandledrejection");
    Object.defineProperty(rejection, "reason", {
      value: new Error("Bearer private-token /Users/private/prompt.txt"),
    });

    window.dispatchEvent(rejection);
    window.dispatchEvent(rejection);

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    const [url, init] = fetchMock.mock.calls[0];
    const body = String(init?.body);
    expect(url).toBe("/api/api/observability/client-exceptions");
    expect(body).toContain('"route":"/projects/:projectId/research"');
    expect(body).toContain('"researchTurnId":"turn-2"');
    expect(body).not.toContain("private-token");
    expect(body).not.toContain("prompt.txt");
    expect(init?.keepalive).toBe(true);
  });
});
