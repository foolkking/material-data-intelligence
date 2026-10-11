import { describe, expect, it } from "vitest";
import type { Agent2ResearchTurnResult } from "../../app/lib/agent2-research-api";
import { resultFollowUpInput } from "./result-follow-up";

describe("result follow-up intent", () => {
  const source = { project_id: "project-1", object_id: "object-1", version_id: "version-1", object_type: "structure.crystal" };
  const result = { result_id: "result-1", result_snapshot_id: "snapshot-1", research_turn_id: "turn-1", research_question: "比较晶格", source_object_refs: [source], scientific_selections: [] } as unknown as Agent2ResearchTurnResult;
  it("reuses the exact snapshot only for interpretation", () => {
    expect(resultFollowUpInput("reinterpret", result)).toMatchObject({ requested_action: "INTERPRET_RESULT", reply_to_turn_id: "turn-1", ui_context: { explicit_result_ids: ["snapshot-1"], explicit_object_refs: [source] } });
    expect(resultFollowUpInput("reinterpret", { ...result, result_snapshot_id: undefined }).ui_context?.explicit_result_ids).toEqual(["result-1"]);
  });
  it("requests a new calculation with the original question and source scope", () => {
    const input = resultFollowUpInput("rerun", result, { turn_id: "turn-1", user_message: { id: "message-1", role: "user", content: "比较晶格" } });
    expect(input.message).toContain("比较晶格");
    expect(input.reply_to_turn_id).toBe("turn-1");
    expect(input.ui_context).toMatchObject({ explicit_result_ids: [], explicit_object_refs: [source], scientific_selections: [] });
    expect(input.model_selection).toBeUndefined();
    expect(input.requested_action).toBeUndefined();
  });
});


it.each(["rerun", "reinterpret"] as const)("strips read-only version metadata from %s requests while retaining exact selection", (action) => {
  const source = { project_id: "project-1", object_id: "object-1", version_id: "version-exact", object_type: "electronic.band_structure", display_name: "能带", version_no: 7 };
  const selection = { contract_version: "1.0", object_ref: source, viewer_id: "scientific.band-structure", selection_type: "ELECTRONIC_BAND_STATE", semantic_locator: { spin_channel_id: "down", band_id: "band-3", kpoint_id: "k-90", kpoint_index: 90 }, display_label: "所选能带" };
  const result = { research_turn_id: "turn-1", research_question: "所选状态", result_snapshot_id: "snapshot-1", source_object_refs: [source], scientific_selections: [selection] } as unknown as Agent2ResearchTurnResult;
  const before = JSON.stringify(result);
  const input = resultFollowUpInput(action, result, { turn_id: "turn-1", user_message: { id: "message-1", role: "user", content: "所选状态" } });
  expect(JSON.stringify(input)).not.toContain("version_no");
  expect(input.ui_context?.explicit_object_refs[0]).toEqual({ project_id: "project-1", object_id: "object-1", version_id: "version-exact", object_type: "electronic.band_structure", display_name: "能带" });
  expect(input.ui_context?.scientific_selections[0].semantic_locator).toEqual(selection.semantic_locator);
  expect(input.ui_context?.scientific_selections[0].object_ref).toEqual(input.ui_context?.explicit_object_refs[0]);
  expect(JSON.stringify(result)).toBe(before);
});


it("reruns the exact submitted question rather than a translated model objective", () => {
  const result = { research_turn_id: "turn-1", research_question: "The selected band is 3.366 eV above Fermi", source_object_refs: [] } as unknown as Agent2ResearchTurnResult;
  const content = "请检查所选能带状态。\n不要把合成数据当作实验结果。";
  const input = resultFollowUpInput("rerun", result, { turn_id: "turn-1", user_message: { id: "message-1", role: "user", content } });
  expect(input.message).toBe(content);
  expect(input.message).not.toContain("3.366");
  expect(input.reply_to_turn_id).toBe("turn-1");
  expect(input.ui_context.explicit_result_ids).toEqual([]);
});

it("does not substitute another turn or a model objective when the original question is unavailable", () => {
  const result = { research_turn_id: "turn-1", research_question: "Model objective" } as Agent2ResearchTurnResult;
  expect(() => resultFollowUpInput("rerun", result)).toThrow("原始问题");
  for (const [turn_id, content] of [["turn-other", "不同问题"], ["turn-1", "  "]]) {
    expect(() => resultFollowUpInput("rerun", result, { turn_id, user_message: { id: "message-1", role: "user", content } })).toThrow("原始问题");
  }
});
