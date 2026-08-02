import { afterEach, describe, expect, it, vi } from "vitest";

import { supportsManagedWebGL } from "./viewerWebglCapability";

describe("supportsManagedWebGL", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("checks browser capability without allocating a WebGL context", () => {
    const getContext = vi.spyOn(HTMLCanvasElement.prototype, "getContext");
    vi.spyOn(window.navigator, "userAgent", "get").mockReturnValue("Chromium");
    vi.stubGlobal("WebGLRenderingContext", class WebGLRenderingContext {});

    expect(supportsManagedWebGL()).toBe(true);
    expect(getContext).not.toHaveBeenCalled();
  });
});
