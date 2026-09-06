import { describe, expect, it } from "vitest";
import {
  isProductRoutePath,
  projectIdFromPath,
  shouldResetProductDocumentScroll,
} from "./ProductRouteFrame";

describe("ProductRouteFrame route classification", () => {
  it("keeps the shared product shell across primary product routes", () => {
    expect(isProductRoutePath("/console")).toBe(true);
    expect(isProductRoutePath("/projects")).toBe(true);
    expect(isProductRoutePath("/projects/project-1/research")).toBe(true);
    expect(isProductRoutePath("/tasks")).toBe(true);
    expect(isProductRoutePath("/notifications")).toBe(true);
    expect(isProductRoutePath("/trash")).toBe(true);
    expect(isProductRoutePath("/account")).toBe(true);
    expect(isProductRoutePath("/admin")).toBe(true);
    expect(isProductRoutePath("/settings/models")).toBe(true);
  });

  it("leaves the landing and legacy scientific workspace layouts unframed", () => {
    expect(isProductRoutePath("/")).toBe(false);
    expect(isProductRoutePath("/workspaces/workspace-1")).toBe(false);
  });

  it("extracts one decoded project identity without guessing other paths", () => {
    expect(projectIdFromPath("/projects/project%20one/data")).toBe(
      "project one",
    );
    expect(projectIdFromPath("/tasks")).toBeUndefined();
  });

  it("resets document scroll only when the product pathname changes", () => {
    expect(
      shouldResetProductDocumentScroll(
        "/projects/project-1/reports",
        "/projects/project-1/reports/report-1",
      ),
    ).toBe(true);
    expect(
      shouldResetProductDocumentScroll(
        "/projects/project-1/research",
        "/projects/project-1/research",
      ),
    ).toBe(false);
    expect(shouldResetProductDocumentScroll("", "/projects")).toBe(false);
  });
});
