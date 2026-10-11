import { afterEach, expect, it, vi } from "vitest";
import { createPlannerJobInterpretation } from "./planner-api";

afterEach(() => vi.unstubAllGlobals());

it("passes cancellation to transport without including it in the interpretation payload", async () => {
  const fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify({ outcome: "PROVIDER_FAILED" }), { status: 200 }));
  vi.stubGlobal("fetch", fetch);
  const controller = new AbortController();
  await createPlannerJobInterpretation("job_1", "hash", { mode: "STRICT_PROVIDER", idempotencyKey: "same-job", signal: controller.signal });
  expect(fetch.mock.calls[0][1].signal).toBe(controller.signal);
  expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({ mode: "STRICT_PROVIDER", expectedPlanHash: "hash", idempotencyKey: "same-job" });
});
