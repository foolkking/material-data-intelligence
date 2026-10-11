import { act, renderHook } from "@testing-library/react";
import { beforeEach, expect, it } from "vitest";
import { useResearchMaterials } from "./use-research-materials";
import { materialsContext, type ResearchMaterials } from "./research-materials";

const value: ResearchMaterials = { items: [{ datasetId: "d", resourceId: "r", ref: { project_id: "p", object_id: "o", version_id: "exact", object_type: "structure.crystal", display_name: "Si.cif" } }], selections: [] };
beforeEach(() => sessionStorage.clear());
it("isolates drafts by branch and restores the same exact versions after reopening", () => {
  const view = renderHook(({ branch }) => useResearchMaterials("p", branch), { initialProps: { branch: "a" } });
  act(() => view.result.current.set(value));
  view.rerender({ branch: "b" }); expect(view.result.current.value).toBeNull();
  view.rerender({ branch: "a" }); expect(view.result.current.value).toEqual(value);
  view.unmount();
  const reopened = renderHook(() => useResearchMaterials("p", "a"));
  expect(reopened.result.current.value?.items[0].ref.version_id).toBe("exact");
});
it("carries selection through session creation and clears only confirmed admission keys", () => {
  const view = renderHook(({ key }) => useResearchMaterials("p", key), { initialProps: { key: "new" } });
  act(() => { view.result.current.set(value); });
  act(() => view.result.current.copyTo("session"));
  view.rerender({ key: "session" }); expect(view.result.current.value).toEqual(value);
  act(() => { view.result.current.set(null); view.result.current.clearKey("new"); });
  expect(sessionStorage.getItem("new:materials")).toBeNull(); expect(sessionStorage.getItem("session:materials")).toBeNull();
});
it("does not fall back to unrelated context when a stored selection is malformed or foreign", () => {
  sessionStorage.setItem("a:materials", JSON.stringify({ ...value, items: [{ ref: { ...value.items[0].ref, project_id: "foreign" } }] }));
  const view = renderHook(() => useResearchMaterials("p", "a"));
  expect(view.result.current.error).toContain("重新选择");
  act(() => view.result.current.set(value)); expect(view.result.current.error).toBe("");
});
it("explicit material context never carries a stale result or invents selections", () => {
  expect(materialsContext(value, "p")).toMatchObject({ explicit_object_refs: [value.items[0].ref], scientific_selections: [], explicit_result_ids: [], explicit_finding_refs: [] });
});
