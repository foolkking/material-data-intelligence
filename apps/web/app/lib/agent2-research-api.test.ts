import { afterEach, describe, expect, it, vi } from "vitest";

import {
  createAgent2ResearchTurn,
  normalizeAgent2TurnDetail,
  normalizeAgent2TurnListItem,
} from "./agent2-research-api";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("Agent2 ResearchTurn list normalization", () => {
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
});
