import { afterEach, expect, it, vi } from "vitest";
import { createHash } from "node:crypto";

import { invalidateProjectHistory, uploadDatasetFiles } from "./planner-api";

afterEach(() => {
  invalidateProjectHistory();
  vi.unstubAllGlobals();
});

it("hashes a large upload in bounded slices without reading the whole File", async () => {
  const payload = new Uint8Array(3 * 1024 * 1024 + 17);
  for (let index = 0; index < payload.length; index += 1) {
    payload[index] = index % 251;
  }
  const blob = new Blob([payload]);
  const wholeFileRead = vi.fn(async () => {
    throw new Error("whole-file arrayBuffer must not be used");
  });
  const slice = vi.fn((start?: number, end?: number) => blob.slice(start, end));
  const file = {
    name: "large-materials.bin",
    size: payload.byteLength,
    type: "application/octet-stream",
    arrayBuffer: wholeFileRead,
    slice,
  } as unknown as File;
  let declaredHash = "";
  let declaredBytes = 0;

  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
    const url = String(input);
    if (url.includes("/upload-sessions") && init?.method === "POST" && !url.includes("/complete")) {
      const body = JSON.parse(String(init.body)) as {
        files: Array<{ clientFileId: string; byteSize: number; sha256: string }>;
      };
      declaredHash = body.files[0].sha256;
      declaredBytes = body.files[0].byteSize;
      return new Response(JSON.stringify({
        uploadSessionId: "session-m4-02",
        files: [{ clientFileId: body.files[0].clientFileId, fileId: "file-m4-02" }],
      }), { status: 200 });
    }
    if (url.includes("/files/file-m4-02") && init?.method === "PUT") {
      return new Response(JSON.stringify({
        byteSize: declaredBytes,
        sha256: declaredHash,
      }), { status: 200 });
    }
    if (url.includes("/complete") && init?.method === "POST") {
      return new Response(JSON.stringify({
        id: "dataset-m4-02",
        datasetId: "dataset-m4-02",
        projectId: "project-m4-02",
        name: "F13 bounded upload",
        status: "profile_ready",
      }), { status: 200 });
    }
    throw new Error(`Unexpected fetch: ${url}`);
  }));

  await uploadDatasetFiles(
    "project-m4-02",
    "F13 bounded upload",
    [{ file }],
  );

  expect(wholeFileRead).not.toHaveBeenCalled();
  expect(slice).toHaveBeenCalledTimes(4);
  for (const call of slice.mock.calls) {
    expect(Number(call[1]) - Number(call[0])).toBeLessThanOrEqual(1024 * 1024);
  }
  expect(declaredHash).toMatch(/^[0-9a-f]{64}$/u);
  expect(declaredHash).toBe(createHash("sha256").update(payload).digest("hex"));
});
