import { expect, it } from "vitest";
import { savedXrdTableRows } from "./scientific-xrd-table";

it("preserves saved peak order, exact values, multiple structures and missing fields", () => {
  const payload = { schema_version: "phase10e4.xrd_pattern.v1", pattern: { peaks: [
    { structureId: "a", two_theta_deg: 20.498535, intensity: 100, d_spacing_angstrom: 4.332692, hkls: [{ hkl: [0, 1, -1] }, { hkl: [1, 0, 1] }] },
    null, { structureId: "b", two_theta_deg: 14, intensity: 0 },
  ] } };
  const original = JSON.stringify(payload);
  expect(savedXrdTableRows(payload)).toEqual([
    { structureId: "a", "2θ (°)": 20.498535, "相对强度": 100, "晶面 hkl": "(0 1 -1) · (1 0 1)", "晶面间距 (Å)": 4.332692 },
    { structureId: "b", "2θ (°)": 14, "相对强度": 0, "晶面 hkl": "—", "晶面间距 (Å)": undefined },
  ]);
  expect(JSON.stringify(payload)).toBe(original);
});

it("requires the supported saved schema and omits a redundant single-structure column", () => {
  expect(savedXrdTableRows({ pattern: { peaks: [] } })).toBeNull();
  expect(savedXrdTableRows({ schema_version: "phase10e4.xrd_pattern.v1", pattern: { peaks: [{ structureId: "only", intensity: 0 }] } })?.[0]).not.toHaveProperty("structureId");
});
