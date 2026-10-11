import { afterEach, describe, expect, it, vi } from "vitest";

import {
  Agent2AdmissionUnconfirmedError,
  Agent2ReadError,
  createAgent2ResearchTurn,
  dispatchAgent2ResearchTurn,
  getAgent2ResearchTurn,
  getAgent2ResearchTurnResult,
  getAgent2ContextManifest,
  listAgent2ResearchTurns,
  normalizeAgent2TurnDetail,
  normalizeAgent2TurnListItem,
} from "./agent2-research-api";

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
  window.sessionStorage.clear();
});

it("submits exact scientific identities without read-only version labels when editing a saved result", async () => {
  const ref = { object_id: "object-1", version_id: "version-1", project_id: "project-1", object_type: "trajectory.atomic", display_name: "轨迹", version_no: 3 };
  const selection = { contract_version: "1.0" as const, object_ref: ref, viewer_id: "trajectory.viewer", selection_type: "TRAJECTORY_FRAME", semantic_locator: { frame_id: "frame-1" }, display_label: "所选帧" };
  const input = { message: "分析当前轨迹", reply_to_turn_id: "parent", ui_context: { active_object_refs: [ref], selection_refs: [ref], explicit_object_refs: [ref], scientific_selections: [selection], explicit_result_ids: [], explicit_finding_refs: [] } };
  const original = structuredClone(input);
  const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ turn_id: "created" })));
  vi.stubGlobal("fetch", fetchMock);
  await createAgent2ResearchTurn("project-1", "session-edit", input);
  const sent = JSON.parse(fetchMock.mock.calls[0][1].body);
  for (const actual of [...sent.ui_context.active_object_refs, ...sent.ui_context.selection_refs, ...sent.ui_context.explicit_object_refs, sent.ui_context.scientific_selections[0].object_ref]) {
    expect(actual).toEqual({ object_id: ref.object_id, version_id: ref.version_id, project_id: ref.project_id, object_type: ref.object_type, display_name: ref.display_name });
  }
  expect(sent.reply_to_turn_id).toBe("parent");
  expect(sent.ui_context.scientific_selections[0].semantic_locator).toEqual(selection.semantic_locator);
  expect(input).toEqual(original);
});

describe("Agent2 ResearchTurn list normalization", () => {
  const pagedTurn = (sequence: number) => ({
    id: `turn-${sequence}`, project_id: "p", research_session_id: "s", sequence_no: sequence,
    parent_turn_id: sequence > 1 ? `turn-${sequence - 1}` : null, status: "COMPLETED",
    messages: [{ id: `question-${sequence}`, role: "USER", content: `问题 ${sequence}`, created_at: "2026-10-08T00:00:00Z" }],
    created_at: "2026-10-08T00:00:00Z",
  });

  it("reads beyond the first 50 turns so later branches and the latest result remain reachable", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(Response.json({ items: Array.from({ length: 50 }, (_, index) => pagedTurn(index + 1)), next_cursor: 50 }))
      .mockResolvedValueOnce(Response.json({ items: [pagedTurn(51)], next_cursor: null }));
    vi.stubGlobal("fetch", fetchMock);
    const turns = await listAgent2ResearchTurns("p", "s");
    expect(turns).toHaveLength(51);
    expect(turns.at(-1)).toMatchObject({ turn_id: "turn-51", parent_turn_id: "turn-50", user_message: { content: "问题 51" } });
    expect(fetchMock.mock.calls.map(call => call[0])).toEqual([
      "/api/api/projects/p/research/sessions/s/turns",
      "/api/api/projects/p/research/sessions/s/turns?cursor=50",
    ]);
  });

  it("rejects a failed later page instead of returning an apparently complete partial directory", async () => {
    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce(Response.json({ items: [pagedTurn(1)], next_cursor: 1 }))
      .mockResolvedValueOnce(new Response(null, { status: 403 })));
    await expect(listAgent2ResearchTurns("p", "s")).rejects.toMatchObject({ status: 403 });
  });

  it("stops pagination when the owner cancels even if the prior fetch ignores cancellation", async () => {
    const controller = new AbortController();
    const fetchMock = vi.fn().mockImplementation(async () => {
      controller.abort();
      return Response.json({ items: [pagedTurn(1)], next_cursor: 1 });
    });
    vi.stubGlobal("fetch", fetchMock);
    await expect(listAgent2ResearchTurns("p", "s", { signal: controller.signal })).rejects.toMatchObject({ name: "AbortError" });
    expect(fetchMock).toHaveBeenCalledOnce();
  });

  it.each([0, -1, 1.5, "1", 2])("rejects an invalid next cursor %s rather than skipping or looping", async next_cursor => {
    const fetchMock = vi.fn().mockResolvedValue(Response.json({ items: [pagedTurn(1)], next_cursor }));
    vi.stubGlobal("fetch", fetchMock);
    await expect(listAgent2ResearchTurns("p", "s")).rejects.toThrow("directory unavailable");
    expect(fetchMock).toHaveBeenCalledOnce();
  });

  it("rejects a repeated page cursor", async () => {
    const fetchMock = vi.fn().mockImplementation(async () => Response.json({ items: [pagedTurn(1)], next_cursor: 1 }));
    vi.stubGlobal("fetch", fetchMock);
    await expect(listAgent2ResearchTurns("p", "s")).rejects.toThrow("directory unavailable");
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it.each([409, 500])("only identifies the explicit not-ready contract on HTTP %s", async status => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({detail:{code:"SCIENTIFIC_RESULT_NOT_READY",summary:"untrusted diagnostic"}}),{status})));
    await expect(getAgent2ResearchTurnResult("t")).rejects.toMatchObject({status,code:status===409 ? "SCIENTIFIC_RESULT_NOT_READY" : undefined});
  });
  it("distinguishes a confirmed empty directory from an absent directory payload", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(new Response(JSON.stringify({ items: [] }))).mockResolvedValueOnce(new Response(JSON.stringify({}))));
    await expect(listAgent2ResearchTurns("p", "s")).resolves.toEqual([]);
    await expect(listAgent2ResearchTurns("p", "s")).rejects.toThrow("directory unavailable");
  });

  it("forwards cancellation to context and directory reads", async () => {
    const signal = new AbortController().signal;
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ items: [] })));
    vi.stubGlobal("fetch", fetchMock);
    await listAgent2ResearchTurns("p", "s", { signal });
    fetchMock.mockResolvedValue(new Response(JSON.stringify({ turn_id: "t" })));
    await getAgent2ContextManifest("t", { signal });
    expect(fetchMock.mock.calls.map((call) => call[1].signal)).toEqual([signal, signal]);
  });

  it("projects the authoritative user message without guessing from the Turn id", () => {
    expect(
      normalizeAgent2TurnListItem({
        id: "turn-explicit",
        research_session_id: "session-1",
        project_id: "project-1",
        sequence_no: 4,
        parent_turn_id: "turn-parent",
        status: "COMPLETED",
        messages: [
          {
            id: "message-user",
            role: "USER",
            content: "比较 mat-2 的 band_gap。",
            created_at: "2026-08-30T10:00:00Z",
          },
          {
            id: "message-assistant",
            role: "ASSISTANT",
            content: "权威结果已生成。",
            created_at: "2026-08-30T10:01:00Z",
          },
        ],
        created_at: "2026-08-30T10:00:00Z",
      }),
    ).toEqual({
      turn_id: "turn-explicit",
      id: "turn-explicit",
      research_session_id: "session-1",
      project_id: "project-1",
      sequence_no: 4,
      parent_turn_id: "turn-parent",
      status: "COMPLETED",
      user_message: {
        id: "message-user",
        role: "user",
        content: "比较 mat-2 的 band_gap。",
      },
      message_ids: ["message-user", "message-assistant"],
      created_at: "2026-08-30T10:00:00Z",
    });
  });

  it("fails closed when a listed Turn has no authoritative user message", () => {
    expect(() =>
      normalizeAgent2TurnListItem({
        id: "turn-invalid",
        research_session_id: "session-1",
        project_id: "project-1",
        sequence_no: 5,
        parent_turn_id: null,
        status: "FAILED",
        messages: [],
        created_at: "2026-08-30T10:00:00Z",
      }),
    ).toThrow("缺少权威用户消息");
  });

  it("normalizes an exact Turn detail without losing scientific scope", () => {
    expect(
      normalizeAgent2TurnDetail({
        id: "turn-failed",
        research_session_id: "session-1",
        project_id: "project-1",
        sequence_no: 6,
        parent_turn_id: "turn-parent",
        status: "FAILED",
        messages: [
          {
            id: "message-failed",
            role: "USER",
            content: "重新分析精确版本。",
            created_at: "2026-08-30T10:00:00Z",
          },
        ],
        context: {
          scope: [
            {
              object_id: "object-1",
              version_id: "version-1",
              project_id: "project-1",
              object_type: "structure.crystal",
            },
          ],
          selection: [],
          scientific_selection: [],
        },
        created_at: "2026-08-30T10:00:00Z",
      }),
    ).toMatchObject({
      turn_id: "turn-failed",
      user_message: { id: "message-failed", content: "重新分析精确版本。" },
      context: {
        scope: [
          {
            object_id: "object-1",
            version_id: "version-1",
          },
        ],
      },
    });
  });
});

describe("Agent2 ResearchTurn admission errors", () => {
  const pendingInput = {
    message: "核对尚未确认的请求",
    admission_key: "first-click",
    ui_context: {
      active_object_refs: [], selection_refs: [], scientific_selections: [],
      explicit_object_refs: [], explicit_result_ids: [], explicit_finding_refs: [],
    },
    model_selection: { provider: "personal", model: "deepseek-v4-pro", thinking_mode: "standard" as const },
  };

  async function loseAdmissionResponse(sessionId: string) {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    const result = expect(createAgent2ResearchTurn("project-1", sessionId, pendingInput)).rejects.toBeInstanceOf(Agent2AdmissionUnconfirmedError);
    await vi.advanceTimersByTimeAsync(1000);
    await result;
  }

  it.each([401, 403, 409, 422, 429])("retains the original identity when a lost response is followed by HTTP %s", async status => {
    vi.useFakeTimers();
    const sessionId = `session-uncertain-then-${status}`;
    const fetchMock = vi.fn().mockRejectedValueOnce(new TypeError("Network interrupted"))
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: "Current attempt rejected" }), { status }));
    vi.stubGlobal("fetch", fetchMock);
    const first = createAgent2ResearchTurn("project-1", sessionId, pendingInput).catch(reason => reason);
    await vi.advanceTimersByTimeAsync(250);
    expect(await first).toMatchObject({ name: "Agent2AdmissionUnconfirmedError", rejectionStatus: status });
    vi.resetModules();
    const resume = (await import("./agent2-research-api")).createAgent2ResearchTurn;
    fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({ turn_id: "already-accepted" }), { status: 202 }));
    await resume("project-1", sessionId, { ...pendingInput, admission_key: "retry-after-recovery" });
    expect(JSON.parse(fetchMock.mock.calls[2][1].body).admission_key).toBe("first-click");
  });

  it.each(["server", "truncated", "invalid-acceptance"])("keeps %s uncertainty through a later denial", async fault => {
    vi.useFakeTimers();
    const response = fault === "server" ? new Response("upstream failure", { status: 503 })
      : new Response(fault === "truncated" ? '{"turn_id":' : '{}', { status: 202 });
    const fetchMock = vi.fn().mockResolvedValueOnce(response).mockResolvedValueOnce(new Response(null, { status: 409 }));
    vi.stubGlobal("fetch", fetchMock);
    const session = `session-${fault}-then-denial`;
    const result = createAgent2ResearchTurn("project-1", session, pendingInput).catch(reason => reason);
    await vi.advanceTimersByTimeAsync(250);
    expect(await result).toMatchObject({ name: "Agent2AdmissionUnconfirmedError", rejectionStatus: 409 });
    fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({ turn_id: "original" }), { status: 202 }));
    await createAgent2ResearchTurn("project-1", session, { ...pendingInput, admission_key: "manual-retry" });
    expect(JSON.parse(fetchMock.mock.calls[2][1].body).admission_key).toBe("first-click");
  });

  it("retains previously uncertain identity through successive denied manual retries", async () => {
    vi.useFakeTimers();
    const session = "session-successive-denials";
    await loseAdmissionResponse(session);
    const fetchMock = vi.fn().mockResolvedValueOnce(new Response(null, { status: 429 }))
      .mockResolvedValueOnce(new Response(null, { status: 401 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ turn_id: "original" }), { status: 202 }));
    vi.stubGlobal("fetch", fetchMock);
    await expect(createAgent2ResearchTurn("project-1", session, { ...pendingInput, admission_key: "retry-1" })).rejects.toMatchObject({ rejectionStatus: 429 });
    await expect(createAgent2ResearchTurn("project-1", session, { ...pendingInput, admission_key: "retry-2" })).rejects.toMatchObject({ rejectionStatus: 401 });
    await createAgent2ResearchTurn("project-1", session, { ...pendingInput, admission_key: "retry-3" });
    expect(fetchMock.mock.calls.map(call => JSON.parse(call[1].body).admission_key)).toEqual(Array(3).fill("first-click"));
  });

  it.each([401, 403, 409, 422, 429])("keeps the identity after an initial HTTP %s denial until acceptance is verified", async status => {
    const session = `session-initial-denial-${status}`;
    const fetchMock = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify({ detail: "本次请求暂时无法接收。" }), { status }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ turn_id: "confirmed" }), { status: 202 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ turn_id: "intentional-repeat" }), { status: 202 }));
    vi.stubGlobal("fetch", fetchMock);
    await expect(createAgent2ResearchTurn("project-1", session, pendingInput)).rejects.toThrow("本次请求暂时无法接收。");
    await createAgent2ResearchTurn("project-1", session, { ...pendingInput, admission_key: "retry-after-access-restored" });
    await createAgent2ResearchTurn("project-1", session, { ...pendingInput, admission_key: "intentional-repeat" });
    expect(fetchMock.mock.calls.map(call => JSON.parse(call[1].body).admission_key)).toEqual(["first-click", "first-click", "intentional-repeat"]);
  });

  it.each(["project_id", "research_session_id", "parent_turn_id"])("rejects a mismatched accepted %s and recovers the same admission", async (field) => {
    vi.useFakeTimers();
    const accepted = { turn_id: "accepted-turn", project_id: "project-1", research_session_id: "session-scope", parent_turn_id: "parent-1" };
    const fetchMock = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify({ ...accepted, [field]: "foreign" }), { status: 202 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(accepted), { status: 202 }));
    vi.stubGlobal("fetch", fetchMock);
    const result = createAgent2ResearchTurn("project-1", "session-scope", { ...pendingInput, reply_to_turn_id: "parent-1" });
    await vi.advanceTimersByTimeAsync(1000);
    await expect(result).resolves.toMatchObject(accepted);
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(fetchMock.mock.calls[0][1].body).toBe(fetchMock.mock.calls[1][1].body);
  });

  it.each([false, true])("reuses unresolved identity on a manual retry with module reload=%s", async (reload) => {
    vi.useFakeTimers();
    await loseAdmissionResponse("session-manual");
    const fetchMock = vi.fn().mockImplementation(async () => new Response(JSON.stringify({ turn_id: "accepted-on-first-click" }), { status: 202 }));
    vi.stubGlobal("fetch", fetchMock);
    if (reload) vi.resetModules();
    const retry = reload ? (await import("./agent2-research-api")).createAgent2ResearchTurn : createAgent2ResearchTurn;
    await expect(retry("project-1", "session-manual", { ...pendingInput, admission_key: "second-click" })).resolves.toMatchObject({ turn_id: "accepted-on-first-click" });
    expect(JSON.parse(fetchMock.mock.calls[0][1].body).admission_key).toBe("first-click");
    // After confirmation an intentional repeat is a new request.
    await retry("project-1", "session-manual", { ...pendingInput, admission_key: "intentional-repeat" });
    expect(JSON.parse(fetchMock.mock.calls[1][1].body).admission_key).toBe("intentional-repeat");
  });

  it.each(["message", "model", "scope", "parent", "session", "project", "action"])("keeps a changed %s distinct from the unresolved request", async (change) => {
    vi.useFakeTimers();
    await loseAdmissionResponse("session-distinct");
    const fetchMock = vi.fn().mockImplementation(async () => new Response(JSON.stringify({ turn_id: "separate-request" }), { status: 202 }));
    vi.stubGlobal("fetch", fetchMock);
    await createAgent2ResearchTurn(change === "project" ? "project-2" : "project-1", change === "session" ? "session-2" : "session-distinct", {
      ...pendingInput, admission_key: "new-click",
      ...(change === "message" ? { message: "另一个问题" } : {}),
      ...(change === "model" ? { model_selection: { ...pendingInput.model_selection, thinking_mode: "deep" as const } } : {}),
      ...(change === "scope" ? { ui_context: { ...pendingInput.ui_context, explicit_result_ids: ["another-result"] } } : {}),
      ...(change === "parent" ? { reply_to_turn_id: "parent-turn" } : {}),
      ...(change === "action" ? { requested_action: "INTERPRET_RESULT" as const } : {}),
    });
    expect(JSON.parse(fetchMock.mock.calls[0][1].body).admission_key).toBe("new-click");
    await createAgent2ResearchTurn("project-1", "session-distinct", { ...pendingInput, admission_key: "resume-original" });
    expect(JSON.parse(fetchMock.mock.calls[1][1].body).admission_key).toBe("first-click");
  });

  it.each(["read and write", "write only"])("retains identity in memory when browser storage blocks %s", async (failure) => {
    vi.useFakeTimers();
    const read = failure === "read and write" ? vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => { throw new Error("Storage blocked"); }) : null;
    const write = vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => { throw new Error("Storage blocked"); });
    try {
      await loseAdmissionResponse("session-blocked-storage");
      const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ turn_id: "recovered" }), { status: 202 }));
      vi.stubGlobal("fetch", fetchMock);
      await createAgent2ResearchTurn("project-1", "session-blocked-storage", { ...pendingInput, admission_key: "later-click" });
      expect(JSON.parse(fetchMock.mock.calls[0][1].body).admission_key).toBe("first-click");
    } finally {
      read?.mockRestore();
      write.mockRestore();
    }
  });

  it("does not treat a server error after admission as a definitive rejection", async () => {
    vi.useFakeTimers();
    const fetchMock = vi.fn().mockResolvedValueOnce(new Response("Internal Server Error", { status: 500 })).mockResolvedValueOnce(new Response(JSON.stringify({ turn_id: "recovered-server-error" }), { status: 202 }));
    vi.stubGlobal("fetch", fetchMock);
    const result = createAgent2ResearchTurn("project-1", "session-500", pendingInput);
    await vi.advanceTimersByTimeAsync(250);
    await expect(result).resolves.toMatchObject({ turn_id: "recovered-server-error" });
    expect(fetchMock.mock.calls[1][1].body).toBe(fetchMock.mock.calls[0][1].body);
  });

  it("preserves the HTTP status for bounded Result-read decisions", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "服务暂时不可用。" }), {
          status: 503,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(
      getAgent2ResearchTurnResult("turn-unavailable"),
    ).rejects.toEqual(expect.objectContaining<Partial<Agent2ReadError>>({
      name: "Agent2ReadError",
      status: 503,
    }));
  });

  it("renders the typed project resource limit as a bounded product message", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: {
              code: "PROJECT_ACTIVE_RESEARCH_LIMIT",
              summary: "当前项目已有 4 项进行中的研究。请等待完成或先停止一项后再试。",
              limit: 4,
              active: 4,
            },
          }),
          {
            status: 429,
            headers: { "Content-Type": "application/json" },
          },
        ),
      ),
    );

    await expect(
      createAgent2ResearchTurn("project-1", "session-1", {
        message: "继续分析。",
        ui_context: {
          active_object_refs: [],
          selection_refs: [],
          scientific_selections: [],
          explicit_object_refs: [],
          explicit_result_ids: [],
          explicit_finding_refs: [],
        },
      }),
    ).rejects.toThrow("当前项目已有 4 项进行中的研究。请等待完成或先停止一项后再试。");
  });

  it("retries a lost admission response with the same durable admission key", async () => {
    vi.useFakeTimers();
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new TypeError("Failed to fetch"))
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            turn_id: "turn-recovered",
            research_session_id: "session-1",
            project_id: "project-1",
            sequence_no: 1,
            status: "RECEIVED",
            user_message: {
              id: "message-1",
              role: "USER",
              content: "重启后恢复",
            },
            created_at: "2026-09-19T00:00:00Z",
          }),
          { status: 202, headers: { "Content-Type": "application/json" } },
        ),
      );
    vi.stubGlobal("fetch", fetchMock);

    const promise = createAgent2ResearchTurn("project-1", "session-1", {
      message: "重启后恢复",
      admission_key: "m4-01-retry-key",
      ui_context: {
        active_object_refs: [],
        selection_refs: [],
        scientific_selections: [],
        explicit_object_refs: [],
        explicit_result_ids: [],
        explicit_finding_refs: [],
      },
    });
    await vi.advanceTimersByTimeAsync(250);
    await expect(promise).resolves.toMatchObject({ turn_id: "turn-recovered" });

    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(JSON.parse(fetchMock.mock.calls[0][1].body as string)).toMatchObject({
      admission_key: "m4-01-retry-key",
    });
    expect(fetchMock.mock.calls[1][1].body).toBe(fetchMock.mock.calls[0][1].body);
    vi.useRealTimers();
  });

  it("generates one durable admission key before retrying a caller that omitted it", async () => {
    vi.useFakeTimers();
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new TypeError("Failed to fetch"))
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            turn_id: "turn-recovered-with-generated-key",
            research_session_id: "session-1",
            project_id: "project-1",
            sequence_no: 1,
            status: "RECEIVED",
            user_message: { id: "message-1", role: "USER", content: "断线后恢复" },
            created_at: "2026-09-19T00:00:00Z",
          }),
          { status: 202, headers: { "Content-Type": "application/json" } },
        ),
      );
    vi.stubGlobal("fetch", fetchMock);

    const promise = createAgent2ResearchTurn("project-1", "session-1", {
      message: "断线后恢复",
      ui_context: {
        active_object_refs: [],
        selection_refs: [],
        scientific_selections: [],
        explicit_object_refs: [],
        explicit_result_ids: [],
        explicit_finding_refs: [],
      },
    });
    await vi.advanceTimersByTimeAsync(250);
    await expect(promise).resolves.toMatchObject({
      turn_id: "turn-recovered-with-generated-key",
    });

    expect(fetchMock).toHaveBeenCalledTimes(2);
    const firstBody = JSON.parse(fetchMock.mock.calls[0][1].body as string);
    const secondBody = JSON.parse(fetchMock.mock.calls[1][1].body as string);
    expect(firstBody.admission_key).toEqual(expect.any(String));
    expect(firstBody.admission_key.length).toBeGreaterThan(0);
    expect(secondBody.admission_key).toBe(firstBody.admission_key);
  });

  it("replays the same admission when an accepted response body is truncated", async () => {
    vi.useFakeTimers();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response("{\"turn_id\":", {
          status: 202,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            turn_id: "turn-replayed-after-truncation",
            research_session_id: "session-1",
            project_id: "project-1",
            sequence_no: 1,
            status: "RECEIVED",
            user_message: { id: "message-1", role: "USER", content: "响应中断" },
            created_at: "2026-09-19T00:00:00Z",
          }),
          { status: 202, headers: { "Content-Type": "application/json" } },
        ),
      );
    vi.stubGlobal("fetch", fetchMock);

    const promise = createAgent2ResearchTurn("project-1", "session-1", {
      message: "响应中断",
      admission_key: "truncated-response-key",
      ui_context: {
        active_object_refs: [],
        selection_refs: [],
        scientific_selections: [],
        explicit_object_refs: [],
        explicit_result_ids: [],
        explicit_finding_refs: [],
      },
    });
    await vi.advanceTimersByTimeAsync(250);
    await expect(promise).resolves.toMatchObject({
      turn_id: "turn-replayed-after-truncation",
    });
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(fetchMock.mock.calls[1][1].body).toBe(fetchMock.mock.calls[0][1].body);
  });

  it.each(["network", "gateway", "truncated", "missing identity", "null body"])(
    "bounds %s recovery and does not claim the admission was rejected",
    async (failure) => {
    vi.useFakeTimers();
    const fetchMock = vi.fn().mockImplementation(async () => {
      if (failure === "network") throw new TypeError("Failed to fetch");
      return new Response(
        failure === "missing identity" ? "{}" : failure === "null body" ? "null" : '{"turn_id":',
        { status: failure === "gateway" ? 504 : 202 },
      );
    });
    vi.stubGlobal("fetch", fetchMock);

    const promise = createAgent2ResearchTurn("project-1", "session-1", {
      message: "无法确认",
      admission_key: "uncertain-admission-key",
      ui_context: {
        active_object_refs: [],
        selection_refs: [],
        scientific_selections: [],
        explicit_object_refs: [],
        explicit_result_ids: [],
        explicit_finding_refs: [],
      },
    });
    const rejection = expect(promise).rejects.toEqual(new Agent2AdmissionUnconfirmedError());
    await vi.advanceTimersByTimeAsync(250);
    await vi.advanceTimersByTimeAsync(750);
    await rejection;
    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(new Set(fetchMock.mock.calls.map(([, request]) => request.body)).size).toBe(1);
    await vi.advanceTimersByTimeAsync(30_000);
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it.each([401, 403, 409, 422, 429])("does not retry a definitive %s rejection", async (status) => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(
      JSON.stringify({ detail: "请检查请求后重试。" }), { status },
    ));
    vi.stubGlobal("fetch", fetchMock);
    await expect(createAgent2ResearchTurn("project-1", "session-1", {
      message: "分析材料",
      ui_context: {
        active_object_refs: [], selection_refs: [], scientific_selections: [],
        explicit_object_refs: [], explicit_result_ids: [], explicit_finding_refs: [],
      },
    })).rejects.toThrow("请检查请求后重试。");
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("explains structured validation rejection without echoing rejected inputs", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({
      detail: [{ loc: ["body", "ui_context"], type: "extra_forbidden", input: "private-rejected-value" }],
    }), { status: 422 }));
    vi.stubGlobal("fetch", fetchMock);
    await expect(createAgent2ResearchTurn("project-1", "session-1", {
      message: "保留这个问题",
      ui_context: {
        active_object_refs: [], selection_refs: [], scientific_selections: [],
        explicit_object_refs: [], explicit_result_ids: [], explicit_finding_refs: [],
      },
    })).rejects.toThrow("研究请求的参数未通过校验。问题已保留，请检查来源和模型设置后重试。");
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it.each(["headers", "body"])("bounds an admission that stalls at %s and aborts each attempt", async (stage) => {
    vi.useFakeTimers();
    const fetchMock = vi.fn().mockImplementation((_url: string, request: RequestInit) => {
      if (stage === "headers") return new Promise(() => {});
      return Promise.resolve({
        ok: true, status: 202,
        json: () => new Promise(() => {}),
      });
    });
    vi.stubGlobal("fetch", fetchMock);
    const pending = createAgent2ResearchTurn("project-1", "session-1", {
      message: "分析材料",
      admission_key: "deadline-stable-key",
      ui_context: {
        active_object_refs: [], selection_refs: [], scientific_selections: [],
        explicit_object_refs: [], explicit_result_ids: [], explicit_finding_refs: [],
      },
    });
    const rejection = expect(pending).rejects.toBeInstanceOf(Agent2AdmissionUnconfirmedError);
    await vi.advanceTimersByTimeAsync(10_000);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][1].signal.aborted).toBe(true);
    await vi.advanceTimersByTimeAsync(21_000);
    await rejection;
    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(fetchMock.mock.calls.every(([, request]) => request.signal.aborted)).toBe(true);
    expect(new Set(fetchMock.mock.calls.map(([, request]) => request.body)).size).toBe(1);
    expect(vi.getTimerCount()).toBe(0);
  });

  it("reports an explicit rejection even if its explanation stalls", async () => {
    vi.useFakeTimers();
    const fetchMock = vi.fn().mockResolvedValue({ ok: false, status: 422, json: () => new Promise(() => {}) });
    vi.stubGlobal("fetch", fetchMock);
    const pending = createAgent2ResearchTurn("project-1", "session-1", {
      message: "分析材料",
      ui_context: {
        active_object_refs: [], selection_refs: [], scientific_selections: [],
        explicit_object_refs: [], explicit_result_ids: [], explicit_finding_refs: [],
      },
    });
    const rejection = expect(pending).rejects.toThrow("研究请求失败 (422)");
    await vi.advanceTimersByTimeAsync(10_000);
    await rejection;
    expect(fetchMock).toHaveBeenCalledTimes(1);
    await vi.runOnlyPendingTimersAsync(); // Flush the browser storage event.
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(vi.getTimerCount()).toBe(0);
  });
});

describe("Agent2 session expiry", () => {
  it.each([
    ["read", () => getAgent2ResearchTurn("turn-expired")],
    [
      "create",
      () =>
        createAgent2ResearchTurn("project-1", "session-1", {
          message: "继续分析。",
          ui_context: {
            active_object_refs: [],
            selection_refs: [],
            scientific_selections: [],
            explicit_object_refs: [],
            explicit_result_ids: [],
            explicit_finding_refs: [],
          },
        }),
    ],
    ["dispatch", () => dispatchAgent2ResearchTurn("turn-expired")],
  ])("emits the shared session-expired event for %s requests", async (_label, operation) => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "登录状态已失效。" }), {
          status: 401,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );
    const expired = vi.fn();
    window.addEventListener("mdi:session-expired", expired);

    await expect(operation()).rejects.toThrow();

    expect(expired).toHaveBeenCalledTimes(1);
    window.removeEventListener("mdi:session-expired", expired);
  });
});
