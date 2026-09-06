import assert from "node:assert/strict";
import test from "node:test";

const origin = process.env.MDI_FRONTEND_URL || "http://127.0.0.1:3000";
const route =
  process.env.MDI_FRONTEND_TEST_ROUTE ||
  "/projects/project_0001_d286007db78e427e/data?dataset=dataset_0001_a0b09e3324e44ca4";

test("current frontend route serves every referenced Next static asset", async () => {
  const pageResponse = await fetch(new URL(route, origin));
  assert.equal(pageResponse.status, 200);
  const html = await pageResponse.text();
  const assets = [
    ...new Set(
      [...html.matchAll(/["']([^"']*\/_next\/static\/[^"']+)["']/gu)].map(
        (match) => match[1].replace(/\\+$/u, ""),
      ),
    ),
  ];
  assert.ok(assets.length > 0, "route did not reference Next static assets");

  const failures = [];
  for (const asset of assets) {
    const response = await fetch(new URL(asset, origin));
    if (response.status !== 200) {
      failures.push(`${response.status} ${asset}`);
    }
  }
  assert.deepEqual(failures, []);
});
