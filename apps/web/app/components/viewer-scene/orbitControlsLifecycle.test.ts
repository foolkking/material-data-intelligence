import { describe, expect, it, vi } from "vitest";

import { captureOrbitControlsDisposer } from "./orbitControlsLifecycle";

describe("captureOrbitControlsDisposer", () => {
  it("removes the key interceptor from the root captured while connected", () => {
    const root = new EventTarget();
    const listener = vi.fn();
    const remove = vi.spyOn(root, "removeEventListener");
    const dispose = vi.fn();
    root.addEventListener("keydown", listener);
    const release = captureOrbitControlsDisposer({
      dispose,
      domElement: { getRootNode: () => root },
      _interceptControlDown: listener,
    } as never);

    release();
    release();

    expect(remove).toHaveBeenCalledWith("keydown", listener, { capture: true });
    expect(dispose).toHaveBeenCalledOnce();
  });
});
