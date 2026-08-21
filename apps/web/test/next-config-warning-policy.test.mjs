import { describe, expect, it } from "vitest";

import nextConfig from "../next.config.mjs";

describe("Next.js build warning policy", () => {
  it("suppresses only the two known glslify dynamic-require warnings", () => {
    const existing = /keep-existing-warning/u;
    const config = nextConfig.webpack({ ignoreWarnings: [existing] });

    expect(config.ignoreWarnings).toHaveLength(3);
    expect(config.ignoreWarnings[0]).toBe(existing);

    const [depsWarning, transformWarning] = config.ignoreWarnings.slice(1);
    expect(
      depsWarning.message.test(
        "Critical dependency: the request of a dependency is an expression",
      ),
    ).toBe(true);
    expect(
      depsWarning.module.test("C:\\repo\\node_modules\\glslify-deps\\sync.js"),
    ).toBe(true);
    expect(
      depsWarning.module.test("C:\\repo\\node_modules\\other\\sync.js"),
    ).toBe(false);
    expect(
      transformWarning.message.test(
        "Critical dependency: the request of a dependency is an expression",
      ),
    ).toBe(true);
    expect(
      transformWarning.module.test("/repo/node_modules/glslify/transform.js"),
    ).toBe(true);
    expect(
      transformWarning.module.test("/repo/node_modules/glslify/other.js"),
    ).toBe(false);
  });
});
